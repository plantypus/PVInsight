# core/meteo/tmy_analysis.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Union

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from utils.paths import RunPaths, make_run_folders
from utils.validation import DataQuality
from utils.run_log import write_run_log
from utils.energy import annual_irradiation, EnergySummary

from core.meteo.tmy_pvsyst import TMYDataset, read_tmy_pvsyst


TextSource = Union[str, Path, bytes]


@dataclass(frozen=True)
class TMYAnalysisResult:
    dataset: TMYDataset
    stats: pd.DataFrame
    energy: EnergySummary
    report_pdf: Path
    log_path: Path
    run_dir: Path


def compute_basic_stats(df: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in ["ghi", "dni", "dhi", "temp"] if c in df.columns]
    stats = df[cols].agg(["mean", "min", "max"]).transpose()
    stats = stats.rename(columns={"mean": "Mean", "min": "Min", "max": "Max"})
    return stats


def generate_pdf_onepage(
    df: pd.DataFrame,
    stats: pd.DataFrame,
    energy: EnergySummary,
    units_by_col: Dict[str, str],
    quality: DataQuality,
    file_label: str,
    output_pdf: Path,
) -> None:
    fig = plt.figure(figsize=(8.27, 11.69))  # A4 portrait
    fig.suptitle("TMY Report (PVSyst)", fontsize=18, fontweight="bold", y=0.96)

    # --- File info ---
    ax0 = fig.add_axes([0.06, 0.86, 0.88, 0.08])
    ax0.axis("off")
    header = (
        f"File: {file_label}\n"
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    ax0.text(0.0, 0.6, header, ha="left", va="center", fontsize=10, family="monospace")

    # --- Data quality ---
    ax1 = fig.add_axes([0.06, 0.70, 0.88, 0.16])
    ax1.axis("off")
    dq_text = "DATA QUALITY\n\n"
    dq_text += f"Rows: {quality.n_rows:,}\n"
    dq_text += f"Period: {quality.start}  →  {quality.end}\n"
    if quality.n_nan == 0 and quality.n_nat == 0:
        dq_text += "Missing values: none\n"
    else:
        dq_text += f"Missing values: {quality.n_nan} NaN, {quality.n_nat} NaT\n"
    if quality.warning:
        dq_text += f"\nWarning: {quality.warning}\n"
    ax1.text(0.0, 0.95, dq_text, ha="left", va="top", fontsize=10, family="monospace")

    # --- Stats + Energy ---
    ax2 = fig.add_axes([0.06, 0.53, 0.88, 0.17])
    ax2.axis("off")
    st_text = "STATISTICS (mean / min / max)\n\n"
    for var in ["ghi", "dni", "dhi", "temp"]:
        if var in stats.index:
            unit = units_by_col.get(var, "")
            mean, mn, mx = stats.loc[var, ["Mean", "Min", "Max"]]
            st_text += f"{var.upper():<6} {mean:>10.2f} {unit}   (min {mn:.2f}, max {mx:.2f})\n"

    st_text += "\nANNUAL IRRADIATION (integrated)\n"
    if energy.annual_ghi is not None:
        st_text += f"GHI: {energy.annual_ghi:.1f} {energy.unit}\n"
    if energy.annual_dni is not None:
        st_text += f"DNI: {energy.annual_dni:.1f} {energy.unit}\n"
    if energy.annual_dhi is not None:
        st_text += f"DHI: {energy.annual_dhi:.1f} {energy.unit}\n"

    ax2.text(0.0, 0.95, st_text, ha="left", va="top", fontsize=10, family="monospace")

    # --- Plot 1: GHI ---
    if "ghi" in df.columns:
        ax3 = fig.add_axes([0.10, 0.30, 0.80, 0.18])
        ax3.set_title("Global Horizontal Irradiance (GHI)", fontsize=12, pad=8)
        ax3.plot(df["datetime"], df["ghi"], lw=1.0)
        ax3.xaxis.set_major_locator(mdates.MonthLocator())
        ax3.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
        ax3.set_xlabel("Month")
        ax3.set_ylabel(f"GHI ({units_by_col.get('ghi','')})")
        ax3.grid(True, linestyle="--", alpha=0.35)

    # --- Plot 2: Temperature ---
    if "temp" in df.columns:
        ax4 = fig.add_axes([0.10, 0.08, 0.80, 0.18])
        ax4.set_title("Ambient Temperature", fontsize=12, pad=8)
        ax4.plot(df["datetime"], df["temp"], lw=1.0)
        ax4.xaxis.set_major_locator(mdates.MonthLocator())
        ax4.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
        ax4.set_xlabel("Month")
        ax4.set_ylabel(f"Temp ({units_by_col.get('temp','')})")
        ax4.grid(True, linestyle="--", alpha=0.35)

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_pdf, dpi=250)
    plt.close(fig)


def analyze_tmy_source(
    source: TextSource,
    source_name: str,
    outputs_dir: Path,
    output_mode: str = "runs",
    target_irradiance_unit: str = "kW/m²",
    energy_unit: str = "kWh/m²",
    resample_hourly_if_subhourly: bool = True,
) -> TMYAnalysisResult:
    tool_name = "TMY_Analysis"
    run: RunPaths = make_run_folders(outputs_dir, tool_name=tool_name, mode=output_mode)

    dataset = read_tmy_pvsyst(
        source,
        source_name=source_name,
        target_irradiance_unit=target_irradiance_unit,
        resample_hourly_if_subhourly=resample_hourly_if_subhourly,
    )

    stats = compute_basic_stats(dataset.df)

    energy = annual_irradiation(
        dataset.df,
        units_by_col=dataset.units_by_col,
        step_minutes=dataset.time_step_minutes,
        energy_unit=energy_unit,
    )
    dataset_warnings = dataset.warnings + energy.warnings

    pdf_path = run.reports_dir / f"{Path(source_name).stem}__TMY_Report.pdf"
    generate_pdf_onepage(
        dataset.df, stats, energy, dataset.units_by_col, dataset.quality,
        file_label=dataset.source_name,
        output_pdf=pdf_path,
    )

    log_path = run.logs_dir / f"{Path(source_name).stem}__TMY_Analysis.log"
    write_run_log(
        log_path=log_path,
        tool_name=tool_name,
        sources=[source_name],
        header_info=dataset.header_info,
        units_by_col=dataset.units_by_col,
        time_step_minutes=dataset.time_step_minutes,
        quality=dataset.quality,
        warnings=dataset_warnings,
    )

    # Return same dataset but with extended warnings visible to UI if needed
    dataset = TMYDataset(
        df=dataset.df,
        header_info=dataset.header_info,
        units_by_col=dataset.units_by_col,
        time_step_minutes=dataset.time_step_minutes,
        quality=dataset.quality,
        source_name=dataset.source_name,
        warnings=dataset_warnings,
    )

    return TMYAnalysisResult(
        dataset=dataset,
        stats=stats,
        energy=energy,
        report_pdf=pdf_path,
        log_path=log_path,
        run_dir=run.run_dir,
    )
