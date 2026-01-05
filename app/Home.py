# app/Home.py
from __future__ import annotations

from _bootstrap import *  # noqa: F401,F403

from config import APP_NAME, LOGO_PNG, DEFAULT_LANG
from app.ui import (
    init_state,
    set_page_config,
    sidebar_global_settings,
    view_home,
    view_tmy_analysis,
    view_tmy_compare,
    view_hourly_results,
)

from app.ui.layout import sidebar_quit_button, sidebar_tools_nav, _render_quit_screen_and_exit

import streamlit as st


def main():
    # state + page
    init_state()
    set_page_config(APP_NAME, LOGO_PNG)

    # sidebar (lang, units...)
    sidebar_global_settings()

    # sidebar navigation (tools)
    sidebar_tools_nav()

    # quit button
    sidebar_quit_button("❌ Quit PVInsight")
    _render_quit_screen_and_exit()


    # router
    tool = st.session_state.get("tool", "home")
    if tool == "tmy_analysis":
        view_tmy_analysis()
    elif tool == "tmy_compare":
        view_tmy_compare()
    elif tool == "hourly_results":
        view_hourly_results()
    else:
        view_home()



if __name__ == "__main__":
    main()
