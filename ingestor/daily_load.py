import os
import psycopg2
import requests
from psycopg2.extras import execute_values
from datetime import datetime

# 1. CARGA DE VARIABLES DE ENTORNO (Seguridad en producción)
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_NAME = os.getenv("POSTGRES_DB", "postgres")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

# 2. EXTRACCIÓN DE DATOS DESDE LA API DE COINGECKO (Extract)
URL = "https://api.coingecko.com/api/v3/coins/markets"
PARAMS = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 50,
    "page": 1,
    "sparkline": "false"
}

print("📥 Conectando con CoinGecko API...")
try:
    response = requests.get(URL, params=PARAMS)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API consultada con éxito. Procesando {len(data)} monedas.")
    else:
        print(f"❌ Error al consultar la API. Código de estado: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"❌ Error de conexión con la API: {e}")
    exit(1)

# 3. CARGA EN EL DATA WAREHOUSE (Load)
try:
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cur = conn.cursor()

    # Creamos la tabla RAW si no existe y la limpiamos (Full Refresh)
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
        TRUNCATE TABLE raw_crypto; 
    """)

    # Mapeamos el JSON de respuesta a tuplas estructuradas
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

    # Inserción masiva de alto rendimiento
    query = """
        INSERT INTO raw_crypto (id, symbol, name, current_price, market_cap, total_volume, price_change_percentage_24h, ath, ath_change_percentage, extracted_at)
        VALUES %s
    """
    execute_values(cur, query, rows_to_insert)

    conn.commit()
    cur.close()
    conn.close()
    print("🚀 ¡Datos reales inyectados en la capa RAW de Postgres!")
    
except Exception as e:
    print(f"❌ Error durante la carga en Postgres: {e}")
    exit(1)
