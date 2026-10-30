"""Скачать небольшой HTTP-файл и сохранить его без изменений в raw."""

from __future__ import annotations

import hashlib
import logging
from typing import Any

import requests

from airflow.exceptions import AirflowFailException
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

RAW_BUCKET = "raw"


def load_to_raw(
    *,
    source_url: str,
    source_filename: str,
    dataset_slug: str,
    s3_conn_id: str,
    **context: Any,
) -> str:
    """Загрузить исходный файл в raw или оставить уже созданный объект без изменений."""
    key = f"{dataset_slug}/ingested_on={context['ds']}/{source_filename}"
    object_path = f"s3://{RAW_BUCKET}/{key}"
    s3_hook = S3Hook(aws_conn_id=s3_conn_id)

    # Бакеты raw, staging и mart создаёт инфраструктура стенда, DAG их не создаёт.
    if not s3_hook.check_for_bucket(bucket_name=RAW_BUCKET):
        raise AirflowFailException(
            f"Бакет s3://{RAW_BUCKET} не найден. Запустите инфраструктуру командой "
            "`docker compose up -d`, дождитесь статуса healthy у seaweedfs и перезапустите задачу."
        )

    if s3_hook.check_for_key(key=key, bucket_name=RAW_BUCKET):
        logging.info("Raw-объект уже существует и не изменяется: %s", object_path)
        return object_path

    response = requests.get(source_url, timeout=60)
    response.raise_for_status()
    s3_hook.load_bytes(
        bytes_data=response.content,
        key=key,
        bucket_name=RAW_BUCKET,
        replace=False,
    )
    logging.info(
        "HTTP-файл %s сохранён в %s: %d байт, SHA-256 %s",
        source_url,
        object_path,
        len(response.content),
        hashlib.sha256(response.content).hexdigest(),
    )
    return object_path
