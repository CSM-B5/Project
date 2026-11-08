"""Brain-tumour classification service.

!!! PLACEHOLDER MODEL !!!
`MockClassifier` derives a deterministic pseudo-prediction from image
statistics so the whole pipeline (API -> UI) works end-to-end today.
It is NOT a diagnostic model.

To plug in the real model (CNN / VGG ...):
  1. Create a class with `predict(image: PIL.Image.Image) -> ClassificationResult`.
  2. Return it from `get_classifier()` below.
  (Keep the class names in CLASSES — the frontend and database use them.)
"""
from dataclasses import dataclass
from functools import lru_cache

import numpy as np
from PIL import Image

CLASSES = ["Glioma", "Meningioma", "Pituitary", "No Tumor"]
NO_TUMOR = "No Tumor"


@dataclass
class ClassificationResult:
    predicted_class: str
    probabilities: dict[str, float]  # percent, sums to 100


class MockClassifier:
    def predict(self, image: Image.Image) -> ClassificationResult:
        g = np.asarray(image.convert("L").resize((64, 64)), dtype="float32") / 255.0
        seed = int(g.mean() * 1e6) + int(g.std() * 1e6) * 7
        rng = np.random.default_rng(seed)
        logits = rng.normal(size=len(CLASSES)) * 1.4
        probs = np.exp(logits) / np.exp(logits).sum() * 100
        rounded = [round(float(p), 1) for p in probs]
        top = int(np.argmax(rounded))
        rounded[top] = round(rounded[top] + (100.0 - sum(rounded)), 1)  # make it sum to 100
        return ClassificationResult(CLASSES[top], dict(zip(CLASSES, rounded)))


@lru_cache
def get_classifier() -> MockClassifier:
    return MockClassifier()  # <- swap in your real model here
