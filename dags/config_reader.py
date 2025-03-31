import pendulum
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator

class ConfigReaderDAG:
    def __init__(self):
        self.dag = DAG(
            dag_id="config_reader_dag",
            default_args={
                "owner": "airflow",
                "retries": 1,
            },
            description="DAG that reads data from dag_run.config using Jinja templating",
            schedule=None,
            start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
            catchup=False,
            tags=["config reader"],
        )
        self.define_tasks()
    
    def define_tasks(self):
        with self.dag:
            start_task = EmptyOperator(
                task_id="start_task",
            )

            read_config = BashOperator(
                task_id="read_config",
                bash_command='echo "Received param_value: {{ dag_run.conf.get(\'param_key\', \'default_value\') }}"'
                #jinja template is woking only in bash operator not in python operator 
            )
            
            start_task >> read_config

example_dag = ConfigReaderDAG().dag
