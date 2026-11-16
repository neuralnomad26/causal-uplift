import numpy as np
import pandas as pd
import pytest

from uplift import data


def _tiny_csv_gz(path, n_rows=50):
    rng = np.random.default_rng(0)
    frame = pd.DataFrame({f"f{i}": rng.normal(size=n_rows) for i in range(12)})
    frame["treatment"] = rng.binomial(1, 0.85, size=n_rows)
    frame["conversion"] = rng.binomial(1, 0.01, size=n_rows)
    frame["visit"] = rng.binomial(1, 0.05, size=n_rows)
    frame["exposure"] = rng.binomial(1, 0.03, size=n_rows)
    frame.to_csv(path, index=False, compression="gzip")


def test_prepare_rejects_a_file_with_the_wrong_checksum(tmp_path):
    (tmp_path / data.CSV_NAME).write_bytes(b"not the real file")
    with pytest.raises(RuntimeError, match="Checksum mismatch"):
        data.prepare(tmp_path)
    assert not (tmp_path / data.PARQUET_NAME).exists()


def test_prepare_builds_the_parquet_from_a_valid_file(tmp_path, monkeypatch):
    _tiny_csv_gz(tmp_path / data.CSV_NAME)
    monkeypatch.setattr(data, "verify_checksum", lambda path: True)
    out = data.prepare(tmp_path)
    frame = pd.read_parquet(out)
    assert out == tmp_path / data.PARQUET_NAME
    expected = data.FEATURES + ["treatment", "visit", "conversion", "exposure"]
    assert sorted(frame.columns) == sorted(expected)
    assert len(frame) == 50
    assert str(frame["f0"].dtype) == "float32"


def test_prepare_can_be_run_twice(tmp_path, monkeypatch):
    _tiny_csv_gz(tmp_path / data.CSV_NAME)
    monkeypatch.setattr(data, "verify_checksum", lambda path: True)
    first = data.prepare(tmp_path)
    modified = first.stat().st_mtime_ns
    second = data.prepare(tmp_path)
    assert first == second
    assert second.stat().st_mtime_ns == modified


def test_failed_download_leaves_no_file_that_looks_complete(tmp_path, monkeypatch):
    def broken_download(url, dest):
        with open(dest, "wb") as handle:
            handle.write(b"half a file")
        raise OSError("connection dropped")

    monkeypatch.setattr(data.urllib.request, "urlretrieve", broken_download)
    target = tmp_path / data.CSV_NAME
    with pytest.raises(OSError):
        data.download(target)
    assert not target.exists()
