# Herramientas de Big Data
## Taller: Análisis Biomecánico con Python y PostgreSQL

**Estudiantes:** Julian Eduardo Romero Martinez (325312), Samuel Esteban Ramírez Rodríguez (296748), Fermin Alejandro Escalona Guillen (0000300181)  
**Facultad:** Facultad de Ingeniería  
**Universidad de la Sabana**  
**Profesor:** Hugo Franco, Ph.D.  
**Fecha:** 06 de abril de 2026

---

## 1. Diagnóstico Avanzado de Sistema de Archivos

### 1.1. Descripción del Problema

El primer punto del taller consiste en realizar un diagnóstico del entorno de ejecución antes de procesar los datos biomecánicos. Esto incluye verificar que el archivo CSV de entrada existe y es accesible, conocer su ruta absoluta en el sistema de archivos, comprobar los permisos de lectura y escritura, y determinar el espacio disponible en disco. Este diagnóstico es fundamental en flujos de Big Data para evitar errores silenciosos o interrupciones inesperadas durante el procesamiento de grandes volúmenes de información.

### 1.2. Método de Solución

**Datos empleados:** Archivo CSV `result_retrieve_left-and-right_x_50_2016_workshop.csv` con registros de cinemática articular.

La solución utiliza el módulo estándar `os` para la verificación de existencia y permisos del archivo, y `shutil` para obtener las estadísticas de disco. La función `format_bytes` convierte dinámicamente bytes a la unidad más legible (KB, MB, GB, TB).

Algoritmo 1. Diagnóstico de sistema de archivos

```
función get_file_diagnostics(filename):
    full_path ← os.path.abspath(filename)
    read_ok   ← os.access(full_path, R_OK)
    write_ok  ← os.access(full_path, W_OK)
    retornar (full_path, read_ok, write_ok)

función get_disk_diagnostics(path):
    usage ← shutil.disk_usage(path)
    retornar (format_bytes(usage.total),
              format_bytes(usage.used),
              format_bytes(usage.free))

procedimiento principal:
    si NOT os.path.exists(csv_file):
        lanzar FileNotFoundError
    file_info ← get_file_diagnostics(csv_file)
    disk_info ← get_disk_diagnostics(csv_file)
    imprimir file_info, disk_info
```

### 1.3. Resultados

Al ejecutar `python main.py` con el archivo CSV presente en el directorio de trabajo, la salida de consola reporta la ruta absoluta del archivo, el estado de los permisos (lectura: SÍ / escritura: SÍ) y el espacio total, usado y libre del disco en formato legible. Si el archivo no existe, el programa lanza un `FileNotFoundError` con un mensaje descriptivo antes de continuar.

### 1.4. Discusión

La verificación previa de existencia del archivo evita que `pd.read_csv()` produzca un error genérico difícil de diagnosticar. El uso de `os.access()` con las banderas `R_OK` y `W_OK` permite distinguir entre archivos inexistentes y archivos con permisos insuficientes, proporcionando información más precisa al operador del pipeline.

---

## 2. Exploración y Limpieza de Datos

### 2.1. Descripción del Problema

El segundo punto consiste en cargar el dataset biomecánico y realizar una exploración inicial para comprender su estructura, tipos de datos y calidad. Posteriormente, se aplica un proceso de limpieza eliminando las filas que presenten valores nulos en las columnas críticas de medición: `value_x`, `value_y` y `value_z`, que representan los ángulos articulares en los tres ejes espaciales.

### 2.2. Método de Solución

**Datos empleados:** DataFrame cargado desde el CSV con columnas categóricas (`subject_id`, `joint`, `side`, `protocol`, etc.) y numéricas (`value_x`, `value_y`, `value_z`, `sd_x`, `sd_y`, `sd_z`, `md_x`, `md_y`, `md_z`).

Algoritmo 2. Exploración y limpieza de datos

```
función get_missing_percentages(df):
    retornar (df.isnull().sum() / len(df)) * 100

procedimiento principal:
    df ← pd.read_csv(csv_file)
    imprimir df.shape, df.dtypes
    imprimir get_missing_percentages(df)

    critical_columns ← ['value_x', 'value_y', 'value_z']
    df_cleaned ← df.dropna(subset=critical_columns).copy()

    imprimir len(df), len(df_cleaned)
    imprimir get_missing_percentages(df_cleaned)
```

### 2.3. Resultados

La exploración muestra las dimensiones originales del dataset, los tipos de datos de cada columna y el porcentaje de valores nulos por columna. Tras aplicar `dropna()` sobre las columnas críticas, se reportan las filas eliminadas y se confirma que el dataset limpio no contiene nulos en las columnas de medición.

### 2.4. Discusión

El uso de `.copy()` al crear `df_cleaned` es una práctica importante en Pandas para evitar el `SettingWithCopyWarning` y garantizar que las operaciones posteriores no afecten inadvertidamente el DataFrame original. Limitar la limpieza únicamente a las columnas críticas (en lugar de eliminar filas con cualquier nulo) preserva la mayor cantidad posible de registros válidos para el análisis.

---

## 3. Manipulación de Datos Orientada al Rendimiento

### 3.1. Descripción del Problema

El tercer punto demuestra el impacto de la elección del método de iteración sobre el rendimiento en análisis de Big Data. Se calcula un puntaje compuesto biomecánico para cada fila del dataset usando tres enfoques diferentes: iteración fila por fila con `iterrows()`, aplicación funcional con `df.apply()`, y vectorización directa sobre Series de Pandas.

La fórmula del puntaje compuesto es:

`composite_score = (value_x × 0.5) + (value_y × 0.3) + (value_z × 1.0)`

### 3.2. Método de Solución

**Datos empleados:** `df_cleaned` con columnas numéricas `value_x`, `value_y`, `value_z`.

Algoritmo 3. Comparación de métodos de manipulación

```
constantes: WEIGHT_X ← 0.5, WEIGHT_Y ← 0.3, WEIGHT_Z ← 1.0

Método 1: iterrows (anti-patrón)
inicio ← time.time()
para cada (_, fila) en df_cleaned.iterrows():
    score ← (fila[value_x]*WEIGHT_X) + (fila[value_y]*WEIGHT_Y) + (fila[value_z]*WEIGHT_Z)
    agregar score a lista
df_cleaned['score_loop'] ← lista
tiempo_iterrows ← time.time() - inicio

Método 2: df.apply
inicio ← time.time()
df_cleaned['score_apply'] ← df_cleaned.apply(lambda r:
    (r[value_x]*WEIGHT_X) + (r[value_y]*WEIGHT_Y) + (r[value_z]*WEIGHT_Z), axis=1)
tiempo_apply ← time.time() - inicio

Método 3: Vectorización
inicio ← time.time()
df_cleaned['composite_score'] ← (df_cleaned[value_x]*WEIGHT_X
    + df_cleaned[value_y]*WEIGHT_Y
    + df_cleaned[value_z]*WEIGHT_Z)
tiempo_vector ← time.time() - inicio

imprimir tiempo_iterrows, tiempo_apply, tiempo_vector
```

### 3.3. Resultados

La ejecución produce tiempos comparativos para los tres métodos. Típicamente se observa que `iterrows()` es el más lento, `apply()` es intermedio, y la vectorización es significativamente más rápida.

### 3.4. Discusión

La diferencia de rendimiento entre métodos se vuelve crítica conforme crece el volumen de datos. La vectorización no solo es más rápida sino también más legible. Definir los pesos como constantes nombradas elimina los "números mágicos" del código.

---

## 4. Integración con Base de Datos

### 4.1. Descripción del Problema

El cuarto punto implementa la persistencia del dataset procesado en PostgreSQL y la recuperación selectiva de datos para visualización. Se requiere crear la tabla si no existe, truncarla antes de cada carga para evitar duplicados, y utilizar el comando `COPY` de PostgreSQL como mecanismo de carga masiva eficiente.
