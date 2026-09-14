from pydantic import BaseModel, Field, SecretStr, field_validator
import ipaddress
from typing import List

class DeviceModel(BaseModel):
    hostname: str = Field(..., min_length=1)
    ip_address: str
    username: str
    password: SecretStr
    device_type: str = Field(default="cisco_ios")
    vlans: List[int]
    total_ports: int = Field(..., gt=0)

    @field_validator('ip_address')
    def validate_ip(cls, v):
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            raise ValueError(f"Geçersiz IP adresi: {v}")