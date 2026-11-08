"""Saves study images on disk: storage/studies/<id>/{original,mask,overlay}.png
Only integer ids are used in paths, so user input can never escape the folder."""
from pathlib import Path

from app.config import get_settings
from app.services.visuals import to_data_url

NAMES = ("original", "mask", "overlay")


def _dir(study_id: int) -> Path:
    return Path(get_settings().storage_dir) / "studies" / str(int(study_id))


def save_images(study_id: int, original: bytes, mask: bytes, overlay: bytes) -> None:
    d = _dir(study_id)
    d.mkdir(parents=True, exist_ok=True)
    (d / "original.png").write_bytes(original)
    (d / "mask.png").write_bytes(mask)
    (d / "overlay.png").write_bytes(overlay)


def load_data_urls(study_id: int) -> dict[str, str | None]:
    d = _dir(study_id)
    out: dict[str, str | None] = {}
    for n in NAMES:
        f = d / f"{n}.png"
        out[n] = to_data_url(f.read_bytes()) if f.exists() else None
    return out
