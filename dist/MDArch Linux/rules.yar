rule PDF_Malicious_JavaScript_Execution {
    meta:
        description = "Detecta ejecucion automatica de JavaScript o acciones sospechosas al abrir el PDF"
        severidad = "Alta"
    strings:
        $js1 = "/JS" nocase
        $js2 = "/JavaScript" nocase
        $action = "/OpenAction" nocase
        $launch = "/Launch" nocase
    condition:
        ($js1 or $js2) and ($action or $launch)
}

rule PDF_Actual_Embedded_File_Malware {
    meta:
        description = "Detecta la presencia real de archivos incrustados ocultos en el PDF"
        severidad = "Media"
    strings:
        $emb = "/EmbeddedFile" nocase
        $ef = "/EF" nocase
    condition:
        $emb and $ef
}

rule PDF_Suspicious_Shell_Commands {
    meta:
        description = "Detecta comandos de consola o scripts incrustados dentro del documento"
        severidad = "Crítica"
    strings:
        $cmd1 = "powershell" nocase
        $cmd2 = "cmd.exe" nocase
        $cmd3 = "wscript" nocase
        $cmd4 = "cscript" nocase
    condition:
        any of them
}