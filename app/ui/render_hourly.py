from __future__ import annotations

import streamlit as st
import plotly.express as px

from app.ui.common import render_plot
from utils.formatting import format_number
from utils.i18n import t

def render_hourly_results_result(res):
    lang = st.session_state.get("lang", "fr")

    ctx = res.context
    df = ctx.df_raw  # noqa: F841

    st.divider()
    st.header(t("hourly_title", lang))

    # -------------------------
    # Synthèse globale
    # -------------------------
    thr = ctx.results.get("threshold", {})
    summ = thr.get("summary", {})

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t("hourly_metric_threshold", lang), format_number(summ.get("threshold_kw", 0.0), 1))
    c2.metric(t("hourly_metric_hours_prod", lang), format_number(summ.get("hours_prod", 0), 0))
    c3.metric(t("hourly_metric_hours_above", lang), format_number(summ.get("hours_above", 0), 0))
    c4.metric(t("hourly_metric_pct_above", lang), f"{summ.get('pct_above_prod_time', 0.0):.1f} %")

    st.metric(t("hourly_metric_energy_above", lang), format_number(summ.get("energy_kwh", 0.0), 0))

    # =====================================================
    # ANALYSE SEUIL
    # =====================================================
    st.divider()
    st.header(t("hourly_section_threshold", lang))

    with st.expander(t("hourly_help_threshold_title", lang)):
        st.markdown(t("hourly_help_threshold_body", lang))

    monthly = thr.get("monthly")
    if monthly is not None and len(monthly) > 0:
        fig = px.bar(monthly, x="month_name", y="hours_above", title=t("hourly_chart_monthly_hours", lang))
        fig.update_layout(xaxis_tickangle=-45, height=520)
        render_plot(fig)

    seasonal = thr.get("seasonal")
    if seasonal is not None and len(seasonal) > 0:
        fig = px.bar(seasonal, x="season", y="hours_above", title=t("hourly_chart_seasonal_hours", lang))
        fig.update_layout(height=520)
        render_plot(fig)

    monthly_pct = thr.get("monthly_pct")
    if monthly_pct is not None and len(monthly_pct) > 0:
        with st.expander(t("hourly_help_threshold_pct_title", lang)):
            st.markdown(t("hourly_help_threshold_pct_body", lang))

        fig = px.bar(monthly_pct, x="month_name", y="pct_above", title=t("hourly_chart_monthly_pct", lang))
        fig.update_layout(xaxis_tickangle=-45, yaxis_ticksuffix=" %", height=520)
        render_plot(fig)

    # =====================================================
    # CLIPPING
    # =====================================================
    st.divider()
    st.header(t("hourly_section_clipping", lang))

    with st.expander(t("hourly_help_clipping_title", lang)):
        st.markdown(t("hourly_help_clipping_body", lang))

    clip = ctx.results.get("inverter_clipping")
    if clip and clip.get("available"):
        if clip.get("empty"):
            st.info(t("hourly_clipping_none", lang))
        else:
            s = clip["summary"]
            c1, c2, c3 = st.columns(3)
            c1.metric(t("hourly_metric_clip_energy", lang), format_number(s["energy_clipped_kwh"], 0))
            c2.metric(t("hourly_metric_clip_pct", lang), f"{s['pct_of_inverter_output']:.2f} %")
            c3.metric(t("hourly_metric_clip_hours", lang), format_number(s["hours_clipping"], 0))

            m = clip["monthly"]
            fig = px.bar(m, x="month_name", y="IL_Pmax", title=t("hourly_chart_clip_monthly", lang))
            fig.update_layout(xaxis_tickangle=-45, height=520)
            render_plot(fig)
    else:
        st.warning(t("hourly_clipping_unavailable", lang))

    # =====================================================
    # DISTRIBUTION DE PUISSANCE
    # =====================================================
    st.divider()
    st.header(t("hourly_section_powerdist", lang))

    with st.expander(t("hourly_help_powerdist_title", lang)):
        st.markdown(t("hourly_help_powerdist_body", lang))

    pdist = ctx.results.get("power_distribution")
    if pdist:
        dfp = pdist["summary"].copy()
        fig = px.bar(
            dfp,
            x="class",
            y="pct_time",
            text=dfp["pct_time"].map(lambda x: f"{x:.1f} %"),
            title=t("hourly_chart_powerdist", lang),
        )
        fig.update_layout(yaxis_ticksuffix=" %", height=520)
        render_plot(fig)
    else:
        st.info(t("hourly_powerdist_none", lang))

    # -------------------------
    # Downloads (inchangé)
    # -------------------------
    st.divider()
    st.header(t("downloads_title", lang))

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            t("download_excel", lang),
            data=res.excel_bytes,
            file_name="hourly_results_analysis.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    with col2:
        st.download_button(
            t("download_pdf", lang),
            data=res.pdf_bytes,
            file_name="hourly_results_analysis.pdf",
            mime="application/pdf",
        )