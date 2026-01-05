# export_pdf.py

from pathlib import Path
from datetime import datetime
import tempfile

import matplotlib.pyplot as plt

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle,
    Spacer, Image
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors

from .hourly_models import AnalysisContext
from config import APP_NAME
from utils import format_number


# =========================================================
# GRAPHIQUES (MATPLOTLIB → PNG)
# =========================================================

def _generate_monthly_chart(monthly_df, output_png: Path) -> Path:
    """Graphe mensuel Heures > seuil (équivalent V1)."""
    width = 5.0
    height = 2.8

    fig, ax = plt.subplots(figsize=(width, height))
    ax.bar(monthly_df["month_name"], monthly_df["hours_above"])
    ax.set_title("Répartition mensuelle – Heures > seuil", fontsize=10)
    ax.set_ylabel("Heures", fontsize=9)
    plt.xticks(rotation=45, ha="right", fontsize=8)
    plt.tight_layout()
    plt.savefig(output_png, dpi=200)
    plt.close(fig)

    return output_png


# =========================================================
# EXPORT PDF GLOBAL (DYNAMIQUE)
# =========================================================

def export_pdf(context: AnalysisContext, pdf_path: Path) -> None:
    """
    PDF 1 page (tant que possible), dynamique :
    - Synthèse générale
    - Analyse seuil (tableau + graphe mensuel)
    - % du temps > seuil par mois
    - Distribution de puissance (si présente)
    """

    if "threshold" not in context.results:
        raise ValueError("Analyse 'threshold' absente — impossible de générer le PDF.")

    threshold_res = context.results["threshold"]
    summary = threshold_res["summary"]
    monthly = threshold_res["monthly"]
    monthly_pct = threshold_res.get("monthly_pct")

    # -----------------------------------------------------
    # Génération graphe mensuel
    # -----------------------------------------------------
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        chart_png = tmpdir / f"{pdf_path.stem}_monthly.png"
        _generate_monthly_chart(monthly, chart_png)

        # -------------------------------------------------
        # Document PDF
        # -------------------------------------------------
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm
        )

        styles = getSampleStyleSheet()
        elems = []

        # =================================================
        # TITRE
        # =================================================
        elems.append(Paragraph(f"<b>{APP_NAME}</b>", styles["Title"]))
        elems.append(Spacer(1, 10))

        # =================================================
        # SYNTHÈSE GÉNÉRALE
        # =================================================
        elems.append(Paragraph("<b>Synthèse générale</b>", styles["Heading2"]))
        elems.append(Spacer(1, 6))

        synth = [
            ["Version PVSyst", context.general_info.get("PVSyst_version", "")],
            ["Fichier analysé", context.input_file.name],
            ["Date de simulation", context.general_info.get("Simulation_date", "")],
            ["Seuil (kW)", format_number(summary["threshold_kw"], 1)],
            ["Heures de fonctionnement (h)", format_number(summary["hours_prod"], 0)],
            ["Heures > seuil (annuel)", format_number(summary["hours_above"], 0)],
            ["Fonctionnement > seuil (%)", f"{summary['pct_above_prod_time']:.1f} %"],
            ["Énergie > seuil (kWh/an)", format_number(summary["energy_kwh"], 0)],
        ]

        elems.append(_styled_table(synth, [7.5 * cm, 6.5 * cm]))
        elems.append(Spacer(1, 10))

        # =================================================
        # SYNTHÈSE TEMPORELLE — TABLEAU MENSUEL
        # =================================================
        elems.append(Paragraph("<b>Synthèse temporelle</b>", styles["Heading2"]))
        elems.append(Spacer(1, 6))

        monthly_data = [["Mois", "Heures > seuil (h)", "Énergie (kWh)"]]
        for _, row in monthly.iterrows():
            monthly_data.append([
                row["month_name"],
                format_number(row["hours_above"], 0),
                format_number(row["energy_kwh"], 0),
            ])

        elems.append(_styled_table(monthly_data, [4.5 * cm, 4.5 * cm, 4.5 * cm]))
        elems.append(Spacer(1, 8))

        # =================================================
        # % DU TEMPS > SEUIL PAR MOIS
        # =================================================
        if monthly_pct is not None:
            elems.append(Paragraph("<b>% du temps de fonctionnement > seuil</b>", styles["Heading3"]))
            elems.append(Spacer(1, 6))

            pct_data = [["Mois", "% du temps > seuil"]]
            for _, row in monthly_pct.iterrows():
                pct_data.append([
                    row["month_name"],
                    f"{row['pct_above']:.1f} %",
                ])

            elems.append(_styled_table(pct_data, [6.0 * cm, 6.0 * cm]))
            elems.append(Spacer(1, 8))

        # =================================================
        # GRAPHE MENSUEL (UNIQUE)
        # =================================================
        img_width = 13.0 * cm
        img_height = 6.0 * cm
        elems.append(Image(str(chart_png), width=img_width, height=img_height))

        # =================================================
        # DISTRIBUTION DE PUISSANCE
        # =================================================
        power_dist = context.results.get("power_distribution")
        if power_dist:
            elems.append(Spacer(1, 10))
            elems.append(Paragraph("<b>Distribution de puissance</b>", styles["Heading2"]))
            elems.append(Spacer(1, 6))

            dist_data = [["Classe", "% du temps", "Énergie (kWh)"]]
            for _, row in power_dist["summary"].iterrows():
                dist_data.append([
                    row["class"],
                    f"{row['pct_time']:.1f} %",
                    format_number(row["energy_kwh"], 0),
                ])

            elems.append(_styled_table(dist_data, [5.0 * cm, 4.0 * cm, 4.0 * cm]))

        # =================================================
        # FOOTER
        # =================================================
        now = datetime.now().strftime("%d/%m/%Y %H:%M")

        def footer(canvas, _doc):
            canvas.setFont("Helvetica", 8)
            canvas.setFillColor(colors.grey)
            canvas.drawRightString(19 * cm, 1.2 * cm, now)

        doc.build(elems, onFirstPage=footer, onLaterPages=footer)


# =========================================================
# TABLE STYLÉE
# =========================================================

def _styled_table(data, col_widths):
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t
