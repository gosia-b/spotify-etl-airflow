from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from spotify_etl import extract_data, transform_data, load_data


with DAG(
        'spotify_dag',
        start_date=datetime(2022, 7, 25),
        schedule_interval='@daily',
        catchup=True) as dag:

    extract = PythonOperator(
        task_id='extract',
        python_callable=extract_data,
        dag=dag
    )

    transform = PythonOperator(
        task_id='transform',
        python_callable=transform_data,
        dag=dag
    )

    load = PythonOperator(
        task_id='load',
        python_callable=load_data,
        dag=dag
    )

    extract >> transform >> load
