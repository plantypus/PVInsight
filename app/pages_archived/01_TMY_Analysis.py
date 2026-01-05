# app/pages/01_TMY_Analysis.py

from __future__ import annotations

from _bootstrap import *  # noqa: F401,F403

import streamlit as st
from PIL import Image

from config import APP_NAME, LOGO_PNG, DEFAULT_LANG, OUTPUTS_DIR, OUTPUT_MODE, METEO_DEFAULTS
from utils.i18n import t
from core.meteo.tmy_analysis import analyze_tmy_source


def _set_page(lang: str):
    icon = "☀️"
    if LOGO_PNG.exists():
        try:
            icon = Image.open(LOGO_PNG)
        except Exception:
            pass
    st.set_page_config(page_title=f"{APP_NAME} — {t('tmy_analysis_title', lang)}", page_icon=icon, layout="wide")


def main():
    lang = st.session_state.get("lang", DEFAULT_LANG)
    _set_page(lang)

    # Sidebar
    with st.sidebar:
        st.header(t("sidebar_settings", lang))
        lang_choice = st.selectbox(t("sidebar_language", lang), ["fr", "en"], index=0 if lang == "fr" else 1)
        st.session_state["lang"] = lang_choice
        lang = lang_choice

        st.subheader(t("option_units", lang))
        irradiance_unit = st.selectbox(t("irradiance_unit", lang), ["kW/m²", "W/m²"], index=0)
        energy_unit = st.selectbox(t("energy_unit", lang), ["kWh/m²", "Wh/m²"], index=0)
        resample = st.checkbox(t("resample_hourly", lang), value=METEO_DEFAULTS.resample_to_hourly_if_subhourly)

    st.title(t("tmy_analysis_title", lang))

    uploaded = st.file_uploader(t("upload_one", lang), type=["csv", "txt"])
    if not uploaded:
        return

    st.caption(f"{uploaded.name} — {uploaded.size/1024:.1f} KB")

    if st.button(t("run_analysis", lang), type="primary"):
        data = uploaded.getvalue()

        result = analyze_tmy_source(
            source=data,
            source_name=uploaded.name,
            outputs_dir=OUTPUTS_DIR,
            output_mode=OUTPUT_MODE,
            target_irradiance_unit=irradiance_unit,
            energy_unit=energy_unit,
            resample_hourly_if_subhourly=resample,
        )

        st.success(t("report_ready", lang))

        # Download PDF
        pdf_bytes = result.report_pdf.read_bytes()
        st.download_button(
            t("download_pdf", lang),
            data=pdf_bytes,
            file_name=result.report_pdf.name,
            mime="application/pdf",
        )

        # Warnings
        with st.expander(t("warnings_title", lang), expanded=False):
            if result.dataset.warnings:
                for w in result.dataset.warnings:
                    st.write(f"- {w}")
            else:
                st.write("—")

        # Logs
        with st.expander(t("logs_title", lang), expanded=False):
            st.code(result.log_path.read_text(encoding="utf-8"), language="text")

        # Preview
        if st.checkbox(t("show_dataframe", lang), value=False):
            st.subheader(t("preview", lang))
            st.dataframe(result.dataset.df.head(200))


if __name__ == "__main__":
    main()
