from __future__ import annotations

import streamlit as st


def uploader_one(label: str, *, key: str, types: list[str] | None = None):
    return st.file_uploader(label, type=types, key=key)


def uploader_two(label_a: str, label_b: str, key_a: str, key_b: str, types: list[str] | None = None):
    c1, c2 = st.columns([1, 1])
    with c1:
        up1 = st.file_uploader(label_a, type=types, key=key_a)
    with c2:
        up2 = st.file_uploader(label_b, type=types, key=key_b)
    return up1, up2


def run_button(label: str, *, key: str | None = None) -> bool:
    return st.button(label, key=key)
