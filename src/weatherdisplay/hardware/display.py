from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Optional

from PIL import Image

try:
    from waveshare_epd import epd7in3f
except ImportError:  # pragma: no cover - running off target hardware
    epd7in3f = None  # type: ignore

from ..config import Settings

LOGGER = logging.getLogger(__name__)


class DisplayDriver:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._cache_path = settings.cache_dir / "last_frame.png"
        self._hash_path = settings.cache_dir / "last_frame.sha1"
        self._mock = settings.mock_display or epd7in3f is None
        self._epd = None
        if not self._mock and epd7in3f is not None:
            self._epd = epd7in3f.EPD()
            self._epd.init()

    def show(self, image: Image.Image) -> None:
        checksum = hashlib.sha1(image.tobytes()).hexdigest()
        if self._hash_path.exists() and self._hash_path.read_text() == checksum:
            LOGGER.info("Display content unchanged; skipping refresh")
            return

        if self._mock:
            image.save(self._cache_path)
            self._hash_path.write_text(checksum)
            LOGGER.info("Mock display updated -> %s", self._cache_path)
            return

        if self._epd is None:
            LOGGER.error("Display driver unavailable")
            return

        LOGGER.info("Refreshing e-paper display")
        buffer = self._epd.getbuffer(image)
        self._epd.display(buffer)
        self._epd.sleep()
        image.save(self._cache_path)
        self._hash_path.write_text(checksum)

    def clear(self) -> None:
        if self._mock:
            if self._cache_path.exists():
                self._cache_path.unlink()
            if self._hash_path.exists():
                self._hash_path.unlink()
            return
        if self._epd is None:
            return
        self._epd.Clear()
        self._epd.sleep()
        if self._cache_path.exists():
            self._cache_path.unlink()
        if self._hash_path.exists():
            self._hash_path.unlink()
