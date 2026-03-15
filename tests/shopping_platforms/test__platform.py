import datetime as dt
from shopping_platforms._platform import BaseRecord, BasePlatform
import pytest
from pydantic import ValidationError

def test_base_record_strip_string():
    record = BaseRecord(
        platform="  runway  ",
        item_id=" 123 ",
        name="  Test  ",
        brand=" Brand ",
        currency=" JPY  ",
        color=" red ",
        size=" M ",
        original_price=100.0,
        current_price=80.0,
        inventory=10,
        in_stock=True,
        url="http://example.com  ",
        asof=dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc)
    )
    assert record.platform == "runway"
    assert record.item_id == "123"
    assert record.name == "Test"
    assert record.brand == "Brand"
    assert record.currency == "JPY"
    assert record.color == "red"
    assert record.size == "M"

def test_base_record_validate_url():
    with pytest.raises(ValidationError):
        BaseRecord(
            platform="runway",
            item_id="123",
            name="Test",
            brand="Brand",
            currency="JPY",
            color="red",
            size="M",
            original_price=100.0,
            current_price=80.0,
            inventory=10,
            in_stock=True,
            url="not_a_url",
            asof=dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc)
        )

def test_base_platform_run():
    class DummyPlatform(BasePlatform):
        def acquire(self, *args):
            return "<html></html>"
        
        def extract(self, html):
            return [{"mock": "data"}]
            
        def transform(self, raw_data, asof, *args):
            return [
                BaseRecord(
                    platform="dummy",
                    item_id="1",
                    name="N",
                    brand="B",
                    currency="J",
                    color="C",
                    size="S",
                    original_price=1.0,
                    current_price=1.0,
                    inventory=1,
                    in_stock=True,
                    url="http://example.com",
                    asof=asof
                )
            ]
            
    platform = DummyPlatform()
    results = platform.run("arg1")
    assert len(results) == 1
    assert results[0].platform == "dummy"
