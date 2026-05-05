from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from config import ScoreConfig, Variant
from score.data import load_metrics
from score.normalise import normalise


FIXTURE_CACHE = Path(__file__).parent / "data" / "cache"


@pytest.fixture(scope="module")
def config(tmp_path_factory) -> ScoreConfig:
    return ScoreConfig(
        name="test",
        output_dir=tmp_path_factory.mktemp("out"),
        cache_dir=FIXTURE_CACHE,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 10),
        weights={"phase_wrms": 0.4, "cn0": 0.3, "amb_resets": 0.3},
        variants=(Variant(name="additive", aggregator="weighted_sum"),),
        window_days=None,
    )


@pytest.fixture(scope="module")
def loaded_df(config) -> pd.DataFrame:
    return load_metrics(config)


@pytest.fixture(scope="module")
def normalised_df(loaded_df) -> pd.DataFrame:
    return normalise(loaded_df)
