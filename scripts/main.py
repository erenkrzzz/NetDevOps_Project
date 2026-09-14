import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
from jinja2 import Environment, FileSystemLoader
from models.device_model import DeviceModel

# 1. Envanter dosyasını (devices.yaml) oku
with open('inventory/devices.yaml', 'r') as file:
    raw_devices = yaml.safe_load(file)

# 2. Jinja2 Şablon Ortamını Hazırla
file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader)
template = env.get_template('cisco_vlan.j2')

# 3. Cihazları Pydantic ile doğrula ve Şablonla Konfigürasyon Üret
for dev_data in raw_devices:
    device = DeviceModel(**dev_data)
    
    config_output = template.render(
        hostname=device.hostname,
        vlans=device.vlans,
        total_ports=device.total_ports
    )
    
    print(f"\n================= {device.hostname} CONFIG =================\n")
    print(config_output)