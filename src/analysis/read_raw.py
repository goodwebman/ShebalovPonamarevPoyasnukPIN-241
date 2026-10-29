"""Прочитать raw-объект из S3 через DuckDB без создания таблиц."""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path

import duckdb


def reader_for(filename: str) -> str:
    """Выбрать DuckDB table function по расширению исходного файла."""
    suffix = Path(filename).suffix.lower()
    readers = {
        ".csv": "read_csv",
        ".json": "read_json_auto",
        ".jsonl": "read_json_auto",
        ".ndjson": "read_json_auto",
        ".parquet": "read_parquet",
    }
    try:
        return readers[suffix]
    except KeyError as error:
        message = f"Для формата {suffix or 'без расширения'} не задан DuckDB reader."
        raise ValueError(message) from error


def configure_s3(connection: duckdb.DuckDBPyConnection) -> None:
    """Настроить S3-совместимый доступ DuckDB к локальному SeaweedFS."""
    endpoint = os.getenv("S3_ENDPOINT")
    access_key = os.getenv("S3_ACCESS_KEY")
    secret_key = os.getenv("S3_SECRET_KEY")

    connection.execute("INSTALL httpfs")
    connection.execute("LOAD httpfs")
    connection.execute(f"SET s3_endpoint = '{endpoint}'")
    connection.execute("SET s3_url_style = 'path'")
    connection.execute("SET s3_use_ssl = false")
    connection.execute(f"SET s3_access_key_id = '{access_key}'")
    connection.execute(f"SET s3_secret_access_key = '{secret_key}'")


def csv_header(connection: duckdb.DuckDBPyConnection, object_path: str) -> list[str]:
    """Прочитать имена столбцов из первой строки CSV-объекта.

    DuckDB 1.1 читает CSV только в UTF-8, а заголовок SeoulBikeData.csv записан в Latin-1
    (символ «°»). Поэтому первая строка того же объекта читается как байты и декодируется
    отдельно, а данные затем читаются со второй строки с этими именами.
    """
    content = connection.execute("SELECT content FROM read_blob(?)", [object_path]).fetchone()[0]
    first_line = bytes(content).split(b"\n", 1)[0].rstrip(b"\r")
    try:
        header = first_line.decode("utf-8")
    except UnicodeDecodeError:
        header = first_line.decode("latin-1")
    return next(csv.reader([header]))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", required=True, help="S3-путь к raw-объекту.")
    args = parser.parse_args()

    object_path = args.path
    reader = reader_for(object_path)

    connection = duckdb.connect()
    configure_s3(connection)
    if reader == "read_csv":
        names = csv_header(connection, object_path)
        result = connection.execute(
            """
            SELECT * FROM read_csv(
                ?, header = false, skip = 1, names = ?, hive_partitioning = false
            ) LIMIT 5
            """,
            [object_path, names],
        )
    else:
        result = connection.execute(
            f"SELECT * FROM {reader}(?, hive_partitioning = false) LIMIT 5", [object_path]
        )
    print([column[0] for column in result.description])
    for row in result.fetchall():
        print(row)


if __name__ == "__main__":
    main()
