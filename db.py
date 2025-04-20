import logging
import psycopg2

logger = logging.getLogger(__file__)

SCHEMA_NAME = 'shopping_alert'
DB_CREDS = {
    'dbname': 'shopping-alert-db',
    'user': 'admin',
    'password': 'admin',
    'host': 'localhost',
    'port': 5432
}


def init_schema() -> None:
    logger.info(f'Creating schema {SCHEMA_NAME} if it does not exist.')
    with psycopg2.connect(**DB_CREDS) as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}")
        conn.commit()


def check_table_exists(table_name: str) -> bool:
    logger.info(f'Checking if the table {SCHEMA_NAME}.{table_name} exists or not.')
    with psycopg2.connect(**DB_CREDS) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT EXISTS (
                    SELECT 1
                    FROM pg_tables
                    WHERE schemaname = '{SCHEMA_NAME}' AND tablename = '{table_name}'
                )
                """
            )
            table_is_exists = cursor.fetchall()[0][0]
    logger.info(f'The table {SCHEMA_NAME}.{table_name} existence: {table_is_exists}.')
    return table_is_exists
