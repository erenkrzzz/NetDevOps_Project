import sys
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
from models.device_model import DeviceModel

# Entegrasyonlar
load_dotenv()
os.makedirs('backups', exist_ok=True)
os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 1. Envanteri Oku
with open('inventory/devices.yaml', 'r') as file:
    raw_devices = yaml.safe_load(file)

# 2. Otomatik Yedekleme Döngüsü
for dev_data in raw_devices:
    dev_data['username'] = os.getenv('DEVICE_USERNAME')
    dev_data['password'] = os.getenv('DEVICE_PASSWORD')
    
    device = DeviceModel(**dev_data)
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
    backup_filename = f"backups/{device.hostname}_{date_str}.cfg"

    print(f"[+] {device.hostname} ({device.ip_address}) cihazından yedek çekiliyor...")

    # Simülasyon/Test Modu: Gerçek cihaza bağlıymış gibi örnek konfigürasyon yediği üretir
    mock_running_config = f"""!
! Last configuration change at {datetime.now()}
!
version 15.2
service timestamps debug datetime msec
service timestamps log datetime msec
no service password-encryption
!
hostname {device.hostname}
!
interface GigabitEthernet0/1
 switchport mode access
 switchport access vlan 10
!
end
"""

    try:
        # GERÇEK BAĞLANTI (Cihaz erişilebilir olduğunda aktif edilir):
        # cisco_device = {
        #     'device_type': device.device_type,
        #     'host': str(device.ip_address),
        #     'username': device.username,
        #     'password': device.password,
        # }
        # net_connect = ConnectHandler(**cisco_device)
        # mock_running_config = net_connect.send_command('show running-config')
        # net_connect.disconnect()

        with open(backup_filename, 'w') as backup_file:
            backup_file.write(mock_running_config)

        log_msg = f"YEDEK BAŞARILI: {device.hostname} konfigürasyonu '{backup_filename}' dosyasına kaydedildi."
        print(f"[SUCCESS] {log_msg}")
        logging.info(log_msg)

    except Exception as e:
        err_msg = f"YEDEK HATASI: {device.hostname} - {e}"
        print(f"[ERROR] {err_msg}")
        logging.error(err_msg)