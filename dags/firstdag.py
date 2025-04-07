from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.decorators import task
from datetime import datetime

# Define a Python function for the PythonOperator
def sample_python_task():
    print("This is a Python task!")

# Define the DAG
with DAG(
    dag_id="sample_test_dag",
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:

    # Define a task using the @task decorator
    @task
    def task_decorator_example():
        print("This is a task created using the @task decorator!")

    # Define a PythonOperator task
    python_task = PythonOperator(
        task_id="python_task",
        python_callable=sample_python_task,
    )

    # Define a BashOperator task
    bash_task = BashOperator(
        task_id="bash_task",
        bash_command="echo 'This is a Bash task!'",
    )

    # Set task dependencies
    task_decorator_example() >> python_task >> bash_task
