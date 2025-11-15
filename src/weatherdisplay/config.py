from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Mapping

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"


@dataclass(slots=True)
class Settings:
    api_key: str
    latitude: float
    longitude: float
    units: str
    timezone: str
    update_interval_minutes: int
    display_driver: str
    mock_display: bool
    witty_i2c_address: int
    low_voltage_cutoff: float
    fonts: Dict[str, Path]
    icon_codepoints: Path
    icon_map: Mapping[str, Mapping[str, str]]
    clothing_dir: Path
    cache_dir: Path
    palette: Mapping[str, str] = field(
        default_factory=lambda: {
            "black": "#000000",
            "white": "#FFFFFF",
            "yellow": "#FFD800",
            "red": "#D0021B",
            "blue": "#0052CC",
            "green": "#0B8457",
        }
    )

    @classmethod
    def from_env(cls, env_path: str | os.PathLike[str] = ".env") -> "Settings":
        load_dotenv(env_path)
        api_key = os.environ.get("OPENWEATHER_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("OPENWEATHER_API_KEY missing in environment")

        latitude = float(os.environ.get("LOCATION_LAT", "0"))
        longitude = float(os.environ.get("LOCATION_LON", "0"))
        units = os.environ.get("UNITS", "imperial").lower()
        timezone = os.environ.get("TZ", "UTC")
        interval = int(os.environ.get("UPDATE_INTERVAL_MINUTES", "10"))
        display_driver = os.environ.get("DISPLAY_DRIVER", "waveshare_epd.epd7in3f")
        mock_display = os.environ.get("MOCK_DISPLAY", "0") not in {"0", "false", "False"}

        witty_addr_raw = os.environ.get("WITTY_PI_I2C_ADDRESS", "0x08")
        witty_addr = int(witty_addr_raw, 16) if witty_addr_raw.startswith("0x") else int(witty_addr_raw)

        fonts = {
            "text": ASSETS / "fonts" / "RobotoMono-Regular.ttf",
            "icons": ASSETS / "fonts" / "MaterialIconsOutlined-Regular.ttf",
        }
        for name, path in fonts.items():
            if not path.exists():
                raise FileNotFoundError(f"Font '{name}' expected at {path}")

        icon_map_path = ASSETS / "icons" / "weather_icon_map.json"
        icon_map = json.loads(icon_map_path.read_text())
        codepoints_path = ASSETS / "icons" / "material_icons_outlined.codepoints"
        if not codepoints_path.exists():
            raise FileNotFoundError(f"Missing Material icon codepoints file at {codepoints_path}")

        public_clothing = ROOT / "public" / "right-section"
        fallback_clothing = ASSETS / "clothing"
        public_clothing.mkdir(parents=True, exist_ok=True)
        fallback_clothing.mkdir(parents=True, exist_ok=True)
        has_public_assets = any(public_clothing.glob("*.png"))
        clothing_dir = public_clothing if has_public_assets else fallback_clothing

        cache_dir = ROOT / "var" / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)

        cutoff = float(os.environ.get("LOW_VOLTAGE_CUTOFF", "4.65"))

        return cls(
            api_key=api_key,
            latitude=latitude,
            longitude=longitude,
            units=units,
            timezone=timezone,
            update_interval_minutes=interval,
            display_driver=display_driver,
            mock_display=mock_display,
            witty_i2c_address=witty_addr,
            low_voltage_cutoff=cutoff,
            fonts=fonts,
            icon_codepoints=codepoints_path,
            icon_map=icon_map,
            clothing_dir=clothing_dir,
            cache_dir=cache_dir,
        )

    def color(self, key: str, fallback: str | None = None) -> str:
        if key in self.palette:
            return self.palette[key]
        if fallback:
            return fallback
        raise KeyError(key)
