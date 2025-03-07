Below are the straightforward steps to run Vinyl-Bot in full-screen kiosk mode on your Raspberry Pi. This guide assumes you already have a working X session (for example, via lightdm or another display manager). If you’re not running a graphical environment, you’ll need to set that up first.

---

### 1. Install Chromium

Make sure Chromium is installed and up-to-date:

```
sudo apt update
sudo apt install -y chromium
```

### 2. Make the script executable

Change the Make the `kiosk.sh` script executable on your Pi: 

```
chmod +x /home/pi/Vinyl-Bot/kiosk.sh
```
*NOTE:* Replace `pi` with your actual username if different.

### 3. Create a Systemd Service

A systemd service will ensure the kiosk mode is launched automatically after the graphical environment is up. Create a service file on your Pi:

```
sudo nano /etc/systemd/system/kiosk.service
```

Paste in the following content:

```
[Unit]
Description=Chromium Kiosk Mode for Vinyl-Bot
After=graphical.target

[Service]
User=pi
Environment=DISPLAY=:0
ExecStart=/home/pi/kiosk.sh
Restart=always

[Install]
WantedBy=graphical.target
```

*NOTES:*
- Replace `pi` in the `ExecStart=` path with your actual username if different.
- The `Environment=DISPLAY=:0` line ensures the script uses the correct display.

Save and exit.


### 4. Enable and Start the Service

Reload systemd to register the new service, then enable and start it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable kiosk.service
sudo systemctl start kiosk.service
```
*Note:*
If you get an error `Failed to start hostapd.service` when attempting to reload systemd, run the following: 
```
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl start hostapd
```

You can check its status with:

```
sudo systemctl status kiosk.service
```

If you need to troubleshoot, view the logs with:

```
sudo journalctl -u kiosk.service -f
```

---

### 5. Reboot to Test

Reboot your Raspberry Pi to confirm that Chromium launches Vinyl-Bot automatically in kiosk mode:

```
sudo reboot
```

Upon reboot, once your X session is active, Chromium should start in full-screen mode displaying the Vinyl-Bot setup page.
