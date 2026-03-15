import pytest
import datetime as dt
import pandas as pd
from unittest.mock import patch, MagicMock

from database.db import Database
from shopping_platforms._platform import BaseRecord

@patch("builtins.open", new_callable=MagicMock)
@patch("tomllib.load")
@patch("psycopg.connect")
def test_load_db_config(mock_connect, mock_tomllib_load, mock_file):
    mock_tomllib_load.return_value = {"postgres": {"host": "localhost", "port": 5432}}
    
    # Needs to bypass init calling psycopg.connect so we temporarily patch it out
    with patch.object(Database, "_initialize"):
        db = Database()
        db._db_config = {"host": "localhost", "port": 5432}

    from pathlib import Path
    path = Path("dummy.toml")
    result = db.load_db_config(path)
    
    # We assert tomllib.load was called once and config parsed
    mock_tomllib_load.assert_called()
    assert result == {"host": "localhost", "port": 5432}


@patch.object(Database, "load_db_config")
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


@patch.object(Database, "load_db_config")
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


@patch.object(Database, "load_db_config")
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
@patch.object(Database, "load_db_config")
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

    specs_ids = db.insert_data([record])

    assert mock_query.call_count == 5
    assert mock_insert.call_count == 4
    assert specs_ids == [1]


@patch.object(Database, "_query_table")
@patch.object(Database, "load_db_config")
@patch("psycopg.connect")
def test_query_full_status_by_specs_ids(mock_connect, mock_load_config, mock_query):
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    mock_query.return_value = pd.DataFrame([{"specs_id": 1, "current_price": 500}])
    
    db = Database()
    df = db.query_full_status_by_specs_ids([1, 2])
    
    assert mock_query.call_count == 1
    # Check that the query was formatted correctly with "1, 2" inside IN clause
    args, _ = mock_query.call_args
    assert "IN (1, 2)" in args[0]
    assert not df.empty


@patch.object(Database, "load_db_config")
@patch("psycopg.connect")
def test_database_close(mock_connect, mock_load_config):
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn

    db = Database()
    db.close()

    mock_conn.close.assert_called_once()
