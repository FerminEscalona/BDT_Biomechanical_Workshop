from utils import get_file_diagnostics, get_disk_diagnostics, get_missing_percentages, get_db_connection, load_data_to_postgres
import pandas as pd
import time
import matplotlib.pyplot as plt
# Reemplaza 'tu_archivo.csv' por el nombre real del archivo que te dio el profesor
csv_file = "result_retrieve_left-and-right_x_50_2016_workshop.csv" 

print("--- 1. DIAGNÓSTICO AVANZADO DE SISTEMA DE ARCHIVOS ---")

# Ejecutar diagnóstico de archivo
file_info = get_file_diagnostics(csv_file)
print(f"Ruta absoluta: {file_info[0]}")
print(f"Permiso de lectura: {'SÍ' if file_info[1] else 'NO'}")
print(f"Permiso de escritura: {'SÍ' if file_info[2] else 'NO'}")

# Ejecutar diagnóstico de disco
disk_info = get_disk_diagnostics(csv_file)
print(f"\nEspacio en disco:")
print(f"  Total: {disk_info[0]}")
print(f"  Usado: {disk_info[1]}")
print(f"  Libre: {disk_info[2]}")

#Seccion de Data exploration and Cleansing

df = pd.read_csv(csv_file)
print("\n--- 2. EXPLORACIÓN Y LIMPIEZA DE DATOS ---")
print(f"\nDimensiones del dataset: {df.shape}")
print("Tipos de datos por columna:")
print(df.dtypes) 
print("\nPorcentaje de valores nulos por columna:")
print(get_missing_percentages(df))

#Seccion de Data transformation

critical_columns = ['value_x', 'value_y', 'value_z']

# Creamos el nuevo DataFrame limpio [cite: 29, 30]
df_cleaned = df.dropna(subset=critical_columns).copy()

print(f"\nLimpieza completada:")
print(f"Filas originales: {len(df)}")
print(f"Filas tras limpieza: {len(df_cleaned)}")
print("\nPorcentaje de valores nulos en el dataset limpio:")
print(get_missing_percentages(df_cleaned))

print("\n--- 3. PERFORMANCE-ORIENTED DATA MANIPULATION ---")

# --- MÉTODO 1: Row-by-Row (The Anti-Pattern) --- 
start_loop = time.time()
scores_loop = []
for index, row in df_cleaned.iterrows():
    # Fórmula: (value_x * 0.5) + (value_y * 0.3) + value_z 
    score = (row['value_x'] * 0.5) + (row['value_y'] * 0.3) + row['value_z']
    scores_loop.append(score)
df_cleaned['score_loop'] = scores_loop
end_loop = time.time()
time_iterrows = end_loop - start_loop

# --- MÉTODO 2: Functional Application (df.apply) --- 
start_apply = time.time()
df_cleaned['score_apply'] = df_cleaned.apply(
    lambda r: (r['value_x'] * 0.5) + (r['value_y'] * 0.3) + r['value_z'], 
    axis=1
)
end_apply = time.time()
time_apply = end_apply - start_apply

# --- MÉTODO 3: Vectorization (The Standard) --- 
start_vector = time.time()
# Operación directa sobre las series de Pandas [cite: 45]
df_cleaned['composite_score'] = (df_cleaned['value_x'] * 0.5) + (df_cleaned['value_y'] * 0.3) + df_cleaned['value_z']
end_vector = time.time()
time_vector = end_vector - start_vector

# --- ANÁLISIS DE RENDIMIENTO --- [cite: 36]
print(f"Tiempo iterrows:    {time_iterrows:.6f} s")
print(f"Tiempo df.apply:    {time_apply:.6f} s")
print(f"Tiempo Vectorización: {time_vector:.6f} s")

print(df_cleaned.dtypes)
print("\n--- 4. DATABASE INTEGRATION & RETRIEVAL ---")

# 1. Cargar datos limpios a la base de datos
load_data_to_postgres(df_cleaned, "kinematics_data")

# 2. Consulta SQL dirigida para visualización [cite: 59, 60, 61]
# Debes ajustar los valores de los filtros (subject_id, date, etc.) a los que tenga tu CSV
query = """
SELECT side, joint, value_x, value_y, value_z 
FROM kinematics_data 
WHERE joint IN ('Hip', 'Knee', 'Ankle')
  AND subject_id = '1T5IA77E6HNZMVG75WMBL35KVPF4D5NUHSGTVV5TUHEV47D1G8' 
  AND trial = 10
  AND date = '09-27-16' 
  AND protocol = 'M'
"""
# Nota: Asegúrate de que 'S01' y trial=1 existan en tu archivo .csv

conn = get_db_connection()
df_plot = pd.read_sql_query(query, conn) 
conn.close()

print("Datos recuperados de la DB para graficar:")
print(df_plot.head())

print("\n--- 5. DATA VISUALIZATION ---")

# 1. Definir la estructura de 3 subplots verticales [cite: 67, 74]
fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(10, 15))
joints = ['Hip', 'Knee', 'Ankle']

# 2. Iterar sobre cada articulación para crear los gráficos
for i, joint in enumerate(joints):
    # Filtrar datos por articulación y lado [cite: 75]
    subset_l = df_plot[(df_plot['joint'] == joint) & (df_plot['side'] == 'L')]
    subset_r = df_plot[(df_plot['joint'] == joint) & (df_plot['side'] == 'R')]
    
    # Graficar Lado Izquierdo (Rojo) [cite: 70, 77]
    # Usamos diferentes estilos de línea para distinguir X, Y, Z
    axes[i].plot(subset_l['value_x'].values, color='red', linestyle='-', label='L - Val X')
    axes[i].plot(subset_l['value_y'].values, color='red', linestyle='--', label='L - Val Y')
    axes[i].plot(subset_l['value_z'].values, color='red', linestyle=':', label='L - Val Z')
    
    # Graficar Lado Derecho (Azul) [cite: 71, 77]
    axes[i].plot(subset_r['value_x'].values, color='blue', linestyle='-', label='R - Val X')
    axes[i].plot(subset_r['value_y'].values, color='blue', linestyle='--', label='R - Val Y')
    axes[i].plot(subset_r['value_z'].values, color='blue', linestyle=':', label='R - Val Z')
    
    # Configuración de cada subplot
    axes[i].set_title(f'Joint Angles: {joint}')
    axes[i].set_ylabel('Angle (degrees)')
    axes[i].legend(loc='upper right', fontsize='small', ncol=2)
    axes[i].grid(True, alpha=0.3)

# Ajustar diseño y mostrar
plt.tight_layout()
plt.show()