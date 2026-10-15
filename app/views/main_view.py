import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
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
        "fondo_tarjeta_interna": "#0d1117",
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
        "alerta_ambar": "#d29922",
        "fondo_ambar_alerta": "#2d2208",
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
        "fondo_tarjeta_interna": "#f6f8fa",
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
        "alerta_ambar": "#9a6700",
        "fondo_ambar_alerta": "#fff8c5",
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
    """Contenedor de tipo acordeon con cabecera interactiva y subtitulo de estado."""
    def __init__(self, titulo_base, widget_contenido, parent=None):
        super().__init__(parent)
        self.setObjectName("seccion_desplegable")
        self.layout_contenedor = QVBoxLayout(self)
        self.layout_contenedor.setContentsMargins(0, 0, 0, 0)
        self.layout_contenedor.setSpacing(4)

        self.titulo_base = titulo_base
        self.subtitulo = ""
        self.esta_abierto = True

        self.btn_cabecera = QPushButton(self._generar_texto_boton(), self)
        self.btn_cabecera.setObjectName("btn_acordeon")
        self.btn_cabecera.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cabecera.clicked.connect(self.alternar_visibilidad)
        self.layout_contenedor.addWidget(self.btn_cabecera)

        self.contenido = widget_contenido
        self.layout_contenedor.addWidget(self.contenido)

    def _generar_texto_boton(self):
        indicador = "[-]" if self.esta_abierto else "[+]"
        if self.subtitulo:
            return f"{indicador} {self.titulo_base} [{self.subtitulo}]"
        return f"{indicador} {self.titulo_base}"

    def alternar_visibilidad(self):
        self.esta_abierto = not self.esta_abierto
        self.contenido.setVisible(self.esta_abierto)
        self.btn_cabecera.setText(self._generar_texto_boton())

    def abrir(self, subtitulo=None):
        self.esta_abierto = True
        if subtitulo is not None:
            self.subtitulo = subtitulo
        self.contenido.setVisible(True)
        self.btn_cabecera.setText(self._generar_texto_boton())

    def cerrar(self, subtitulo=None):
        self.esta_abierto = False
        if subtitulo is not None:
            self.subtitulo = subtitulo
        self.contenido.setVisible(False)
        self.btn_cabecera.setText(self._generar_texto_boton())


class TarjetaPilarCID(QFrame):
    """Tarjeta individual para mostrar el impacto en Confidencialidad, Integridad o Disponibilidad."""
    def __init__(self, nombre_pilar, parent=None):
        super().__init__(parent)
        self.setObjectName("tarjeta_pilar_cid")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        self.lbl_titulo = QLabel(nombre_pilar.upper(), self)
        self.lbl_titulo.setStyleSheet("font-size: 11px; font-weight: 700; letter-spacing: 0.5px;")

        self.lbl_nivel = QLabel("NORMAL", self)
        self.lbl_nivel.setStyleSheet("font-size: 14px; font-weight: 800;")

        self.lbl_motivo = QLabel("Sin alteraciones detectadas.", self)
        self.lbl_motivo.setWordWrap(True)
        self.lbl_motivo.setStyleSheet("font-size: 11px;")

        layout.addWidget(self.lbl_titulo)
        layout.addWidget(self.lbl_nivel)
        layout.addWidget(self.lbl_motivo)
        layout.addStretch()

    def actualizar(self, nivel, motivo, tema="oscuro"):
        t = CONFIG_TEMA[tema]
        nivel_normalizado = str(nivel).strip().capitalize()
        
        if nivel_normalizado in ["Critico", "Crítico", "Alto"]:
            color = t["alerta_rojo"]
            fondo = t["fondo_rojo_alerta"]
        elif nivel_normalizado == "Medio":
            color = t["alerta_ambar"]
            fondo = t["fondo_ambar_alerta"]
        else:
            color = t["alerta_verde"]
            fondo = t["fondo_verde_alerta"]

        self.setStyleSheet(f"""
            QFrame#tarjeta_pilar_cid {{
                background-color: {fondo};
                border: 1px solid {color};
                border-radius: {t['borde_radio']};
            }}
        """)
        self.lbl_titulo.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: 700;")
        self.lbl_nivel.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: 800;")
        self.lbl_nivel.setText(nivel_normalizado.upper())

        texto_motivo = motivo if motivo else "Sin impacto adverso detectado."
        self.lbl_motivo.setText(texto_motivo)
        self.lbl_motivo.setStyleSheet(f"color: {t['texto_principal']}; font-size: 11px;")


class LoginDialog(QDialog):
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

        if self.callback_autenticacion:
            exito, mensaje = self.callback_autenticacion(usuario, password)
            if exito:
                self.accept()
            else:
                self.lbl_mensaje.setText(mensaje)
        else:
            self.accept()


class ConfigDialog(QDialog):
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
        self.txt_nuevo_pass.setPlaceholderText("Contrasena robusta")
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
        self.resize(1260, 800)
        self.setMinimumSize(1040, 680)

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

        # Area de trabajo principal
        self.layout_cuerpo = QHBoxLayout()
        self.layout_cuerpo.setSpacing(16)

        # Panel Izquierdo
        self.panel_izquierdo = QFrame(self)
        self.panel_izquierdo.setObjectName("panel_contenedor")
        self.layout_panel_izq = QVBoxLayout(self.panel_izquierdo)
        self.layout_panel_izq.setContentsMargins(14, 14, 14, 14)
        self.layout_panel_izq.setSpacing(10)
        self.construir_panel_izquierdo()

        # Panel Derecho
        self.panel_derecho = QFrame(self)
        self.panel_derecho.setObjectName("panel_contenedor")
        self.layout_panel_der = QVBoxLayout(self.panel_derecho)
        self.layout_panel_der.setContentsMargins(10, 10, 10, 10)
        self.layout_panel_der.setSpacing(8)
        self.construir_panel_derecho()

        self.layout_cuerpo.addWidget(self.panel_izquierdo, 38)
        self.layout_cuerpo.addWidget(self.panel_derecho, 62)
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
        lbl_der_titulo = QLabel("EXPEDIENTE FORENSE Y MODULOS DE AMENAZA", self)
        lbl_der_titulo.setObjectName("lbl_seccion_titulo")
        self.layout_panel_der.addWidget(lbl_der_titulo)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setObjectName("scroll_forense")
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        contenedor_scroll = QWidget()
        self.layout_acordeones = QVBoxLayout(contenedor_scroll)
        self.layout_acordeones.setContentsMargins(4, 4, 10, 4)
        self.layout_acordeones.setSpacing(10)

        # 1. Cabecera
        self.card_cabecera = QFrame()
        self.card_cabecera.setObjectName("card_cabecera")
        layout_c = QVBoxLayout(self.card_cabecera)
        layout_c.setContentsMargins(12, 12, 12, 12)
        layout_c.setSpacing(6)

        self.lbl_cabecera_estado = QLabel("ESTADO: EN ESPERA", self)
        self.lbl_cabecera_estado.setObjectName("lbl_cabecera_estado")
        self.lbl_cabecera_detalle = QLabel("Firma magica pendiente de validacion.", self)
        self.lbl_cabecera_detalle.setWordWrap(True)
        layout_c.addWidget(self.lbl_cabecera_estado)
        layout_c.addWidget(self.lbl_cabecera_detalle)

        self.sec_cabecera = SeccionDesplegable("1. Validacion de Cabecera y Firmas", self.card_cabecera)
        self.layout_acordeones.addWidget(self.sec_cabecera)

        # 2. Metadatos
        self.tbl_metadatos = QTableWidget()
        self.tbl_metadatos.setColumnCount(2)
        self.tbl_metadatos.setHorizontalHeaderLabels(["Propiedad / Token", "Valor Extraido"])
        self.tbl_metadatos.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_metadatos.horizontalHeader().setStretchLastSection(True)
        self.tbl_metadatos.verticalHeader().setVisible(False)
        self.tbl_metadatos.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_metadatos.setMinimumHeight(150)

        self.sec_metadatos = SeccionDesplegable("2. Metadatos de Estructura Binaria", self.tbl_metadatos)
        self.layout_acordeones.addWidget(self.sec_metadatos)

        # 3. IOCs
        self.txt_iocs = QTextEdit()
        self.txt_iocs.setReadOnly(True)
        self.txt_iocs.setMinimumHeight(110)
        self.txt_iocs.setPlaceholderText("IPs, URLs, dominios y comandos detectados.")

        self.sec_iocs = SeccionDesplegable("3. Indicadores de Compromiso (IOCs)", self.txt_iocs)
        self.layout_acordeones.addWidget(self.sec_iocs)

        # 4. YARA
        self.txt_yara = QTextEdit()
        self.txt_yara.setReadOnly(True)
        self.txt_yara.setMinimumHeight(110)
        self.txt_yara.setPlaceholderText("Firmas y reglas de deteccion YARA coincidentes.")

        self.sec_yara = SeccionDesplegable("4. Modulo de Reglas YARA", self.txt_yara)
        self.layout_acordeones.addWidget(self.sec_yara)

        # 5. MITRE ATT&CK
        self.txt_mitre = QTextEdit()
        self.txt_mitre.setReadOnly(True)
        self.txt_mitre.setMinimumHeight(130)
        self.txt_mitre.setPlaceholderText("Tecnicas y tacticas de MITRE ATT&CK correlacionadas.")

        self.sec_mitre = SeccionDesplegable("5. Correlacion Heuristica MITRE ATT&CK", self.txt_mitre)
        self.layout_acordeones.addWidget(self.sec_mitre)

        # 6. Triada CID y Nivel de Riesgo (Dashboard estructurado)
        self.card_cid = QFrame()
        self.card_cid.setObjectName("card_cid")
        layout_cid_principal = QVBoxLayout(self.card_cid)
        layout_cid_principal.setContentsMargins(14, 14, 14, 14)
        layout_cid_principal.setSpacing(12)

        # Encabezado del dashboard: Estado general a la izquierda, metricas a la derecha
        layout_resumen_seguridad = QHBoxLayout()
        layout_resumen_seguridad.setSpacing(14)

        # Bloque izquierdo: Badge de riesgo general
        bloque_badge = QVBoxLayout()
        bloque_badge.setSpacing(4)
        lbl_titulo_estado = QLabel("ESTADO GENERAL:", self)
        lbl_titulo_estado.setStyleSheet("font-size: 11px; font-weight: 700; color: #8b949e;")
        
        self.lbl_badge_riesgo = QLabel("SIN AMENAZAS", self)
        self.lbl_badge_riesgo.setObjectName("lbl_badge_riesgo")
        self.lbl_badge_riesgo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_badge_riesgo.setFixedHeight(36)
        
        bloque_badge.addWidget(lbl_titulo_estado)
        bloque_badge.addWidget(self.lbl_badge_riesgo)
        layout_resumen_seguridad.addLayout(bloque_badge, 45)

        # Bloque derecho: Puntuacion y cantidad de indicadores
        bloque_metricas = QVBoxLayout()
        bloque_metricas.setSpacing(4)

        self.lbl_puntuacion_amenaza = QLabel("Puntuacion de Riesgo: 0.0 / 10", self)
        self.lbl_puntuacion_amenaza.setStyleSheet("font-weight: 700; font-size: 12px;")

        self.bar_riesgo_general = QProgressBar(self)
        self.bar_riesgo_general.setRange(0, 100)
        self.bar_riesgo_general.setValue(0)
        self.bar_riesgo_general.setFixedHeight(10)
        self.bar_riesgo_general.setTextVisible(False)

        self.lbl_conteo_indicadores = QLabel("Indicadores encontrados: 0", self)
        self.lbl_conteo_indicadores.setStyleSheet("font-size: 11px; color: #8b949e;")

        bloque_metricas.addWidget(self.lbl_puntuacion_amenaza)
        bloque_metricas.addWidget(self.bar_riesgo_general)
        bloque_metricas.addWidget(self.lbl_conteo_indicadores)
        layout_resumen_seguridad.addLayout(bloque_metricas, 55)

        layout_cid_principal.addLayout(layout_resumen_seguridad)

        # Subtitulo seccional
        lbl_sub_cid = QLabel("CLASIFICACION DE IMPACTO TRIADA CID", self)
        lbl_sub_cid.setStyleSheet("font-size: 11px; font-weight: 800; color: #8b949e; margin-top: 4px;")
        layout_cid_principal.addWidget(lbl_sub_cid)

        # Tres tarjetas modulares en paralelo para la triada
        layout_tres_pilares = QHBoxLayout()
        layout_tres_pilares.setSpacing(10)

        self.card_conf = TarjetaPilarCID("Confidencialidad", self)
        self.card_inte = TarjetaPilarCID("Integridad", self)
        self.card_disp = TarjetaPilarCID("Disponibilidad", self)

        layout_tres_pilares.addWidget(self.card_conf)
        layout_tres_pilares.addWidget(self.card_inte)
        layout_tres_pilares.addWidget(self.card_disp)
        layout_cid_principal.addLayout(layout_tres_pilares)

        self.sec_cid = SeccionDesplegable("6. Impacto en Triada CID y Riesgo", self.card_cid)
        self.layout_acordeones.addWidget(self.sec_cid)

        # 7. Recomendaciones
        self.txt_recomendaciones = QTextEdit()
        self.txt_recomendaciones.setReadOnly(True)
        self.txt_recomendaciones.setMinimumHeight(100)
        self.txt_recomendaciones.setPlaceholderText("Acciones correctivas recomendadas.")

        self.sec_recomendaciones = SeccionDesplegable("7. Plan y Medidas de Mitigacion", self.txt_recomendaciones)
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

        if self.callback_ejecutar_analisis:
            self.callback_ejecutar_analisis(ruta)

    def ejecutar_proceso_secuencial_interfaz(self, datos):
        self.sec_cabecera.cerrar()
        self.sec_metadatos.cerrar()
        self.sec_iocs.cerrar()
        self.sec_yara.cerrar()
        self.sec_mitre.cerrar()
        self.sec_cid.cerrar()
        self.sec_recomendaciones.cerrar()

        # Volcados protegidos
        self.txt_hex_view.setText(str(datos.get("hex_dump", ""))[:8000])
        self.txt_bin_view.setText(str(datos.get("bin_stream", ""))[:4000])
        self.txt_text_view.setText(str(datos.get("text_stream", ""))[:4000])

        # Renderizado secuencial
        QTimer.singleShot(300, lambda: self._mostrar_cabecera(datos.get("cabecera", {})))
        QTimer.singleShot(600, lambda: self._mostrar_metadatos(datos.get("metadatos", {})))
        QTimer.singleShot(900, lambda: self._mostrar_iocs(datos.get("ioc", {})))
        QTimer.singleShot(1200, lambda: self._mostrar_yara(datos.get("yara", {})))
        QTimer.singleShot(1500, lambda: self._mostrar_mitre(datos.get("mitre", [])))
        QTimer.singleShot(1800, lambda: self._mostrar_cid(datos.get("riesgo", {}), datos))
        QTimer.singleShot(2100, lambda: self._mostrar_recomendaciones(datos.get("recomendaciones", [])))

    def _mostrar_cabecera(self, c):
        t = CONFIG_TEMA[self.tema_actual]
        coincide = c.get("coincide", False)
        tipo_det = c.get("tipo_detectado", "No reconocido").upper()
        ext_esp = c.get("extension_esperada", "").upper()
        hex_rec = c.get("hex_recibido", "")
        mensaje = c.get("mensaje", "")

        color = t["alerta_verde"] if coincide else t["alerta_rojo"]
        fondo = t["fondo_verde_alerta"] if coincide else t["fondo_rojo_alerta"]
        estado_txt = "ESTADO: FIRMA CONSISTENTE" if coincide else "ESTADO: DISCREPANCIA DETECTADA"
        subtitulo = f"{tipo_det} valido" if coincide else "Firma discrepante o desconocida"

        self.lbl_cabecera_estado.setText(estado_txt)
        self.lbl_cabecera_estado.setStyleSheet(f"color: {color}; font-weight: bold;")
        self.lbl_cabecera_detalle.setText(f"Hex leido: {hex_rec} | Esperado: {ext_esp}\n{mensaje}")
        self.card_cabecera.setStyleSheet(
            f"QFrame#card_cabecera {{ background-color: {fondo}; border: 1px solid {color}; border-radius: {t['borde_radio']}; }}"
        )
        self.sec_cabecera.abrir(subtitulo)

    def _mostrar_metadatos(self, metas):
        cantidad = len(metas)
        self.tbl_metadatos.setRowCount(cantidad)
        for fila, (k, v) in enumerate(metas.items()):
            self.tbl_metadatos.setItem(fila, 0, QTableWidgetItem(str(k)))
            self.tbl_metadatos.setItem(fila, 1, QTableWidgetItem(str(v)))
        self.sec_metadatos.abrir(f"{cantidad} campos extraidos")

    def _mostrar_iocs(self, iocs):
        bloques = []
        total_iocs = 0

        urls = iocs.get("urls", [])
        if urls:
            total_iocs += len(urls)
            bloques.append("[URLs]")
            bloques.extend([f"  * {u}" for u in urls])

        ips = iocs.get("ips", [])
        if ips:
            total_iocs += len(ips)
            bloques.append("\n[Direcciones IP]")
            bloques.extend([f"  * {ip}" for ip in ips])

        dominios = iocs.get("dominios", [])
        if dominios:
            total_iocs += len(dominios)
            bloques.append("\n[Dominios]")
            bloques.extend([f"  * {d}" for d in dominios])

        comandos = iocs.get("comandos", [])
        if comandos:
            total_iocs += len(comandos)
            bloques.append("\n[Comandos y Scripts]")
            bloques.extend([f"  * {c}" for c in comandos])

        hashes = iocs.get("hashes", {})
        if hashes:
            bloques.append("\n[Hashes]")
            for alg, lista in hashes.items():
                total_iocs += len(lista)
                for h in lista:
                    bloques.append(f"  * {alg.upper()}: {h}")

        if bloques:
            self.txt_iocs.setText("\n".join(bloques))
            self.sec_iocs.abrir(f"{total_iocs} detectados")
        else:
            self.txt_iocs.setText("No se identificaron patrones de IOCs en la muestra.")
            self.sec_iocs.abrir("0 detectados")

    def _mostrar_yara(self, yara_res):
        total = yara_res.get("total_coincidencias", 0)
        resultados = yara_res.get("resultados", [])
        bloques = []

        for r in resultados:
            regla = r.get("regla_activada", "Desconocida")
            tags = ", ".join(r.get("tags", []))
            meta = r.get("metadatos", {})
            severidad = meta.get("severidad", "Normal")
            desc = meta.get("description", "Sin descripcion")

            bloques.append(f"Regla: {regla} | Severidad: {severidad}")
            if tags:
                bloques.append(f"Etiquetas: {tags}")
            bloques.append(f"Descripcion: {desc}")

            cadenas = r.get("cadenas_coincidentes", [])
            if cadenas:
                bloques.append("Coincidencias en memoria:")
                for c in cadenas:
                    offset = c.get("offset", 0)
                    ident = c.get("identificador", "")
                    cont = c.get("contenido", "")
                    bloques.append(f"  * Offset {offset} ({ident}): {cont}")
            bloques.append("-" * 40)

        if bloques:
            self.txt_yara.setText("\n".join(bloques))
            self.sec_yara.abrir(f"{total} regla activada" if total == 1 else f"{total} reglas activadas")
        else:
            self.txt_yara.setText("Sin coincidencias en el motor de reglas YARA.")
            self.sec_yara.abrir("0 reglas")

    def _mostrar_mitre(self, mitre_list):
        cantidad = len(mitre_list)
        bloques = []

        for m in mitre_list:
            tid = m.get("tecnica_id", "T0000")
            nombre = m.get("nombre", "Tecnica desconocida")
            origen = m.get("origen_deteccion", "Analisis")
            gatillo = m.get("gatillado_por", "")
            tacticas = ", ".join(m.get("tacticas", []))
            desc = m.get("descripcion", "")

            bloques.append(f"{tid}: {nombre}")
            bloques.append(f"Tactica: {tacticas} | Origen: {origen} (Token: {gatillo})")
            bloques.append(f"Detalle: {desc}")
            bloques.append("-" * 50)

        if bloques:
            self.txt_mitre.setText("\n".join(bloques))
            self.sec_mitre.abrir(f"{cantidad} tecnicas mapeadas")
        else:
            self.txt_mitre.setText("No se correlacionaron tecnicas de la matriz MITRE ATT&CK.")
            self.sec_mitre.abrir("0 tecnicas")

    def _mostrar_cid(self, r, datos_completos):
        t = CONFIG_TEMA[self.tema_actual]
        
        # Extraccion limpia de valores evitando imprimir diccionarios crudos
        c_dict = r.get("confidencialidad", {})
        i_dict = r.get("integridad", {})
        d_dict = r.get("disponibilidad", {})

        c_nivel = c_dict.get("nivel", "Bajo") if isinstance(c_dict, dict) else str(c_dict)
        i_nivel = i_dict.get("nivel", "Bajo") if isinstance(i_dict, dict) else str(i_dict)
        d_nivel = d_dict.get("nivel", "Bajo") if isinstance(d_dict, dict) else str(d_dict)

        c_motivo = c_dict.get("motivos", [""])[0] if isinstance(c_dict, dict) and c_dict.get("motivos") else ""
        i_motivo = i_dict.get("motivos", [""])[0] if isinstance(i_dict, dict) and i_dict.get("motivos") else ""
        d_motivo = d_dict.get("motivos", [""])[0] if isinstance(d_dict, dict) and d_dict.get("motivos") else ""

        # Actualizacion de las 3 tarjetas modulares
        self.card_conf.actualizar(c_nivel, c_motivo, self.tema_actual)
        self.card_inte.actualizar(i_nivel, i_motivo, self.tema_actual)
        self.card_disp.actualizar(d_nivel, d_motivo, self.tema_actual)

        # Calculo ponderado de puntuacion de 0 a 10
        escala = {"Critico": 3.4, "Crítico": 3.4, "Alto": 3.0, "Medio": 1.8, "Bajo": 0.5, "Normal": 0.0}
        score_10 = escala.get(c_nivel.capitalize(), 0.5) + escala.get(i_nivel.capitalize(), 0.5) + escala.get(d_nivel.capitalize(), 0.5)
        score_10 = min(round(score_10, 1), 10.0)
        porcentaje_barra = int(score_10 * 10)

        # Conteo total de indicadores encontrados en la muestra
        total_indicadores = 0
        iocs = datos_completos.get("ioc", {})
        if isinstance(iocs, dict):
            total_indicadores += len(iocs.get("urls", [])) + len(iocs.get("ips", [])) + len(iocs.get("dominios", [])) + len(iocs.get("comandos", []))
            for hlist in iocs.get("hashes", {}).values():
                total_indicadores += len(hlist)
        yara = datos_completos.get("yara", {})
        if isinstance(yara, dict):
            total_indicadores += yara.get("total_coincidencias", 0)

        self.lbl_puntuacion_amenaza.setText(f"Puntuacion de Riesgo: {score_10} / 10")
        self.bar_riesgo_general.setValue(porcentaje_barra)
        self.lbl_conteo_indicadores.setText(f"Indicadores encontrados: {total_indicadores}")

        # Determinacion del badge de estado general
        if score_10 >= 6.0:
            color_badge = t["alerta_rojo"]
            fondo_badge = t["fondo_rojo_alerta"]
            texto_badge = "RIESGO ALTO (Contenido hostil detectado)"
        elif score_10 >= 3.5:
            color_badge = t["alerta_ambar"]
            fondo_badge = t["fondo_ambar_alerta"]
            texto_badge = "RIESGO MEDIO (Anomalias bajo observacion)"
        else:
            color_badge = t["alerta_verde"]
            fondo_badge = t["fondo_verde_alerta"]
            texto_badge = "ESTADO LIMPIO (Firma integra)"

        self.lbl_badge_riesgo.setText(texto_badge)
        self.lbl_badge_riesgo.setStyleSheet(f"""
            QLabel#lbl_badge_riesgo {{
                background-color: {fondo_badge};
                color: {color_badge};
                border: 1px solid {color_badge};
                border-radius: {t['borde_radio']};
                font-weight: 800;
                font-size: 11px;
                padding: 4px 8px;
            }}
        """)

        self.sec_cid.abrir(f"Score {score_10}/10")

    def _mostrar_recomendaciones(self, recom):
        cantidad = len(recom)
        if recom:
            lineas = [f"{idx + 1}. {texto}" for idx, texto in enumerate(recom)]
            self.txt_recomendaciones.setText("\n\n".join(lineas))
            self.sec_recomendaciones.abrir(f"{cantidad} acciones")
        else:
            self.txt_recomendaciones.setText("No se requieren acciones de mitigacion inmediatas.")
            self.sec_recomendaciones.abrir("0 acciones")

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
            QFrame#card_cid, QFrame#card_cabecera {{
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
                height: 10px;
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