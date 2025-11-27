"""Model performance monitoring stub."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def load_live_metrics(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path)


def compute_population_stability(train: pd.Series, live: pd.Series) -> float:
    bins = pd.qcut(train, q=10, duplicates="drop")
    train_counts = train.groupby(bins).count()
    live_counts = live.groupby(pd.cut(live, bins.cat.categories)).count()
    live_dist = live_counts / live_counts.sum()
    train_dist = train_counts / train_counts.sum()
    psi = (live_dist - train_dist) * np.log((live_dist + 1e-9) / (train_dist + 1e-9))
    return float(psi.sum())
