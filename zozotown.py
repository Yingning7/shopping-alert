import datetime as dt
import logging

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

from db import PD_DTYPES

logger = logging.getLogger(__file__)


def fetch_html(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url, timeout=0)
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
    for dd in soup.find_all('dd', {'class': 'p-goods-information-spec-horizontal-list__description'}):
        if '（ZOZO）' in dd.text:
            idx = dd.text.find('（ZOZO）')
            item_id = dd.text[:idx].strip()
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
                        'item_id': item_id,
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
    df['platform'] = 'zozotown'
    df['url'] = url
    df['asof'] = dt.datetime.now(tz=dt.timezone.utc)
    df = df.astype(PD_DTYPES)[list(PD_DTYPES.keys())]
    return df

def scrape(url: str) -> pd.DataFrame:
    logger.info(f'Scraping for URL: {url}.')
    html = fetch_html(url)
    data = extract_data(html)
    df = parse_data(data, url)
    return df


if __name__ == '__main__':
    df = scrape('https://zozo.jp/shop/cecilmcbee/goods/92381698/?did=149456227&rid=1006')
    pass
