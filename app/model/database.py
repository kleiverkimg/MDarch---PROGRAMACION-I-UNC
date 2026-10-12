import os
from sqlcipher3 import dbapi2 as sqlite3  # Importa sqlcipher con la misma interfaz de sqlite3

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DB_PATH = os.path.join(BASE_DIR, 'metadatos_motor.db')
ENCRYPTION_KEY = "ClaveSecretaForenseUNC2026*"
class Database:
    def __init__(self):
        self.db_path = DB_PATH
        self.encryption_key = ENCRYPTION_KEY
        self.init_database()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # APLICAR EL CIFRAJE AES-256 REQUERIDO POR SQLCIPHER
        # Esta línea debe ejecutarse inmediatamente después de cada conexión nueva
        cursor.execute(f"PRAGMA key = '{self.encryption_key}';")
        
        # Validar que la llave sea correcta haciendo una consulta de prueba
        cursor.execute("SELECT count(*) FROM sqlite_master;")
        cursor.fetchall()
        
        return conn

    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Tabla de Usuarios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)

        # Tabla de Historial Forense
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS forensic_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                declared_extension TEXT NOT NULL,
                real_extension TEXT NOT NULL,
                anomaly_detected BOOLEAN NOT NULL,
                mitre_tactic TEXT,
                mitre_technique TEXT,
                description TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 1. Tabla de Formatos (Identificación principal por Magic Bytes)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS formatos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,          -- Ej: 'PDF', 'JPEG', 'PNG'
                extension TEXT NOT NULL,       -- Ej: '.pdf', '.jpg'
                magic_bytes TEXT NOT NULL,     -- Ej: '255044462D' para %PDF-
                descripcion TEXT               -- Detalle opcional del formato
            )
        """)

        # 2. Tabla de Parámetros y Estrategias de Búsqueda (Soporta múltiples formas por formato)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS parametros_extraccion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                formato_id INTEGER NOT NULL,   -- Relación con la tabla formatos
                forma_nombre TEXT NOT NULL,    -- Ej: 'PDF_Diccionario_Info' o 'PDF_XMP_Metadata'
                estrategia_busqueda TEXT NOT NULL, -- Ej: 'BUSQUEDA_TOKENS', 'PARSE_XML', 'EXIF_IFD'
                patron_busqueda TEXT NOT NULL, -- Ej: '/Author (' o '<dc:creator>'
                longitud_max INTEGER DEFAULT 50, -- Cuántos bytes leer tras hallar el patrón
                FOREIGN KEY (formato_id) REFERENCES formatos(id)
            )
        """)

        # --- INSERCIÓN DE DATOS INICIALES (SEMILLAS) ---

        # Insertar Formato PDF
        cursor.execute("""
            INSERT OR IGNORE INTO formatos (id, nombre, extension, magic_bytes, descripcion)
            VALUES (1, 'PDF', '.pdf', '255044462D', 'Documento Portátil de Adobe (Comienza con %PDF-)');
        """)

        # Insertar Formato JPEG (para cuando lo implementes más adelante)
        cursor.execute("""
            INSERT OR IGNORE INTO formatos (id, nombre, extension, magic_bytes, descripcion)
            VALUES (2, 'JPEG', '.jpg', 'FFD8', 'Imagen JPEG (Comienza con los Magic Bytes FFD8)');
        """)

        # Insertar Parámetros para la Forma 1 del PDF: Diccionario /Info clásico (Título, Autor, Creador, Fechas)
        parametros_pdf_info = [
            (1, 'PDF_Diccionario_Info', 'BUSQUEDA_TOKENS', '/Title', 60),
            (1, 'PDF_Diccionario_Info', 'BUSQUEDA_TOKENS', '/Author', 60),
            (1, 'PDF_Diccionario_Info', 'BUSQUEDA_TOKENS', '/Creator', 60),
            (1, 'PDF_Diccionario_Info', 'BUSQUEDA_TOKENS', '/Producer', 60),
            (1, 'PDF_Diccionario_Info', 'BUSQUEDA_TOKENS', '/CreationDate', 30)
        ]
        cursor.executemany("""
            INSERT INTO parametros_extraccion (formato_id, forma_nombre, estrategia_busqueda, patron_busqueda, longitud_max)
            VALUES (?, ?, ?, ?, ?)
        """, parametros_pdf_info)

        # Insertar Parámetros para la Forma 2 del PDF: Metadatos XMP / XML modernos
        parametros_pdf_xmp = [
            (1, 'PDF_XMP_Metadata', 'PARSE_XML_TAG', '<dc:title>', 100),
            (1, 'PDF_XMP_Metadata', 'PARSE_XML_TAG', '<dc:creator>', 100),
            (1, 'PDF_XMP_Metadata', 'PARSE_XML_TAG', '<xmp:CreateDate>', 50)
        ]
        cursor.executemany("""
            INSERT INTO parametros_extraccion (formato_id, forma_nombre, estrategia_busqueda, patron_busqueda, longitud_max)
            VALUES (?, ?, ?, ?, ?)
        """, parametros_pdf_xmp)
        # Insertar usuario administrador por defecto (con contraseña protegida por hash)
        # Aquí puedes usar hashlib.sha256 en lugar de texto plano
        import hashlib
        default_pwd_hash = hashlib.sha256("Admin123#".encode()).hexdigest()

        cursor.execute("""
            INSERT OR IGNORE INTO users (username, password_hash) 
            VALUES ('admin', ?)
        """, (default_pwd_hash,))

        conn.commit()
        conn.close()

    def validate_user(self, username, password):
        import hashlib
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?", (username, pwd_hash))
        user = cursor.fetchone()
        conn.close()
        return user is not None

    def save_report(self, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO forensic_reports 
            (filename, declared_extension, real_extension, anomaly_detected, mitre_tactic, mitre_technique, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("archivo"),
            data.get("analisis_cabecera", {}).get("extension_declarada"),
            data.get("analisis_cabecera", {}).get("extension_real"),
            data.get("analisis_cabecera", {}).get("anomalia_detectada"),
            data.get("mitre_attck", {}).get("tactica"),
            data.get("mitre_attck", {}).get("tecnica"),
            data.get("mitre_attck", {}).get("descripcion")
        ))
        conn.commit()
        conn.close()

    def obtener_reglas_formato(self, formato_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT forma_nombre, estrategia_busqueda, patron_busqueda, longitud_max 
            FROM parametros_extraccion 
            WHERE formato_id = ?
        """, (formato_id,))
        reglas = cursor.fetchall()
        conn.close()
        return reglas