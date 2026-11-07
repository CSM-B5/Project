"""Load PNG / JPG / DICOM uploads into a PIL image."""
import io

from fastapi import HTTPException
from PIL import Image, UnidentifiedImageError

ALLOWED_EXT = {".png", ".jpg", ".jpeg", ".dcm"}


def load_scan(filename: str, data: bytes) -> tuple[Image.Image, str]:
    """Returns (RGB image, human readable scan type)."""
    name = (filename or "").lower()
    ext = "." + name.rsplit(".", 1)[-1] if "." in name else ""
    if ext not in ALLOWED_EXT:
        raise HTTPException(
            415, f"Unsupported file type '{ext}'. Use PNG, JPG or DICOM (.dcm)."
        )

    if ext == ".dcm":
        return _load_dicom(data)

    try:
        img = Image.open(io.BytesIO(data))
        img.load()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(400, "File is not a valid image.")
    return img.convert("RGB"), "Chest X-Ray"


def _load_dicom(data: bytes) -> tuple[Image.Image, str]:
    import numpy as np
    import pydicom

    try:
        ds = pydicom.dcmread(io.BytesIO(data), force=True)
        arr = ds.pixel_array.astype("float32")
    except Exception:
        raise HTTPException(400, "Could not read DICOM pixel data.")

    if arr.ndim == 3:  # multi-frame / colour -> take the first slice
        arr = arr[0] if arr.shape[-1] not in (3, 4) else arr.mean(axis=-1)
    lo, hi = np.percentile(arr, [1, 99])
    arr = np.clip((arr - lo) / max(hi - lo, 1e-6), 0, 1)
    if getattr(ds, "PhotometricInterpretation", "") == "MONOCHROME1":
        arr = 1 - arr
    img = Image.fromarray((arr * 255).astype("uint8")).convert("RGB")
    modality = getattr(ds, "Modality", "") or "Scan"
    return img, f"DICOM ({modality})"
