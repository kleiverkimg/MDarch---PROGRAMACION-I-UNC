import sys
from PyQt6.QtWidgets import QApplication
from controller.main_controller import MainController

def main():
    app = QApplication(sys.argv)
    controlador = MainController()
    if controlador.iniciar():
        sys.exit(app.exec())
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()