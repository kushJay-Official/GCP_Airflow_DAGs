from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.decorators import task
from datetime import datetime, timedelta
import sqlite3
import pandas as pd
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define file paths
BASE_DIR = "/home/kushjay/testing"
DB_FILE = os.path.join(BASE_DIR, "database.db")
SQL_FILE = os.path.join(BASE_DIR, "sql/read_data.sql")
TARGET_TABLE = os.path.join(BASE_DIR, "sql/laptop_ddl.sql")

class SqlETLProcess:
    def __init__(self, db_file, sql_file, target_table):
        self.db_file = db_file
        self.sql_file = sql_file
        self.target_table = target_table

    def read_sql_query(self,sql_file):
        try:
            with open(sql_file, 'r') as file:
                query = file.read().strip()
            logger.info(f"Executing SQL Query: {query}")
            return query
        except Exception as e:
            logger.error(f"Error reading SQL file: {e}")
            raise

    def extract_data(self):
        try:
            query = self.read_sql_query(self.sql_file)
            conn = sqlite3.connect(self.db_file)
            df = pd.read_sql_query(query, conn)
            conn.close()
            logger.info("Data extraction process completed")
            return df.to_dict(orient='records')
        except Exception as e:
            logger.error(f"Error in extract_data: {e}")
            raise

    def transform_data(self, data):
        try:
            df = pd.DataFrame(data)
            df['price'] = df['price'] * 1.1  # Example transformation: increase price by 10%
            return df
        except Exception as e:
            print(f"Error in transform_data: {e}")
            raise

    def load_data(self, df):
        try:
            logger.info("Starting data load process")
            conn = sqlite3.connect(self.db_file) 
            # Ensure the target table exists using the extracted schema
            create_table_query = self.read_sql_query(self.target_table)
            conn.execute(create_table_query)
            conn.commit()
            logger.info(f"Table created successfully")
            # Insert transformed data
            df.to_sql('novel_data', conn, if_exists='append', index=False)
            conn.close()
            logger.info(f"Data load process completed ")
        except Exception as e:
            logger.error(f"Error in load_data: {e}")
            raise

class RunETLDAG:
    def __init__(self, etl_process):
        self.dag = DAG(
            dag_id="sqlite_etl_sql_to_sql_dag",
            default_args={
                "owner": "airflow",
                "retries": 1,
                "retry_delay": timedelta(minutes=5),
                "execution_timeout": timedelta(minutes=30),
            },
            description="SQLite ETL DAG: Extracts, Transforms, and Loads data into another table",
            schedule_interval=None,
            start_date=datetime(2024, 3, 30),
            catchup=False,
            tags=["sqlite", "etl"],
        )
        self.etl_process = etl_process
        self.define_elt_tasks()

    def define_elt_tasks(self):
        with self.dag:
            @task(task_id="SQLite-extract_data", retries=1)
            def extract_data():
                df = self.etl_process.extract_data()
                return df
            
            @task(task_id="Transform-data", retries=1)
            def transform_data(df):
                df = self.etl_process.transform_data(df)
                return df
            
            @task(task_id="SQLite-load_data", retries=1)
            def load_data(df):
                self.etl_process.load_data(df)
            
            start_task = EmptyOperator(task_id="start_process")
            end_task = EmptyOperator(task_id="end_process")
            
            extracted_data = extract_data()
            transformed_data = transform_data(extracted_data)
            
            start_task >> extracted_data >> transformed_data >> load_data(transformed_data) >> end_task

# Instantiate ETL process
etl = SqlETLProcess(DB_FILE, SQL_FILE, TARGET_TABLE)
initiate_process = RunETLDAG(etl).dag
