from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator # type: ignore
from airflow.providers.postgres.operators.postgres import PostgresOperator # type: ignore
from airflow.providers.amazon.aws.operators.s3 import S3DeleteObjectsOperator # type: ignore

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def notify_failure(context):
    print(f"Task {context['task_instance'].task_id} failed. Initiating rollback...")

with DAG(
    'rollback_pipeline',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    on_failure_callback=notify_failure
) as dag:

    rollback_db = PostgresOperator(
        task_id='rollback_database',
        postgres_conn_id='postgres_dwh',
        sql='''
        BEGIN;
        DELETE FROM customers WHERE load_date = '{{ ds }}';
        DELETE FROM customer_metrics WHERE metric_date = '{{ ds }}';
        COMMIT;
        '''
    )

    rollback_storage = S3DeleteObjectsOperator(
        task_id='rollback_storage',
        bucket='enriched-data',
        prefix='{{ ds }}',
        aws_conn_id='minio_conn'
    )

    notify_team = PythonOperator(
        task_id='notify_team',
        python_callable=lambda: print("Rollback completed. Please investigate the failure.")
    )

    rollback_db >> rollback_storage >> notify_team