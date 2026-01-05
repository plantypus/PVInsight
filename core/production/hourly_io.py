from __future__ import annotations

from typing import Dict, List, Tuple
import pandas as pd

from config import PVSYST_DATE_FMT


def _decode_bytes(source: bytes) -> str:
    # PVSyst exports are often latin-1
    for enc in ("latin-1", "utf-8"):
        try:
            return source.decode(enc)
        except Exception:
            continue
    # fallback (will keep running but may mangle some chars)
    return source.decode("latin-1", errors="ignore")


def parse_general_info(lines: List[str]) -> Dict[str, str]:
    info: Dict[str, str] = {}
    if lines:
        info["PVSyst_version"] = lines[0].strip()

    for line in lines:
        if line.startswith("Simulation date"):
            parts = line.split(";")
            if len(parts) > 2:
                info["Simulation_date"] = parts[2].strip()
    return info


def detect_table(lines: List[str]) -> Tuple[List[str], List[str], int]:
    for i, line in enumerate(lines):
        if line.lower().startswith("date;"):
            headers = [h.strip() for h in line.split(";")]
            if i + 1 >= len(lines):
                raise ValueError("Ligne d'unités manquante après l'en-tête.")
            units = [u.strip() for u in lines[i + 1].split(";")]
            return headers, units, i + 2
    raise ValueError("Table horaire non trouvée (ligne 'date;...' absente).")


def load_hourly_dataframe(lines: List[str]) -> Tuple[pd.DataFrame, Dict[str, str]]:
    headers, units, start = detect_table(lines)

    if "E_Grid" not in headers:
        raise ValueError("Colonne obligatoire 'E_Grid' absente.")

    data = [l.split(";") for l in lines[start:] if l.strip()]
    df = pd.DataFrame(data, columns=headers)

    df["date"] = pd.to_datetime(df["date"], format=PVSYST_DATE_FMT, errors="coerce")
    df = df.dropna(subset=["date"])

    numeric_cols = [c for c in headers if c != "date"]
    for c in numeric_cols:
        df[c] = (
            df[c].astype(str)
            .str.replace(",", ".", regex=False)
            .str.strip()
        )
        df[c] = pd.to_numeric(df[c], errors="coerce")

    n_total = len(df)
    n_valid = df[numeric_cols].notna().any(axis=1).sum()
    if n_total > 0 and n_valid / n_total < 0.5:
        raise ValueError(
            "Moins de 50 % des lignes contiennent des valeurs numériques valides. "
            "Vérifiez le séparateur décimal du fichier PVSyst."
        )

    df = df.set_index("date").sort_index()
    units_map = dict(zip(headers, units))
    return df, units_map


def read_hourly_from_bytes(source: bytes) -> tuple[dict, pd.DataFrame, dict]:
    text = _decode_bytes(source)
    lines = text.splitlines()
    general_info = parse_general_info(lines)
    df, units_map = load_hourly_dataframe(lines)
    return general_info, df, units_map
