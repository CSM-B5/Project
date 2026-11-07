"""Segmentation service.

!!! PLACEHOLDER MODEL !!!
`MockSegmenter` thresholds the brightest areas inside the central (lung) field
and labels connected blobs. It exists so the overlay feature works end-to-end.
Replace with Swin UNETR / nnU-Net / SegResMamba / a promptable VLSM
(see the PDFs in the repo) by implementing the same `segment()` signature.
"""
import base64
import io
from collections import deque
from functools import lru_cache

import numpy as np
from PIL import Image

OVERLAY_RGB = (244, 63, 94)  # #f43f5e
OVERLAY_HEX = "#f43f5e"
MAX_SIDE = 512


class SegmentationResult:
    def __init__(self, mask: np.ndarray, regions: int):
        self.mask = mask  # bool array (H, W) at mask resolution
        self.regions = regions


def _count_regions(mask: np.ndarray, min_area: int = 12) -> int:
    seen = np.zeros_like(mask, dtype=bool)
    h, w = mask.shape
    count = 0
    for y in range(h):
        for x in range(w):
            if mask[y, x] and not seen[y, x]:
                area, q = 0, deque([(y, x)])
                seen[y, x] = True
                while q:
                    cy, cx = q.popleft()
                    area += 1
                    for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            q.append((ny, nx))
                if area >= min_area:
                    count += 1
    return count


class MockSegmenter:
    def segment(self, image: Image.Image) -> SegmentationResult:
        small = image.convert("L").resize((128, 128))
        g = np.asarray(small, dtype="float32")
        field = np.zeros_like(g, dtype=bool)
        field[24:104, 20:108] = True  # rough lung field
        vals = g[field]
        thr = np.percentile(vals, 92)
        mask = (g >= thr) & field
        return SegmentationResult(mask, _count_regions(mask))

    @staticmethod
    def to_overlay_data_url(result: SegmentationResult, size: tuple[int, int]) -> str:
        """Transparent RGBA PNG with the mask in the overlay colour."""
        w, h = size
        scale = min(1.0, MAX_SIDE / max(w, h))
        out_size = (max(1, int(w * scale)), max(1, int(h * scale)))
        m = Image.fromarray((result.mask * 255).astype("uint8")).resize(
            out_size, Image.NEAREST
        )
        m = np.asarray(m) > 0
        rgba = np.zeros((out_size[1], out_size[0], 4), dtype="uint8")
        rgba[m] = (*OVERLAY_RGB, 120)
        buf = io.BytesIO()
        Image.fromarray(rgba, "RGBA").save(buf, format="PNG")
        return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


@lru_cache
def get_segmenter() -> MockSegmenter:
    return MockSegmenter()  # <- swap in your real model here
