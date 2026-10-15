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

    def mostrar_spinner_carga(self, mostrar: bool):
        if mostrar:
            self.vista.lbl_spinner.setVisible(True)
            self.vista.movie.start()  # Empieza a reproducir la animación del GIF
            self.vista.btn_analizar.setEnabled(False)
        else:
            self.vista.movie.stop()   # Detiene la animación
            self.vista.lbl_spinner.setVisible(False)
            self.vista.btn_analizar.setEnabled(True)


