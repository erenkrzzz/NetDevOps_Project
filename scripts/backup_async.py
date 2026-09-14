import sys
import os
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from utils.common import BACKUP_DIR, load_inventory
from models.device_model import DeviceModel

# Netmiko bağımlılığı kontrolü
try:
    from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException
    NETMIKO_AVAILABLE = True
except ImportError:
    NETMIKO_AVAILABLE = False

USE_MOCK = os.getenv("USE_MOCK", "True").lower() == "true"
MAX_WORKERS = int(os.getenv("MAX_WORKERS", 5))

def backup_single_device(dev_data: dict) -> bool:
    dev_dict = dev_data.copy()
    dev_dict['username'] = os.getenv('DEVICE_USERNAME')
    dev_dict['password'] = os.getenv('DEVICE_PASSWORD')
    
    try:
        device = DeviceModel(**dev_dict)
    except Exception as e:
        err_msg = f"Model Doğrulama Hatası ({dev_data.get('hostname', 'Bilinmeyen')}): Bilgiler geçersiz."
        print(f"[ERROR] {err_msg}")
        logging.error(err_msg)
        return False

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d_%H-%M-%S")
    # IP adresi dosya adına eklenerek çakışma engellendi
    backup_filename = os.path.join(BACKUP_DIR, f"{device.hostname}_{device.ip_address}_{date_str}.cfg")

    print(f"[THREAD START] {device.hostname} ({device.ip_address}) yedekleniyor...")

    if not USE_MOCK and NETMIKO_AVAILABLE:
        cisco_device = {
            'device_type': 'cisco_ios',
            'host': device.ip_address,
            'username': device.username,
            'password': device.password.get_secret_value(),
            'timeout': 10
        }
        try:
            with ConnectHandler(**cisco_device) as net_connect:
                running_config = net_connect.send_command("show running-config")
        except NetmikoTimeoutException:
            err_msg = f"Zaman Aşımı (Timeout): {device.hostname} ({device.ip_address}) erişilemiyor."
            print(f"[ERROR] {err_msg}")
            logging.error(err_msg)
            return False
        except NetmikoAuthenticationException:
            err_msg = f"Kimlik Doğrulama Hatası (Auth Error): {device.hostname} kullanıcı adı/şifre hatalı."
            print(f"[ERROR] {err_msg}")
            logging.error(err_msg)
            return False
        except Exception as e:
            err_msg = f"SSH Bağlantı Hatası: {device.hostname} - {type(e).__name__}"
            print(f"[ERROR] {err_msg}")
            logging.error(err_msg)
            return False
    else:
        # Simülasyon / Mock Modu
        running_config = f"!\n! Mock Backup taken at {now} for {device.hostname}\nhostname {device.hostname}\n!\n"

    try:
        with open(backup_filename, 'w', encoding='utf-8') as backup_file:
            backup_file.write(running_config)

        log_msg = f"PARALEL YEDEK BAŞARILI: {device.hostname} -> {backup_filename}"
        print(f"[SUCCESS] {log_msg}")
        logging.info(log_msg)
        return True

    except Exception as e:
        err_msg = f"Dosya Yazma Hatası: {device.hostname} - {type(e).__name__}"
        print(f"[ERROR] {err_msg}")
        logging.error(err_msg)
        return False

if __name__ == "__main__":
    raw_devices = load_inventory()
    print(f"=== {len(raw_devices)} Cihaz İçin Paralel Yedekleme Başlatılıyor (Mock={USE_MOCK}) ===")
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(executor.map(backup_single_device, raw_devices))

    successful = results.count(True)
    failed = results.count(False)
    print(f"=== İşlem Tamamlandı | Başarılı: {successful} | Hatalı: {failed} ===")
    
    if failed > 0:
        sys.exit(1)