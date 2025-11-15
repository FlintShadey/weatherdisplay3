from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional, Sequence

from PIL import Image, ImageDraw, ImageFont

from ..config import Settings
from ..models import BatteryStatus, ForecastEntry, RenderPayload, WeatherBundle
from ..utils.icon_font import MaterialIconFont

WIDTH, HEIGHT = 800, 480
LEFT_WIDTH = 400
RIGHT_WIDTH = 400
PADDING = 20


class LayoutRenderer:
    """Compose the 800×480 canvas for the e-paper display."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._time_font = ImageFont.truetype(str(settings.fonts["text"]), 68)
        self._data_font = ImageFont.truetype(str(settings.fonts["text"]), 32)
        self._mono_small = ImageFont.truetype(str(settings.fonts["text"]), 24)
        self._icon_font = MaterialIconFont(settings.fonts["icons"], settings.icon_codepoints)
        self._icon_face = ImageFont.truetype(str(settings.fonts["icons"]), 120)
        self._icon_small_face = ImageFont.truetype(str(settings.fonts["icons"]), 48)

    def build(self, payload: RenderPayload) -> Image.Image:
        canvas = Image.new("RGB", (WIDTH, HEIGHT), color=self._settings.color("white"))
        left = self._build_left(payload.weather, payload.battery, payload.last_updated)
        right = self._build_right(payload.clothing_image)
        canvas.paste(left, (0, 0))
        canvas.paste(right, (LEFT_WIDTH, 0))
        return canvas

    def _build_left(self, weather: WeatherBundle, battery: Optional[BatteryStatus], current_time: datetime) -> Image.Image:
        section = Image.new("RGB", (LEFT_WIDTH, HEIGHT), color=self._settings.color("white"))
        draw = ImageDraw.Draw(section)

        draw.text((PADDING, 18), current_time.strftime("%H:%M"), font=self._time_font, fill=self._settings.color("black"))
        draw.text((PADDING, 110), current_time.strftime("%a %b %d"), font=self._data_font, fill=self._settings.color("blue"))

        self._draw_battery(draw, battery)
        self._draw_current_weather(draw, weather)
        self._draw_forecast(draw, weather.next_hours)
        return section

    def _draw_battery(self, draw: ImageDraw.ImageDraw, battery: Optional[BatteryStatus]) -> None:
        top = (LEFT_WIDTH - 180, 24)
        bottom = (LEFT_WIDTH - 20, 84)
        outline = self._settings.color("black")
        draw.rectangle([top, bottom], outline=outline, width=3)
        nub = [(bottom[0], 40), (bottom[0] + 14, 68)]
        draw.rectangle(nub, fill=outline)

        if not battery:
            draw.text((top[0] + 12, top[1] + 6), "--%", font=self._data_font, fill=outline)
            return

        inner_width = bottom[0] - top[0] - 10
        pct = max(0, min(100, battery.percentage)) / 100
        filled = int(inner_width * pct)
        fill_color = self._settings.color("green" if pct > 0.4 else "red")
        draw.rectangle(
            (
                (top[0] + 5, top[1] + 5),
                (top[0] + 5 + filled, bottom[1] - 5),
            ),
            fill=fill_color,
        )
        draw.text((top[0] - 110, top[1] + 6), f"{battery.percentage:3d}%", font=self._data_font, fill=outline)

    def _draw_current_weather(self, draw: ImageDraw.ImageDraw, weather: WeatherBundle) -> None:
        current = weather.current
        icon = self._icon_font.glyph(current.icon_key)
        icon_color = current.icon_color
        draw.text((PADDING, 160), icon, font=self._icon_face, fill=icon_color)

        temp_text = f"{current.temperature:.0f}°"
        draw.text((PADDING + 150, 170), temp_text, font=self._data_font, fill=self._settings.color("black"))
        draw.text((PADDING + 150, 210), current.description, font=self._mono_small, fill=self._settings.color("blue"))

        feels = f"Feels {current.feels_like:.0f}°"
        humidity = f"Humidity {current.humidity}%"
        wind = f"Wind {current.wind_speed:.1f} mph"
        draw.text((PADDING, 310), feels, font=self._mono_small, fill=self._settings.color("black"))
        draw.text((PADDING, 340), humidity, font=self._mono_small, fill=self._settings.color("black"))
        draw.text((PADDING, 370), wind, font=self._mono_small, fill=self._settings.color("black"))

    def _draw_forecast(self, draw: ImageDraw.ImageDraw, forecast: Sequence[ForecastEntry]) -> None:
        start_y = 380
        if not forecast:
            return
        col_width = (LEFT_WIDTH - 2 * PADDING) // len(forecast)
        for idx, entry in enumerate(forecast):
            x = PADDING + idx * col_width
            hour_text = entry.timestamp.strftime("%H:%M")
            draw.text((x, start_y), hour_text, font=self._mono_small, fill=self._settings.color("blue"))
            glyph = self._icon_font.glyph(entry.icon_key)
            draw.text((x, start_y + 24), glyph, font=self._icon_small_face, fill=entry.icon_color)
            temp = f"{entry.temperature:.0f}°"
            draw.text((x, start_y + 80), temp, font=self._mono_small, fill=self._settings.color("black"))
            pop = f"{int(entry.precipitation_probability * 100)}%"
            draw.text((x, start_y + 110), pop, font=self._mono_small, fill=self._settings.color("blue"))

    def _build_right(self, clothing_path: Optional[str]) -> Image.Image:
        section = Image.new("RGB", (RIGHT_WIDTH, HEIGHT), color=self._settings.color("white"))
        if clothing_path:
            img_path = Path(clothing_path)
            if img_path.exists():
                card = Image.open(img_path).convert("RGB")
                section.paste(card.resize((RIGHT_WIDTH, HEIGHT)))
                return section
        # fallback
        draw = ImageDraw.Draw(section)
        draw.rectangle([(0, 0), (RIGHT_WIDTH - 1, HEIGHT - 1)], outline=self._settings.color("blue"), width=4)
        draw.text((PADDING, HEIGHT // 2 - 20), "No outfit data", font=self._data_font, fill=self._settings.color("blue"))
        return section
