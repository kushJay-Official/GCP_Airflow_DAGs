from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.decorators import task
from datetime import datetime, timedelta
import sqlite3
import pandas as pd
import os

# Define file paths
BASE_DIR = "/home/kushjay/testing"
DB_FILE = os.path.join(BASE_DIR, "database.db")
OUTPUT_FILE = os.path.join(BASE_DIR, "output_data/laptop_data.csv.zip")
SQL_FILE = os.path.join(BASE_DIR, "sql/read_data.sql")


class SqlETLProcess:
    def __init__(self, db_file, output_file, sql_file):
        self.db_file = db_file
        self.output_file = output_file
        self.sql_file = sql_file

    def read_sql_query(self):
        try:
            with open(self.sql_file, 'r') as file:
                query = file.read().strip()
            print(f"Executing SQL Query: {query}")
            return query
        except Exception as e:
            print(f"Error reading SQL file: {e}")
            raise

    def extract_data(self):
        try:
            query = self.read_sql_query()
            conn = sqlite3.connect(self.db_file)
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df.to_dict(orient='records')
        except Exception as e:
            print(f"Error in extract_data: {e}")
            raise

    def transform_data(self, data):
        try:
            df = pd.DataFrame(data)
            df['price'] = df['price'] * 1.1  # Example transformation: increase price by 10%
            df.to_csv(self.output_file, index=False, compression='zip')  # Save transformed data to a new file
            return df.to_dict(orient='records')
        except Exception as e:
            print(f"Error in transform_data: {e}")
            raise

    def load_data(self, data):
        try:
            df = pd.DataFrame(data)
            df.to_csv(self.output_file, index=False)  # Save transformed data again (mock load)
        except Exception as e:
            print(f"Error in load_data: {e}")
            raise



class RunETLDAG:
    def __init__(self, etl_process):
        self.dag = DAG(
            dag_id="sql_etl_dag",
            default_args={
                "owner": "airflow",
                "retries": 1,
                "retry_delay": timedelta(minutes=5),
                "execution_timeout": timedelta(minutes=30),  # Increase timeout to prevent premature termination
            },
            description="SQLite ETL DAG : extracts data from SQLite, transforms it, and loads it into a CSV file",
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
                return self.etl_process.extract_data()
            
            @task(task_id="Transform-data", retries=1)
            def transform_data(data):
                return self.etl_process.transform_data(data)
            
            @task(task_id="CSV-load_data", retries=1)
            def load_data(data):
                self.etl_process.load_data(data)
            
            start_task = EmptyOperator(task_id="start_process")
            end_task = EmptyOperator(task_id="end_process")
            
            extracted_data = extract_data()
            transformed_data = transform_data(extracted_data)
            #load_data(transformed_data)
            
            start_task >> extracted_data >> transformed_data >> load_data(transformed_data) >> end_task

# Instantiate ETL process
etl = SqlETLProcess(DB_FILE, OUTPUT_FILE, SQL_FILE)
initiate_process = RunETLDAG(etl).dag
# 