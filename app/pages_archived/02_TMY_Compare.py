# app/pages/02_TMY_Compare.py

from __future__ import annotations

from _bootstrap import *  # noqa: F401,F403

import streamlit as st
from PIL import Image

from config import APP_NAME, LOGO_PNG, DEFAULT_LANG, OUTPUTS_DIR, OUTPUT_MODE, METEO_DEFAULTS
from utils.i18n import t
from core.meteo.tmy_compare import compare_tmy_sources


def _set_page(lang: str):
    icon = "☀️"
    if LOGO_PNG.exists():
        try:
            icon = Image.open(LOGO_PNG)
        except Exception:
            pass
    st.set_page_config(page_title=f"{APP_NAME} — {t('tmy_compare_title', lang)}", page_icon=icon, layout="wide")


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
        threshold_pct = st.number_input("Alert threshold (% mean diff)", min_value=0.0, max_value=100.0, value=5.0, step=0.5)

    st.title(t("tmy_compare_title", lang))

    up1 = st.file_uploader(t("upload_two_a", lang), type=["csv", "txt"], key="tmy1")
    up2 = st.file_uploader(t("upload_two_b", lang), type=["csv", "txt"], key="tmy2")
    if not up1 or not up2:
        return

    if st.button(t("run_compare", lang), type="primary"):
        data1 = up1.getvalue()
        data2 = up2.getvalue()

        result = compare_tmy_sources(
            source1=data1,
            name1=up1.name,
            source2=data2,
            name2=up2.name,
            outputs_dir=OUTPUTS_DIR,
            output_mode=OUTPUT_MODE,
            target_irradiance_unit=irradiance_unit,
            energy_unit=energy_unit,
            resample_hourly_if_subhourly=resample,
            threshold_pct=float(threshold_pct),
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

        with st.expander(t("warnings_title", lang), expanded=False):
            warn = (result.ds1.warnings or []) + (result.ds2.warnings or []) + (result.energy1.warnings or []) + (result.energy2.warnings or [])
            if warn:
                for w in warn:
                    st.write(f"- {w}")
            else:
                st.write("—")

        with st.expander("Differences", expanded=False):
            st.json(result.diffs)

        with st.expander(t("logs_title", lang), expanded=False):
            st.code(result.log_path.read_text(encoding="utf-8"), language="text")


if __name__ == "__main__":
    main()
