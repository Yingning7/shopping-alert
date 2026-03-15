import pytest
import datetime as dt
import pandas as pd
from unittest.mock import patch, MagicMock

from database.db import Database
from shopping_platforms._platform import BaseRecord

@patch("database.db.load_db_config")
@patch("psycopg.connect")
def test_database_init(mock_connect, mock_load_config):
    mock_load_config.return_value = {"host": "localhost"}
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    db = Database()

    mock_load_config.assert_called_once()
    mock_connect.assert_called_once_with(host="localhost")
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()


@patch("database.db.load_db_config")
@patch("psycopg.connect")
def test_query_table(mock_connect, mock_load_config):
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    
    mock_cursor.fetchall.return_value = [(1, "runway")]
    mock_cursor.description = [("platform_id", None, None, None, None, None, None), 
                               ("platform", None, None, None, None, None, None)]

    db = Database()
    df = db._query_table("SELECT * FROM test")

    mock_cursor.execute.assert_called_with("SELECT * FROM test")
    assert isinstance(df, pd.DataFrame)
    assert df.to_dict(orient="records") == [{"platform_id": 1, "platform": "runway"}]


@patch("database.db.load_db_config")
@patch("psycopg.connect")
def test_run_insert_sql(mock_connect, mock_load_config):
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    db = Database()
    db._run_insert_sql("INSERT INTO test VALUES(%(val)s)", [{"val": 1}])

    mock_cursor.executemany.assert_called_once_with("INSERT INTO test VALUES(%(val)s)", [{"val": 1}])


@patch.object(Database, "_run_insert_sql")
@patch.object(Database, "_query_table")
@patch("database.db.load_db_config")
@patch("psycopg.connect")
def test_insert_data_all_new(mock_connect, mock_load_config, mock_query, mock_insert):
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn

    db = Database()

    query_returns = [
        pd.DataFrame(columns=["platform_id", "platform"]), 
        pd.DataFrame([{"platform_id": 1, "platform": "runway"}]), 
        pd.DataFrame(columns=["platform_id", "item_id"]), 
        pd.DataFrame(columns=["specs_id", "platform_id", "item_id", "color", "size"]), 
        pd.DataFrame([{"specs_id": 1, "platform_id": 1, "item_id": "123", "color": "red", "size": "M"}]) 
    ]
    mock_query.side_effect = query_returns

    record = BaseRecord(
        platform="runway",
        item_id="123",
        name="Test Item",
        brand="Test Brand",
        currency="JPY",
        color="red",
        size="M",
        original_price=1000.0,
        current_price=800.0,
        inventory=10,
        in_stock=True,
        url="http://example.com/123",
        asof=dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc)
    )

    db.insert_data([record])

    assert mock_query.call_count == 5
    assert mock_insert.call_count == 4


@patch("database.db.load_db_config")
@patch("psycopg.connect")
def test_database_close(mock_connect, mock_load_config):
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn

    db = Database()
    db.close()

    mock_conn.close.assert_called_once()
