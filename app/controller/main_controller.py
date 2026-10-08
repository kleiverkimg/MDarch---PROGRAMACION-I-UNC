# app/controller/main_controller.py

from pathlib import Path
from PyQt6.QtWidgets import QMainWindow
from PyQt6 import uic
from PyQt6.uic import loadUi  # <--- Se importa directamente desde PyQt6.uic
from app.model.main_model import MainModel
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem

class MainController(QMainWindow):
    def __init__(self):
        super().__init__()
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
        self.btnLoadSample.clicked.connect(self.load_sample_data)
        self.btnRunAnalysis.clicked.connect(self.execute_forensic_analysis)

    def handle_login(self):
        user = self.textUser.text().strip()
        pwd = self.textPass.text().strip()
        
        if user == "admin" and pwd == "admin123":
            self.lblLoginMsg.setText("✓ Autenticación Exitosa")
            self.mainTabWidget.setCurrentIndex(1) # Cambia a la pestaña "Cargar Muestra"
        else:
            self.lblLoginMsg.setText("❌ Credenciales inválidas (Prueba: admin / admin123)")

    def load_sample_data(self):
        self.txtFilePath.setText("documento.pdf.exe")

    def execute_forensic_analysis(self):
        # Poblar tabla de Hex Dump con bytes de la muestra MZ/PE
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

        # Redirigir a la pestaña de análisis MITRE ATT&CK
        self.mainTabWidget.setCurrentIndex(2)
