# app/ui/layout.py
from __future__ import annotations
import os
import streamlit as st
import time
from PIL import Image
from pathlib import Path

from utils.i18n import t

def _trigger_quit():
    st.session_state["_quitting"] = True
    st.rerun()

def _render_quit_screen_and_exit():
    if not st.session_state.get("_quitting"):
        return

    st.empty()
    st.markdown(
        """
        <div style="text-align:center; margin-top:20vh;">
            <h2>👋 Application arrêtée</h2>
            <p style="font-size:1.1em;">
                Le serveur PVInsight est maintenant arrêté.<br><br>
                ✅ Vous pouvez fermer cet onglet ou le navigateur.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    time.sleep(1.2)
    os._exit(0)

def set_page_config(app_name: str, logo_png: Path):
    icon = "☀️"
    if logo_png and logo_png.exists():
        try:
            icon = Image.open(logo_png)
        except Exception:
            pass
    st.set_page_config(page_title=app_name, page_icon=icon, layout="wide")

def sidebar_global_settings():
    lang = st.session_state.get("lang", "fr")

    with st.sidebar:
        st.header(t("sidebar_settings", lang))

        # Language
        lang_choice = st.selectbox(
            t("sidebar_language", lang),
            ["fr", "en"],
            index=["fr", "en"].index(st.session_state["lang"]),
        )
        st.session_state["lang"] = lang_choice
        lang = lang_choice

        # Units
        st.subheader(t("option_units", lang))

        irr_options = ["W/m²", "kW/m²"]
        st.session_state["irradiance_unit"] = st.selectbox(
            t("irradiance_unit", lang),
            irr_options,
            index=irr_options.index(st.session_state["irradiance_unit"]),
        )

        en_options = ["kWh/m²", "Wh/m²"]
        st.session_state["energy_unit"] = st.selectbox(
            t("energy_unit", lang),
            en_options,
            index=en_options.index(st.session_state["energy_unit"]),
        )

        st.session_state["resample_hourly"] = st.checkbox(
            t("resample_hourly", lang),
            value=st.session_state["resample_hourly"],
        )

    return lang


def tool_header(title: str, back_to: str = "home", back_label: str = "⬅️ Home"):
    c1, c2, c3 = st.columns([7, 2, 1])
    with c1:
        st.title(title)
    with c2:
        if st.button(back_label, key=f"back_{back_to}", use_container_width=True):
            st.session_state["tool"] = back_to
            st.rerun()
    with c3:
        # petit bouton toujours visible
        if st.button("❌", key=f"quit_{title}", use_container_width=True):
            st.session_state["_quitting"] = True
            st.rerun()

def sidebar_quit_button(label: str = "Quit application"):
    st.sidebar.divider()
    if st.sidebar.button(label, use_container_width=True):
        _trigger_quit()

def header_quit_button(label: str = "❌ Quit"):
    # bouton compact, fait pour le header
    if st.button(label, key="quit_header_btn"):
        _trigger_quit()

def sidebar_tools_nav():
    """
    Sidebar navigation based on st.session_state["tool"].
    Keeps your 'hub/router' approach (no Streamlit multipage).
    """
    lang = st.session_state.get("lang", "fr")

    with st.sidebar:
        st.divider()
        st.header(t("sidebar_tools", lang))

        # --- Meteo ---
        st.subheader(t("sidebar_meteo", lang))
        if st.button(t("nav_tmy_analysis", lang), use_container_width=True):
            st.session_state["tool"] = "tmy_analysis"
            st.rerun()

        if st.button(t("nav_tmy_compare", lang), use_container_width=True):
            st.session_state["tool"] = "tmy_compare"
            st.rerun()

        # --- Production ---
        st.subheader(t("sidebar_production", lang))
        if st.button(t("nav_hourly_results", lang), use_container_width=True):
            st.session_state["tool"] = "hourly_results"
            st.rerun()
