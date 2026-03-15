import pytest
import datetime as dt
from unittest.mock import patch, MagicMock
from shopping_platforms.runway import RunwayPlatform

def test_runway_get_full_url():
    platform = RunwayPlatform()
    url = platform._get_full_url("123")
    assert url == "https://runway-webstore.com/ap/item/i/m/123"

@patch("shopping_platforms.runway.requests.get")
def test_runway_acquire(mock_get):
    mock_resp = MagicMock()
    mock_resp.text = "<html></html>"
    mock_get.return_value = mock_resp
    
    platform = RunwayPlatform()
    html = platform.acquire("123")
    
    mock_get.assert_called_once_with("https://runway-webstore.com/ap/item/i/m/123")
    assert html == "<html></html>"

def test_runway_extract():
    html = """
    <html>
        <body>
            <h1 class="item_detail_productname">Test Item</h1>
            <p class="item_detail_brandname">Test Brand</p>
            <p class="proper">1,000円(税込)</p>
            <ul class="shopping_area_ul_01">
                <li>
                    <div><dl><dd>Red</dd></dl></div>
                    <div class="choose_item">
                        <ul class="shopping_area_ul_02">
                            <li>
                                <dt>M</dt>
                                <dd>SOLD OUT</dd>
                            </li>
                            <li>
                                <dt>L</dt>
                                <dd>残り5点</dd>
                            </li>
                        </ul>
                    </div>
                </li>
            </ul>
        </body>
    </html>
    """
    platform = RunwayPlatform()
    data = platform.extract(html)
    assert len(data) == 2
    assert data[0]["name"] == "Test Item"
    assert data[0]["original_price"] == "1000"
    assert data[0]["current_price"] == "1000"
    assert data[0]["color"] == "Red"
    assert data[0]["size"] == "M"
    assert data[0]["status"] == "SOLD OUT"

    assert data[1]["size"] == "L"
    assert data[1]["status"] == "残り5点"

def test_runway_transform():
    platform = RunwayPlatform()
    raw_data = [
        {
            "name": "Test", "brand": "Brand", "currency": "JPY", 
            "color": "Red", "size": "M", "original_price": "1000", 
            "current_price": "1000", "status": "SOLD OUT"
        },
        {
            "name": "Test", "brand": "Brand", "currency": "JPY", 
            "color": "Red", "size": "L", "original_price": "1000", 
            "current_price": "1000", "status": "残り5点"
        }
    ]
    asof = dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc)
    transformed = platform.transform(raw_data, asof, "123")
    
    assert len(transformed) == 2
    assert transformed[0].in_stock is False
    assert transformed[0].inventory is None
    
    assert transformed[1].in_stock is True
    assert transformed[1].inventory == 5
    assert transformed[1].item_id == "123"
    assert str(transformed[1].url) == "https://runway-webstore.com/ap/item/i/m/123"
