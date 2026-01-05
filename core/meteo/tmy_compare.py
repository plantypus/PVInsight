# core/meteo/tmy_compare.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from utils.paths import RunPaths, make_run_folders
from utils.run_log import write_run_log
from utils.energy import annual_irradiation, EnergySummary
from core.meteo.tmy_pvsyst import TMYDataset, read_tmy_pvsyst


TextSource = Union[str, Path, bytes]


@dataclass(frozen=True)
class TMYCompareResult:
    ds1: TMYDataset
    ds2: TMYDataset
    diffs: Dict[str, Dict[str, float]]
    alert_flag: bool
    common_start: pd.Timestamp
    common_end: pd.Timestamp
    energy1: EnergySummary
    energy2: EnergySummary
    report_pdf: Path
    log_path: Path
    run_dir: Path


def align_common_period(df1: pd.DataFrame, df2: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Timestamp, pd.Timestamp]:
    start = max(df1["datetime"].min(), df2["datetime"].min())
    end = min(df1["datetime"].max(), df2["datetime"].max())
    df1a = df1[(df1["datetime"] >= start) & (df1["datetime"] <= end)].reset_index(drop=True)
    df2a = df2[(df2["datetime"] >= start) & (df2["datetime"] <= end)].reset_index(drop=True)
    return df1a, df2a, start, end


def compute_differences(df1: pd.DataFrame, df2: pd.DataFrame, threshold_pct: float = 5.0) -> Tuple[Dict[str, Dict[str, float]], bool]:
    common_vars = [c for c in ["ghi", "dni", "dhi", "temp", "wind_speed"] if c in df1.columns and c in df2.columns]
    results: Dict[str, Dict[str, float]] = {}
    alert = False

    for var in common_vars:
        diff_abs = (df1[var] - df2[var]).abs()
        denom = df2[var].replace(0, np.nan)
        diff_pct = (diff_abs / denom) * 100.0

        results[var] = {
            "mean_abs": float(np.nanmean(diff_abs)),
            "max_abs": float(np.nanmax(diff_abs)),
            "mean_pct": float(np.nanmean(diff_pct)),
            "max_pct": float(np.nanmax(diff_pct)),
        }

        if results[var]["mean_pct"] > threshold_pct:
            alert = True

    return results, alert


def generate_compare_pdf(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    name1: str,
    name2: str,
    diffs: Dict[str, Dict[str, float]],
    alert_flag: bool,
    energy1: EnergySummary,
    energy2: EnergySummary,
    output_pdf: Path,
) -> None:
    fig = plt.figure(figsize=(8.27, 11.69))
    fig.suptitle("TMY Comparison Report (PVSyst)", fontsize=16, fontweight="bold", y=0.97)

    # --- Text block ---
    ax_text = fig.add_axes([0.06, 0.76, 0.88, 0.18])
    ax_text.axis("off")

    txt = ""
    txt += f"File 1: {name1}\n"
    txt += f"File 2: {name2}\n"
    txt += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    # energy summary
    if energy1.annual_ghi is not None and energy2.annual_ghi is not None:
        txt += f"Annual GHI: {energy1.annual_ghi:.1f} vs {energy2.annual_ghi:.1f} {energy1.unit}\n"
    if energy1.annual_dni is not None and energy2.annual_dni is not None:
        txt += f"Annual DNI: {energy1.annual_dni:.1f} vs {energy2.annual_dni:.1f} {energy1.unit}\n"
    txt += "\nMean % differences (vs File 2):\n"
    for v in ["ghi", "dni", "dhi", "temp"]:
        if v in diffs:
            txt += f"  - {v.upper()}: {diffs[v]['mean_pct']:.2f}%\n"
    txt += "\n"
    txt += "ALERT: Significant discrepancies detected.\n" if alert_flag else "Differences look generally consistent.\n"

    ax_text.text(0.0, 1.0, txt, ha="left", va="top", fontsize=10, family="monospace")

    # --- Plots (stacked) ---
    vars_to_plot = [v for v in ["ghi", "dni", "temp"] if v in df1.columns and v in df2.columns]
    base_bottom = 0.10
    height = 0.17
    gap = 0.07

    for i, var in enumerate(vars_to_plot):
        bottom = base_bottom + (len(vars_to_plot) - 1 - i) * (height + gap)
        ax = fig.add_axes([0.10, bottom, 0.80, height])

        ax.plot(df1["datetime"], df1[var], lw=0.9, alpha=0.9, label="File 1")
        ax.plot(df2["datetime"], df2[var], lw=0.9, alpha=0.9, label="File 2")

        ax.set_title(var.upper(), fontsize=12, pad=6)
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
        ax.grid(True, linestyle="--", alpha=0.35)
        ax.legend(loc="upper right", fontsize=8)

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_pdf, dpi=250)
    plt.close(fig)


def compare_tmy_sources(
    source1: TextSource,
    name1: str,
    source2: TextSource,
    name2: str,
    outputs_dir: Path,
    output_mode: str = "runs",
    target_irradiance_unit: str = "kW/m²",
    energy_unit: str = "kWh/m²",
    resample_hourly_if_subhourly: bool = True,
    threshold_pct: float = 5.0,
) -> TMYCompareResult:
    tool_name = "TMY_Compare"
    run: RunPaths = make_run_folders(outputs_dir, tool_name=tool_name, mode=output_mode)

    ds1 = read_tmy_pvsyst(
        source1,
        source_name=name1,
        target_irradiance_unit=target_irradiance_unit,
        resample_hourly_if_subhourly=resample_hourly_if_subhourly,
    )
    ds2 = read_tmy_pvsyst(
        source2,
        source_name=name2,
        target_irradiance_unit=target_irradiance_unit,
        resample_hourly_if_subhourly=resample_hourly_if_subhourly,
    )

    df1a, df2a, start, end = align_common_period(ds1.df, ds2.df)
    diffs, alert_flag = compute_differences(df1a, df2a, threshold_pct=threshold_pct)

    energy1 = annual_irradiation(ds1.df, ds1.units_by_col, ds1.time_step_minutes, energy_unit=energy_unit)
    energy2 = annual_irradiation(ds2.df, ds2.units_by_col, ds2.time_step_minutes, energy_unit=energy_unit)

    all_warnings = ds1.warnings + ds2.warnings + energy1.warnings + energy2.warnings

    pdf_path = run.reports_dir / f"TMY_Comparison__{Path(name1).stem}__VS__{Path(name2).stem}.pdf"
    generate_compare_pdf(df1a, df2a, ds1.source_name, ds2.source_name, diffs, alert_flag, energy1, energy2, pdf_path)

    log_path = run.logs_dir / f"TMY_Compare__{Path(name1).stem}__VS__{Path(name2).stem}.log"
    write_run_log(
        log_path=log_path,
        tool_name=tool_name,
        sources=[name1, name2],
        header_info=None,
        units_by_col=None,
        time_step_minutes=60,  # after optional resample it's hourly; keep simple here
        quality=None,
        warnings=all_warnings,
    )

    return TMYCompareResult(
        ds1=ds1,
        ds2=ds2,
        diffs=diffs,
        alert_flag=alert_flag,
        common_start=start,
        common_end=end,
        energy1=energy1,
        energy2=energy2,
        report_pdf=pdf_path,
        log_path=log_path,
        run_dir=run.run_dir,
    )
