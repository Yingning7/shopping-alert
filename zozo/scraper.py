import logging

import requests

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

logger = logging.getLogger(__file__)

URL = 'https://zozo.jp/shop/mercuryduo/goods-sale/87837454/?did=142436883&rid=1006'
DTYPES = {
    #'item_id': 'str',
    'name': 'str',
    'brand': 'str',
    'original_price': 'float',
    'current_price': 'float',
    'currency': 'str',
    'color': 'str',
    'size': 'str',
    'is_available': 'bool',
    'unit_left': 'float',
    'url': 'str',
    'asof': 'datetime64[ns, UTC]'
}


def fetch_html(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
        html = page.content()
        browser.close()
    return html


def extract_data(html: str) -> list[dict[str, str]]:
    logger.info('Extracting data.')
    soup = BeautifulSoup(html, features='html.parser')
    brand = soup.find('div', {'class': 'p-goods-information-brand-link__label'}).text.strip()
    name = soup.find('h1', {'class':'p-goods-information__heading'}).text.strip()
    if soup.find('div', {'class':'p-goods-information__price'}):
        original_price = soup.find('div', {'class':'p-goods-information__price'}).text.replace('¥', '').replace('税込', '').replace(',', '').strip()
        current_price = original_price
    else:
        original_price = soup.find('span', {'class': 'u-text-style-strike'}).text.replace('¥', '').replace(',', '').strip()
        current_price = soup.find('div', {'class': 'p-goods-information__price--discount'}).text.replace('¥', '').replace('税込', '').replace(',', '').strip()
    currency = 'JPY'
    color_dls = soup.find_all('dl', {'class': 'p-goods-information-action'})
    data = []
    for color_dl in color_dls:
        color = color_dl.find('span', {'class': 'txt p-goods-add-cart__color'}).text.strip()
        spec_lis = color_dl.find_all('li')
        for spec_li in spec_lis:
            text = spec_li.find('p',{'class': 'p-goods-add-cart-stock'}).text.strip()
            parts = text.split('\xa0/\xa0')
            size = parts[0]
            status = parts[1]
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


def parse_data(data: list[dict[str, str]], url: str) -> pd.DataFrame:
    logger.info('Parsing data.')
    df = pd.DataFrame.from_records(data)
    df['is_available'] = df['status'] != '在庫なし'
    mask = df['status'].str.startswith('残り') & df['status'].str.endswith('点')
    df['unit_left'] = np.where(mask, df['status'].str.replace('点', '').str.replace('残り', ''), np.nan)
    df = df.drop(labels='status', axis=1)
    #df['item_id'] = item_id
    df['url'] = url
    df['asof'] = pd.Timestamp.now().tz_localize('Europe/London').tz_convert('UTC')
    df = df.astype(DTYPES)[list(DTYPES.keys())]
    return df

def scrape(url: str) -> pd.DataFrame:
    logger.info(f'Scraping for URL: {url}.')
    html = fetch_html(url)
    data = extract_data(html)
    df = parse_data(data, url)
    print(df)

scrape(URL)