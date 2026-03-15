import pytest
from unittest.mock import patch, mock_open
from pathlib import Path
from database.utils import load_db_config

@patch("builtins.open", new_callable=mock_open, read_data=b'[postgres]\nhost="localhost"\nport=5432')
@patch("tomllib.load")
def test_load_db_config(mock_tomllib_load, mock_file):
    mock_tomllib_load.return_value = {"postgres": {"host": "localhost", "port": 5432}}
    path = Path("dummy.toml")
    result = load_db_config(path)
    
    mock_file.assert_called_once_with(path, mode="rb")
    mock_tomllib_load.assert_called_once()
    assert result == {"host": "localhost", "port": 5432}
