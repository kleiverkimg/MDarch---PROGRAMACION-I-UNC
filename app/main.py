import sys
from PyQt6.QtWidgets import QApplication
from app.controller.main_controller import MainController

def main():
    app = QApplication(sys.argv)
    
    # Crear la instancia del controlador principal
    window = MainController()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()