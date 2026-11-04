"""Evaluation: Qini, AUUC, bootstrap confidence intervals, uplift by decile.

Stage 3. These functions only read the scores file in results/. They never fit
a model.
"""
import numpy as np


def qini_curve(y, treatment, score):
    """Cumulative incremental outcomes when targeting rows in order of score."""
    raise NotImplementedError


def auuc(y, treatment, score) -> float:
    """Area under the uplift curve."""
    raise NotImplementedError


def bootstrap_ci(metric, y, treatment, score, n_boot: int = 200, seed: int = 42):
    """Confidence interval for a metric by resampling rows."""
    raise NotImplementedError


def uplift_by_decile(y, treatment, score) -> np.ndarray:
    """Observed uplift in each decile of predicted uplift."""
    raise NotImplementedError
