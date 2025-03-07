# Vinyl‑Bot

Vinyl‑Bot is a Raspberry Pi application that captures audio from a turntable, fingerprints the audio to identify the track (using MusicBrainz and AcoustID), displays track metadata (including album art), and automatically scrobbles the track to a user’s LastFM account. The application also provides a kiosk interface in AP mode for initial WiFi and LastFM configuration. This project is containerized with Docker for simplified deployment and reproducibility.

> **Note:**  
> The Docker container runs the Python application (Flask server, audio capture/scrobbling, etc.). However, AP mode configuration (using hostapd/dnsmasq) and kiosk browser launch are handled on the Raspberry Pi host. Ensure your Pi is configured as an AP before deploying the Docker container.

---

## Features

- **Access Point & Kiosk Interface:**  
  - The Pi boots in AP mode (SSID: `Vinyl-Bot`) and displays a kiosk-style web interface.
  - The interface shows the AP credentials (with a randomly generated password) and QR codes for WiFi setup and LastFM login.

- **WiFi Setup:**  
  - Users can connect to the Pi’s AP, access the web interface, and choose a home/office WiFi network from a scanned list.
  - The application then reconfigures the Pi’s WiFi (writing to `/etc/wpa_supplicant/wpa_supplicant.conf`) to join the selected network.

- **LastFM Integration:**  
  - Users can authenticate with their LastFM account via a QR code login.
  - The application stores the authenticated session for subsequent scrobbling.

- **Audio Fingerprinting & Scrobbling:**  
  - Audio is captured using a Pi‑compatible sound card (via PyAudio).
  - The fingerprint is generated with Chromaprint and sent to MusicBrainz (with fallback to AcoustID) to retrieve track metadata.
  - New tracks are scrobbled automatically to LastFM using `pylast`.

- **Dockerized Deployment:**  
  - The entire Python application is containerized using Docker.
  - The Docker container simplifies installation and ensures consistent environments on the Raspberry Pi.

---

## File Structure
The project is organized as follows:
```
VinylBot/
├── app.py
├── config.py
├── utils.py
├── wifi.py
├── lastfm.py
├── audio.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore 
└── templates/
    ├── index.html
    ├── wifi_setup.html
    ├── connection_status.html
    ├── lastfm_login.html
    ├── lastfm_callback.html
    └── current_track.html
```
- **app.py:**  
  Initializes the Flask app, registers Blueprints for WiFi and LastFM, starts background threads for kiosk browser and audio capture/scrobbling, and runs the server.

- **config.py:**  
  Contains configuration variables and API keys (LastFM, AcoustID, etc.). **Update with your credentials.**

- **utils.py:**  
  Provides shared utility functions (e.g., random password generation, IP retrieval, QR code generation).

- **wifi.py:**  
  Implements endpoints and functions for scanning WiFi networks, handling WiFi configuration, and connecting to a selected network.

- **lastfm.py:**  
  Implements LastFM authentication endpoints (login, callback, status) and session handling using `pylast`.

- **audio.py:**  
  Contains functions for audio capture (with PyAudio), fingerprinting (with Chromaprint), metadata lookup (via MusicBrainz and AcoustID), and scrobbling to LastFM.

- **requirements.txt:**  
  Lists all required Python packages.

- **Dockerfile:**  
  Defines the Docker image, installs dependencies, and runs the application.

- **templates/**  
  Contains HTML templates for the kiosk interface, WiFi setup, LastFM login, and current track display.

---

## Docker Deployment

### Prerequisites

- A Raspberry Pi with Docker installed.
- The Pi must be pre-configured to run in AP mode (using hostapd and dnsmasq) with the SSID `Vinyl-Bot`: [AP Mode Configuration](./AP_MODE_CONFIGURATION.md)
- Access to a Pi‑compatible sound card (and proper device mapping in Docker).
- Chromium installed on the host if kiosk mode is required (note: kiosk browser launch is handled outside the container): [Kiosk Mode Configuration](./KIOSK_MODE_CONFIGURATION.md)
- Credentials for services: API keys for LastFM and AcoustID, MusicBrainz User Agent.

### Building the Docker Image

From the project root (`VinylBot/`), build the Docker image:
```
docker build -t vinyl-bot .
```
### Running the Docker Container

Run the container with host networking so that the Flask server is accessible on the Pi’s IP, and map the audio device for capturing audio (adjust `/dev/snd` as needed):

```
docker run --rm --net=host --device /dev/snd vinyl-bot
```
**Important:**  
Running in host network mode allows the container to share the host’s network interfaces, which is necessary for AP mode and for the application to bind to the correct IP (e.g., 192.168.4.1).  
You may need to configure additional device mappings (or use `--privileged`) if your audio device requires special permissions.

---

## AP Mode Configuration (Host Setup)

Before running the Docker container, configure your Raspberry Pi to run in AP mode. Refer to the [AP Mode Configuration](./AP_MODE_CONFIGURATION.md) guide for details on installing and configuring `hostapd`, `dnsmasq`, setting a static IP, and enabling NAT. This setup is done on the Pi host, outside the Docker container.

---

## Installation & Setup

1. **Clone the Repository:**

   ```
   git clone https://github.com/ateames/Vinyl-Bot.git
   cd VinylBot
   ```

2. **Update Configuration:**
Copy `example.config.py` and rename to `config.py`:
```
cp example.config.py config.py
```

Edit `config.py` with your LastFM, AcoustID API credentials and MusicBrainz user agent.
```
LASTFM_API_KEY = "YOUR_LASTFM_API_KEY"
LASTFM_API_SECRET = "YOUR_LASTFM_API_SECRET"
ACOUSTID_API_KEY = "YOUR_ACOUSTID_API_KEY"

WIFI_SSID = "Vinyl-Bot"
WIFI_SECURITY = "WPA"
COUNTRY_CODE = "US"

MUSICBRAINZ_USER_AGENT = ("Vinyl-Bot", "1.0", "contact@example.com")
```

4. **Build & Run the Docker Container:**

   ```
   docker build -t vinyl-bot .
   docker run --rm --net=host --device /dev/snd vinyl-bot
   ```

5. **AP Mode & Kiosk Interface:**
   - Ensure your Raspberry Pi is running in AP mode. The device will broadcast the `Vinyl-Bot` SSID.
   - The kiosk interface will open automatically (via Chromium on the host, if configured) and display instructions for WiFi setup and LastFM login.

6. **Interacting with the Application:**
   - Use a mobile device to connect to the `Vinyl-Bot` WiFi.
   - Follow the on-screen instructions to configure your home/office WiFi and sign in to LastFM.
   - The application continuously captures audio, identifies tracks, displays current track metadata, and scrobbles new tracks to LastFM.

---

## Additional Considerations

- **Permissions & Device Access:**  
  The Docker container must have access to system devices (e.g., audio devices) and may require additional privileges. Adjust your Docker run command accordingly.

- **Kiosk Mode:**  
  The provided code automatically attempts to launch Chromium in kiosk mode. If running within Docker, you may need to disable this feature or configure the container to use the host’s display.

- **Error Handling & Logging:**  
  The application includes basic error handling. For production use, consider integrating a robust logging solution.

- **Security:**  
  Ensure secure handling of API keys and WiFi credentials. Secure your web endpoints (consider HTTPS) for production deployment.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
