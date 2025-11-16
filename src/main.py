from __future__ import annotations

import argparse
import logging
import subprocess
from datetime import datetime

from zoneinfo import ZoneInfo

from weatherdisplay.config import Settings
from weatherdisplay.hardware.display import DisplayDriver
from weatherdisplay.hardware.wittypi import WittyPiController
from weatherdisplay.models import BatteryStatus, RenderPayload
from weatherdisplay.render.clothing import choose_clothing_card
from weatherdisplay.render.layout import LayoutRenderer
from weatherdisplay.services.openweather import OpenWeatherClient, WeatherFetchError

LOGGER = logging.getLogger(__name__)


def configure_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)-8s %(name)s - %(message)s")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Weather display refresher")
    parser.add_argument("--env", default=".env", help="Path to .env file")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    return parser.parse_args()


def _should_request_shutdown(battery: BatteryStatus | None, cutoff: float) -> bool:
    if battery is None:
        return False
    if battery.is_external_power:
        return False
    return battery.output_voltage <= cutoff


def main() -> int:
    args = parse_args()
    configure_logging(args.verbose)

    settings = Settings.from_env(args.env)
    weather_client = OpenWeatherClient(settings)
    witty = WittyPiController(settings.witty_i2c_address)
    display = DisplayDriver(settings)
    renderer = LayoutRenderer(settings)

    try:
        weather = weather_client.fetch_bundle()
    except WeatherFetchError as exc:
        LOGGER.error("Weather fetch failed: %s", exc)
        return 2

    battery = witty.read_battery_status()
    if _should_request_shutdown(battery, settings.low_voltage_cutoff):
        LOGGER.warning(
            "Output voltage %.2fV below %.2fV threshold; requesting safe shutdown",
            battery.output_voltage if battery else 0.0,
            settings.low_voltage_cutoff,
        )
        subprocess.run(["sudo", "shutdown", "-h", "now", "Witty Pi battery low"], check=False)
        return 3
    clothing = choose_clothing_card(weather, settings.clothing_dir)

    tz = ZoneInfo(settings.timezone)
    payload = RenderPayload(
        weather=weather,
        battery=battery,
        clothing_image=clothing,
        last_updated=datetime.now(tz),
    )

    image = renderer.build(payload)
    display.show(image)
    LOGGER.info("Display updated successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
