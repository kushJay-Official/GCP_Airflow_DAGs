from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.decorators import task
from datetime import datetime, timedelta
import pandas as pd
import os

# Define file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = "/home/kushjay/testing/source_data/large_sample_data.csv"
OUTPUT_FILE = "/home/kushjay/testing/output_data/transformed_data_1.csv"

class ETLProcess:
    def __init__(self, csv_file, output_file):
        self.csv_file = csv_file
        self.output_file = output_file

    def extract_data(self):
        try:
            chunk_size = 100000  # Process large files in chunks
            data = []
            for chunk in pd.read_csv(self.csv_file, chunksize=chunk_size, low_memory=False):
                data.extend(chunk.to_dict(orient='records'))
            return data
        except Exception as e:
            print(f"Error in extract_data: {e}")
            return []

    def transform_data(self, data):
        try:
            df = pd.DataFrame(data)
            df['price'] = df['price'] * 2.02  # Example transformation: increase price by 10%
            df.to_csv(self.output_file, index=False)  # Save transformed data to a new file
            return df.to_dict(orient='records')
        except Exception as e:
            print(f"Error in transform_data: {e}")
            return []

    def load_data(self, data):
        try:
            df = pd.DataFrame(data)
            df.to_csv(self.output_file, index=False)  # Save transformed data again (mock load)
        except Exception as e:
            print(f"Error in load_data: {e}")

class RunETLDAG:
    def __init__(self, etl_process):
        self.dag = DAG(
            dag_id="basic_etl_dag",
            default_args={
                "owner": "airflow",
                "retries": 1,
                "retry_delay": timedelta(minutes=5),
                "execution_timeout": timedelta(minutes=30),  # Increase timeout to prevent premature termination
            },
            description="Basic ETL DAG",
            schedule_interval=None,
            start_date=datetime(2024, 3, 30),
            catchup=False,
            tags=["basic", "etl"],
        )
        self.etl_process = etl_process
        self.define_elt_tasks()

    def define_elt_tasks(self):
        with self.dag:
            @task(task_id="extract_data", retries=3)
            def extract_data():
                return self.etl_process.extract_data()
            
            @task(task_id="transform_data", retries=3)
            def transform_data(data):
                return self.etl_process.transform_data(data)
            
            @task(task_id="load_data", retries=3)
            def load_data(data):
                self.etl_process.load_data(data)
            
            start_task = EmptyOperator(task_id="start_task")
            end_task = EmptyOperator(task_id="end_task")
            
            extracted_data = extract_data()
            transformed_data = transform_data(extracted_data)
            #load_data(transformed_data)
            
            start_task >> extracted_data >> transformed_data >> load_data(transformed_data) >> end_task

# Instantiate ETL process
etl = ETLProcess(CSV_FILE, OUTPUT_FILE)
initiate_process = RunETLDAG(etl).dag
#