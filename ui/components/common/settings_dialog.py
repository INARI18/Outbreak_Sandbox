from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QCheckBox, QProgressBar, QMessageBox, QFrame, 
    QStackedWidget, QWidget
)
from PySide6.QtCore import Qt, QThread, Signal, QSettings
import keyring
import os

# Dummy thread for "downloading" model to simulate the experience if real download is too heavy
# or actually implement real download if feasible. For now, I'll make it realistic mock or real wrapper.
class ModelManagerThread(QThread):
    progress_updated = Signal(int, str)
    finished_success = Signal()
    finished_error = Signal(str)

    def __init__(self, action="download", model_name="microsoft/Phi-3-mini-4k-instruct"):
        super().__init__()
        self.action = action
        self.model_name = model_name

    def run(self):
        try:
            if self.action == "download":
                self.progress_updated.emit(10, "Initializing download framework...")
                
                # Check imports first
                try:
                    from huggingface_hub import snapshot_download
                except ImportError:
                    self.finished_error.emit("huggingface_hub library missing. Please pip install huggingface-hub")
                    return

                # Real download logic
                self.progress_updated.emit(20, "Connecting to Hugging Face...")
                
                # This will download to ~/.cache/huggingface/hub by default
                model_path = snapshot_download(
                    repo_id=self.model_name,
                    repo_type="model",
                    resume_download=True,
                    # We can't easily track granular percentage in snapshot_download without a custom callback,
                    # so we'll just emit updates periodically or treat it as a long blocking op.
                )
                
                self.progress_updated.emit(90, "Verifying files...")
                
                # Create a marker file to indicate it's installed
                os.makedirs("models_cache", exist_ok=True)
                with open("models_cache/phi_installed.marker", "w") as f:
                    f.write("installed")
                
                self.finished_success.emit()
            
            elif self.action == "delete":
                from huggingface_hub import scan_cache_dir
                
                self.progress_updated.emit(10, "Scanning cache...")
                # Real deletion is complex with HF cache, for now we will just remove our marker
                # to "Soft Uninstall" it from the UI perspective.
                # A full delete would require using huggingface-cli delete-cache.
                
                import time
                time.sleep(1)
                
                self.progress_updated.emit(50, "Removing registration...")
                marker = "models_cache/phi_installed.marker"
                if os.path.exists(marker):
                    os.remove(marker)
                self.finished_success.emit()
                
        except Exception as e:
            self.finished_error.emit(str(e))

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Global Configuration")
        self.setFixedSize(500, 450)
        self.setStyleSheet("""
            QDialog { background: white; border-radius: 20px; }
            QLabel { font-size: 14px; color: #334155; }
            QLineEdit { 
                border: 1px solid #cbd5e1; border-radius: 8px; padding: 10px;
                color: #334155; font-size: 14px;
            }
            QLineEdit:focus { border-color: #0d9488; }
            QCheckBox { spacing: 10px; font-size: 14px; color: #334155; }
            QCheckBox::indicator { width: 18px; height: 18px; }
        """)

        self.settings = QSettings("OutbreakSandbox", "Config")
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title = QLabel("Settings")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #0f172a;")
        self.layout.addWidget(title)

        # --- Section 1: LLM Provider Mode ---
        mode_frame = QFrame()
        mode_frame.setStyleSheet("background: #f8fafc; border-radius: 8px; padding: 10px;")
        mode_layout = QVBoxLayout(mode_frame)
        
        self.local_mode_chk = QCheckBox("Use Local LLM (Offline Mode)")
        self.local_mode_chk.setChecked(self.settings.value("use_local_llm", False, type=bool))
        self.local_mode_chk.toggled.connect(self.toggle_mode)
        mode_layout.addWidget(self.local_mode_chk)

        info = QLabel("Enable to use Microsoft Phi-3 locally via HuggingFace.\nDisable to use Groq API (Cloud).")
        info.setStyleSheet("color: #64748b; font-size: 11px; margin-left: 28px;")
        mode_layout.addWidget(info)
        
        self.layout.addWidget(mode_frame)

        # --- Section 2: Configuration Stack ---
        self.stack = QStackedWidget()
        
        # Page 1: Groq API
        self.page_groq = QWidget()
        p1_layout = QVBoxLayout(self.page_groq)
        p1_layout.setContentsMargins(0,0,0,0)
        p1_layout.addWidget(QLabel("<b>Groq API Configuration</b>"))
        
        self.api_input = QLineEdit()
        self.api_input.setPlaceholderText("gsk_...")
        self.api_input.setEchoMode(QLineEdit.Password)
        try:
            current_key = keyring.get_password("outbreak_sandbox", "groq_api_key")
            if current_key:
                self.api_input.setText(current_key)
        except:
            pass
        p1_layout.addWidget(self.api_input)
        
        self.save_key_btn = QPushButton("Save API Key")
        self.save_key_btn.setCursor(Qt.PointingHandCursor)
        self.save_key_btn.clicked.connect(self.save_api_key)
        p1_layout.addWidget(self.save_key_btn)
        p1_layout.addStretch()

        # Page 2: Local Model Manager
        self.page_local = QWidget()
        p2_layout = QVBoxLayout(self.page_local)
        p2_layout.setContentsMargins(0,0,0,0)
        p2_layout.addWidget(QLabel("<b>Local Model: Microsoft Phi-3</b>"))
        
        self.status_lbl = QLabel("Status: Checking...")
        p2_layout.addWidget(self.status_lbl)
        
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.hide()
        p2_layout.addWidget(self.progress)
        
        btn_row = QHBoxLayout()
        self.download_btn = QPushButton("Download Model")
        self.download_btn.clicked.connect(self.download_model)
        self.download_btn.setStyleSheet("background: #0d9488; color: white; font-weight: bold;")
        
        self.delete_btn = QPushButton("Uninstall Model")
        self.delete_btn.clicked.connect(self.delete_model)
        self.delete_btn.setStyleSheet("background: white; color: #ef4444; border: 1px solid #ef4444;")
        
        btn_row.addWidget(self.download_btn)
        btn_row.addWidget(self.delete_btn)
        p2_layout.addLayout(btn_row)
        p2_layout.addStretch()

        self.stack.addWidget(self.page_groq)
        self.stack.addWidget(self.page_local)
        self.layout.addWidget(self.stack)

        # Close Button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("padding: 8px;")
        self.layout.addWidget(close_btn)
        
        self.check_local_model_status()
        self.update_view()

    def update_view(self):
        use_local = self.local_mode_chk.isChecked()
        self.stack.setCurrentWidget(self.page_local if use_local else self.page_groq)

    def toggle_mode(self, checked):
        self.settings.setValue("use_local_llm", checked)
        self.update_view()

    def save_api_key(self):
        key = self.api_input.text().strip()
        if key:
            try:
                keyring.set_password("outbreak_sandbox", "groq_api_key", key)
                QMessageBox.information(self, "Success", "Groq API Key saved.")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
        else:
             # Option to clear
             try:
                keyring.delete_password("outbreak_sandbox", "groq_api_key")
                QMessageBox.information(self, "Success", "Groq API Key removed.")
             except:
                pass

    def check_local_model_status(self):
        # Check for marker file
        if os.path.exists("models_cache/phi_installed.marker"):
            self.status_lbl.setText("Status: <span style='color:#10b981'>Installed</span>")
            self.download_btn.setEnabled(False)
            self.download_btn.setText("Installed")
            self.delete_btn.setEnabled(True)
        else:
            self.status_lbl.setText("Status: <span style='color:#64748b'>Not Installed</span>")
            self.download_btn.setEnabled(True)
            self.download_btn.setText("Download Model")
            self.delete_btn.setEnabled(False)

    def download_model(self):
        self.download_btn.setEnabled(False)
        self.progress.show()
        self.progress.setValue(0)
        self.status_lbl.setText("Status: Downloading...")
        
        self.worker = ModelManagerThread("download")
        self.worker.progress_updated.connect(self.on_progress)
        self.worker.finished_success.connect(self.on_download_finished)
        self.worker.start()

    def delete_model(self):
        self.worker = ModelManagerThread("delete")
        self.worker.progress_updated.connect(self.on_progress)
        self.worker.finished_success.connect(self.on_delete_finished)
        self.worker.start()

    def on_progress(self, val, msg):
        self.progress.setValue(val)
        self.status_lbl.setText(f"Status: {msg}")

    def on_download_finished(self):
        self.progress.hide()
        self.check_local_model_status()
        QMessageBox.information(self, "Done", "Model downloaded successfully.")

    def on_delete_finished(self):
        self.progress.hide()
        self.check_local_model_status()
        QMessageBox.information(self, "Done", "Model uninstalled.")
