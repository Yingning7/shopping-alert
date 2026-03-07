from abc import ABC, abstractmethod
from typing import Any
import datetime as dt

from pydantic import BaseModel, model_validator, HttpUrl


class BaseRecord(BaseModel):
    item_id: str
    name: str
    brand: str
    currency: str
    color: str
    size: str
    original_price: int
    current_price: int
    inventory: int | None
    in_stock: bool
    url: HttpUrl
    asof: dt.datetime
    
    @model_validator(mode="before")
    @classmethod
    def strip_string(cls, record: dict[str, Any]) -> dict[str, Any]:
        for k, v in record.items():
            if isinstance(v, str):
                record[k] = v.strip()
        return record


class BasePlatform(ABC):
    @abstractmethod
    def acquire(self, *args) -> str:
        pass

    @abstractmethod
    def extract(self, html: str) -> list[dict[str, str]]:
        pass

    @abstractmethod
    def transform(self, raw_data: list[dict[str, str]], asof: dt.datetime, *args) -> list[BaseRecord]:
        pass

    def run(self, *args) -> list[BaseRecord]:
        asof = dt.datetime.utcnow()
        html = self.acquire(*args)
        raw_data = self.extract(html)
        transformed_data = self.transform(raw_data, asof, *args)
        return transformed_data
