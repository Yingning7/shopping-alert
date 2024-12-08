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
    df = df.replace({np.nan: None})

    # TODO: Add the INSERT INTO table_name (column1, column2, column3) VALUES

    values_sql_list = []
    for _, row in df.replace({np.nan: None}).iterrows():
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
    values_sql = f"{',\n'.join(values_sql_list)};"

    # TODO: use conn and cursor, execute the insertion sql, remember to `conn.commit()` 
    # just like `init_schema` function

    return values_sql  # TODO: remove this return, this is just for debugging the sql string


def query_data(query_sql: str, dtypes: dict[str, str]) -> pd.DataFrame:
    # TODO: use conn and cursor, execute the query_sql and cursor.fetchall(), it will be a list of tuples
    # TODO: convert the list of tuples to a pandas DataFrame, with column name set
    # search online / ask ChatGPT, how to convert a list of tuples to a pandas dataframe
    # and how to get the column names from the psycopg2 after `cursor.fetchall()`
    # TODO: set the data types for all columns of resultant pandas DataFrame, using the `dtypes` provided
    pass
