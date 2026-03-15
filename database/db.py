from pathlib import Path
from typing import Any
import logging

import pandas as pd
import psycopg

from shopping_platforms._platform import BaseRecord

from .utils import load_db_config
from . import sql

logger = logging.getLogger(__file__)


class Database:
    def __init__(self) -> None:
        logger.info("Initializing database.")
        self.db_config = load_db_config(Path(__file__).parents[1] / "configs/db.toml")
        logger.info("Connecting to database.")
        self.conn = psycopg.connect(**self.db_config)
        self._initialize()

    def _initialize(self) -> None:
        logger.info("Initializing schemas and tables.")
        with self.conn.cursor() as cur:
            cur.execute(sql.INITIALIZE_DB)
        self.conn.commit()

    def _query_table(self, query_sql: str) -> pd.DataFrame:
        with self.conn.cursor() as cur:
            cur.execute(query_sql)
            data = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
        return pd.DataFrame(data, columns=columns)

    def _run_insert_sql(self, insert_sql: str, data: list[dict[str, Any]]) -> None:
        with self.conn.cursor() as cur:
            cur.executemany(insert_sql, data)
        self.conn.commit()

    def _insert_platforms(self, df: pd.DataFrame) -> None:
        platforms_exist = self._query_table(sql.QUERY_PLATFORMS)
        merged = pd.merge(df, platforms_exist, on="platform", how="left")
        platforms_to_upload = merged.loc[merged["platform_id"].isna()][["platform"]].drop_duplicates()
        if not platforms_to_upload.empty:
            self._run_insert_sql(sql.INSERT_PLATFORMS, platforms_to_upload.to_dict(orient="records"))

    def insert_data(self, data: list[BaseRecord]) -> None:
        logger.info("Inserting data.")
        df = pd.DataFrame([record.model_dump() for record in data])
        self._insert_platforms(df)
        platforms_current = self._query_table(sql.QUERY_PLATFORMS)
        df = pd.merge(df, platforms_current, on="platform", how="left")
        pass

    def close(self) -> None:
        logger.info("Closing database connection.")
        self.conn.close()
