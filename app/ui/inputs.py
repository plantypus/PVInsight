# app/ui/inputs.py
from __future__ import annotations
import streamlit as st

def uploader_one(label: str, key: str):
    return st.file_uploader(label, type=["csv", "txt"], key=key)

def uploader_two(label1: str, label2: str, key1: str, key2: str):
    up1 = st.file_uploader(label1, type=["csv", "txt"], key=key1)
    up2 = st.file_uploader(label2, type=["csv", "txt"], key=key2)
    return up1, up2

def run_button(label: str) -> bool:
    return st.button(label, type="primary")
