from __future__ import annotations

from typing import Callable, Dict
import pandas as pd

from .hourly_models import AnalysisContext
from utils import check_required_columns, suggest_similar_columns  # adapte si besoin


AnalysisFunc = Callable[[AnalysisContext], None]
ANALYSIS_REGISTRY: Dict[str, AnalysisFunc] = {}


def register_analysis(analysis_id: str, func: AnalysisFunc) -> None:
    ANALYSIS_REGISTRY[analysis_id] = func


def register_analyses() -> None:
    register_analysis("threshold", analyze_threshold)
    register_analysis("power_distribution", analyze_power_distribution)
    register_analysis("inverter_clipping", analyze_inverter_clipping)


def run_all_analyses(context: AnalysisContext) -> None:
    for func in ANALYSIS_REGISTRY.values():
        func(context)


def analyze_threshold(context: AnalysisContext) -> None:
    df = context.df_raw.copy()
    threshold_kw = float(context.options.threshold_kw)

    df_prod = df[df["E_Grid"] > 0].copy()
    df_above = df[df["E_Grid"] > threshold_kw].copy()

    hours_prod = int(len(df_prod))
    hours_above = int(len(df_above))

    pct_above_global = 100.0 * hours_above / hours_prod if hours_prod > 0 else 0.0

    summary = {
        "threshold_kw": threshold_kw,
        "hours_prod": hours_prod,
        "hours_above": hours_above,
        "pct_above_prod_time": pct_above_global,
        "energy_kwh": float(df_above["E_Grid"].sum()),
    }

    month_map = {
        1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
        5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
        9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
    }

    df_above["month"] = df_above.index.month
    monthly = (
        df_above.groupby("month", observed=False)["E_Grid"]
        .agg(hours_above="count", energy_kwh="sum")
        .reset_index()
    )
    monthly["month_name"] = monthly["month"].map(month_map)
    monthly = monthly[["month_name", "hours_above", "energy_kwh"]]

    df_above["season"] = df_above.index.month.map({
        12: "Hiver", 1: "Hiver", 2: "Hiver",
        3: "Printemps", 4: "Printemps", 5: "Printemps",
        6: "Été", 7: "Été", 8: "Été",
        9: "Automne", 10: "Automne", 11: "Automne"
    })
    seasonal = (
        df_above.groupby("season", observed=False)["E_Grid"]
        .agg(hours_above="count", energy_kwh="sum")
        .reset_index()
    )

    df_prod["month"] = df_prod.index.month
    monthly_pct = (
        df_above.groupby("month", observed=False).size()
        / df_prod.groupby("month", observed=False).size()
        * 100
    ).fillna(0).reset_index(name="pct_above")

    monthly_pct["month_name"] = monthly_pct["month"].map(month_map)
    monthly_pct = monthly_pct[["month_name", "pct_above"]]

    context.results["threshold"] = {
        "summary": summary,
        "monthly": monthly,
        "seasonal": seasonal,
        "monthly_pct": monthly_pct,
    }


def analyze_power_distribution(context: AnalysisContext) -> None:
    df = context.df_raw.copy()
    df = df[df["E_Grid"] > 0]

    if df.empty:
        context.results["power_distribution"] = None
        return

    p_max = df["E_Grid"].max()
    df["ratio"] = df["E_Grid"] / p_max

    bins = [0, 0.5, 0.7, 0.9, 1.01]
    labels = ["< 50 %", "50–70 %", "70–90 %", "> 90 %"]

    df["class"] = pd.cut(df["ratio"], bins=bins, labels=labels)

    summary = (
        df.groupby("class", observed=False)["E_Grid"]
        .agg(hours=("count"), energy_kwh=("sum"))
        .reset_index()
    )
    summary["pct_time"] = summary["hours"] / summary["hours"].sum() * 100

    context.results["power_distribution"] = {"p_max": p_max, "summary": summary}


def analyze_inverter_clipping(context: AnalysisContext) -> None:
    df = context.df_raw.copy()
    required_cols = ["EOutInv", "IL_Pmax"]

    ok, missing = check_required_columns(df.columns.tolist(), required_cols)
    if not ok:
        context.results["inverter_clipping"] = {
            "available": False,
            "missing_columns": missing,
            "suggestions": suggest_similar_columns(df.columns.tolist(), missing),
        }
        return

    df = df[(df["EOutInv"] > 0) | (df["IL_Pmax"] > 0)].copy()
    if df.empty:
        context.results["inverter_clipping"] = {"available": True, "empty": True}
        return

    df["E_potential"] = df["EOutInv"] + df["IL_Pmax"]
    total_potential = df["E_potential"].sum()
    total_clipped = df["IL_Pmax"].sum()
    pct_clipping = 100.0 * total_clipped / total_potential if total_potential > 0 else 0.0
    hours_clipping = int((df["IL_Pmax"] > 0).sum())

    month_map = {
        1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
        5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
        9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
    }

    df["month"] = df.index.month
    monthly = (
        df.groupby("month", observed=False)[["IL_Pmax", "E_potential"]]
        .sum()
        .reset_index()
    )
    monthly["month_name"] = monthly["month"].map(month_map)
    monthly["pct_clipping"] = (monthly["IL_Pmax"] / monthly["E_potential"] * 100).fillna(0)

    monthly = monthly[["month_name", "IL_Pmax", "pct_clipping"]]

    context.results["inverter_clipping"] = {
        "available": True,
        "summary": {
            "energy_clipped_kwh": float(total_clipped),
            "pct_of_inverter_output": pct_clipping,
            "hours_clipping": hours_clipping,
        },
        "monthly": monthly,
    }
