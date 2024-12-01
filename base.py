from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel
import pandas as pd


class BaseScraper(ABC):
    URL = ...

    @abstractmethod
    def __init__(self, *arg: Any, **kwargs: Any) -> None:
        pass

    @abstractmethod
    def scrape(self) -> pd.DataFrame:
        pass


class BaseRecord(BaseModel):
    @classmethod
    def get_df_dtypes(cls) -> dict[str, str]:
        pass

    @classmethod
    def get_db_table_dtypes(cls) -> dict[str, str]:
        pass

    @classmethod
    def get_db_index(cls) -> dict[str, str]:
        pass
