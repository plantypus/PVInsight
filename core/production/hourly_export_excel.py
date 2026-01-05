# export_excel.py

from pathlib import Path
import pandas as pd

from .hourly_models import AnalysisContext
from utils import format_number


# =========================================================
# EXPORT EXCEL GLOBAL (DYNAMIQUE)
# =========================================================

def export_excel(context: AnalysisContext, output: Path) -> None:
    """
    Export Excel dynamique :
    - Synthèse globale (équivalent V1)
    - Analyse seuil (mensuel, saisonnier, % mensuel)
    - Distribution de puissance (si présente)
    - Données horaires
    - Unités
    """

    if "threshold" not in context.results:
        raise ValueError("Analyse 'threshold' absente — export Excel impossible.")

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        workbook = writer.book

        _export_synthese(writer, context)
        _export_threshold_excel(writer, workbook, context.results["threshold"])

        if "power_distribution" in context.results:
            _export_power_distribution_excel(
                writer, context.results["power_distribution"]
            )

        context.df_raw.to_excel(writer, sheet_name="Données horaires", index=True)
        _export_units(writer, context)


# =========================================================
# SYNTHÈSE GLOBALE
# =========================================================

def _export_synthese(writer, context: AnalysisContext) -> None:
    summary = context.results["threshold"]["summary"]

    df = pd.DataFrame({
        "Clé": [
            "Version PVSyst",
            "Fichier analysé",
            "Date de simulation",
            "Seuil de puissance (kW)",
            "Heures de fonctionnement (h)",
            "Heures > seuil (h)",
            "Temps de fonctionnement > seuil (%)",
            "Énergie produite > seuil (kWh)",
        ],
        "Valeur": [
            context.general_info.get("PVSyst_version", ""),
            context.input_file.name,
            context.general_info.get("Simulation_date", ""),
            format_number(summary["threshold_kw"], 1),
            format_number(summary["hours_prod"], 0),
            format_number(summary["hours_above"], 0),
            f"{summary['pct_above_prod_time']:.1f} %",
            format_number(summary["energy_kwh"], 0),
        ],
    })

    df.to_excel(writer, sheet_name="Synthèse", index=False)


# =========================================================
# ANALYSE SEUIL — EXCEL
# =========================================================

def _export_threshold_excel(writer, workbook, res: dict) -> None:
    monthly = res["monthly"]
    seasonal = res["seasonal"]
    monthly_pct = res.get("monthly_pct")

    # -----------------------------------------------------
    # Mensuel
    # -----------------------------------------------------
    sheet_month = "Seuil — Mensuel"
    monthly.to_excel(writer, sheet_name=sheet_month, index=False)

    worksheet = writer.sheets[sheet_month]

    chart_month = workbook.add_chart({"type": "column"})
    chart_month.add_series({
        "name": "Heures > seuil",
        "categories": [sheet_month, 1, 0, monthly.shape[0], 0],
        "values":     [sheet_month, 1, 1, monthly.shape[0], 1],
    })
    chart_month.set_title({"name": "Répartition mensuelle – Heures > seuil"})
    chart_month.set_x_axis({"name": "Mois"})
    chart_month.set_y_axis({"name": "Heures"})

    worksheet.insert_chart("E2", chart_month)

    # -----------------------------------------------------
    # Saisonnier
    # -----------------------------------------------------
    sheet_season = "Seuil — Saisonnier"
    seasonal.to_excel(writer, sheet_name=sheet_season, index=False)

    worksheet = writer.sheets[sheet_season]

    chart_season = workbook.add_chart({"type": "column"})
    chart_season.add_series({
        "name": "Heures > seuil",
        "categories": [sheet_season, 1, 0, seasonal.shape[0], 0],
        "values":     [sheet_season, 1, 1, seasonal.shape[0], 1],
    })
    chart_season.set_title({"name": "Répartition saisonnière – Heures > seuil"})
    chart_season.set_x_axis({"name": "Saison"})
    chart_season.set_y_axis({"name": "Heures"})

    worksheet.insert_chart("E2", chart_season)

    # -----------------------------------------------------
    # % mensuel > seuil
    # -----------------------------------------------------
    if monthly_pct is not None:
        df_pct = monthly_pct.copy()
        df_pct["% du temps > seuil"] = df_pct["pct_above"].map(
            lambda x: f"{x:.1f} %"
        )

        df_pct[["month_name", "% du temps > seuil"]].to_excel(
            writer, sheet_name="Seuil — % mensuel", index=False
        )


# =========================================================
# DISTRIBUTION DE PUISSANCE — EXCEL
# =========================================================

def _export_power_distribution_excel(writer, res: dict) -> None:
    df = res["summary"].copy()

    df["% du temps"] = df["pct_time"].map(lambda x: f"{x:.1f} %")
    df["Énergie (kWh)"] = df["energy_kwh"].map(
        lambda x: format_number(x, 0)
    )

    df[["class", "% du temps", "Énergie (kWh)"]].to_excel(
        writer, sheet_name="Distribution puissance",
        index=False
    )


# =========================================================
# UNITÉS
# =========================================================

def _export_units(writer, context: AnalysisContext) -> None:
    df_units = pd.DataFrame(
        [{"Paramètre": k, "Unité": v} for k, v in context.units_map.items()]
    )
    df_units.to_excel(writer, sheet_name="Unités", index=False)
