# QGIS data preparation

Every data-preparation step lives here as a file, so it can be re-run without clicking through QGIS:

- **Models** (`*.model3`), built in **Processing ▸ Model Designer**.
- **Scripts** (`*.py`), either PyQGIS scripts written in the editor of the Python Console (**Plugins ▸ Python Console**) or shell scripts that call `qgis_process`.

Outputs go to `data/interim/` (reprojected, clipped, rasterized layers) and `data/processed/` (model-ready rasters). Both folders are not in git; the scripts here recreate them.

## Running steps headless with `qgis_process`

`qgis_process` ships with QGIS. On macOS it is inside the app bundle, not on PATH:

```bash
QP=$(ls /Applications/QGIS*.app/Contents/MacOS/qgis_process | head -1)
"$QP" list                              # all Processing algorithms
"$QP" help native:reprojectlayer        # parameters of one algorithm
"$QP" run qgis/<model>.model3 -- PARAM=value ...
```

To turn a step in the GUI into a command: open the tool's dialog, click **Advanced** at the bottom and copy it as a `qgis_process` command.

## Steps

| Script | Input | Output | What it does |
| --- | --- | --- | --- |
| `s2_warp_bands.py` | `data/raw/sentinel2/` | `data/processed/s2_<date>_<band>.tif` (32 files) | Crops 8 bands of 4 dates to the AOI extent and resamples to 10 m, EPSG:32629 |
| `check_grid.py` | `data/processed/*.tif` | printed OK/BAD per file | Confirms every raster is 4224 × 5322 at 10 m, EPSG:32629 |

Both are PyQGIS scripts: run them from the Python Console editor (**Show Editor ▸ Open Script ▸ Run Script**), not from a plain terminal.
