import hashlib
import numpy as np
import pandas as pd
import pytest

from uplift.data import FEATURES, make_splits, take, treated_share_ok, verify_checksum


@pytest.fixture
def sample_df():
    rng = np.random.default_rng(42)
    n_rows = 10_000
    data = {col: rng.normal(size=n_rows).astype("float32") for col in FEATURES}
    data["treatment"] = rng.binomial(1, 0.85, size=n_rows).astype("int8")
    data["visit"] = rng.binomial(1, 0.05, size=n_rows).astype("int8")
    data["conversion"] = rng.binomial(1, 0.003, size=n_rows).astype("int8")
    data["exposure"] = rng.binomial(1, 0.03, size=n_rows).astype("int8")
    return pd.DataFrame(data)


@pytest.fixture
def splits(sample_df):
    return make_splits(len(sample_df), holdout=2_000, seed=42)


def test_holdout_and_pool_do_not_overlap(sample_df, splits):
    test_ids, pool_ids = splits
    assert len(np.intersect1d(test_ids, pool_ids)) == 0
    combined = np.concatenate([test_ids, pool_ids])
    assert len(combined) == len(sample_df)
    assert np.array_equal(np.sort(combined), np.arange(len(sample_df)))


def test_holdout_size(splits):
    test_ids, _ = splits
    assert len(test_ids) == 2_000


def test_nested_samples(splits):
    test_ids, pool_ids = splits
    holdout_set = set(test_ids.tolist())
    sizes = [100, 500, 1_000]

    for n in sizes:
        assert len(set(pool_ids[:n].tolist()) & holdout_set) == 0

    for small, large in zip(sizes, sizes[1:]):
        assert np.array_equal(pool_ids[:small], pool_ids[:large][:small])


def test_deterministic_splits(sample_df):
    test_a, pool_a = make_splits(len(sample_df), holdout=2_000, seed=42)
    test_b, pool_b = make_splits(len(sample_df), holdout=2_000, seed=42)
    test_diff, pool_diff = make_splits(len(sample_df), holdout=2_000, seed=99)

    assert np.array_equal(test_a, test_b)
    assert np.array_equal(pool_a, pool_b)
    assert not np.array_equal(test_a, test_diff)
    assert not np.array_equal(pool_a, pool_diff)


def test_ordered_file_trap(sample_df):
    ordered_df = sample_df.copy()
    rng = np.random.default_rng(42)
    tail_treatment = np.array([1] * 3_500 + [0] * 1_500, dtype="int8")
    rng.shuffle(tail_treatment)
    ordered_df.iloc[:5_000, ordered_df.columns.get_loc("treatment")] = 1
    ordered_df.iloc[5_000:, ordered_df.columns.get_loc("treatment")] = tail_treatment

    assert not treated_share_ok(ordered_df.head(1_000))
    random_sample = ordered_df.sample(n=1_000, random_state=42)
    assert treated_share_ok(random_sample)


def test_row_ids_kept(sample_df, splits):
    _, pool_ids = splits
    ids = pool_ids[:250]
    subset = take(sample_df, ids)

    assert subset.index.name == "row_id"
    assert np.array_equal(subset.index.to_numpy(), ids)


def test_verify_checksum(tmp_path):
    file_path = tmp_path / "dummy.bin"
    payload = b"criteo-uplift-checksum-test"
    file_path.write_bytes(payload)
    expected_sha = hashlib.sha256(payload).hexdigest()

    assert verify_checksum(file_path, expected=expected_sha)

    corrupted = bytearray(payload)
    corrupted[0] ^= 0xFF
    file_path.write_bytes(bytes(corrupted))
    assert not verify_checksum(file_path, expected=expected_sha)
