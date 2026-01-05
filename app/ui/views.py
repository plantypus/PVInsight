# app/ui/views.py
from __future__ import annotations

import streamlit as st
from PIL import Image

from config import OUTPUTS_DIR, OUTPUT_MODE
from utils.i18n import t
from config import LOGO_PNG, APP_NAME, APP_VERSION

from app.ui.layout import tool_header
from app.ui.widgets import uploader_one, uploader_two, run_button

from core.meteo.tmy_analysis import analyze_tmy_source
from core.meteo.tmy_compare import compare_tmy_sources

from core.production import analyze_hourly_source
from app.ui.render_tmy import render_tmy_analysis_result, render_tmy_compare_result
from app.ui.render_hourly import render_hourly_results_result


# =============================================================================
# Helpers
# =============================================================================

def _file_sig(up) -> str | None:
    if not up:
        return None
    return f"{up.name}|{up.size}"


def _invalidate_on_change(sig_key: str, result_key: str, new_sig: str | None) -> None:
    """
    Generic "memo invalidation" when upload changes.
    """
    old_sig = st.session_state.get(sig_key)
    if new_sig != old_sig:
        st.session_state[sig_key] = new_sig
        st.session_state.pop(result_key, None)


# =============================================================================
# Home
# =============================================================================

def view_home():
    lang = st.session_state.get("lang", "fr")

    # --- Header (logo + title)

    col_logo, col_title = st.columns([1, 5], vertical_alignment="center")

    with col_logo:
        if LOGO_PNG.exists():
            try:
                st.image(Image.open(LOGO_PNG), width=110)
            except Exception:
                st.write("☀️")

    with col_title:
        st.title(t("app_title", lang))
        st.caption(f"{t('app_tagline', lang)} — v{APP_VERSION}")

    st.divider()

    # --- About / description
    st.subheader(t("home_intro_title", lang))
    st.markdown(t("home_intro_body", lang))

    st.divider()

    # --- Tools
    st.subheader(t("home_tools_title", lang))
    st.caption(t("home_tools_subtitle", lang))

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📄 " + t("tmy_analysis_title", lang), use_container_width=True):
            st.session_state["tool"] = "tmy_analysis"
            st.rerun()
    with c2:
        if st.button("📊 " + t("tmy_compare_title", lang), use_container_width=True):
            st.session_state["tool"] = "tmy_compare"
            st.rerun()
    with c3:
        if st.button("⚡ " + t("hourly_results_title", lang), use_container_width=True):
            st.session_state["tool"] = "hourly_results"
            st.rerun()

    st.divider()

    # --- How-to
    with st.expander("ℹ️ " + t("home_howto_title", lang)):
        st.markdown(t("home_howto_body", lang))



# =============================================================================
# Meteo — TMY Analysis
# =============================================================================

def view_tmy_analysis():
    lang = st.session_state.get("lang", "fr")
    tool_header(t("tmy_analysis_title", lang))

    # Upload
    up = uploader_one(t("upload_one", lang), key="tmy_analysis_upload")

    _invalidate_on_change(
        sig_key="tmy_analysis_sig",
        result_key="tmy_analysis_result",
        new_sig=_file_sig(up),
    )

    if up:
        st.caption(f"{up.name} — {up.size/1024:.1f} KB")
    else:
        st.info("Charge un fichier TMY pour lancer l’analyse.")

    # Run
    if up is not None and run_button(t("run_analysis", lang), key="run_tmy_analysis"):
        with st.spinner("Analyse en cours…"):
            res = analyze_tmy_source(
                source=up.getvalue(),
                source_name=up.name,
                outputs_dir=OUTPUTS_DIR,
                output_mode=OUTPUT_MODE,
                target_irradiance_unit=st.session_state.get("irradiance_unit", "kW/m²"),
                energy_unit=st.session_state.get("energy_unit", "kWh/m²"),
                resample_hourly_if_subhourly=st.session_state.get("resample_hourly", True),
            )
        st.session_state["tmy_analysis_result"] = res
        st.success(t("report_ready", lang))

    # Render memo
    res = st.session_state.get("tmy_analysis_result")
    if res is not None:
        render_tmy_analysis_result(res)

    # Clear
    if st.button("🧹 Clear results", use_container_width=True, key="clear_tmy_analysis"):
        st.session_state.pop("tmy_analysis_result", None)
        st.rerun()


# =============================================================================
# Meteo — TMY Compare
# =============================================================================

def view_tmy_compare():
    lang = st.session_state.get("lang", "fr")
    tool_header(t("tmy_compare_title", lang))

    # Uploads
    up1, up2 = uploader_two(
        t("upload_two_a", lang),
        t("upload_two_b", lang),
        "tmy_cmp_1",
        "tmy_cmp_2",
    )

    new_sig = None
    if up1 and up2:
        new_sig = _file_sig(up1) + "||" + _file_sig(up2)

    _invalidate_on_change(
        sig_key="tmy_compare_sig",
        result_key="tmy_compare_result",
        new_sig=new_sig,
    )

    if up1 and up2:
        st.caption(f"File 1: {up1.name} — {up1.size/1024:.1f} KB")
        st.caption(f"File 2: {up2.name} — {up2.size/1024:.1f} KB")
    else:
        st.info("Charge deux fichiers TMY pour lancer la comparaison.")

    # Run
    if (up1 is not None and up2 is not None) and run_button(t("run_compare", lang), key="run_tmy_compare"):
        with st.spinner("Comparaison en cours…"):
            res = compare_tmy_sources(
                source1=up1.getvalue(),
                name1=up1.name,
                source2=up2.getvalue(),
                name2=up2.name,
                outputs_dir=OUTPUTS_DIR,
                output_mode=OUTPUT_MODE,
                target_irradiance_unit=st.session_state.get("irradiance_unit", "kW/m²"),
                energy_unit=st.session_state.get("energy_unit", "kWh/m²"),
                resample_hourly_if_subhourly=st.session_state.get("resample_hourly", True),
            )
        st.session_state["tmy_compare_result"] = res
        st.success(t("report_ready", lang))

    # Render memo
    res = st.session_state.get("tmy_compare_result")
    if res is not None:
        render_tmy_compare_result(res)

    # Clear
    if st.button("🧹 Clear results", use_container_width=True, key="clear_tmy_compare"):
        st.session_state.pop("tmy_compare_result", None)
        st.rerun()


# =============================================================================
# Production — Hourly Results
# =============================================================================

def view_hourly_results() -> None:
    lang = st.session_state.get("lang", "fr")
    tool_header(t("hourly_results_title", lang))

    # Upload
    up = uploader_one(t("upload_hourly", lang), key="hourly_upload", types=["csv"])

    _invalidate_on_change(
        sig_key="hourly_sig",
        result_key="hourly_result",
        new_sig=_file_sig(up),
    )

    if not up:
        st.info(t("upload_hourly", lang))
        return

    st.caption(f"{up.name} — {up.size/1024:.1f} KB")

    # Option : threshold
    threshold_kw = st.number_input(
        "Seuil de puissance (kW)",
        min_value=0.0,
        value=float(st.session_state.get("hourly_threshold_kw", 500.0)),
        step=10.0,
    )
    st.session_state["hourly_threshold_kw"] = float(threshold_kw)

    # Run
    if run_button(t("run_hourly", lang), key="run_hourly"):
        with st.spinner("Analyse en cours…"):
            res = analyze_hourly_source(
                source=up.getvalue(),
                source_name=up.name,
                threshold_kw=float(threshold_kw),
            )
        st.session_state["hourly_result"] = res
        st.success(t("report_ready", lang))

    # Render memo
    res = st.session_state.get("hourly_result")
    if res is None:
        return

    # Affichage streamlit (et pas seulement PDF)
    # -> on s'appuie sur ton renderer dédié (cohérent avec TMY)
    render_hourly_results_result(res)

    # Clear
    if st.button("🧹 Clear results", use_container_width=True, key="clear_hourly"):
        st.session_state.pop("hourly_result", None)
        st.rerun()
