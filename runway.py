from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
import smtplib
import logging

from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import requests

import yaml

from db import SCHEMA_NAME, query_data

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


def scrape(item_id: str) -> pd.DataFrame:
    html = fetch_html(item_id)
    data = extract_data(html)
    df = parse_data(item_id, data)
    return df


def fetch_last(item_id: str) -> pd.DataFrame:
    df_old = query_data(
        f"""
        SELECT
            *
        FROM
            {SCHEMA_NAME}.{TABLE_NAME}
        WHERE
            item_id = '{item_id}'
            AND asof = (SELECT MAX(asof) FROM {SCHEMA_NAME}.{TABLE_NAME} WHERE item_id = '{item_id}')
        """,
        DTYPES
    )
    return df_old


def email(status: str, unit: str) -> None:
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
        </style>
    </head>
    <body>
        <h2>These are the items back in stock:</h2>
        {status}
        <hr>
        <h2>These are the items that the stock is running low:</h2>
        {unit}
    </body>
    </html>
    """
    with open(Path('~/Documents/tokens.yaml').expanduser(), 'r') as fp:
        tokens = yaml.safe_load(fp)
    sender_email = "shenyingningsyn@gmail.com"
    app_password = tokens['gmail']
    receiver_email = "414891445@qq.com"
    subject = "Runway Alert"
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(html_content, "html"))
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        logging.info("Email sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")


def alert(df_new: pd.DataFrame, df_old: pd.DataFrame) -> None:
    joined = df_old.merge(df_new, on=['item_id', 'name', 'brand', 'currency', 'color', 'size', 'url'], how='inner')
    status_change = joined.loc[(joined['is_available_x'] == False) & (joined['is_available_y'] == True)]
    unit_change = joined.loc[joined['unit_left_x'] > joined['unit_left_y']]
    if not (status_change.empty and unit_change.empty):
        logging.info('Sending email.')
        email(status_change.to_html(), unit_change.to_html())
    else:
        logging.info('No changes to alert.')
