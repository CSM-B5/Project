"""Classification service.

!!! PLACEHOLDER MODEL !!!
`MockClassifier` derives a deterministic pseudo-prediction from image
statistics so the whole pipeline (API -> UI) works end-to-end today.
It is NOT a diagnostic model.

To plug in the real model (CLIP/LLaVA-style VLM, ResNet, Swin, ...):
  1. Create a class with a `predict(self, image: PIL.Image.Image) -> Classification`
     method (see MockClassifier for the expected output).
  2. Return it from `get_classifier()` below.
"""
from functools import lru_cache

import numpy as np
from PIL import Image

from app.schemas import Classification

LABELS = ["Pneumonia", "Normal Variant", "Pleural Effusion", "Cardiomegaly"]
REGIONS = ["Left Lower Lobe", "Right Lower Lobe", "Left Upper Lobe", "Right Upper Lobe"]


class MockClassifier:
    def predict(self, image: Image.Image) -> Classification:
        g = np.asarray(image.convert("L").resize((64, 64)), dtype="float32") / 255.0
        # seed from content so same image -> same answer
        seed = int(g.mean() * 1e6) + int(g.std() * 1e6)
        rng = np.random.default_rng(seed)
        logits = rng.normal(size=len(LABELS)) + np.array([1.0, 0.6, 0.0, -0.2])
        probs = np.exp(logits) / np.exp(logits).sum()
        order = np.argsort(probs)[::-1]
        top, second = order[0], order[1]
        # report as a two-class style summary like the UI expects (sums to 100)
        total = probs[top] + probs[second]
        primary = round(float(probs[top] / total * 100), 1)
        return Classification(
            primaryLabel=LABELS[top],
            confidenceScore=primary,
            secondaryLabel=LABELS[second],
            secondaryScore=round(100 - primary, 1),
            anatomicalTarget=REGIONS[int(rng.integers(len(REGIONS)))],
        )


@lru_cache
def get_classifier() -> MockClassifier:
    return MockClassifier()  # <- swap in your real model here
