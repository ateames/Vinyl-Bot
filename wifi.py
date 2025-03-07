# wifi.py

import re
import subprocess
import time
from flask import Blueprint, render_template, request
from utils import get_device_ip

wifi_bp = Blueprint('wifi', __name__)

def scan_wifi_networks():
    try:
        scan_output = subprocess.check_output(
            ["sudo", "iwlist", "wlan0", "scan"],
            stderr=subprocess.STDOUT
        ).decode('utf-8')
    except subprocess.CalledProcessError:
        return []
    ssids = set()
    for line in scan_output.splitlines():
        line = line.strip()
        if line.startswith("ESSID:"):
            m = re.search(r'ESSID:"(.*)"', line)
            if m:
                found_ssid = m.group(1)
                if found_ssid:
                    ssids.add(found_ssid)
    return list(ssids)

def connect_to_wifi(ssid, password):
    wpa_conf = f"""ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US

network={{
    ssid="{ssid}"
    psk="{password}"
}}
"""
    try:
        with open("/etc/wpa_supplicant/wpa_supplicant.conf", "w") as f:
            f.write(wpa_conf)
    except Exception as e:
        return False, f"Failed to write configuration: {str(e)}"
    
    try:
        subprocess.check_call(["sudo", "wpa_cli", "-i", "wlan0", "reconfigure"])
    except subprocess.CalledProcessError:
        return False, "Failed to reconfigure WiFi."
    
    time.sleep(10)
    try:
        subprocess.check_call(
            ["ping", "-c", "1", "8.8.8.8"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True, "Connected successfully."
    except subprocess.CalledProcessError:
        return False, "Unable to connect to the WiFi network. Please check your credentials."

@wifi_bp.route("/wifi-setup", methods=["GET"])
def wifi_setup():
    ssids = scan_wifi_networks()
    return render_template("wifi_setup.html", ssids=ssids, error=None)

@wifi_bp.route("/configure-wifi", methods=["POST"])
def configure_wifi():
    ssid = request.form.get("ssid")
    password = request.form.get("password")
    success, message = connect_to_wifi(ssid, password)
    if success:
       return render_template("connection_status.html", ssid=ssid, success=True, message=message)
    else:
       ssids = scan_wifi_networks()
       return render_template("wifi_setup.html", ssids=ssids, error=message)
