import pytest
import pandas as pd
from trader.cache import DataCache


def test_save_and_load(tmp_path):
    cache = DataCache(str(tmp_path / "test_cache"))
    df = pd.DataFrame({"Close": [1.0, 2.0, 3.0]})
    cache.save(df, "TEST")
    loaded = cache.load("TEST")
    assert loaded is not None
    assert len(loaded) == 3


def test_load_missing(tmp_path):
    cache = DataCache(str(tmp_path / "test_cache"))
    result = cache.load("NONEXISTENT")
    assert result is None
