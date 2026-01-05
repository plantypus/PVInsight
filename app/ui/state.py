# app/ui/state.py
from __future__ import annotations
import streamlit as st

DEFAULTS = {
    "tool": "home",
    "lang": "fr",
    "irradiance_unit": "W/m²",
    "energy_unit": "kWh/m²",
    "resample_hourly": True,
}

def init_state():
    for k, v in DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = v

def get_global_settings() -> dict:
    return {
        "lang": st.session_state.get("lang", DEFAULTS["lang"]),
        "irradiance_unit": st.session_state.get("irradiance_unit", DEFAULTS["irradiance_unit"]),
        "energy_unit": st.session_state.get("energy_unit", DEFAULTS["energy_unit"]),
        "resample_hourly": st.session_state.get("resample_hourly", DEFAULTS["resample_hourly"]),
    }

def set_tool(tool_name: str):
    st.session_state["tool"] = tool_name
    st.rerun()
