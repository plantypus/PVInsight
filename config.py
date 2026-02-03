# config.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


APP_NAME = "PVInsight"
APP_VERSION = "0.1.0"

# --- Paths (project root = folder containing this file) ---
PROJECT_ROOT = Path(__file__).resolve().parent
ASSETS_DIR = PROJECT_ROOT / "assets"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# --- Assets ---
LOGO_PNG = ASSETS_DIR / "logo.png"
LOGO_ICO = ASSETS_DIR / "logo.ico"

# --- Internationalization (future-proof) ---
DEFAULT_LANG = "fr"  # 'fr' or 'en' later via assets/i18n

# --- Defaults for meteorological normalization ---
DEFAULT_TARGET_IRRADIANCE_UNIT = "W/m²"  # can be "W/m²"
DEFAULT_RESAMPLE_TO_HOURLY_IF_SUBHOURLY = True

# --- Output policy ---
OUTPUT_MODE = "latest"  # "runs" (timestamped) or "latest" (overwrite)


@dataclass(frozen=True)
class MeteoDefaults:
    target_irradiance_unit: str = DEFAULT_TARGET_IRRADIANCE_UNIT
    resample_to_hourly_if_subhourly: bool = DEFAULT_RESAMPLE_TO_HOURLY_IF_SUBHOURLY


METEO_DEFAULTS = MeteoDefaults()

# --- Defaults for production / Hourly Results ---
DEFAULT_THRESHOLD_KW = 500.0

# PVSyst Hourly Results date parsing (csv "date" column)
# Example: "01/01/90 09:00"
PVSYST_DATE_FMT = "%d/%m/%y %H:%M"

# PDF
PDF_PAGE_SIZE = "A4"
