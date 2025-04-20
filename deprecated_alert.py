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
