# 🚀 source2notebooklm

**`source2notebooklm`** es una herramienta en linea de comandos (CLI) ligera y sin dependencias externas diseñada para empaquetar repositorios de código fuente enteros en un único archivo de texto (o Markdown) formateado y optimizado para ser subido a **Google NotebookLM** o cualquier LLM (ChatGPT, Claude, Gemini).

---

## 💡 ¿Por qué usar source2notebooklm?

NotebookLM es ideal para analizar código, generar documentación, explicaciones o responder preguntas sobre la arquitectura de tu software. Sin embargo, subir decenas o cientos de archivos individuales a mano es tedioso.

**`source2notebooklm`** recorre de forma inteligente la estructura de tu proyecto y consolida todo tu código fuente en un solo archivo con delimitadores claros por archivo (`// --- ARCHIVO: ruta/al/archivo.py ---`), respetando las reglas de tu `.gitignore` y omitiendo artefactos de compilación y archivos binarios.

---

## ✨ Características Principal

- ⚡ **Zero Dependencies:** Funciona con Python 3.6+ estándar (`os`, `argparse`, `fnmatch`). No requiere `pip install`.
- 🙈 **Integración con `.gitignore`:** Respeta automáticamente los patrones de tu `.gitignore`.
- 🚫 **Filtros inteligentes por defecto:** Omite automáticamente carpetas como `node_modules`, `venv`, `.git`, `dist`, `target`, `__pycache__` y archivos binarios (`.png`, `.pdf`, `.jar`, etc.).
- 📊 **Estadísticas de salida:** Muestra al finalizar el número de archivos procesados, líneas de código, tamaño total en MB y estimación aproximada de tokens.
- 🎨 **Formatos flexibles (`txt` o `md`):** Soporta sintaxis de comentarios de archivo estándar o bloques de código Markdown.
- 🔀 **Modo de división Backend/Frontend (`--split-frontend-backend`):** Permite categorizar y empaquetar proyectos Fullstack en dos o tres archivos separados.

---

## 📦 Instalación

No requiere instalación de paquetes. Solo clona el repositorio o descarga el script `source2notebooklm.py`:

```bash
git clone https://github.com/jzsalinas/source2notebooklm.git
cd source2notebooklm
```

O hazlo ejecutable directamente en tu sistema:

```bash
chmod +x source2notebooklm.py
```

---

## 🚀 Ejemplos de Uso

### 1. Empaquetar el directorio actual
Empaqueta todo el proyecto actual en `notebooklm_codebase.txt`:
```bash
python3 source2notebooklm.py .
```

### 2. Especificar el nombre y ruta de salida
```bash
python3 source2notebooklm.py /ruta/a/mi-proyecto -o mi_codigo.txt
```

### 3. Generar en formato Markdown (`.md`)
Útil si prefieres sintaxis Markdown con bloques de código destacados:
```bash
python3 source2notebooklm.py . -o mi_codigo.md --format md
```

### 4. Filtrar solo por ciertas extensiones
Incluir únicamente archivos de Python y TypeScript:
```bash
python3 source2notebooklm.py . --include-ext .py,.ts,.tsx
```

### 5. Dividir proyecto en Backend y Frontend
Separa automáticamente el código en `notebooklm_codebase_backend.txt` y `notebooklm_codebase_frontend.txt`:
```bash
python3 source2notebooklm.py . --split-frontend-backend
```

### 6. Excluir directorios o archivos adicionales
```bash
python3 source2notebooklm.py . --ignore-dirs docs,tests --max-size-kb 500
```

---

## ⚙️ Opciones de Línea de Comandos (CLI)

```
uso: source2notebooklm.py [-h] [-o OUTPUT] [--format {txt,md}]
                          [--split-frontend-backend]
                          [--include-ext INCLUDE_EXT]
                          [--exclude-ext EXCLUDE_EXT]
                          [--ignore-dirs IGNORE_DIRS]
                          [--ignore-files IGNORE_FILES]
                          [--max-size-kb MAX_SIZE_KB] [--no-gitignore]
                          [path]

Positional Arguments:
  path                  Directorio raíz del proyecto a escanear (por defecto: directorio actual).

Options:
  -h, --help            Muestra este mensaje de ayuda.
  -o, --output OUTPUT   Nombre/ruta del archivo de salida (por defecto: notebooklm_codebase.txt).
  -format {txt,md}      Estilo de formato de salida: 'txt' (encabezado con comentario) o 'md' (bloques Markdown).
  --split-frontend-backend
                        Separa la salida en archivos independientes para backend y frontend.
  --include-ext         Lista separada por comas de extensiones a incluir (ej: .py,.ts,.java).
  --exclude-ext         Lista separada por comas de extensiones a excluir.
  --ignore-dirs         Nombres adicionales de carpetas a ignorar separados por comas.
  --ignore-files        Nombres adicionales de archivos a ignorar separados por comas.
  --max-size-kb         Tamaño máximo por archivo en KB (por defecto: 1000 KB).
  --no-gitignore        Desactiva la lectura automática del archivo .gitignore.
```

---

## 📝 Consejos para NotebookLM

- **Límites de fuente:** NotebookLM soporta hasta 500,000 palabras por fuente y un máximo de 50 fuentes por libreta.
- **Consultas recomendadas:** Al subir tu archivo consolidado a NotebookLM, puedes hacer preguntas como:
  - *"Resume la arquitectura general de este proyecto"*
  - *"¿Dónde se manejan las llamadas a las API o endpoints en el backend?"*
  - *"Explícame cómo funciona el flujo de autenticación paso a paso"*
  - *"Encuentra posibles refactorizaciones o vulnerabilidades de seguridad en el código"*

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo LICENSE para obtener más detalles.
