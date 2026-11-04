"""Load, verify, convert, sample and split the Criteo Uplift v2.1 data.

Stage 0 and Stage 1. Read data/README.md first: the file is ordered, so never
take the first rows.
"""
from pathlib import Path

import pandas as pd

MIRROR_URL = "https://github.com/jszymon/uplift_sklearn_data/releases/download/Criteo/criteo-research-uplift-v2.1.csv.gz"
SHA256 = "2716e1bf0fd157a93b5bf86924d9088419dfbac2022c6cd90030220634f616dc"
SEED = 42

FEATURES = [f"f{i}" for i in range(12)]  # we keep 10 of these after the Stage 1 feature cut
TREATMENT = "treatment"
OUTCOMES = ["visit", "conversion"]  # develop on visit first. Never use "exposure".


def download(dest: Path) -> Path:
    """Download the mirror file into dest and return its path."""
    raise NotImplementedError


def verify_checksum(path: Path, expected: str = SHA256) -> bool:
    """Return True if the SHA256 of the file at path matches expected."""
    raise NotImplementedError


def to_parquet(csv_gz: Path, out: Path) -> Path:
    """Convert the downloaded csv.gz to parquet and return the output path."""
    raise NotImplementedError


def draw_sample(df: pd.DataFrame, n: int, seed: int = SEED) -> pd.DataFrame:
    """Random sample of n rows. Check that the treated share is about 0.85."""
    raise NotImplementedError


def split_by_row_id(df: pd.DataFrame, test_size: float = 0.3, seed: int = SEED):
    """Fixed train and test split by row id, saved to disk. Nobody splits again."""
    raise NotImplementedError
