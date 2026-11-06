#!/usr/bin/env python3
"""Download the datasets for the DLAG course project (June 2017 Pedrogao Grande wildfire).

Usage, from this folder:
    python3 download_data.py                 # everything listed in README.md (about 6.6 GB)
    python3 download_data.py --dry-run       # show the plan and sizes, download nothing
    python3 download_data.py --no-s2         # skip Sentinel-2 (no Copernicus login needed)
    python3 download_data.py --s2-minimal    # Sentinel-2 only for 14 Jun (pre) and 4 Jul 2017 (post)
    python3 download_data.py --unzip-s2      # also unzip the Sentinel-2 SAFE archives (+ about 5 GB)
    python3 download_data.py --all-ems-pdfs  # PDF maps for all 11 EMSR207 AOIs (+ about 680 MB)
    python3 download_data.py --benchmark     # Satellite Burned Area Dataset from Zenodo (+ 14 GB)

Only the Python 3 standard library is used. Re-running skips finished files and resumes partial ones.
Copernicus Data Space credentials come from CDSE_USERNAME / CDSE_PASSWORD (plus CDSE_TOTP if your
account uses two-factor login) or are asked for interactively. They are sent only to
identity.dataspace.copernicus.eu and are never written to disk.
"""
import argparse
import csv
import getpass
import json
import os
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
LOG = ROOT / "download_log.csv"
UA = "DLAG-project-downloader/1.0 (Python urllib)"
MB = 1_000_000

# ICNF perimeters of the Pedrogao Grande and Gois fires span lon -8.353..-7.973, lat 39.784..40.172.
# This box adds a margin of about 5 km and is used to cut the FIRMS hotspots down to the fire.
AOI = {"lon_min": -8.45, "lon_max": -7.90, "lat_min": 39.70, "lat_max": 40.25}
FIRMS_DATES = ("2017-06-15", "2017-06-25")

# Sentinel-2 L2A, Collection-1, tile T29TNE, relative orbit 37: this tile holds the whole fire plus
# the 5 km buffer. Orbit 80 scenes of the same tile stop west of the fire, and 19-29 June is cloudy.
# (date, CDSE product Id, product name, size in MB, cloud % over the whole tile)
S2_PRODUCTS = [
    ("2017-06-04", "98c0f69a-cf21-4689-8888-aea7d028dcfe",
     "S2A_MSIL2A_20170604T112121_N0500_R037_T29TNE_20231112T010859.SAFE", 1228, 1.5),
    ("2017-06-14", "be9f55e1-35f1-42e5-8e4f-c140749682c5",
     "S2A_MSIL2A_20170614T112111_N0500_R037_T29TNE_20231009T091756.SAFE", 1235, 10.7),
    ("2017-07-04", "5f0cc035-9773-4830-8380-68579e690ccf",
     "S2A_MSIL2A_20170704T112111_N0500_R037_T29TNE_20231006T233809.SAFE", 1237, 6.1),
    ("2017-07-14", "82fb47f5-bf5f-4d54-8d34-c3d88075df09",
     "S2A_MSIL2A_20170714T112111_N0500_R037_T29TNE_20231005T073211.SAFE", 1225, 1.5),
]
S2_MINIMAL_DATES = {"2017-06-14", "2017-07-04"}
CDSE_TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
CDSE_DOWNLOAD_URL = "https://zipper.dataspace.copernicus.eu/odata/v1/Products({id})/$value"

# Copernicus EMS EMSR207: all 61 products, as listed on the activation page.
EMS_BASE = ("https://cems-mapping-website.s3.eu-west-1.amazonaws.com/static/activations/EMSR207/"
            "EMSR207_{aoi}_{product}")
EMS_PRODUCTS = {
    "01MIRANDADOCORVO": ["01DELINEATION_MAP_v1", "01DELINEATION_MONIT01_v1", "01DELINEATION_MONIT02_v1",
                         "02GRADING_MAP_v2", "02GRADING_MONIT01_v2", "02GRADING_MONIT02_v1"],
    "02LOUSA": ["01DELINEATION_MAP_v1", "01DELINEATION_MONIT01_v2", "01DELINEATION_MONIT02_v1",
                "02GRADING_MAP_v2", "02GRADING_MONIT01_v2", "02GRADING_MONIT02_v1"],
    "03PAMPILHOSADASERRA": ["01DELINEATION_MAP_v1", "01DELINEATION_MONIT01_v1", "01DELINEATION_MONIT02_v1",
                            "02GRADING_MAP_v2", "02GRADING_MONIT01_v2", "02GRADING_MONIT02_v1"],
    "04AVELAR": ["01DELINEATION_MAP_v1", "01DELINEATION_MONIT01_v1", "01DELINEATION_MONIT02_v1",
                 "01DELINEATION_MONIT03_v1", "02GRADING_MAP_v2", "02GRADING_MONIT01_v2", "02GRADING_MONIT02_v1"],
    "05PEDROGAOGRANDE": ["01DELINEATION_MAP_v2", "01DELINEATION_MONIT01_v1", "01DELINEATION_MONIT02_v1",
                         "01DELINEATION_MONIT03_v1", "02GRADING_MAP_v2", "02GRADING_MONIT01_v2",
                         "02GRADING_MONIT02_v1"],
    "06MADEIRA": ["01DELINEATION_MAP_v1", "01DELINEATION_MONIT01_v1", "01DELINEATION_MONIT02_v1",
                  "02GRADING_MAP_v2", "02GRADING_MONIT01_v2", "02GRADING_MONIT02_v1"],
    "07ALVAIAZERE": ["01DELINEATION_MAP_v1", "01DELINEATION_MONIT01_v1", "01DELINEATION_MONIT02_v1",
                     "02GRADING_MAP_v2", "02GRADING_MONIT01_v2", "02GRADING_MONIT02_v1"],
    "08CERNACHEDOBONJARDIM": ["01DELINEATION_MAP_v1", "01DELINEATION_MONIT01_v1", "01DELINEATION_MONIT02_v1",
                              "02GRADING_MAP_v2", "02GRADING_MONIT01_v2", "02GRADING_MONIT02_v1"],
    "09SERTA": ["01DELINEATION_MAP_v1", "01DELINEATION_MONIT01_v1", "01DELINEATION_MONIT02_v1"],
    "10ORVALHO": ["01DELINEATION_MAP_v1", "01DELINEATION_MONIT01_v1", "01DELINEATION_MONIT02_v1",
                  "02GRADING_MAP_v2", "02GRADING_MONIT01_v2", "02GRADING_MONIT02_v2"],
    "11PEDROGAOGRANDEOVERVIEW": ["01DELINEATION_MAP_v1", "01DELINEATION_MONIT01_v1"],
}
EMS_PDF_AOIS_DEFAULT = {"05PEDROGAOGRANDE", "11PEDROGAOGRANDEOVERVIEW"}

# Copernicus DEM GLO-30 public tiles on AWS (no account needed). Each covers 1 x 1 degree.
DEM_TILES = {"N39_00_W009_00": 47.8, "N39_00_W008_00": 44.5, "N40_00_W009_00": 38.4, "N40_00_W008_00": 43.3}
DEM_URL = ("https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_{t}_DEM/"
           "Copernicus_DSM_COG_10_{t}_DEM.tif")

ICNF_SHP_URL = "https://si.icnf.pt/shp/ardida_2017"
ICNF_JUNE_URL = ("https://sigservices.icnf.pt/server/rest/services/BDG/areas_ardidas/MapServer/3/query?"
                 "objectIds=69728,68910&outFields=*&outSR=4326&f=geojson")
CAOP_URL = "https://www.dgterritorio.gov.pt/sites/default/files/ficheiros-cartografia/Cont_AAD_CAOP2017.zip"
COS_URL = "https://geo2.dgterritorio.gov.pt/cos/S1/COS2015/COS2015v2-S1-gpkg.zip"
FIRMS_URLS = {
    "MODIS": ("https://firms.modaps.eosdis.nasa.gov/data/country/modis/2017/modis_2017_Portugal.csv", 0.5),
    "VIIRS_SNPP": ("https://firms.modaps.eosdis.nasa.gov/data/country/viirs-snpp/2017/"
                   "viirs-snpp_2017_Portugal.csv", 1.5),
}
ZENODO_URL = "https://zenodo.org/records/6597139/files/{name}?download=1"
BENCH_PARTS = {f"Satellite_burned_area_dataset_part{i}.zip": s
               for i, s in zip(range(1, 6), (3500, 3000, 2900, 3200, 1500))}


# ---------------------------------------------------------------- plan

def plan(args):
    items = []

    def add(group, url, dest, size_mb, kind="open", is_zip=False, unzip_to=None, is_json=False):
        items.append(dict(group=group, url=url, dest=dest, size_mb=size_mb, kind=kind,
                          is_zip=is_zip, unzip_to=unzip_to, is_json=is_json))

    d = RAW / "icnf"
    add("ICNF burnt areas 2017", ICNF_SHP_URL, d / "ardida_2017.zip", 50, is_zip=True, unzip_to=d / "ardida_2017")
    add("ICNF burnt areas 2017", ICNF_JUNE_URL, d / "icnf_june2017_pedrogao_gois.geojson", 1, is_json=True)

    d = RAW / "emsr207"
    for aoi, products in EMS_PRODUCTS.items():
        for p in products:
            name = f"EMSR207_{aoi}_{p}"
            base = EMS_BASE.format(aoi=aoi, product=p)
            add("Copernicus EMS EMSR207 (vector)", base + "_vector.zip", d / "vector" / f"{name}_vector.zip",
                6.6, is_zip=True, unzip_to=d / "vector" / name)
            if args.all_ems_pdfs or aoi in EMS_PDF_AOIS_DEFAULT:
                add("Copernicus EMS EMSR207 (PDF maps)", base + "_200dpi.pdf", d / "pdf" / f"{name}_200dpi.pdf", 13.5)

    for t, size in DEM_TILES.items():
        add("Copernicus DEM GLO-30", DEM_URL.format(t=t), RAW / "dem_glo30" / f"Copernicus_DSM_COG_10_{t}_DEM.tif", size)

    d = RAW / "caop2017"
    add("CAOP 2017", CAOP_URL, d / "Cont_AAD_CAOP2017.zip", 32.4, is_zip=True, unzip_to=d / "Cont_AAD_CAOP2017")
    d = RAW / "cos2015"
    add("COS2015 v2 (land cover)", COS_URL, d / "COS2015v2-S1-gpkg.zip", 605.8, is_zip=True, unzip_to=d)

    for sensor, (url, size) in FIRMS_URLS.items():
        add("NASA FIRMS active fires", url, RAW / "firms" / Path(urllib.parse.urlparse(url).path).name, size)

    d = RAW / "benchmark_colomba2022"
    add("Satellite Burned Area Dataset", ZENODO_URL.format(name="satellite_data.csv"), d / "satellite_data.csv", 0.02)
    if args.benchmark:
        for name, size in BENCH_PARTS.items():
            add("Satellite Burned Area Dataset", ZENODO_URL.format(name=name), d / name, size, is_zip=True,
                unzip_to=d)

    if not args.no_s2:
        for date, pid, name, size, _cloud in S2_PRODUCTS:
            if args.s2_minimal and date not in S2_MINIMAL_DATES:
                continue
            stem = name[:-len(".SAFE")]
            add("Sentinel-2 L2A (T29TNE)", CDSE_DOWNLOAD_URL.format(id=pid), RAW / "sentinel2" / f"{stem}.zip",
                size, kind="cdse", is_zip=True, unzip_to=(RAW / "sentinel2") if args.unzip_s2 else None)
    return items


def is_done(item):
    p = item["dest"]
    marker = (item["unzip_to"] or p.parent) / f".{p.stem}.unzipped"
    if item["is_zip"] and marker.exists():
        return True  # extracted and verified earlier; the zip may have been deleted to save space
    if not p.exists() or p.stat().st_size == 0:
        return False
    return zipfile.is_zipfile(p) if item["is_zip"] else True


# ---------------------------------------------------------------- HTTP

class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # redirects are followed by hand in open_url()


_OPENER = urllib.request.build_opener(_NoRedirect)


def open_url(url, headers=None, data=None, timeout=120):
    """Open a URL, following redirects by hand so the Copernicus token survives its own redirects
    but is never forwarded to any other host."""
    headers = dict(headers or {})
    headers.setdefault("User-Agent", UA)
    for _ in range(10):
        req = urllib.request.Request(url, data=data, headers=headers)
        try:
            return _OPENER.open(req, timeout=timeout)
        except urllib.error.HTTPError as e:
            loc = e.headers.get("Location")
            if e.code in (301, 302, 303, 307, 308) and loc:
                url = urllib.parse.urljoin(url, loc)
                if not (urllib.parse.urlparse(url).hostname or "").endswith("dataspace.copernicus.eu"):
                    headers.pop("Authorization", None)
                if e.code == 303:
                    data = None
                continue
            raise
    raise RuntimeError(f"too many redirects: {url}")


def log(item, nbytes):
    new = not LOG.exists()
    with open(LOG, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["downloaded_utc", "dataset", "file", "bytes", "url"])
        url = item["url"] if item["kind"] == "open" else item["url"]  # no credentials are part of any URL
        w.writerow([datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), item["group"],
                    str(item["dest"].relative_to(ROOT)), nbytes, url])


def fetch(item, headers=None):
    dest = item["dest"]
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_name(dest.name + ".part")
    have = part.stat().st_size if part.exists() else 0
    h = dict(headers or {})
    if have:
        h["Range"] = f"bytes={have}-"
    resp = None
    try:
        resp = open_url(item["url"], h)
    except urllib.error.HTTPError as e:
        if not (e.code == 416 and have):  # 416 = the .part file is already complete
            raise
    if resp is not None:
        with resp:
            if have and resp.status != 206:
                have = 0  # server ignored the range request: start again
            length = resp.headers.get("Content-Length")
            total = int(length) + have if length else None
            done, t0, last = have, time.time(), 0.0
            with open(part, "ab" if have else "wb") as f:
                while True:
                    chunk = resp.read(1 << 20)
                    if not chunk:
                        break
                    f.write(chunk)
                    done += len(chunk)
                    if time.time() - last > 2:
                        last = time.time()
                        pct = f"{100 * done / total:5.1f}%" if total else ""
                        rate = (done - have) / max(time.time() - t0, 1e-6) / MB
                        print(f"\r      {done / MB:9.1f} MB {pct} {rate:6.1f} MB/s", end="", flush=True)
            print(f"\r      {done / MB:9.1f} MB done" + " " * 24)
            if total and done != total:
                raise RuntimeError(f"incomplete ({done} of {total} bytes); run the script again to resume")
    if item["is_zip"] and not zipfile.is_zipfile(part):
        bad = part.with_name(dest.name + ".bad")
        part.replace(bad)
        raise RuntimeError(f"not a zip file (the server probably sent an error page); kept as {bad.name}")
    if item["is_json"]:
        try:
            j = json.loads(part.read_text(encoding="utf-8"))
            assert "features" in j and j["features"], "no features"
        except Exception as e:
            raise RuntimeError(f"unexpected JSON from server: {e}")
    part.replace(dest)
    log(item, dest.stat().st_size)


# ---------------------------------------------------------------- Copernicus login

class CDSE:
    def __init__(self):
        self.user = os.environ.get("CDSE_USERNAME") or input("  Copernicus Data Space username (e-mail): ").strip()
        self.pw = os.environ.get("CDSE_PASSWORD") or getpass.getpass("  Copernicus Data Space password (hidden): ")
        self.refresh = None

    def _post(self, data):
        body = urllib.parse.urlencode(data).encode()
        with open_url(CDSE_TOKEN_URL, {"Content-Type": "application/x-www-form-urlencoded"}, data=body, timeout=60) as r:
            return json.load(r)

    def token(self):
        """Fresh access token for each product (they expire after about 10 minutes)."""
        if self.refresh:
            try:
                j = self._post({"client_id": "cdse-public", "grant_type": "refresh_token",
                                "refresh_token": self.refresh})
                self.refresh = j.get("refresh_token", self.refresh)
                return j["access_token"]
            except urllib.error.HTTPError:
                self.refresh = None
        data = {"client_id": "cdse-public", "grant_type": "password", "username": self.user, "password": self.pw}
        if os.environ.get("CDSE_TOTP"):
            data["totp"] = os.environ["CDSE_TOTP"]
        try:
            j = self._post(data)
        except urllib.error.HTTPError as e:
            if e.code not in (400, 401):
                raise
            code = "" if "totp" in data else input(
                "  Login refused. If your account uses two-factor login, type the 6-digit code "
                "(or press Enter to stop): ").strip()
            if not code:
                raise SystemExit("  Copernicus login failed: check your username and password.")
            data["totp"] = code
            j = self._post(data)
        self.refresh = j.get("refresh_token")
        return j["access_token"]


# ---------------------------------------------------------------- post-processing

def safe_unzip(zp, out_dir):
    marker = out_dir / f".{zp.stem}.unzipped"
    if marker.exists():
        return False
    out_dir.mkdir(parents=True, exist_ok=True)
    root = out_dir.resolve()
    with zipfile.ZipFile(zp) as z:
        for m in z.infolist():
            target = (out_dir / m.filename).resolve()
            if target != root and root not in target.parents:
                raise RuntimeError(f"unsafe path inside {zp.name}: {m.filename}")
        z.extractall(out_dir)
    marker.touch()
    return True


def firms_subset():
    """Cut the two Portugal-wide 2017 FIRMS files down to the fire box and 15-25 June 2017."""
    out = RAW / "firms" / f"firms_aoi_{FIRMS_DATES[0]}_to_{FIRMS_DATES[1]}.csv"
    cols = ["sensor", "latitude", "longitude", "acq_date", "acq_time", "satellite", "confidence", "frp", "daynight"]
    counts, rows = {}, []
    for sensor, (url, _) in FIRMS_URLS.items():
        src = RAW / "firms" / Path(urllib.parse.urlparse(url).path).name
        if not src.exists():
            continue
        with open(src, newline="") as f:
            for r in csv.DictReader(f):
                try:
                    lat, lon = float(r["latitude"]), float(r["longitude"])
                except (KeyError, ValueError):
                    continue
                if (AOI["lat_min"] <= lat <= AOI["lat_max"] and AOI["lon_min"] <= lon <= AOI["lon_max"]
                        and FIRMS_DATES[0] <= r.get("acq_date", "") <= FIRMS_DATES[1]):
                    rows.append({"sensor": sensor, **{c: r.get(c, "") for c in cols[1:]}})
                    counts[sensor] = counts.get(sensor, 0) + 1
    if not rows:
        return None
    rows.sort(key=lambda r: (r["acq_date"], r["acq_time"].zfill(4)))
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    return out, counts


def benchmark_note():
    p = RAW / "benchmark_colomba2022" / "satellite_data.csv"
    if not p.exists():
        return None
    with open(p, newline="") as f:
        rows = list(csv.DictReader(f))
    hits = [(r["folder"], r.get("fold", "?")) for r in rows if r.get("folder", "").startswith("EMSR207")]
    folds = sorted({fold for _, fold in hits})
    return len(rows), len(hits), folds


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-s2", action="store_true")
    ap.add_argument("--s2-minimal", action="store_true")
    ap.add_argument("--unzip-s2", action="store_true")
    ap.add_argument("--all-ems-pdfs", action="store_true")
    ap.add_argument("--benchmark", action="store_true")
    args = ap.parse_args()

    items = plan(args)
    todo = [it for it in items if not is_done(it)]
    groups = {}
    for it in items:
        g = groups.setdefault(it["group"], {"n": 0, "done": 0, "mb": 0.0})
        g["n"] += 1
        g["done"] += is_done(it)
        g["mb"] += 0 if is_done(it) else (it["size_mb"] or 0)
    print(f"Data folder: {ROOT}\n")
    print(f"  {'dataset':38s} {'files':>5s} {'have':>5s} {'to fetch':>10s}")
    for name, g in groups.items():
        print(f"  {name:38s} {g['n']:5d} {g['done']:5d} {g['mb'] / 1000:8.2f} GB")
    need = sum(it["size_mb"] or 0 for it in todo) / 1000
    free = shutil.disk_usage(ROOT).free / 1e9
    extra = 0.0
    if args.unzip_s2:
        extra += sum(s for d, _, _, s, _ in S2_PRODUCTS if not args.s2_minimal or d in S2_MINIMAL_DATES) / 1000
    extra += 1.5  # unzipped COS2015 GeoPackage, EMS vectors, ICNF and CAOP (estimate)
    print(f"\n  To download: about {need:.1f} GB (+ about {extra:.1f} GB once unzipped). Free: {free:.1f} GB")
    if args.dry_run:
        return
    if (need + extra) * 1.05 > free:
        raise SystemExit("  Not enough free disk space for this selection; try --s2-minimal or drop --benchmark.")

    failures = []
    for it in [i for i in todo if i["kind"] == "open"]:
        print(f"\n  -> {it['group']}: {it['dest'].relative_to(ROOT)}")
        try:
            fetch(it)
        except Exception as e:  # keep going; report at the end
            failures.append((it, e))
            print(f"      FAILED: {e}")

    s2 = [i for i in todo if i["kind"] == "cdse"]
    if s2:
        print("\n  Sentinel-2 needs your Copernicus Data Space login.")
        auth = CDSE()
        for it in s2:
            print(f"\n  -> {it['group']}: {it['dest'].relative_to(ROOT)}")
            try:
                fetch(it, {"Authorization": f"Bearer {auth.token()}"})
            except SystemExit:
                raise
            except Exception as e:
                failures.append((it, e))
                print(f"      FAILED: {e}")

    print("\n  Unzipping ...")
    for it in items:
        if it["unzip_to"] is not None and is_done(it):
            try:
                if safe_unzip(it["dest"], it["unzip_to"]):
                    print(f"      {it['dest'].name} -> {it['unzip_to'].relative_to(ROOT)}")
            except Exception as e:
                failures.append((it, e))
                print(f"      FAILED to unzip {it['dest'].name}: {e}")

    res = firms_subset()
    if res:
        out, counts = res
        print(f"\n  FIRMS hotspots in the fire box, {FIRMS_DATES[0]} to {FIRMS_DATES[1]}: "
              + ", ".join(f"{k} {v}" for k, v in counts.items()) + f" -> {out.relative_to(ROOT)}")
    note = benchmark_note()
    if note:
        n, hits, folds = note
        print(f"\n  Benchmark index: {n} fires; {hits} are EMSR207 areas, all in fold(s) {', '.join(folds)}. "
              "Hold those fold(s) out of training so the test fire stays unseen.")

    print("\n  Not scripted (needs a web form): EFFIS burnt areas -> https://effis.jrc.ec.europa.eu/apps/data.request.form")
    if failures:
        print(f"\n  {len(failures)} file(s) failed; run the script again to retry and resume:")
        for it, e in failures:
            print(f"    - {it['dest'].relative_to(ROOT)}: {e}")
        sys.exit(1)
    print("\n  All done. See README.md for what each folder holds; download_log.csv records every file.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n  Stopped. Run the script again to resume where it left off.")
        sys.exit(130)
