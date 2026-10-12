import sys
import os
import ctypes
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from controller.main_controller import MainController

# Identificador de aplicacion para que Windows fije el icono en la barra de tareas
try:
    myappid = "mdarch.forensics.system.1.0"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

def main():
    app = QApplication(sys.argv)
    
    # Ruta absoluta al icono ubicado en la carpeta views
    base_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(base_dir, "views", "icono.png")
    
    app_icon = QIcon(icon_path)
    app.setWindowIcon(app_icon)
    
    # Crear la instancia del controlador principal y asignar icono a la ventana
    window = MainController()
    window.setWindowIcon(app_icon)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()