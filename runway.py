import datetime as dt
import logging

from pydantic import BaseModel
from bs4 import BeautifulSoup
import pandas as pd
import requests
import pytz

from base import BaseRecord, BaseScraper


class Price(BaseModel):
    original: float
    current: float
    currency: str


class Spec(BaseModel):
    size: str
    status: str

    @property
    def is_available(self) -> bool:
        return self.status != 'SOLD OUT'
    
    @property
    def unit_left(self) -> float:
        if self.status.startswith('残り') and self.status.endswith('点'):
            return float(self.status.replace('点', '').replace('残り', ''))
        return float('NaN')


class Detail(BaseModel):
    color: str
    specs: list[Spec]


class ItemInfo(BaseModel):
    name: str
    brand: str
    price: Price
    details: list[Detail]


class Record(BaseRecord):
    item_id: str
    name: str
    brand: str
    price_original: float
    price_current: float
    price_currency: str
    color: str
    size: str
    is_available: bool
    unit_left: float
    asof: dt.datetime
    url: str

    @classmethod
    def get_df_dtypes(cls) -> dict[str, str]:
        return {
            'item_id': 'str',
            'name': 'str',
            'brand': 'str',
            'price_original': 'float',
            'price_current': 'float',
            'price_currency': 'str',
            'color': 'str',
            'size': 'str',
            'is_available': 'bool',
            'unit_left': 'float',
            'asof': 'datetime64[ns, UTC]',
            'url': 'str'
        }


class Scraper(BaseScraper):
    URL = 'https://runway-webstore.com/ap/item/i/m/{item_id}'

    def __init__(self, item_id: str) -> None:
        self.item_id = item_id
        self.url = self.URL.format(item_id=item_id)

    def _fetch_html(self) -> str:
        logging.info(f'Fetching HTML from {self.url}.')
        resp = requests.get(self.url)
        if resp.status_code != 200:
            raise RuntimeError(f'Error when fetching HTML from {self.url} for Item ID: {self.item_id}.')
        html = resp.text
        return html
    
    @staticmethod
    def _extract_item_info(html: str) -> ItemInfo:
        logging.info('Extracting item information from HTML.')
        soup = BeautifulSoup(html, features='html.parser')
        name = soup.find('h1',{'class', 'item_detail_productname'}).text.strip()
        brand = soup.find('p', {'class', 'item_detail_brandname'}).text.strip()
        if soup.find('p', {'class', 'proper'}):
            original = soup.find('p', {'class', 'proper'}).text.replace(',', '').replace('円(税込)', '').strip()
            current = original
        else:
            original = soup.find('del').text.replace(',', '').replace('円(税込)', '').strip()
            current = soup.find('span', {'class', 'sale_price'}).text.replace(',', '').replace('円(税込)', '').strip()
        price = Price(original=float(original), current=float(current), currency='JPY')
        detail_ul = soup.find('ul', {'class': 'shopping_area_ul_01'})
        color_lis = detail_ul.find_all('li', recursive=False)
        details = []
        for color_li in color_lis:
            color = color_li.div.dl.dd.text.strip()
            specs = []
            spec_lis = color_li.find('div', {'class': 'choose_item'}).find('ul', {'class': 'shopping_area_ul_02'}).find_all('li', recursive=False)
            for spec_li in spec_lis:
                size = spec_li.dt.text.strip()
                status = spec_li.dd.text.strip()
                specs.append(Spec(size=size, status=status))
            details.append(Detail(color=color, specs=specs))
        item_info = ItemInfo(
            name=name,
            brand=brand,
            price=price,
            details=details
        )
        return item_info
    
    def _parse_item_info(self, item_info: ItemInfo, asof: dt.datetime) -> pd.DataFrame:
        logging.info('Parsing item information to DataFrame.')
        records = []
        for detail in item_info.details:
            for spec in detail.specs:
                records.append(
                    Record(
                        item_id=self.item_id,
                        name=item_info.name,
                        brand=item_info.brand,
                        price_original=item_info.price.original,
                        price_current=item_info.price.current,
                        price_currency=item_info.price.currency,
                        color=detail.color,
                        size=spec.size,
                        is_available=spec.is_available,
                        unit_left=spec.unit_left,
                        asof=asof,
                        url=self.url
                    )
                )
        data = pd.DataFrame.from_records([record.dict() for record in records]).astype(Record.get_df_dtypes())
        return data

    def scrape(self) -> pd.DataFrame:
        asof = pytz.timezone('Europe/London').localize(dt.datetime.now()).astimezone(pytz.UTC)
        logging.info(f'Scraping at {asof} for Item ID: {self.item_id}.')
        html = self._fetch_html()
        item_info = self._extract_item_info(html)
        data = self._parse_item_info(item_info, asof)
        return data
