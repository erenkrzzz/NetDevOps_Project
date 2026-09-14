import os
import sys
import logging
import yaml
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

load_dotenv()

LOG_DIR = os.path.join(BASE_DIR, 'logs')
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
INVENTORY_PATH = os.path.join(BASE_DIR, 'inventory', 'devices.yaml')

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, 'app.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(threadName)s] - %(message)s'
)

def load_inventory():
    if not os.path.exists(INVENTORY_PATH):
        logging.critical(f"Envanter dosyası bulunamadı: {INVENTORY_PATH}")
        print(f"[CRITICAL] Envanter dosyası bulunamadı: {INVENTORY_PATH}")
        sys.exit(1)
    
    with open(INVENTORY_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or []