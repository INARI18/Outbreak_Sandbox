import os
import json
from PySide6.QtWidgets import (
    QLabel, QGridLayout, QPushButton, QVBoxLayout, QFrame, QHBoxLayout, 
    QButtonGroup, QWidget
)
from PySide6.QtCore import Qt
from ui.utils.base import create_icon, create_qicon
from .base_wizard import WizardScreen

class VirusSelectionScreen(WizardScreen):
    def __init__(self):
        super().__init__(2)
        self.viruses_data = self._load_viruses()
        self.current_page = 0
        self.items_per_page = 3
        self.selected_virus_id = None
        self.current_filter = "All Types"
        
        self._setup_ui()
        self._render_page()

    def _load_viruses(self):
        """Load viruses from JSON and map UI properties based on type."""
        try:
            # Assuming viruses.json is in config/ directory
            file_path = os.path.join(os.getcwd(), 'config/viruses.json')
            if not os.path.exists(file_path):
                 # Fallback if running from a different dir look up one level
                 file_path = os.path.join(os.getcwd(), '..', 'config/viruses.json')

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                raw_viruses = data.get('viruses', [])
        except Exception as e:
            print(f"Error loading viruses.json: {e}")
            return []

        # Color and Icon mapping by virus type
        type_config = {
            "ransomware": {"color": "#ef4444", "icon": "lock"},      # Red
            "worm":       {"color": "#f59e0b", "icon": "bug_report"},# Amber
            "botnet":     {"color": "#6366f1", "icon": "router"},    # Indigo
            "trojan":     {"color": "#8b5cf6", "icon": "extension"}, # Violet
            "spyware":    {"color": "#ec4899", "icon": "visibility"},# Pink
            "adware":     {"color": "#10b981", "icon": "campaign"},  # Emerald
        }
        
        processed = []
        for v in raw_viruses:
            # Normalize type to lowercase for key lookup
            v_type_key = v.get('type', 'unknown').lower()
            
            # Get config or default (Slate color, virus icon)
            config = type_config.get(v_type_key, {"color": "#64748b", "icon": "coronavirus"})
            
            # Read characteristics (scale 1-10 -> 0-100)
            chars = v.get('characteristics', {})
            atk = chars.get('attack_power', 0) * 10
            spd = chars.get('speed', 0) * 10
            # stealth is sometimes 'stealth' or might be missing? default 0
            stl = chars.get('stealth', 0) * 10
            
            processed.append({
                "id": v.get('id'),
                "name": v.get('name'),
                # Capitalize type for display
                "type": v_type_key.capitalize(),
                "atk": atk,
                "spd": spd,
                "stl": stl,
                "color": config['color'],
                "icon": config['icon'],
                "desc": v.get('description', 'No description available.')
            })
            
        return processed

    def _get_next_text(self):
        return "Next: Config"

    def _setup_ui(self):
        # Title
        title = QLabel("Select Simulation Strain")
        title.setObjectName("h2")
        title.setStyleSheet("font-size: 24px; font-weight: 800; color: #1e293b; margin-bottom: 8px;")
        title.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(title)
        
        subtitle = QLabel("Choose the pathogen for this scenario. Each strain has unique propagation characteristics.")
        subtitle.setStyleSheet("color: #64748b; font-size: 14px; margin-bottom: 24px;")
        subtitle.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(subtitle)
        
        # Filters
        filters_container = QWidget() 
        fc_lay = QHBoxLayout(filters_container)
        fc_lay.setContentsMargins(0,0,0,0)
        fc_lay.setAlignment(Qt.AlignCenter)
        
        self.filter_group = QButtonGroup(self)
        self.filter_group.setExclusive(True)
        self.filter_group.buttonClicked.connect(self._on_filter_changed)

        for f in ["All Types", "Ransomware", "Trojan", "Worm", "Botnet"]:
            btn = QPushButton(f)
            btn.setCheckable(True)
            btn.setProperty("filter_key", f)
            if f == "All Types": btn.setChecked(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(36)
            btn.setStyleSheet("""
                QPushButton { 
                    border-radius: 18px; 
                    padding: 0 20px; 
                    border: 1px solid #e2e8f0; 
                    background: white; 
                    color: #64748b; 
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background: #f8fafc;
                    color: #334155;
                }
                QPushButton:checked { 
                    background: #0f172a; 
                    color: white; 
                    border: 1px solid #0f172a; 
                }
            """)
            self.filter_group.addButton(btn)
            fc_lay.addWidget(btn)
            
        self.content_layout.addWidget(filters_container)
        self.content_layout.addSpacing(20)
        
        # --- CAROUSEL AREA ---
        carousel_container = QWidget()
        carousel_layout = QHBoxLayout(carousel_container)
        carousel_layout.setContentsMargins(0,0,0,0)
        carousel_layout.setSpacing(16)
        
        # Left Chevron
        self.btn_prev = QPushButton()
        self.btn_prev.setFixedSize(40, 40)
        self.btn_prev.setIcon(create_qicon("chevron_left", 24, "#64748b"))
        self.btn_prev.setCursor(Qt.PointingHandCursor)
        self.btn_prev.setStyleSheet("""
            QPushButton { background: white; border: 1px solid #e2e8f0; border-radius: 20px; }
            QPushButton:hover { background: #f1f5f9; }
            QPushButton:disabled { background: #f8fafc; border: 1px solid #f1f5f9; color: #cbd5e1; }
        """)
        self.btn_prev.clicked.connect(self._prev_page)
        
        # Middle Content (The Cards)
        self.card_host = QWidget()
        self.card_layout = QHBoxLayout(self.card_host)
        self.card_layout.setContentsMargins(0,0,0,0)
        self.card_layout.setSpacing(24)
        self.card_layout.setAlignment(Qt.AlignCenter)
        
        # Right Chevron
        self.btn_next = QPushButton()
        self.btn_next.setFixedSize(40, 40)
        self.btn_next.setIcon(create_qicon("chevron_right", 24, "#64748b"))
        self.btn_next.setCursor(Qt.PointingHandCursor)
        self.btn_next.setStyleSheet("""
            QPushButton { background: white; border: 1px solid #e2e8f0; border-radius: 20px; }
            QPushButton:hover { background: #f1f5f9; }
            QPushButton:disabled { background: #f8fafc; border: 1px solid #f1f5f9; color: #cbd5e1; }
        """)
        self.btn_next.clicked.connect(self._next_page)
        
        carousel_layout.addStretch()
        carousel_layout.addWidget(self.btn_prev)
        carousel_layout.addWidget(self.card_host)
        carousel_layout.addWidget(self.btn_next)
        carousel_layout.addStretch()

        self.content_layout.addWidget(carousel_container)
        
        # Single QButtonGroup to manage exclusivity across pages logic (conceptually)
        # But since we rebuild widgets, we need to add them to group dynamically
        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        self.group.buttonClicked.connect(lambda btn: self._on_virus_selected(btn))
        
        # Disable next initially
        try:
            self.footer.next_btn.setEnabled(False)
        except Exception:
            pass
        self.content_layout.addStretch()

    def _on_filter_changed(self, btn):
        self.current_filter = btn.property("filter_key")
        self.current_page = 0
        self._render_page()

    def _get_filtered_viruses(self):
        if self.current_filter == "All Types":
            return self.viruses_data
        
        return [
            v for v in self.viruses_data 
            if v['type'].lower() == self.current_filter.lower()
        ]

    def _render_page(self):
        # Clear existing widgets from layout and group
        # Note: Removing from layout doesn't delete immediately unless we call deleteLater
        while self.card_layout.count():
            item = self.card_layout.takeAt(0)
            w = item.widget()
            if w:
                if isinstance(w, QPushButton):
                    self.group.removeButton(w)
                w.deleteLater()
        
        filtered_data = self._get_filtered_viruses()
        
        # Calculate slice
        start = self.current_page * self.items_per_page
        end = start + self.items_per_page
        slice_data = filtered_data[start:end]
        
        for v in slice_data:
            card = self._create_card(v)
            # Restore selection state
            if self.selected_virus_id == v['id']:
                card.setChecked(True)
                
            self.group.addButton(card)
            self.card_layout.addWidget(card)
            
        # Update chevron states
        self.btn_prev.setEnabled(self.current_page > 0)
        # Check if there is a next page
        self.btn_next.setEnabled(end < len(filtered_data))

    def _prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self._render_page()

    def _next_page(self):
        filtered_data = self._get_filtered_viruses()
        if (self.current_page + 1) * self.items_per_page < len(filtered_data):
            self.current_page += 1
            self._render_page()

    def _create_card(self, data):
        name = data['name']
        vtype = data['type']
        atk = data['atk']
        spd = data['spd']
        stl = data['stl']
        color = data['color']
        icon_name = data['icon']
        desc = data['desc']
        vid = data['id']
        
        card = QPushButton()
        card.setCheckable(True)
        card.setFixedSize(300, 420)
        card.setProperty("virus_name", name) 
        card.setProperty("virus_id", vid)
        card.setCursor(Qt.PointingHandCursor)
        
        # Updated Style: Border is always #0d9488 (Teal/Green) when checked
        card.setStyleSheet(f"""
            QPushButton {{ 
                background: white; 
                border: 1px solid #e2e8f0; 
                border-radius: 20px; 
                text-align: left; 
                padding: 0;
            }}
            QPushButton:hover {{
                border: 1px solid #cbd5e1;
                background: #fdfdfd;
            }}
            QPushButton:checked {{ 
                border: 3px solid #0d9488; 
                background: #ffffff;
            }}
        """)
        
        vl = QVBoxLayout(card)
        vl.setContentsMargins(24, 24, 24, 24)
        vl.setSpacing(0)
        
        # Header Row: Type Badge + Dot
        hdr = QHBoxLayout()
        
        badge = QLabel(vtype.upper())
        badge.setStyleSheet(f"background: {color}20; color: {color}; font-weight: 800; font-size: 10px; padding: 4px 8px; border-radius: 6px;")
        
        hdr.addWidget(badge)
        hdr.addStretch()
        
        # Severity Dots
        dots = QHBoxLayout()
        dots.setSpacing(2)
        for i in range(3):
            d = QFrame()
            d.setFixedSize(6, 6)
            d.setStyleSheet(f"background: {color if i < (atk/30) else '#e2e8f0'}; border-radius: 3px;")
            dots.addWidget(d)
        hdr.addLayout(dots)
        
        vl.addLayout(hdr)
        
        # Main Icon Area
        vl.addStretch()
        icon_container = QFrame()
        icon_container.setFixedSize(80, 80)
        icon_container.setStyleSheet(f"background: rgba({int(color[1:3],16)}, {int(color[3:5],16)}, {int(color[5:7],16)}, 0.1); border-radius: 40px;")
        
        icl = QVBoxLayout(icon_container); icl.setContentsMargins(0,0,0,0); icl.setAlignment(Qt.AlignCenter)
        icl.addWidget(create_icon(icon_name, 40, color))
        
        vl.addWidget(icon_container, 0, Qt.AlignCenter)
        vl.addStretch()

        # Content
        vn = QLabel(name)
        vn.setAlignment(Qt.AlignCenter)
        vn.setStyleSheet("font-weight: 800; font-size: 18px; color: #1e293b; border: none; background: transparent;")
        vl.addWidget(vn)
        
        vd = QLabel(desc)
        vd.setAlignment(Qt.AlignCenter)
        vd.setWordWrap(True)
        vd.setStyleSheet("color: #64748b; font-size: 12px; margin-top: 8px; margin-bottom: 20px; border: none; background: transparent;")
        vl.addWidget(vd)
        
        # Stats Bars
        stats_box = QWidget()
        stats_box.setStyleSheet("background: #f8fafc; border-radius: 12px; border: none;")
        sbl = QVBoxLayout(stats_box)
        sbl.setContentsMargins(16, 16, 16, 16)
        sbl.setSpacing(8)
        
        self._add_stat(sbl, "Infectivity", atk, color)
        self._add_stat(sbl, "Speed", spd, color)
        self._add_stat(sbl, "Stealth", stl, color)
        
        vl.addWidget(stats_box)
        
        return card

    def _on_virus_selected(self, btn):
        self.footer.next_btn.setEnabled(True)
        self.selected_virus_id = btn.property("virus_id")

    def get_selected_virus_name(self) -> str | None:
        """Return the name of the selected virus card or None."""
        if not self.selected_virus_id:
            return None
        v = next((item for item in self.viruses_data if item["id"] == self.selected_virus_id), None)
        return v['name'] if v else None

    def reset(self):
        self.selected_virus_id = None
        self.current_page = 0
        self.current_filter = "All Types"
        self._render_page()
        if hasattr(self, 'footer'):
             self.footer.next_btn.setEnabled(False)

    def is_complete(self) -> bool:
        return self.selected_virus_id is not None

    def _add_stat(self, layout, label, val, color):
        row = QHBoxLayout()
        row.setSpacing(10)
        
        lbl = QLabel(label)
        lbl.setFixedWidth(60)
        lbl.setStyleSheet("color: #64748b; font-size: 10px; font-weight: bold; border: none; background: transparent;")
        
        bar_bg = QFrame()
        bar_bg.setFixedHeight(6)
        # bar_bg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed) # removed redundant, frame is expanding
        bar_bg.setStyleSheet("background: #e2e8f0; border-radius: 3px;")
        
        stop = min(max(val / 100.0, 0.0), 1.0)
        stop_next = min(stop + 0.001, 1.0)
        
        bar_bg.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                stop:0 {color}, stop:{stop} {color}, 
                stop:{stop_next} #e2e8f0, stop:1 #e2e8f0);
            border-radius: 3px;
        """)
        
        val_txt = QLabel(f"{val}%")
        val_txt.setFixedWidth(30)
        val_txt.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        val_txt.setStyleSheet("font-size: 10px; font-weight: bold; color: #334155; border: none; background: transparent;")
        
        row.addWidget(lbl)
        row.addWidget(bar_bg)
        row.addWidget(val_txt)
        
        layout.addLayout(row)
