from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import snowflake.connector
import os

def snowflake_setup():
    # Establish a connection to Snowflake using environment variables
    conn = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "WH_PUBLICATIONS_ETL"),
        role=os.getenv("SNOWFLAKE_ROLE")
    )

    # Create a cursor
    cursor = conn.cursor()

    # Get the database, schema, and table names from environment variables, or use default values
    database_name = os.getenv("SNOWFLAKE_DATABASE", "DB_CFA_PUBLICATIONS")
    schema_name = os.getenv("SNOWFLAKE_SCHEMA", "CFA_PUBLICATIONS")
    warehouse_name = os.getenv("SNOWFLAKE_WAREHOUSE", "WH_PUBLICATIONS_ETL")
    table_name = os.getenv("SNOWFLAKE_TABLE", "PUBLICATION_LIST")

    # Script to create warehouse (if not exists)
    create_warehouse_script = f"""
    CREATE WAREHOUSE IF NOT EXISTS {warehouse_name}
    WITH WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE;
    """

    # Script to create database
    create_database_script = f"CREATE DATABASE IF NOT EXISTS {database_name};"

    # Script to use the database
    use_database_script = f"USE DATABASE {database_name};"

    # Script to create schema (if not exists)
    create_schema_script = f"CREATE SCHEMA IF NOT EXISTS {schema_name};"

    # Script to use the schema
    use_schema_script = f"USE SCHEMA {schema_name};"

    # Script to drop and create the table within the schema
    create_table_script = f"""
    CREATE OR REPLACE TABLE {database_name}.{schema_name}.{table_name} (
        ID INT AUTOINCREMENT(1, 1) PRIMARY KEY,
        TITLE VARCHAR(250),
        BRIEF_SUMMARY VARCHAR(1000),
        DATE VARCHAR(20),
        AUTHOR VARCHAR(500),
        IMAGE_LINK VARCHAR(300),
        PDF_LINK VARCHAR(300),
        RESEARCH_NOTES VARCHAR(1500),
        CREATED_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """


    try:
        # Execute each statement separately
        print(f"Creating warehouse '{warehouse_name}' if not already exists...")
        cursor.execute(create_warehouse_script)
        print(f"Warehouse '{warehouse_name}' successfully created or confirmed to already exist.")

        print(f"Creating database '{database_name}' if not already exists...")
        cursor.execute(create_database_script)
        print(f"Database '{database_name}' successfully created or confirmed to already exist.")

        print(f"Switching to database '{database_name}'...")
        cursor.execute(use_database_script)
        print(f"Successfully switched to database '{database_name}'.")

        print(f"Creating schema '{schema_name}' if not already exists...")
        cursor.execute(create_schema_script)
        print(f"Schema '{schema_name}' successfully created or confirmed to already exist.")

        print(f"Switching to schema '{schema_name}'...")
        cursor.execute(use_schema_script)
        print(f"Successfully switched to schema '{schema_name}'.")

        print(f"Dropping and recreating the '{table_name}' table...")
        cursor.execute(create_table_script)
        print(f"Table '{table_name}' successfully created or replaced.")

    except snowflake.connector.errors.ProgrammingError as e:
        print(f"Error during setup: {e}")

    finally:
        cursor.close()
        conn.close()
        print("Snowflake connection closed.")


# Define the DAG for Airflow
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 10, 22),
    'retries': 1,
}

with DAG(
    'snowflake_setup_dag',
    default_args=default_args,
    description='DAG for setting up Snowflake warehouse, database, schema, and table',
    schedule_interval=None,
    catchup=False,
) as dag:

    setup_snowflake = PythonOperator(
        task_id='setup_snowflake',
        python_callable=snowflake_setup,
        dag=dag
    )

    setup_snowflake
