import pytest
import datetime as dt
from unittest.mock import patch, MagicMock
from shopping_platforms.zozotown import ZozotownPlatform

@patch("shopping_platforms.zozotown.sync_playwright")
def test_zozotown_acquire(mock_playwright):
    mock_p = MagicMock()
    mock_browser = MagicMock()
    mock_page = MagicMock()
    
    mock_playwright.return_value.__enter__.return_value = mock_p
    mock_p.chromium.launch.return_value = mock_browser
    mock_browser.new_page.return_value = mock_page
    mock_page.content.return_value = "<html></html>"
    
    platform = ZozotownPlatform()
    html = platform.acquire("http://example.com")
    
    mock_p.chromium.launch.assert_called_once_with(headless=True)
    mock_browser.new_page.assert_called_once()
    mock_page.goto.assert_called_once_with("http://example.com", timeout=0)
    mock_browser.close.assert_called_once()
    assert html == "<html></html>"

def test_zozotown_extract():
    html = """
    <html>
        <body>
            <div class="p-goods-information-brand-link__label">Test Brand</div>
            <h1 class="p-goods-information__heading">Test Item</h1>
            <div class="p-goods-information__price">1,000¥税込</div>
            <dd class="p-goods-information-spec-horizontal-list__description">12345（ZOZO）</dd>
            <dl class="p-goods-information-action">
                <span class="txt p-goods-add-cart__color">Red</span>
                <li>
                    <p class="p-goods-add-cart-stock">M\xa0/\xa0在庫なし</p>
                </li>
                <li>
                    <p class="p-goods-add-cart-stock">L\xa0/\xa0残り3点</p>
                </li>
            </dl>
        </body>
    </html>
    """
    platform = ZozotownPlatform()
    data = platform.extract(html)
    assert len(data) == 2
    assert data[0]["item_id"] == "12345"
    assert data[0]["name"] == "Test Item"
    assert data[0]["brand"] == "Test Brand"
    assert data[0]["original_price"] == "1000"
    assert data[0]["current_price"] == "1000"
    assert data[0]["color"] == "Red"
    assert data[0]["size"] == "M"
    assert data[0]["status"] == "在庫なし"

def test_zozotown_transform():
    platform = ZozotownPlatform()
    raw_data = [
        {
            "item_id": "12345", "name": "Test", "brand": "Brand", "currency": "JPY", 
            "color": "Red", "size": "M", "original_price": "1000", 
            "current_price": "1000", "status": "在庫なし"
        },
        {
            "item_id": "12345", "name": "Test", "brand": "Brand", "currency": "JPY", 
            "color": "Red", "size": "L", "original_price": "1000", 
            "current_price": "1000", "status": "残り3点"
        }
    ]
    asof = dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc)
    transformed = platform.transform(raw_data, asof, "http://example.com")
    
    assert len(transformed) == 2
    assert transformed[0].in_stock is False
    assert transformed[0].inventory is None
    
    assert transformed[1].in_stock is True
    assert transformed[1].inventory == 3
    assert str(transformed[1].url) == "http://example.com/"
