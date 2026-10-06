from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
RESULTS_DIR = ROOT / "results"
REPORTS_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"

def ensure_directories() -> None:
    for path in [DATA_DIR, RAW_DIR, PROCESSED_DIR, RESULTS_DIR, REPORTS_DIR, DOCS_DIR]:
        path.mkdir(parents=True, exist_ok=True)
