MAPEO_IOC_MITRE = {
    # Intérpretes de comandos y ejecución
    "powershell": "T1059.001",
    "cmd.exe": "T1059.003",
    "cmd /c": "T1059.003",
    "wscript": "T1059.005",
    "cscript": "T1059.005",
    
    # Objetos y acciones típicas maliciosas dentro de la estructura de un PDF
    "/js": "T1059.007",         # JavaScript (Ejecución mediante JavaScript en PDF)
    "/javascript": "T1059.007", # JavaScript en objetos PDF
    "/launch": "T1204.002",     # User Execution: Malicious File (Acciones de lanzamiento automático)
    "/embeddedfile": "T1566.001", # Phishing: Spearphishing Attachment (Archivos incrustados)
    "/openaction": "T1204.002",   # Acciones automáticas al abrir el documento
    
    # Descarga de herramientas / Ingress
    "certutil": "T1105",        # Ingress Tool Transfer (uso de certutil para bajar Payloads)
    "bitsadmin": "T1197",       # BITS Jobs para descarga lateral o persistente
    "rundll32": "T1218.011",    # Signed Binary Proxy Execution
    
    # Red y C2 (Si el módulo 3.A detecta URLs o IPs externas)
    "http://": "T1071.001",     # Application Layer Protocol: Web Protocols
    "https://": "T1071.001",
    
    # Coincidencias basadas en el nombre o patrones de las Reglas YARA (Módulo 3.B)
    "pdf_javascript_suspicioso": "T1059.007",
    "pdf_embedded_file_or_stream": "T1566.001",
    "pdf_exploit_heap_spray": "T1203"  # Exploitation for Client Execution
}
