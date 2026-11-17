"""Tests for the three stages of the X learner.

The planted fixture (conftest.py) has a true effect of 0.10 for users with
x0 > 0 and 0 for everyone else. Each test pins down one part of the method so
a silent change, such as swapping tau0_ and tau1_, makes a test fail.
"""
import numpy as np
import pytest

from uplift.learners import XLearner
from uplift.metrics import qini_coefficient

FAST = dict(n_estimators=60, learning_rate=0.1, num_leaves=15, min_child_samples=200)


@pytest.fixture(scope="module")
def fitted(planted):
    """X learner fitted on the first half of the rows. The second half is the test set."""
    X, t, y, tau = planted
    half = len(y) // 2
    model = XLearner(FAST).fit(X.iloc[:half], t[:half], y[:half])
    return model, half


def _sample_with_treated_share(X, t, y, share, n=40_000, seed=0):
    """Draw n rows from the fixture so that exactly `share` of them are treated."""
    rng = np.random.default_rng(seed)
    n_treated = int(round(n * share))
    treated = rng.choice(np.flatnonzero(t == 1), size=n_treated, replace=False)
    control = rng.choice(np.flatnonzero(t == 0), size=n - n_treated, replace=False)
    rows = rng.permutation(np.concatenate([treated, control]))
    return X.iloc[rows], t[rows], y[rows]


def test_weight_is_the_treated_share_of_the_training_rows(planted, fitted):
    X, t, y, tau = planted
    model, half = fitted
    assert model.g_ == pytest.approx(t[:half].mean())


def test_blend_uses_the_treated_share(planted, fitted):
    X, t, y, tau = planted
    model, half = fitted
    X_test = X.iloc[half:]
    g = model.g_
    expected = g * model.tau0_.predict(X_test) + (1 - g) * model.tau1_.predict(X_test)
    assert np.allclose(model.predict_uplift(X_test), expected)


@pytest.mark.parametrize("share", [0.5, 0.9])
def test_weight_follows_the_treated_share_in_the_data(planted, share):
    X, t, y, tau = planted
    Xs, ts, ys = _sample_with_treated_share(X, t, y, share)
    model = XLearner(FAST).fit(Xs, ts, ys)
    assert model.g_ == pytest.approx(share, abs=0.01)


def test_scores_find_the_planted_effect(planted, fitted):
    X, t, y, tau = planted
    model, half = fitted
    score = model.predict_uplift(X.iloc[half:])
    assert np.corrcoef(score, tau[half:])[0, 1] > 0.3
    assert qini_coefficient(y[half:], t[half:], score) > 0.004


def test_one_finite_score_per_test_row(planted, fitted):
    X, t, y, tau = planted
    model, half = fitted
    score = model.predict_uplift(X.iloc[half:])
    assert score.shape == (len(y) - half,)
    assert np.isfinite(score).all()
