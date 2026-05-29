# 🚀 Crypto Data Pipeline Histórico (Modern Data Stack)

Este proyecto implementa un pipeline de datos robusto y automatizado de extremo a extremo para la ingesta, transformación histórica y visualización de datos del mercado de criptomonedas utilizando la API pública de **CoinGecko**.

## 🏗️ Arquitectura y Capas de Datos
El pipeline está completamente contenerizado en **Docker** y sigue la arquitectura de capas analíticas:

1. **Ingesta (Python):** Un script interactúa con la API de CoinGecko de forma acumulativa (incremental) y aplica una política de retención auto-limpiable de **90 días (3 meses)** para garantizar la agilidad del almacenamiento.
2. **Orquestación (Apache Airflow):** Controla los tiempos de ejecución, reintentos y dependencias del flujo.
3. **Transformación (dbt Core v1.12):**
   * `stg_crypto`: Modela el tipado, renombrado y estructura limpia de los datos entrantes.
   * `mart_resumen_crypto`: Aplica funciones de ventana avanzadas (`PARTITION BY extracted_at`) para calcular rankings de liquidez y *Market Share* global minuto a minuto de manera histórica.
4. **Visualización (Metabase BI):** Dashboard interactivo conectado a la capa de marts que permite analizar las dominancias del mercado y visualizar gráficos de líneas con el evolutivo de precios en el tiempo.

## 🛠️ Tecnologías Utilizadas
* Python 3 (`requests`, `psycopg2`)
* Apache Airflow
* dbt Core (v1.12)
* PostgreSQL
* Metabase BI
* Docker & Docker Compose
