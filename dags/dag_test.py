import pendulum
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.decorators import task

class BasedOnTaskflow:
    def __init__(self):
        self.dag = DAG(
            dag_id="sample_classbased_dag",
            default_args={
                "owner": "airflow",
                "retries": 1,
            },
            description="A simple class based example DAG",
            schedule=None,
            start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
            catchup=False,
            tags=["class based airflow"],
        )
        self.define_tasks()
    
    def define_tasks(self):
        with self.dag:
            sample_task_1 = EmptyOperator(
                task_id="sample_task_EmptyOperator",
            )

            @task(task_id="sample_task_decorator")
            def sample_task_decorator(**kwargs):
                dag_run_id = kwargs["dag_run"].run_id  # Access DAG run ID
                print(f"DAG Run ID with kwargs : - {dag_run_id}")

            @task(task_id="sample_task_jinja")
            def sample_task_jinja(dag_run_id: str):
                print(f"DAG Run ID with Jinja : - {dag_run_id}")
            
            # Pass the Jinja template to sample_task_3
            sample_task_1 >> sample_task_decorator() >> sample_task_jinja(dag_run_id="{{ dag_run.run_id }}")

example_dag = BasedOnTaskflow().dag
# redeploy the dag_v9