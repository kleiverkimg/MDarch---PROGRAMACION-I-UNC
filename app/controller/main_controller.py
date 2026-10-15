import os
import hashlib
from model.database import Database
from controller.seguridad import Seguridad
from controller.Mdata import MdataController
from views.main_view import MainView, LoginDialog, ConfigDialog
from PyQt6.QtWidgets import QDialog
from datetime import datetime, timezone

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
        # 1. Obtener las reglas de metadatos desde la BD (por defecto PDF formato_id=1)
        reglas = self.db.obtener_reglas_formato(formato_id=1)
        res_extraccion = self.mdata.analizar_con_parametros_bd(ruta_archivo, reglas)

        if not res_extraccion.get("exito"):
            return

        metadatos_dict, contenido_text, contenido_hex, contenido_bin = res_extraccion["resultados"]
        nombre_fichero = os.path.basename(ruta_archivo)
        ext_declarada = os.path.splitext(nombre_fichero)[1].lower()

        # 2. Heuristica de discrepancia entre extension declarada y cabecera binaria real
        
        riesgo_data = {}
        recomendacion_txt = ""
        
        analisis_cabecera = self.mdata.validar_cabecera_archivo(contenido_hex[:20], ext_declarada)
        iocs_extraidos = self.mdata.extraer_iocs(contenido_text)
        resultados_yara = self.mdata.analisis_yara(ruta_archivo)
        mitre_data = self.mdata.correlacionar_todo_con_mitre(iocs_extraidos, resultados_yara)
        evaluacion_riesgo_cid = self.mdata.evaluar_cid(mitre_data.get("correlaciones", []))
        plan_mitigacion = self.mdata.generar_mitigaciones(mitre_data.get("correlaciones", []))

        # 3. Guardar el reporte en la base de datos cifrada
        reporte_db = {
            "archivo": nombre_fichero,
            "timestamp_analisis": datetime.now(timezone.utc).isoformat(),
            "modulo_1_2_metadatos": metadatos_dict,       # Resultado de tu función de metadatos/hash
            "analisis_cabecera": analisis_cabecera,       # Resultado de validar_cabecera_archivo()
            "modulo_3a_ioc": iocs_extraidos,             # Resultado de extraer_iocs_desde_hex()
            "modulo_3b_yara": resultados_yara,            # Resultado de ejecutar_modulo_yara()
            "modulo_4_mitre_attck": mitre_data["correlaciones"], # De tu función unificada
            "modulo_5_evaluacion_cid": evaluacion_riesgo_cid,          # Resultado de evaluar_cid()
            "modulo_6_mitigacion": plan_mitigacion                     # Resultado de generar_mitigaciones()
        }

        print(reporte_db)

        # Guardar de forma robusta en la BD
        # self.db.save_report(reporte_db)

        # 4. Enviar datos a la vista para iniciar la aparicion secuencial
        self.vista.ejecutar_proceso_secuencial_interfaz({
             "hex_dump": contenido_hex,
             "bin_stream": contenido_bin,
             "text_stream": contenido_text,  
             "cabecera": analisis_cabecera,
             "ioc": iocs_extraidos,
             "yara": resultados_yara,
             "mitre": mitre_data["correlaciones"],
             "metadatos": metadatos_dict,
             "riesgo": evaluacion_riesgo_cid,
             "recomendaciones": plan_mitigacion
        })