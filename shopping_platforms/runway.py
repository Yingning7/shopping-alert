import datetime as dt
import regex as re
import logging

from bs4 import BeautifulSoup
import requests

from ._platform import BaseRecord, BasePlatform

logger = logging.getLogger(__file__)


class RunwayPlatform(BasePlatform):
    _platform = "runway"
    _BASE_URL = "https://runway-webstore.com/ap/item/i/m/{item_id}"

    def _get_full_url(self, item_id: str) -> str:
        full_url = self._BASE_URL.format(item_id=item_id)
        return full_url

    def acquire(self, item_id: str) -> str:
        logger.info(f"Acquiring data for item id: {item_id}.")
        full_url = self._get_full_url(item_id)
        resp = requests.get(full_url)
        html = resp.text
        return html

    def extract(self, html: str) -> list[dict[str, str]]:
        logger.info("Extracting data.")
        soup = BeautifulSoup(html, features="html.parser")
        name = soup.find("h1", {"class", "item_detail_productname"}).text
        brand = soup.find("p", {"class", "item_detail_brandname"}).text
        if soup.find("p", {"class", "proper"}):
            original_price = soup.find("p", {"class", "proper"}).text.replace(",", "").replace("円(税込)", "")
            current_price = original_price
        else:
            original_price = soup.find("del").text.replace(",", "").replace("円(税込)", "")
            current_price = soup.find("span", {"class", "sale_price"}).text.replace(",", "").replace("円(税込)", "")
        detail_ul = soup.find("ul", {"class": "shopping_area_ul_01"})
        color_lis = detail_ul.find_all("li", recursive=False)
        raw_data = []
        for color_li in color_lis:
            color = color_li.div.dl.dd.text
            spec_lis = color_li.find("div", {"class": "choose_item"}).find("ul", {"class": "shopping_area_ul_02"}).find_all("li", recursive=False)
            for spec_li in spec_lis:
                size = spec_li.dt.text
                status = spec_li.dd.text
                raw_data.append(
                    {
                        "name": name,
                        "brand": brand,
                        "currency": "JPY",
                        "color": color,
                        "size": size,
                        "original_price": original_price,
                        "current_price": current_price,
                        "status": status
                    }
                )
        return raw_data

    def transform(self, raw_data: list[dict[str, str]], asof: dt.datetime, item_id: str) -> list[BaseRecord]:
        logger.info("Transforming data.")
        transformed_data = []
        for raw_record in raw_data:
            in_stock = raw_record["status"].strip() != "SOLD OUT"
            match_result = re.fullmatch(r"^残り(\d+)点$", raw_record["status"].strip())
            if match_result is not None:
                inventory = match_result.group(1)
            else:
                inventory = None
            transformed_data.append(
                BaseRecord(
                    platform=self._platform,
                    item_id=item_id,
                    url=self._get_full_url(item_id),
                    asof=asof,
                    in_stock=in_stock,
                    inventory=inventory,
                    **raw_record
                )
            )
        return transformed_data
