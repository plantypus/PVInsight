from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict
import pandas as pd


@dataclass
class AnalysisOptions:
    threshold_kw: float


@dataclass
class AnalysisContext:
    input_file: Path
    general_info: Dict[str, str]
    units_map: Dict[str, str]
    df_raw: pd.DataFrame

    options: AnalysisOptions
    results: Dict[str, Any] = field(default_factory=dict)
