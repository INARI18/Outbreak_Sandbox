from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget,
    QListWidgetItem, QFrame, QLineEdit, QMessageBox, QDialog
)
from ui.screens.utils.base import NativeBase, create_icon, create_card, create_qicon
from ui.components import StandardHeader
from ui.components.network_visualizer import NetworkVisualizer
from infra.repositories.stats_repository import StatsRepository
from infra.repositories.activity_repository import ActivityRepository
from simulation.stop_conditions import check_stop
import uuid

class SimulationExecutionDashboardScreen(NativeBase):
    def __init__(self):
        super().__init__()
        self.engine = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.run_step)
        self.is_running = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # --- Navbar ---
        self.header = StandardHeader(subtitle="Scenario: Setup Pending...")
        # Intercept dashboard clicks to confirm stopping the running simulation
        self.header.dashboard_requested.connect(self._confirm_exit_to_dashboard)
        layout.addWidget(self.header)
        
        # --- Main Grid ---
        grid = QHBoxLayout()
        grid.setContentsMargins(20, 20, 20, 20)
        grid.setSpacing(20)
        
        # Column 1: Decision Engine (Left) - width ~25%
        col1 = create_card()
        col1.setFixedWidth(280)
        col1_layout = QVBoxLayout(col1)
        
        # Header
        c1_head = QHBoxLayout()
        c1_head.addWidget(create_icon("neurology", 20, "#0d9488"))
        c1_title = QLabel("DECISION ENGINE")
        c1_title.setStyleSheet("font-weight: bold; font-size: 12px; letter-spacing: 0.5px;")
        c1_head.addWidget(c1_title)
        c1_head.addStretch()
        self.live_badge = QLabel(" READY ")
        self.live_badge.setStyleSheet("background: #f1f5f9; color: #64748b; font-size: 10px; font-weight: bold; border-radius: 4px; padding: 2px;")
        c1_head.addWidget(self.live_badge)
        col1_layout.addLayout(c1_head)
        
        col1_layout.addWidget(QLabel("<hr style='color:#e2e8f0'>"))

        # List of decisions
        self.decision_list = QListWidget()
        self.decision_list.setFrameShape(QFrame.NoFrame)
        self.decision_list.setStyleSheet("background: transparent;")
        # avoid horizontal scrolling for long reasoning text
        self.decision_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.decision_list.setSizeAdjustPolicy(QListWidget.AdjustToContents)
        
        col1_layout.addWidget(self.decision_list)
        
        # Prompt Input
        input_row = QHBoxLayout()
        inp = QLineEdit()
        inp.setPlaceholderText("Ask about AI reasoning...")
        send_btn = QPushButton()
        send_btn.setText("->") 
        send_btn.setFixedSize(32, 32)
        input_row.addWidget(inp)
        input_row.addWidget(send_btn)
        col1_layout.addLayout(input_row)

        grid.addWidget(col1)
        
        # Column 2: Network View (Center) - flexible width
        col2 = QFrame()
        col2.setObjectName("card") # allow it to be a card too, or transparent
        col2.setStyleSheet("background: #e2e8f0; border-radius: 16px; border: 1px solid #cbd5e1;")
        col2_layout = QVBoxLayout(col2)
        
        # Overlay Stats inside the Graph View
        top_stats = QHBoxLayout()
        
        self.lbl_infection_val = QLabel("0%")
        self.lbl_infection_val.setStyleSheet("font-size: 18px; font-weight: 800; font-family: 'Space Grotesk';")

        self.lbl_step_val = QLabel("0")
        self.lbl_step_val.setStyleSheet("font-size: 18px; font-weight: 800; font-family: 'Space Grotesk';")
        
        self.lbl_nodes_val = QLabel("0")
        self.lbl_nodes_val.setStyleSheet("font-size: 18px; font-weight: 800; font-family: 'Space Grotesk';")


        def glass_stat(label, val_widget, change=None):
            f = QFrame()
            f.setStyleSheet("background: rgba(255,255,255,0.85); border-radius: 12px; border: 1px solid white;")
            v = QVBoxLayout(f)
            v.setContentsMargins(12, 8, 12, 8)
            lbl = QLabel(label)
            lbl.setStyleSheet("font-size: 10px; font-weight: bold; text-transform: uppercase; color: #64748b;")
            val_box = QHBoxLayout()
            val_box.addWidget(val_widget)
            if change:
                # Placeholder for trend
                pass
            v.addWidget(lbl)
            v.addLayout(val_box)
            return f

        top_stats.addWidget(glass_stat("Infection", self.lbl_infection_val))
        top_stats.addWidget(glass_stat("Step", self.lbl_step_val))
        top_stats.addWidget(glass_stat("Nodes", self.lbl_nodes_val))
        top_stats.addStretch()
        
        # Zoom controls
        zoom_col = QVBoxLayout()
        z1 = QPushButton("+"); z1.setFixedSize(32,32)
        z2 = QPushButton("-"); z2.setFixedSize(32,32)
        zoom_col.addWidget(z1)
        zoom_col.addWidget(z2)
        
        top_stats.addLayout(zoom_col)
        
        col2_layout.addLayout(top_stats)
        
        # Network Visualizer
        self.visualizer = NetworkVisualizer()
        self.visualizer.setStyleSheet("background: transparent; border: none;")
        col2_layout.addWidget(self.visualizer)
        
        # Bottom controls (Play/Pause)
        controls = QHBoxLayout()
        controls.addStretch()
        
        play_bar = QFrame()
        play_bar.setStyleSheet("background: rgba(255,255,255,0.9); border-radius: 24px; border: 1px solid #cbd5e1;")
        pb_lay = QHBoxLayout(play_bar)
        
        def mk_ctrl(icon_name):
            b = QPushButton(create_icon(icon_name, 20).text())
            b.setStyleSheet("font-family: 'Material Symbols Outlined'; border: none; background: transparent; font-size: 24px; color: #475569;")
            return b

        back_btn = mk_ctrl("fast_rewind") # Restart?
        self.play_btn = mk_ctrl("play_circle")
        self.play_btn.clicked.connect(self.toggle_simulation)
        self.play_btn.setStyleSheet("font-family: 'Material Symbols Outlined'; border: none; background: transparent; font-size: 32px; color: #0d9488;") # Bigger play
        fwd_btn = mk_ctrl("fast_forward")
        
        pb_lay.addWidget(back_btn)
        pb_lay.addWidget(self.play_btn)
        pb_lay.addWidget(fwd_btn)
        
        controls.addWidget(play_bar)
        controls.addStretch()
        
        col2_layout.addLayout(controls)
        
        grid.addWidget(col2, 1) # stretch 1
        
        # Column 3: Node Inspector (Right) - width 300px
        col3 = QVBoxLayout()
        col3.setSpacing(20)

        # Node Details Card
        node_card = create_card()
        nc_lay = QVBoxLayout(node_card)
        nc_lay.setSpacing(15)

        # Header
        n_head = QHBoxLayout()
        ico_pc = create_icon("desktop_windows", 24, "#1e293b")
        n_info = QVBoxLayout()
        n_info.setSpacing(2)
        self.n_title = QLabel("Node #—")
        self.n_title.setStyleSheet("font-weight: bold; font-family: 'Space Grotesk';")
        self.n_sub = QLabel("—")
        self.n_sub.setStyleSheet("font-size: 10px; color: #64748b;")
        n_info.addWidget(self.n_title); n_info.addWidget(self.n_sub)

        self.node_status_badge = QLabel("")
        self.node_status_badge.setStyleSheet("background: transparent; color: #0d9488; font-size: 10px; font-weight: bold; border-radius: 4px; padding: 2px 4px;")

        n_head.addWidget(ico_pc)
        n_head.addLayout(n_info)
        n_head.addStretch()
        n_head.addWidget(self.node_status_badge)

        nc_lay.addLayout(n_head)
        nc_lay.addWidget(QLabel("<hr style='color:#f1f5f9'>"))
        
        # Fields
        def field(k, v, link=False):
            r = QHBoxLayout()
            lbl = QLabel(k)
            lbl.setStyleSheet("color: #64748b; font-size: 11px;")
            val = QLabel(v)
            val.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {'#0d9488' if link else '#1e293b'};")
            r.addWidget(lbl)
            r.addStretch()
            r.addWidget(val)
            if link:
                ico = create_icon("open_in_new", 12, "#0d9488")
                r.addWidget(ico)
            return r

        nc_lay.addLayout(field("IP Address", "192.168.1.45"))
        nc_lay.addLayout(field("Infection Source", "Node #401", True))
        nc_lay.addLayout(field("Vulnerability", "SMBv1 (MS17-010)"))
        
        nc_lay.addWidget(QLabel("<hr style='color:#f1f5f9'>"))
        
        # Actions
        acts = QHBoxLayout()
        b1 = QPushButton(" Packet Log")
        b1.setIcon(create_qicon("description", 16, "#475569"))
        b1.setStyleSheet("border: 1px solid #cbd5e1; border-radius: 6px; padding: 8px; font-size: 11px;")
        b2 = QPushButton(" Isolate")
        b2.setIcon(create_qicon("gpp_bad", 16, "#be123c"))
        b2.setStyleSheet("background: #fff1f2; color: #be123c; border: 1px solid #fecdd3; border-radius: 6px; padding: 8px; font-size: 11px;")
        
        acts.addWidget(b1)
        acts.addWidget(b2)
        nc_lay.addLayout(acts)
        
        col3.addWidget(node_card)

    # Event Log Card - dynamic
        log_card = create_card()
        log_lay = QVBoxLayout(log_card)
        l_head = QHBoxLayout()
        l_head.addWidget(create_icon("receipt_long", 18, "#0d9488"))
        l_head.addWidget(QLabel("EVENT LOG"))
        l_head.addStretch()
        l_head.addWidget(create_icon("download", 16, "#94a3b8")) # Export
        log_lay.addLayout(l_head)
        log_lay.addWidget(QLabel("<hr style='color:#e2e8f0'>"))

        self.event_list = QListWidget()
        self.event_list.setFrameShape(QFrame.NoFrame)
        self.event_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.event_list.setSizeAdjustPolicy(QListWidget.AdjustToContents)
        log_lay.addWidget(self.event_list)
        log_lay.addStretch()

        col3.addWidget(log_card)
        
        wrapper_col3 = QWidget()
        wrapper_col3.setFixedWidth(300)
        wrapper_col3.setLayout(col3)
        
        grid.addWidget(wrapper_col3)
        
        layout.addLayout(grid)

        # Connect back
        self.back_requested.connect(lambda: None) # handled by nav logic

    def set_engine(self, engine):
        self.engine = engine
        self.decision_list.clear()
        
        virus_name = engine.virus.name
        self.header.set_subtitle(f"Scenario: {virus_name} • Ready")
        
        # Update node count
        total = len(engine.network.nodes)
        self.lbl_nodes_val.setText(f"{total:,}")
        
        # Initialize Visualizer
        self.visualizer.set_network(engine.network)
        
        self.update_stats_ui()

    def _confirm_exit_to_dashboard(self):
        """Ask the user to confirm leaving the simulation (this will stop it and clear state).

        If confirmed, stop timer, clear engine and UI state, and emit dashboard_requested so
        MainWindow navigates back to the dashboard/home screen.
        """
        # Use a custom-styled dialog (so it matches the app look) instead of the native QMessageBox
        dlg = QDialog(self)
        dlg.setModal(True)
        dlg.setWindowTitle("Confirm Leave Simulation")
        dlg_layout = QVBoxLayout(dlg)

        card = create_card()
        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Leaving the dashboard will STOP the running simulation and clear all state (events, AI reasoning, configurations).")
        title.setWordWrap(True)
        title.setStyleSheet("color: #334155; font-size: 13px;")
        cl.addWidget(title)
        cl.addSpacing(10)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        no_btn = QPushButton("No")
        no_btn.setStyleSheet("background: white; border: 1px solid #cbd5e1; padding: 8px 14px; border-radius: 8px;")
        yes_btn = QPushButton("Yes")
        yes_btn.setObjectName("primary")
        yes_btn.setStyleSheet("padding: 8px 14px; border-radius: 8px;")
        btn_row.addWidget(no_btn)
        btn_row.addSpacing(8)
        btn_row.addWidget(yes_btn)

        cl.addLayout(btn_row)
        dlg_layout.addWidget(card)

        # Wire buttons
        no_btn.clicked.connect(dlg.reject)
        yes_btn.clicked.connect(dlg.accept)

        accepted = dlg.exec()
        if accepted:
            # Stop timer if running
            try:
                if self.is_running:
                    self.timer.stop()
                    self.is_running = False
            except Exception:
                pass

            # Save activity record before clearing
            self._save_activity()

            # Clear engine and UI state
            self.engine = None
            try:
                self.decision_list.clear()
            except Exception:
                pass
            try:
                self.event_list.clear()
            except Exception:
                pass
            try:
                # reset node inspector
                self.n_title.setText("Node #—")
                self.n_sub.setText("—")
                self.node_status_badge.setText("")
                self.node_status_badge.setStyleSheet("background: transparent; color: #0d9488; font-size: 10px; font-weight: bold; border-radius: 4px; padding: 2px 4px;")
            except Exception:
                pass
            try:
                # Clear visualizer
                self.visualizer.set_network(None)
            except Exception:
                pass

            # Update play button and live badge
            try:
                self.play_btn.setText(create_icon("play_circle", 32).text())
                self.live_badge.setText(" READY ")
                self.live_badge.setStyleSheet("background: #f1f5f9; color: #64748b; font-size: 10px; font-weight: bold; border-radius: 4px; padding: 2px;")
            except Exception:
                pass

            # Emit signal so MainWindow can navigate away
            self.dashboard_requested.emit()

    def toggle_simulation(self):
        if not self.engine:
            QMessageBox.warning(self, "No Engine", "Simulation engine not initialized.")
            return

        if self.is_running:
            self.timer.stop()
            self.is_running = False
            self.play_btn.setText(create_icon("play_circle", 32).text())
            self.live_badge.setText(" PAUSED ")
            self.live_badge.setStyleSheet("background: #fff1f2; color: #be123c; font-size: 10px; font-weight: bold; border-radius: 4px; padding: 2px;")
        else:
            self.timer.start(500) # 500ms per step
            self.is_running = True
            self.play_btn.setText(create_icon("pause_circle", 32).text())
            self.live_badge.setText(" LIVE ")
            self.live_badge.setStyleSheet("background: #ecfdf5; color: #059669; font-size: 10px; font-weight: bold; border-radius: 4px; padding: 2px;")

    def run_step(self):
        if not self.engine:
            return
        result = self.engine.step()
        # Defensive: ensure result is a dict
        if not isinstance(result, dict):
            self.add_event_item('error', f"Step {self.engine.current_step}: Engine returned invalid result")
            return

        self.update_stats_ui()
        self.visualizer.refresh_state()

        # Event log and node inspector updates
        step_num = result.get('step', -1)
        reason = result.get('llm_reasoning', '')

        # Normalize attempt dict safely
        attempt = result.get('attempt') or {}
        success = attempt.get('success', False)
        target = result.get('target_node')
        src = result.get('source_node')

        # Errors
        if 'error' in result and result.get('error'):
            err = result.get('error')
            # concise error in event log; full LLM reasoning kept in decision panel only
            self.add_event_item('error', f"Step {step_num}: ERROR - {err}")
        else:
            # Mutation
            if result.get('mutated'):
                self.add_event_item('mutation', f"Step {step_num}: Mutation executed")

            # Infection attempt
            if success:
                self.add_event_item('infection', f"Step {step_num}: Infection - Node {target}")
                node = self.engine.network.get_node(str(target))
                if node:
                    self.update_node_inspector(node)
            else:
                self.add_event_item('attack_blocked', f"Step {step_num}: Attack blocked ({src} -> {target})")

        # Add human-friendly decision reasoning to the left panel (only here)
        icon = "check_circle" if success else "block"
        color = "#059669" if success else "#ef4444"
        title = "Infectious Spread" if success else "Attack Blocked"
        self.add_decision(f"Step {step_num}", title, reason, icon, color)
        self.decision_list.scrollToBottom()

        # Check stop conditions
        should_stop, stop_reason = check_stop(self.engine)
        if should_stop:
            self.timer.stop()
            self.is_running = False
            self.play_btn.setText(create_icon("play_circle", 32).text())
            self.live_badge.setText(" FINISHED ")
            self.live_badge.setStyleSheet("background: #dcfce7; color: #166534; font-size: 10px; font-weight: bold; border-radius: 4px; padding: 2px;")
            self.add_event_item('info', f"Simulation Finished: {stop_reason}")
            self._save_activity()

    def update_stats_ui(self):
        if not self.engine:
            return
        
        step = self.engine.current_step
        infected = len(self.engine.network.infected_nodes())
        total = len(self.engine.network.nodes)
        if total > 0:
            pct = (infected / total) * 100
        else:
            pct = 0
            
        self.lbl_step_val.setText(str(step))
        self.lbl_infection_val.setText(f"{pct:.1f}%")

    def add_event(self, text: str, color: str = "#334155"):
        # Backwards-compatible simple API, maps to rich item
        self.add_event_item('info', text)

    def add_event_item(self, event_type: str, text: str):
        """Add a rich event item with icon + color based on event_type.

        Supported event_type: infection, attack_blocked, mutation, propagation, scan, clean, error, info
        """
        from PySide6.QtGui import QColor

        type_map = {
            'infection': ('medical_services', '#ef4444'),
            'attack_blocked': ('block', '#94a3b8'),
            'mutation': ('science', '#7c3aed'),
            'propagation': ('bolt', '#f59e0b'),
            'scan': ('search', '#0ea5a4'),
            'clean': ('check_circle', '#059669'),
            'error': ('error', '#ef4444'),
            'info': ('receipt_long', '#334155')
        }

        icon_name, color = type_map.get(event_type, type_map['info'])

        item = QListWidgetItem()
        widget = QWidget()
        lay = QHBoxLayout(widget)
        lay.setContentsMargins(0, 4, 0, 4)

        icon_lbl = create_icon(icon_name, 16, color)
        bub = QFrame()
        bub.setFixedSize(28, 28)
        bub.setStyleSheet(f"background: white; border-radius: 14px; border: 1px solid #e6eef2;")
        bl = QVBoxLayout(bub); bl.setContentsMargins(0,0,0,0); bl.setAlignment(Qt.AlignCenter)
        bl.addWidget(icon_lbl)

        lay.addWidget(bub, 0, Qt.AlignTop)

        txt_v = QVBoxLayout()
        main = QLabel(text)
        main.setWordWrap(True)
        main.setStyleSheet(f"font-weight: bold; color: {color};")
        main.setTextInteractionFlags(Qt.TextSelectableByMouse)
        txt_v.addWidget(main)

        lay.addLayout(txt_v)

        item.setSizeHint(widget.sizeHint())
        self.event_list.addItem(item)
        self.event_list.setItemWidget(item, widget)
        self.event_list.scrollToBottom()

    def update_node_inspector(self, node):
        # Update right-hand inspector with node details
        self.n_title.setText(f"Node #{node.id}")
        self.n_sub.setText(node.name)
        # status badge
        if node.is_infected:
            self.node_status_badge.setText("INFECTED")
            self.node_status_badge.setStyleSheet("background: #fee2e2; color: #ef4444; font-size: 10px; font-weight: bold; border-radius: 4px; padding: 2px 4px;")
        elif node.status == 'quarantined':
            self.node_status_badge.setText("QUARANTINED")
            self.node_status_badge.setStyleSheet("background: #fff7ed; color: #b45309; font-size: 10px; font-weight: bold; border-radius: 4px; padding: 2px 4px;")
        else:
            self.node_status_badge.setText("HEALTHY")
            self.node_status_badge.setStyleSheet("background: #ecfdf5; color: #059669; font-size: 10px; font-weight: bold; border-radius: 4px; padding: 2px 4px;")

    def add_decision(self, step, title, desc, icon_name, color="#0d9488"):
        """Adds a tailored ListItemWidget."""
        item = QListWidgetItem()
        widget = QWidget()
        lay = QHBoxLayout(widget)
        lay.setContentsMargins(0, 5, 0, 5)
        
        # Icon bubble
        icon_lbl = create_icon(icon_name, 18, color)
        icon_bubble = QFrame()
        icon_bubble.setFixedSize(32, 32)
        icon_bubble.setStyleSheet("background: white; border-radius: 16px; border: 1px solid #e2e8f0;")
        ib_lay = QVBoxLayout(icon_bubble); ib_lay.setContentsMargins(0,0,0,0); ib_lay.setAlignment(Qt.AlignCenter)
        ib_lay.addWidget(icon_lbl)
        
        lay.addWidget(icon_bubble, 0, Qt.AlignTop)
        
        # Text content
        txt_v = QVBoxLayout()
        top_row = QHBoxLayout()
        t_step = QLabel(step)
        t_step.setStyleSheet("font-size: 10px; color: #94a3b8;")
        t_title = QLabel(title)
        t_title.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {color}; text-transform: uppercase;")
        top_row.addWidget(t_step)
        top_row.addWidget(t_title)
        top_row.addStretch()
        
        body = QLabel(desc)
        body.setWordWrap(True)
        body.setStyleSheet("font-size: 11px; color: #334155;")
        
        txt_v.addLayout(top_row)
        txt_v.addWidget(body)
        
        lay.addLayout(txt_v)
        
        item.setSizeHint(widget.sizeHint())
        self.decision_list.addItem(item)
        self.decision_list.setItemWidget(item, widget)

    def _save_activity(self):
        if not self.engine or self.engine.current_step <= 0:
            return

        try:
            repo = ActivityRepository()
            infected = sum(1 for n in self.engine.network.nodes.values() if n.is_infected)
            total = len(self.engine.network.nodes)
            rate = (infected / total) * 100 if total > 0 else 0
            
            # Extract data safely. Assuming simulation ID is just a random string or incremental
            sim_id = str(uuid.uuid4())[:8].upper()
            
            virus_name = self.engine.virus.name if self.engine.virus and hasattr(self.engine.virus, 'name') else "Unknown"
            topo_type = "Network" 
            
            repo.log_activity(sim_id, topo_type, total, virus_name, rate)
        except Exception as e:
            print(f"Failed to log activity: {e}")
