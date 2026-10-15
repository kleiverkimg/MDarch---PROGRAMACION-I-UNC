import subprocess
import sys
import os
import re
import yara
from mitreattack.stix20 import MitreAttackData
from controller.mappings import MAPEO_IOC_MITRE
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
        self.dir = directorio_binarios

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

    def extraer_iocs(self, text_data: str):
        lista_blanca = [ "ns.adobe.com", "w3.org", "purl.org", "adobe.com", "schemas.microsoft.com", "openxmlformats.org" ]
        
        iocs = {
            "urls": [],
            "ips": [],
            "dominios": [],
            "hashes": {
                "md5": [],
                "sha1": [],
                "sha256": []
            },
            "comandos": []
        }

        # 2. Extracción de URLs (http, https, ftp, etc.)
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        urls_encontradas = re.findall(url_pattern, text_data, re.IGNORECASE)

        urls_filtradas = []
        for url in urls_encontradas:
            # Verificamos si alguna palabra clave de la lista blanca está contenida en la URL
            es_blanco = False
            for dominio in lista_blanca:
                if dominio in url.lower():
                    es_blanco = True
                    break
            
            if not es_blanco:
                urls_filtradas.append(url)

        # Asignar a tu diccionario de IoCs únicos
        iocs["urls"] = list(set(urls_filtradas))

        # 3. Extracción de Direcciones IP (IPv4)
        ip_pattern = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
        iocs["ips"] = list(set(re.findall(ip_pattern, text_data)))

        # 4. Extracción de Dominios (excluyendo IPs coincidentes)
        domain_pattern = r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b'
        potential_domains = re.findall(domain_pattern, text_data, re.IGNORECASE)
        iocs["dominios"] = list(set([d.lower() for d in potential_domains if not re.match(ip_pattern, d)]))

        # 5. Extracción de Hashes (Se buscan tanto en texto como directamente en el hex original)
        md5_pattern = r'\b[a-fA-F0-9]{32}\b'
        sha1_pattern = r'\b[a-fA-F0-9]{40}\b'
        sha256_pattern = r'\b[a-fA-F0-9]{64}\b'

        iocs["hashes"]["md5"] = list(set(re.findall(md5_pattern, text_data)))
        iocs["hashes"]["sha1"] = list(set(re.findall(sha1_pattern, text_data)))
        iocs["hashes"]["sha256"] = list(set(re.findall(sha256_pattern, text_data)))

        # 6. Extracción de Comandos de Ejecución / Patrones Sospechosos
        cmd_keywords = [
            r'powershell(?:\.exe)?', r'cmd(?:\.exe)?', r'wscript', r'cscript',
            r'rundll32', r'regsvr32', r'mshta', r'certutil', r'bash', r'sh',
            r'/bin/sh', r'/bin/bash', r'eval\(', r'exec\('
        ]
        command_pattern = '|'.join(cmd_keywords)
        iocs["comandos"] = list(set(re.findall(command_pattern, text_data, re.IGNORECASE)))

        return iocs
    
    def validar_cabecera_archivo(self, hex_header: str, extension_esperada: str):
        # 1. Normalizar la cadena hexadecimal y la extensión
        hex_header = hex_header.strip().lower()
        extension_esperada = extension_esperada.strip().lower().lstrip('.')
        
        # Base de datos de firmas comunes (Magic Numbers) en hexadecimal
        # Las firmas se comparan por prefijo (longitud variable según el tipo)
        firmas_conocidas = {
            'pdf': ['25504446'],                                # %PDF
            'png': ['89504e470d0a1a0a'],                        # .PNG
            'jpg': ['ffd8ffe0', 'ffd8ffe1', 'ffd8ffee', 'ffd8ffdb'], # JPEG / JPG
            'zip': ['504b0304', '504b0506', '504b0708'],        # ZIP / DOCX / XLSX / JAR
            'rar': ['526172211a0700', '526172211a070100'],      # RAR
            'pdf': ['25504446'],                                # PDF
            'exe': ['4d5a'],                                    # MZ (Windows PE / Executable)
            'elf': ['7f454c46'],                                # ELF (Linux Executable)
            'pdf': ['25504446'],                                # PDF
            'doc': ['d0cf11e0a1b11ae1'],                        # OLE2 (Word, Excel, PPT antiguos)
            'xls': ['d0cf11e0a1b11ae1'],
            'ppt': ['d0cf11e0a1b11ae1'],
            '7z':  ['377abcaf271c'],                            # 7-Zip
            'tar': ['7573746172'],                              # ustar (TAR archive)
            'pdf': ['25504446']
        }

        resultado = {
            "extension_esperada": extension_esperada,
            "hex_recibido": hex_header,
            "tipo_detectado": "Desconocido",
            "coincide": False,
            "mensaje": ""
        }

        # 2. Identificar a qué tipo de archivo pertenece el header recibido
        tipo_detectado = None
        for ext, firmas in firmas_conocidas.items():
            for firma in firmas:
                if hex_header.startswith(firma):
                    tipo_detectado = ext
                    break
            if tipo_detectado:
                break

        resultado["tipo_detectado"] = tipo_detectado if tipo_detectado else "No reconocido"

        # 3. Validar si la extensión esperada coincide con el tipo detectado
        if not tipo_detectado:
            resultado["mensaje"] = "Advertencia: La firma hexadecimal no coincide con ningún tipo de archivo conocido (posible archivo desconocido o corrupto)."
            return resultado

        # Manejo especial para extensiones de Office modernas (docx, xlsx, pptx) que usan contenedor ZIP
        formatos_zip = ['docx', 'xlsx', 'pptx', 'odt', 'ods', 'odp']
        if extension_esperada in formatos_zip and tipo_detectado == 'zip':
            resultado["coincide"] = True
            resultado["mensaje"] = f"Válido: La extensión .{extension_esperada} utiliza un contenedor ZIP y su cabecera es correcta."
            return resultado

        # Comparación estándar
        if tipo_detectado == extension_esperada:
            resultado["coincide"] = True
            resultado["mensaje"] = f"Válido: La cabecera corresponde exactamente con la extensión .{extension_esperada}."
        else:
            resultado["coincide"] = False
            resultado["mensaje"] = f"¡Alerta de Anomalía! La cabecera pertenece a un archivo tipo '{tipo_detectado}', pero la extensión esperada es .{extension_esperada} (Posible suplantación u ocultamiento de archivos)."

        return resultado

    def analisis_yara(self, ruta_pdf: str) -> dict:
        ruta_reglas_yar = os.path.join(self.dir, "rules.yar") 
        if not os.path.exists(ruta_pdf) or not os.path.exists(ruta_reglas_yar):
            return {"error": "El archivo PDF o el archivo de reglas YARA no existen en la ruta especificada."}

        try:
            # 1. Compilar las reglas YARA desde el archivo de texto
            rules = yara.compile(filepath=ruta_reglas_yar)
            
            # 2. Ejecutar el análisis (match) sobre el archivo PDF
            matches = rules.match(ruta_pdf)
            
            hallazgos_yara = []
            for match in matches:
                cadenas_info = []
                # Recorrer cada coincidencia de cadena y sus instancias internas
                for string_match in match.strings:
                    # string_match tiene: identifier (ej. "$js1") y .instances
                    for instance in string_match.instances:
                        cadenas_info.append({
                            "offset": instance.offset,
                            "identificador": string_match.identifier,
                            "contenido": instance.matched_data.decode('utf-8', errors='ignore') if isinstance(instance.matched_data, bytes) else instance.matched_data
                        })

                hallazgos_yara.append({
                    "regla_activada": match.rule,
                    "namespace": match.namespace,
                    "tags": match.tags,
                    "metadatos": match.meta,
                    "cadenas_coincidentes": cadenas_info
                })

            return {
                "total_coincidencias": len(hallazgos_yara),
                "resultados": hallazgos_yara
            }

        except yara.Error as e:
            return {"error": f"Error interno en el motor YARA: {str(e)}"}

    def correlacionar_todo_con_mitre(self, iocs_extraidos: dict, resultados_yara: dict, ruta_json_stix: str = "enterprise-attack.json"):
        try:
            attack_data = MitreAttackData(ruta_json_stix)
        except Exception as e:
            return {"error": f"No se pudo cargar el archivo STIX de MITRE ({ruta_json_stix}): {str(e)}"}

        hallazgos_mitre = []
        tecnicas_procesadas = set()

        # 1. Procesar evidencias del Módulo 3.A (IoCs y comandos)
        comandos_texto = " ".join(iocs_extraidos.get("comandos", [])).lower()
        urls_texto = " ".join(iocs_extraidos.get("urls", [])).lower()
        texto_iocs = comandos_texto + " " + urls_texto

        for patron, tech_id in MAPEO_IOC_MITRE.items():
            if patron in texto_iocs and tech_id not in tecnicas_procesadas:
                tecnicas_procesadas.add(tech_id)
                hallazgos_mitre.append(self.agregar_info_tecnica(attack_data, tech_id, origen="IoC", gatillado_por=patron))

        # 2. Procesar evidencias del Módulo 3.B (Reglas YARA activadas)
        for match_yara in resultados_yara.get("resultados", []):
            nombre_regla = match_yara.get("regla_activada", "").lower()
            
            # Buscar coincidencia directa con el nombre de la regla en el diccionario
            for patron, tech_id in MAPEO_IOC_MITRE.items():
                if patron in nombre_regla and tech_id not in tecnicas_procesadas:
                    tecnicas_procesadas.add(tech_id)
                    hallazgos_mitre.append(self.agregar_info_tecnica(attack_data, tech_id, origen="YARA", gatillado_por=match_yara.get("regla_activada")))

        return {
            "total_correlaciones": len(hallazgos_mitre),
            "correlaciones": hallazgos_mitre
        }

    def agregar_info_tecnica(self, attack_data, tech_id: str, origen: str, gatillado_por: str) -> dict:
        try:
            # CORRECCIÓN AQUÍ: Usamos el método oficial para buscar por ID de ATT&CK
            technique_obj = attack_data.get_object_by_attack_id(tech_id, "attack-pattern")
        except Exception:
            technique_obj = None
        
        tacticas = []
        nombre = "Técnica no encontrada en STIX local"
        descripcion = "Sin descripción disponible."
        
        if technique_obj:
            # Extraer atributos del objeto devuelto por la librería
            nombre = getattr(technique_obj, "name", "Desconocido")
            descripcion = getattr(technique_obj, "description", "Sin descripción disponible.")
            
            # Extraer fases tácticas (Kill Chain Phases)
            kill_chain = getattr(technique_obj, "kill_chain_phases", [])
            if kill_chain:
                tacticas = [
                    phase.get("phase_name") if isinstance(phase, dict) else getattr(phase, "phase_name", "") 
                    for phase in kill_chain
                ]

        return {
            "tecnica_id": tech_id,
            "nombre": nombre,
            "origen_deteccion": origen,
            "gatillado_por": gatillado_por,
            "tacticas": tacticas,
            "descripcion": descripcion[:300] + "..." if descripcion else ""
        }

    def evaluar_cid(self, correlaciones_mitre: list) -> dict:
        impacto_cid = {
            "confidencialidad": {"nivel": "Bajo", "motivos": []},
            "integridad": {"nivel": "Bajo", "motivos": []},
            "disponibilidad": {"nivel": "Bajo", "motivos": []}
        }

        # Ponderadores o reglas heurísticas basadas en las técnicas detectadas
        for item in correlaciones_mitre:
            tech_id = item.get("tecnica_id")
            nombre = item.get("nombre")

            # 1. Ejecución de comandos / JavaScript / Lanzadores (Afecta principalmente Integridad y Confidencialidad)
            if tech_id in ["T1059.001", "T1059.003", "T1059.007", "T1204.002"]:
                impacto_cid["integridad"]["nivel"] = "Alto"
                impacto_cid["integridad"]["motivos"].append(f"La técnica {tech_id} ({nombre}) permite la ejecución arbitraria de comandos o scripts, alterando el flujo esperado del sistema.")
                
                impacto_cid["confidencialidad"]["nivel"] = "Medio"
                impacto_cid["confidencialidad"]["motivos"].append(f"La ejecución no autorizada ({tech_id}) podría exponer información sensible del usuario o entorno.")

            # 2. Archivos incrustados o Phishing / Ingress (Afecta Integridad)
            elif tech_id in ["T1566.001", "T1105"]:
                impacto_cid["integridad"]["nivel"] = "Alto"
                impacto_cid["integridad"]["motivos"].append(f"La técnica {tech_id} ({nombre}) facilita la descarga o transporte de payloads maliciosos externos.")

            # 3. Protocolos de red / C2 (Afecta Confidencialidad)
            elif tech_id == "T1071.001":
                impacto_cid["confidencialidad"]["nivel"] = "Alto"
                impacto_cid["confidencialidad"]["motivos"].append(f"La detección de comunicación web externa ({tech_id}) sugiere posible exfiltración de datos o control remoto.")

            # 4. Explotación de vulnerabilidades / Heap Spray (Afecta Disponibilidad)
            elif tech_id == "T1203":
                impacto_cid["disponibilidad"]["nivel"] = "Crítico"
                impacto_cid["disponibilidad"]["motivos"].append(f"La técnica {tech_id} ({nombre}) puede provocar caídas del lector (Crash) o denegación de servicio local.")

        return impacto_cid
    
    def generar_mitigaciones(self, correlaciones_mitre: list) -> list:
        recomendaciones = set()

        # Banco de mitigaciones asociadas a cada técnica
        mitigaciones_por_tecnica = {
            "T1059.001": "Deshabilitar la ejecución de scripts de PowerShell no firmados en las políticas de GPO de la organización.",
            "T1059.003": "Restringir el acceso directo al intérprete de comandos (cmd.exe) para usuarios estándar mediante listas de control de acceso (ACL).",
            "T1059.007": "Desactivar la ejecución de JavaScript de forma predeterminada en los visores de PDF (ej. Adobe Reader Config).",
            "T1204.002": "Bloquear la ejecución automática de acciones de lanzamiento (/Launch) y advertir al usuario ante aperturas de archivos adjuntos no verificados.",
            "T1566.001": "Implementar pasarelas de correo y filtros de seguridad perimétricos para bloquear documentos PDF con objetos incrustados sospechosos.",
            "T1105": "Monitorear y restringir el uso de utilidades nativas del sistema como certutil.exe o bitsadmin.exe mediante reglas de EDR/Sysmon.",
            "T1071.001": "Configurar proxies web y firewalls perimétricos para inspeccionar y bloquear conexiones HTTP/HTTPS hacia dominios o IPs no reputadas.",
            "T1203": "Mantener actualizados los parches de seguridad del software lector de PDF para evitar ataques de corrupción de memoria."
        }

        for item in correlaciones_mitre:
            tech_id = item.get("tecnica_id")
            if tech_id in mitigaciones_por_tecnica:
                recomendaciones.add(mitigaciones_por_tecnica[tech_id])

        # Si no se detectó ninguna técnica específica pero el análisis se ejecutó
        if not recomendaciones:
            recomendaciones.add("Mantener buenas prácticas de higiene digital: no abrir archivos PDF provenientes de fuentes desconocidas y usar sandboxing.")

        return list(recomendaciones)