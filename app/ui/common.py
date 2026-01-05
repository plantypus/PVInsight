# app/ui/common.py
from __future__ import annotations
from pathlib import Path
import streamlit as st
import pandas as pd

def render_kpis(kpis: dict):
    if not kpis:
        return
    items = list(kpis.items())
    n = min(4, len(items))
    cols = st.columns(n)
    for i, (k, v) in enumerate(items[:n]):
        cols[i].metric(label=str(k), value=str(v))

    if len(items) > n:
        with st.expander("More KPIs", expanded=False):
            for k, v in items[n:]:
                st.write(f"**{k}**: {v}")

def render_dataframe(df: pd.DataFrame, title: str = "Preview", max_rows: int = 200):
    if df is None:
        return
    if st.checkbox("Show data preview", value=False):
        st.subheader(title)
        st.dataframe(df.head(max_rows))

def render_warnings(warnings, title: str = "Warnings"):
    with st.expander(title, expanded=False):
        if warnings:
            for w in warnings:
                st.write(f"- {w}")
        else:
            st.write("—")

def render_logs(log_path: Path, title: str = "Logs"):
    with st.expander(title, expanded=False):
        if log_path and log_path.exists():
            st.code(log_path.read_text(encoding="utf-8"), language="text")
        else:
            st.write("No log file.")

def render_pdf_download(pdf_path: Path, label: str = "Download PDF"):
    if pdf_path and pdf_path.exists():
        st.download_button(
            label=label,
            data=pdf_path.read_bytes(),
            file_name=pdf_path.name,
            mime="application/pdf",
        )

def render_plot(fig, width_ratio=(1, 2, 1)):
    """
    Render a Plotly figure centered on the page with margins.
    width_ratio must contain strictly positive numbers.
    """
    ratios = [r if r > 0 else 0.1 for r in width_ratio]
    left, center, right = st.columns(ratios)
    with center:
        st.plotly_chart(fig, width="stretch")



