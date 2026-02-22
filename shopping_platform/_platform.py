from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, model_validator


class BaseRecord(BaseModel):
    name: str
    brand: str
    currency: str
    colour: str
    size: str
    in_stock: bool

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
    def transform(self, raw_data: list[dict[str, str]]) -> list[BaseRecord]:
        pass

    def run(self, *args) -> list[BaseRecord]:
        html = self.acquire(*args)
        raw_data = self.extract(html)
        transformed_data = self.transform(raw_data)
        return transformed_data
