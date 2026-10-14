import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QLineEdit,
    QTextEdit,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFileDialog,
    QDialog,
    QProgressBar,
    QScrollArea,
    QMessageBox
)
from PyQt6.QtCore import Qt, QTimer

CONFIG_TEMA = {
    "oscuro": {
        "fondo_ventana": "#0d1117",
        "fondo_panel": "#161b22",
        "borde_panel": "#30363d",
        "texto_principal": "#e6edf3",
        "texto_secundario": "#8b949e",
        "color_acento": "#38bdf8",
        "color_acento_hover": "#0284c7",
        "fondo_boton": "#21262d",
        "fondo_boton_hover": "#30363d",
        "fondo_input": "#090d13",
        "borde_radio": "4px",
        "alerta_rojo": "#f85149",
        "fondo_rojo_alerta": "#2b1419",
        "alerta_verde": "#2ea043",
        "fondo_verde_alerta": "#0f231a",
        "alerta_neutra": "#8b949e",
        "fondo_neutro_alerta": "#161b22",
        "fuente_interfaz": "Segoe UI",
        "fuente_codigo": "Consolas",
        "tamano_base": "13px",
        "tamano_titulos": "15px",
        "tamano_subtitulos": "12px",
        "tamano_etiquetas": "11px"
    },
    "claro": {
        "fondo_ventana": "#f6f8fa",
        "fondo_panel": "#ffffff",
        "borde_panel": "#d0d7de",
        "texto_principal": "#1f2328",
        "texto_secundario": "#656d76",
        "color_acento": "#0969da",
        "color_acento_hover": "#054da7",
        "fondo_boton": "#eaeef2",
        "fondo_boton_hover": "#afb8c1",
        "fondo_input": "#ffffff",
        "borde_radio": "4px",
        "alerta_rojo": "#cf222e",
        "fondo_rojo_alerta": "#ffebe9",
        "alerta_verde": "#1a7f37",
        "fondo_verde_alerta": "#dafbe1",
        "alerta_neutra": "#656d76",
        "fondo_neutro_alerta": "#f6f8fa",
        "fuente_interfaz": "Segoe UI",
        "fuente_codigo": "Consolas",
        "tamano_base": "13px",
        "tamano_titulos": "15px",
        "tamano_subtitulos": "12px",
        "tamano_etiquetas": "11px"
    }
}


class SeccionDesplegable(QFrame):
    """Contenedor de tipo acordeon con cabecera interactiva para colapsar o expandir."""
    def __init__(self, titulo, widget_contenido, parent=None):
        super().__init__(parent)
        self.setObjectName("seccion_desplegable")
        self.layout_contenedor = QVBoxLayout(self)
        self.layout_contenedor.setContentsMargins(0, 0, 0, 0)
        self.layout_contenedor.setSpacing(4)

        self.btn_cabecera = QPushButton(f"[-] {titulo}", self)
        self.btn_cabecera.setObjectName("btn_acordeon")
        self.btn_cabecera.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cabecera.clicked.connect(self.alternar_visibilidad)
        self.layout_contenedor.addWidget(self.btn_cabecera)

        self.contenido = widget_contenido
        self.layout_contenedor.addWidget(self.contenido)
        self.titulo_base = titulo
        self.esta_abierto = True

    def alternar_visibilidad(self):
        self.esta_abierto = not self.esta_abierto
        self.contenido.setVisible(self.esta_abierto)
        indicador = "[-]" if self.esta_abierto else "[+]"
        self.btn_cabecera.setText(f"{indicador} {self.titulo_base}")

    def abrir(self):
        self.esta_abierto = True
        self.contenido.setVisible(True)
        self.btn_cabecera.setText(f"[-] {self.titulo_base}")

    def cerrar(self):
        self.esta_abierto = False
        self.contenido.setVisible(False)
        self.btn_cabecera.setText(f"[+] {self.titulo_base}")


class LoginDialog(QDialog):
    """Ventana modal de autenticacion conectada a la logica del controlador."""
    def __init__(self, parent=None, callback_autenticacion=None):
        super().__init__(parent)
        self.callback_autenticacion = callback_autenticacion
        self.setWindowTitle("MDArch, Acceso Forense")
        self.setFixedSize(380, 260)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        lbl_titulo = QLabel("Autenticacion de Operador", self)
        lbl_titulo.setStyleSheet("font-size: 15px; font-weight: bold;")
        layout.addWidget(lbl_titulo)

        self.txt_usuario = QLineEdit(self)
        self.txt_usuario.setPlaceholderText("Nombre de usuario")
        layout.addWidget(self.txt_usuario)

        self.txt_password = QLineEdit(self)
        self.txt_password.setPlaceholderText("Contrasena de acceso")
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.txt_password)

        self.lbl_mensaje = QLabel("", self)
        self.lbl_mensaje.setStyleSheet("color: #f85149; font-size: 11px;")
        layout.addWidget(self.lbl_mensaje)

        self.btn_ingresar = QPushButton("Ingresar al Sistema", self)
        self.btn_ingresar.setObjectName("btn_accion_primaria")
        self.btn_ingresar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ingresar.clicked.connect(self.procesar_ingreso)
        layout.addWidget(self.btn_ingresar)

    def procesar_ingreso(self):
        usuario = self.txt_usuario.text().strip()
        password = self.txt_password.text().strip()

        if not usuario or not password:
            self.lbl_mensaje.setText("Complete ambos campos obligatorios.")
            return

        exito, mensaje = self.callback_autenticacion(usuario, password)
        if exito:
            self.accept()
        else:
            self.lbl_mensaje.setText(mensaje)

class ConfigDialog(QDialog):
    """Ventana de administracion para logs y creacion de usuarios."""
    def __init__(self, parent=None, callback_crear_usuario=None, callback_obtener_logs=None):
        super().__init__(parent)
        self.callback_crear_usuario = callback_crear_usuario
        self.callback_obtener_logs = callback_obtener_logs
        self.setWindowTitle("MDArch, Administracion y Logs")
        self.resize(750, 480)
        self.setModal(True)

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(16, 16, 16, 16)
        layout_principal.setSpacing(12)

        self.tabs_config = QTabWidget(self)

        # Pestana de historial forense
        self.tab_logs = QWidget()
        layout_logs = QVBoxLayout(self.tab_logs)
        layout_logs.setContentsMargins(10, 10, 10, 10)

        self.tbl_logs = QTableWidget(self)
        self.tbl_logs.setColumnCount(5)
        self.tbl_logs.setHorizontalHeaderLabels(["Fecha", "Archivo", "Ext. Real", "Anomalia", "Tecnica MITRE"])
        self.tbl_logs.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_logs.horizontalHeader().setStretchLastSection(True)
        self.tbl_logs.verticalHeader().setVisible(False)
        self.tbl_logs.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout_logs.addWidget(self.tbl_logs)
        self.tabs_config.addTab(self.tab_logs, "Historial Forense")

        # Pestana de usuarios
        self.tab_usuarios = QWidget()
        layout_usuarios = QVBoxLayout(self.tab_usuarios)
        layout_usuarios.setContentsMargins(16, 16, 16, 16)
        layout_usuarios.setSpacing(10)

        lbl_crear = QLabel("Alta de Operador Forense", self)
        lbl_crear.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout_usuarios.addWidget(lbl_crear)

        self.txt_nuevo_user = QLineEdit(self)
        self.txt_nuevo_user.setPlaceholderText("Usuario (3 a 20 caracteres)")
        layout_usuarios.addWidget(self.txt_nuevo_user)

        self.txt_nuevo_pass = QLineEdit(self)
        self.txt_nuevo_pass.setPlaceholderText("Contrasena robusta (mayusculas, numeros, simbolos)")
        self.txt_nuevo_pass.setEchoMode(QLineEdit.EchoMode.Password)
        layout_usuarios.addWidget(self.txt_nuevo_pass)

        self.btn_guardar_user = QPushButton("Registrar en Base de Datos", self)
        self.btn_guardar_user.setObjectName("btn_accion_primaria")
        self.btn_guardar_user.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_guardar_user.clicked.connect(self.procesar_alta_usuario)
        layout_usuarios.addWidget(self.btn_guardar_user)
        layout_usuarios.addStretch()

        self.tabs_config.addTab(self.tab_usuarios, "Gestion de Usuarios")
        layout_principal.addWidget(self.tabs_config)
        self.cargar_datos_historial()

    def procesar_alta_usuario(self):
        user = self.txt_nuevo_user.text().strip()
        pwd = self.txt_nuevo_pass.text().strip()

        if self.callback_crear_usuario:
            exito, mensaje = self.callback_crear_usuario(user, pwd)
            if exito:
                QMessageBox.information(self, "Registro", "Usuario registrado exitosamente.")
                self.txt_nuevo_user.clear()
                self.txt_nuevo_pass.clear()
            else:
                QMessageBox.warning(self, "Error de Validacion", mensaje)
        else:
            QMessageBox.information(self, "Modo Desconectado", "Funcion lista para conectar con la base de datos.")

    def cargar_datos_historial(self):
        if self.callback_obtener_logs:
            registros = self.callback_obtener_logs()
            self.tbl_logs.setRowCount(len(registros))
            for fila, reg in enumerate(registros):
                for col, valor in enumerate(reg):
                    self.tbl_logs.setItem(fila, col, QTableWidgetItem(str(valor)))

class MainView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tema_actual = "oscuro"
        self.callback_ejecutar_analisis = None
        self.inicializar_ventana()
        self.construir_interfaz()
        self.aplicar_tema(self.tema_actual)

    def inicializar_ventana(self):
        self.setWindowTitle("MDArch, Analizador Forense y Deteccion de Amenazas")
        self.resize(1200, 760)
        self.setMinimumSize(1000, 640)

    def construir_interfaz(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout_raiz = QVBoxLayout(self.central_widget)
        self.layout_raiz.setContentsMargins(16, 16, 16, 16)
        self.layout_raiz.setSpacing(12)

        # Barra superior
        self.layout_barra_superior = QHBoxLayout()
        self.lbl_titulo_app = QLabel("MDArch Forensics", self)
        self.lbl_titulo_app.setObjectName("lbl_titulo_app")
        self.lbl_subtitulo_app = QLabel("Inspeccion Binaria de Cabeceras", self)
        self.lbl_subtitulo_app.setObjectName("lbl_subtitulo_app")

        self.layout_barra_superior.addWidget(self.lbl_titulo_app)
        self.layout_barra_superior.addWidget(self.lbl_subtitulo_app)
        self.layout_barra_superior.addStretch()

        self.btn_tema = QPushButton("Modo Claro", self)
        self.btn_tema.setObjectName("btn_accion_secundaria")
        self.btn_tema.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_tema.clicked.connect(self.alternar_tema)
        self.layout_barra_superior.addWidget(self.btn_tema)

        self.btn_config = QPushButton("Configuracion", self)
        self.btn_config.setObjectName("btn_accion_secundaria")
        self.btn_config.setCursor(Qt.CursorShape.PointingHandCursor)
        self.layout_barra_superior.addWidget(self.btn_config)

        self.btn_salir = QPushButton("Cerrar Sesion", self)
        self.btn_salir.setObjectName("btn_accion_secundaria")
        self.btn_salir.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_salir.clicked.connect(self.close)
        self.layout_barra_superior.addWidget(self.btn_salir)

        self.layout_raiz.addLayout(self.layout_barra_superior)

        # Area principal
        self.layout_cuerpo = QHBoxLayout()
        self.layout_cuerpo.setSpacing(16)

        # Panel Izquierdo: Carga y Volcado C
        self.panel_izquierdo = QFrame(self)
        self.panel_izquierdo.setObjectName("panel_contenedor")
        self.layout_panel_izq = QVBoxLayout(self.panel_izquierdo)
        self.layout_panel_izq.setContentsMargins(14, 14, 14, 14)
        self.layout_panel_izq.setSpacing(10)
        self.construir_panel_izquierdo()

        # Panel Derecho: Analisis con Scroll y Acordeones
        self.panel_derecho = QFrame(self)
        self.panel_derecho.setObjectName("panel_contenedor")
        self.layout_panel_der = QVBoxLayout(self.panel_derecho)
        self.layout_panel_der.setContentsMargins(10, 10, 10, 10)
        self.layout_panel_der.setSpacing(8)
        self.construir_panel_derecho()

        self.layout_cuerpo.addWidget(self.panel_izquierdo, 42)
        self.layout_cuerpo.addWidget(self.panel_derecho, 58)
        self.layout_raiz.addLayout(self.layout_cuerpo)

    def construir_panel_izquierdo(self):
        lbl_seccion = QLabel("MUESTRA BINARIA", self)
        lbl_seccion.setObjectName("lbl_seccion_titulo")
        self.layout_panel_izq.addWidget(lbl_seccion)

        layout_selector = QHBoxLayout()
        layout_selector.setSpacing(8)

        self.txt_ruta_archivo = QLineEdit(self)
        self.txt_ruta_archivo.setPlaceholderText("Seleccione archivo (.pdf, .exe, .png)...")
        self.txt_ruta_archivo.setReadOnly(True)

        self.btn_examinar = QPushButton("Examinar", self)
        self.btn_examinar.setObjectName("btn_accion_secundaria")
        self.btn_examinar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_examinar.clicked.connect(self.abrir_dialogo_archivo)

        layout_selector.addWidget(self.txt_ruta_archivo)
        layout_selector.addWidget(self.btn_examinar)
        self.layout_panel_izq.addLayout(layout_selector)

        self.btn_analizar = QPushButton("Ejecutar Analisis Forense", self)
        self.btn_analizar.setObjectName("btn_accion_primaria")
        self.btn_analizar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_analizar.clicked.connect(self.disparar_analisis)
        self.layout_panel_izq.addWidget(self.btn_analizar)

        self.tabs_visor = QTabWidget(self)

        self.txt_hex_view = QTextEdit(self)
        self.txt_hex_view.setReadOnly(True)
        self.txt_hex_view.setPlaceholderText("Esperando volcado hexadecimal de C...")
        self.tabs_visor.addTab(self.txt_hex_view, "Volcado Hex")

        self.txt_bin_view = QTextEdit(self)
        self.txt_bin_view.setReadOnly(True)
        self.txt_bin_view.setPlaceholderText("Esperando flujo de bits crudo...")
        self.tabs_visor.addTab(self.txt_bin_view, "Flujo Binario")

        self.txt_text_view = QTextEdit(self)
        self.txt_text_view.setReadOnly(True)
        self.txt_text_view.setPlaceholderText("Esperando flujo de texto crudo...")
        self.tabs_visor.addTab(self.txt_text_view, "Flujo de Texto")

        self.layout_panel_izq.addWidget(self.tabs_visor)

    def construir_panel_derecho(self):
        lbl_der_titulo = QLabel("EXPEDIENTE FORENSE Y METADATOS", self)
        lbl_der_titulo.setObjectName("lbl_seccion_titulo")
        self.layout_panel_der.addWidget(lbl_der_titulo)

        # Scroll para permitir navegacion comoda de todos los bloques
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setObjectName("scroll_forense")
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        contenedor_scroll = QWidget()
        self.layout_acordeones = QVBoxLayout(contenedor_scroll)
        self.layout_acordeones.setContentsMargins(4, 4, 10, 4)
        self.layout_acordeones.setSpacing(10)

        # 1. Seccion Heuristica y MITRE
        self.card_mitre = QFrame()
        self.card_mitre.setObjectName("card_mitre")
        layout_m = QVBoxLayout(self.card_mitre)
        layout_m.setContentsMargins(12, 12, 12, 12)
        layout_m.setSpacing(6)

        self.lbl_mitre_estado = QLabel("ESTADO: EN ESPERA DE MUESTRA", self)
        self.lbl_mitre_estado.setObjectName("lbl_mitre_estado")
        self.lbl_mitre_tactica = QLabel("Tactica: Pendiente", self)
        self.lbl_mitre_tactica.setObjectName("lbl_mitre_sub")
        self.lbl_mitre_tecnica = QLabel("Tecnica: Pendiente", self)
        self.lbl_mitre_tecnica.setObjectName("lbl_mitre_sub")
        self.lbl_mitre_desc = QLabel("Cargue un archivo para iniciar la verificacion de firmas.", self)
        self.lbl_mitre_desc.setWordWrap(True)

        layout_m.addWidget(self.lbl_mitre_estado)
        layout_m.addWidget(self.lbl_mitre_tactica)
        layout_m.addWidget(self.lbl_mitre_tecnica)
        layout_m.addWidget(self.lbl_mitre_desc)

        self.sec_mitre = SeccionDesplegable("1. Diagnostico Heuristico y MITRE ATT&CK", self.card_mitre)
        self.layout_acordeones.addWidget(self.sec_mitre)

        # 2. Seccion Metadatos
        self.tbl_metadatos = QTableWidget()
        self.tbl_metadatos.setColumnCount(2)
        self.tbl_metadatos.setHorizontalHeaderLabels(["Propiedad / Token", "Valor Extraido"])
        self.tbl_metadatos.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_metadatos.horizontalHeader().setStretchLastSection(True)
        self.tbl_metadatos.verticalHeader().setVisible(False)
        self.tbl_metadatos.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_metadatos.setMinimumHeight(160)

        self.sec_metadatos = SeccionDesplegable("2. Metadatos de Estructura Binaria", self.tbl_metadatos)
        self.layout_acordeones.addWidget(self.sec_metadatos)

        # 3. Seccion Impacto Triada CID y Nivel de Riesgo
        card_cid = QFrame()
        card_cid.setObjectName("card_cid")
        layout_cid = QVBoxLayout(card_cid)
        layout_cid.setContentsMargins(12, 12, 12, 12)
        layout_cid.setSpacing(8)

        layout_stats = QHBoxLayout()
        self.lbl_confidencialidad = QLabel("Confidencialidad: Normal", self)
        self.lbl_integridad = QLabel("Integridad: En espera", self)
        self.lbl_disponibilidad = QLabel("Disponibilidad: Normal", self)
        layout_stats.addWidget(self.lbl_confidencialidad)
        layout_stats.addWidget(self.lbl_integridad)
        layout_stats.addWidget(self.lbl_disponibilidad)
        layout_cid.addLayout(layout_stats)

        self.lbl_riesgo_score = QLabel("Nivel de Riesgo Global: 0%", self)
        self.lbl_riesgo_score.setStyleSheet("font-weight: bold;")
        layout_cid.addWidget(self.lbl_riesgo_score)

        self.bar_riesgo = QProgressBar(self)
        self.bar_riesgo.setRange(0, 100)
        self.bar_riesgo.setValue(0)
        self.bar_riesgo.setTextVisible(True)
        layout_cid.addWidget(self.bar_riesgo)

        self.sec_cid = SeccionDesplegable("3. Impacto en Triada CID y Evaluacion de Riesgo", card_cid)
        self.layout_acordeones.addWidget(self.sec_cid)

        # 4. Seccion Recomendaciones de Mitigacion
        self.txt_recomendaciones = QTextEdit()
        self.txt_recomendaciones.setReadOnly(True)
        self.txt_recomendaciones.setMinimumHeight(100)
        self.txt_recomendaciones.setPlaceholderText("Recomendaciones tecnicas segun el vector de amenaza detectado.")

        self.sec_recomendaciones = SeccionDesplegable("4. Medidas y Recomendaciones de Mitigacion", self.txt_recomendaciones)
        self.layout_acordeones.addWidget(self.sec_recomendaciones)

        self.layout_acordeones.addStretch()
        scroll.setWidget(contenedor_scroll)
        self.layout_panel_der.addWidget(scroll)

    def abrir_dialogo_archivo(self):
        filtros = "Archivos Soportados (*.pdf *.exe *.png);;Todos los archivos (*.*)"
        ruta, _ = QFileDialog.getOpenFileName(self, "Seleccionar muestra para analisis", "", filtros)
        if ruta:
            self.txt_ruta_archivo.setText(ruta)

    def disparar_analisis(self):
        ruta = self.txt_ruta_archivo.text().strip()
        if not ruta:
            return

        # Si el controlador registro la funcion real, la ejecutamos
        if self.callback_ejecutar_analisis:
            self.callback_ejecutar_analisis(ruta)
        else:
            self.ejecutar_proceso_secuencial_interfaz({
                "hex_dump": "Lectura en espera de enlace.",
                "bin_stream": "Flujo en espera de enlace.",
                "text_stream": "Flujo en espera de enlace.",
                "mitre": {
                    "es_anomalia": False,
                    "estado": "POR DEFINIR (ENLACE PENDIENTE)",
                    "tactica": "Por definir en controlador",
                    "tecnica": "Por definir en controlador",
                    "descripcion": "Pendiente de integrar la llamada directa al motor C."
                },
                "metadatos": {
                    "Ruta seleccionada": ruta.split("/")[-1],
                    "Analisis Binario": "Por definir",
                    "Reglas BD": "Por definir"
                },
                "riesgo": {
                    "confidencialidad": "Normal",
                    "integridad": "Por verificar",
                    "disponibilidad": "Normal",
                    "score": 10
                },
                "recomendaciones": "1. Verificar que el archivo coincida con la firma declarada.\n2. No ejecutar el archivo si la extension fue modificada."
            })

    def ejecutar_proceso_secuencial_interfaz(self, datos):
        """Muestra los resultados paso a paso cada 1 segundo en cada contenedor."""
        # Colapsamos todo al inicio
        self.sec_mitre.cerrar()
        self.sec_metadatos.cerrar()
        self.sec_cid.cerrar()
        self.sec_recomendaciones.cerrar()

        # Asignamos volcados crudos inmediatos en panel izquierdo
        self.txt_hex_view.setText(datos.get("hex_dump", ""))
        self.txt_bin_view.setText(datos.get("bin_stream", ""))
        self.txt_text_view.setText(datos.get("text_stream", ""))

        # Paso 1: A los 1000ms se abre MITRE
        QTimer.singleShot(1000, lambda: self._mostrar_paso_mitre(datos.get("mitre", {})))

        # Paso 2: A los 2000ms se abren Metadatos
        QTimer.singleShot(2000, lambda: self._mostrar_paso_metadatos(datos.get("metadatos", {})))

        # Paso 3: A los 3000ms se abre Riesgo y CID
        QTimer.singleShot(3000, lambda: self._mostrar_paso_cid(datos.get("riesgo", {})))

        # Paso 4: A los 4000ms se abren Recomendaciones
        QTimer.singleShot(4000, lambda: self._mostrar_paso_recomendaciones(datos.get("recomendaciones", "")))

    def _mostrar_paso_mitre(self, m):
        self.actualizar_diagnostico_mitre(
            es_anomalia=m.get("es_anomalia", False),
            estado=m.get("estado", "PENDIENTE"),
            tactica=m.get("tactica", "N/A"),
            tecnica=m.get("tecnica", "N/A"),
            descripcion=m.get("descripcion", "")
        )
        self.sec_mitre.abrir()

    def _mostrar_paso_metadatos(self, metas):
        self.tbl_metadatos.setRowCount(len(metas))
        for fila, (k, v) in enumerate(metas.items()):
            self.tbl_metadatos.setItem(fila, 0, QTableWidgetItem(str(k)))
            self.tbl_metadatos.setItem(fila, 1, QTableWidgetItem(str(v)))
        self.sec_metadatos.abrir()

    def _mostrar_paso_cid(self, r):
        self.lbl_confidencialidad.setText(f"Confidencialidad: {r.get('confidencialidad', 'Normal')}")
        self.lbl_integridad.setText(f"Integridad: {r.get('integridad', 'Normal')}")
        self.lbl_disponibilidad.setText(f"Disponibilidad: {r.get('disponibilidad', 'Normal')}")
        score = r.get("score", 0)
        self.lbl_riesgo_score.setText(f"Nivel de Riesgo Global: {score}%")
        self.bar_riesgo.setValue(score)
        self.sec_cid.abrir()

    def _mostrar_paso_recomendaciones(self, texto):
        self.txt_recomendaciones.setText(texto)
        self.sec_recomendaciones.abrir()

    def actualizar_diagnostico_mitre(self, es_anomalia: bool, estado: str, tactica: str, tecnica: str, descripcion: str):
        t = CONFIG_TEMA[self.tema_actual]
        self.lbl_mitre_estado.setText(f"ESTADO: {estado}")
        self.lbl_mitre_tactica.setText(f"Tactica: {tactica}")
        self.lbl_mitre_tecnica.setText(f"Tecnica: {tecnica}")
        self.lbl_mitre_desc.setText(descripcion)

        if estado.startswith("POR DEFINIR"):
            color = t["alerta_neutra"]
            fondo = t["fondo_neutro_alerta"]
        else:
            color = t["alerta_rojo"] if es_anomalia else t["alerta_verde"]
            fondo = t["fondo_rojo_alerta"] if es_anomalia else t["fondo_verde_alerta"]

        self.card_mitre.setStyleSheet(f"""
            QFrame#card_mitre {{
                background-color: {fondo};
                border: 1px solid {color};
                border-radius: {t['borde_radio']};
            }}
            QLabel#lbl_mitre_estado {{
                color: {color};
                font-size: 13px;
                font-weight: 800;
            }}
            QLabel#lbl_mitre_sub {{
                color: {color};
                font-size: 12px;
                font-weight: 600;
            }}
            QLabel#lbl_mitre_desc {{
                color: {t['texto_principal']};
                font-size: 12px;
            }}
        """)

    def alternar_tema(self):
        if self.tema_actual == "oscuro":
            self.tema_actual = "claro"
            self.btn_tema.setText("Modo Oscuro")
        else:
            self.tema_actual = "oscuro"
            self.btn_tema.setText("Modo Claro")
        self.aplicar_tema(self.tema_actual)

    def aplicar_tema(self, modo):
        t = CONFIG_TEMA[modo]
        qss = f"""
            QMainWindow, QDialog {{
                background-color: {t['fondo_ventana']};
            }}
            QWidget {{
                color: {t['texto_principal']};
                font-family: '{t['fuente_interfaz']}', sans-serif;
                font-size: {t['tamano_base']};
            }}
            QLabel#lbl_titulo_app {{
                font-size: {t['tamano_titulos']};
                font-weight: 700;
                color: {t['color_acento']};
            }}
            QLabel#lbl_subtitulo_app {{
                font-size: {t['tamano_subtitulos']};
                color: {t['texto_secundario']};
                margin-left: 6px;
            }}
            QLabel#lbl_seccion_titulo {{
                font-size: {t['tamano_etiquetas']};
                font-weight: 700;
                color: {t['texto_secundario']};
                letter-spacing: 1px;
            }}
            QFrame#panel_contenedor {{
                background-color: {t['fondo_panel']};
                border: 1px solid {t['borde_panel']};
                border-radius: {t['borde_radio']};
            }}
            QFrame#seccion_desplegable {{
                background-color: {t['fondo_panel']};
                border: 1px solid {t['borde_panel']};
                border-radius: {t['borde_radio']};
                padding: 4px;
            }}
            QPushButton#btn_acordeon {{
                background-color: {t['fondo_boton']};
                color: {t['texto_principal']};
                border: 1px solid {t['borde_panel']};
                border-radius: {t['borde_radio']};
                padding: 6px 10px;
                text-align: left;
                font-weight: 700;
                font-size: 12px;
            }}
            QPushButton#btn_acordeon:hover {{
                background-color: {t['fondo_boton_hover']};
            }}
            QFrame#card_cid {{
                background-color: {t['fondo_input']};
                border: 1px solid {t['borde_panel']};
                border-radius: {t['borde_radio']};
            }}
            QLineEdit {{
                background-color: {t['fondo_input']};
                border: 1px solid {t['borde_panel']};
                border-radius: {t['borde_radio']};
                padding: 6px 10px;
                color: {t['texto_principal']};
            }}
            QPushButton#btn_accion_secundaria {{
                background-color: {t['fondo_boton']};
                color: {t['texto_principal']};
                border: 1px solid {t['borde_panel']};
                border-radius: {t['borde_radio']};
                padding: 6px 14px;
                font-weight: 600;
            }}
            QPushButton#btn_accion_secundaria:hover {{
                background-color: {t['fondo_boton_hover']};
            }}
            QPushButton#btn_accion_primaria {{
                background-color: {t['color_acento']};
                color: #ffffff;
                border: none;
                border-radius: {t['borde_radio']};
                padding: 8px 16px;
                font-weight: 700;
            }}
            QPushButton#btn_accion_primaria:hover {{
                background-color: {t['color_acento_hover']};
            }}
            QTabWidget::pane {{
                border: 1px solid {t['borde_panel']};
                background-color: {t['fondo_input']};
                border-radius: {t['borde_radio']};
            }}
            QTabBar::tab {{
                background-color: {t['fondo_panel']};
                color: {t['texto_secundario']};
                padding: 6px 12px;
                border: 1px solid {t['borde_panel']};
                border-bottom: none;
                border-top-left-radius: {t['borde_radio']};
                border-top-right-radius: {t['borde_radio']};
                margin-right: 4px;
            }}
            QTabBar::tab:selected {{
                color: {t['color_acento']};
                font-weight: 700;
                background-color: {t['fondo_input']};
            }}
            QTextEdit {{
                background-color: {t['fondo_input']};
                border: 1px solid {t['borde_panel']};
                border-radius: {t['borde_radio']};
                color: {t['texto_principal']};
                font-family: '{t['fuente_codigo']}', monospace;
                padding: 8px;
            }}
            QProgressBar {{
                background-color: {t['fondo_panel']};
                border: 1px solid {t['borde_panel']};
                border-radius: {t['borde_radio']};
                height: 14px;
                text-align: center;
                font-size: 10px;
            }}
            QProgressBar::chunk {{
                background-color: {t['color_acento']};
                border-radius: {t['borde_radio']};
            }}
            QTableWidget {{
                background-color: {t['fondo_input']};
                gridline-color: {t['borde_panel']};
                border: 1px solid {t['borde_panel']};
                border-radius: {t['borde_radio']};
                color: {t['texto_principal']};
            }}
            QHeaderView::section {{
                background-color: {t['fondo_panel']};
                color: {t['texto_secundario']};
                padding: 6px 10px;
                font-weight: 700;
                border: none;
                border-bottom: 1px solid {t['borde_panel']};
            }}
        """
        self.setStyleSheet(qss)