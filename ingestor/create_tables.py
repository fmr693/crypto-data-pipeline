import os
import psycopg2

conn = psycopg2.connect(
    host="postgres", # Nombre del servicio en docker-compose
    database=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD")
)
cursor = conn.cursor()

# Crear esquema RAW y la tabla
cursor.execute("CREATE SCHEMA IF NOT EXISTS raw;")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS raw.alumnos_sucios (
        id SERIAL PRIMARY KEY,
        nombre VARCHAR(100),
        email VARCHAR(100),
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")
conn.commit()
print("¡Esquema RAW y tabla creados exitosamente!")
cursor.close()
conn.close()
