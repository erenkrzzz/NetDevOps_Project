import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

from models.device_model import DeviceModel
from utils.common import setup_environment, load_inventory, is_mock_mode, get_max_workers

setup_environment()

BACKUP_DIR = os.path.join(BASE_DIR, "backups")


def fetch_running_config(device: DeviceModel) -> str:
    conn_params = {
        "device_type": device.device_type,
        "host": str(device.ip_address),
        "username": device.username,
        "password": device.password.get_secret_value(),
    }
    with ConnectHandler(**conn_params) as net_connect:
        output = net_connect.send_command("show running-config")

    if not output or not output.strip():
        raise RuntimeError("Cihazdan boş çıktı döndü.")
    if "Invalid input" in output or "% " in output:
        raise RuntimeError(f"Cihaz komutu reddetti:\n{output}")
    return output


def backup_single_device(dev_data: dict) -> bool:
    hostname = dev_data.get("hostname", "Bilinmeyen")
    mock_mode = is_mock_mode()

    try:
        device = DeviceModel(**dev_data)
    except Exception as e:
        err_msg = f"Model Doğrulama Hatası: {hostname} - {e}"
        print(f"[ERROR] {err_msg}")
        logging.error(err_msg)
        return False

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = os.path.join(
        BACKUP_DIR, f"{device.hostname}_{device.ip_address}_{date_str}.cfg"
    )

    print(f"[THREAD START] {device.hostname} ({device.ip_address}) işleniyor...")

    try:
        if mock_mode:
            config_data = (
                "! [WARNING: MOCK DATA - NOT A REAL BACKUP]\n"
                f"! Backup taken at {now} for {device.hostname}\n"
                f"hostname {device.hostname}\n!\n"
            )
        else:
            config_data = fetch_running_config(device)

        with open(backup_filename, "w", encoding="utf-8") as backup_file:
            backup_file.write(config_data)

        log_msg = f"{'[MOCK] ' if mock_mode else ''}YEDEK BAŞARILI: {device.hostname} -> {backup_filename}"
        print(f"[SUCCESS] {log_msg}")
        logging.info(log_msg)
        return True

    except (NetmikoTimeoutException, NetmikoAuthenticationException) as e:
        err_msg = f"BAĞLANTI HATASI: {device.hostname} -> {type(e).__name__}"
        print(f"[ERROR] {err_msg}")
        logging.error(err_msg)
        return False

    except Exception as e:
        err_msg = f"Yedekleme Başarısız: {device.hostname} - {e}"
        print(f"[ERROR] {err_msg}")
        logging.error(err_msg, exc_info=True)
        return False


if __name__ == "__main__":
    raw_devices = load_inventory()
    max_workers = get_max_workers()

    print(f"=== {len(raw_devices)} Cihaz İçin Paralel Yedekleme Başlatılıyor (max_workers={max_workers}) ===")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(backup_single_device, raw_devices))

    successful = results.count(True)
    failed = results.count(False)
    print(f"=== İşlem Tamamlandı | Başarılı: {successful} | Hatalı: {failed} ===")

    if failed > 0:
        sys.exit(1)