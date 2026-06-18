Guía de instalación desde cero
1. Instalar Python con uv

# Instala uv (gestor de Python)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Cierra y abre la terminal, luego instala Python 3.13
uv python install 3.13
2. Clonar o copiar el proyecto
Copia la carpeta conversor_universitario/ a tu nueva máquina. Debe quedar así:


docs a markdown/
├── conversor_universitario/
│   ├── convert_to_md.py
│   ├── requirements.txt
│   ├── core/
│   └── utils/
├── Pymes.pdf
└── Sector agroindustrial (1).ppsx
3. Crear entorno virtual e instalar dependencias

# Entra a la carpeta del conversor
cd "C:\Users\NICK\Documents\nick-Personal\docs a markdown\conversor_universitario"

# Crea el entorno virtual (solo la primera vez)
uv venv .venv

# Activa el entorno
.venv\Scripts\activate

# Instala todas las dependencias
uv pip install -r requirements.txt
Verás (.venv) al inicio de tu terminal cuando el entorno esté activo.

4. Instalar Tesseract OCR (para leer texto en imágenes)

winget install UB-Mannheim.TesseractOCR
Después de instalar, cierra y abre la terminal para que lo detecte.

5. Ejecutar el conversor

# Asegúrate de estar en la carpeta con el venv activo
cd "C:\Users\NICK\Documents\nick-Personal\docs a markdown\conversor_universitario"
.venv\Scripts\activate

# Ejecutar
python convert_to_md.py
Uso diario (cada vez que quieras convertir)

# 1. Edita la lista de archivos en convert_to_md.py
#    ARCHIVOS_A_PROCESAR = [ r"..\nuevo_archivo.pdf", ... ]

# 2. Activa el entorno y ejecuta
cd "C:\Users\NICK\Documents\nick-Personal\docs a markdown\conversor_universitario"
.venv\Scripts\activate
python convert_to_md.py
Resumen de comandos clave
Qué hacer	Comando
Instalar uv	powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
Instalar Python	uv python install 3.13
Crear entorno	uv venv .venv
Activar entorno	.venv\Scripts\activate
Instalar librerías	uv pip install -r requirements.txt
Instalar Tesseract	winget install UB-Mannheim.TesseractOCR
Ejecutar conversor	python convert_to_md.py
