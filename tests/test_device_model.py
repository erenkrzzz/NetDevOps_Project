import pytest
from pydantic import ValidationError
from models.device_model import DeviceModel

# 1. Doğru verinin sorunsuz geçtiğini test eden senaryo
def test_valid_device_model():
    data = {
        "hostname": "Test-Switch-01",
        "ip_address": "10.0.0.1",
        "device_type": "cisco_ios",
        "username": "admin",
        "password": "password123",
        "total_ports": 48,
        "is_active": True,
        "vlans": [10, 20]
    }
    device = DeviceModel(**data)
    assert device.hostname == "Test-Switch-01"
    assert device.total_ports == 48

# 2. Hatalı VLAN ID (4094'ten büyük) girildiğinde hata fırlattığını test eden senaryo
def test_invalid_vlan_range():
    data = {
        "hostname": "Test-Switch-02",
        "ip_address": "10.0.0.2",
        "device_type": "cisco_ios",
        "username": "admin",
        "password": "password123",
        "total_ports": 24,
        "is_active": True,
        "vlans": [10, 5000]  # 5000 geçersiz VLAN ID!
    }
    with pytest.raises(ValidationError):
        DeviceModel(**data)