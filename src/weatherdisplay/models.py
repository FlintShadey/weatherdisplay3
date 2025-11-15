from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Sequence


@dataclass(slots=True)
class WeatherSnapshot:
    timestamp: datetime
    temperature: float
    feels_like: float
    humidity: int
    wind_speed: float
    wind_gust: Optional[float]
    condition_code: int
    condition_label: str
    description: str
    icon_key: str
    icon_color: str


@dataclass(slots=True)
class ForecastEntry:
    timestamp: datetime
    temperature: float
    precipitation_probability: float
    icon_key: str
    icon_color: str
    description: str


@dataclass(slots=True)
class WeatherBundle:
    current: WeatherSnapshot
    next_hours: Sequence[ForecastEntry]


@dataclass(slots=True)
class BatteryStatus:
    input_voltage: float
    output_voltage: float
    output_current: float
    is_external_power: bool
    is_low_voltage_shutdown: bool
    last_action_code: int

    @property
    def percentage(self) -> int:
        # Rough guess using 4.8-5.2V range for USB supply.
        span = 5.2 - 4.6
        pct = max(0.0, min(1.0, (self.output_voltage - 4.6) / span))
        return int(round(pct * 100))


@dataclass(slots=True)
class RenderPayload:
    weather: WeatherBundle
    battery: Optional[BatteryStatus]
    clothing_image: Optional[str]
    last_updated: datetime
