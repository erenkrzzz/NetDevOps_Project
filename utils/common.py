import os
import sys
import logging
import yaml
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def setup_environment():
    load_dotenv()
    log_dir = os.path.join(BASE_DIR, "logs")
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "backups"), exist_ok=True)

    logging.basicConfig(
        filename=os.path.join(log_dir, "app.log"),
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - [%(threadName)s] - %(message)s",
    )


def load_inventory():
    inventory_path = os.path.join(BASE_DIR, "inventory", "devices.yaml")
    if not os.path.exists(inventory_path):
        logging.critical(f"Envanter dosyası bulunamadı: {inventory_path}")
        print(f"[CRITICAL] Envanter dosyası bulunamadı: {inventory_path}")
        sys.exit(1)

    with open(inventory_path, "r", encoding="utf-8") as f:
        raw_devices = yaml.safe_load(f) or []

    username = os.getenv("DEVICE_USERNAME")
    password = os.getenv("DEVICE_PASSWORD")
    for dev in raw_devices:
        dev.setdefault("username", username)
        dev.setdefault("password", password)
    return raw_devices


def is_mock_mode() -> bool:
    return os.getenv("USE_MOCK", "False").strip().lower() in ("1", "true", "yes")


def get_max_workers(default: int = 5) -> int:
    try:
        return int(os.getenv("MAX_WORKERS", default))
    except ValueError:
        return default