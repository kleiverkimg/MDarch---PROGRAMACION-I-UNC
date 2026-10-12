import subprocess
import sys
import os

class MdataController:
    def __init__(self, directorio_binarios=None):
        if directorio_binarios is None:
            # Obtener la raíz del proyecto (subiendo dos niveles desde app/controller/)
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            directorio_binarios = base_dir

        if sys.platform.startswith("win"):
            self.nombre_ejecutable = "MD_HB.exe"
        else:
            self.nombre_ejecutable = "MD_HB.bin"
            
        self.ruta_ejecutable = os.path.join(directorio_binarios, self.nombre_ejecutable)

    def ejecutar_extraccion(self, ruta_archivo, tipo=1, bytes_to_read=None):
        if not os.path.exists(self.ruta_ejecutable):
            return {
                "exito": False,
                "error": f"El binario no se encuentra en la ruta: {self.ruta_ejecutable}"
            }

        if not os.path.exists(ruta_archivo):
            return {
                "exito": False,
                "error": f"El archivo objetivo no existe: {ruta_archivo}"
            }

        comando = [
            self.ruta_ejecutable,
            "-dir", str(ruta_archivo),
            "-tipo", str(tipo)
        ]

        if bytes_to_read is not None:
            comando.extend(["-bytes", str(bytes_to_read)])

        try:
            resultado = subprocess.run(
                comando,
                capture_output=True,
                text=True,
                check=True
            )
            return {
                "exito": True,
                "salida": resultado.stdout,
                "error": None
            }
        except subprocess.CalledProcessError as e:
            return {
                "exito": False,
                "salida": e.stdout,
                "error": e.stderr
            }

    def analizar_con_parametros_bd(self, ruta_archivo, reglas_bd):
        # Usamos tipo 2 para obtener el texto plano/caracteres y facilitar la búsqueda de tokens
        resultado_c = self.ejecutar_extraccion(ruta_archivo, tipo=2)

        if not resultado_c["exito"]:
            return {"exito": False, "error": resultado_c["error"]}

        contenido_archivo = resultado_c["salida"]
        metadatos_encontrados = {}

        # Recorremos cada regla dictada por la base de datos
        for forma, estrategia, patron, longitud_max in reglas_bd:
            pos = contenido_archivo.find(patron)
            if pos != -1:
                inicio_valor = pos + len(patron)
                fin_valor = min(inicio_valor + longitud_max, len(contenido_archivo))
                valor_extraido = contenido_archivo[inicio_valor:fin_valor].strip()
                # Limpiar caracteres comunes de sintaxis PDF
                valor_extraido = valor_extraido.lstrip("(").rstrip(")")
                
                clave_resultado = f"{forma} -> {patron}"
                metadatos_encontrados[clave_resultado] = valor_extraido
            else:
                metadatos_encontrados[f"{forma} -> {patron}"] = "No detectado"

        return {"exito": True, "resultados": metadatos_encontrados}