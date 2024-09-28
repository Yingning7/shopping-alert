import datetime as dt

from pydantic import BaseModel
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import requests

from .base import BaseScraper


class RawSpecInfo(BaseModel):
    size: str
    status: str


class ItemInfo(BaseModel):
    inventory_id: str
    color: str
    size: str
    is_available: bool
    amount: int | None
    timestamp: dt.datetime


class RunwayScraper(BaseScraper):
    URL = 'https://runway-webstore.com/ap/item/i/m/{inventory_id}'

    def __init__(self, inventory_id: str) -> None:
        self.inventory_id = inventory_id
        self.url = self.URL.format(inventory_id=inventory_id)

    def _fetch_html(self) -> str:
        resp = requests.get(self.url)
        html = resp.text
        return html
    
    @staticmethod
    def _process_html(html: str) -> dict[str, list[RawSpecInfo]]:
        soup = BeautifulSoup(html, features='html.parser')
        shopping_area = soup.find('ul', {'class': 'shopping_area_ul_01'})
        raw = {}
        color_lis = shopping_area.find_all('li', recursive=False)
        for color_li in color_lis:
            color = color_li.div.dl.dd.text.strip()
            raw[color] = []
            spec_lis = color_li.find('div', {'class': 'choose_item'}).find('ul', {'class': 'shopping_area_ul_02'}).find_all('li', recursive=False)
            for spec_li in spec_lis:
                size = spec_li.dt.text.strip()
                status = spec_li.dd.text.strip()
                raw[color].append(RawSpecInfo(size=size, status=status))
        return raw
    
    def _parse_to_dataframe(self, raw: dict[str, list[RawSpecInfo]], timestamp: dt.datetime) -> pd.DataFrame:
        item_infos = []
        for color, raw_spec_infos in raw.items():
            for raw_spec_info in raw_spec_infos:
                item_info = {}
                item_info['inventory_id'] = self.inventory_id
                item_info['color'] = color
                item_info['size'] = raw_spec_info.size
                item_info['is_available'] = raw_spec_info.status != 'SOLD OUT'
                if raw_spec_info.status.startswith('残り') and raw_spec_info.status.endswith('点'):
                    item_info['amount'] = int(raw_spec_info.status.replace('点', '').replace('残り', ''))
                else:
                    item_info['amount'] = None
                item_info['timestamp'] = timestamp
                item_infos.append(ItemInfo(**item_info))
        inventory = pd.DataFrame.from_records([x.dict() for x in item_infos])
        inventory['amount'] = inventory['amount'].replace({None: np.nan})
        inventory = inventory.astype(
            {
                'inventory_id': 'str',
                'color': 'str',
                'size': 'str',
                'is_available': 'bool',
                'amount': 'float',
                'timestamp': 'datetime64[ns]'
            }
        )
        return inventory

    def scrape(self) -> pd.DataFrame:
        timestamp = dt.datetime.now()
        html = self._fetch_html()
        raw = self._process_html(html)
        inventory = self._parse_to_dataframe(raw, timestamp)
        return inventory
