from abc import ABC, abstractmethod
from typing import Any

import pandas as pd


class BaseScraper(ABC):
    URL = ...

    @abstractmethod
    def __init__(self, *arg: Any, **kwargs: Any) -> None:
        pass

    @abstractmethod
    def scrape(self) -> pd.DataFrame:
        pass
