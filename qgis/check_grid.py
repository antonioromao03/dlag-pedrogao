"""Confirm every raster in data/processed sits on the same 10 m grid (4224 x 5322, EPSG:32629).

Run inside QGIS: Plugins > Python Console > Show Editor > Open Script > Run Script.
Every line should start with OK.
"""
from pathlib import Path
from qgis.core import QgsRasterLayer

# The console editor may not define __file__; fall back to the usual repo location.
ROOT = (Path(__file__).resolve().parents[1] if "__file__" in globals()
        else Path.home() / "University/DLAG/Project/dlag-pedrogao")

for p in sorted((ROOT / "data/processed").glob("*.tif")):
    r = QgsRasterLayer(str(p), p.stem)
    e = r.extent()
    ok = ((r.width(), r.height()) == (4224, 5322) and r.crs().authid() == "EPSG:32629"
          and round(e.xMinimum()) == 550320 and round(e.yMaximum()) == 4452240)
    print("OK " if ok else "BAD", p.name, r.width(), r.height(), r.crs().authid())
