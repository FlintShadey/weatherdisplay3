from __future__ import annotations

from pathlib import Path
from typing import Dict


class MaterialIconFont:
    def __init__(self, font_path: Path, codepoints_path: Path) -> None:
        self.font_path = font_path
        self.codepoints_path = codepoints_path
        self._glyphs = self._load_codepoints(codepoints_path)

    @staticmethod
    def _load_codepoints(path: Path) -> Dict[str, str]:
        mapping: Dict[str, str] = {}
        for line in path.read_text().splitlines():
            if not line or line.startswith("#"):
                continue
            name, code = line.split()
            mapping[name] = chr(int(code, 16))
        return mapping

    def glyph(self, name: str) -> str:
        try:
            return self._glyphs[name]
        except KeyError as exc:
            raise KeyError(f"Unknown Material icon: {name}") from exc
