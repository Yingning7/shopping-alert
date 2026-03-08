from typing import Any
import logging

from pathlib import Path
import tomllib

logger = logging.getLogger(__file__)


def load_db_config(path: Path) -> dict[str, Any]:
    logger.info("Loading database config.")
    with open(path, mode="rb") as fp:
        return tomllib.load(fp)["postgres"]
