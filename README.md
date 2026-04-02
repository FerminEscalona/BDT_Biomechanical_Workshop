# Biomechanical Data Workshop 1 - Big Data Tools 📊

## 🛠️ Requisitos Previos
* **Python 3.x**
* **Docker Desktop** (para la base de datos PostgreSQL)
* El archivo de datos `.csv` proporcionado por el curso (debe estar en la raíz del proyecto).

## 🚀 Configuración del Entorno

### 1. Ambiente Virtual e Instalación
Primero, crea y activa un entorno virtual para aislar las dependencias del proyecto:

```bash
# Crear el ambiente virtual
python -m venv env

# Activar en macOS/Linux
source env/bin/activate

# Activar en Windows
.\env\Scripts\activate
```

Una vez activado, instala las librerías necesarias:
```bash
pip install -r requirements.txt
```

### 2. Base de Datos (Docker)
El proyecto requiere una base de datos **PostgreSQL** corriendo en un contenedor. [cite_start]Asegúrate de que tu contenedor esté mapeado al puerto **5433** como se solicita en el taller.

### 3. Configuración de Variables de Entorno (`.env`)
Por seguridad, las credenciales no están incluidas en el código. Crea un archivo llamado `.env` en la raíz del proyecto con el siguiente contenido:

```env
DB_HOST=127.0.0.1
DB_PORT=5433
DB_NAME=bigdatatools1
DB_USER=psqluser
DB_PASS=tu_password_aqui
```

## 📂 Estructura del Proyecto
* [cite_start]**`main.py`**: Script principal que ejecuta las tareas en secuencia y genera los reportes de salida[cite: 6].
* [cite_start]**`utils.py`**: Librería de soporte que contiene las funciones de diagnóstico, limpieza y carga de datos[cite: 6].
* **`requirements.txt`**: Lista de dependencias del proyecto.
* **`.gitignore`**: Define los archivos y carpetas que deben ignorarse (env, .env, .csv, __pycache__).

## 🏃 Cómo Ejecutar el Proyecto
Para iniciar el proceso completo del taller, simplemente corre:

```bash
python main.py
```

## 📝 Tareas Realizadas
El script ejecutará automáticamente los siguientes módulos:
1.  [cite_start]**Diagnóstico de Archivos**: Obtención de rutas absolutas, verificación de permisos y métricas de espacio en disco (con conversión dinámica de unidades)[cite: 12, 14, 15, 17].
2.  [cite_start]**Limpieza de Datos**: Validación de tipos, cálculo de porcentajes de nulos y eliminación de registros incompletos en columnas críticas (`value_x`, `value_y`, `value_z`)[cite: 23, 26, 28].
3.  [cite_start]**Optimización de Rendimiento**: Comparación de tiempos de ejecución entre `iterrows`, `df.apply` y **Vectorización**[cite: 33, 34, 35].
4.  [cite_start]**Integración SQL**: Carga eficiente mediante `copy_expert` hacia PostgreSQL y recuperación selectiva mediante queries SQL[cite: 51, 56, 59].
5.  [cite_start]**Visualización**: Generación de subplots para los ángulos de Hip, Knee y Ankle, comparando los lados izquierdo (Rojo) y derecho (Azul)[cite: 67, 68, 70, 71].
