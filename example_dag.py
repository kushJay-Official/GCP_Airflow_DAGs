
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime

def hello_world():
    print("Hello, Jay!")

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
}

with DAG(
    dag_id='example_dag',
    default_args=default_args,
    description='A simple example DAG',
    schedule_interval='@daily',
    catchup=False,
) as dag:

    start = DummyOperator(task_id='start')

    task1 = PythonOperator(
        task_id='hello_task',
        python_callable=hello_world,
    )

    end = DummyOperator(task_id='end')

    start >> task1 >> end
