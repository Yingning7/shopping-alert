import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from run import main


@patch("run.Alerter")
@patch("run.Database")
@patch("run.load_platform_configs")
@patch("run.parse_args")
@patch("run.PLATFORM_CLS_SELECTOR")
def test_main_single_platform(mock_selector, mock_parse_args, mock_load_configs, mock_database_cls, mock_alerter_cls):
    mock_args = MagicMock()
    mock_args.platform = "runway"
    mock_parse_args.return_value = mock_args

    mock_load_configs.return_value = {
        "runway": {"run_args": [{"item_id": "123"}, {"item_id": "456"}]}
    }

    mock_db_instance = MagicMock()
    # Mock insert_data to return specs_ids
    mock_db_instance.insert_data.side_effect = [[1], [2, 3]]
    mock_database_cls.return_value = mock_db_instance

    mock_alerter_instance = MagicMock()
    mock_alerter_cls.return_value = mock_alerter_instance

    mock_platform_instance = MagicMock()
    mock_platform_instance.run.side_effect = [
        [MagicMock()],
        [MagicMock(), MagicMock()]
    ]
    
    mock_platform_cls = MagicMock(return_value=mock_platform_instance)
    mock_selector.__getitem__.return_value = mock_platform_cls

    main()

    mock_parse_args.assert_called_once()
    mock_load_configs.assert_called_once()
    mock_database_cls.assert_called_once()
    mock_db_instance.close.assert_called_once()
    mock_alerter_cls.assert_called_once()

    mock_platform_cls.assert_called_once()
    assert mock_platform_instance.run.call_count == 2
    mock_platform_instance.run.assert_any_call({"item_id": "123"})
    mock_platform_instance.run.assert_any_call({"item_id": "456"})
    
    assert mock_db_instance.insert_data.call_count == 2
    mock_db_instance.query_full_status_by_specs_ids.assert_called_once_with([1, 2, 3])
    
    mock_alerter_instance.send_alert_email.assert_called_once()


@patch("run.Alerter")
@patch("run.Database")
@patch("run.load_platform_configs")
@patch("run.parse_args")
@patch("run.PLATFORM_CLS_SELECTOR")
def test_main_exception_handling(mock_selector, mock_parse_args, mock_load_configs, mock_database_cls, mock_alerter_cls):
    mock_args = MagicMock()
    mock_args.platform = "runway"
    mock_parse_args.return_value = mock_args

    mock_load_configs.return_value = {
        "runway": {"run_args": [{"item_id": "123"}, {"item_id": "456"}]}
    }

    mock_db_instance = MagicMock()
    mock_db_instance.insert_data.return_value = [10]
    mock_database_cls.return_value = mock_db_instance

    mock_platform_instance = MagicMock()
    # First invocation fails, second succeeds
    mock_platform_instance.run.side_effect = [
        Exception("Failed to run"), 
        [MagicMock()]
    ]
    
    mock_platform_cls = MagicMock(return_value=mock_platform_instance)
    mock_selector.__getitem__.return_value = mock_platform_cls

    main()

    # Even with an exception in one iteration, it should insert for the second and alert
    assert mock_db_instance.insert_data.call_count == 1
    mock_db_instance.query_full_status_by_specs_ids.assert_called_once_with([10])
    mock_alerter_cls.return_value.send_alert_email.assert_called_once()
