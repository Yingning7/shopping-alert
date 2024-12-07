import psycopg2

SCHEMA_NAME = 'shopping_alert'
DB_CREDENTIALS = {
    'dbname': 'shopping-alert-pg-db',
    'user': 'admin',
    'password': 'admin',
    'host': 'localhost',
    'port': 5432
}

def init_schema() -> None:
    with psycopg2.connect(**DB_CREDENTIALS) as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}")
        conn.commit()

def check_table_exists(table_name: str) -> bool:
    with psycopg2.connect(**DB_CREDENTIALS) as conn:
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
            return cursor.fetchall()[0][0]


def create_table(table_name: str, table_def: dict[str, str], index_def: dict[str, str]) -> None:
    table_dict = table_def
    content_lst = []
    for i in table_dict.items():
        content = i[0] +' ' + i[1]
        content_lst.append(content)
    query = f'CREATE TABLE {SCHEMA_NAME}.{table_name}('
    for content in content_lst:
        query += content + ', '
    query_final = query[:-2] + ');'
    index_dict = index_def
    index_query = ''
    for i in index_dict.items():
        index_query += f'CREATE INDEX {i[0]} ON {SCHEMA_NAME}.{table_name}({i[1]});'
    with psycopg2.connect(**DB_CREDENTIALS) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query_final + index_query)
        conn.commit()
