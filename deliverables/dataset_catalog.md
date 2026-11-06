# Dataset Catalog — Pedrógão Grande Wildfire

Deep Learning in Analysis of Geohazards · AGH University of Krakow · Nov 5, 2026 · António Romão

## Purpose and Scope

The project needs three things from data: Sentinel-2 images from before and after the fire as model input, burnt-area polygons as labels, and context layers (terrain, land cover, boundaries) to explain where the model succeeds or fails. Each dataset below is tagged **Required**, **Recommended** or **Optional** for that purpose.

- **Task the data serves:** burnt-area segmentation from Sentinel-2 pre/post pairs, the lead direction in the Part 1 brief, with burn severity as an extension. Layers that only matter for susceptibility mapping are marked Optional.
- **Area of interest (AOI):** the June 2017 Pedrógão Grande and Góis fire perimeters from ICNF, buffered by 5 km. Defining the AOI from the labels avoids hand-drawn boxes.
- **Time windows:** pre-fire 1–16 June 2017 (ignition was 17 June at 14:43); post-fire late June to mid-July 2017, before green-up blurs the burn scar.
- **Working grid:** WGS 84 / UTM zone 29N (EPSG:32629) at 10 m, the native Sentinel-2 grid. Every other layer is reprojected and resampled to it.

## Catalog at a Glance

Nine datasets cover the project: the three from Part 1 are required, four context layers are recommended, and two are optional extras. Ma & Mei (2021) name multispectral imagery with spectral indices and DEMs among the main data sources for geohazard deep learning, and pixel-wise CNN segmentation as the most common task; this set follows that pattern.

| Dataset | Priority | Spatial resolution | Data format | Owner / source | Why it is useful |
| --- | --- | --- | --- | --- | --- |
| [Sentinel-2 MSI Level-2A, Collection-1](https://sentinels.copernicus.eu/-/sentinel-2-collection-1-products-availability) (tile T29TNE, pre- and post-fire) | Required | 10 m (B2–B4, B8); 20 m (B5–B7, B8A, B11, B12, SCL); 60 m (B1, B9) | SAFE folder (.zip) of JPEG2000 (.jp2) bands plus XML metadata; WGS 84 / UTM 29N | ESA for the EU Copernicus programme; download from the Copernicus Data Space Ecosystem (CDSE) | Model input: surface reflectance before and after the fire; the NIR and SWIR bands give NBR and dNBR |
| [ICNF Áreas Ardidas 2017](https://geocatalogo.icnf.pt/metadados/area_ardida.html) | Required | 1:100,000 | Shapefile (.zip), also WMS/WFS and ArcGIS REST; EPSG:3763 | ICNF, Portugal's nature and forest institute | Main label set: official final perimeters, with attributes (dates, ignition municipality, cause) to pick out the June fires |
| [Copernicus EMS EMSR207](https://mapping.emergency.copernicus.eu/activations/EMSR207/) | Required | Mapped from SPOT-6/7 at 1.5 m (overview map); map scale 1:110,000 | Vector package (.zip) plus PDF map per product; WGS 84 / UTM 29N | European Commission, Copernicus EMS Rapid Mapping; maps by SERTIT | Independent expert labels; the grading products give damage classes for a severity extension |
| [Copernicus DEM GLO-30](https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM) | Recommended | 30 m (1 arc-second) | GeoTIFF, 32-bit float, 1° × 1° tiles; EPSG:4326, heights in EGM2008 | ESA / EU Copernicus; TanDEM-X data (DLR) produced by Airbus Defence and Space | Elevation, slope and aspect as extra input channels, and for error analysis on steep or shaded slopes |
| [COS2015 v2.0 land use and land cover](https://www.dgterritorio.gov.pt/atividades/cartografia/cartografia-tematica/SMOS-CLMS) | Recommended | Vector; 1 ha minimum mapping unit; 1:25,000 | Vector polygons, PT-TM06 (EPSG:3763); download via SNIG | DGT, Portugal's Directorate-General for Territory | Pre-fire land cover (pine, eucalyptus, shrubland, urban) to stratify accuracy by fuel type and mask land that cannot burn |
| [CAOP 2017 administrative boundaries](https://www.dgterritorio.gov.pt/atividades/cartografia/cartografia-tematica/caop) | Recommended | Vector; official legal limits | Shapefile (.zip), PT-TM06 (EPSG:3763) | DGT | Burnt area per municipality and parish; joins ICNF ignition fields and the census figures from Part 1 |
| [NASA FIRMS active fires](https://firms.modaps.eosdis.nasa.gov/download/) (MODIS C6.1, VIIRS S-NPP) | Recommended | 1 km (MODIS); 375 m (VIIRS) | Points as SHP, CSV or JSON; EPSG:4326 | NASA LANCE / FIRMS | Time-stamped hotspots show how the fire spread on 17–22 June; a sanity check on the labels and a figure for the presentation |
| [EFFIS burnt areas](https://forest-fire.emergency.copernicus.eu/about-effis/technical-background/rapid-damage-assessment) | Optional | 250 m (MODIS-based for 2017) | Vector polygons, via the EFFIS data request form | European Commission JRC, Copernicus EMS | A third, coarse perimeter used as reference in earlier Pedrógão studies; shows how much the label choice changes burnt area |
| [Satellite Burned Area Dataset](https://zenodo.org/records/6597139) (Colomba et al. 2022) | Optional | Up to 10 m | 5 zip parts (14.0 GB) plus satellite\_data.csv with folds; CC BY 4.0 | Politecnico di Torino, on Zenodo | 73 European fires with Sentinel-2 L2A and EMS-derived masks, for pre-training or extra training data |

## Core Datasets: What Exactly to Download

### Sentinel-2 MSI Level-2A

Download two Sentinel-2A Level-2A scenes of tile T29TNE on relative orbit 37: 14 June 2017 (pre-fire) and 4 July 2017 (post-fire).

- **Why Level-2A:** Level-1C is top-of-atmosphere reflectance; Level-2A is surface (bottom-of-atmosphere) reflectance after atmospheric correction with Sen2Cor. Comparing two dates needs Level-2A, otherwise haze differences look like burn change ([ESA RUS kit HAZA02](https://eo4society.esa.int/wp-content/uploads/2022/01/HAZA02_BurnedArea_Portugal.pdf)).
- **2017 availability:** the reprocessed Collection-1 (processing baseline 05.00) L1C and L2A archive is complete on CDSE from 4 July 2015 for Sentinel-2A and from 17 March 2017 for Sentinel-2B ([ESA, Sept 2024](https://sentinels.copernicus.eu/-/sentinel-2-collection-1-products-availability)). Product names now contain N0500, not the N0205 seen in older tutorials.
- **Dates:** ESA's RUS training kit for this fire used 4 June and 4 July 2017 on T29TNE, R037; a University of Lisbon lab used [14 June and 4 July](https://fenix.ciencias.ulisboa.pt/downloadFile/2533412229371504/Aulas_Laboratorio_04-05_2024_2025.pdf). Prefer 14 June: the RUS kit notes that a month-long gap during the drought made unburnt vegetation look like low-severity burn.
- **Closer post-fire date:** also check Sentinel-2B and neighbouring orbits between 19 June and 10 July in Copernicus Browser; images from the first days after ignition may be hidden by smoke.
- **Bands to keep:** B2, B3, B4, B8 at 10 m; B8A, B11, B12 and SCL at 20 m. SCL (Scene Classification Layer) is a per-pixel class map (cloud, cloud shadow, water, vegetation) used for masking.
- **Tile edge:** checked on 5 Nov 2026: the whole fire complex (lon −8.353 to −7.973, lat 39.784 to 40.172 in ICNF) plus the 5 km buffer lies inside T29TNE, so no second tile is needed. Orbit-80 scenes of this tile stop west of the fire, and every scene from 19 to 29 June is 81–91% cloud.
- **Radiometric offset:** Collection-1 L2A stores digital numbers with BOA\_ADD\_OFFSET = −1000, so reflectance = (DN − 1000) / 10000 and DN = 0 is no-data ([CDSE forum](https://forum.dataspace.copernicus.eu/t/ndvi-with-radiometric-offset-of-sentinel-2-l2a/5243)). Skipping the offset biases NBR.

### Copernicus EMS EMSR207

The activation (18 June 2017, 20:43) has 61 products over 11 areas of interest (AOIs), each delivered as a PDF map plus a vector package (.zip) ([EMSR207 page](https://mapping.emergency.copernicus.eu/activations/EMSR207/)). *Delineation* maps the burnt extent, *grading* maps the degree of damage, and *Monit* products are later monitoring updates.

| AOI | Product | Delivered | Use |
| --- | --- | --- | --- |
| AOI11 Pedrógão Grande Overview | Delineation Map and Delineation Monit01 | 22 Jun 2017 | Burnt extent of the whole complex, early snapshot |
| AOI05 Pedrógão Grande | Delineation Monit03 | 27 Jul 2017 | Latest delineation of the core area |
| AOI05 Pedrógão Grande | Grading Map and Grading Monit01 | 6 Jul 2017 | Damage grades for a severity model |
| AOI01–AOI10 | Latest delineation and grading per AOI | 23 Jun–14 Aug 2017 | Detail maps around the complex, if you mosaic them |

Each PDF's margin names its source image and date; record these, because they set how current each label is.

### ICNF Burnt Areas 2017

Download the 2017 shapefile from [si.icnf.pt/shp/ardida\_2017](http://si.icnf.pt/shp/ardida_2017); the same layer is served by WFS (`si.icnf.pt/wfs/ardida_2017`) and the ArcGIS REST service listed in Part 1 ([ICNF metadata](https://geocatalogo.icnf.pt/metadados/area_ardida.html)).

- **Reference:** EPSG:3763 (PT-TM06/ETRS89), scale 1:100,000; free to use, but always credit ICNF.
- **Method:** perimeters come from satellite images and field surveys by the GNR police and municipal forestry offices.
- **Selecting the June fires:** keep polygons whose start time (DH\_Inicio) is 17–18 June 2017 and whose ignition municipality (PI\_Conc) belongs to the complex, such as Pedrógão Grande and Góis. Check how the values are written in the attribute table first.
- **Keep the whole layer:** the other 2017 fires are your extra training data (see below).

## Supporting Datasets: What Exactly to Download

### Copernicus DEM GLO-30

Download the four 1° × 1° tiles N39–N40 × W009–W008, or only the AOI through the OpenTopography DEM Downloader plugin in QGIS.

- **Access:** free registration on CDSE ([COP-DEM page](https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM)), or the [OpenTopography DEM Downloader](https://plugins.qgis.org/plugins/OpenTopography-DEM-Downloader/) plugin (version 4.2 supports QGIS 3.16–4.99; pick "Copernicus Global DSM 30m"; needs a free OpenTopography API key).
- **It is a surface model:** GLO-30 is a DSM, so over forest it records the top of the canopy, as acquired by TanDEM-X in 2011–2015. Slope and aspect at 30 m are still fine; say so in the report.
- **Accuracy:** absolute vertical error under 4 m (90% linear error).
- **Why terrain matters:** fire runs faster upslope, and slopes facing away from the sun at the satellite's late-morning overpass look darker, which can mimic burnt land. Slope and aspect let the model, and your error analysis, separate the two.
- **Credit line (if you modify it):** "produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved".

### COS2015 v2.0 Land Use and Land Cover

Use COS2015, the last national land-cover edition before the fire; COS2018 already shows the burn scar as changed land.

- **Specification:** polygons with a 1 ha minimum mapping unit, 20 m minimum distance between lines, scale 1:25,000, PT-TM06; v2.0 belongs to the revised 1995–2018 series ([DGT technical specifications, 2022](https://www.dgterritorio.gov.pt/sites/default/files/documentos-publicos/ET-COS-1995-2007-2010-2015-2018-v1.pdf)).
- **Download:** DGT publishes all its land-cover products as open data through [SNIG](https://snig.dgterritorio.gov.pt/); search the catalogue for "COS2015".
- **Do not mix series:** DGT warns that the newer Series 2 maps (COS2018v3 onwards, COS2023, COS2025) are not comparable with Series 1 ([DGT land-cover page](https://www.dgterritorio.gov.pt/atividades/cartografia/cartografia-tematica/SMOS-CLMS)).

### CAOP 2017 Administrative Boundaries

Download the 2017 polygons, `Cont_AAD_CAOP2017.zip` (shapefile, PT-TM06), from DGT's [CAOP page](https://www.dgterritorio.gov.pt/atividades/cartografia/cartografia-tematica/caop), which also hosts every earlier edition.

- **Why 2017 and not the current edition:** parish names then match ICNF's PI\_Freg field. The current CAOP2025 (GeoPackage, approved 28 January 2026) includes later boundary changes, such as those from 16 March to 31 December 2025.

### NASA FIRMS Active Fires

Request MODIS Collection 6.1 and VIIRS S-NPP 375 m detections for the AOI box and 15–25 June 2017 from the [FIRMS archive](https://firms.modaps.eosdis.nasa.gov/download/); the files arrive by email after an Earthdata login or an emailed code.

- **Coverage:** MODIS from November 2000 and VIIRS S-NPP from January 2012; VIIRS NOAA-20 only starts in April 2018, so it does not cover this fire.
- **What a point means:** the centre of a 1 km (MODIS) or 375 m (VIIRS) pixel flagged as burning at one overpass. With only a few overpasses a day, this gives a coarse timeline of the spread, not a perimeter.
- **Version:** take standard (science-quality) records, which replace near-real-time ones after about 5 months.

### EFFIS Burnt Areas

Request the 2017 Portuguese perimeters through the EFFIS data request form.

- **Resolution:** for 2017, EFFIS mapped fires of about 30 ha or more semi-automatically from daily MODIS images at 250 m; Sentinel-2 refinement only began in 2018 ([EFFIS method](https://forest-fire.emergency.copernicus.eu/about-effis/technical-background/rapid-damage-assessment)).
- **Why bother:** [Brown et al. (2018)](https://doi.org/10.1016/j.apgeog.2018.10.004) used EFFIS as the reference for Pedrógão, so it lets you compare your numbers with theirs.

## Extra Training Data for the Model

Train on other fires and keep Pedrógão Grande as the unseen test fire. A single fire is essentially one scene, so random patch splits inside it put neighbouring, near-identical pixels in both train and test and overstate accuracy. Wang et al. (2023) also stress that deep learning needs large amounts of data, which has long been a bottleneck in geohazard work.

1. **Other 2017 Portuguese fires (first choice):** take more fires from the same ICNF 2017 layer, for example the October 2017 fires, and download a Sentinel-2 L2A pre/post pair for each. Same label source, same region and the same sensor mean almost no domain shift.
2. **Satellite Burned Area Dataset (Colomba et al. 2022):** 73 European fires from 2017–2019 with Sentinel-1 and Sentinel-2 L2A images and EMS-derived masks in five severity levels, from undamaged to destroyed ([CIKM paper](https://doi.org/10.1145/3511808.3557528)). It ships with 7 cross-validation folds and a U-Net baseline ([code](https://github.com/lccol/burned-area-baseline)). Caveat: nine EMSR207 AOIs are in it, all in fold "coral", so leave that whole fold out of training to keep the test fire unseen. 50 of its 73 fires have a pre-fire date, so a pre/post change model can use most of it.
3. **CaBuAr (California Burned Areas):** 340 Californian fires as Sentinel-2 L2A pre/post pairs at 20 m, with U-Net and SegFormer baselines on [Hugging Face](https://huggingface.co/datasets/DarthReca/california_burned_areas) ([paper](https://arxiv.org/abs/2401.11519)). The vegetation and the 20 m grid differ from your test fire, so use it only for pre-training.

## Caveats, Disagreements and Licences

The biggest caveat is that each label source measures a different fire: the burnt area your model is scored against will change with the source, so every metric in the report should name its label set.

- **Burnt-area figures differ:** Part 1 lists about 28,914 ha (Independent Technical Commission, Pedrógão fire only), 45,328 ha (CEIF, five-fire complex), 42,080 ha (EMSR207, mapped by 20 June) and about 44,969 ha (Wikipedia, as of 20 June). The ESA RUS kit repeats the 44,969 ha early estimate, with 29,693 ha in the Pedrógão area. The gaps come from extent (one fire or the complex), date (snapshot or final) and resolution (EFFIS 250 m, ICNF 1:100,000, EMS from 1.5 m imagery).
- **Correction to Part 1:** the EMSR207 portal now lists only PDF maps and vector packages; no GeoTIFF download is offered.
- **ICNF year range:** Part 1 gives yearly layers for 1975–2025 from the ICNF REST service, while ICNF's metadata record (revised 2019) describes the series from 1990. They may describe different services; 2017 is in both.
- **Old product names:** 2017–2019 tutorials cite N0205 products from the closed SciHub; CDSE now serves the Collection-1 reprocessing instead, with the radiometric offset described above.

| Dataset | Licence and credit |
| --- | --- |
| Sentinel-2 | Free and open; credit "Contains modified Copernicus Sentinel data 2017" |
| EMSR207 | © European Union, Copernicus EMS; follow the [EMS terms](https://mapping.emergency.copernicus.eu/terms-and-conditions/) |
| ICNF burnt areas | No restrictions; always credit ICNF |
| Copernicus DEM GLO-30 | Free licence; use the credit line in the DEM section |
| COS2015, CAOP | DGT open data; credit DGT |
| FIRMS | Free; cite NASA FIRMS |
| EFFIS | EFFIS data licence; credit JRC / Copernicus EMS |
| Satellite Burned Area Dataset | CC BY 4.0; cite Colomba et al. (2022) |
| CaBuAr | Cite Rege Cambrin et al. (2024) |

## Sources

- Part 1 brief (`Part_1_Brief.pdf`, in this folder) and the sources it lists
- Ma, Z. & Mei, G. (2021). Deep learning for geological hazards analysis. *Earth-Science Reviews* 223, 103858. [doi:10.1016/j.earscirev.2021.103858](https://doi.org/10.1016/j.earscirev.2021.103858)
- Wang, J. et al. (2023). Recent advances of deep learning in geological hazard forecasting. *CMES* 137(2). [doi:10.32604/cmes.2023.023693](https://doi.org/10.32604/cmes.2023.023693)
- ESA: [Sentinel-2 Collection-1 products availability](https://sentinels.copernicus.eu/-/sentinel-2-collection-1-products-availability) (2 Sept 2024)
- ESA RUS: [Burned area mapping with Sentinel-2, June 2017, Portugal (HAZA02)](https://eo4society.esa.int/wp-content/uploads/2022/01/HAZA02_BurnedArea_Portugal.pdf)
- University of Lisbon: [lab sheet using 14 June and 4 July 2017 scenes](https://fenix.ciencias.ulisboa.pt/downloadFile/2533412229371504/Aulas_Laboratorio_04-05_2024_2025.pdf)
- CDSE forum: [radiometric offset of Sentinel-2 L2A](https://forum.dataspace.copernicus.eu/t/ndvi-with-radiometric-offset-of-sentinel-2-l2a/5243)
- Copernicus EMS: [EMSR207 activation page](https://mapping.emergency.copernicus.eu/activations/EMSR207/)
- ICNF: [burnt areas metadata](https://geocatalogo.icnf.pt/metadados/area_ardida.html)
- CDSE: [Copernicus DEM collection description](https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM)
- DGT: [CAOP versions and downloads](https://www.dgterritorio.gov.pt/atividades/cartografia/cartografia-tematica/caop); [land-cover cartography (SMOS)](https://www.dgterritorio.gov.pt/atividades/cartografia/cartografia-tematica/SMOS-CLMS); [COS 1995–2018 technical specifications](https://www.dgterritorio.gov.pt/sites/default/files/documentos-publicos/ET-COS-1995-2007-2010-2015-2018-v1.pdf); [SNIG](https://snig.dgterritorio.gov.pt/)
- NASA: [FIRMS archive download](https://firms.modaps.eosdis.nasa.gov/download/)
- EFFIS: [Rapid Damage Assessment method](https://forest-fire.emergency.copernicus.eu/about-effis/technical-background/rapid-damage-assessment)
- Brown, A. R., Ferentinos, K. P. & Petropoulos, G. P. (2018). Appraisal of the Sentinel-1 & 2 use in a large-scale wildfire assessment. *Applied Geography*. [doi:10.1016/j.apgeog.2018.10.004](https://doi.org/10.1016/j.apgeog.2018.10.004)
- Colomba, L. et al. (2022). [Satellite Burned Area Dataset](https://zenodo.org/records/6597139), Zenodo; [CIKM paper](https://doi.org/10.1145/3511808.3557528); [baseline code](https://github.com/lccol/burned-area-baseline)
- Rege Cambrin, D., Colomba, L. & Garza, P. (2024). [CaBuAr: California Burned Areas dataset](https://arxiv.org/abs/2401.11519)
