"""Tumour segmentation service.

!!! PLACEHOLDER MODEL !!!
`MockSegmenter` thresholds the brightest pixels in the central brain area and
labels connected blobs. Replace with U-Net++ (or any model) by implementing
the same `segment()` signature and returning it from `get_segmenter()`.
"""
from collections import deque
from dataclasses import dataclass
from functools import lru_cache

import numpy as np
from PIL import Image, ImageFilter


@dataclass
class SegmentationResult:
    mask: np.ndarray  # bool (H, W) at working resolution
    regions: int
    area_percent: float


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
    SIZE = 128

    def segment(self, image: Image.Image, tumor_expected: bool = True) -> SegmentationResult:
        n = self.SIZE
        if not tumor_expected:  # classifier said "No Tumor" -> nothing to outline
            return SegmentationResult(np.zeros((n, n), dtype=bool), 0, 0.0)
        small = image.convert("L").resize((n, n)).filter(ImageFilter.GaussianBlur(2))  # smooth -> coherent blobs
        g = np.asarray(small, dtype="float32")
        field = np.zeros_like(g, dtype=bool)
        field[20:108, 20:108] = True  # central brain area
        thr = np.percentile(g[field], 93)
        mask = (g > thr) & field
        regions = _count_regions(mask)
        if regions == 0:
            mask = np.zeros_like(mask)
        return SegmentationResult(mask, regions, round(float(mask.mean() * 100), 2))


@lru_cache
def get_segmenter() -> MockSegmenter:
    return MockSegmenter()  # <- swap in your real model here
