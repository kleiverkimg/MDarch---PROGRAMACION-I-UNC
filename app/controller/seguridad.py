import re

class Seguridad:
    def validarTexto(self, texto:str, tipo:str):
        if not isinstance(texto, str):
            return False, "La entrada debe ser una cadena de texto."

        # 2. Eliminar espacios al inicio y final
        texto = texto.strip()

        # 3. Reglas generales contra contenido malicioso
        patrones_prohibidos = [
            r"(--|\|\||;)",          # Comentarios o separadores SQL
            r"(DROP|SELECT|INSERT|DELETE|UPDATE)\b",  # Palabras SQL peligrosas
            r"<.*?>",                # Etiquetas HTML/JS
            r"(script|onerror|onload)", # Eventos JS
            r"[&|><]",               # Operadores de shell
        ]
        for patron in patrones_prohibidos:
            if re.search(patron, texto, re.IGNORECASE):
                return False, "La entrada contiene contenido potencialmente malicioso."

        # 4. Validaciones específicas
        if tipo == "usuario":
            if not re.match(r"^[A-Za-z0-9_.-]{3,20}$", texto):
                return False, "El usuario solo puede contener letras, números, guiones, puntos y guiones bajos (3-20 caracteres)."

        elif tipo == "password":
            # Longitud mínima
            if len(texto) < 8:
                return False, "La contraseña debe tener al menos 8 caracteres."
            # Debe contener mayúsculas, minúsculas, números y símbolos
            if not re.search(r"[A-Z]", texto):
                return False, "La contraseña debe contener al menos una letra mayúscula."
            if not re.search(r"[a-z]", texto):
                return False, "La contraseña debe contener al menos una letra minúscula."
            if not re.search(r"[0-9]", texto):
                return False, "La contraseña debe contener al menos un número."
            if not re.search(r"[^A-Za-z0-9]", texto):
                return False, "La contraseña debe contener al menos un carácter especial."
            if " " in texto:
                return False, "La contraseña no puede contener espacios."

        else:
            return False, "Tipo de validación no reconocido."

        return True, texto