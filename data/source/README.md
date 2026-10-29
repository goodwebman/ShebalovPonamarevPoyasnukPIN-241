# Происхождение исходного файла

Файл в этой папке - неизменяемая локальная копия набора Seoul Bike Sharing Demand из UCI Machine Learning Repository.
Обычный запуск DAG `ingest_raw` его не читает: копия нужна для ручного fallback, если первоисточник недоступен.

| Локальный файл      | Официальный URL                                                                                            |    Размер | SHA-256                                                            |
|---------------------|------------------------------------------------------------------------------------------------------------|----------:|--------------------------------------------------------------------|
| `SeoulBikeData.csv` | [SeoulBikeData.csv](https://archive.ics.uci.edu/ml/machine-learning-databases/00560/SeoulBikeData.csv)     | 604 166 Б | `373339b71a8935d69e9af0abf26a70744632119862eeb3919efb389a7b749c60` |

Файл побайтно совпадает с `SeoulBikeData.csv` из
[официального архива набора](https://archive.ics.uci.edu/static/public/560/seoul+bike+sharing+demand.zip).

## Первичный источник и условия использования

- Страница набора: [UCI - Seoul Bike Sharing Demand](https://archive.ics.uci.edu/dataset/560/seoul+bike+sharing+demand),
  DOI [10.24432/C5F62R](https://doi.org/10.24432/C5F62R).
- Лицензия: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Цитирование по рекомендации UCI:
  «Seoul Bike Sharing Demand [Dataset]. (2020). UCI Machine Learning Repository. https://doi.org/10.24432/C5F62R».
- Дата загрузки: 2026-10-26. Последнее обновление метаданных набора в UCI: 2024-02-05.

Лицензия курса на этот файл не распространяется: действуют условия первоисточника.

## Зафиксированная версия

- 8 760 строк данных и строка заголовка, 14 столбцов, окончания строк CRLF.
- Период: 2017-12-01 00:00 - 2018-11-30 23:00 (поля `Date` в формате `dd/mm/yyyy` и `Hour`).
- Кодировка ISO-8859-1: символ `°` в именах `Temperature(°C)` и `Dew point temperature(°C)` записан байтом `0xB0`.
  Строки данных содержат только ASCII.
- Файл не сокращался и не преобразовывался. `.gitattributes` отключает для этой папки нормализацию переводов строк,
  чтобы Git хранил байты без изменений.
