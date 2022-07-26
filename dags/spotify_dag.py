from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from spotify_etl import run_spotify_etl


with DAG(
        'spotify_dag',
        start_date=datetime(2022, 7, 25),
        schedule_interval='@daily',
        catchup=True) as dag:

    run_etl = PythonOperator(
        task_id='spotify_etl',
        python_callable=run_spotify_etl,
        dag=dag
    )

    run_etl
