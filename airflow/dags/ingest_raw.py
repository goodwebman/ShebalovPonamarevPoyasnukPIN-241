"""DAG ЛР № 2: дождаться HTTP-источника Seoul Bike Sharing Demand и загрузить файл в raw."""

from urllib.parse import urlsplit

import pendulum

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.http.sensors.http import HttpSensor
from ingestion.load_raw import load_to_raw

# Источник из Project Brief: прямой CSV-файл UCI Machine Learning Repository.
# Host URL должен совпадать с AIRFLOW_CONN_SOURCE_HTTP_CONN в .env.
SOURCE_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00560/SeoulBikeData.csv"
SOURCE_FILENAME = "SeoulBikeData.csv"
DATASET_SLUG = "seoul_bike_sharing"
HTTP_CONN_ID = "source_http_conn"
S3_CONN_ID = "s3_conn"

parsed_url = urlsplit(SOURCE_URL)
endpoint = parsed_url.path or "/"
if parsed_url.query:
    endpoint = f"{endpoint}?{parsed_url.query}"

with DAG(
    dag_id="ingest_raw",
    description="Ждёт HTTP-источник Seoul Bike Sharing Demand и сохраняет файл в raw-слой S3.",
    start_date=pendulum.datetime(2026, 10, 1, tz="UTC"),
    schedule="@daily",
    catchup=False,
    max_active_runs=1,
    tags=["raw"],
) as dag:
    wait_for_primary_source = HttpSensor(
        task_id="wait_for_primary_source",
        http_conn_id=HTTP_CONN_ID,
        endpoint=endpoint,
        method="HEAD",
        poke_interval=60,
        timeout=600,
    )

    load_to_raw_task = PythonOperator(
        task_id="load_to_raw",
        python_callable=load_to_raw,
        op_kwargs={
            "source_url": SOURCE_URL,
            "source_filename": SOURCE_FILENAME,
            "dataset_slug": DATASET_SLUG,
            "s3_conn_id": S3_CONN_ID,
        },
    )

    wait_for_primary_source >> load_to_raw_task
