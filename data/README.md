# Data: June 2017 Pedrógão Grande wildfire (DLAG project)

Everything in this folder is fetched by `download_data.py`. Run it from Terminal on your Mac:

```bash
cd ~/University/DLAG/Project/dlag-pedrogao/data
python3 download_data.py --dry-run   # plan and sizes only
python3 download_data.py             # download everything (asks for your Copernicus login at the Sentinel-2 step)
```

Default download: about 6.3 GB, plus about 1.5 GB once the vector data is unzipped. Running it again skips finished files and resumes partial ones. Options: `--s2-minimal` (only 14 Jun and 4 Jul), `--unzip-s2` (+ about 5 GB), `--all-ems-pdfs` (+ about 680 MB), `--benchmark` (+ 14 GB), `--no-s2`. Every file is logged in `download_log.csv`. Links and sizes were checked on 5 Nov 2026.

The zip archives were extracted, checked file by file and deleted on 5 Nov 2026. Each extraction left a hidden `.<name>.unzipped` marker file: keep these, because `download_data.py` uses them to know the data is already here and will not download it again.

## Folder layout

| Folder | Contents | Size |
| --- | --- | --- |
| `raw/sentinel2/` | 4 Sentinel-2 L2A scenes, tile T29TNE, as unzipped `.SAFE` folders, trimmed on 18 Nov 2026 to the bands the project uses: `GRANULE/*/IMG_DATA/R10m` (B02, B03, B04, B08, TCI) and `R20m` (B8A, B11, B12, SCL); the other bands and `R60m` were deleted and can be re-downloaded | 2.9 GB |
| `raw/icnf/` | `ardida_2017/ardida_2017.shp` (all 2017 burnt areas, 2,765 polygons, EPSG:3763) (`icnf_june2017_pedrogao_gois.geojson`, the two June fires, was deleted as a duplicate; `download_data.py` fetches it again on its next run) | small |
| `raw/emsr207/vector/` | all 61 EMSR207 vector packages, one folder per product (shapefiles; the duplicate KMZ files were deleted) | 0.7 GB |
| `raw/emsr207/pdf/` | PDF maps for AOI05 Pedrógão Grande and AOI11 Overview | 125 MB |
| `raw/dem_glo30/` | Copernicus DEM GLO-30, tiles N39–N40 × W009–W008 (GeoTIFF, EPSG:4326) | 174 MB |
| `raw/cos2015/` | `COS2015v2-S1.gpkg`, land use/land cover (648,006 polygons, EPSG:3763) | 1.4 GB |
| `raw/caop2017/` | `Cont_AAD_CAOP2017/Cont_AAD_CAOP2017.shp`, 3,223 parishes (EPSG:3763) | 60 MB |
| `raw/firms/` | MODIS and VIIRS S-NPP 2017 Portugal hotspots, plus `firms_aoi_2017-06-15_to_2017-06-25.csv` cut to the fire | 2 MB |
| `raw/benchmark_colomba2022/` | `satellite_data.csv` (index and folds) and one folder per fire inside `Satellite_burned_area_dataset_partN/` (Sentinel-1/2 GeoTIFFs, severity mask, PNG previews). All 5 parts are extracted (73 fires) | 16.4 GB unzipped |

## Sentinel-2 scenes

Tile T29TNE, relative orbit 37, Collection-1 (processing baseline 05.00). The whole fire complex (lon −8.353 to −7.973, lat 39.784 to 40.172, from ICNF) plus a 5 km buffer lies inside this tile. The orbit-80 scenes of the same tile stop west of the fire, and every scene from 19 to 29 June is 81–91% cloud.

| Date | Role | Product | Cloud (whole tile) | Size |
| --- | --- | --- | --- | --- |
| 2017-06-04 | pre-fire | S2A_MSIL2A_20170604T112121_N0500_R037_T29TNE_20231112T010859 | 1.5% | 1.23 GB |
| 2017-06-14 | pre-fire (closest) | S2A_MSIL2A_20170614T112111_N0500_R037_T29TNE_20231009T091756 | 10.7% | 1.24 GB |
| 2017-07-04 | post-fire (closest clear) | S2A_MSIL2A_20170704T112111_N0500_R037_T29TNE_20231006T233809 | 6.1% | 1.24 GB |
| 2017-07-14 | post-fire | S2A_MSIL2A_20170714T112111_N0500_R037_T29TNE_20231005T073211 | 1.5% | 1.23 GB |

Cloud cover is for the whole 110 × 110 km tile; check the SCL band over the fire before choosing between 4 and 14 June. Reflectance = (DN − 1000) / 10000 for these products.

## Direct links

| Dataset | Link | Account |
| --- | --- | --- |
| Sentinel-2 | Copernicus Browser, <https://browser.dataspace.copernicus.eu> (search the product names above) | CDSE |
| ICNF burnt areas 2017 | <https://si.icnf.pt/shp/ardida_2017> | none |
| ICNF June fires (GeoJSON) | <https://sigservices.icnf.pt/server/rest/services/BDG/areas_ardidas/MapServer/3/query?objectIds=69728,68910&outFields=*&outSR=4326&f=geojson> | none |
| EMSR207 | <https://mapping.emergency.copernicus.eu/activations/EMSR207/> (each product: `_vector.zip` and `_200dpi.pdf`) | none |
| Copernicus DEM GLO-30 | <https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N39_00_W009_00_DEM/Copernicus_DSM_COG_10_N39_00_W009_00_DEM.tif> (and N39_00_W008_00, N40_00_W009_00, N40_00_W008_00) | none |
| COS2015 v2 | <https://geo2.dgterritorio.gov.pt/cos/S1/COS2015/COS2015v2-S1-gpkg.zip> (shapefile: `-shp.zip`) | none |
| CAOP 2017 | <https://www.dgterritorio.gov.pt/sites/default/files/ficheiros-cartografia/Cont_AAD_CAOP2017.zip> | none |
| FIRMS MODIS 2017 | <https://firms.modaps.eosdis.nasa.gov/data/country/modis/2017/modis_2017_Portugal.csv> | none |
| FIRMS VIIRS S-NPP 2017 | <https://firms.modaps.eosdis.nasa.gov/data/country/viirs-snpp/2017/viirs-snpp_2017_Portugal.csv> | none |
| Satellite Burned Area Dataset | <https://zenodo.org/records/6597139> | none |
| EFFIS burnt areas (manual form) | <https://effis.jrc.ec.europa.eu/apps/data.request.form> | form |

The DEM comes from the public AWS copy, so the OpenTopography key and plugin are not needed.

## Notes found while checking the data

**The two June fires in ICNF** (layer "Áreas Ardidas 2017", REST service):

| OBJECTID | SGIF code | Ignition (DH_Inicio) | Area, GIS | Area, SGIF | Cause in ICNF |
| --- | --- | --- | --- | --- | --- |
| 69728 | BL4171577 | Pedrógão Grande, Escalos Fundeiros, 2017-06-17 14:43 | 30,618 ha | 30,359 ha | 211 Negligent – accidental: transport and communications |
| 68910 | BL217377 | Góis, Alvares, 2017-06-17 14:52 | 17,432 ha | 17,521 ha | 51 Natural |

Together 48,049 ha (GIS). That is higher than the 28,914 ha (Pedrógão only) and 45,328 ha (five-fire complex) figures in the Part 1 brief; report which figure each comparison uses. `deliverables/dataset_catalog.md` lists all the burnt-area figures side by side.

**Extra training fires** (ICNF 2017, start date, GIS area): Lousã 15 Oct, 67,911 ha; Arganil 15 Oct, 47,200 ha; Sertã (Ermida) 15 Oct, 35,422 ha; Sertã (Várzea dos Cavaleiros) 23 Jul, 33,712 ha; Alvaiázere 11 Aug, 23,760 ha; Figueira da Foz 15 Oct, 21,184 ha; Vouzela 15 Oct, 21,086 ha; Alcobaça 15 Oct, 17,290 ha. Each needs its own Sentinel-2 pre/post pair, which the script does not fetch.

**Benchmark folds:** `satellite_data.csv` lists 73 fires, 50 of them with a pre-fire date. Nine EMSR207 AOIs are included, all in fold `coral` (which also holds EMSR250 from October 2017 in Portugal and EMSR372 from 2019 near Sertã). Leave the whole `coral` fold out of training so the Pedrógão test fire stays unseen.

**FIRMS:** between 17 and 24 June 2017, 402 MODIS and 1,973 VIIRS S-NPP detections fall inside the fire box (lon −8.45 to −7.90, lat 39.70 to 40.25).

## Credits

- Sentinel-2: contains modified Copernicus Sentinel data 2017.
- EMSR207: © European Union, Copernicus Emergency Management Service.
- ICNF burnt areas: ICNF, I.P.
- Copernicus DEM: produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved.
- COS2015 and CAOP: Direção-Geral do Território (DGT), open data.
- FIRMS: NASA LANCE / FIRMS.
- Satellite Burned Area Dataset: Colomba et al. (2022), CC BY 4.0.
