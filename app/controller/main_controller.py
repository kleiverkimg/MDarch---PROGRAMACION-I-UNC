import os
import hashlib
from PyQt6.QtWidgets import QDialog
from datetime import datetime, timezone
from model.database import Database
from controller.seguridad import Seguridad
from controller.Mdata import MdataController
from controller.segundo_plano import ForensicWorker
from views.main_view import MainView, LoginDialog, ConfigDialog
class MainController:
    def __init__(self):
        self.db = Database()
        self.mdata = MdataController()
        self.vista = MainView()

        # Vinculacion de callbacks y eventos
        self.vista.callback_ejecutar_analisis = self.disparar_analisis
        self.vista.btn_config.clicked.connect(self.abrir_dialogo_configuracion)

    def iniciar(self):
        dialogo_login = LoginDialog(callback_autenticacion=self.autenticar_operador)
        if dialogo_login.exec() == QDialog.DialogCode.Accepted:
            self.vista.show()
            return True
        return False

    def autenticar_operador(self, usuario, password):
        ok_u, msg_u = Seguridad.validarTexto(usuario, "usuario")
        if not ok_u:
            return False, msg_u

        ok_p, msg_p = Seguridad.validarTexto(password, "password")
        if not ok_p:
            return False, msg_p

        if self.db.validate_user(usuario, password):
            return True, "Autenticacion correcta"
        return False, "Usuario o contrasena incorrectos."

    def registrar_nuevo_operador(self, usuario, password):
        ok_u, msg_u = Seguridad.validarTexto(usuario, "usuario")
        if not ok_u:
            return False, msg_u

        ok_p, msg_p = Seguridad.validarTexto(password, "password")
        if not ok_p:
            return False, msg_p

        try:
            pwd_hash = hashlib.sha256(password.encode()).hexdigest()
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (usuario, pwd_hash))
            conn.commit()
            conn.close()
            return True, "Operador registrado exitosamente."
        except Exception as e:
            return False, f"Error al guardar: {str(e)}"

    def obtener_historial_logs(self):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT timestamp, filename, real_extension, anomaly_detected, mitre_technique FROM forensic_reports ORDER BY id DESC")
            filas = cursor.fetchall()
            conn.close()
            return filas
        except Exception:
            return []

    def abrir_dialogo_configuracion(self):
        diag = ConfigDialog(
            parent=self.vista,
            callback_crear_usuario=self.registrar_nuevo_operador,
            callback_obtener_logs=self.obtener_historial_logs
        )
        diag.exec()

    def disparar_analisis(self, ruta_archivo):        
        # Opcional: Mostrar un indicador de carga (Spinner / Progress Bar) en la UI
        self.mostrar_spinner_carga(True)
        self.vista.btn_analizar.setEnabled(False) # Evitar múltiples clicks

        # Instanciamos el hilo en segundo plano
        self.worker = ForensicWorker(self, ruta_archivo)
        
        # Conectamos la señal de término a una función que actualice la interfaz
        self.worker.finished.connect(self.manejar_resultados_completos)
        self.worker.error.connect(self.manejar_error_analisis)
        
        # Iniciamos el hilo (esto libera inmediatamente a la ventana principal para que no se congele)
        self.worker.start()

    def manejar_resultados_completos(self, paquete_datos):
        self.mostrar_spinner_carga(False)
        self.vista.btn_analizar.setEnabled(True)
        
        # Enviamos los datos consolidados a la interfaz tal como lo hacías antes
        self.vista.ejecutar_proceso_secuencial_interfaz(paquete_datos)

    def manejar_error_analisis(self, mensaje_error):
        self.mostrar_spinner_carga(False)
        self.vista.btn_analizar.setEnabled(True)
        print(f"[!] Error durante el análisis en segundo plano: {mensaje_error}")

    def mostrar_spinner_carga(self, mostrar: bool):
        if mostrar:
            self.vista.lbl_spinner.raise_()
            self.vista.lbl_spinner.setVisible(True)
            self.vista.movie.start()  # Empieza a reproducir la animación del GIF
            self.vista.btn_analizar.setEnabled(False)
        else:
            self.vista.movie.stop()   # Detiene la animación
            self.vista.lbl_spinner.setVisible(False)
            self.vista.btn_analizar.setEnabled(True)


