import os
import sys
from dotenv import load_dotenv
from PySide6.QtGui import QIcon, QFontDatabase
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from .main_window import MainWindow


def main():
    try:
        load_dotenv()
    except Exception:
        pass
    
    app = QApplication(sys.argv)

    fonts_dir = os.path.join(os.path.dirname(__file__), "assets", "fonts")
    if os.path.isdir(fonts_dir):
        for fname in os.listdir(fonts_dir):
            if fname.lower().endswith(('.ttf', '.otf', '.woff', '.woff2')):
                path = os.path.join(fonts_dir, fname)
                try:
                    QFontDatabase.addApplicationFont(path)
                except Exception:
                    pass

    icon_path = os.path.join(os.path.dirname(__file__), "assets", "icons", "app_icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    app.setStyleSheet("""
    /* Basic layout */
    QMainWindow { background: #f8fafc; } /* slate-50 */
    QWidget { font-family: 'Noto Sans', 'Inter', sans-serif; color: #0f172a; font-size: 14px; }
    
    /* Typography */
    QLabel { color: #334155; }
    QLabel#h1 { font-family: 'Space Grotesk'; font-size: 48px; font-weight: 800; color: #0f172a; }
    QLabel#h2 { font-family: 'Space Grotesk'; font-size: 24px; font-weight: 700; color: #0f172a; }
    QLabel#h3 { font-family: 'Space Grotesk'; font-size: 18px; font-weight: 600; color: #334155; }
    QLabel#subtitle { color: #64748b; font-size: 16px; }
    
    /* Material Icons */
    QLabel[class="icon"] { font-family: 'Material Symbols Outlined'; font-size: 24px; color: #475569; }
    QPushButton[class="icon-btn"] { font-family: 'Material Symbols Outlined'; font-size: 20px; }

    /* Cards / Glass Panels */
    QFrame#card { 
        background: white; 
        border: 1px solid #e2e8f0; 
        border-radius: 16px; 
    }
    
    /* Buttons */
    QPushButton { 
        padding: 10px 20px; 
        border-radius: 12px; 
        background: white; 
        border: 1px solid #cbd5e1; 
        color: #475569; 
        font-weight: 600;
        font-family: 'Space Grotesk';
    }
    QPushButton:hover { background: #f1f5f9; border-color: #94a3b8; color: #0f172a; }
    QPushButton:pressed { background: #e2e8f0; }

    QPushButton#primary { 
        background: #0d9488;
        color: white; 
        border: 1px solid #0f766e;
        font-size: 16px;
    }
    QPushButton#primary:hover {
        background: #14b8a6;
    }
    
    /* Inputs */
    QLineEdit, QSpinBox {
        padding: 8px 12px;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        background: #ffffff;
        selection-background-color: #0d9488;
    }
    QLineEdit:focus, QSpinBox:focus {
        border: 2px solid #0d9488;
    }

    /* Lists/Tables */
    QListWidget, QTableWidget { 
        background: rgba(255,255,255,0.6); 
        border: 1px solid #e2e8f0; 
        border-radius: 12px;
        outline: none;
    }
    QHeaderView::section {
        background-color: #f1f5f9;
        padding: 4px;
        border: none;
        font-weight: bold;
        color: #475569;
    }
    QTableWidget::item { padding: 4px; }
    
    /* Scrollbars */
    QScrollBar:vertical {
        background: transparent;
        width: 8px;
        margin: 0px;
    }
    QScrollBar::handle:vertical {
        background: #cbd5e1;
        min-height: 20px;
        border-radius: 4px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
    """)

    w = MainWindow()
    w.show()

    platform = os.environ.get("QT_QPA_PLATFORM", "")
    if platform == "offscreen":
        QTimer.singleShot(1000, app.quit)

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
