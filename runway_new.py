from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import requests

URL = 'https://runway-webstore.com/ap/item/i/m/{item_id}'
DTYPES = {
    'item_id': 'str',
    'name': 'str',
    'brand': 'str',
    'original_price': 'float',
    'current_price': 'float',
    'currency': 'str',
    'color': 'str',
    'size': 'str',
    'is_available': 'bool',
    'unit_left': 'float',
    'asof': 'datetime64[ns, UTC]',
    'url': 'str'
}
TABLE_NAME = 'runway'
TABLE_DEF = {
    'item_id': 'TEXT NOT NULL',
    'name': 'TEXT NOT NULL',
    'brand': 'TEXT NOT NULL',
    'original_price': 'DOUBLE PRECISION NOT NULL',
    'current_price': 'DOUBLE PRECISION NOT NULL',
    'currency': 'TEXT NOT NULL',
    'color': 'TEXT NOT NULL',
    'size': 'TEXT NOT NULL',
    'is_available': 'BOOLEAN NOT NULL',
    'unit_left': 'DOUBLE PRECISION',
    'asof': 'TIMESTAMP WITH TIME ZONE NOT NULL',
    'url': 'TEXT NOT NULL',
    'PRIMARY KEY': '(item_id, color, size, asof)'
}
INDEX_DEF = {
    'idx_item_id': 'item_id',
    'idx_color': 'color',
    'idx_size': 'size',
    'idx_asof': 'asof',
    'idx_item_id_asof': 'item_id, asof'
}


def fetch_html(item_id: str) -> str:
    url = URL.format(item_id=item_id)
    resp = requests.get(url)
    if resp.status_code != 200:
        raise RuntimeError(f'Error when fetching HTML from {url} for Item ID: {item_id}.')
    html = resp.text
    return html


def extract_data(html: str) -> list[dict[str, int | float | str]]:
    soup = BeautifulSoup(html, features='html.parser')
    name = soup.find('h1',{'class', 'item_detail_productname'}).text.strip()
    brand = soup.find('p', {'class', 'item_detail_brandname'}).text.strip()
    if soup.find('p', {'class', 'proper'}):
        original_price = soup.find('p', {'class', 'proper'}).text.replace(',', '').replace('円(税込)', '').strip()
        current_price = original_price
    else:
        original_price = soup.find('del').text.replace(',', '').replace('円(税込)', '').strip()
        current_price = soup.find('span', {'class', 'sale_price'}).text.replace(',', '').replace('円(税込)', '').strip()
    currency = 'JPY'
    detail_ul = soup.find('ul', {'class': 'shopping_area_ul_01'})
    color_lis = detail_ul.find_all('li', recursive=False)
    data = []
    for color_li in color_lis:
        color = color_li.div.dl.dd.text.strip()
        spec_lis = color_li.find('div', {'class': 'choose_item'}).find('ul', {'class': 'shopping_area_ul_02'}).find_all('li', recursive=False)
        for spec_li in spec_lis:
            size = spec_li.dt.text.strip()
            status = spec_li.dd.text.strip()
            data.append(
                {
                    'name': name,
                    'brand': brand,
                    'original_price': original_price,
                    'current_price': current_price,
                    'currency': currency,
                    'color': color,
                    'size': size,
                    'status': status
                }
            )
    return data


def parse_data(item_id: str, data: list[dict[str, str]]) -> pd.DataFrame:
    df = pd.DataFrame.from_records(data)
    df['is_available'] = df['status'] != 'SOLD OUT'
    mask = df['status'].str.startswith('残り') & df['status'].str.endswith('点')
    df['unit_left'] = np.where(mask, df['status'].str.replace('点', '').str.replace('残り', ''), np.nan)
    df = df.drop(labels='status', axis=1)
    df['item_id'] = item_id
    df['asof'] = pd.Timestamp.now().tz_localize('Europe/London').tz_convert('UTC')
    df['url'] = URL.format(item_id=item_id)
    df = df.astype(DTYPES)
    return df
