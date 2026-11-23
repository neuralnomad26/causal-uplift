
import numpy as np
import pandas as pd
import pytest

from uplift.data import FEATURES, TREATMENT, OUTCOMES
from uplift.pipeline import (
    MODELS,
    select_features,
    tune_base,
    build_scores,
)


# Create our own small dataset for testing the pipeline.
# This does not use or change the original Criteo dataset.
@pytest.fixture(scope="module")
def sample_data():
    rng = np.random.default_rng(42)
    n = 20_000

    # Generate 12 features: f0 to f11.
    values = rng.normal(size=(n, 12)).astype("float32")
    df = pd.DataFrame(values, columns=FEATURES)

    # Random treatment assignment: approximately 85% treated.
    treatment = (rng.random(n) < 0.85).astype("int8")
    df[TREATMENT] = treatment

    # Only f0 to f9 influence the outcome.
    # f10 and f11 are deliberately irrelevant.
    weights = np.linspace(2.0, 3.0, 10)
    signal = (values[:, :10] @ weights) / 4.0

    base_probability = 1 / (1 + np.exp(-signal))

    # Treatment adds a small positive effect.
    visit_prob = np.clip(
        base_probability + 0.10 * treatment, 0.01, 0.99
    )
    conversion_prob = np.clip(
        0.25 * base_probability + 0.04 * treatment,
        0.01, 0.99
    )

    df["visit"] = (rng.random(n) < visit_prob).astype("int8")
    df["conversion"] = (
        rng.random(n) < conversion_prob
    ).astype("int8")

    return df


# Fast model settings to keep our tests below 60 seconds.
@pytest.fixture
def fast_params():
    return {
        "n_estimators": 30,
        "learning_rate": 0.1,
        "num_leaves": 7,
        "min_child_samples": 50,
    }


# Fixed training and test IDs.
@pytest.fixture(scope="module")
def split_ids():
    rng = np.random.default_rng(123)
    ids = rng.permutation(20_000)

    train_ids = ids[:5_000]
    test_ids = ids[5_000:6_000]

    return train_ids, test_ids


# TEST 1: Check that feature selection drops f10 and f11.
def test_feature_selection_removes_irrelevant_features(sample_data):
    kept, log, importance = select_features(
        sample_data,
        FEATURES,
        n_keep=10,
        n_rows=20_000,
    )

    assert len(kept) == 10
    assert set(FEATURES) - set(kept) == {"f10", "f11"}
    assert len(log) == 2
    assert set(log["dropped"]) == {"f10", "f11"}
    assert len(importance) == 12


# TEST 2: Check that tuning selects a setting from the grid.
def test_tuning_returns_valid_parameters(sample_data, fast_params):
    grid = [
        fast_params,
        {**fast_params, "num_leaves": 15},
    ]

    best, table = tune_base(
        sample_data,
        FEATURES[:10],
        "visit",
        grid=grid,
        n_rows=5_000,
        folds=2,
    )

    assert best in grid
    assert len(table) == 2
    assert "cv_logloss" in table.columns
    assert table["cv_logloss"].notna().all()


# TEST 3: Check the structure of the scores file.
def test_scores_file_has_correct_structure(
    sample_data, split_ids, fast_params
):
    train_ids, test_ids = split_ids

    params = {
        "visit": fast_params,
        "conversion": fast_params,
    }

    scores = build_scores(
        sample_data,
        train_ids,
        test_ids,
        FEATURES[:10],
        params,
    )

    expected_columns = (
        ["treatment", "visit", "conversion"]
        + [
            f"{model}_{outcome}"
            for outcome in OUTCOMES
            for model in MODELS
        ]
    )

    assert list(scores.columns) == expected_columns
    assert len(scores) == len(test_ids)
    assert scores.index.name == "row_id"
    assert scores.index.tolist() == test_ids.tolist()
    assert not scores.isna().any().any()

    for column in expected_columns[3:]:
        assert scores[column].dtype == np.float32


# TEST 4: Check that the response baseline ignores treatment.
def test_response_baseline_ignores_treatment(
    sample_data, split_ids, fast_params
):
    train_ids, test_ids = split_ids

    params = {"visit": fast_params}

    # Train and score using the original treatment values.
    original = build_scores(
        sample_data,
        train_ids,
        test_ids,
        FEATURES[:10],
        params,
        outcomes=["visit"],
    )

    # Copy the dataset and randomly flip treatment values
    # in training rows only.
    modified_data = sample_data.copy()

    rng = np.random.default_rng(456)
    flip_mask = rng.random(len(train_ids)) < 0.5
    rows_to_flip = train_ids[flip_mask]

    modified_data.loc[rows_to_flip, TREATMENT] = (
        1 - modified_data.loc[rows_to_flip, TREATMENT]
    )

    # Train and score again with the changed treatment values.
    modified = build_scores(
        modified_data,
        train_ids,
        test_ids,
        FEATURES[:10],
        params,
        outcomes=["visit"],
    )

    # Response predictions must remain identical.
    np.testing.assert_array_equal(
        original["response_visit"].to_numpy(),
        modified["response_visit"].to_numpy(),
    )

    # S-Learner predictions must respond to treatment changes.
    assert not np.allclose(
        original["s_visit"].to_numpy(),
        modified["s_visit"].to_numpy(),
    )

