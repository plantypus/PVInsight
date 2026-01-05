# assets/i18n/fr.py

TEXTS = {
    # --- App ---
    "app_title": "PVInsight",
    "app_tagline": "Outils d’analyse Météo & Production PV",

    # --- Sidebar ---
    "sidebar_settings": "Paramètres",
    "sidebar_language": "Langue",
    "sidebar_tools": "Outils",
    "sidebar_meteo": "Météo",
    "sidebar_production": "Production",

    # --- Navigation ---
    "nav_tmy_analysis": "🔎 Analyse TMY",
    "nav_tmy_compare": "🆚 Comparaison TMY",
    "nav_hourly_results": "📈 Hourly Results (PVSyst)",

    # --- Home
    "home_title": "Accueil",
    "home_intro_title": "À propos",
    "home_intro_body": (
        "PVInsight regroupe des outils d’analyse pour les thématiques **Météo** et **Production PV**.\n\n"
        "**Météo (TMY)**\n"
        "- contrôle qualité et cohérence des séries\n"
        "- statistiques et visualisations\n"
        "- comparaison de deux sources (écarts, alignement des périodes)\n"
        "- gestion du pas de temps (horaire / sub-hourly)\n"
        "- normalisation des unités (irradiance / énergie)\n\n"
        "**Production (PVSyst Hourly Results)**\n"
        "- analyse de seuil de puissance\n"
        "- distribution de fonctionnement (proche Pmax, etc.)\n"
        "- clipping onduleur (IL_Pmax / EOutInv)\n"
        "- exports **Excel** et **PDF**\n\n"
        "Objectif : aider au **design**, à l’**optimisation** et à la **compréhension des pertes** "
        "(bridage, clipping, PR, etc.)."
    ),

    "home_tools_title": "Outils",
    "home_tools_subtitle": "V1 — Météo + Production",
    "home_howto_title": "Comment ça marche ?",
    "home_howto_body": (
        "1) Choisis un outil ci-dessus\n"
        "2) Importe ton fichier\n"
        "3) Ajuste les options (unités, agrégation horaire, seuil…)\n"
        "4) Consulte les graphiques puis télécharge Excel/PDF"
    ),

    # --- Titles ---
    "tmy_analysis_title": "Analyse TMY",
    "tmy_compare_title": "Comparaison TMY",
    "hourly_results_title": "Analyse Hourly Results",

    # --- Uploads ---
    "upload_one": "Importer un fichier TMY (CSV PVSyst)",
    "upload_two_a": "Importer le TMY #1",
    "upload_two_b": "Importer le TMY #2",
    "upload_hourly": "Importer un fichier Hourly Results (CSV PVSyst)",

    # --- Options / Units ---
    "option_units": "Unités",
    "irradiance_unit": "Unité irradiance (valeurs instantanées)",
    "energy_unit": "Unité énergie intégrée (bilan)",
    "resample_hourly": (
        "Agréger en horaire si sub-hourly "
        "(somme irradiance / moyenne température & vent)"
    ),

    # --- Actions ---
    "run_analysis": "Lancer l’analyse",
    "run_compare": "Lancer la comparaison",
    "run_hourly": "Lancer l’analyse Hourly Results",

    # --- Outputs ---
    "report_ready": "Rapport généré avec succès.",
    "download_pdf": "Télécharger le PDF",
    "download_excel": "Télécharger l’Excel",

    # --- Misc ---
    "warnings_title": "Avertissements / contrôles",
    "logs_title": "Logs",
    "show_dataframe": "Afficher un aperçu des données",
    "preview": "Aperçu",

    # --- Hourly Results ---
    "hourly_results_title": "Hourly Results",
    "hourly_title": "Hourly Results — Synthèse",

    "hourly_metric_threshold": "Seuil (kW)",
    "hourly_metric_hours_prod": "Heures prod",
    "hourly_metric_hours_above": "Heures > seuil",
    "hourly_metric_pct_above": "% prod > seuil",
    "hourly_metric_energy_above": "Énergie > seuil (kWh)",

    "hourly_section_threshold": "Analyse seuil",
    "hourly_help_threshold_title": "ℹ️ Que représente cette analyse ?",
    "hourly_help_threshold_body": """
    Cette analyse montre **combien d’heures la centrale dépasse un seuil de puissance donné**.

    - Le seuil correspond à une **puissance de référence** (ex. puissance de raccordement, seuil contractuel, ou puissance critique).
    - Seules les **heures de production réelle** sont prises en compte.
    - Les heures avec consommation auxiliaire (**E_Grid ≤ 0**) sont exclues du calcul.

    🎯 **Objectifs** :
    - identifier la fréquence des **pics de puissance**
    - évaluer le risque de **saturation / limitation**
    - fournir une base pour réfléchir au **dimensionnement du raccordement** ou à un éventuel écrêtage
    """,

    "hourly_help_threshold_pct_title": "ℹ️ Comment interpréter ce graphique ?",
    "hourly_help_threshold_pct_body": """
    Ce graphique représente, **pour chaque mois**, la part du temps de fonctionnement
    où la centrale **dépasse le seuil de puissance choisi**.

    - Le pourcentage est calculé **uniquement sur les heures où la centrale produit**.
    - Il permet de comparer les mois **indépendamment de leur durée**.
    - Un pourcentage élevé indique un **fonctionnement fréquent à forte puissance**.

    🎯 **Intérêt métier** :
    - repérer les périodes où la centrale est la plus sollicitée
    - identifier les mois critiques pour le **raccordement réseau**
    - aider à arbitrer un compromis entre **puissance déclarée** et **pertes par écrêtage**
    """,

    "hourly_chart_monthly_hours": "Répartition mensuelle – Heures > seuil",
    "hourly_chart_seasonal_hours": "Répartition saisonnière – Heures > seuil",
    "hourly_chart_monthly_pct": "% du temps de prod > seuil (mensuel)",

    "hourly_section_clipping": "Clipping onduleur",
    "hourly_help_clipping_title": "ℹ️ Qu’est-ce que le clipping onduleur et pourquoi c’est important ?",
    "hourly_help_clipping_body": """
    Le **clipping onduleur** correspond à l’énergie **perdue parce que l’onduleur atteint sa
    puissance maximale**, alors que le champ photovoltaïque pourrait produire davantage.

    Cette analyse repose directement sur les résultats PVSyst :
    - **EOutInv** : énergie réellement produite par l’onduleur
    - **IL_Pmax** : énergie perdue par limitation de puissance onduleur

    🎯 **Objectifs** :
    - quantifier l’énergie réellement écrêtée
    - identifier **quand** (et combien) ce clipping se produit
    - aider à raisonner le **dimensionnement DC/AC**
    - fournir une base pour réfléchir à l’optimisation de la **puissance de raccordement**
    """,
    "hourly_clipping_none": "Aucun clipping onduleur détecté sur la période analysée.",
    "hourly_clipping_unavailable": "Clipping indisponible (colonnes EOutInv / IL_Pmax absentes).",
    "hourly_metric_clip_energy": "Énergie écrêtée (kWh)",
    "hourly_metric_clip_pct": "% du potentiel onduleur",
    "hourly_metric_clip_hours": "Heures avec clipping",
    "hourly_chart_clip_monthly": "Énergie écrêtée (IL_Pmax) — Mensuel",

    "hourly_section_powerdist": "Distribution de puissance",
    "hourly_help_powerdist_title": "ℹ️ À quoi correspond cette analyse ?",
    "hourly_help_powerdist_body": """
    Cette analyse montre **comment se répartit le temps de fonctionnement de la centrale**
    selon son **niveau de puissance instantanée**.

    - Seules les heures où la centrale produit sont prises en compte.
    - La puissance est exprimée en **% de la puissance maximale observée**.
    - Chaque heure est classée dans une plage de fonctionnement.

    🎯 **Objectif** : identifier si la centrale fonctionne majoritairement
    à faible charge, à charge nominale ou proche de sa puissance maximale.
    """,
    "hourly_chart_powerdist": "Répartition du temps de fonctionnement (%)",
    "hourly_powerdist_none": "Distribution de puissance : pas de production (E_Grid <= 0) ou données insuffisantes.",

    "downloads_title": "Téléchargements",
    "download_excel": "📥 Télécharger Excel",
    "download_pdf": "📥 Télécharger le PDF",

}
