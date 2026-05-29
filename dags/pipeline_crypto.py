from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'felipe',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=30),  # Si la API parpadea, reintenta a los 30 segundos
}

with DAG(
    'pipeline_crypto_coingecko',
    default_args=default_args,
    description='Pipeline automatizado de criptomonedas cada 5 minutos',
    schedule='*/5 * * * *',          # Expresión CRON para cada 5 minutos
    start_date=datetime(2026, 1, 1), # Año actual, arranca limpio
    catchup=False,                   # Evita que Airflow intente recuperar el pasado
    max_active_runs=1,               # Evita que se pisen las ejecuciones
) as dag:

    # Tarea 1: Descargar los datos frescos de la API
    ingesta_datos = BashOperator(
        task_id='ingestar_desde_coingecko',
        bash_command='python /opt/airflow/ingestor.py'
    )

    # Tarea 2: Compilar y refrescar las tablas en dbt
    transformacion_dbt = BashOperator(
        task_id='ejecutar_dbt_run',
        bash_command='dbt run --project-dir /opt/airflow/dbt_proyecto'
    )

    # Tarea 3: Pasar el control de calidad
    pruebas_calidad_dbt = BashOperator(
        task_id='ejecutar_dbt_test',
        bash_command='dbt test --project-dir /opt/airflow/dbt_proyecto'
    )

    # 🔗 LA CADENA DE MANDO (El orden de las flechas)
    ingesta_datos >> transformacion_dbt >> pruebas_calidad_dbt
