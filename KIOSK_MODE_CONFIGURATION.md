Below are the straightforward steps to run Vinyl-Bot in full-screen kiosk mode on your Raspberry Pi. This guide assumes you already have a working X session (for example, via lightdm or another display manager). If you’re not running a graphical environment, you’ll need to set that up first.

---

### 1. Install Chromium

Make sure Chromium is installed and up-to-date:

```
sudo apt update
sudo apt install -y chromium
```
### 2. Create a Startup Script

Create a script (for example, `/home/Vinyl-Bot/kiosk.sh`) that waits for the graphical environment to fully load and then launches Chromium.

```
nano /home/pi/kiosk.sh
```

Paste in the following code:

```
#!/bin/bash
# Disable screensaver and power management
xset s off         # Turn off the screensaver
xset s noblank     # Prevent screen blanking
xset -dpms         # Disable Display Power Management Signaling

# Wait to ensure the graphical environment is ready
sleep 10

# Launch Chromium in kiosk mode pointing to Vinyl-Bot
/usr/bin/chromium --noerrdialogs --disable-infobars --kiosk http://localhost:5000
```
*Tip:* The `sleep 10` command gives the system time to load the X session. Adjust the delay if necessary.

Save the file and exit the editor. Then, make the script executable:

```bash
chmod +x /home/pi/Vinyl-Bot/kiosk.sh
```

### 3. Create a Systemd Service

A systemd service will ensure the kiosk mode is launched automatically after the graphical environment is up. Create a service file:

```
sudo nano /etc/systemd/system/kiosk.service
```

Paste in the following content and update the path to your `kiosk.sh` file:

```ini
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

*Notes:*
- Replace `pi` with your actual username if different.
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

```bash
sudo systemctl status kiosk.service
```

If you need to troubleshoot, view the logs with:

```bash
sudo journalctl -u kiosk.service -f
```

---

### 5. Reboot to Test

Reboot your Raspberry Pi to confirm that Chromium launches Vinyl-Bot automatically in kiosk mode:

```bash
sudo reboot
```

Upon reboot, once your X session is active, Chromium should start in full-screen mode displaying the Vinyl-Bot setup page.
