from PySide6.QtCore import Qt, QTimer, QSize, QSettings
from PySide6.QtGui import QFont, QFontMetrics
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget,
    QListWidgetItem, QFrame, QLineEdit, QMessageBox, QDialog, QListView
)
from ui.utils.base import NativeBase, create_icon, create_card, create_qicon
from ui.components import StandardHeader
from ui.components.common.badge import Badge
from ui.components.visualizers.network_visualizer import NetworkVisualizer
from ui.components.execution.decision_log import DecisionLog
from ui.components.execution.stats_overlay import StatsOverlay
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
        self.header = StandardHeader(subtitle="Scenario: Setup Pending...", show_settings_btn=False)
        self.header.dashboard_requested.connect(self._confirm_exit_to_dashboard)
        layout.addWidget(self.header)
        
        # --- Main Grid ---
        grid = QHBoxLayout()
        grid.setContentsMargins(20, 20, 20, 20)
        grid.setSpacing(20)
        
        # Column 1: Decision Engine (Left)
        # Refactored into DecisionLog component
        self.decision_log = DecisionLog()
        grid.addWidget(self.decision_log)
        
        # Column 2: Network View (Center) - flexible width
        col2 = QFrame()
        col2.setObjectName("card")
        col2.setStyleSheet("background: #e2e8f0; border-radius: 16px; border: 1px solid #cbd5e1;")
        col2_layout = QVBoxLayout(col2)
        
        # Overlay Stats inside the Graph View
        # Refactored into StatsOverlay component
        top_stats = QHBoxLayout()
        self.stats_overlay = StatsOverlay()
        top_stats.addWidget(self.stats_overlay)
        
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
        self.visualizer.node_clicked.connect(self._on_node_clicked)
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

        # Campos dinâmicos: nível de segurança, vizinhos, origem da infecção
        self.n_field_security = field("Security Level", "—")
        self.n_field_neighbors = field("Neighbors", "—")
        self.n_field_origin = field("Infection Source", "—", True)
        nc_lay.addLayout(self.n_field_security)
        nc_lay.addLayout(self.n_field_neighbors)
        nc_lay.addLayout(self.n_field_origin)
        
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
        log_lay.setContentsMargins(10, 15, 10, 15)
        l_head = QHBoxLayout()
        l_head.addWidget(create_icon("receipt_long", 18, "#0d9488"))
        l_head.addWidget(QLabel("EVENT LOG"))
        l_head.addStretch()
        log_lay.addLayout(l_head)
        log_lay.addWidget(QLabel("<hr style='color:#e2e8f0'>"))

        self.event_list = QListWidget()
        self.event_list.setFrameShape(QFrame.NoFrame)
        self.event_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.event_list.setResizeMode(QListView.Adjust)
        self.event_list.setStyleSheet("""
            QListWidget {
                background: transparent;
                outline: none;
            }
            QListWidget::item {
                border-bottom: 1px solid #f1f5f9;
                padding: 4px 0;
            }
            QListWidget::item:selected {
                background: transparent;
                color: inherit;
            }
        """)
        self.event_list.setWordWrap(True)
        log_lay.addWidget(self.event_list)

        col3.addWidget(log_card)
        
        wrapper_col3 = QWidget()
        wrapper_col3.setFixedWidth(300)
        col3.setContentsMargins(0, 0, 0, 0)
        wrapper_col3.setLayout(col3)
        
        grid.addWidget(wrapper_col3)
        
        layout.addLayout(grid)

        # Connect back
        self.back_requested.connect(lambda: None) # handled by nav logic

    def set_engine(self, engine):
        self.engine = engine
        self._setup_initial_state()
        self.update_ai_badge() # Force update badge when engine is set

        virus_name = engine.virus.name
        network_type = engine.topology_type if hasattr(engine, 'topology_type') else "Network"
        self.header.set_subtitle(f"Scenario: {virus_name} • {network_type}")

        # Update node count
        total = len(engine.network.nodes)
        self.stats_overlay.lbl_nodes_val.setText(f"{total:,}")

        # Initialize Visualizer
        self.visualizer.set_network(engine.network)

        self.update_stats_ui()

    def _confirm_exit_to_dashboard(self):
        """Ask the user to confirm leaving the simulation"""
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
                self.decision_log.live_badge.setText(" READY ")
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
            self.decision_log.live_badge.setText(" PAUSED ")
            self.decision_log.live_badge.set_theme("red")
        else:
            self.timer.start(500) # 500ms per step
            self.is_running = True
            self.play_btn.setText(create_icon("pause_circle", 32).text())
            self.decision_log.live_badge.setText(" LIVE ")
            self.decision_log.live_badge.set_theme("green")

    def run_step(self):
        if not self.engine:
            return
        result = self.engine.step()
        # Defensive: ensure result is a dict
        if not isinstance(result, dict):
            self.add_event_item('error', f"Step {self.engine.current_step}: Engine returned invalid result", step=self.engine.current_step)
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
            
            error_detail = reason if reason else str(err)

            # Check for LLM rate limit or context errors specifically
            if "limit" in str(err).lower() or "token" in str(err).lower() or "429" in str(err):
               self.add_event_item('llm_error', f"Step {step_num}: LLM Resource Limit - {err}", step=step_num)
               self.add_decision(f"Step {step_num}", "LLM PAUSED", f"Limit Reached: {error_detail}", "memory", "#f59e0b")
            else:
               self.add_event_item('error', f"Step {step_num}: ERROR - {err}", step=step_num)
               self.add_decision(f"Step {step_num}", "SYSTEM ERROR", error_detail, "error", "#ef4444")

        else:
            # Mutation
            if result.get('mutated'):
                self.add_event_item('mutation', f"Step {step_num}: Mutation executed", step=step_num)

            # Infection attempt
            if success:
                self.add_event_item('infection', f"Step {step_num}: Infection - Node {target}", step=step_num)
                node = self.engine.network.get_node(str(target))
                if node:
                    self.update_node_inspector(node)

                icon = "check_circle"
                color = "#059669"
                title = "Infectious Spread"
                self.add_decision(f"Step {step_num}", title, reason, icon, color)

            else:
                self.add_event_item('attack_blocked', f"Step {step_num}: Attack blocked ({src} -> {target})", step=step_num)
                
                icon = "shield" # Changed from block for distinction
                color = "#94a3b8" 
                title = "Attack Blocked"
                self.add_decision(f"Step {step_num}", title, reason, icon, color)


        self.decision_log.decision_list.scrollToBottom()

        # Check stop conditions
        should_stop, stop_reason = check_stop(self.engine)
        if should_stop:
            self.timer.stop()
            self.is_running = False
            self.play_btn.setText(create_icon("play_circle", 32).text())
            self.decision_log.live_badge.setText(" FINISHED ")
            self.decision_log.live_badge.set_theme("green")
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
            
        self.stats_overlay.lbl_step_val.setText(str(step))
        self.stats_overlay.lbl_infection_val.setText(f"{pct:.1f}%")

    def add_event(self, text: str, color: str = "#334155"):
        # Backwards-compatible simple API, maps to rich item
        self.add_event_item('info', text)

    def add_event_item(self, event_type: str, text: str, step: int = None):
        """Add a rich event item matching the new design."""
        
        # Color & Icon Map
        type_map = {
            'infection':      ('medical_services', '#ef4444', '#fee2e2'), 
            'attack_blocked': ('shield',           '#64748b', '#f1f5f9'), 
            'mutation':       ('science',          '#7c3aed', '#f3e8ff'), 
            'propagation':    ('bolt',             '#f59e0b', '#fef3c7'), 
            'scan':           ('search',           '#0ea5a4', '#ccfbf1'), 
            'clean':          ('check_circle',     '#059669', '#dcfce7'), 
            'error':          ('error',            '#ef4444', '#fee2e2'), 
            'info':           ('receipt_long',     '#334155', '#f1f5f9'), 
            'llm_error':      ('memory',           '#f59e0b', '#fef3c7')  
        }

        icon_name, main_color, bg_color = type_map.get(event_type, type_map['info'])

        item = QListWidgetItem()
        widget = QWidget()
        widget.setStyleSheet("background: transparent; border: none; margin: 0; padding: 0;")
        
        lay = QHBoxLayout(widget)
        lay.setContentsMargins(0, 8, 0, 8)
        lay.setSpacing(8)

        # 1. Left Icon (Rounded Square)
        icon_box = QFrame()
        icon_box.setFixedSize(30, 30)
        icon_box.setStyleSheet(f"background: {bg_color}; border-radius: 8px;")
        ib_lay = QVBoxLayout(icon_box)
        ib_lay.setContentsMargins(0,0,0,0)
        ib_lay.setAlignment(Qt.AlignCenter)
        ib_lay.addWidget(create_icon(icon_name, 16, main_color))
        
        lay.addWidget(icon_box, 0, Qt.AlignTop)

        # 2. Right Content
        right_col = QVBoxLayout()
        right_col.setContentsMargins(0, 0, 0, 0)
        right_col.setSpacing(4)

        # Header: "System Log" + Timestamp
        header_row = QHBoxLayout()
        header_row.setSpacing(8)
        
        title_lbl = QLabel("System Log" if event_type == 'info' else event_type.replace('_', ' ').title())
        title_lbl.setStyleSheet(f"font-weight: bold; color: #1e293b; font-size: 13px;")
        
        if step is not None:
             step_val = step
        else:
             step_val = self.engine.current_step if self.engine else 0
             
        time_badge = QLabel(f"Step: {step_val}")
        time_badge.setStyleSheet("background: #f1f5f9; color: #64748b; font-size: 10px; padding: 2px 6px; border-radius: 4px; font-weight: bold;")
        
        header_row.addWidget(title_lbl)
        header_row.addStretch()
        header_row.addWidget(time_badge)
        
        right_col.addLayout(header_row)

        # Log Box (Monospace look)
        log_box = QLabel(f"> {text}")
        log_box.setWordWrap(True)
        # Using a slight border/background to mimic a terminal block
        log_box.setStyleSheet("""
            background: #f8fafc; 
            border: 1px solid #e2e8f0; 
            border-radius: 6px; 
            padding: 8px; 
            color: #334155; 
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 11px;
        """)
        
        right_col.addWidget(log_box)
        
        lay.addLayout(right_col)
        
        target_width = 270
        widget.setFixedWidth(target_width)
        text_width_limit = 210 
        
        font = QFont("Consolas", 11)
        font.setStyleHint(QFont.Monospace)
        
        fm = QFontMetrics(font)
        text_rect = fm.boundingRect(0, 0, text_width_limit, 10000, Qt.TextWordWrap, f"> {text}")
        text_height = text_rect.height()
        
        total_height = 8 + 20 + 4 + text_height + 18 + 8
        total_height = max(total_height, 60)
        
        item.setSizeHint(QSize(target_width, total_height))
        self.event_list.addItem(item)
        self.event_list.setItemWidget(item, widget)
        self.event_list.scrollToBottom()

    def update_node_inspector(self, node):
        # Atualiza o inspector com informações dinâmicas
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

        # Nível de segurança
        self.n_field_security.itemAt(2).widget().setText(f"{node.security_level:.2f}")

        # Vizinhos
        vizinhos = ', '.join([str(nid) for nid in node.connected_nodes]) if node.connected_nodes else '—'
        self.n_field_neighbors.itemAt(2).widget().setText(vizinhos)

        # Origem da infecção (busca simples no histórico do engine)
        origem = '—'
        if self.engine and hasattr(self.engine, 'history'):
            for step in reversed(self.engine.history):
                for n in step.get('nodes_snapshot', []):
                    if n['id'] == node.id and n['status'] == 'infected':
                        # Tenta buscar source_node do step
                        origem = step.get('source_node', '—')
                        if origem and origem != node.id:
                            origem = f"Node #{origem}"
                        else:
                            origem = '—'
                        break
                if origem != '—':
                    break
        self.n_field_origin.itemAt(2).widget().setText(origem)

    def add_decision(self, step, title, desc, icon_name, color="#0d9488"):
        bg_map = {
            '#ef4444': '#fee2e2', 
            '#059669': '#dcfce7', 
            '#94a3b8': '#f1f5f9', 
            '#0d9488': '#ccfbf1', 
        }
        bg_color = bg_map.get(color, '#f1f5f9')

        item = QListWidgetItem()
        widget = QWidget()
        widget.setStyleSheet("background: transparent; border: none; margin: 0; padding: 0;") 
        
        lay = QHBoxLayout(widget)
        lay.setContentsMargins(0, 4, 0, 4)
        lay.setSpacing(8)
        
        # 1. Left Icon (Rounded Square)
        icon_box = QFrame()
        icon_box.setFixedSize(32, 32)
        icon_box.setStyleSheet(f"background: {bg_color}; border-radius: 8px;")
        ib_lay = QVBoxLayout(icon_box)
        ib_lay.setContentsMargins(0,0,0,0)
        ib_lay.setAlignment(Qt.AlignCenter)
        ib_lay.addWidget(create_icon(icon_name, 18, color))
        
        lay.addWidget(icon_box, 0, Qt.AlignTop)
        
        # 2. Right Content
        right_col = QVBoxLayout()
        right_col.setContentsMargins(0, 0, 0, 0)
        right_col.setSpacing(4)
        
        # Header: Title + Timestamp Badge
        header_row = QHBoxLayout()
        header_row.setSpacing(8)
        
        t_title = QLabel("Virus Logic Core" if "step" in step.lower() else title)
        t_title.setStyleSheet("font-weight: 800; font-size: 13px; color: #0f172a;")
        
        try:
            import re
            digits = re.findall(r'\d+', str(step))
            step_val = digits[0] if digits else "?"
            badge_text = f"Step: {step_val}"
        except:
            badge_text = "Step: ?"

        time_badge = QLabel(badge_text)
        time_badge.setStyleSheet("border: 1px solid #e2e8f0; color: #64748b; font-size: 10px; padding: 2px 6px; border-radius: 4px; font-weight: bold;")
        
        header_row.addWidget(t_title)
        header_row.addStretch()
        header_row.addWidget(time_badge)
        
        right_col.addLayout(header_row)
        
        # Body Content (with accent line)
        body_container = QWidget()
        body_lay = QHBoxLayout(body_container)
        body_lay.setContentsMargins(0,0,0,0)
        body_lay.setSpacing(8)
        
        # Accent Line
        accent_line = QFrame()
        accent_line.setFixedWidth(2)
        accent_line.setStyleSheet(f"background: {color}; border-radius: 1px;")
        body_lay.addWidget(accent_line)
        
        # Text Block
        text_block = QVBoxLayout()
        text_block.setContentsMargins(0,0,0,0)
        text_block.setSpacing(4)
        
        formatted_desc = desc
        if "#" in desc:
            import re
            # Regex to wrap #Number or Node #Number
            formatted_desc = re.sub(r"(#Node_\d+|Node #\d+|Node \d+|#\d+)", rf"<span style='background: {bg_color}; color: {color}; padding: 0 4px;'>\1</span>", desc)
        
        msg_label = QLabel(formatted_desc)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("color: #1e293b; font-size: 12px; line-height: 1.3;")
        msg_label.setTextFormat(Qt.RichText)
        
        text_block.addWidget(msg_label)
        
        body_lay.addLayout(text_block)
        
        right_col.addWidget(body_container)
        
        lay.addLayout(right_col)
        
        widget.setFixedWidth(255)
        
        item.setSizeHint(widget.sizeHint())
        self.decision_log.decision_list.addItem(item)
        self.decision_log.decision_list.setItemWidget(item, widget)
        widget.adjustSize()
        item.setSizeHint(widget.sizeHint())

    def _save_activity(self):
        if not self.engine or self.engine.current_step <= 0:
            return

        try:
            repo = ActivityRepository()
            infected = sum(1 for n in self.engine.network.nodes.values() if n.is_infected)
            total = len(self.engine.network.nodes)
            rate = (infected / total) * 100 if total > 0 else 0
            
            sim_id = str(uuid.uuid4())[:8].upper()
            
            virus_name = self.engine.virus.name if self.engine.virus and hasattr(self.engine.virus, 'name') else "Unknown"
            topo_type = self.engine.topology_type if hasattr(self.engine, 'topology_type') else "Unknown" 
            
            repo.log_activity(sim_id, topo_type, total, virus_name, rate)
        except Exception as e:
            print(f"Failed to log activity: {e}")

    def _on_node_clicked(self, node_id):
        if not self.engine or not self.engine.network:
            return
        node = self.engine.network.get_node(node_id)
        if node:
            self.update_node_inspector(node)

    def update_ai_badge(self):
        settings = QSettings("OutbreakSandbox", "Config")
        use_local = settings.value("use_local_llm", False, type=bool)
        
        if use_local:
            self.decision_log.set_ai_mode("LOCAL AI", theme="yellow")
        else:
            self.decision_log.set_ai_mode("CLOUD AI", theme="blue")

    def _setup_initial_state(self):
        self.decision_log.decision_list.clear()
        self.event_list.clear()
        self.is_running = False
        self.timer.stop()
        self.play_btn.setText(create_icon("play_circle", 32).text())
        self.decision_log.live_badge.setText(" READY ")
        self.decision_log.live_badge.set_theme("gray")