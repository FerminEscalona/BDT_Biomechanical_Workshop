from dotenv import load_dotenv
import os
import shutil
import psycopg2

load_dotenv()

def get_file_diagnostics(filename):
    """
    Obtiene la ruta absoluta y verifica permisos de lectura/escritura. [cite: 12, 13]
    """
    # 1. Obtener la ruta absoluta [cite: 12]
    full_path = os.path.abspath(filename)
    
    # 2. Verificar permisos usando os.access [cite: 13, 14]
    # os.R_OK comprueba lectura, os.W_OK comprueba escritura
    read_permission = os.access(full_path, os.R_OK)
    write_permission = os.access(full_path, os.W_OK)
    
    return full_path, read_permission, write_permission

def get_disk_diagnostics(path):
    """
    Obtiene el espacio libre y total en el disco.
    """
    usage = shutil.disk_usage(path)
    total = format_bytes(usage.total)
    used = format_bytes(usage.used)
    free = format_bytes(usage.free)
    return total, used, free
def format_bytes(size_bytes):
    """
    Formatea bytes a un formato legible (KB, MB, GB).
    """
    if size_bytes == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = 0
    while size_bytes >= 1024 and i < len(size_name) - 1:
        size_bytes /= 1024
        i += 1
    return f"{size_bytes:.2f} {size_name[i]}"

def get_missing_percentages(df):
    """Calcula el porcentaje de valores nulos por columna."""
    # Sumamos los nulos y dividimos por el total de filas [cite: 27]
    return (df.isnull().sum() / len(df)) * 100

def get_db_connection():
    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS")
        )
        return connection
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

def load_data_to_postgres(df, table_name):
    """Exporta a CSV temporal y carga a Postgres usando copy_expert."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 1. Crear tabla (ajusta los tipos según el dataset) 
    # Usamos VARCHAR para texto y FLOAT para números
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
    subject_id VARCHAR(50),
    date VARCHAR(50),
    otp VARCHAR(50),
    trial BIGINT,
    "group" VARCHAR(50),  -- 'group' es palabra reservada, por eso va entre comillas
    marker VARCHAR(100),
    side VARCHAR(10),
    joint VARCHAR(50),
    variable VARCHAR(100),
    units VARCHAR(50),
    protocol VARCHAR(100),
    value_x FLOAT8,
    value_y FLOAT8,
    value_z FLOAT8,
    sd_x FLOAT8,
    sd_y FLOAT8,
    sd_z FLOAT8,
    md_x FLOAT8,
    md_y FLOAT8,
    md_z FLOAT8,
    score_loop FLOAT8,
    score_apply FLOAT8,
    composite_score FLOAT8
);
    """
    cur.execute(create_table_query)
    cur.execute(f"TRUNCATE TABLE {table_name};") # Limpiar tabla antes de cargar
    
    # 2. Carga eficiente con copy_expert 
    temp_csv = "temp_data.csv"
    df.to_csv(temp_csv, index=False, header=False) # Guardar sin cabecera para el COPY
    
    with open(temp_csv, 'r') as f:
        # El comando COPY es mucho más rápido que INSERT para Big Data [cite: 57, 58]
        sql = f"COPY {table_name} FROM STDIN WITH (FORMAT CSV)"
        cur.copy_expert(sql, f)
    
    conn.commit()
    cur.close()
    conn.close()
    os.remove(temp_csv) # Borrar archivo temporal
    print(f"Datos cargados exitosamente en la tabla {table_name}.")