import pendulum
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.decorators import task

class ExampleDisplayNameDAG:
    def __init__(self):
        self.dag = DAG(
            dag_id="runtime_config_dag",
            default_args={
                "owner": "airflow",
                "retries": 1,
            },
            description="A simple example DAG to demonstrate runtime configuration",
            schedule=None,
            start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
            catchup=False,
            tags=["runtime config example"],
            params={
                "param1": "default_value",
                "param2": 10
            }
        )
        self.define_tasks()

    def define_tasks(self):
        with self.dag:
            sample_task_1 = EmptyOperator(
                task_id="sample_task_1",
            )

            @task
            def sample_task_2(**kwargs):
                runtime_params = kwargs["params"]
                print(f"Runtime Params: {runtime_params}")

            sample_task_1 >> sample_task_2()

example_dag = ExampleDisplayNameDAG().dag
