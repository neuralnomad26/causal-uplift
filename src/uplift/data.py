import hashlib
import urllib.request
from pathlib import Path
import numpy as np
import pandas as pd

MIRROR_URL = "https://github.com/jszymon/uplift_sklearn_data/releases/download/Criteo/criteo-research-uplift-v2.1.csv.gz"
SHA256 = "2716e1bf0fd157a93b5bf86924d9088419dfbac2022c6cd90030220634f616dc"
SEED = 42

FEATURES = [f"f{i}" for i in range(12)]  # we keep 10 of the 12 in modeling
TREATMENT = "treatment"
OUTCOMES = ["visit", "conversion"]  # develop on visit


def download(dest: Path) -> Path:
    """Download the mirror file into dest and return it."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        urllib.request.urlretrieve(MIRROR_URL, dest)
    return dest


def verify_checksum(path: Path, expected: str = SHA256) -> bool:
    """Return True if the SHA256 of the file at path matches expected."""
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            sha.update(chunk)
    return sha.hexdigest().lower() == expected.lower()


def to_parquet(csv_gz: Path, out: Path) -> Path:
    """Convert the downloaded csv.gz to parquet and return out."""
    csv_gz = Path(csv_gz)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        return out

    dtypes = {col: "float32" for col in FEATURES}
    dtypes.update({TREATMENT: "int8", "visit": "int8", "conversion": "int8", "exposure": "int8"})
    usecols = FEATURES + [TREATMENT, "visit", "conversion", "exposure"]

    df = pd.read_csv(csv_gz, usecols=usecols, dtype=dtypes)
    df.to_parquet(out, index=False)
    return out


def draw_sample(df: pd.DataFrame, n: int, seed: int = SEED) -> pd.DataFrame:
    """Random sample of n rows. Check that the treated share matches the full data."""
    if n >= len(df):
        sample = df.copy()
    else:
        sample = df.sample(n=n, random_state=seed)

    full_share = df[TREATMENT].mean()
    sample_share = sample[TREATMENT].mean()
    if abs(full_share - sample_share) > 0.01:
        raise ValueError(
            f"Treated share mismatch: full={full_share:.4f}, sample={sample_share:.4f}"
        )
    return sample


def split_by_row_id(
    df: pd.DataFrame, test_size: float = 0.2, seed: int = SEED, out_dir: Path | None = None
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Fixed train and test split by row id, saved to disk if out_dir is provided."""
    rng = np.random.default_rng(seed)
    row_ids = df.index.to_numpy()
    shuffled = rng.permutation(row_ids)
    n_test = int(len(df) * test_size)

    test_idx = shuffled[:n_test]
    train_idx = shuffled[n_test:]

    train_df = df.loc[train_idx].copy()
    test_df = df.loc[test_idx].copy()

    if out_dir is not None:
        out_path = Path(out_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        train_df.to_parquet(out_path / "train.parquet", index=True)
        test_df.to_parquet(out_path / "test.parquet", index=True)

    return train_df, test_df


HOLDOUT_SIZE = 2_000_000
TRAIN_SIZES = [100_000, 500_000, 1_000_000, 5_000_000]


def make_splits(n_rows: int, holdout: int = HOLDOUT_SIZE, seed: int = SEED):
    """Fixed split by row position: a held out test set and a shuffled training pool.

    The test rows are never used for fitting, tuning or feature selection.
    Every training sample is a prefix of the shuffled pool, so the 100k, 500k,
    1M and 5M samples are nested and always avoid the test rows. The same seed
    always gives the same split, so nothing needs to be saved or shared.
    """
    rng = np.random.default_rng(seed)
    order = rng.permutation(n_rows)
    return order[:holdout], order[holdout:]


def take(df: pd.DataFrame, ids: np.ndarray) -> pd.DataFrame:
    """Rows of df at the given positions. The original row number is kept as row_id."""
    out = df.iloc[ids].copy()
    out.index.name = "row_id"
    return out


def treated_share_ok(df: pd.DataFrame, expected: float = 0.85, tol: float = 0.01) -> bool:
    """The file is ordered, so always check a sample is not all treated."""
    return abs(df[TREATMENT].mean() - expected) <= tol