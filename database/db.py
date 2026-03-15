from pathlib import Path
from typing import Any
import logging
import tomllib

import pandas as pd
import numpy as np
import psycopg

from shopping_platforms._platform import BaseRecord

from . import sql

logger = logging.getLogger(__file__)


class Database:
    def __init__(self) -> None:
        logger.info("Initializing database.")
        self._db_config = self.load_db_config(Path(__file__).parents[1] / "configs/db.toml")
        logger.info("Connecting to database.")
        self.conn = psycopg.connect(**self._db_config)
        self._initialize()

    def load_db_config(self, path: Path) -> dict[str, Any]:
        logger.info("Loading database config.")
        with open(path, mode="rb") as fp:
            return tomllib.load(fp)["postgres"]

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

    def _insert_items(self, df: pd.DataFrame) -> None:
        items_exist = self._query_table(sql.QUERY_ITEMS)
        items_to_upload = df.loc[
            ~(
                df["platform_id"].isin(items_exist["platform_id"])
                & df["item_id"].isin(items_exist["item_id"])
            )
        ][["platform_id", "item_id", "name", "brand", "currency", "url"]].drop_duplicates()
        if not items_to_upload.empty:
            self._run_insert_sql(sql.INSERT_ITEMS, items_to_upload.to_dict(orient="records"))

    def _insert_specs(self, df: pd.DataFrame) -> None:
        specs_exist = self._query_table(sql.QUERY_SPECS)
        merged = pd.merge(df, specs_exist, on=["platform_id", "item_id", "color", "size"], how="left")
        specs_to_upload = merged.loc[merged["specs_id"].isna()][["platform_id", "item_id", "color", "size"]]
        if not specs_to_upload.empty:
            self._run_insert_sql(sql.INSERT_SPECS, specs_to_upload.to_dict(orient="records"))

    def _insert_status(self, df: pd.DataFrame) -> None:
        status_to_upload = df[["specs_id", "original_price", "current_price", "inventory", "in_stock", "asof"]].replace({np.nan: None})
        self._run_insert_sql(sql.INSERT_STATUS, status_to_upload.to_dict(orient="records"))

    def insert_data(self, data: list[BaseRecord]) -> list[int]:
        logger.info("Inserting data.")
        df = pd.DataFrame([record.model_dump() for record in data])
        self._insert_platforms(df)
        platforms_current = self._query_table(sql.QUERY_PLATFORMS)
        df = pd.merge(df, platforms_current, on="platform", how="inner")
        self._insert_items(df)
        self._insert_specs(df)
        specs_current = self._query_table(sql.QUERY_SPECS)
        df = pd.merge(df, specs_current, on=["platform_id", "item_id", "color", "size"], how="inner")
        self._insert_status(df)
        return df["specs_id"].tolist()

    def query_full_status_by_specs_ids(self, specs_ids: list[int]) -> pd.DataFrame:
        logger.info(f"Querying full status for the provided specs_ids.")
        return self._query_table(sql.QUERY_FULL_STATUS_BY_SPECS_IDS.format(specs_ids=", ".join([str(specs_id) for specs_id in specs_ids])))

    def close(self) -> None:
        logger.info("Closing database connection.")
        self.conn.close()
