import sys
import os
import logging
from dotenv import load_dotenv
import yaml
from jinja2 import Environment, FileSystemLoader

# Proje ana dizinini sistem yoluna ekle (Script nereden çalıştırılırsa çalışsın şaşmaz)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from models.device_model import DeviceModel

# 1. Ortam Değişkenlerini ve Log Sistemini Yükle
load_dotenv()
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, 'app.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def deploy_configurations():
    inventory_path = os.path.join(BASE_DIR, 'inventory', 'devices.yaml')
    templates_dir = os.path.join(BASE_DIR, 'templates')

    if not os.path.exists(inventory_path):
        logging.critical(f"Envanter dosyası bulunamadı: {inventory_path}")
        print(f"[CRITICAL] Envanter dosyası bulunamadı: {inventory_path}")
        sys.exit(1)

    # 2. Envanteri Oku
    with open(inventory_path, 'r', encoding='utf-8') as file:
        raw_devices = yaml.safe_load(file) or []

    file_loader = FileSystemLoader(templates_dir)
    env = Environment(loader=file_loader)
    
    # Varsayılan şablon (İleride cihaz modeline göre dinamik seçilebilir)
    template = env.get_template('cisco_vlan.j2')

    success_count = 0
    fail_count = 0

    # 3. Konfigürasyon Üretim ve Dağıtım Döngüsü
    for dev_data in raw_devices:
        dev_dict = dev_data.copy()
        dev_dict['username'] = os.getenv('DEVICE_USERNAME')
        dev_dict['password'] = os.getenv('DEVICE_PASSWORD')

        # Cihaz bazlı Hata Yönetimi (Tek cihazın hatası tüm sistemi durdurmaz)
        try:
            device = DeviceModel(**dev_dict)
            
            config_rendered = template.render(
                hostname=device.hostname,
                vlans=device.vlans,
                total_ports=device.total_ports
            )
            
            # Yorum satırlarını ve boş satırları temizle
            config_commands = [
                line.strip() for line in config_rendered.splitlines() 
                if line.strip() and not line.startswith('!')
            ]

            # GERÇEK DEPLOYMENT NOKTASI:
            # Buraya Netmiko / Scrapli entegre edildiğinde komutlar cihaza itilir:
            # netmiko_connection.send_config_set(config_commands)

            log_msg = f"DEPLOY HAZIR: {device.hostname} ({device.ip_address}) -> {len(config_commands)} komut üretildi."
            print(f"[SUCCESS] {log_msg}")
            logging.info(log_msg)
            success_count += 1

        except Exception as e:
            fail_msg = f"DEPLOY HATASI: {dev_data.get('hostname', 'Bilinmeyen Cihaz')} -> {e}"
            print(f"[ERROR] {fail_msg}")
            logging.error(fail_msg, exc_info=True)
            fail_count += 1

    print(f"\n=== Deploy Özeti | Başarılı: {success_count} | Hatalı: {fail_count} ===")
    
    # CI/CD Pipeline uyumluluğu için hatalı işlem varsa exit code 1 dön
    if fail_count > 0:
        sys.exit(1)

if __name__ == "__main__":
    deploy_configurations()