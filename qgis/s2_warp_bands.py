"""Cut 8 Sentinel-2 bands of 4 dates to the AOI on one 10 m grid (EPSG:32629).

Run inside QGIS: Plugins > Python Console > Show Editor > Open Script > Run Script.
Reads data/raw/sentinel2/, writes data/processed/s2_<date>_<band>.tif (32 files).
Files that already exist are skipped, so the script can be re-run.
"""
from pathlib import Path
import processing

# The console editor may not define __file__; fall back to the usual repo location.
ROOT = (Path(__file__).resolve().parents[1] if "__file__" in globals()
        else Path.home() / "University/DLAG/Project/dlag-pedrogao")
DATA = ROOT / "data"
OUT = DATA / "processed"
OUT.mkdir(exist_ok=True)
EXTENT = "550320,592560,4399020,4452240 [EPSG:32629]"
DATES = ["20170604", "20170614", "20170704", "20170714"]
BANDS = {"B02": "10", "B03": "10", "B04": "10", "B08": "10",
         "B8A": "20", "B11": "20", "B12": "20", "SCL": "20"}

for date in DATES:
    for band, res in BANDS.items():
        dst = OUT / f"s2_{date}_{band}.tif"
        if dst.exists():
            continue
        src = next(DATA.glob(f"raw/sentinel2/S2A_MSIL2A_{date}*.SAFE/GRANULE/*/IMG_DATA/"
                             f"R{res}m/*_{band}_{res}m.jp2"))
        processing.run("gdal:warpreproject", {
            "INPUT": str(src),
            "TARGET_CRS": "EPSG:32629",
            "RESAMPLING": 0 if band == "SCL" else 1,   # 0 nearest (classes), 1 bilinear
            "TARGET_RESOLUTION": 10,
            "TARGET_EXTENT": EXTENT,
            "TARGET_EXTENT_CRS": "EPSG:32629",
            "DATA_TYPE": 0,                              # keep the input type (UInt16)
            "OUTPUT": str(dst),
        })
        print("wrote", dst.name)
print("done")
