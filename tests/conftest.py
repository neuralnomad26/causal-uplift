import numpy as np
import pandas as pd
import pytest


@pytest.fixture(scope="session")
def planted():
    """Randomized data where the true effect is known.

    Treatment adds 0.10 to the outcome probability only for users with x0 > 0
    and does nothing for everyone else. The average effect is therefore 0.05.
    """
    rng = np.random.default_rng(0)
    n = 200_000
    X = pd.DataFrame(rng.normal(size=(n, 4)), columns=["x0", "x1", "x2", "x3"]).astype("float32")
    t = (rng.random(n) < 0.85).astype(int)
    tau = 0.10 * (X["x0"] > 0).to_numpy()
    y = (rng.random(n) < 0.05 + tau * t).astype(int)
    return X, t, y, tau
