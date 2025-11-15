from __future__ import annotations

from pathlib import Path
from typing import Optional

from ..models import ForecastEntry, WeatherBundle


def choose_clothing_card(weather: WeatherBundle, assets_dir: Path) -> Optional[str]:
    current_temp = weather.current.temperature
    description = weather.current.description.lower()
    rain_probability = max((entry.precipitation_probability for entry in weather.next_hours), default=0.0)

    slug = "mild"
    if "rain" in description or rain_probability >= 0.5:
        slug = "rain"
    elif current_temp <= 45:
        slug = "cold"
    elif current_temp >= 85:
        slug = "hot"
    else:
        slug = "mild"

    card = assets_dir / f"{slug}.png"
    if card.exists():
        return str(card)
    return None
