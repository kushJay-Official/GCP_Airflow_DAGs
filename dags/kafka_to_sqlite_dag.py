from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.decorators import task
from datetime import datetime, timedelta
import sqlite3
import json
from kafka import KafkaConsumer
import os

# Define file paths
BASE_DIR = "/home/kushjay/testing"
DB_FILE = os.path.join(BASE_DIR, "database.db")
KAFKA_TOPIC = "test_topic"
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_GROUP_ID = "kafka_consumer_group"  # Added group ID

class KafkaToSQLiteETL:
    def __init__(self, db_file, kafka_topic, kafka_servers, group_id):
        self.db_file = db_file
        self.kafka_topic = kafka_topic
        self.kafka_servers = kafka_servers
        self.group_id = group_id

    def consume_kafka_messages(self):
        try:
            consumer = KafkaConsumer(
                self.kafka_topic,
                bootstrap_servers=self.kafka_servers,
                group_id=self.group_id,  # Setting group ID
                auto_offset_reset='earliest',  # Read from the beginning if no offset
                enable_auto_commit=True,  # Commit offsets automatically
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            for message in consumer:
                data = message.value
                print(f"Received Message: {data}")  # Debugging purpose
                insert_query = "INSERT INTO data_lake (id, name, category, price, quantity, date_added) VALUES (?, ?, ?, ?, ?, ?)"
                cursor.execute(insert_query, (data['id'], data['name'], data['category'], data['price'], data['quantity'], data['date_added']))
                conn.commit()

            conn.close()

        except Exception as e:
            print(f"Error in consume_kafka_messages: {e}")
            raise  # Ensures DAG failure on error

class RunKafkaETL:
    def __init__(self, etl_process):
        self.dag = DAG(
            dag_id="kafka_to_sqlite_dag",
            default_args={
                "owner": "airflow",
                "retries": 1,
                "retry_delay": timedelta(minutes=5),
                "execution_timeout": timedelta(minutes=30),
            },
            description="Kafka to SQLite Streaming DAG",
            schedule_interval=None,
            start_date=datetime(2024, 3, 30),
            catchup=False,
            tags=["kafka", "sqlite", "streaming"],
        )
        self.etl_process = etl_process
        self.define_tasks()

    def define_tasks(self):
        with self.dag:
            @task(task_id="consume_kafka", retries=None)
            def consume_kafka():
                self.etl_process.consume_kafka_messages()
            
            start_task = EmptyOperator(task_id="start_task")
            end_task = EmptyOperator(task_id="end_task")
            
            kafka_task = consume_kafka()
            start_task >> kafka_task >> end_task

# Initialize the ETL process and DAG
etl = KafkaToSQLiteETL(DB_FILE, KAFKA_TOPIC, KAFKA_BOOTSTRAP_SERVERS, KAFKA_GROUP_ID)
initiate_process = RunKafkaETL(etl).dag
