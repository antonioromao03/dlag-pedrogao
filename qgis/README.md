# QGIS data preparation

Every data-preparation step lives here as a file, so it can be re-run without clicking through QGIS:

- **Models** (`*.model3`), built in **Processing ▸ Model Designer**.
- **Scripts** (`*.py`), either PyQGIS scripts written in the editor of the Python Console (**Plugins ▸ Python Console**) or shell scripts that call `qgis_process`.

Outputs go to `data/interim/` (reprojected, clipped, rasterized layers) and `data/processed/` (model-ready rasters). Both folders are not in git; the scripts here recreate them.

## Running steps headless with `qgis_process`

`qgis_process` ships with QGIS. On macOS it is inside the app bundle, not on your PATH:

```bash
QP=$(ls /Applications/QGIS*.app/Contents/MacOS/bin/qgis_process | head -1)
"$QP" list                              # all Processing algorithms
"$QP" help native:reprojectlayer        # parameters of one algorithm
"$QP" run qgis/<model>.model3 -- PARAM=value ...
```

To turn a step you did in the GUI into a command: open the tool's dialog, click **Advanced** at the bottom and copy it as a `qgis_process` command.

## Steps

| Script | Input | Output | What it does |
| --- | --- | --- | --- |
| *(none yet)* | | | |
