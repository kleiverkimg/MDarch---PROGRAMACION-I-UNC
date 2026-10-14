import os
import hashlib
from model.database import Database
from controller.seguridad import Seguridad
from controller.Mdata import MdataController
from views.main_view import MainView, LoginDialog, ConfigDialog
from PyQt6.QtWidgets import QDialog

class MainController:
    """Controlador principal que conecta el modelo de base de datos con la vista."""
    def __init__(self):
        self.db = Database()
        self.mdata = MdataController()
        self.vista = MainView()

        # Vinculacion de callbacks y eventos
        self.vista.callback_ejecutar_analisis = self.ejecutar_analisis_forense
        self.vista.btn_config.clicked.connect(self.abrir_dialogo_configuracion)

    def iniciar(self):
        """Muestra primero el login. Si las credenciales son validas, abre la consola principal."""
        dialogo_login = LoginDialog(callback_autenticacion=self.autenticar_operador)
        if dialogo_login.exec() == QDialog.DialogCode.Accepted:
            self.vista.show()
            return True
        return False

    def autenticar_operador(self, usuario, password):
        """Valida entradas contra inyecciones y comprueba credenciales en la base de datos cifrada."""
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
        """Valida y da de alta un nuevo usuario con hash SHA-256."""
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
        """Recupera los reportes forenses almacenados en forensic_reports."""
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

    def ejecutar_analisis_forense(self, ruta_archivo):
        """Invoca el motor C, evalua firmas binarias y genera el dictamen."""
        # 1. Obtener las reglas de metadatos desde la BD (por defecto PDF formato_id=1)
        reglas = self.db.obtener_reglas_formato(formato_id=1)
        res_extraccion = self.mdata.analizar_con_parametros_bd(ruta_archivo, reglas)

        if not res_extraccion.get("exito"):
            return

        metadatos_dict, contenido_text, contenido_hex, contenido_bin = res_extraccion["resultados"]
        nombre_fichero = os.path.basename(ruta_archivo)
        ext_declarada = os.path.splitext(nombre_fichero)[1].lower()

        # 2. Heuristica de discrepancia entre extension declarada y cabecera binaria real
        es_anomalia = False
        ext_real = ext_declarada
        mitre_data = {}
        riesgo_data = {}
        recomendacion_txt = ""

        # Verificacion basica de firma binaria
        cabecera_hex = contenido_hex[:20].upper().replace(" ", "")
        
        if "4D5A" in cabecera_hex:  # Firma MZ de ejecutable PE
            ext_real = ".exe"
        elif "25504446" in cabecera_hex:  # Firma %PDF
            ext_real = ".pdf"
        elif "89504E47" in cabecera_hex:  # Firma PNG
            ext_real = ".png"

        if ext_declarada != ext_real and ext_real != "":
            es_anomalia = True
            mitre_data = {
                "es_anomalia": True,
                "estado": "ANOMALIA CRITICA: DISCREPANCIA ESTRUCTURAL",
                "tactica": "Defense Evasion (TA0005)",
                "tecnica": "T1036.001 - Masquerading: Extension Discrepancy",
                "descripcion": f"El archivo simula ser {ext_declarada}, pero los Magic Bytes demuestran que es un archivo {ext_real}."
            }
            riesgo_data = {
                "confidencialidad": "Medio (Posible exfiltracion)",
                "integridad": "Critico (Cabecera falsificada)",
                "disponibilidad": "Bajo",
                "score": 85
            }
            recomendacion_txt = (
                "1. Aislar inmediatamente la muestra en entorno de sandbox.\n"
                "2. Bloquear la ejecucion directa; el archivo esta enmascarando su tipo real.\n"
                "3. Registrar el hash SHA-256 en la lista negra perimetral."
            )
        else:
            mitre_data = {
                "es_anomalia": False,
                "estado": "ESTRUCTURA INTEGRA",
                "tactica": "Ninguna detectada",
                "tecnica": "Sin patrones maliciosos conocidos",
                "descripcion": "La firma de cabecera binaria coincide de forma consistente con la extension del fichero."
            }
            riesgo_data = {
                "confidencialidad": "Bajo",
                "integridad": "Integro",
                "disponibilidad": "Normal",
                "score": 10
            }
            recomendacion_txt = (
                "1. La cabecera es valida y coherente.\n"
                "2. El archivo puede procesarse bajo los protocolos habituales de la organizacion."
            )

        # 3. Guardar el reporte en la base de datos cifrada
        reporte_db = {
            "archivo": nombre_fichero,
            "analisis_cabecera": {
                "extension_declarada": ext_declarada,
                "extension_real": ext_real,
                "anomalia_detectada": es_anomalia
            },
            "mitre_attck": {
                "tactica": mitre_data["tactica"],
                "tecnica": mitre_data["tecnica"],
                "descripcion": mitre_data["descripcion"]
            }
        }
        self.db.save_report(reporte_db)
        print(metadatos_dict)
        # 4. Enviar datos a la vista para iniciar la aparicion secuencial
        self.vista.ejecutar_proceso_secuencial_interfaz({
            "hex_dump": contenido_hex[:3000],
            "bin_stream": contenido_bin[:1500],
            "text_stream": contenido_text[:1500],            
            "mitre": mitre_data,
            "metadatos": metadatos_dict,
            "riesgo": riesgo_data,
            "recomendaciones": recomendacion_txt
        })