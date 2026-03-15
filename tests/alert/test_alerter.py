import pytest
import pandas as pd
import numpy as np
import datetime as dt
from unittest.mock import patch, MagicMock

from alert.alerter import Alerter

@pytest.fixture
def mock_alerter():
    with patch.object(Alerter, 'load_email_config', return_value={
        "smtp_server": "smtp.test", 
        "smtp_port": 465,
        "email_address": "test@test.com",
        "app_password": "pass"
    }):
        return Alerter()


def test_groupby_detect_less_than_two_rows(mock_alerter):
    df = pd.DataFrame([{"status_id": 1}])
    result = mock_alerter._groupby_detect(df)
    assert result is None


def test_groupby_detect_no_change(mock_alerter):
    df = pd.DataFrame([
        {
            "status_id": 1, "platform": "runway", "name": "Item", "brand": "Brand",
            "currency": "JPY", "url": "url", "color": "red", "size": "M",
            "current_price": 1000, "inventory": 10, "in_stock": True,
            "asof": pd.Timestamp("2023-01-01")
        },
        {
            "status_id": 2, "platform": "runway", "name": "Item", "brand": "Brand",
            "currency": "JPY", "url": "url", "color": "red", "size": "M",
            "current_price": 1000, "inventory": 10, "in_stock": True,
            "asof": pd.Timestamp("2023-01-02")
        }
    ])
    result = mock_alerter._groupby_detect(df)
    assert result is None


def test_groupby_detect_price_drop(mock_alerter):
    df = pd.DataFrame([
        {
            "status_id": 1, "platform": "runway", "name": "Item", "brand": "Brand",
            "currency": "JPY", "url": "url", "color": "red", "size": "M",
            "current_price": 1000, "inventory": 10, "in_stock": True,
            "asof": pd.Timestamp("2023-01-01")
        },
        {
            "status_id": 2, "platform": "runway", "name": "Item", "brand": "Brand",
            "currency": "JPY", "url": "url", "color": "red", "size": "M",
            "current_price": 800, "inventory": 10, "in_stock": True,
            "asof": pd.Timestamp("2023-01-02")
        }
    ])
    result = mock_alerter._groupby_detect(df)
    assert result is not None
    assert result["previous_price"] == 1000
    assert result["new_price"] == 800


def test_groupby_detect_nan_inventory_change(mock_alerter):
    df = pd.DataFrame([
        {
            "status_id": 1, "platform": "runway", "name": "Item", "brand": "Brand",
            "currency": "JPY", "url": "url", "color": "red", "size": "M",
            "current_price": 1000, "inventory": 10, "in_stock": True,
            "asof": pd.Timestamp("2023-01-01")
        },
        {
            "status_id": 2, "platform": "runway", "name": "Item", "brand": "Brand",
            "currency": "JPY", "url": "url", "color": "red", "size": "M",
            "current_price": 1000, "inventory": np.nan, "in_stock": True,
            "asof": pd.Timestamp("2023-01-02")
        }
    ])
    result = mock_alerter._groupby_detect(df)
    assert result is not None
    assert result["previous_inventory"] == 10
    assert pd.isna(result["new_inventory"])


@patch("alert.alerter.smtplib.SMTP_SSL")
def test_send_alert_email(mock_smtp_cls, mock_alerter):
    mock_smtp_instance = MagicMock()
    mock_smtp_cls.return_value.__enter__.return_value = mock_smtp_instance

    full_status_df = pd.DataFrame([
        {
            "specs_id": 1, "status_id": 1, "platform": "runway", "name": "Item", 
            "brand": "Brand", "currency": "JPY", "url": "url", "color": "red", 
            "size": "M", "current_price": 1000, "inventory": 10, "in_stock": True,
            "asof": pd.Timestamp("2023-01-01")
        },
        {
            "specs_id": 1, "status_id": 2, "platform": "runway", "name": "Item", 
            "brand": "Brand", "currency": "JPY", "url": "url", "color": "red", 
            "size": "M", "current_price": 800, "inventory": 10, "in_stock": True,
            "asof": pd.Timestamp("2023-01-02")
        }
    ])

    mock_alerter.send_alert_email(full_status_df)
    
    # Needs to log in and send message
    mock_smtp_instance.login.assert_called_once_with("test@test.com", "pass")
    mock_smtp_instance.send_message.assert_called_once()
