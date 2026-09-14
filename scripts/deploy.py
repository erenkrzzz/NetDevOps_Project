import sys
import os
import logging
from dotenv import load_dotenv

# Proje ana dizinini sistem yoluna ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
from jinja2 import Environment, FileSystemLoader
from models.device_model import DeviceModel

# 1. Ortam Değişkenlerini ve Log Sistemini Yükle
load_dotenv()
os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 2. Envanteri Oku
with open('inventory/devices.yaml', 'r') as file:
    raw_devices = yaml.safe_load(file)

file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader)
template = env.get_template('cisco_vlan.j2')

# 3. Bağlantı ve Konfigürasyon İşlemleri
for dev_data in raw_devices:
    # Şifre bilgilerini .env dosyasından çekiyoruz
    dev_data['username'] = os.getenv('DEVICE_USERNAME')
    dev_data['password'] = os.getenv('DEVICE_PASSWORD')

    device = DeviceModel(**dev_data)
    
    config_rendered = template.render(
        hostname=device.hostname,
        vlans=device.vlans,
        total_ports=device.total_ports
    )
    config_commands = [line.strip() for line in config_rendered.splitlines() if line.strip() and not line.startswith('!')]

    log_msg = f"{device.hostname} ({device.ip_address}) için {len(config_commands)} adet komut başarıyla üretildi."
    print(f"[SUCCESS] {log_msg}")
    logging.info(log_msg)