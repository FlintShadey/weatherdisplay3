from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Mapping, Sequence

import requests
from zoneinfo import ZoneInfo

from ..config import Settings
from ..models import ForecastEntry, WeatherBundle, WeatherSnapshot

LOGGER = logging.getLogger(__name__)
API_URL = "https://api.openweathermap.org/data/2.5/onecall"


class WeatherFetchError(RuntimeError):
    pass


@dataclass(slots=True)
class IconResolver:
    icon_map: Mapping[str, Mapping[str, str]]

    def resolve(self, condition_code: int, descriptor: str, is_daytime: bool) -> tuple[str, str]:
        """Return material icon name + accent color for the given condition."""
        family = self._family_from_code(condition_code, descriptor)
        if family == "clear":
            key = "clear-day" if is_daytime else "clear-night"
        elif family == "few-clouds":
            key = "few-clouds"
        elif family == "clouds":
            key = "clouds"
        else:
            key = family

        icon = self.icon_map.get(key)
        if not icon:
            icon = self.icon_map.get("clouds", {"icon": "cloud", "accent": "#0052CC"})
        return icon["icon"], icon["accent"]

    @staticmethod
    def _family_from_code(condition_code: int, descriptor: str) -> str:
        if 200 <= condition_code < 300:
            return "thunderstorm"
        if 300 <= condition_code < 400:
            return "drizzle"
        if 500 <= condition_code < 600:
            return "rain"
        if 600 <= condition_code < 700:
            return "snow"
        if 700 <= condition_code < 800:
            return descriptor.lower()
        if condition_code == 800:
            return "clear"
        if condition_code == 801:
            return "few-clouds"
        return "clouds"


class OpenWeatherClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._session = requests.Session()
        self._icons = IconResolver(settings.icon_map)

    def fetch_bundle(self) -> WeatherBundle:
        params = {
            "lat": self._settings.latitude,
            "lon": self._settings.longitude,
            "appid": self._settings.api_key,
            "units": self._settings.units,
            "exclude": "minutely,daily,alerts",
        }
        try:
            resp = self._session.get(API_URL, params=params, timeout=12)
            resp.raise_for_status()
            payload = resp.json()
        except requests.RequestException as exc:
            raise WeatherFetchError("Unable to reach OpenWeatherMap") from exc

        tz = ZoneInfo(self._settings.timezone)
        current_block = payload["current"]
        weather_meta = current_block["weather"][0]
        now = datetime.fromtimestamp(current_block["dt"], tz)
        is_day = current_block.get("sunrise", 0) <= current_block["dt"] <= current_block.get("sunset", 0)
        icon_name, icon_color = self._icons.resolve(weather_meta["id"], weather_meta["main"], is_day)

        current = WeatherSnapshot(
            timestamp=now,
            temperature=current_block["temp"],
            feels_like=current_block.get("feels_like", current_block["temp"]),
            humidity=current_block.get("humidity", 0),
            wind_speed=current_block.get("wind_speed", 0.0),
            wind_gust=current_block.get("wind_gust"),
            condition_code=weather_meta["id"],
            condition_label=weather_meta["main"],
            description=weather_meta.get("description", "").title(),
            icon_key=icon_name,
            icon_color=icon_color,
        )

        forecast = self._parse_hourly(payload.get("hourly", []), tz, limit=4)
        return WeatherBundle(current=current, next_hours=forecast)

    def _parse_hourly(self, data: Sequence[Mapping[str, object]], tz: ZoneInfo, limit: int) -> list[ForecastEntry]:
        entries: list[ForecastEntry] = []
        cursor = list(data)[1 : limit + 1] if len(data) > 1 else data[:limit]
        for block in cursor:
            weather_list = block.get("weather") or []
            descriptor = weather_list[0].get("main", "Clouds") if weather_list else "Clouds"
            icon_name, icon_color = self._icons.resolve(int(weather_list[0]["id"]) if weather_list else 802, descriptor, True)
            entries.append(
                ForecastEntry(
                    timestamp=datetime.fromtimestamp(int(block["dt"]), tz),
                    temperature=float(block.get("temp", 0.0)),
                    precipitation_probability=float(block.get("pop", 0.0)),
                    icon_key=icon_name,
                    icon_color=icon_color,
                    description=descriptor,
                )
            )
        return entries
