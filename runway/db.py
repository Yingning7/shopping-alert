import logging

import pandas as pd
import numpy as np
import psycopg2

from runway.scraper import DTYPES

logger = logging.getLogger(__file__)

TABLE_NAME = "runway"
TABLE_CREATE_SQL = f"""
    CREATE TABLE {{schema_name}}.{TABLE_NAME}(
        item_id TEXT NOT NULL,
        name TEXT NOT NULL,
        brand TEXT NOT NULL,
        original_price DOUBLE PRECISION NOT NULL,
        current_price DOUBLE PRECISION NOt NULL,
        currency TEXT NOT NULL,
        color TEXT NOT NULL,
        size TEXT NOT NULL,
        is_available BOOLEAN NOT NULL,
        unit_left DOUBLE PRECISION,
        url TEXT NOT NULL,
        asof TIMESTAMPTZ NOT NULL,
        PRIMARY KEY (item_id, color, size, asof)
    );
    CREATE INDEX runway_item_id ON {{schema_name}}.{TABLE_NAME} (item_id);
    CREATE INDEX runway_color ON {{schema_name}}.{TABLE_NAME} (color);
    CREATE INDEX runway_size ON {{schema_name}}.{TABLE_NAME} (size);
    CREATE INDEX runway_asof ON {{schema_name}}.{TABLE_NAME} (asof);
    CREATE INDEX runway_item_id_asof ON {{schema_name}}.{TABLE_NAME} (item_id, asof);
"""
DATA_INSERT_SQL = f"""
    INSERT INTO {{schema_name}}.{TABLE_NAME} (item_id, name, brand, original_price, current_price, currency, color, size, is_available, unit_left, url, asof)
    VALUES
        (%(item_id)s, %(name)s, %(brand)s, %(original_price)s, %(current_price)s, %(currency)s, %(color)s, %(size)s, %(is_available)s, %(unit_left)s, %(url)s, %(asof)s)
"""
QUERY_LAST_DATA_SQL = f"""
    SELECT
        *
    FROM
        {{schema_name}}.{TABLE_NAME}
    WHERE
        item_id = '{{item_id}}'
        AND asof = (SELECT MAX(asof) FROM {{schema_name}}.{TABLE_NAME} WHERE item_id = '{{item_id}}')
"""


def create_table(schema_name: str, db_creds: dict[str, str | int]) -> None:
    logger.info(f'Creating the table: {schema_name}.{TABLE_NAME}.')
    with psycopg2.connect(**db_creds) as conn:
        with conn.cursor() as cur:
            cur.execute(TABLE_CREATE_SQL.format(schema_name=schema_name))
        conn.commit()


def insert_data(schema_name: str, db_creds: dict[str, str | int], df: pd.DataFrame) -> None:
    logger.info(f'Inserting data into the table: {schema_name}.{TABLE_NAME}.')
    df = df.copy().replace({np.nan: None})
    records = [row.to_dict() for _, row in df.iterrows()]
    with psycopg2.connect(**db_creds) as conn:
        with conn.cursor() as cur:
            cur.executemany(DATA_INSERT_SQL.format(schema_name=schema_name), records)
        conn.commit()


def query_last_data(schema_name: str, db_creds: dict[str, str | int], item_id: str) -> pd.DataFrame:
    with psycopg2.connect(**db_creds) as conn:
        with conn.cursor() as cur:
            cur.execute(QUERY_LAST_DATA_SQL.format(schema_name=schema_name, item_id=item_id))
            data = cur.fetchall()
            column_names = [desc[0] for desc in cur.description]
    df = pd.DataFrame(data, columns=column_names).astype(DTYPES)
    return df
