# lastfm.py

from flask import Blueprint, render_template, redirect, request, jsonify
import pylast
from utils import get_device_ip, generate_qr_code_image
from config import LASTFM_API_KEY, LASTFM_API_SECRET

lastfm_bp = Blueprint('lastfm', __name__)

# Global variable to store LastFM session details
lastfm_session = None

@lastfm_bp.route("/lastfm", methods=["GET"])
def lastfm_page():
    device_ip = get_device_ip()
    login_url = f"http://{device_ip}:5000/lastfm/login"
    qr_code_image = generate_qr_code_image(login_url)
    return render_template("lastfm_login.html", login_url=login_url, qr_code=qr_code_image)

@lastfm_bp.route("/lastfm/login", methods=["GET"])
def lastfm_login():
    device_ip = get_device_ip()
    callback_url = f"http://{device_ip}:5000/lastfm/callback"
    lastfm_auth_url = f"http://www.last.fm/api/auth/?api_key={LASTFM_API_KEY}&cb={callback_url}"
    return redirect(lastfm_auth_url)

@lastfm_bp.route("/lastfm/callback", methods=["GET"])
def lastfm_callback():
    global lastfm_session
    token = request.args.get("token")
    if not token:
        return "Error: No token received", 400
    try:
        network = pylast.LastFMNetwork(api_key=LASTFM_API_KEY, api_secret=LASTFM_API_SECRET)
        session_key = network.get_session_key(token)
        lastfm_session = {
            "session_key": session_key,
            "username": network.get_authenticated_user().get_name()
        }
    except Exception as e:
        return f"Error during LastFM authentication: {str(e)}", 500
    return render_template("lastfm_callback.html", username=lastfm_session["username"])

@lastfm_bp.route("/lastfm/status", methods=["GET"])
def lastfm_status():
    if lastfm_session:
        return jsonify(status="logged_in", username=lastfm_session["username"])
    else:
        return jsonify(status="not_logged_in")

def get_lastfm_session():
    global lastfm_session
    return lastfm_session
