from pydantic import BaseModel, IPvAnyAddress, field_validator
from typing import List

class DeviceModel(BaseModel):
    hostname: str
    ip_address: IPvAnyAddress
    device_type: str = "cisco_ios"
    username: str
    password: str
    total_ports: int
    is_active: bool
    vlans: List[int]

    @field_validator('vlans')
    def validate_vlan_range(cls, vlan_list):
        for vlan in vlan_list:
            if not (1 <= vlan <= 4094):
                raise ValueError(f"Geçersiz VLAN ID: {vlan}. VLAN ID 1 ile 4094 arasında olmalıdır.")
        return vlan_list