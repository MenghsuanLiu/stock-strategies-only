import pandas as pd
from stock_strategies import data


def test_get_price_history_uses_cache(monkeypatch):
    raw = pd.DataFrame({
        "date": pd.to_datetime(["2024-01-02", "2024-01-03"]),
        "open": [10, 11], "max": [10.5, 11.5], "min": [9.5, 10.5],
        "close": [10.2, 11.2], "Trading_Volume": [1000, 1100],
    })
    monkeypatch.setattr(data, "fetch_finmind_cached", lambda *a, **k: raw.copy())
    df = data.get_price_history("2330", years=1)
    assert {"date", "open", "high", "low", "close", "volume"}.issubset(df.columns)
    assert df.iloc[1]["high"] == 11.5    # max→high
    assert df.iloc[1]["volume"] == 1100  # Trading_Volume→volume
