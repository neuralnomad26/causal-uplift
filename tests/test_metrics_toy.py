"""Two independent proofs that the evaluation code in uplift.metrics is right.

Part A works a tiny example by hand and checks the library returns the same
numbers. Part B writes the definition of Q(i) as plain loops and checks the
vectorized library code agrees on random data.
"""
from fractions import Fraction

import numpy as np
import pytest

from uplift import metrics as m


def _frac(f: Fraction) -> float:
    return float(f)


def test_toy_qini_by_hand():
    """Eight users worked on paper: Qini curve, area (AUUC) and Qini coefficient.

    The users, already sorted from the highest score to the lowest. t is the
    treatment flag (1 = treated, 0 = control) and y is the outcome.

        user  score  t  y
          1    0.9   1  1
          2    0.8   0  0
          3    0.7   1  1
          4    0.6   0  1
          5    0.5   1  0
          6    0.4   0  0
          7    0.3   1  1
          8    0.2   0  0

    Definition. For the top i users:

        rate_treated(i) = treated outcomes in top i / treated users in top i
        rate_control(i) = control outcomes in top i / control users in top i
        Q(i)            = i * (rate_treated(i) minus rate_control(i))

    Convention 1. While one group has not appeared yet, its rate is undefined,
    so there is no estimate. The code sets Q(i) = 0 for those rows. Here that
    is i = 1 only, because user 1 is treated and no control user has been seen.

    Working, one row per cut off i:

        i  treated  control  treated   control   rate_treated  rate_control  Q(i)
           count    count    outcomes  outcomes
        1     1        0         1         0       1/1           undefined    0   (convention 1)
        2     1        1         1         0       1/1 = 1       0/1 = 0      2 * (1 minus 0)       = 2
        3     2        1         2         0       2/2 = 1       0/1 = 0      3 * (1 minus 0)       = 3
        4     2        2         2         1       2/2 = 1       1/2           4 * (1 minus 1/2)     = 2
        5     3        2         2         1       2/3           1/2           5 * (2/3 minus 1/2)   = 5 * 1/6   = 5/6
        6     3        3         2         1       2/3           1/3           6 * (2/3 minus 1/3)   = 6 * 1/3   = 2
        7     4        3         3         1       3/4           1/3           7 * (3/4 minus 1/3)   = 7 * 5/12  = 35/12
        8     4        4         3         1       3/4           1/4           8 * (3/4 minus 1/4)   = 8 * 1/2   = 4

    Sum of Q(i) over i = 0 + 2 + 3 + 2 + 5/6 + 2 + 35/12 + 4
                       = 13 + 10/12 + 35/12 = 13 + 15/4 = 67/4 = 16.75

    The library works in units of outcomes per user, so it reports Q(i) / N
    with N = 8:

        Q(i) / 8 = 0, 1/4, 3/8, 1/4, 5/48, 1/4, 35/96, 1/2

    Convention 2. qini_curve samples at most n_points cut offs (default 200).
    With 8 users every cut off is a sample, so the curve has 9 points: the
    origin (0, 0) followed by x = i / 8 and y = Q(i) / 8 for i = 1 to 8.

    Area (auuc). The curve is read as a step for each user, each of width 1/N,
    so the area is the sum of Q(i)/N times 1/N:

        auuc = (sum of Q(i)) / N^2 = (67/4) / 64 = 67/256 = 0.26171875

    Qini coefficient. The random targeting line goes straight from (0, 0) to
    (1, Q(N)/N) = (1, 1/2), and the area under it is 1/2 * 1/2 = 1/4 = 64/256.
    The coefficient is the area of the model minus the area of that line:

        qini_coefficient = 67/256 minus 64/256 = 3/256 = 0.01171875

    Positive, so ranking by this score beats random targeting on this table.
    """
    users = [  # (score, treatment, outcome)
        (0.9, 1, 1), (0.8, 0, 0), (0.7, 1, 1), (0.6, 0, 1),
        (0.5, 1, 0), (0.4, 0, 0), (0.3, 1, 1), (0.2, 0, 0),
    ]
    score = np.array([u[0] for u in users])
    t = np.array([u[1] for u in users])
    y = np.array([u[2] for u in users])

    # Numbers from the docstring, written as exact fractions.
    q_hand = [Fraction(0), Fraction(2), Fraction(3), Fraction(2),
              Fraction(5, 6), Fraction(2), Fraction(35, 12), Fraction(4)]
    n = len(q_hand)
    assert sum(q_hand) == Fraction(67, 4)
    auuc_hand = sum(q_hand) / n**2
    coef_hand = auuc_hand - Fraction(1, 2) * q_hand[-1] / n
    assert auuc_hand == Fraction(67, 256)
    assert coef_hand == Fraction(3, 256)

    # The curve: origin, then (i / 8, Q(i) / 8).
    x, q = m.qini_curve(y, t, score)
    assert len(x) == len(q) == 9
    np.testing.assert_allclose(x, [i / 8 for i in range(9)], atol=1e-12)
    np.testing.assert_allclose(q, [0.0] + [_frac(v / n) for v in q_hand], atol=1e-12)

    # The area and the coefficient.
    assert m.auuc(y, t, score) == pytest.approx(0.26171875, abs=1e-12)
    assert m.auuc(y, t, score) == pytest.approx(_frac(auuc_hand), abs=1e-12)
    assert m.qini_coefficient(y, t, score) == pytest.approx(0.01171875, abs=1e-12)
    assert m.qini_coefficient(y, t, score) == pytest.approx(_frac(coef_hand), abs=1e-12)

    # Row order must not matter, only the scores do.
    perm = np.random.default_rng(0).permutation(n)
    assert m.qini_coefficient(y[perm], t[perm], score[perm]) == pytest.approx(0.01171875, abs=1e-12)


def test_toy_deciles_by_hand():
    """Two groups worked on paper for uplift_by_decile with bins=2.

    Eight users sorted from the highest score to the lowest. bins=2 splits them
    into the top 4 and the bottom 4.

        user  score  t  y
          1    0.8   1  1
          2    0.7   1  1
          3    0.6   1  0
          4    0.5   0  0      <- top group: users 1 to 4
          5    0.4   1  0
          6    0.3   1  1
          7    0.2   0  1
          8    0.1   0  0      <- bottom group: users 5 to 8

    Top group. Treated users are 1, 2, 3 (n_treated = 3) with outcomes 1, 1, 0,
    so rate_treated = 2/3. The only control user is user 4 (n_control = 1) with
    outcome 0, so rate_control = 0. Uplift = 2/3 minus 0 = 2/3.
    Standard error = sqrt(p1 (1 minus p1) / n1 + p0 (1 minus p0) / n0)
                   = sqrt((2/3)(1/3)/3 + 0) = sqrt(2/27) = 0.27217.
    Mean score = (0.8 + 0.7 + 0.6 + 0.5) / 4 = 0.65.

    Bottom group. Treated users are 5, 6 (n_treated = 2) with outcomes 0, 1, so
    rate_treated = 1/2. Control users are 7, 8 (n_control = 2) with outcomes
    1, 0, so rate_control = 1/2. Uplift = 0.
    Standard error = sqrt((1/4)/2 + (1/4)/2) = sqrt(1/4) = 0.5.
    Mean score = (0.4 + 0.3 + 0.2 + 0.1) / 4 = 0.25.
    """
    score = np.array([0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1])
    t = np.array([1, 1, 1, 0, 1, 1, 0, 0])
    y = np.array([1, 1, 0, 0, 0, 1, 1, 0])

    expected = [
        dict(decile=1, n=4, n_treated=3, n_control=1, rate_treated=2 / 3, rate_control=0.0,
             uplift=2 / 3, se=float(np.sqrt(2 / 27)), mean_score=0.65),
        dict(decile=2, n=4, n_treated=2, n_control=2, rate_treated=0.5, rate_control=0.5,
             uplift=0.0, se=0.5, mean_score=0.25),
    ]
    for shuffle in (False, True):
        idx = np.random.default_rng(1).permutation(8) if shuffle else np.arange(8)
        d = m.uplift_by_decile(y[idx], t[idx], score[idx], bins=2)
        assert len(d) == 2
        for row, exp in zip(d.to_dict("records"), expected):
            for key, value in exp.items():
                assert row[key] == pytest.approx(value, abs=1e-12), (shuffle, key)


def _qini_by_loops(y, t, score):
    """Q(i) for i = 1..N written the obvious slow way, no numpy arrays, no cumsum.

    For each cut off i it walks over the top i users and counts again from
    scratch. Returns the list of Q(i) (not divided by N).
    """
    n = len(y)
    order = sorted(range(n), key=lambda k: -score[k])  # highest score first
    q = []
    for i in range(1, n + 1):
        n_t = n_c = out_t = out_c = 0
        for k in order[:i]:
            if t[k] == 1:
                n_t += 1
                out_t += y[k]
            else:
                n_c += 1
                out_c += y[k]
        if n_t == 0 or n_c == 0:
            q.append(0.0)  # same convention as the library: no estimate yet
        else:
            q.append(i * (out_t / n_t - out_c / n_c))
    return q


def _coefficient_by_loops(q):
    n = len(q)
    area = 0.0
    for value in q:
        area += (value / n) / n  # one slice of width 1/n and height Q(i)/n
    random_line = 0.5 * q[-1] / n
    return area, area - random_line


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_vectorized_qini_matches_loop_version(seed):
    """3,000 random users: the loop version and the library agree to 1e-9."""
    rng = np.random.default_rng(seed)
    n = 3000
    t = (rng.random(n) < 0.85).astype(int)
    hidden = rng.normal(size=n)
    # Treatment helps users with a high hidden value. The score is a noisy view of it.
    y = (rng.random(n) < 0.10 + 0.08 * (hidden > 0) * t).astype(int)
    score = hidden + rng.normal(scale=1.0, size=n)

    q_loop = _qini_by_loops(y.tolist(), t.tolist(), score.tolist())
    auuc_loop, coef_loop = _coefficient_by_loops(q_loop)

    assert abs(m.qini_coefficient(y, t, score) - coef_loop) < 1e-9
    assert abs(m.auuc(y, t, score) - auuc_loop) < 1e-9

    # Every sampled point of the curve is Q(i) / N from the loop version.
    x, q = m.qini_curve(y, t, score)
    cut = np.rint(x[1:] * n).astype(int)
    expected = np.array([q_loop[i - 1] / n for i in cut])
    assert np.max(np.abs(q[1:] - expected)) < 1e-9
