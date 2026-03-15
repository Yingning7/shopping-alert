from pathlib import Path
from email.message import EmailMessage
import smtplib
from typing import Any
import logging
import tomllib

import pandas as pd
import numpy as np

logger = logging.getLogger(__file__)


class Alerter:
    def __init__(self):
        logger.info("Initializing alerter.")
        self._email_config = self.load_email_config(Path(__file__).parents[1] / "configs/email.toml")

    def load_email_config(self, path: Path) -> dict[str, Any]:
        logger.info("Loading email config.")
        with open(path, mode="rb") as fp:
            return tomllib.load(fp)["gmail"]

    def _groupby_detect(self, df: pd.DataFrame) -> pd.Series | None:
        if len(df.index) < 2:
            return None
        df = df.sort_values("status_id").tail(2)
        inv_0 = df.iloc[0]["inventory"]
        inv_1 = df.iloc[1]["inventory"]
        inventory_changed = False
        if np.isnan(inv_0) and not np.isnan(inv_1):
            inventory_changed = True
        elif not np.isnan(inv_0) and np.isnan(inv_1):
            inventory_changed = True
        elif not np.isnan(inv_0) and not np.isnan(inv_1):
            inventory_changed = not np.isclose(inv_0, inv_1)
        if (
            (not np.isclose(df.iloc[0]["current_price"], df.iloc[1]["current_price"]))
            or inventory_changed
            or (df.iloc[0]["in_stock"] != df.iloc[1]["in_stock"])
        ):
            data = {
                "platform": df.iloc[0]["platform"],
                "name": df.iloc[0]["name"],
                "brand": df.iloc[0]["brand"],
                "currency": df.iloc[0]["currency"],
                "url": df.iloc[0]["url"],
                "color": df.iloc[0]["color"],
                "size": df.iloc[0]["size"],
                "previous_price": df.iloc[0]["current_price"],
                "new_price": df.iloc[1]["current_price"],
                "previous_inventory": df.iloc[0]["inventory"],
                "new_inventory": df.iloc[1]["inventory"],
                "previous_in_stock": df.iloc[0]["in_stock"],
                "new_in_stock": df.iloc[1]["in_stock"],
                "previous_asof": df.iloc[0]["asof"],
                "new_asof": df.iloc[1]["asof"]
            }
            return pd.Series(data)
        return None

    def send_alert_email(self, full_status_df: pd.DataFrame) -> None:
        logger.info("Sending alert email.")
        detected_df = full_status_df.groupby("specs_id").apply(self._groupby_detect).dropna(how="all")
        if detected_df.empty:
            logger.info("No price drops or inventory changes detected. Skipping email.")
        else:
            msg = EmailMessage()
            msg["Subject"] = "Shopping Alert: Price Drops or Inventory Changes Detected"
            msg["From"] = self._email_config["email_address"]
            msg["To"] = self._email_config["email_address"]
            msg.set_content(detected_df.reset_index(drop=True).to_html(index=False), subtype="html")
            with smtplib.SMTP_SSL(self._email_config["smtp_server"], self._email_config["smtp_port"]) as smtp:
                smtp.login(self._email_config["email_address"], self._email_config["app_password"])
                smtp.send_message(msg)
