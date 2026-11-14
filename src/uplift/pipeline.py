"""Glue between the data and the learners: feature cut, tuning, scores file.

Used by notebooks 02 and 03. The notebooks explain each step, and this module
holds the code so every notebook runs the same thing.

Scores file contract: one row per held out user, with the real treatment and
outcomes, and one column per model and outcome named {model}_{outcome}, where
model is response, s, t or x. Models write it, evaluation only reads it.
"""
import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.metrics import log_loss
from sklearn.model_selection import StratifiedKFold

from .data import OUTCOMES, TREATMENT, take
from .learners import BASE_PARAMS, SLearner, TLearner, XLearner, _prob

MODELS = ["response", "s", "t", "x"]


def select_features(train: pd.DataFrame, features: list, n_keep: int = 10, outcome: str = "visit",
                    n_rows: int = 500_000, seed: int = 42):
    """Cut features down to n_keep using importance, then check correlation. Training rows only.

    Fit a response model and drop the features with the lowest importance. For
    each dropped feature, also record its strongest correlation with a kept
    feature, to show whether the information is duplicated elsewhere. Returns
    the kept list, a log of each drop, and the importances.
    """
    s = train.sample(min(n_rows, len(train)), random_state=seed)
    corr = s[features].corr().abs()
    model = LGBMClassifier(**BASE_PARAMS).fit(s[features], s[outcome])
    gain = model.booster_.feature_importance("gain")
    importance = pd.Series(gain / gain.sum(), index=features, name="importance")
    kept, log = list(features), []
    while len(kept) > n_keep:
        drop = importance[kept].idxmin()
        kept.remove(drop)
        partner = corr.loc[drop, kept].idxmax()
        log.append(dict(dropped=drop, importance=importance[drop], most_similar_kept=partner,
                        abs_corr_with_it=corr.loc[drop, partner]))
    return kept, pd.DataFrame(log), importance


GRID = [
    dict(num_leaves=15, learning_rate=0.05, n_estimators=200, min_child_samples=200),
    dict(num_leaves=15, learning_rate=0.05, n_estimators=400, min_child_samples=200),
    dict(num_leaves=31, learning_rate=0.05, n_estimators=300, min_child_samples=100),
    dict(num_leaves=31, learning_rate=0.03, n_estimators=500, min_child_samples=300),
    dict(num_leaves=63, learning_rate=0.03, n_estimators=400, min_child_samples=300),
    dict(num_leaves=63, learning_rate=0.02, n_estimators=600, min_child_samples=500),
]


def tune_base(train: pd.DataFrame, features: list, outcome: str, grid: list = GRID,
              n_rows: int = 300_000, folds: int = 3, seed: int = 42):
    """Pick one set of LightGBM settings with cross validation on training rows only.

    The same small grid is tried for every outcome, scored by log loss on a
    model that sees the features and the treatment. The winner is then used by
    every learner, so tuning effort is identical across models.
    """
    s = train.sample(min(n_rows, len(train)), random_state=seed)
    X, y = s[features].assign(treatment=s[TREATMENT].to_numpy()), s[outcome].to_numpy()
    cv = StratifiedKFold(folds, shuffle=True, random_state=seed)
    rows = []
    for cfg in grid:
        losses = []
        for tr, va in cv.split(X, y):
            m = LGBMClassifier(**{**BASE_PARAMS, **cfg}).fit(X.iloc[tr], y[tr])
            losses.append(log_loss(y[va], _prob(m, X.iloc[va])))
        rows.append({**cfg, "cv_logloss": float(np.mean(losses))})
    table = pd.DataFrame(rows)
    best = table.loc[table["cv_logloss"].idxmin()].drop("cv_logloss").to_dict()
    best = {k: int(v) if k != "learning_rate" else float(v) for k, v in best.items()}
    return best, table


def fit_and_score(train: pd.DataFrame, test: pd.DataFrame, features: list, outcome: str, params: dict) -> dict:
    """Fit the response baseline and the S, T and X learners. Score the test rows."""
    X, t, y, Xte = train[features], train[TREATMENT], train[outcome], test[features]
    out = {"response": _prob(LGBMClassifier(**{**BASE_PARAMS, **params}).fit(X, y), Xte)}  # ignores treatment
    for name, cls in (("s", SLearner), ("t", TLearner), ("x", XLearner)):
        out[name] = cls(params).fit(X, t, y).predict_uplift(Xte)
    return out


def build_scores(df: pd.DataFrame, train_ids, test_ids, features: list, params: dict, outcomes=OUTCOMES) -> pd.DataFrame:
    """The scores file: held out users with one score column per model and outcome."""
    train, test = take(df, train_ids), take(df, test_ids)
    scores = test[[TREATMENT] + list(OUTCOMES)].copy()
    for outcome in outcomes:
        p = params[outcome] if outcome in params else params
        for model, values in fit_and_score(train, test, features, outcome, p).items():
            scores[f"{model}_{outcome}"] = values.astype("float32")
    return scores
