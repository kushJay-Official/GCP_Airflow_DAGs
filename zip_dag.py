
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
}

dag = DAG(
    'zip_file_dag',
    default_args=default_args,
    description='A DAG to zip a file and log the process',
    schedule_interval=None,  # Set to None to run manually or set a cron expression
    start_date=days_ago(1),
    catchup=False,
)

# Define the command to zip the file
zip_file_command = '''
zip -r /content/output/zipfile.zip /content/airflow/logs/airflow_scheduler.log
'''
  #zip /content/output/zipfile.zip /content/airflow/logs/airflow_scheduler.log > /content/output/zipfile.log 2>&1


# Task to execute the zip command
zip_task = BashOperator(
    task_id='zip_file_task',
    bash_command=zip_file_command,
    dag=dag,
)

# Optionally, you can add more tasks or dependencies here
