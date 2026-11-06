# Pedrógão Grande Wildfire, June 2017: Deep Learning on Satellite Data

Course project for **Deep Learning in Analysis of Geohazards**, AGH University of Krakow, winter semester 2026/27 (lecturer: Agnieszka Malinowska). Individual project by António Romão.

## Status

- **Part 1, understanding the geohazard and its data:** done. See `deliverables/Part_1_Brief.pdf` (slides) and `deliverables/dataset_catalog.md` (what to download for each dataset, with priority, resolution, format, licence and caveats).
- **Data:** downloaded and checked. See `data/README.md`.
- **Final project:** direction not chosen yet. Candidates: burnt-area segmentation, burn-severity mapping, wildfire susceptibility mapping.

## Layout

```text
.
├── data/              download script, data notes; raw/, interim/, processed/ are not in git
├── deliverables/      submitted work (Part 1 brief, dataset catalog; later the report and slides)
├── tasks/             assignment sheets
├── qgis/              QGIS models and scripts for data preparation (see qgis/README.md)
├── src/pedrogao/      Python package: paths, baselines, dataset, models, training, metrics
├── notebooks/         exploration, baseline, training and results analysis, run in order
├── environment.yml    conda environment
└── pyproject.toml     package metadata (installed in editable mode by environment.yml)
```

## Setup

```bash
conda env create -f environment.yml    # from the repo root; installs pedrogao in editable mode
conda activate dlag
```

QGIS 4 is installed separately and used for data preparation; see `qgis/README.md`.

## Data

Data files are not in git. `data/README.md` lists every dataset, its source, licence and size, and `data/download_data.py` fetches them (about 6.3 GB, plus 14 GB for the optional benchmark).

## Reproducing the Results

1. Download the data: `cd data && python3 download_data.py`
2. Prepare the inputs with the steps in `qgis/` (writes `data/interim/` and `data/processed/`).
3. Run the notebooks in `notebooks/` in order.

## Course Material

The syllabus and lecture material are kept outside this repo: `../../Syllabus.pdf` and `../../Lectures/`.

## Credits

Data credits and licences are listed in `data/README.md`.
