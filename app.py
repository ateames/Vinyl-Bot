# app.py

import threading
import time
import subprocess
from flask import Flask, render_template
from config import WIFI_SSID, WIFI_SECURITY
from utils import generate_random_password, get_device_ip, generate_wifi_qr_data, generate_qr_code_image
from wifi import wifi_bp
from lastfm import lastfm_bp, get_lastfm_session
from audio import start_audio_capture, current_track_metadata

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(wifi_bp)
app.register_blueprint(lastfm_bp)

@app.route("/")
def index():
    password = generate_random_password()
    device_ip = get_device_ip()
    qr_data_string = generate_wifi_qr_data(WIFI_SSID, password, device_ip, WIFI_SECURITY)
    ap_qr = generate_qr_code_image(qr_data_string)
    setup_url = f"http://{device_ip}:5000/wifi-setup"
    lastfm_login_url = f"http://{device_ip}:5000/lastfm"
    lastfm_qr = generate_qr_code_image(lastfm_login_url)
    return render_template("index.html", ssid=WIFI_SSID, password=password,
                           ap_qr=ap_qr, setup_url=setup_url, device_ip=device_ip, lastfm_qr=lastfm_qr)

@app.route("/current-track")
def current_track():
    return render_template("current_track.html", metadata=current_track_metadata)

def open_kiosk_browser():
    time.sleep(2)
    try:
        subprocess.Popen(["chromium-browser", "--kiosk", "http://localhost:5000"])
    except Exception as e:
        print(f"Failed to open kiosk browser: {e}")

if __name__ == "__main__":
    threading.Thread(target=open_kiosk_browser, daemon=True).start()
    start_audio_capture(get_lastfm_session)
    app.run(host="0.0.0.0", port=5000)
