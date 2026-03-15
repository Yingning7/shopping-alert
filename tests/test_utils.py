import pytest
from unittest.mock import patch, mock_open
from pathlib import Path

from utils import parse_args, load_platform_configs


@patch("sys.argv", ["run.py", "--platform", "runway"])
def test_parse_args_specific_platform():
    args = parse_args()
    assert args.platform == "runway"


@patch("sys.argv", ["run.py", "--platform", "all"])
def test_parse_args_all_platforms():
    args = parse_args()
    assert args.platform == "all"


@patch("sys.argv", ["run.py"])
def test_parse_args_missing_platform():
    with pytest.raises(SystemExit):
        parse_args()


@patch("sys.argv", ["run.py", "--platform", "invalid"])
def test_parse_args_invalid_platform():
    with pytest.raises(SystemExit):
        parse_args()


@patch("builtins.open", new_callable=mock_open, read_data=b'key="value"')
@patch("tomllib.load")
def test_load_platform_configs(mock_tomllib_load, mock_file):
    mock_tomllib_load.return_value = {"key": "value"}
    path = Path("dummy.toml")
    result = load_platform_configs(path)
    
    mock_file.assert_called_once_with(path, mode="rb")
    mock_tomllib_load.assert_called_once()
    assert result == {"key": "value"}
