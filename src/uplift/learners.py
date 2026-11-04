"""S, T and X learners behind one interface.

Stage 2. Every learner offers the same two methods so the evaluation code never
needs to know which model it is scoring:

    fit(X, treatment, y)
    predict_uplift(X)  ->  one uplift score per row, higher means more persuadable
"""
import numpy as np
import pandas as pd


class UpliftModel:
    """Shared interface for all uplift learners."""

    def fit(self, X: pd.DataFrame, treatment: pd.Series, y: pd.Series) -> "UpliftModel":
        raise NotImplementedError

    def predict_uplift(self, X: pd.DataFrame) -> np.ndarray:
        raise NotImplementedError


class SLearner(UpliftModel):
    """One model with treatment as an input. The effect is the prediction gap."""


class TLearner(UpliftModel):
    """One model for treated, one for control, then subtract."""


class XLearner(UpliftModel):
    """Impute individual effects, then weight using the 85/15 treatment share."""
