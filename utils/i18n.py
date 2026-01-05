# utils/i18n.py
from __future__ import annotations

from importlib import import_module
from typing import Dict


_CACHE: Dict[str, Dict[str, str]] = {}


def load_texts(lang: str) -> Dict[str, str]:
    """
    Load assets/i18n/<lang>.py which must expose TEXTS dict.
    """
    lang = (lang or "fr").lower()
    if lang not in {"fr", "en"}:
        lang = "fr"

    if lang in _CACHE:
        return _CACHE[lang]

    mod = import_module(f"assets.i18n.{lang}")
    texts = getattr(mod, "TEXTS", {})
    if not isinstance(texts, dict):
        texts = {}

    _CACHE[lang] = texts
    return texts


def t(key: str, lang: str, default: str = "") -> str:
    texts = load_texts(lang)
    return texts.get(key, default or key)
