"""FactorContext（C1 唯一定義）與 point-in-time 建構器。

契約：欄位名一律 price_df/index_df；as_of 為 pd.Timestamp；
後續因子層/回測層一律 `from .context import FactorContext`，禁止 redefine。
price_df 進 ctx 時尚未 add_indicators，由消費端統一呼叫一次。
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass
class FactorContext:
    stock_id: str
    as_of: pd.Timestamp
    price_df: pd.DataFrame
    index_df: pd.DataFrame
    inst: pd.DataFrame
    revenue: pd.DataFrame
    valuation: pd.DataFrame
    margin: pd.DataFrame
    shareholding: pd.DataFrame
    fundamentals: dict
    industry: str | None = None
    shares_outstanding: float | None = None
    market_cap: float | None = None
    meta: dict = field(default_factory=dict)

    def latest_price(self) -> pd.Series | None:
        """取 date<=as_of 的最後一筆報價（停牌則為停牌前最後成交）。"""
        if self.price_df is None or self.price_df.empty:
            return None
        df = self.price_df
        if "date" in df.columns:
            df = df[df["date"] <= self.as_of]
        return df.iloc[-1] if len(df) else None

    def asof_row(self, df_name: str) -> pd.Series | None:
        """對不規則頻率資料取 date<=as_of 的最後一筆。"""
        df = getattr(self, df_name, None)
        if df is None or df.empty or "date" not in df.columns:
            return None
        sub = df[df["date"] <= self.as_of]
        return sub.iloc[-1] if len(sub) else None
