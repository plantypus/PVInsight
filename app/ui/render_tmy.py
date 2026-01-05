# app/ui/render_tmy.py
from __future__ import annotations

import streamlit as st
import pandas as pd

from app.ui.common import (
    render_kpis,
    render_pdf_download,
    render_warnings,
    render_logs,
    render_dataframe,
    render_plot,
)
from app.ui.plots import (
    time_series_single,
    time_series_overlay,
    time_series_difference,
    histogram,
)



def render_tmy_analysis_result(result):
    df = result.dataset.df
    units = result.dataset.units_by_col
    q = result.dataset.quality

    # --- KPIs
    kpis = {
        "Rows": f"{q.n_rows:,}",
        "Period": f"{q.start} → {q.end}",
        "Time step": f"{result.dataset.time_step_minutes} min",
    }
    if result.energy.annual_ghi is not None:
        kpis["Annual GHI"] = f"{result.energy.annual_ghi:.1f} {result.energy.unit}"
    if result.energy.annual_dni is not None:
        kpis["Annual DNI"] = f"{result.energy.annual_dni:.1f} {result.energy.unit}"
    if "temp" in df.columns:
        kpis["Temp mean"] = f"{df['temp'].mean():.1f} {units.get('temp','')}"
        kpis["Temp min/max"] = f"{df['temp'].min():.1f} / {df['temp'].max():.1f} {units.get('temp','')}"

    render_kpis(kpis)

    # --- Charts
    st.subheader("Charts (interactive)")

    tabs = st.tabs(["Time series", "Distributions"])

    with tabs[0]:
        if "ghi" in df.columns:
            fig = time_series_single(df, "datetime", "ghi", "GHI", unit=units.get("ghi", ""))
            render_plot(fig)

        if "dni" in df.columns:
            fig = time_series_single(df, "datetime", "dni", "DNI", unit=units.get("dni", ""))
            render_plot(fig)

        if "temp" in df.columns:
            fig = time_series_single(df, "datetime", "temp", "Temperature", unit=units.get("temp", ""))
            render_plot(fig)

    with tabs[1]:
        c1, c2 = st.columns(2)
        with c1:
            if "ghi" in df.columns:
                render_plot(
                    histogram(df, "ghi", "GHI", unit=units.get("ghi", "")),
                    width_ratio=(0.5, 2.5, 0.5),  # histogram slightly wider
                )
        with c2:
            if "temp" in df.columns:
                render_plot(
                    histogram(df, "temp", "Temperature", unit=units.get("temp", "")),
                    width_ratio=(0.5, 2.5, 0.5),
                )


    # --- Tables
    st.subheader("Tables")
    st.write("Statistics (mean / min / max)")
    st.dataframe(result.stats)

    if result.dataset.header_info:
        st.write("Header info")
        st.dataframe(pd.DataFrame(list(result.dataset.header_info.items()), columns=["key", "value"]))

    # --- Exports + QA
    st.divider()
    render_pdf_download(result.report_pdf, label="Download PDF")
    render_warnings(result.dataset.warnings, title="Warnings / checks")
    render_logs(result.log_path, title="Logs")
    render_dataframe(df, title="Data preview")


def render_tmy_compare_result(result):
    ds1 = result.ds1
    ds2 = result.ds2
    df1 = ds1.df
    df2 = ds2.df

    unit_map = ds1.units_by_col  # same target units if your pipeline normalizes

    # --- KPIs
    kpis = {
        "Common period": f"{result.common_start} → {result.common_end}",
        "Alert": "YES" if result.alert_flag else "NO",
    }
    if result.energy1.annual_ghi is not None and result.energy2.annual_ghi is not None:
        kpis["Annual GHI"] = f"{result.energy1.annual_ghi:.1f} vs {result.energy2.annual_ghi:.1f} {result.energy1.unit}"
    if result.energy1.annual_dni is not None and result.energy2.annual_dni is not None:
        kpis["Annual DNI"] = f"{result.energy1.annual_dni:.1f} vs {result.energy2.annual_dni:.1f} {result.energy1.unit}"
    render_kpis(kpis)

    # --- Differences table
    st.subheader("Differences")
    diffs_df = pd.DataFrame(result.diffs).T
    # Optional: highlight high mean_pct
    st.dataframe(diffs_df)

    # --- Charts
    st.subheader("Charts (interactive)")
    vars_to_plot = [v for v in ["ghi", "dni", "dhi", "temp"] if v in df1.columns and v in df2.columns]

    # Choose variable
    var = st.selectbox("Variable", vars_to_plot, index=0 if vars_to_plot else None)
    if var:
        unit = unit_map.get(var, "")

        fig = time_series_overlay(
            df1, df2, "datetime", var,
            ds1.source_name, ds2.source_name,
            unit=unit,
        )
        render_plot(fig)

        show_diff = st.checkbox("Show difference curve (File1 - File2)", value=True)
        if show_diff:
            figd = time_series_difference(
                df1, df2, "datetime", var,
                label=f"{var.upper()} diff",
                unit=unit,
            )
            render_plot(figd, width_ratio=(1, 1.5, 1))  # diff curve slightly narrower

    # --- Exports + QA
    st.divider()
    render_pdf_download(result.report_pdf, label="Download PDF")
    warn = (ds1.warnings or []) + (ds2.warnings or []) + (result.energy1.warnings or []) + (result.energy2.warnings or [])
    render_warnings(warn, title="Warnings / checks")
    render_logs(result.log_path, title="Logs")
