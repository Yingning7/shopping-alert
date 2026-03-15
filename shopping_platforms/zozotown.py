import datetime as dt
import regex as re
import logging

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

from ._platform import BaseRecord, BasePlatform

logger = logging.getLogger(__file__)


class ZozotownPlatform(BasePlatform):
    _platform = "zozotown"

    def acquire(self, url: str) -> str:
        logger.info(f"Acquiring data for url: {url}.")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=0)
            html = page.content()
            browser.close()
        return html

    def extract(self, html: str) -> list[dict[str, str]]:
        logger.info("Extracting data.")
        soup = BeautifulSoup(html, features="html.parser")
        brand = soup.find("div", {"class": "p-goods-information-brand-link__label"}).text
        name = soup.find("h1", {"class":"p-goods-information__heading"}).text
        if soup.find("div", {"class":"p-goods-information__price"}):
            original_price = soup.find("div", {"class":"p-goods-information__price"}).text.replace("¥", "").replace("税込", "").replace(",", "")
            current_price = original_price
        else:
            original_price = soup.find("span", {"class": "u-text-style-strike"}).text.replace("¥", "").replace(",", "")
            current_price = soup.find("div", {"class": "p-goods-information__price--discount"}).text.replace("¥", "").replace("税込", "").replace(",", "")
        color_dls = soup.find_all("dl", {"class": "p-goods-information-action"})
        for dd in soup.find_all("dd", {"class": "p-goods-information-spec-horizontal-list__description"}):
            if "（ZOZO）" in dd.text:
                idx = dd.text.find("（ZOZO）")
                item_id = dd.text[:idx]
                break
        raw_data = []
        for color_dl in color_dls:
            color = color_dl.find("span", {"class": "txt p-goods-add-cart__color"}).text
            spec_lis = color_dl.find_all("li")
            for spec_li in spec_lis:
                text = spec_li.find("p",{"class": "p-goods-add-cart-stock"}).text
                parts = text.split("\xa0/\xa0")
                size = parts[0]
                status = parts[1]
                raw_data.append(
                        {
                            "item_id": item_id,
                            "name": name,
                            "brand": brand,
                            "original_price": original_price,
                            "current_price": current_price,
                            "currency": "JPY",
                            "color": color,
                            "size": size,
                            "status": status
                        }
                    )
        return raw_data

    def transform(self, raw_data: list[dict[str, str]], asof: dt.datetime, url: str) -> list[BaseRecord]:
        logger.info("Transforming data.")
        transformed_data = []
        for raw_record in raw_data:
            in_stock = raw_record["status"].strip() != "在庫なし"
            match_result = re.fullmatch(r"^残り(\d+)点$", raw_record["status"].strip())
            if match_result is not None:
                inventory = match_result.group(1)
            else:
                inventory = None
            transformed_data.append(
                BaseRecord(
                    platform=self._platform,
                    url=url,
                    asof=asof,
                    in_stock=in_stock,
                    inventory=inventory,
                    **raw_record
                )
            )
        return transformed_data
