import sys
import os
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import yaml

# Proje kök dizinini sisteme ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.device_model import DeviceModel

load_dotenv()

# Klasörlerin varlığından emin ol
os.makedirs('backups', exist_ok=True)
os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(threadName)s] - %(message)s'
)

def backup_single_device(dev_data: dict) -> bool:
    """Tek bir cihazın yedeğini alan thread fonksiyonu"""
    dev_dict = dev_data.copy()
    dev_dict['username'] = os.getenv('DEVICE_USERNAME')
    dev_dict['password'] = os.getenv('DEVICE_PASSWORD')
    
    try:
        device = DeviceModel(**dev_dict)
    except Exception as e:
        err_msg = f"Model Doğrulama Hatası: {dev_data.get('hostname', 'Bilinmeyen')} - {e}"
        print(f"[ERROR] {err_msg}")
        logging.error(err_msg)
        return False

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = f"backups/{device.hostname}_{date_str}.cfg"

    print(f"[THREAD START] {device.hostname} ({device.ip_address}) işleniyor...")

    mock_running_config = f"""!
! Backup taken at {now} for {device.hostname}
hostname {device.hostname}
!
"""
    try:
        with open(backup_filename, 'w', encoding='utf-8') as backup_file:
            backup_file.write(mock_running_config)

        log_msg = f"PARALEL YEDEK BAŞARILI: {device.hostname} -> {backup_filename}"
        print(f"[SUCCESS] {log_msg}")
        logging.info(log_msg)
        return True

    except Exception as e:
        err_msg = f"Yedekleme Başarısız: {device.hostname} - {e}"
        print(f"[ERROR] {err_msg}")
        logging.error(err_msg, exc_info=True)
        return False

if __name__ == "__main__":
    inventory_path = 'inventory/devices.yaml'
    
    if not os.path.exists(inventory_path):
        print(f"[CRITICAL] Envanter dosyası bulunamadı: {inventory_path}")
        sys.exit(1)

    with open(inventory_path, 'r', encoding='utf-8') as file:
        raw_devices = yaml.safe_load(file) or []

    print(f"=== {len(raw_devices)} Cihaz İçin Paralel Yedekleme Başlatılıyor ===")
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(backup_single_device, raw_devices))

    successful = results.count(True)
    failed = results.count(False)
    print(f"=== İşlem Tamamlandı | Başarılı: {successful} | Hatalı: {failed} ===")