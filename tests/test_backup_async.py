import pytest
from unittest.mock import patch, MagicMock
from models.device_model import DeviceModel
from scripts.backup_async import fetch_running_config


def make_device():
    return DeviceModel(
        hostname="Test-Router",
        ip_address="10.0.0.1",
        device_type="cisco_ios",
        username="admin",
        password="test123",
    )


@patch("scripts.backup_async.ConnectHandler")
def test_fetch_running_config_success(mock_connect):
    mock_conn = MagicMock()
    mock_conn.send_command.return_value = "hostname Test-Router\n!"
    mock_connect.return_value.__enter__.return_value = mock_conn

    device = make_device()
    result = fetch_running_config(device)

    assert "hostname Test-Router" in result


@patch("scripts.backup_async.ConnectHandler")
def test_fetch_running_config_empty_output_raises(mock_connect):
    mock_conn = MagicMock()
    mock_conn.send_command.return_value = ""
    mock_connect.return_value.__enter__.return_value = mock_conn

    device = make_device()
    with pytest.raises(RuntimeError, match="boş çıktı"):
        fetch_running_config(device)


@patch("scripts.backup_async.ConnectHandler")
def test_fetch_running_config_invalid_input_raises(mock_connect):
    mock_conn = MagicMock()
    mock_conn.send_command.return_value = "% Invalid input detected"
    mock_connect.return_value.__enter__.return_value = mock_conn

    device = make_device()
    with pytest.raises(RuntimeError, match="reddetti"):
        fetch_running_config(device)