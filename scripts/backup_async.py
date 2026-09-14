import sys
import os
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
from models.device_model import DeviceModel

load_dotenv()
os.makedirs('backups', exist_ok=True)
os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def backup_single_device(dev_data):
    """Tek bir cihazın yedeğini alan fonksiyon"""
    dev_data['username'] = os.getenv('DEVICE_USERNAME')
    dev_data['password'] = os.getenv('DEVICE_PASSWORD')
    
    device = DeviceModel(**dev_data)
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = f"backups/{device.hostname}_{date_str}.cfg"

    print(f"[THREAD START] {device.hostname} ({device.ip_address}) için işlem başladı...")

    mock_running_config = f"""!
! Backup taken at {datetime.now()} for {device.hostname}
hostname {device.hostname}
!
"""
    try:
        with open(backup_filename, 'w') as backup_file:
            backup_file.write(mock_running_config)

        log_msg = f"PARALEL YEDEK BAŞARILI: {device.hostname} -> {backup_filename}"
        print(f"[SUCCESS] {log_msg}")
        logging.info(log_msg)
        return True
    except Exception as e:
        print(f"[ERROR] {device.hostname} - {e}")
        return False

# 1. Envanteri Oku
with open('inventory/devices.yaml', 'r') as file:
    raw_devices = yaml.safe_load(file)

# 2. ThreadPoolExecutor ile Tüm Cihazlara Aynı Anda Bağlan
if __name__ == "__main__":
    print(f"=== {len(raw_devices)} Cihaz İçin Paralel Yedekleme Başlatılıyor ===")
    
    # max_workers=5 -> 5 farklı cihaza aynı anda paralel bağlanır
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(backup_single_device, raw_devices)

    print("=== Tüm Paralel İşlemler Tamamlandı ===")