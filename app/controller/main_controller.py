from pathlib import Path
from PyQt6 import uic
from PyQt6.uic import loadUi
from model.database import Database
from controller.seguridad import Seguridad
from controller.Mdata import MdataController  # <--- Importamos tu controlador Mdata
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QGraphicsOpacityEffect
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve

class MainController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.mdata_controller = MdataController() # <--- Inicializamos el controlador de C
        
        base_dir = Path(__file__).resolve().parent.parent
        ui_path = base_dir / "views" / "main_window.ui"

        loadUi(str(ui_path), self)
        
        self.tblHexDump.setColumnWidth(0, 100)
        self.tblHexDump.setColumnWidth(1, 350)
        self.tblHexDump.setColumnWidth(2, 180)

        self.btnLogin.clicked.connect(self.handle_login)
        self.btnLogout.clicked.connect(self.handle_logout)
        self.btnLoadSample.clicked.connect(self.load_sample_data)
        self.btnRunAnalysis.clicked.connect(self.execute_forensic_analysis)

        self.menuList.currentRowChanged.connect(self.stackedContent.setCurrentIndex)
        self.menuList.setCurrentRow(0)

    def handle_login(self):
        resp1, user = Seguridad.validarTexto(self.textUser.text(), "usuario")
        if not resp1:
            self.lblLoginMsg.setText(f"❌ {resp1}")
            return
        
        resp2, pwd = Seguridad.validarTexto(self.textPass.text(), "password")
        if not resp2:
            self.lblLoginMsg.setText(f"❌ {resp2}")
            return
        
        if self.db.validate_user(user, pwd):
            self.lblLoginMsg.setText("✓ Autenticación Exitosa")
            self.animate_login_transition()
        else:
            self.lblLoginMsg.setText("❌ Credenciales inválidas")

    def animate_login_transition(self):
        self.effect = QGraphicsOpacityEffect(self.stackedMain)
        self.stackedMain.setGraphicsEffect(self.effect)
        
        self.anim = QPropertyAnimation(self.effect, b"opacity")
        self.anim.setDuration(500)
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        
        def on_animation_finished():
            self.stackedMain.setCurrentIndex(1)
            self.effect.setOpacity(1.0)
            self.stackedMain.setGraphicsEffect(None)
            
        self.anim.finished.connect(on_animation_finished)
        self.anim.start()

    def handle_logout(self):
        self.textUser.clear()
        self.textPass.clear()
        self.stackedMain.setCurrentIndex(0)

    def load_sample_data(self):
        self.txtFilePath.setText("seleccione un archivo")

    def execute_forensic_analysis(self):
        ruta_archivo = self.txtFilePath.text().strip()
        
        # Validación básica si no hay ruta seleccionada
        if not ruta_archivo or ruta_archivo == "seleccione un archivo":
            # Si quieres mantener el respaldo visual o probar con un archivo por defecto:
            ruta_archivo = "desarrollo.pdf" # O tu archivo de prueba

        # 1. Obtenemos las reglas de la BD para PDF (formato_id = 1)
        reglas = self.db.obtener_reglas_formato(formato_id=1)

        # 2. Ejecutamos el análisis dinámico usando C y las reglas obtenidas
        analisis = self.mdata_controller.analizar_con_parametros_bd(ruta_archivo, reglas)

        self.tblHexDump.setRowCount(0)
        
        if analisis["exito"]:
            resultados = analisis["resultados"]
            self.tblHexDump.setRowCount(len(resultados))
            
            row_idx = 0
            for etiqueta, valor in resultados.items():
                self.tblHexDump.setItem(row_idx, 0, QTableWidgetItem("PDF Meta"))
                self.tblHexDump.setItem(row_idx, 1, QTableWidgetItem(etiqueta))
                self.tblHexDump.setItem(row_idx, 2, QTableWidgetItem(str(valor)))
                row_idx += 1
        else:
            # En caso de error, mostramos el mensaje en la tabla
            self.tblHexDump.setRowCount(1)
            self.tblHexDump.setItem(0, 0, QTableWidgetItem("Error"))
            self.tblHexDump.setItem(0, 1, QTableWidgetItem(analisis.get("error", "Desconocido")))
            self.tblHexDump.setItem(0, 2, QTableWidgetItem("N/A"))

        # Redirigir a la pestaña de resultados en tu interfaz
        self.mainTabWidget.setCurrentIndex(2)