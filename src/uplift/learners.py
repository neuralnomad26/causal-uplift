"""S, T and X learners behind one interface.

Stage 2. Every learner offers the same two methods so the evaluation code never
needs to know which model it is scoring:

    fit(X, treatment, y)
    predict_uplift(X)  ->  one uplift score per row, higher means more persuadable

All three use the same LightGBM settings for the outcome model, so any
difference between them comes from the strategy and not from tuning luck.
Reference: Kunzel et al. (2019), Metalearners for Estimating Heterogeneous
Treatment Effects Using Machine Learning, PNAS.
"""
import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier, LGBMRegressor

BASE_PARAMS = dict(
    n_estimators=300,
    learning_rate=0.05,
    num_leaves=31,
    min_child_samples=100,
    subsample=0.8,
    subsample_freq=1,
    colsample_bytree=0.8,
    random_state=42,
    n_jobs=-1,
    verbose=-1,
)


def _prob(model, X) -> np.ndarray:
    """Probability of the outcome being 1."""
    return model.predict_proba(X)[:, 1]


class UpliftModel:
    """Shared interface for all uplift learners."""

    def __init__(self, params: dict | None = None):
        self.params = {**BASE_PARAMS, **(params or {})}

    def fit(self, X: pd.DataFrame, treatment: pd.Series, y: pd.Series) -> "UpliftModel":
        raise NotImplementedError

    def predict_uplift(self, X: pd.DataFrame) -> np.ndarray:
        raise NotImplementedError


class SLearner(UpliftModel):
    """One model with treatment as an input. The effect is the prediction gap.

    Score for a row = P(y=1 | x, treated) - P(y=1 | x, not treated), both read
    from the same model. Simple, but a tree model can ignore the treatment
    column when the effect is small.
    """

    def fit(self, X, treatment, y):
        self.model_ = LGBMClassifier(**self.params).fit(X.assign(treatment=np.asarray(treatment)), y)
        return self

    def predict_uplift(self, X):
        return _prob(self.model_, X.assign(treatment=1)) - _prob(self.model_, X.assign(treatment=0))


class TLearner(UpliftModel):
    """One model for treated, one for control, then subtract."""

    def fit(self, X, treatment, y):
        t = np.asarray(treatment) == 1
        y = np.asarray(y)
        self.mu1_ = LGBMClassifier(**self.params).fit(X[t], y[t])
        self.mu0_ = LGBMClassifier(**self.params).fit(X[~t], y[~t])
        return self

    def predict_uplift(self, X):
        return _prob(self.mu1_, X) - _prob(self.mu0_, X)


class XLearner(UpliftModel):
    """Impute individual effects, then weight using the 85/15 treatment share.

    Stage 1: fit the two outcome models mu1 (treated) and mu0 (control), as in
    the T-learner.
    Stage 2: for treated users the imputed effect is y - mu0(x). For control
    users it is mu1(x) - y. Fit one regressor on each set of imputed effects.
    Stage 3: blend the two effect models with the propensity g = P(treated):
    tau(x) = g * tau0(x) + (1 - g) * tau1(x). Treatment was randomized, so g is
    just the treated share, about 0.85. tau0 is built from mu1, which was
    learned from the large treated group and is the more accurate model, so
    tau0 gets the larger weight. This is why the X-learner suits unbalanced
    groups like ours.
    """

    def __init__(self, params: dict | None = None, effect_params: dict | None = None):
        super().__init__(params)
        # imputed effects are very noisy targets, so the effect models are kept simple
        self.effect_params = {**self.params, "num_leaves": 15, "min_child_samples": 500, **(effect_params or {})}

    def fit(self, X, treatment, y):
        t = np.asarray(treatment) == 1
        y = np.asarray(y)
        Xt, Xc = X[t], X[~t]
        self.mu1_ = LGBMClassifier(**self.params).fit(Xt, y[t])
        self.mu0_ = LGBMClassifier(**self.params).fit(Xc, y[~t])
        d1 = y[t] - _prob(self.mu0_, Xt)    # imputed effect for treated users
        d0 = _prob(self.mu1_, Xc) - y[~t]   # imputed effect for control users
        self.tau1_ = LGBMRegressor(**self.effect_params).fit(Xt, d1)
        self.tau0_ = LGBMRegressor(**self.effect_params).fit(Xc, d0)
        self.g_ = float(t.mean())
        return self

    def predict_uplift(self, X):
        return self.g_ * self.tau0_.predict(X) + (1 - self.g_) * self.tau1_.predict(X)
