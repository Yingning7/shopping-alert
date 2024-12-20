import pandas as pd
import numpy as np
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


def insert_data(table_name: str, table_def: dict[str, str], df: pd.DataFrame) -> None:
    df = df.copy().replace({np.nan: None})
    insert_sql_list = []
    for k in table_def:
        insert_sql_list.append(k)
    insert_sql = f'INSERT INTO {SCHEMA_NAME}.{table_name}(' + f"{',\n'.join(insert_sql_list[:-1])})"
    values_sql_list = []
    for _, row in df.iterrows():
        single_value_sql_list = []
        for col_name, dtype in table_def.items():
            if col_name.startswith('PRIMARY KEY'):
                continue
            elif row[col_name] is None:
                single_value_sql_list.append('NULL')
            elif dtype.startswith(('TEXT', 'TIME', 'DATE')):
                single_value_sql_list.append(f"'{row[col_name]}'")
            elif dtype.startswith('BOOL'):
                single_value_sql_list.append(f"{row[col_name]}".upper())
            else:
                single_value_sql_list.append(str(row[col_name]))
        values_sql_list.append(f"({', '.join(single_value_sql_list)})")
    values_sql = "VALUES" + f"{',\n'.join(values_sql_list)};"
    with psycopg2.connect(**DB_CREDENTIALS) as conn:
        with conn.cursor() as cursor:
            cursor.execute(insert_sql+values_sql)
        conn.commit()


def query_data(query_sql: str, dtypes: dict[str, str]) -> pd.DataFrame:
    with psycopg2.connect(**DB_CREDENTIALS) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query_sql)
            data = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data, columns=column_names).astype(dtypes)
    return df
