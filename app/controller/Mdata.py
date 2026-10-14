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

    def ejecutar_extraccion(self, ruta_archivo):
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
            "-tipo", "2"
        ]

        comandoHexadecimal = [
            self.ruta_ejecutable,
            "-dir", str(ruta_archivo),
            "-tipo", "1"
        ]
        comandoBinario = [
            self.ruta_ejecutable,
            "-dir", str(ruta_archivo),
            "-tipo", "3"
        ]

        try:
            resultado = subprocess.run(
                comando,
                capture_output=True,
                check=True
            )

            resultadoHexadecimal = subprocess.run(
                comandoHexadecimal,
                capture_output=True,
                check=True
            )

            resultadoBinario = subprocess.run(
                comandoBinario,
                capture_output=True,
                check=True
            )
            salida_decodificada = resultado.stdout.decode('utf-8', errors='ignore')
            salida_decodificadaHexadecimal = resultadoHexadecimal.stdout.decode('utf-8', errors='ignore')
            salida_decodificadaBinaria = resultadoBinario.stdout.decode('utf-8', errors='ignore')
            return {
                "exito": True,
                "salida": [salida_decodificada,salida_decodificadaHexadecimal,salida_decodificadaBinaria],
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
        resultado_c = self.ejecutar_extraccion(ruta_archivo)
        
        if not resultado_c["exito"]:
            return {"exito": False, "error": resultado_c["error"]}

        contenido_archivo, contenido_hexadecimal, contenido_binario = resultado_c["salida"]
        metadatos_encontrados = {}
        
        # Recorremos cada regla dictada por la base de datos
        for forma, estrategia, patron, longitud_max in reglas_bd:
            pos = contenido_archivo.find(patron)
            if pos != -1:
                inicio_valor = pos + len(patron)
                fin_valor = min(inicio_valor + longitud_max, len(contenido_archivo))
                valor_extraido = contenido_archivo[inicio_valor:fin_valor].strip()  
                
                cierre = valor_extraido.find(")")          
                # Limpiar caracteres comunes de sintaxis PDF
                valor_extraido = valor_extraido[1:cierre].strip() 

                clave_resultado = f"{forma} -> {patron}"
                metadatos_encontrados[clave_resultado] = valor_extraido
            else:
                metadatos_encontrados[f"{forma} -> {patron}"] = "No detectado"

        return {"exito": True, "resultados": [metadatos_encontrados, contenido_archivo, contenido_hexadecimal, contenido_binario]}