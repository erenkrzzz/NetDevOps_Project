import sys
import os
import logging
from jinja2 import Environment, FileSystemLoader

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from utils.common import load_inventory
from models.device_model import DeviceModel

try:
    from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException
    NETMIKO_AVAILABLE = True
except ImportError:
    NETMIKO_AVAILABLE = False

USE_MOCK = os.getenv("USE_MOCK", "True").lower() == "true"

def deploy_configurations():
    raw_devices = load_inventory()
    templates_dir = os.path.join(BASE_DIR, 'templates')

    file_loader = FileSystemLoader(templates_dir)
    env = Environment(loader=file_loader)
    template = env.get_template('cisco_vlan.j2')

    success_count = 0
    fail_count = 0

    for dev_data in raw_devices:
        dev_dict = dev_data.copy()
        dev_dict['username'] = os.getenv('DEVICE_USERNAME')
        dev_dict['password'] = os.getenv('DEVICE_PASSWORD')

        try:
            device = DeviceModel(**dev_dict)
            
            config_rendered = template.render(
                hostname=device.hostname,
                vlans=device.vlans,
                total_ports=device.total_ports
            )
            
            config_commands = [
                line.strip() for line in config_rendered.splitlines() 
                if line.strip() and not line.startswith('!')
            ]

            if not USE_MOCK and NETMIKO_AVAILABLE:
                cisco_device = {
                    'device_type': device.device_type,
                    'host': device.ip_address,
                    'username': device.username,
                    'password': device.password.get_secret_value(),
                    'timeout': 10
                }
                with ConnectHandler(**cisco_device) as net_connect:
                    output = net_connect.send_config_set(config_commands)
                    logging.info(f"Netmiko Output ({device.hostname}): {output}")
            else:
                # Mock Deployment Loglama
                print(f"[MOCK DEPLOY] {device.hostname} ({device.ip_address}) -> {len(config_commands)} komut simüle edildi.")

            log_msg = f"DEPLOY BAŞARILI: {device.hostname} ({device.ip_address})"
            print(f"[SUCCESS] {log_msg}")
            logging.info(log_msg)
            success_count += 1

        except Exception as e:
            fail_msg = f"DEPLOY HATASI: {dev_data.get('hostname', 'Bilinmeyen Cihaz')} -> {type(e).__name__}"
            print(f"[ERROR] {fail_msg}")
            logging.error(fail_msg, exc_info=True)
            fail_count += 1

    print(f"\n=== Deploy Özeti | Başarılı: {success_count} | Hatalı: {fail_count} ===")
    
    if fail_count > 0:
        sys.exit(1)

if __name__ == "__main__":
    deploy_configurations()