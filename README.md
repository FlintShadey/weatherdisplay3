# Weatherdisplay3

A Raspberry Pi Zero 2 W based 7.3" Waveshare e-paper dashboard that combines Witty Pi 4 L3V7 power management, OpenWeatherMap intelligence, and clothing recommendations that use the limited six-color palette of the display.

## Highlights

- **OpenWeatherMap current + 4-hour forecast** rendered with Material Design icons and localized timestamps.
- **Smart power guard** pulled from the Witty Pi I²C registers (0x08) with automatic shutdown if the output rail drops below the configurable threshold.
- **Right-panel clothing cards** (400×480 PNGs) stored in `public/right-section/` so you can swap outfits without touching the code; regenerate the defaults with `scripts/generate_clothing_cards.py`.
- **10-minute refresh cadence** managed by a `systemd` timer and cached frame hashes to avoid unnecessary full updates.
- **Graceful degradation**: mock display output saved under `var/cache/` when the Waveshare driver or smbus is unavailable.

## Repository layout

```
assets/               Fonts, Material icon mapping, source clothing art
  fonts/              Roboto Mono + Material Icons Outlined
  clothing/           Palette-friendly card templates (mirrored to `public/right-section/`)
  icons/              Icon metadata + codepoints
public/right-section/ Final 400×480 PNGs rendered on the right-hand panel
src/
  main.py             Entry point (reads .env, refreshes display)
  weatherdisplay/     Package with services, renderers, and hardware adapters
scripts/              Utilities (e.g., clothing card generator)
systemd/              Service + timer unit files (10-minute refresh)
docs/                 HARDWARE_SETUP and SOFTWARE_SETUP guides
```

## Quick start

1. Copy `.env.example` to `.env` and fill in your Wi-Fi and OpenWeather credentials (the provided `.env` contains the Austin, TX coordinates and sample secrets from the brief).
2. Install dependencies (ideally inside a venv) and run the refresh manually:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   python src/main.py --verbose
   ```

3. When running on the Pi with the e-paper connected, set `MOCK_DISPLAY=0` in the `.env` file. For local dry runs keep it at `1` and inspect `var/cache/last_frame.png` to review the rendered layout.
4. Deploy the systemd units once everything looks correct (documented in `docs/SOFTWARE_SETUP.md`).

Need to refresh the outfit art? Drop new 400×480 PNGs (named however you like) into `public/right-section/` and the renderer will pick them up on the next run. The generator script mirrors its output there automatically.

## Documentation

- `docs/HARDWARE_SETUP.md` – wiring plans for the Pi Zero 2 W + Witty Pi 4 stack, display connections, and battery notes.
- `docs/SOFTWARE_SETUP.md` – installing Witty Pi support software, Wi-Fi provisioning, Python runtime, service installation, and troubleshooting.
- `THIRD_PARTY.md` – license references for bundled fonts.
