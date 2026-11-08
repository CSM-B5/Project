import numpy as np


def dice_iou(pred: np.ndarray, truth: np.ndarray) -> tuple[float, float]:
    """Overlap between predicted and ground-truth masks (both bool, same shape)."""
    inter = float(np.logical_and(pred, truth).sum())
    p, t = float(pred.sum()), float(truth.sum())
    union = p + t - inter
    if p + t == 0:  # both empty -> perfect agreement
        return 1.0, 1.0
    return round(2 * inter / (p + t), 4), round(inter / union, 4)
