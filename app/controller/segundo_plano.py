import os
from datetime import datetime, timezone
from PyQt6.QtCore import QThread, pyqtSignal

class ForensicWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, main_controller, ruta_archivo):
        super().__init__()
        self.controller = main_controller
        self.ruta_archivo = ruta_archivo

    def run(self):
        try:
            # 1. Obtener las reglas de metadatos desde la BD (por defecto PDF formato_id=1)
            reglas = self.controller.db.obtener_reglas_formato(formato_id=1)
            res_extraccion = self.controller.mdata.analizar_con_parametros_bd(self.ruta_archivo, reglas)

            if not res_extraccion.get("exito"):
                raise FileNotFoundError("Archivo de prueba no encontrado")

            metadatos_dict, contenido_text, contenido_hex, contenido_bin = res_extraccion["resultados"]
            nombre_fichero = os.path.basename(self.ruta_archivo)
            ext_declarada = os.path.splitext(nombre_fichero)[1].lower()

            # 2. Heuristica de discrepancia entre extension declarada y cabecera binaria real
            analisis_cabecera = self.controller.mdata.validar_cabecera_archivo(contenido_hex[:20], ext_declarada)
            iocs_extraidos = self.controller.mdata.extraer_iocs(contenido_text)
            resultados_yara = self.controller.mdata.analisis_yara(self.ruta_archivo)
            mitre_data = self.controller.mdata.correlacionar_todo_con_mitre(iocs_extraidos, resultados_yara)
            evaluacion_riesgo_cid = self.controller.mdata.evaluar_cid(mitre_data.get("correlaciones", []))
            plan_mitigacion = self.controller.mdata.generar_mitigaciones(mitre_data.get("correlaciones", []))

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
            # self.controller.db.save_report(reporte_db)

            # 4. Enviar datos a la vista para iniciar la aparicion secuencial
            paquete_datos = {
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
            }

            self.finished.emit(paquete_datos)

        except FileNotFoundError as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(str(e))