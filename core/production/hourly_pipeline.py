from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from config import OUTPUTS_DIR, OUTPUT_MODE
from utils.paths import make_run_folders

from .hourly_io import read_hourly_from_bytes
from .hourly_models import AnalysisContext, AnalysisOptions
from .hourly_analyzer import register_analyses, run_all_analyses
from .hourly_export_excel import export_excel
from .hourly_export_pdf import export_pdf


@dataclass
class HourlyAnalysisResult:
    context: AnalysisContext
    excel_bytes: bytes
    pdf_bytes: bytes
    run_dir: Path


def analyze_hourly_source(*, source: bytes, source_name: str, threshold_kw: float) -> HourlyAnalysisResult:
    runpaths = make_run_folders(OUTPUTS_DIR, tool_name="hourly_results", mode=OUTPUT_MODE)

    general_info, df, units_map = read_hourly_from_bytes(source)

    # Sauvegarde du fichier source dans le run (trace)
    input_path = runpaths.run_dir / source_name
    try:
        input_path.write_bytes(source)
    except Exception:
        # non bloquant
        pass

    context = AnalysisContext(
        input_file=input_path,
        general_info=general_info,
        units_map=units_map,
        df_raw=df,
        options=AnalysisOptions(threshold_kw=float(threshold_kw)),
    )

    register_analyses()
    run_all_analyses(context)

    excel_path = runpaths.reports_dir / "hourly_results_analysis.xlsx"
    pdf_path = runpaths.reports_dir / "hourly_results_analysis.pdf"

    export_excel(context, excel_path)
    export_pdf(context, pdf_path)

    return HourlyAnalysisResult(
        context=context,
        excel_bytes=excel_path.read_bytes(),
        pdf_bytes=pdf_path.read_bytes(),
        run_dir=runpaths.run_dir,
    )
