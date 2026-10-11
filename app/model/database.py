import os
from sqlcipher3 import dbapi2 as sqlite3  # Importa sqlcipher con la misma interfaz de sqlite3

class Database:
    def __init__(self, db_name="mdarch.db", encryption_key="ClaveSecretaForenseUNC2026*"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_dir, db_name)
        self.encryption_key = encryption_key
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

        # Tabla de Archivos permitidos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS archivos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                magic_bytes TEXT NOT NULL,
                estrategia_busqueda TEXT,
                patrones_claves TEXT
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insertar usuario administrador por defecto (con contraseña protegida por hash)
        # Aquí puedes usar hashlib.sha256 en lugar de texto plano
        import hashlib
        default_pwd_hash = hashlib.sha256("admin123".encode()).hexdigest()

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