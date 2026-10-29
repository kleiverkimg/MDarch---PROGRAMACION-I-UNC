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

        # Tabla de Logs (Actividad del sistema / Relacionada con Usuarios)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_register TEXT NOT NULL,
                date DATETIME DEFAULT CURRENT_TIMESTAMP,
                description TEXT,
                id_user INTEGER,
                FOREIGN KEY (id_user) REFERENCES users(id)
            )
        """)

        # Tabla de Catálogo MITRE (Técnicas y Tácticas de Ataque)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mittre (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tech_id TEXT UNIQUE NOT NULL,
                level TEXT,
                purpose TEXT,
                recomendation TEXT
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
            CREATE TABLE IF NOT EXISTS formats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,          -- Ej: 'PDF', 'JPEG', 'PNG'
                extension TEXT NOT NULL,       -- Ej: '.pdf', '.jpg'
                magic_bytes TEXT NOT NULL,     -- Ej: '255044462D' para %PDF-
                description TEXT               -- Detalle opcional del formato
            )
        """)

        # 2. Tabla de Parámetros y Estrategias de Búsqueda (Soporta múltiples formas por formato)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS extraction_parameters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                format_id INTEGER NOT NULL,   -- Relación con la tabla formatos
                format_name TEXT NOT NULL,    -- Ej: 'PDF_Diccionario_Info' o 'PDF_XMP_Metadata'
                search_strategy TEXT NOT NULL, -- Ej: 'BUSQUEDA_TOKENS', 'PARSE_XML', 'EXIF_IFD'
                search_pattern TEXT NOT NULL, -- Ej: '/Author (' o '<dc:creator>'
                max_lenght INTEGER DEFAULT 50, -- Cuántos bytes leer tras hallar el patrón
                FOREIGN KEY (format_id) REFERENCES formats(id)
            )
        """)

        # --- INSERCIÓN DE DATOS INICIALES (SEMILLAS) ---

        # Insertar Formato PDF
        cursor.execute("""
            INSERT OR IGNORE INTO formats (id, name, extension, magic_bytes, description)
            VALUES (1, 'PDF', '.pdf', '255044462D', 'Documento Portátil de Adobe (Comienza con %PDF-)');
        """)

        # Insertar Formato JPEG (para cuando lo implementes más adelante)
        cursor.execute("""
            INSERT OR IGNORE INTO formats (id, name, extension, magic_bytes, description)
            VALUES (2, 'JPEG', '.jpg', 'FFD8', 'Imagen JPEG (Comienza con los Magic Bytes FFD8)');
        """)

        # Semillas iniciales para la tabla MITTRE
        mittre_seeds = [
            ('T1036', 'Alto', 'Ocultamiento de extensión o identidad de archivos', 'Validar siempre los Magic Bytes en lugar de confiar en la extensión del usuario.'),
            ('T1027', 'Medio', 'Ofuscación de archivos o información interna', 'Realizar escaneo de patrones y desofuscar metadatos antes de procesar.')
        ]
        cursor.executemany("""
            INSERT OR IGNORE INTO mittre (tech_id, level, purpose, recomendation)
            VALUES (?, ?, ?, ?)
        """, mittre_seeds)

        # Insertar Parámetros para la Forma 1 del PDF: Diccionario /Info clásico (Título, Autor, Creador, Fechas)
        parametros_pdf_info = [
            (1, 'PDF_Diccionario_Info', 'BUSQUEDA_TOKENS', '/Title', 60),
            (1, 'PDF_Diccionario_Info', 'BUSQUEDA_TOKENS', '/Author', 60),
            (1, 'PDF_Diccionario_Info', 'BUSQUEDA_TOKENS', '/Creator', 60),
            (1, 'PDF_Diccionario_Info', 'BUSQUEDA_TOKENS', '/Producer', 60),
            (1, 'PDF_Diccionario_Info', 'BUSQUEDA_TOKENS', '/CreationDate', 30)
        ]
        cursor.executemany("""
            INSERT INTO extraction_parameters (format_id, format_name, search_strategy, search_pattern, max_length)
            VALUES (?, ?, ?, ?, ?)
        """, parametros_pdf_info)

        # Insertar Parámetros para la Forma 2 del PDF: Metadatos XMP / XML modernos
        parametros_pdf_xmp = [
            (1, 'PDF_XMP_Metadata', 'PARSE_XML_TAG', '<dc:title>', 100),
            (1, 'PDF_XMP_Metadata', 'PARSE_XML_TAG', '<dc:creator>', 100),
            (1, 'PDF_XMP_Metadata', 'PARSE_XML_TAG', '<xmp:CreateDate>', 50)
        ]
        cursor.executemany("""
            INSERT INTO extraction_parameters (format_id, format_name, search_strategy, search_pattern, max_length)
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

    def obtener_reglas_formato(self, format_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT format_name, search_strategy, search_pattern, max_length 
            FROM extraction_parameters 
            WHERE format_id = ?
        """, (format_id,))
        reglas = cursor.fetchall()
        conn.close()
        return reglas