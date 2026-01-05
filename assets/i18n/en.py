# assets/i18n/en.py

TEXTS = {
    # --- App ---
    "app_title": "PVInsight",
    "app_tagline": "Weather & PV production analysis tools",

    # --- Sidebar ---
    "sidebar_settings": "Settings",
    "sidebar_language": "Language",
    "sidebar_tools": "Tools",
    "sidebar_meteo": "Weather",
    "sidebar_production": "Production",

    # --- Navigation ---
    "nav_tmy_analysis": "🔎 TMY Analysis",
    "nav_tmy_compare": "🆚 TMY Comparison",
    "nav_hourly_results": "📈 Hourly Results (PVSyst)",

    # --- Home
    "home_title": "Home",
    "home_intro_title": "About",
    "home_intro_body": (
        "PVInsight bundles analysis tools for **Weather** and **PV Production** topics.\n\n"
        "**Weather (TMY)**\n"
        "- time series quality checks and consistency\n"
        "- statistics and visualizations\n"
        "- comparison of two sources (gaps, common period alignment)\n"
        "- time step handling (hourly / sub-hourly)\n"
        "- unit normalization (irradiance / energy)\n\n"
        "**Production (PVSyst Hourly Results)**\n"
        "- power threshold analysis\n"
        "- operating distribution (near Pmax, etc.)\n"
        "- inverter clipping (IL_Pmax / EOutInv)\n"
        "- **Excel** and **PDF** exports\n\n"
        "Goal: support **design**, **optimization**, and **loss analysis** "
        "(curtailment, clipping, PR drivers, etc.)."
    ),

    "home_tools_title": "Tools",
    "home_tools_subtitle": "V1 — Weather + Production",
    "home_howto_title": "How it works",
    "home_howto_body": (
        "1) Pick a tool above\n"
        "2) Upload your file\n"
        "3) Tune options (units, hourly aggregation, threshold…)\n"
        "4) Review charts and download Excel/PDF"
    ),


    # --- Titles ---
    "tmy_analysis_title": "TMY Analysis",
    "tmy_compare_title": "TMY Comparison",
    "hourly_results_title": "Hourly Results Analysis",

    # --- Uploads ---
    "upload_one": "Upload a TMY file (PVSyst CSV)",
    "upload_two_a": "Upload TMY #1",
    "upload_two_b": "Upload TMY #2",
    "upload_hourly": "Upload an Hourly Results file (PVSyst CSV)",

    # --- Options / Units ---
    "option_units": "Units",
    "irradiance_unit": "Irradiance unit (instantaneous values)",
    "energy_unit": "Integrated energy unit (summary)",
    "resample_hourly": (
        "Aggregate to hourly if sub-hourly "
        "(sum irradiance / mean temperature & wind)"
    ),

    # --- Actions ---
    "run_analysis": "Run analysis",
    "run_compare": "Run comparison",
    "run_hourly": "Run Hourly Results analysis",

    # --- Outputs ---
    "report_ready": "Report successfully generated.",
    "download_pdf": "Download PDF",
    "download_excel": "Download Excel",

    # --- Misc ---
    "warnings_title": "Warnings / checks",
    "logs_title": "Logs",
    "show_dataframe": "Show data preview",
    "preview": "Preview",

    # --- Hourly Results ---
    "hourly_results_title": "Hourly Results",
    "hourly_title": "Hourly Results — Summary",

    "hourly_metric_threshold": "Threshold (kW)",
    "hourly_metric_hours_prod": "Production hours",
    "hourly_metric_hours_above": "Hours > threshold",
    "hourly_metric_pct_above": "% prod > threshold",
    "hourly_metric_energy_above": "Energy > threshold (kWh)",

    "hourly_section_threshold": "Threshold analysis",
    "hourly_help_threshold_title": "ℹ️ What does this analysis represent?",
    "hourly_help_threshold_body": """
    This analysis shows **how many hours the plant exceeds a given power threshold**.

    - The threshold is a **reference power** (grid limit, contractual limit, or critical level).
    - Only **actual production hours** are considered.
    - Hours with **E_Grid ≤ 0** are excluded.

    🎯 Goals:
    - quantify peak occurrences
    - assess saturation / limitation risk
    - support grid connection sizing and curtailment discussions
    """,

    "hourly_help_threshold_pct_title": "ℹ️ How to interpret this chart?",
    "hourly_help_threshold_pct_body": """
    For each month, this chart shows the share of production time
    during which the plant **exceeds the chosen threshold**.

    - The percentage is computed **only over production hours**.
    - It allows month-to-month comparison regardless of month length.
    """,

    "hourly_chart_monthly_hours": "Monthly distribution — Hours > threshold",
    "hourly_chart_seasonal_hours": "Seasonal distribution — Hours > threshold",
    "hourly_chart_monthly_pct": "% of prod time > threshold (monthly)",

    "hourly_section_clipping": "Inverter clipping",
    "hourly_help_clipping_title": "ℹ️ What is inverter clipping and why it matters?",
    "hourly_help_clipping_body": """
    Inverter clipping is energy lost because the inverter reaches its maximum power
    while the PV field could produce more.

    Based on PVSyst outputs:
    - EOutInv: inverter AC output
    - IL_Pmax: energy lost due to inverter saturation
    """,
    "hourly_clipping_none": "No inverter clipping detected over the analyzed period.",
    "hourly_clipping_unavailable": "Clipping unavailable (missing EOutInv / IL_Pmax columns).",
    "hourly_metric_clip_energy": "Clipped energy (kWh)",
    "hourly_metric_clip_pct": "% of inverter potential",
    "hourly_metric_clip_hours": "Clipping hours",
    "hourly_chart_clip_monthly": "Clipped energy (IL_Pmax) — Monthly",

    "hourly_section_powerdist": "Power distribution",
    "hourly_help_powerdist_title": "ℹ️ What does this analysis represent?",
    "hourly_help_powerdist_body": """
    This analysis shows how operating time is distributed across power levels.

    - Only production hours are included.
    - Power is expressed as % of the observed maximum.
    """,
    "hourly_chart_powerdist": "Operating time distribution (%)",
    "hourly_powerdist_none": "Power distribution: no production (E_Grid <= 0) or insufficient data.",

    "downloads_title": "Downloads",
    "download_excel": "📥 Download Excel",
    "download_pdf": "📥 Download PDF",

}
