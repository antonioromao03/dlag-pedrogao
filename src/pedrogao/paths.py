"""Project folders. Import these instead of hard-coding paths in notebooks and scripts."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DATA = ROOT / "data"
RAW = DATA / "raw"              # downloads from data/download_data.py (not in git)
INTERIM = DATA / "interim"      # QGIS outputs: reprojected, clipped, rasterized layers (not in git)
PROCESSED = DATA / "processed"  # model-ready tiles and labels (not in git)
OUTPUTS = ROOT / "outputs"      # checkpoints, predictions, logs (not in git)

SENTINEL2 = RAW / "sentinel2"
ICNF = RAW / "icnf"
EMSR207 = RAW / "emsr207"
BENCHMARK = RAW / "benchmark_colomba2022"

# Course material lives next to the repo, not inside it.
COURSE = ROOT.parents[1]  # DLAG/ (the repo is DLAG/Project/dlag-pedrogao)
SYLLABUS = COURSE / "Syllabus.pdf"
LECTURES = COURSE / "Lectures"
