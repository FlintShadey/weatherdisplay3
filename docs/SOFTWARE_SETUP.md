# Software Setup

This document complements the hardware guide by covering Wi-Fi provisioning, Witty Pi firmware installation, the Python stack, and the 10-minute refresh service.

## 1. Prepare Raspberry Pi OS Lite

1. Flash the latest Raspberry Pi OS Lite (Bookworm) onto a microSD card.
2. Before ejecting the SD card, create an empty `ssh` file in the boot partition to enable SSH on first boot.
3. Boot the Pi Zero 2 W with the Witty Pi installed but **without** the Waveshare display connected the first time.

## 2. Wi-Fi provisioning (2.4 GHz)

This project uses the `I haz interwebs 2.4` SSID (2.4 GHz) with the password `Flintis2`.

```bash
sudo tee /etc/wpa_supplicant/wpa_supplicant.conf >/dev/null <<'CONF'
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US

network={
    ssid="I haz interwebs 2.4"
    psk="Flintis2"
}
CONF
sudo rfkill unblock wifi
sudo wpa_cli -i wlan0 reconfigure
```

Verify connectivity with `ping -c4 api.openweathermap.org` once the firewall allows traffic.

## 3. Install Witty Pi software + UWI service

UUGear provides an installer that both configures the `daemon.sh` service and deploys the UWI (Witty Pi web interface) components. Run the commands directly on the Pi:

```bash
wget https://www.uugear.com/repo/WittyPi4/install.sh
sudo sh install.sh
```

The script registers the wittypi service so it runs after boot and issues the required permissions to talk to the MCU at I²C address `0x08`. After installation:

- `sudo ./wittypi.sh` brings up the interactive configuration utility.
- `i2cdetect -y 1` should still show `08`.
- The helper scripts live under `/home/pi/wittyPi` (`utilities.sh`, `daemon.sh`, etc.).

## 4. Clone this repository

```bash
cd /home/pi
git clone https://github.com/your-account/weatherdisplay3.git
cd weatherdisplay3
```

(Replace the URL with your actual remote.)

## 5. Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

The requirements pull in `requests`, `python-dotenv`, `smbus2`, and `Pillow`.

### Installing Waveshare e-Paper library

The Waveshare library must be installed separately due to repository checkout issues:

```bash
source .venv/bin/activate
./scripts/install_waveshare.sh
```

This script clones the Waveshare repository and installs only the Python package needed for the display.

## 6. Environment variables (`.env`)

Two files are provided:

- `.env` already contains the Wi-Fi SSID/password, the Austin, TX coordinates (`30.2578, -97.7432`), and the supplied OpenWeather API key (`13db313321d27c54d05b8e99968deb6d`).
- `.env.example` mirrors the keys so you can template another deployment.

Key entries:

| Key | Description |
| --- | --- |
| `OPENWEATHER_API_KEY` | API token for the One Call endpoint. |
| `LOCATION_LAT` / `LOCATION_LON` | Decimal GPS coordinates. |
| `TZ` | Olson timezone string (used for timestamps). |
| `UPDATE_INTERVAL_MINUTES` | Informational; used in documentation + timers. |
| `WITTY_PI_I2C_ADDRESS` | Defaults to `0x08`. Update if you ever change the MCU address via register `16`. |
| `LOW_VOLTAGE_CUTOFF` | Output voltage (in volts) at which the Python app issues `sudo shutdown -h now`. |
| `MOCK_DISPLAY` | `1` on dev machines to skip SPI writes and emit `var/cache/last_frame.png`. Set to `0` on the Pi. |

## 7. Manual test run

```bash
source .venv/bin/activate
MOCK_DISPLAY=1 python src/main.py --verbose
```

- The OpenWeather client hits `https://api.openweathermap.org/data/2.5/onecall` and downloads the current + hourly data (4 data points are rendered under the main panel).
- Witty Pi telemetry is read from registers `0–11`. If the bus is not present the app logs a warning and continues.
- The renderer saves the composed layout to `var/cache/last_frame.png` when `MOCK_DISPLAY=1`.
- When `MOCK_DISPLAY=0`, the `waveshare_epd.epd7in3f` driver pushes the buffer over SPI.

## 8. systemd service & timer

Copy the provided units and enable the timer:

```bash
sudo cp systemd/weatherdisplay.service /etc/systemd/system/
sudo cp systemd/weatherdisplay.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now weatherdisplay.timer
```

- If you installed the virtual environment somewhere else, edit `ExecStart` in `weatherdisplay.service` so it points at the correct Python interpreter.
- The timer kicks the oneshot service 2 minutes after boot and every 10 minutes afterwards (`OnUnitActiveSec=10min`).
- Logs are available via `journalctl -u weatherdisplay.service -f`.
- To test interactively: `sudo systemctl start weatherdisplay.service`.

## 9. Graceful degradation & troubleshooting

| Symptom | What to check |
| --- | --- |
| `Weather fetch failed` | Verify internet connectivity and confirm the API key has an active One Call subscription. Running `curl "https://api.openweathermap.org/data/2.5/onecall?lat=..."` should return JSON. |
| `smbus2 unavailable` | The Pi kernel must load `i2c-dev`. Run `sudo raspi-config` → *Interface Options* → *I2C* and reboot. |
| Auto-shutdown triggered immediately | Increase `LOW_VOLTAGE_CUTOFF` or verify that `battery.is_external_power` is `True` (USB power connected). |
| Display never updates after hardware failure | Delete `var/cache/last_frame.sha1` so the driver cannot think the content is unchanged. |

## 10. Updating assets

- Run `scripts/generate_clothing_cards.py` whenever you edit the palette or need new outfit combinations. The script enforces the six-color limit and now mirrors its output into `public/right-section/`, which is what the renderer reads first.
- Drop any hand-curated cards directly into `public/right-section/` (400×480 PNG). If that folder is empty the app falls back to `assets/clothing/`.
- Material Design icons are bundled as fonts; update `assets/fonts/MaterialIconsOutlined-Regular.ttf` + the `.codepoints` file if Google publishes a new revision.

With hardware and software configured, the Pi refreshes the panel every 10 minutes, displays current and short-term forecast data, shows battery state-of-charge, and automatically powers down if the Witty Pi reports a dangerously low rail voltage.
