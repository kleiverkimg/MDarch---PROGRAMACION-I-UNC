class MainModel:
    def __init__(self):
        self.datos = []

    def obtener_mensaje(self, texto: str) -> str:
        if not texto.strip():
            return "Por favor, escribe algo."
        return f"Procesado correctamente: {texto.upper()}"