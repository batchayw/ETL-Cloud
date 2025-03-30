from datetime import datetime, timedelta
from airflow import DAG # type: ignore
from airflow.operators.python import PythonOperator # type: ignore
from airflow.providers.postgres.operators.postgres import PostgresOperator # type: ignore
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator # type: ignore
from airflow.providers.docker.operators.docker import DockerOperator # type: ignore
from airflow.utils.dates import days_ago # type: ignore

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': days_ago(1),
}

dag = DAG(
    'etl_pipeline',
    default_args=default_args,
    description='Complete ETL pipeline from extraction to loading',
    schedule_interval='@daily',
    catchup=False,
    tags=['etl', 'production']
)

with dag:
    # Extraction tasks
    extract_api_task = DockerOperator(
        task_id='extract_from_api',
        image='nifi:latest',
        api_version='auto',
        auto_remove=True,
        command="/opt/nifi/nifi-current/bin/nifi.sh run -f /opt/nifi/nifi-current/extract_flow.xml",
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        environment={
            'API_URL': 'https://api.william.com/data',
            'API_KEY': '{{ var.value.api_key }}'
        },
        volumes=['/data/nifi:/opt/nifi/nifi-current']
    )

    extract_db_task = PostgresOperator(
        task_id='extract_from_database',
        postgres_conn_id='source_db',
        sql="""
            COPY (SELECT * FROM source_data 
                  WHERE updated_at > '{{ prev_ds }}' AND updated_at <= '{{ ds }}')
            TO '/data/extracts/source_data_{{ ds }}.csv' WITH CSV HEADER;
        """
    )

    # Transformation tasks
    clean_data_task = SparkSubmitOperator(
        task_id='clean_raw_data',
        application='/jobs/clean_data.py',
        conn_id='spark_default',
        jars='/opt/spark/jars/hadoop-aws-3.3.1.jar,/opt/spark/jars/aws-java-sdk-bundle-1.11.901.jar',
        application_args=['--date', '{{ ds }}'],
        verbose=True
    )

    enrich_data_task = SparkSubmitOperator(
        task_id='enrich_clean_data',
        application='/jobs/enrich_data.py',
        conn_id='spark_default',
        application_args=['--date', '{{ ds }}'],
        verbose=True
    )

    # Loading tasks
    load_to_dwh_task = PostgresOperator(
        task_id='load_to_data_warehouse',
        postgres_conn_id='dwh_postgres',
        sql='load_to_dwh.sql',
        params={'execution_date': '{{ ds }}'}
    )

    create_partitions_task = PythonOperator(
        task_id='create_table_partitions',
        python_callable='data_partitioning.create_partitions'
    )

    # Data quality check
    dq_check_task = PostgresOperator(
        task_id='data_quality_checks',
        postgres_conn_id='dwh_postgres',
        sql="""
            INSERT INTO dq_checks (check_date, check_name, passed, records_checked)
            SELECT 
                '{{ ds }}' AS check_date,
                'customer_count' AS check_name,
                COUNT(*) > 0 AS passed,
                COUNT(*) AS records_checked
            FROM customers
            WHERE load_date = '{{ ds }}';
            
            INSERT INTO dq_checks (check_date, check_name, passed, records_checked)
            SELECT 
                '{{ ds }}' AS check_date,
                'null_emails' AS check_name,
                COUNT(*) = 0 AS passed,
                COUNT(*) AS records_checked
            FROM customers
            WHERE email IS NULL AND load_date = '{{ ds }}';
        """
    )

    # Define dependencies
    [extract_api_task, extract_db_task] >> clean_data_task
    clean_data_task >> enrich_data_task
    enrich_data_task >> load_to_dwh_task
    load_to_dwh_task >> create_partitions_task
    create_partitions_task >> dq_check_task