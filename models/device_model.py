from pydantic import BaseModel, Field, SecretStr, field_validator
from ipaddress import IPv4Address
from typing import List


class DeviceModel(BaseModel):
    hostname: str
    ip_address: IPv4Address
    device_type: str = Field(default="cisco_ios")
    username: str
    password: SecretStr
    vlans: List[int] = Field(default_factory=list)
    total_ports: int = Field(default=24, gt=0)

    @field_validator("vlans")
    @classmethod
    def validate_vlans(cls, v):
        for vlan_id in v:
            if not (1 <= vlan_id <= 4094):
                raise ValueError(f"Geçersiz VLAN ID: {vlan_id} (1-4094 aralığında olmalı)")
        return v