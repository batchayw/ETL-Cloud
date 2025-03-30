import psycopg2 # type: ignore
from psycopg2 import sql # type: ignore

def create_partitions():
    conn = psycopg2.connect(
        host="postgres",
        database="etl_dwh",
        user="etl_user",
        password="etlpassword123"
    )
    cursor = conn.cursor()

    # Create partition schema if not exists
    cursor.execute("CREATE SCHEMA IF NOT EXISTS partman;")
    
    # Enable pg_partman extension
    cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_partman WITH SCHEMA partman;")

    # Create partitioned table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer_transactions_partitioned (
            transaction_id BIGSERIAL,
            customer_id INT,
            amount DECIMAL(10,2),
            transaction_date TIMESTAMP,
            category VARCHAR(100),
            PRIMARY KEY (transaction_id, transaction_date)
        ) PARTITION BY RANGE (transaction_date);
    """)

    # Configure pg_partman to manage partitions
    cursor.execute("""
        SELECT partman.create_parent(
            p_parent_table := 'public.customer_transactions_partitioned',
            p_control := 'transaction_date',
            p_type := 'native',
            p_interval := 'daily',
            p_premake := 7
        );
    """)

    # Create default partition
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer_transactions_default PARTITION OF customer_transactions_partitioned
        DEFAULT;
    """)

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_partitions()