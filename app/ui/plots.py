# app/ui/plots.py
from __future__ import annotations

from typing import Optional, Sequence
import numpy as np
import pandas as pd
import plotly.graph_objects as go


def _downsample_time_series(df: pd.DataFrame, x: str, max_points: int = 20000) -> pd.DataFrame:
    """
    Downsample by simple stride to keep UI responsive.
    Preserves chronology. Good enough for visualization.
    """
    if df is None or df.empty or max_points <= 0:
        return df
    n = len(df)
    if n <= max_points:
        return df
    step = int(np.ceil(n / max_points))
    return df.iloc[::step].copy()


def time_series_single(
    df: pd.DataFrame,
    x: str,
    y: str,
    name: str,
    unit: str = "",
    max_points: int = 20000,
) -> go.Figure:
    d = _downsample_time_series(df[[x, y]].dropna(), x=x, max_points=max_points)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=d[x],
            y=d[y],
            mode="lines",
            name=name,
            line=dict(width=1.2),
        )
    )

    ylabel = f"{name} ({unit})" if unit else name

    fig.update_layout(
        height=480,
        margin=dict(l=40, r=15, t=40, b=40),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    fig.update_xaxes(
        title="Date",
        rangeslider=dict(visible=True),
        showgrid=True,
        gridcolor="rgba(0,0,0,0.08)",
    )
    fig.update_yaxes(
        title=ylabel,
        showgrid=True,
        gridcolor="rgba(0,0,0,0.08)",
        zeroline=False,
    )
    return fig


def time_series_overlay(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    x: str,
    y: str,
    label1: str,
    label2: str,
    unit: str = "",
    max_points: int = 20000,
) -> go.Figure:
    d1 = _downsample_time_series(df1[[x, y]].dropna(), x=x, max_points=max_points)
    d2 = _downsample_time_series(df2[[x, y]].dropna(), x=x, max_points=max_points)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=d1[x], y=d1[y], mode="lines", name=label1, line=dict(width=1.2)))
    fig.add_trace(go.Scatter(x=d2[x], y=d2[y], mode="lines", name=label2, line=dict(width=1.2)))

    ylabel = f"{y.upper()} ({unit})" if unit else y.upper()

    fig.update_layout(
        height=480,
        margin=dict(l=40, r=15, t=40, b=40),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    fig.update_xaxes(
        title="Date",
        rangeslider=dict(visible=True),
        showgrid=True,
        gridcolor="rgba(0,0,0,0.08)",
    )
    fig.update_yaxes(
        title=ylabel,
        showgrid=True,
        gridcolor="rgba(0,0,0,0.08)",
        zeroline=False,
    )
    return fig


def time_series_difference(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    x: str,
    y: str,
    label: str = "Difference",
    unit: str = "",
    max_points: int = 20000,
) -> go.Figure:
    """
    Plot df1[y] - df2[y] after aligning on x by merge_asof-like exact match on timestamp.
    Assumes same timestep after harmonization (your pipeline does hourly).
    """
    a = df1[[x, y]].dropna().copy()
    b = df2[[x, y]].dropna().copy()
    m = a.merge(b, on=x, how="inner", suffixes=("_1", "_2"))
    m["diff"] = m[f"{y}_1"] - m[f"{y}_2"]
    m = _downsample_time_series(m[[x, "diff"]], x=x, max_points=max_points)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=m[x], y=m["diff"], mode="lines", name=label, line=dict(width=1.2)))

    ylabel = f"{label} ({unit})" if unit else label

    fig.update_layout(
        height=360,
        margin=dict(l=40, r=15, t=40, b=40),
        hovermode="x unified",
        showlegend=False,
    )
    fig.update_xaxes(
        title="Date",
        rangeslider=dict(visible=True),
        showgrid=True,
        gridcolor="rgba(0,0,0,0.08)",
    )
    fig.update_yaxes(
        title=ylabel,
        showgrid=True,
        gridcolor="rgba(0,0,0,0.08)",
        zeroline=True,
        zerolinecolor="rgba(0,0,0,0.25)",
    )
    return fig


def histogram(
    df: pd.DataFrame,
    col: str,
    title: str,
    unit: str = "",
    nbins: int = 60,
) -> go.Figure:
    s = df[col].dropna()
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=s, nbinsx=nbins, name=col, opacity=0.85))
    fig.update_layout(height=360, margin=dict(l=40, r=15, t=40, b=40))
    fig.update_xaxes(title=f"{title} ({unit})" if unit else title)
    fig.update_yaxes(title="Count")
    return fig
