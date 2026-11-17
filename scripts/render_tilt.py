"""Кадри, де горщик нахилений до камери. Той самий масштаб, що assets/pots.

Flet не крутить сітку, тож нахил — це справжній рендер моделі.
Запуск: python3 scripts/render_tilt.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_pots import OUT, SRC, SKIP, WIDTH, _prepare, _raster  # noqa: E402

TILT_OUT = OUT / "tilt"
ANGLES = tuple(range(1, 46))


def _stems() -> list[str]:
    """Усі етапи культур, для яких є і GLB, і звичайний PNG."""
    stems: list[str] = []
    for path in sorted(SRC.glob("*.glb")):
        if path.stem in SKIP:
            continue
        if not (OUT / f"{path.stem}.png").exists():
            continue
        stems.append(path.stem)
    return stems


def _tilt(points: np.ndarray, normals: np.ndarray, degrees: float) -> tuple[np.ndarray, np.ndarray]:
    """Верх горщика йде до камери, дно лишається на місці."""
    angle = np.deg2rad(degrees)
    cosine, sine = np.cos(angle), np.sin(angle)
    rotation = np.array([[1, 0, 0], [0, cosine, -sine], [0, sine, cosine]], dtype=np.float32)
    bottom = float(points[:, :, 1].min())
    moved = points.copy()
    moved[:, :, 1] -= bottom
    moved = moved @ rotation.T
    moved[:, :, 1] += bottom
    return moved, normals @ rotation.T


def main() -> None:
    TILT_OUT.mkdir(parents=True, exist_ok=True)
    sample = next(OUT.glob("cute_pea_stage1.png"))
    height = Image.open(sample).size[1]
    stems = _stems()
    for stem in stems:
        path = SRC / f"{stem}.glb"
        points, lit, span, pot_x, _h = _prepare(path)
        for degrees in ANGLES:
            destination = TILT_OUT / f"{stem}_{degrees}.png"
            if destination.exists():
                continue
            tilted, _normals = _tilt(points, lit, degrees)
            image = _raster(tilted, lit, span, pot_x, height)
            Image.fromarray((np.clip(image, 0, 1) * 255).astype(np.uint8), "RGBA").save(destination)
            print(destination.name)
        print(f"готово {stem}")
    print(f"{len(stems)} моделей, кадри в {TILT_OUT}")


if __name__ == "__main__":
    main()
