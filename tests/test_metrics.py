import numpy as np

from uplift import metrics as m


def test_oracle_score_hits_the_known_qini_value(planted):
    X, t, y, tau = planted
    # Ranking by x0 puts everyone with an effect first. Triangle plus flat part
    # gives an area between the curve and the random line of 0.0125.
    coef = m.qini_coefficient(y, t, X["x0"])
    assert abs(coef - 0.0125) < 0.002


def test_random_score_is_near_zero(planted):
    X, t, y, tau = planted
    rng = np.random.default_rng(1)
    assert abs(m.qini_coefficient(y, t, rng.random(len(y)))) < 0.002


def test_reversed_oracle_is_negative(planted):
    X, t, y, tau = planted
    assert m.qini_coefficient(y, t, -X["x0"]) < -0.01


def test_curve_ends_at_the_average_effect(planted):
    X, t, y, tau = planted
    x, q = m.qini_curve(y, t, X["x0"])
    ate = y[t == 1].mean() - y[t == 0].mean()
    assert x[0] == 0 and q[0] == 0 and abs(x[-1] - 1) < 1e-9
    assert abs(q[-1] - ate) < 1e-3


def test_deciles_show_the_effect_only_in_the_top_half(planted):
    X, t, y, tau = planted
    d = m.uplift_by_decile(y, t, X["x0"])
    assert d["uplift"].iloc[:5].mean() > 0.08
    assert abs(d["uplift"].iloc[5:].mean()) < 0.02
    assert d["n"].sum() == len(y)


def test_incremental_at_half_matches_the_effect(planted):
    X, t, y, tau = planted
    # Targeting the top half reaches only people with a 0.10 effect: about 100 per 1,000.
    assert abs(m.incremental_at(y, t, X["x0"], 0.5) - 100) < 10


def test_bootstrap_separates_oracle_from_random(planted):
    X, t, y, tau = planted
    rng = np.random.default_rng(2)
    scores = {"oracle": X["x0"].to_numpy(), "random": rng.random(len(y))}
    boot = m.bootstrap_metrics(y, t, scores, n_boot=40, n_jobs=2)
    point = {k: m.qini_coefficient(y, t, v) for k, v in scores.items()}
    res = m.paired_difference(boot, "oracle", "random", point["oracle"], point["random"])
    assert res["lo"] > 0 and res["p_one_sided"] < 0.05
    ci = m.bootstrap_ci(boot)
    assert ci.loc["oracle", "lo"] < point["oracle"] < ci.loc["oracle", "hi"]
