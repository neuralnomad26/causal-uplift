import numpy as np
import pytest

from uplift import metrics as m
from uplift.learners import SLearner, TLearner, XLearner

FAST = dict(n_estimators=60, learning_rate=0.1, num_leaves=15, min_child_samples=200)


@pytest.mark.parametrize("cls", [SLearner, TLearner, XLearner])
def test_learner_finds_the_planted_effect(planted, cls):
    X, t, y, tau = planted
    half = len(y) // 2
    model = cls(FAST).fit(X.iloc[:half], t[:half], y[:half])
    score = model.predict_uplift(X.iloc[half:])
    assert score.shape == (len(y) - half,)
    # ranking by the learner must beat random and must lean towards x0 > 0
    coef = m.qini_coefficient(y[half:], t[half:], score)
    assert coef > 0.004
    assert np.corrcoef(score, tau[half:])[0, 1] > 0.3
