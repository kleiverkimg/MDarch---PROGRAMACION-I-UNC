from pathlib import Path
from PyQt6 import uic
from PyQt6.uic import loadUi
from model.main_model import MainModel
from model.database import Database
from PyQt6.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QTableWidgetItem, 
    QGraphicsOpacityEffect, 
    QFileDialog
)
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve

class MainController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        
        # Carga dinámica del archivo XML UI
        base_dir = Path(__file__).resolve().parent.parent
        ui_path = base_dir / "views" / "main_window.ui"
        loadUi(str(ui_path), self)

        self.model = MainModel()
        
        # Ajustar ancho de columnas para el Visor Hexadecimal
        self.tblHexDump.setColumnWidth(0, 100)
        self.tblHexDump.setColumnWidth(1, 350)
        self.tblHexDump.setColumnWidth(2, 180)

        # Conexión de señales/eventos
        self.btnLogin.clicked.connect(self.handle_login)
        self.btnLogout.clicked.connect(self.handle_logout)
        self.btnLoadSample.clicked.connect(self.load_sample_data)
        self.btnBrowse.clicked.connect(self.handle_browse_file)
        self.btnRunAnalysis.clicked.connect(self.execute_forensic_analysis)

        # Conectar el menú lateral izquierdo con el stackedContent derecho
        self.menuList.currentRowChanged.connect(self.stackedContent.setCurrentIndex)
        self.menuList.setCurrentRow(0) # Iniciar en "Cargar Muestra"

    def handle_browse_file(self):
        # Mapeo de formatos comunes según la selección del combo
        file_type = self.comboFileType.currentText().strip().upper()
        
        if "EXE" in file_type or "PE" in file_type or "BINARIO" in file_type:
            filters = "Ejecutables (*.exe *.dll *.bin);;Todos los archivos (*.*)"
        elif "PDF" in file_type:
            filters = "Documentos PDF (*.pdf);;Todos los archivos (*.*)"
        elif "IMAGEN" in file_type or "IMG" in file_type or "PNG" in file_type or "JPG" in file_type:
            filters = "Imágenes (*.png *.jpg *.jpeg *.bmp);;Todos los archivos (*.*)"
        elif "LOG" in file_type or "TXT" in file_type or "TEXTO" in file_type:
            filters = "Archivos de texto (*.txt *.log *.csv);;Todos los archivos (*.*)"
        else:
            filters = "Todos los archivos (*.*)"

        # Abre el explorador de archivos nativo del SO
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar muestra para análisis",
            "",
            filters
        )

        if file_path:
            self.txtFilePath.setText(file_path)

    def handle_login(self):
        user = self.textUser.text().strip()
        pwd = self.textPass.text().strip()

        if self.db.validate_user(user, pwd):
            self.lblLoginMsg.setText("✓ Autenticación Exitosa")
            self.animate_login_transition()
        else:
            self.lblLoginMsg.setText("❌ Credenciales inválidas (Prueba: admin / admin123)")

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
        self.tblHexDump.setRowCount(4)
        sample_rows = [
            ("00000000", "4D 5A 90 00 03 00 00 00 04 00 00 00 FF FF 00 00", "MZ.............."),
            ("00000010", "B8 00 00 00 00 00 00 00 40 00 00 00 00 00 00 00", "........@......."),
            ("00000020", "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00", "................"),
            ("00000030", "00 00 00 00 00 00 00 00 00 00 00 00 80 00 00 00", "................")
        ]
        
        for row_idx, (offset, hex_val, ascii_val) in enumerate(sample_rows):
            self.tblHexDump.setItem(row_idx, 0, QTableWidgetItem(offset))
            self.tblHexDump.setItem(row_idx, 1, QTableWidgetItem(hex_val))
            self.tblHexDump.setItem(row_idx, 2, QTableWidgetItem(ascii_val))

        self.mainTabWidget.setCurrentIndex(2)