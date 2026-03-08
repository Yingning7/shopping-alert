from pathlib import Path
import logging

import psycopg

from .utils import load_db_config
from .sql import INITIALIZE_SQL

logger = logging.getLogger(__file__)


class Database:
    def __init__(self):
        logger.info("Initializing database.")
        self.db_config = load_db_config(Path(__file__).parents[1] / "configs/db.toml")
        logger.info("Connecting to database.")
        self.conn = psycopg.connect(**self.db_config)
        self._initialize()

    def _initialize(self):
        logger.info("Initializing schemas and tables.")
        with self.conn.cursor() as cur:
            cur.execute(INITIALIZE_SQL)
        self.conn.commit()

    def close(self):
        logger.info("Closing database connection.")
        self.conn.close()
