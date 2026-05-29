import os
import psycopg2
import requests
from psycopg2.extras import execute_values
from datetime import datetime

# 1. CARGA DE VARIABLES DE ENTORNO
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_NAME = os.getenv("POSTGRES_DB", "postgres")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

# 2. EXTRACCIÓN DE DATOS (EXTRACT)
URL = "https://api.coingecko.com/api/v3/coins/markets"
PARAMS = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 50,
    "page": 1,
    "sparkline": "false"
}

print("📥 Conectando con CoinGecko API...")
response = requests.get(URL, params=PARAMS)

if response.status_code == 200:
    data = response.json()
    print(f"✅ API consultada con éxito. Procesando {len(data)} monedas.")
else:
    print(f"❌ Error al consultar la API. Código de estado: {response.status_code}")
    exit(1)

# 3. CARGA EN EL DATA WAREHOUSE (LOAD) - MODO ACUMULATIVO e HISTÓRICO
conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
cur = conn.cursor()

# Eliminamos el TRUNCATE para permitir que la tabla acumule registros históricos
cur.execute("""
    CREATE TABLE IF NOT EXISTS raw_crypto (
        id VARCHAR(50),
        symbol VARCHAR(20),
        name VARCHAR(100),
        current_price NUMERIC,
        market_cap NUMERIC,
        total_volume NUMERIC,
        price_change_percentage_24h NUMERIC,
        ath NUMERIC,
        ath_change_percentage NUMERIC,
        extracted_at TIMESTAMP
    );
""")

# Mapeamos el JSON de la API a tuplas legibles por Postgres
rows_to_insert = [
    (
        coin['id'],
        coin['symbol'].upper(),
        coin['name'],
        coin['current_price'],
        coin['market_cap'],
        coin['total_volume'],
        coin['price_change_percentage_24h'],
        coin['ath'],
        coin['ath_change_percentage'],
        datetime.now()
    )
    for coin in data
]

# Inserción masiva del nuevo bloque de datos (Añade 50 filas nuevas)
query = """
    INSERT INTO raw_crypto (id, symbol, name, current_price, market_cap, total_volume, price_change_percentage_24h, ath, ath_change_percentage, extracted_at)
    VALUES %s
"""
execute_values(cur, query, rows_to_insert)
print("🚀 ¡Nuevos datos inyectados en el histórico de la capa RAW!")

# 🧹 POLÍTICA DE RETENCIÓN DE 3 MESES (90 DÍAS)
# ¿POR QUÉ?: Para mantener el sistema ágil, borramos las filas que tengan más de 90 días.
# Esto corre automáticamente cada 5 minutos protegiendo el almacenamiento.
cur.execute("""
    DELETE FROM raw_crypto 
    WHERE extracted_at < NOW() - INTERVAL '90 days';
""")
print("🧹 Mantenimiento ejecutado: Registros con más de 90 días eliminados automáticamente.")

conn.commit()
cur.close()
conn.close()
print("🎯 Proceso finalizado correctamente.")
