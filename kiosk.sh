#!/bin/bash
# Disable screensaver and power management
xset s off         # Turn off the screensaver
xset s noblank     # Prevent screen blanking
xset -dpms         # Disable Display Power Management Signaling

# Wait to ensure the graphical environment is ready
sleep 10

# Launch Chromium in kiosk mode pointing to Vinyl-Bot
/usr/bin/chromium --noerrdialogs --disable-infobars --kiosk http://localhost:5000
