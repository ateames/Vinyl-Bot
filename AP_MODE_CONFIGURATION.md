# AP Mode Configuration for Vinyl‑Bot
This section outlines the steps required to configure your Raspberry Pi to boot in Access Point (AP) mode. This configuration is necessary for the Vinyl‑Bot application to serve its kiosk setup interface and allow users to connect to the device for WiFi and LastFM configuration.

> **Note:** The AP mode configuration is independent of the Python application code. You must configure the system (via hostapd, dnsmasq, etc.) separately. The application code assumes that the Pi is already in AP mode (with SSID "Vinyl‑Bot") and that the interface is set up as described below.

## 1. Install Required Packages

Update your package lists and install `hostapd` and `dnsmasq`:

```bash
sudo apt-get update
sudo apt-get install hostapd dnsmasq
```

## 2. Configure a Static IP for wlan0

Edit `/etc/dhcpcd.conf` to assign a static IP to the wireless interface:

```bash
sudo nano /etc/dhcpcd.conf
```
Add the following lines at the end of the file:
```
interface wlan0
    static ip_address=192.168.4.1/24
    nohook wpa_supplicant
```
Save and exit the editor.

## 3. Configure dnsmasq

Rename the original dnsmasq configuration file:
```bash
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
```
Create a new `/etc/dnsmasq.conf` file:
```bash
sudo nano /etc/dnsmasq.conf
```
Insert the following configuration:
```
interface=wlan0      # Use interface wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
```
Save and exit.

## 4. Configure hostapd
Create the hostapd configuration file:
```bash
sudo nano /etc/hostapd/hostapd.conf
```
Insert the following content (adjust parameters as needed):
```
interface=wlan0
driver=nl80211
ssid=Vinyl-Bot
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=YOUR_RANDOM_PASSWORD
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
```
Replace `YOUR_RANDOM_PASSWORD` with a strong, randomly generated password.
Now, point hostapd to this configuration file by editing:

```bash
sudo nano /etc/default/hostapd
```
Find the line with `#DAEMON_CONF=""` and change it to:
```
DAEMON_CONF="/etc/hostapd/hostapd.conf"
```
Save and exit.

## 5. Enable IP Forwarding and Configure NAT
Enable IP forwarding by editing `/etc/sysctl.conf`:
```bash
sudo nano /etc/sysctl.conf
```
Uncomment or add the following line:
```
net.ipv4.ip_forward=1
```
Set up NAT (Network Address Translation) with iptables:
```bash
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo iptables -A FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT
```
Save these rules so they persist across reboots:
```bash
sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"
```
Edit `/etc/rc.local` (before the `exit 0` line) to restore the iptables rules on boot:

```bash
sudo nano /etc/rc.local
```
Add this line above `exit 0`:
```
iptables-restore < /etc/iptables.ipv4.nat
```
Save and exit.
## 6. Start and Enable Services
Start the hostapd and dnsmasq services:
```bash
sudo systemctl start hostapd
sudo systemctl start dnsmasq
```
Enable them to start automatically at boot:
```bash
sudo systemctl enable hostapd
sudo systemctl enable dnsmasq
```
## 7. Reboot the Raspberry Pi
Reboot to apply all changes:
```bash
sudo reboot
```
After rebooting, your Raspberry Pi should:
- Broadcast the "Vinyl‑Bot" SSID.
- Have a static IP of 192.168.4.1 on wlan0.
- Serve DHCP leases via dnsmasq.
- Run hostapd to manage the wireless network.

This configuration enables the Vinyl‑Bot application to provide a kiosk setup interface, allowing users to connect to the device and configure WiFi and LastFM settings.
