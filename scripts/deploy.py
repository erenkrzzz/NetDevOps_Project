import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import logging
from jinja2 import Environment, FileSystemLoader
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

from models.device_model import DeviceModel
from utils.common import setup_environment, load_inventory, is_mock_mode

setup_environment()

# Vendor -> template eşlemesi; yeni cihaz tipi eklendikçe burayı büyütün
TEMPLATE_MAP = {
    "cisco_ios": "cisco_vlan.j2",
}


def render_config(device: DeviceModel, templates_dir: str) -> list:
    template_name = TEMPLATE_MAP.get(device.device_type)
    if not template_name:
        raise ValueError(f"'{device.device_type}' için tanımlı bir template yok.")

    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template(template_name)
    rendered = template.render(
        hostname=device.hostname,
        vlans=device.vlans,
        total_ports=device.total_ports,
    )
    return [line.strip() for line in rendered.splitlines() if line.strip() and not line.startswith("!")]


def push_config(device: DeviceModel, config_commands: list) -> None:
    conn_params = {
        "device_type": device.device_type,
        "host": str(device.ip_address),
        "username": device.username,
        "password": device.password.get_secret_value(),
    }
    with ConnectHandler(**conn_params) as net_connect:
        output = net_connect.send_config_set(config_commands)
        if "Invalid input" in output or "% " in output:
            raise RuntimeError(f"Cihaz komutları reddetti:\n{output}")
        net_connect.save_config()


def deploy_configurations():
    templates_dir = os.path.join(BASE_DIR, "templates")
    raw_devices = load_inventory()
    mock_mode = is_mock_mode()

    success_count = 0
    fail_count = 0

    for dev_data in raw_devices:
        hostname = dev_data.get("hostname", "Bilinmeyen Cihaz")
        try:
            device = DeviceModel(**dev_data)
            config_commands = render_config(device, templates_dir)

            if mock_mode:
                log_msg = f"[MOCK] DEPLOY HAZIR: {device.hostname} ({device.ip_address}) -> {len(config_commands)} komut üretildi."
            else:
                push_config(device, config_commands)
                log_msg = f"DEPLOY BAŞARILI: {device.hostname} ({device.ip_address}) -> {len(config_commands)} komut uygulandı."

            print(f"[SUCCESS] {log_msg}")
            logging.info(log_msg)
            success_count += 1

        except (NetmikoTimeoutException, NetmikoAuthenticationException) as e:
            fail_msg = f"BAĞLANTI HATASI: {hostname} -> {type(e).__name__}"
            print(f"[ERROR] {fail_msg}")
            logging.error(fail_msg)
            fail_count += 1

        except Exception as e:
            fail_msg = f"DEPLOY HATASI: {hostname} -> {e}"
            print(f"[ERROR] {fail_msg}")
            logging.error(fail_msg, exc_info=True)
            fail_count += 1

    print(f"\n=== Deploy Özeti | Başarılı: {success_count} | Hatalı: {fail_count} ===")
    if fail_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    deploy_configurations()