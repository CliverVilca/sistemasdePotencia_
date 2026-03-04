import sys
from app.ui.main_window import PowerSystemPro
from PyQt6.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Iniciar la Suite Profesional
    window = PowerSystemPro()
    window.showMaximized()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
