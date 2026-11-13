"""Evaluation: Qini, AUUC, bootstrap confidence intervals, uplift by decile.

Stage 3. These functions only read scores. They never fit a model.

Qini idea. Sort users from highest to lowest score. For the top i users, the
extra outcomes caused by treatment are estimated as

    Q(i) = i * (outcome rate of treated users in top i - outcome rate of control users in top i)

Using rates means the 85/15 split does not matter. Q(N) over everyone is the
average treatment effect times N. A random ordering gives a straight line from
0 to Q(N), so a model is useful only if its curve bends above that line.
This is the population scaled form of the Qini curve. Reference: Radcliffe
(2007), Using Control Groups to Target on Predicted Lift.
"""
import numpy as np
import pandas as pd
from joblib import Parallel, delayed


def _as_arrays(y, treatment, score):
    return np.asarray(y, dtype=np.float64), np.asarray(treatment, dtype=np.float64), np.asarray(score)


def _qini_values(y, t, score):
    """Q(i) for every cut off i = 1..N, in units of outcomes per user (Q(i) / N)."""
    order = np.argsort(-score, kind="stable")
    y, t = y[order], t[order]
    cum_t = np.cumsum(t)
    cum_c = np.cumsum(1 - t)
    cum_yt = np.cumsum(y * t)
    cum_yc = np.cumsum(y * (1 - t))
    rate_t = np.divide(cum_yt, cum_t, out=np.zeros_like(cum_t), where=cum_t > 0)
    rate_c = np.divide(cum_yc, cum_c, out=np.zeros_like(cum_c), where=cum_c > 0)
    i = np.arange(1, len(y) + 1)
    q = i * (rate_t - rate_c) / len(y)
    q[(cum_t == 0) | (cum_c == 0)] = 0.0  # no estimate until both groups appear
    return q


def qini_curve(y, treatment, score, n_points: int = 200):
    """Points of the Qini curve for plotting: share of users targeted, and Q / N."""
    y, t, s = _as_arrays(y, treatment, score)
    q = _qini_values(y, t, s)
    idx = np.unique(np.linspace(0, len(q) - 1, n_points).astype(int))
    x = np.concatenate([[0.0], (idx + 1) / len(q)])
    return x, np.concatenate([[0.0], q[idx]])


def auuc(y, treatment, score) -> float:
    """Area under the Qini curve. Units: outcomes per user."""
    y, t, s = _as_arrays(y, treatment, score)
    q = _qini_values(y, t, s)
    return float(q.sum() / len(q))  # mean of Q(i)/N over i, same as the area on [0, 1]


def qini_coefficient(y, treatment, score) -> float:
    """Area between the model's Qini curve and the random line.

    Zero for a useless score, positive when ranking by the score beats random
    targeting. This is the single number we compare models with.
    """
    y, t, s = _as_arrays(y, treatment, score)
    q = _qini_values(y, t, s)
    return float(q.sum() / len(q) - 0.5 * q[-1])


def incremental_at(y, treatment, score, frac: float) -> float:
    """Extra outcomes per 1,000 users contacted when the top frac of users are targeted."""
    y, t, s = _as_arrays(y, treatment, score)
    q = _qini_values(y, t, s)
    i = max(1, int(round(frac * len(q))))
    return float(q[i - 1] * len(q) / i * 1000)


def uplift_by_decile(y, treatment, score, bins: int = 10) -> pd.DataFrame:
    """Observed uplift in each group of equal size, from highest to lowest score.

    A good model shows high uplift in decile 1 and falling uplift after that.
    Uplift here is measured on real outcomes, so it is not a prediction.
    """
    y, t, s = _as_arrays(y, treatment, score)
    order = np.argsort(-s, kind="stable")
    rows = []
    for d, idx in enumerate(np.array_split(order, bins), start=1):
        yt, tt = y[idx], t[idx]
        p1, p0 = yt[tt == 1].mean(), yt[tt == 0].mean()
        n1, n0 = int((tt == 1).sum()), int((tt == 0).sum())
        se = np.sqrt(p1 * (1 - p1) / n1 + p0 * (1 - p0) / n0)
        rows.append(dict(decile=d, n=len(idx), n_treated=n1, n_control=n0, rate_treated=p1,
                         rate_control=p0, uplift=p1 - p0, se=se, mean_score=float(s[idx].mean())))
    return pd.DataFrame(rows)


def _one_boot(y, t, scores, metric, seed):
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(y), len(y))
    return {name: metric(y[idx], t[idx], s[idx]) for name, s in scores.items()}


def bootstrap_metrics(y, treatment, scores: dict, metric=qini_coefficient, n_boot: int = 200, seed: int = 42, n_jobs: int = -1):
    """Paired bootstrap of a metric for several models at once.

    Each resample draws rows with replacement and scores every model on the
    same rows, so differences between models are fair. Returns a table with one
    row per resample and one column per model.
    """
    y, t = np.asarray(y, dtype=np.float64), np.asarray(treatment, dtype=np.float64)
    scores = {k: np.asarray(v) for k, v in scores.items()}
    seeds = np.random.SeedSequence(seed).generate_state(n_boot)
    out = Parallel(n_jobs=n_jobs)(delayed(_one_boot)(y, t, scores, metric, int(s)) for s in seeds)
    return pd.DataFrame(out)


def bootstrap_ci(boot: pd.DataFrame, alpha: float = 0.05) -> pd.DataFrame:
    """Percentile confidence interval for each column of a bootstrap table."""
    return pd.DataFrame({"lo": boot.quantile(alpha / 2), "hi": boot.quantile(1 - alpha / 2)})


def paired_difference(boot: pd.DataFrame, a: str, b: str, point_a: float, point_b: float, alpha: float = 0.05):
    """Is model a better than model b?

    Uses the paired bootstrap of the difference a - b. The one sided p value is
    the share of resamples where a did not beat b, with a small correction so it
    is never exactly zero. This is the test behind hypothesis H1.
    """
    diff = boot[a] - boot[b]
    p = (int((diff <= 0).sum()) + 1) / (len(diff) + 1)
    return dict(diff=point_a - point_b, lo=float(diff.quantile(alpha / 2)), hi=float(diff.quantile(1 - alpha / 2)), p_one_sided=p)
