# QGIS preparation, step by step

Turns the raw downloads in `data/raw/` into model-ready layers in `data/processed/`: Sentinel-2 bands, NBR/dNBR, cloud masks, burnt-area labels, terrain, land cover and municipalities, all on one 10 m grid. Follow the steps in order; each ends with a **Check** that says what you should see. Plan on two to three hours the first time. On a Mac, read Ctrl as Cmd and Alt as Option. Paths are relative to the repo root, `~/University/DLAG/Project/dlag-pedrogao/`.

**How this was verified.** Every number in the Checks was computed from the real data in `data/raw/`. Every Processing tool call, both Raster Calculator expressions and both scripts ([s2_warp_bands.py](s2_warp_bands.py), [check_grid.py](check_grid.py)) were run headless in **QGIS 3.44.15**, the version installed on this Mac. Menu paths are the 3.x ones, and the purely on-screen parts (menus, export dialogs, symbology, the Delimited Text dialog) were not clicked through, only the tools behind them. QGIS 4 (4.2 is current; the 4.4 long-term release is scheduled for 20 Nov 2026, per the [QGIS roadmap](https://qgis.github.io/QGIS-Website/resources/roadmap)) was not available to test. If a menu entry is missing there, type the tool's name in the Processing Toolbox search box instead.

## Settings used throughout

| Setting | Value | Why |
| --- | --- | --- |
| Coordinate system (CRS) | EPSG:32629, WGS 84 / UTM zone 29N | the Sentinel-2 grid; units are metres |
| Clip extent | `550320,592560,4399020,4452240 [EPSG:32629]` | the two June fires plus 5 km, snapped to 60 m so 10, 20 and 60 m pixels line up; its corners are whole multiples of 60 m from the tile origin (499980, 4500000) |
| Pixel size | 10 m | the finest Sentinel-2 bands |
| Raster size | 4,224 columns × 5,322 rows | every output raster must have exactly this size |

## Step 1 – A first look at QGIS

1. Install QGIS from qgis.org (Download → macOS). If macOS refuses to open it the first time, right-click the app in Applications and choose **Open**.
2. Start QGIS and click **New Empty Project**.
3. Find the areas you will use all the time:
   - **Browser panel** (top left): your files, like Finder. Right-click the `data` folder → **Add as a Favorite**.
   - **Layers panel** (bottom left): what is on the map. A layer higher in the list is drawn on top; its tick box shows or hides it.
   - **Map canvas** (centre): scroll to zoom; drag with the hand (**Pan**) tool to move.
   - **Processing Toolbox** (Processing → Toolbox, Ctrl+Alt+T): every analysis tool, with a search box.
   - A panel is missing → View → Panels.
4. Three controls you will use in every step:
   - **Identify Features** (the cursor with an "i"): click a pixel or polygon to see its values.
   - **Open Attribute Table** (F6): the selected layer's table.
   - **Layer Properties** (double-click a layer): the **Information** tab shows CRS, extent and size; **Symbology** sets colours.

## Step 2 – Create the project and set its coordinate system

A coordinate reference system (CRS) is the rule that turns positions on the curved Earth into flat x/y numbers. Your files use three: EPSG:4326 (degrees; DEM, FIRMS), EPSG:3763 (PT-TM06, metres; ICNF, COS2015, CAOP) and EPSG:32629 (UTM zone 29N, metres; Sentinel-2, EMSR207). QGIS converts on the fly for display, but layers you combine pixel by pixel must share one CRS, so everything you save goes to EPSG:32629.

1. Project → **Save As…** → save `pedrogao.qgz` in the repo root (next to `data`, not inside it).
2. Project → **Properties…** → **CRS** tab → type `32629` in the filter box → select **WGS 84 / UTM zone 29N** → **OK**.
3. In Finder, create the folder `data/processed`.
4. Optional background map: in the Browser panel expand **XYZ Tiles** and double-click **OpenStreetMap**.

**Check:** the status bar (bottom right) shows **EPSG:32629**. Over central Portugal the coordinates read x in the hundreds of thousands and y around 4.4 million (metres).

## Step 3 – Load the ICNF burnt areas and keep the two June fires

1. In the Browser open `data/raw/icnf/ardida_2017/` and drag `ardida_2017.shp` onto the map. A shapefile is several files sharing one name (.shp, .dbf, .shx, .prj); you only open the .shp.
2. Right-click the layer → **Show Feature Count**: **2765**, every fire ICNF mapped in mainland Portugal in 2017.
3. Press F6 and look at the columns: `Cod_SGIF` (fire ID), `PI_Conc` (municipality where it started), `DH_Inicio` (start date; always midnight, the file has no time of day) and `AreaHaSIG` (area in hectares). Close the table.
4. Edit → Select → **Select Features by Expression…** (Ctrl+F3). Type `"Cod_SGIF" IN ('BL4171577', 'BL217377')` → **Select Features** → **Close**. Double quotes name a field; single quotes are text values.
5. The two fires turn yellow. Right-click the layer → Export → **Save Selected Features As…**:
   - Format: **GeoPackage** (one file that keeps the CRS; better than a shapefile)
   - File name: `data/processed/fires_june2017.gpkg`
   - Layer name: `fires_june2017`
   - CRS: click the globe button → **EPSG:32629**
   - Tick **Save only selected features** and **Add saved file to map** → **OK**.
6. If a **Select Transformation** window appears, keep the default. The ETRS89 to WGS 84 difference is about a metre or less, below the 10 m pixel.

**Check:** `fires_june2017` has 2 features, `AreaHaSIG` 30617.85 (Pedrógão Grande, BL4171577) and 17431.64 (Góis, BL217377), and Layer Properties → Information shows EPSG:32629.

Why only these two: the other 2017 ICNF fires inside the 5 km buffer are either tiny before 4 July (four fires, 18, 2, 48 and 0.05 ha) or start after both July scenes (the 23,760 ha Alvaiázere fire in August, the Sertã fires), so they cannot be in the images and do not belong in the label.

## Step 4 – Draw the area of interest (AOI)

1. Vector → Geoprocessing Tools → **Buffer…**
2. Input layer `fires_june2017`; Distance `5000` meters; tick **Dissolve result**; Buffered → **…** → Save to File → `data/processed/aoi_5km.gpkg` → **Run** → **Close**.
3. To see through it: double-click `aoi_5km` → Symbology → **Simple Fill** → Fill style **No Brush** → pick a bright Stroke color → **OK**.

**Check:** one polygon around both fires. Layer Properties → Information → Extent reads about 550348, 4399062 : 592468, 4452225. With the default of 5 segments the buffer is a slightly smaller polygon than a true 5 km circle (the exact value is 550348, 4399062 : 592523, 4452231); either way the clip extent in the settings table, which is this box rounded outwards to multiples of 60 m, encloses it.

## Step 5 – Look at a Sentinel-2 scene

Each scene is a folder ending in `.SAFE`. Its images sit in `GRANULE/L2A_T29TNE_…/IMG_DATA/`, sorted by pixel size into `R10m`, `R20m` and `R60m`, one JPEG 2000 file (.jp2) per band, named like `T29TNE_20170704T112111_B08_10m.jp2`. The bands you need: B02 blue, B03 green, B04 red and B08 near-infrared (NIR) at 10 m; B8A narrow NIR, B11 and B12 short-wave infrared (SWIR) and SCL (scene classification) at 20 m. TCI is a ready-made true-colour picture.

1. In the Browser open `raw/sentinel2/S2A_MSIL2A_20170704T112111_…SAFE/GRANULE/L2A_T29TNE_A010616_20170704T112431/IMG_DATA/R10m/` and drag `T29TNE_20170704T112111_TCI_10m.jp2` onto the map. Zoom into the `aoi_5km` outline.
2. Add the 14 June picture the same way (`…20170614…/R10m/T29TNE_20170614T112111_TCI_10m.jp2`) and switch between the two with the tick boxes.
3. Add `T29TNE_20170704T112111_B08_10m.jp2` from the same folder and click a few pixels with Identify Features.

The values are digital numbers (DN), not reflectance. Reflectance, the fraction of sunlight the ground reflects, is (DN − 1000) / 10000 for these products: DN 2500 means 0.15. DN 0 means no data. Healthy leaves reflect a lot of NIR; burnt ground reflects little NIR and more SWIR, and NBR measures that contrast.

**Check:** on 4 July the burn scar is a large dark brown-grey patch inside the AOI outline; on 14 June the same place is green. B08 averages about 2,200 inside the scar and about 3,700 outside it.

## Step 6 – Cut every band to the 10 m grid

Each band file covers the whole 110 × 110 km tile, at 10 m or 20 m. The model needs every input on one identical grid. **Warp (Reproject)** crops to the clip extent, resamples to 10 m and writes EPSG:32629 in one go. Do one band by hand to learn the tool, then let the script do the other 31.

1. Raster → Projections → **Warp (Reproject)…**
2. Input layer: click **…** and pick `…20170614…/IMG_DATA/R20m/T29TNE_20170614T112111_B12_20m.jp2`.
3. Target CRS **EPSG:32629**; Resampling method **Bilinear**; Output file resolution `10`.
4. Open **Advanced Parameters**. In **Georeferenced extents of output file** paste `550320,592560,4399020,4452240 [EPSG:32629]`; set **CRS of the target raster extent** to EPSG:32629. Leave **Nodata value** empty.
5. Reprojected → **…** → Save to File → `data/processed/s2_20170614_B12.tif` → **Run**.

Bilinear averages the four nearest pixels, which suits reflectance. Nearest neighbour copies the closest pixel, the only correct choice for class codes such as SCL.

**Check:** Layer Properties → Information shows Width 4224, Height 5322, pixel size 10, −10, EPSG:32629 and data type UInt16.

Now the rest: Plugins → **Python Console** (Ctrl+Alt+P) → **Show Editor** (notepad icon) → **Open Script** → `qgis/s2_warp_bands.py` → **Run Script** (green triangle). It writes 32 files (4 dates × 8 bands) and skips existing ones. QGIS freezes for a minute or two; wait for `done`.

**Check:** `data/processed` holds 32 files, `s2_20170604_B02.tif` to `s2_20170714_SCL.tif`, all 4224 × 5322.

## Step 7 – Check clouds, then compute NBR, dNBR and cloud masks

The SCL band gives every pixel a class: 0 no data, 1 saturated, 2 dark area, 3 cloud shadow, 4 vegetation, 5 bare ground, 6 water, 7 unclassified, 8 cloud (medium probability), 9 cloud (high probability), 10 thin cirrus, 11 snow.

1. **Pick the dates.** Processing Toolbox → **Raster layer unique values report** → Input `data/processed/s2_20170604_SCL.tif` → **Run**; read the pixel counts for classes 3, 8, 9 and 10 in the log. Repeat for the other three SCL files. These are the counts over the whole AOI box (22,480,128 pixels at 10 m):

   | Date | Cloud and shadow pixels (classes 3, 8, 9, 10) | Share |
   | --- | --- | --- |
   | 4 June | about 281,000 | 1.25% |
   | **14 June** | **23,748** | **0.11%** |
   | **4 July** | **304** | **0.001%** |
   | 14 July | about 210 | 0.001% |

   Use **14 June** (the closest clear pre-fire scene) and **4 July** (clear, and closest to the fire). The whole-tile cloud figures in `data/README.md` rank 4 June first, but over the fire 14 June is clearer; always judge by SCL inside the AOI.
2. **Load the bands.** In the Browser select `s2_20170614_B08.tif`, `s2_20170614_B12.tif`, `s2_20170704_B08.tif` and `s2_20170704_B12.tif` (Cmd-click) and drag them in. Each layer is named after its file.
3. **NBR before.** Raster → **Raster Calculator…** and enter (one line):

   `(("s2_20170614_B08@1" - "s2_20170614_B12@1") / ("s2_20170614_B08@1" + "s2_20170614_B12@1" - 2000)) / ("s2_20170614_B08@1" > 1000 AND "s2_20170614_B12@1" > 1000)`

   - `@1` means band 1. The `- 2000` removes the +1000 offset of both bands, which cancels on top but not underneath, so this equals NBR on true reflectance.
   - The final `/ ( … > 1000 AND … > 1000)` divides by 0 wherever a band has zero or negative reflectance; the Raster Calculator turns that into no-data. Without it, no-data pixels and dark water (the reservoirs) give NBR values as extreme as −217 and +253, which also wrecks the colour stretch later.
   - Output layer `data/processed/nbr_20170614.tif`, format GeoTIFF; select `s2_20170614_B08@1` in the band list and click **Use Selected Layer Extent** → **OK**.
4. **NBR after.** The same with the 20170704 layers → `data/processed/nbr_20170704.tif`.
5. **dNBR.** Raster Calculator: `"nbr_20170614@1" - "nbr_20170704@1"` → `data/processed/dnbr_20170614_20170704.tif` (use `nbr_20170614@1` for the extent).
6. **See it.** Double-click the dNBR layer → Symbology → Render type **Singleband pseudocolor** → colour ramp **Reds** → set Min `-0.2` and Max `1.2` → **Classify** → **OK**. Drag `fires_june2017` above it with a No Brush fill (as in Step 4).
7. **Cloud masks.** Drag in `s2_20170614_SCL.tif` and `s2_20170704_SCL.tif`, then Raster Calculator: `("s2_20170614_SCL@1" = 3) OR ("s2_20170614_SCL@1" >= 8 AND "s2_20170614_SCL@1" <= 10)` → `data/processed/cloudmask_20170614.tif` (1 = cloud or shadow, 0 = clear). Repeat for 20170704.

   The mask deliberately leaves out classes 2, 5 and 7. On 4 July Sen2Cor labels the burn scar mostly as bare ground (5), dark area (2) and unclassified (7), and never as cloud shadow (3) inside the fire perimeter, so masking classes 2 or 7 would erase the burn you want to map.

**Check:** NBR is between −1 and 1 everywhere it is defined (about 47,000 pixels, mostly reservoirs, are no-data); on average 0.43 inside the future scar on 14 June and −0.17 on 4 July. dNBR averages 0.61 inside the ICNF perimeter, and its range is about −1.3 to 1.4. The dNBR map is bright almost exactly inside the ICNF outline; mismatches at the edges are expected and worth discussing in your analysis. The masks hold 23,748 (14 June) and 304 (4 July) pixels set to 1.

## Step 8 – Turn the labels into rasters on the same grid

A label raster holds 1 (burnt) or 0 (unburnt) in each 10 m pixel; that is what a segmentation model trains on. **Rasterize** "burns" polygons onto a grid, and you give it the same extent and pixel size as the bands. It writes in the layer's own CRS and does not reproject, which is why every layer is exported to EPSG:32629 first. One rule from here on: never edit files in `data/raw/`; copy to `data/processed/` first.

### A. ICNF label (your main label set)

1. Raster → Conversion → **Rasterize (Vector to Raster)…**
2. Input layer `fires_june2017`. Leave **Field to use for a burn-in value** empty and set **A fixed value to burn** to `1`.
3. Output raster size units **Georeferenced units**; Width/Horizontal resolution `10`; Height/Vertical resolution `10`.
4. Output extent: paste `550320,592560,4399020,4452240 [EPSG:32629]`.
5. **Assign a specified NoData value to output bands**: `255`. With the default of 0, every unburnt pixel would count as missing.
6. Advanced Parameters: Output data type **Byte**; **Pre-initialize the output image with value** `0`.
7. Rasterized → Save to File → `data/processed/label_icnf_10m.tif` → **Run**.

**Check:** 4224 × 5322 pixels, values 0 and 1 only; 4,800,796 pixels are 1 (about 48,008 ha, against 48,049 ha of polygon area).

### B. EMSR207 burnt area (second label set, for comparison)

1. Add `raw/emsr207/vector/EMSR207_11PEDROGAOGRANDEOVERVIEW_01DELINEATION_MONIT01_v1/EMSR207_11PEDROGAOGRANDEOVERVIEW_01DELINEATION_MONIT01_v1_110000_crisis_information_poly.shp`. Its 1,878 polygons are all `interpret` = Burnt Area for the whole complex, mapped from SPOT-6/7 images at 1.5 m and dated 21 June 2017 (`src_date`). It is already in EPSG:32629.
2. Rasterize it with exactly the settings of A → `data/processed/label_ems_overview_10m.tif`.

**Check:** the same shape as the ICNF label but smaller: 4,481,326 pixels are 1 (about 44,813 ha), because it is an early snapshot while ICNF holds final perimeters.

### C. Damage grades (optional, for a severity model)

1. Add `raw/emsr207/vector/EMSR207_05PEDROGAOGRANDE_02GRADING_MONIT01_v2/EMSR207_05PEDROGAOGRANDE_02GRADING_MONIT01_v2_25000_crisis_information_poly_grading.shp` (AOI05, the core of the Pedrógão fire, 2,024 polygons, EPSG:32629).
2. `grading` is text, but Rasterize needs numbers. Processing Toolbox → **Field calculator** (under Vector table). Input layer: the grading layer; Result field name `grade`; Result field type **Integer (32 bit)**; Formula:
   `CASE WHEN "grading" = 'Negligible to slight damage' THEN 1 WHEN "grading" = 'Moderately Damaged' THEN 2 WHEN "grading" = 'Highly Damaged' THEN 3 END`
   → Calculated → Save to File → `data/processed/ems_grading_aoi05.gpkg` → **Run**. These are the only three values in the data (648, 891 and 485 polygons).
3. Rasterize as in A, but set **Field to use for a burn-in value** to `grade` and leave the fixed value empty → `data/processed/label_ems_grading_aoi05_10m.tif`.

**Check:** values 0 (outside), 1, 2 and 3, with 256,363, 563,093 and 933,212 pixels respectively. This covers AOI05 only; for the whole fire, first join the grading layers of AOI01–AOI10 with Vector → Data Management Tools → **Merge Vector Layers…**

## Step 9 – Terrain from the DEM

1. Raster → Miscellaneous → **Build Virtual Raster…** Input layers: **…** → **Add File(s)…** → the four `.tif` files in `raw/dem_glo30/`. Resolution **Highest**. **Untick** "Place each input file into a separate band": you want one seamless mosaic, not a four-band stack. Virtual → Save to File → `data/processed/dem_mosaic.vrt` → **Run**. A virtual raster (.vrt) is a tiny file that points at the originals.
2. Raster → Projections → **Warp (Reproject)…** Input `dem_mosaic`; Target CRS EPSG:32629; Resampling **Bilinear**; resolution `10`; under Advanced Parameters paste the clip extent and set its CRS to EPSG:32629 → `data/processed/dem_10m.tif`. Going from 30 m to 10 m adds no detail; it only lines the DEM up with the bands.
3. Raster → Analysis → **Slope…** Input `dem_10m`; leave **Ratio of vertical units to horizontal** at 1.0 (both are metres); **tick Compute edges** → `data/processed/slope_10m.tif`, in degrees.
4. Raster → Analysis → **Aspect…** Input `dem_10m`; **tick Compute edges** → `data/processed/aspect_10m.tif`, in degrees clockwise from north.

Without **Compute edges** the outermost row and column of slope and aspect are no-data (−9999), a one-pixel frame that silently breaks patches at the raster border.

**Check:** `dem_10m` is 4224 × 5322, elevations from 17.5 m in the valleys to 1204 m at Trevim in the Serra da Lousã; remember the DEM is a surface model that includes the tree canopy. Slope runs 0–66°. Aspect is undefined on perfectly flat ground (reservoirs and valley floors, about 170,000 pixels) and stays −9999 there; in Python, mask those pixels or encode aspect as sin and cos with 0 for flat.

## Step 10 – Land cover (COS2015)

1. In the Browser expand `raw/cos2015/COS2015v2-S1.gpkg` and drag in the layer `COS2015v2`. It holds 648,006 polygons for all of mainland Portugal and draws slowly, so untick it while you work.
2. Processing Toolbox → **Extract/clip by extent**. Input layer `COS2015v2`; Extent: paste `550320,592560,4399020,4452240 [EPSG:32629]`; tick **Clip features to extent**; leave the output as a temporary layer → **Run** (it can take a minute).
3. Right-click the new temporary layer → Export → **Save Features As…** → GeoPackage `data/processed/cos2015_aoi.gpkg`, CRS EPSG:32629.
4. The class codes are text such as `5.1.2.1`. Processing Toolbox → **Field calculator**; Input `cos2015_aoi`; Result field name `cos_n4`; type **Integer (32 bit)**; Formula `to_int(replace("COS15n4_C", '.', ''))` → Save to File → `data/processed/cos2015_aoi_n4.gpkg` → **Run**. `5.1.2.1` becomes 5121.
5. Rasterize as in Step 8A, but with Input `cos2015_aoi_n4`, **Field to use for a burn-in value** `cos_n4`, no fixed value, NoData `0`, pre-initialise `0` and Output data type **UInt16** → `data/processed/cos2015_n4_10m.tif`.

Clip to the rectangle, not to `aoi_5km`: the buffer covers only 58% of the raster box, so clipping to it would leave 42% of the land-cover raster empty.

The codes you will meet most: 5121 maritime pine forest, 5115 eucalyptus forest, 5117 other broadleaf forest, 6111 shrubland, 2321 mosaics of small fields; 1xxx is built-up land, 2xxx agriculture, 3xxx pasture, 4xxx agroforestry, 7xxx open ground and 9xxx water.

**Check:** UInt16, 4224 × 5322, no pixel left at 0. Inside the ICNF burnt area 94% of pixels are forest or shrub (5xxx, 6xxx): 51% eucalyptus (5115), 31% maritime pine (5121), 6% shrubland (6111).

## Step 11 – Municipalities (CAOP 2017)

1. Add `raw/caop2017/Cont_AAD_CAOP2017/Cont_AAD_CAOP2017.shp` (3,223 parishes).
2. Vector → Geoprocessing Tools → **Dissolve…** Input `Cont_AAD_CAOP2017`; Dissolve field(s) **…** → tick `Concelho` and `Distrito` → **Run**. Parishes merge into 278 municipalities.
3. Vector → Research Tools → **Select by Location…** Select features from `Dissolved` where the features **intersect** `aoi_5km` → **Run**.
4. Right-click `Dissolved` → Export → **Save Selected Features As…** → `data/processed/municipalities_aoi.gpkg`, CRS EPSG:32629.

Names here are upper case with accents (`PEDRÓGÃO GRANDE`, `CASTANHEIRA DE PÊRA`), while ICNF writes `Pedrógão Grande`. Compare them with `upper("PI_Conc")`.

**Check:** 15 municipalities: Alvaiázere, Ansião, Arganil, Castanheira de Pêra, Ferreira do Zêzere, Figueiró dos Vinhos, Góis, Lousã, Miranda do Corvo, Oleiros, Pampilhosa da Serra, Pedrógão Grande, Penela, Sertã and Vila de Rei.

## Step 12 – FIRMS hotspots

1. Layer → Add Layer → **Add Delimited Text Layer…**
2. File name `data/raw/firms/firms_aoi_2017-06-15_to_2017-06-25.csv`; File format **CSV**; Geometry definition **Point coordinates**; X field `longitude`; Y field `latitude`; Geometry CRS **EPSG:4326 – WGS 84** → **Add** → **Close**.
3. Double-click the layer → Symbology → **Categorized** → Value `acq_date` → **Classify** → **OK**. Each day gets its own colour.
4. Optional: Export → **Save Features As…** → `data/processed/firms_aoi.gpkg`, CRS EPSG:32629.

Each point is the centre of a 375 m (VIIRS) or 1 km (MODIS) pixel flagged as burning at one satellite pass. `acq_time` is UTC as hhmm (an integer, so 147 means 01:47); Portugal was UTC+1.

**Check:** 2,375 points (1,973 VIIRS, 402 MODIS), dated 17–23 June: 1 on the 17th, 1,076 on the 18th, 648, 463, 175, 10 and 2 on the following days.

## Step 13 – Final check

When you finish, `data/processed/` holds the files below. Every raster must be 4224 × 5322 pixels at 10 m in EPSG:32629 with the same extent; then any two files line up pixel for pixel when you read them in Python.

| File | What it is | Step |
| --- | --- | --- |
| `fires_june2017.gpkg` | the two June fire perimeters (ICNF) | 3 |
| `aoi_5km.gpkg` | the area of interest | 4 |
| `s2_<date>_<band>.tif` (32 files) | Sentinel-2 bands as DN (UInt16; SCL UInt8): 4 dates × B02, B03, B04, B08, B8A, B11, B12, SCL | 6 |
| `nbr_20170614.tif`, `nbr_20170704.tif` | NBR before and after the fire (Float32, no-data on water and bad pixels) | 7 |
| `dnbr_20170614_20170704.tif` | dNBR, before minus after | 7 |
| `cloudmask_20170614.tif`, `cloudmask_20170704.tif` | 1 = cloud or shadow | 7 |
| `label_icnf_10m.tif` | main label: 1 burnt, 0 unburnt | 8A |
| `label_ems_overview_10m.tif` | EMSR207 burnt area, 21 June | 8B |
| `label_ems_grading_aoi05_10m.tif` | damage grade 1–3 (optional) | 8C |
| `dem_10m.tif`, `slope_10m.tif`, `aspect_10m.tif` | terrain | 9 |
| `cos2015_aoi_n4.gpkg`, `cos2015_n4_10m.tif` | land cover | 10 |
| `municipalities_aoi.gpkg` | municipalities touching the AOI | 11 |
| `firms_aoi.gpkg` (optional) | hotspots | 12 |

Helper files `ems_grading_aoi05.gpkg`, `cos2015_aoi.gpkg` and `dem_mosaic.vrt` will also be there.

1. In the Python Console editor open `qgis/check_grid.py` and run it; every line should start with OK.
2. A BAD line names the file to redo: almost always the extent was not pasted or the resolution was left empty.
3. Save the project (Ctrl+S). The `.qgz` file stores layers and styles, not data, so keep it next to the `data` folder.

In Python, convert band values with (DN − 1000) / 10000, skip pixels where a cloud mask is 1, and treat no-data in NBR (and −9999 in aspect) as missing.

## Appendix – Headless commands

Steps 3, 4, 6, 8A, 9 and 10 can also be run from Terminal with `qgis_process`, which satisfies the project rule that data steps are reproducible. These were all run on QGIS 3.44.15. The tool is inside the app bundle, not on PATH:

```bash
QP=/Applications/QGIS.app/Contents/MacOS/qgis_process
export PROJ_DATA=/Applications/QGIS.app/Contents/Resources/qgis/proj   # silences "Cannot find proj.db"
EXT="550320,592560,4399020,4452240 [EPSG:32629]"
R=data/raw; P=data/processed

# Steps 3 and 4: the two June fires in EPSG:32629, then the 5 km AOI
$QP run native:extractbyexpression -- INPUT=$R/icnf/ardida_2017/ardida_2017.shp \
  EXPRESSION="\"Cod_SGIF\" IN ('BL4171577', 'BL217377')" OUTPUT=/tmp/sel.gpkg
$QP run native:reprojectlayer -- INPUT=/tmp/sel.gpkg TARGET_CRS=EPSG:32629 OUTPUT=$P/fires_june2017.gpkg
$QP run native:buffer -- INPUT=$P/fires_june2017.gpkg DISTANCE=5000 DISSOLVE=true OUTPUT=$P/aoi_5km.gpkg

# Step 6, one band (the script loops over all 32)
$QP run gdal:warpreproject -- INPUT=<band.jp2> TARGET_CRS=EPSG:32629 RESAMPLING=1 TARGET_RESOLUTION=10 \
  TARGET_EXTENT="$EXT" TARGET_EXTENT_CRS=EPSG:32629 DATA_TYPE=0 OUTPUT=$P/s2_20170614_B12.tif   # RESAMPLING=0 for SCL

# Step 8A: ICNF label (UNITS=1 georeferenced, DATA_TYPE=0 Byte)
$QP run gdal:rasterize -- INPUT=$P/fires_june2017.gpkg BURN=1 UNITS=1 WIDTH=10 HEIGHT=10 \
  EXTENT="$EXT" NODATA=255 DATA_TYPE=0 INIT=0 OUTPUT=$P/label_icnf_10m.tif

# Step 9: a list input is repeated, one INPUT= per file
ARGS=(); for f in $R/dem_glo30/*.tif; do ARGS+=("INPUT=$f"); done
$QP run gdal:buildvirtualraster -- "${ARGS[@]}" SEPARATE=false OUTPUT=$P/dem_mosaic.vrt
$QP run gdal:warpreproject -- INPUT=$P/dem_mosaic.vrt TARGET_CRS=EPSG:32629 RESAMPLING=1 TARGET_RESOLUTION=10 \
  TARGET_EXTENT="$EXT" TARGET_EXTENT_CRS=EPSG:32629 DATA_TYPE=0 OUTPUT=$P/dem_10m.tif
$QP run gdal:slope  -- INPUT=$P/dem_10m.tif BAND=1 SCALE=1 COMPUTE_EDGES=true OUTPUT=$P/slope_10m.tif
$QP run gdal:aspect -- INPUT=$P/dem_10m.tif BAND=1 COMPUTE_EDGES=true OUTPUT=$P/aspect_10m.tif

# Step 10: clip land cover to the rectangle, to EPSG:32629, make the integer code, rasterize (DATA_TYPE=2 UInt16)
$QP run native:extractbyextent -- INPUT="$R/cos2015/COS2015v2-S1.gpkg|layername=COS2015v2" EXTENT="$EXT" CLIP=true OUTPUT=/tmp/cos.gpkg
$QP run native:reprojectlayer -- INPUT=/tmp/cos.gpkg TARGET_CRS=EPSG:32629 OUTPUT=$P/cos2015_aoi.gpkg
$QP run native:fieldcalculator -- INPUT=$P/cos2015_aoi.gpkg FIELD_NAME=cos_n4 FIELD_TYPE=1 \
  FORMULA="to_int(replace(\"COS15n4_C\", '.', ''))" OUTPUT=$P/cos2015_aoi_n4.gpkg
$QP run gdal:rasterize -- INPUT=$P/cos2015_aoi_n4.gpkg FIELD=cos_n4 UNITS=1 WIDTH=10 HEIGHT=10 \
  EXTENT="$EXT" NODATA=0 DATA_TYPE=2 INIT=0 OUTPUT=$P/cos2015_n4_10m.tif
```

The Raster Calculator expressions of Step 7 have no `qgis_process` equivalent in 3.44 (only the GDAL calculator, which uses different syntax); they are run from the Raster menu.
