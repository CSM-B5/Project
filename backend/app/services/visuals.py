"""Turn images/masks into PNG bytes for storage and data URLs for the frontend."""
import base64
import io

import numpy as np
from PIL import Image

MAX_SIDE = 512


def prepare_original(image: Image.Image) -> Image.Image:
    """Copy of the scan, shrunk so its longest side is <= 512 px."""
    img = image.convert("RGB")
    scale = min(1.0, MAX_SIDE / max(img.size))
    if scale < 1.0:
        img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))))
    return img


def upscale_mask(mask: np.ndarray, size: tuple[int, int]) -> np.ndarray:
    """bool mask (any size) -> bool mask of PIL `size` (w, h)."""
    m = Image.fromarray((mask * 255).astype("uint8")).resize(size, Image.NEAREST)
    return np.asarray(m) > 0


def mask_png(mask: np.ndarray) -> bytes:
    buf = io.BytesIO()
    Image.fromarray((mask * 255).astype("uint8"), "L").save(buf, format="PNG")
    return buf.getvalue()


def overlay_png(original: Image.Image, mask: np.ndarray, color=(244, 63, 94), alpha=0.45) -> bytes:
    arr = np.asarray(original.convert("RGB"), dtype="float32").copy()
    if mask.any():
        arr[mask] = arr[mask] * (1 - alpha) + np.array(color, dtype="float32") * alpha
    buf = io.BytesIO()
    Image.fromarray(arr.astype("uint8"), "RGB").save(buf, format="PNG")
    return buf.getvalue()


def image_png(image: Image.Image) -> bytes:
    buf = io.BytesIO()
    image.convert("RGB").save(buf, format="PNG")
    return buf.getvalue()


def to_data_url(png_bytes: bytes) -> str:
    return "data:image/png;base64," + base64.b64encode(png_bytes).decode()
