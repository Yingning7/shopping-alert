import logging
import psycopg2

import pandas as pd
import numpy as np

logger = logging.getLogger(__file__)

SCHEMA_NAME = 'shopping_alert'
TABLE_NAME = 'inventory'
DB_CREDS = {
    'dbname': 'shopping-alert-db',
    'user': 'admin',
    'password': 'admin',
    'host': 'localhost',
    'port': 5432
}

PD_DTYPES = {
    'platform': 'str',
    'item_id': 'str',
    'name': 'str',
    'brand': 'str',
    'original_price': 'float',
    'current_price': 'float',
    'currency': 'str',
    'color': 'str',
    'size': 'str',
    'is_available': 'bool',
    'unit_left': 'float',
    'url': 'str',
    'asof': 'datetime64[ns, UTC]'
}

TABLE_CREATE_SQL = f"""
    CREATE TABLE {SCHEMA_NAME}.{TABLE_NAME}(
        platform TEXT NOT NULL,
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
        PRIMARY KEY (platform, item_id, color, size, asof)
    );
    CREATE INDEX inventory_platform ON {SCHEMA_NAME}.{TABLE_NAME} (platform);
    CREATE INDEX inventory_item_id ON {SCHEMA_NAME}.{TABLE_NAME} (item_id);
    CREATE INDEX inventory_asof ON {SCHEMA_NAME}.{TABLE_NAME} (asof);
    CREATE INDEX inventory_platform_item_id_asof ON {SCHEMA_NAME}.{TABLE_NAME} (platform, item_id, asof);
"""
DATA_INSERT_SQL = f"""
    INSERT INTO {SCHEMA_NAME}.{TABLE_NAME} (platform, item_id, name, brand, original_price, current_price, currency, color, size, is_available, unit_left, url, asof)
    VALUES
        (%(platform)s, %(item_id)s, %(name)s, %(brand)s, %(original_price)s, %(current_price)s, %(currency)s, %(color)s, %(size)s, %(is_available)s, %(unit_left)s, %(url)s, %(asof)s)
"""


def init_schema() -> None:
    logger.info(f'Creating schema {SCHEMA_NAME} if it does not exist.')
    with psycopg2.connect(**DB_CREDS) as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}")
        conn.commit()


def check_table_exists() -> bool:
    logger.info(f'Checking if the table {SCHEMA_NAME}.{TABLE_NAME} exists or not.')
    with psycopg2.connect(**DB_CREDS) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT EXISTS (
                    SELECT 1
                    FROM pg_tables
                    WHERE schemaname = '{SCHEMA_NAME}' AND tablename = '{TABLE_NAME}'
                )
                """
            )
            table_is_exists = cursor.fetchall()[0][0]
    logger.info(f'The table {SCHEMA_NAME}.{TABLE_NAME} existence: {table_is_exists}.')
    return table_is_exists


def create_table() -> None:
    logger.info(f'Creating the table: {SCHEMA_NAME}.{TABLE_NAME}.')
    with psycopg2.connect(**DB_CREDS) as conn:
        with conn.cursor() as cur:
            cur.execute(TABLE_CREATE_SQL)
        conn.commit()


def insert_data(df: pd.DataFrame) -> None:
    logger.info(f'Inserting data into the table: {SCHEMA_NAME}.{TABLE_NAME}.')
    df = df.copy().replace({np.nan: None})
    records = [row.to_dict() for _, row in df.iterrows()]
    with psycopg2.connect(**DB_CREDS) as conn:
        with conn.cursor() as cur:
            cur.executemany(DATA_INSERT_SQL, records)
        conn.commit()
