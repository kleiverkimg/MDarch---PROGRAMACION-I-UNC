```markdown
# MDArch - Lector y Analizador de Metadatos (Forense Digital)

**MDArch - SyS** es una plataforma de análisis forense digital diseñada para la inspección de metadatos, extracción de cabeceras binarias y detección de anomalías en archivos. El sistema integra un motor extractor de bajo nivel en **C**, un módulo de procesamiento de metadatos en **Python** y una interfaz gráfica construida en **PyQt6**, vinculando las inconsistencias detectadas con la matriz **MITRE ATT&CK**.

---

## 📁 Estructura del Proyecto

El repositorio está organizado bajo el patrón de arquitectura **Modelo-Vista-Controlador (MVC)**:

```text
MDArch---PROGRAMACION-I-UNC/
│
├── app/
│   ├── controller/
│   │   └── main_controller.py   # Lógica de interacción y puente C/Python
│   ├── model/
│   │   └── main_model.py        # Procesamiento de metadatos y mapeo MITRE ATT&CK
│   ├── views/
│   │   └── main_window.ui       # Interfaz gráfica (Qt Designer XML)
│   ├── __init__.py
│   └── main.py                  # Punto de entrada de la aplicación
│
├── .gitignore                   # Archivos excluidos del control de versiones
├── README.md                    # Documentación del proyecto
└── requirements.txt             # Dependencias de Python

```

---

## 📋 Requisitos Previos

Asegúrate de tener instaladas las siguientes herramientas en tu entorno de desarrollo:

1. **Python 3.10+**: [https://www.python.org/](https://www.python.org/)
2. **Compilador de C**:
* **Windows:** GCC (MinGW-w64 / MSYS2) o MSVC.
* **Linux / macOS:** `gcc` o `clang`.


3. **Git**: [https://git-scm.com/](https://git-scm.com/)

---

## 🚀 Guía de Instalación y Configuración

Sigue estos pasos para clonar e instalar el proyecto en tu máquina local:

### 1. Clonar el Repositorio

```bash
git clone [https://github.com/kleiverkimg/MDArch---PROGRAMACION-I-UNC.git](https://github.com/kleiverkimg/MDArch---PROGRAMACION-I-UNC.git)
cd MDArch---PROGRAMACION-I-UNC

```

Si vas a trabajar en la rama de desarrollo, ejecuta:

```bash
git checkout desarrollo

```

---

### 2. Crear y Activar Entorno Virtual

* **En Windows (PowerShell / CMD):**
```bash
python -m venv venv
.\venv\Scripts\activate

```


* **En Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate

```



---

### 3. Instalar Dependencias de Python

Con el entorno virtual activo, instala las librerías requeridas (PyQt6, etc.):

```bash
pip install -r requirements.txt

```

---

### 4. Compilar el Módulo Extractor en C

El motor de bajo nivel debe compilarse previamente para generar el ejecutable que procesará los *Magic Bytes* y volcados binarios/hexadecimales.

* **Ejemplo de compilación con GCC:**
```bash
gcc -O2 src/extractor.c -o app/bin/extractor.exe

```



---

## 💻 Ejecución de la Aplicación

Para lanzar la interfaz gráfica de **MDArch - SyS**, ejecuta desde el directorio raíz:

```bash
python app/main.py

```

---

## 🔑 Credenciales de Acceso (Entorno de Pruebas)

* **Usuario:** `admin`
* **Contraseña:** `admin123`

---

## 🛡️ Flujo de Operación Forense

1. **Autenticación:** Acceso al panel mediante módulo de credenciales.
2. **Carga de Muestra:** Selección del tipo de archivo objetivo (`.pdf`, `.exe`, `.png`).
3. **Procesamiento Binario:** Envío del archivo hacia el binario en **C** para extracción en bruto (Hex Dump y Flujo Binario).
4. **Análisis Forense en Python:**
* Comparación entre la extensión declarada y la firma real (`Magic Bytes`).
* Detección de máscaras o ejecutables camuflados (`Masquerading`).


5. **Mapeo MITRE ATT&CK:** Identificación automática de Tácticas y Técnicas (Ejemplo: `TA0005 - Defense Evasion` / `T1036.001`).

---

## 🤝 Flujo de Trabajo en Git (Para Colaboradores)

1. Sincroniza la rama `desarrollo` antes de realizar cambios:
```bash
git checkout desarrollo
git pull origin desarrollo

```


2. Crea una rama propia para cada función o módulo:
```bash
git checkout -b feature/nombre-de-tu-modulo

```


3. Guarda tus cambios y sube la rama:
```bash
git add .
git commit -m "feat: integración del módulo de análisis forense"
git push origin feature/nombre-de-tu-modulo

```


4. Abre un **Pull Request (PR)** dirigido hacia la rama `desarrollo` para revisión.