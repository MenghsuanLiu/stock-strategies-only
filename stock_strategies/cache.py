"""帶 parquet 快取 + 限流退避的 FinMind 取數層。

設計：一檔一 dataset 一 parquet（全歷史，不依日期切檔），讀取時記憶體過濾。
所有新 loader 一律呼叫 fetch_finmind_cached；回測逐日推進時命中快取、不重打 API。
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .config import FINMIND_CACHE_DIR


class FinMindRateLimitError(RuntimeError):
    """FinMind 限流且退避重試耗盡。由上層 loader 接住回中性結果。"""


def _cache_dir() -> Path:
    # 每次讀 env：測試會用 monkeypatch 改 FINMIND_CACHE_DIR
    import os
    return Path(os.environ.get("FINMIND_CACHE_DIR", FINMIND_CACHE_DIR))


def cache_path(dataset: str, data_id: str) -> Path:
    safe_id = data_id or "_ALL_"
    return _cache_dir() / f"{dataset}__{safe_id}.parquet"


def _meta_path(dataset: str, data_id: str) -> Path:
    return cache_path(dataset, data_id).with_suffix(".meta.json")


def clear_cache(dataset: str | None = None, data_id: str | None = None) -> int:
    """刪除符合條件的快取檔（含 sidecar meta），回傳刪除的 parquet 數。"""
    root = _cache_dir()
    if not root.exists():
        return 0
    if dataset and data_id:
        pattern = f"{dataset}__{data_id}.parquet"
    elif dataset:
        pattern = f"{dataset}__*.parquet"
    else:
        pattern = "*.parquet"
    removed = 0
    for p in root.glob(pattern):
        p.unlink()
        meta = p.with_suffix(".meta.json")
        if meta.exists():
            meta.unlink()
        removed += 1
    return removed
