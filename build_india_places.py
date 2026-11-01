#!/usr/bin/env python3
"""Build the bundled all-India place index from GeoNames.

What it does
------------
Downloads the latest GeoNames India extract (or uses local files), keeps
populated places and administrative divisions, and writes:

    data/india_places.sqlite        (uncompressed, ignored by git)
    data/india_places.sqlite.gz     (committed, decompressed at runtime)

The app searches this SQLite file first. Live Nominatim/Open-Meteo remains the
fallback for PIN codes and places newer than this snapshot.

Usage
-----
    python build_india_places.py
    python build_india_places.py --input IN.txt --admin1 admin1CodesASCII.txt \
        --admin2 admin2Codes.txt
    python build_india_places.py --keep-sqlite

Data: GeoNames, CC BY 4.0 — https://www.geonames.org/
"""
from __future__ import annotations

import argparse
import gzip
import math
import os
import shutil
import sqlite3
import sys
import tempfile
import urllib.request
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DEFAULT_DB = DATA_DIR / "india_places.sqlite"
DEFAULT_GZ = DATA_DIR / "india_places.sqlite.gz"

BASE_URL = "https://download.geonames.org/export/dump"
FILES = {
    "IN.zip": f"{BASE_URL}/IN.zip",
    "admin1CodesASCII.txt": f"{BASE_URL}/admin1CodesASCII.txt",
    "admin2Codes.txt": f"{BASE_URL}/admin2Codes.txt",
}

FEATURE_CLASSES = {"P", "A"}  # populated places + administrative divisions


def download(url: str, dest: Path) -> None:
    if dest.is_file() and dest.stat().st_size > 0:
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {url} ...", flush=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    with urllib.request.urlopen(url, timeout=120) as response, open(tmp, "wb") as out:
        shutil.copyfileobj(response, out, length=1024 * 1024)
    os.replace(tmp, dest)


def load_admin1(path: Path) -> dict[str, str]:
    names: dict[str, str] = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 4 and parts[0].startswith("IN."):
                names[parts[0].split(".", 1)[1]] = parts[2] or parts[1]
    return names


def load_admin2(path: Path) -> dict[tuple[str, str], str]:
    names: dict[tuple[str, str], str] = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 4 or not parts[0].startswith("IN."):
                continue
            codes = parts[0].split(".")
            if len(codes) >= 3:
                raw_name = parts[2] or parts[1]
                clean = re.sub(r"^(District|Zila)\s+", "", raw_name, flags=re.I)
                clean = re.sub(r"\s+(District|district|Zila|zila|Division|division)$", "", clean).strip()
                names[(codes[1], codes[2])] = clean or raw_name
    return names


def load_admin3(path: Path) -> dict[tuple[str, str, str], str]:
    """GeoNames has no admin3Codes file; derive names from the ADM3 rows."""
    names: dict[tuple[str, str, str], str] = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 19 or parts[6] != "A" or parts[7] != "ADM3":
                continue
            a1, a2, a3 = parts[10], parts[11], parts[12]
            if a1 and a2 and a3:
                names[(a1, a2, a3)] = parts[2] or parts[1]
    return names


def valid_coord(lat: float, lon: float) -> bool:
    return (
        math.isfinite(lat)
        and math.isfinite(lon)
        and -90 <= lat <= 90
        and -180 <= lon <= 180
    )


def build(
    geonames_txt: Path,
    admin1_path: Path,
    admin2_path: Path,
    output: Path,
) -> Counter:
    admin1 = load_admin1(admin1_path)
    admin2 = load_admin2(admin2_path)
    admin3 = load_admin3(geonames_txt)

    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()

    con = sqlite3.connect(output)
    con.executescript(
        """
        PRAGMA journal_mode = OFF;
        PRAGMA synchronous = OFF;
        PRAGMA temp_store = MEMORY;
        PRAGMA page_size = 4096;
        CREATE TABLE places (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            local_name TEXT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            feature_code TEXT NOT NULL,
            admin1 TEXT,
            admin2 TEXT,
            admin3 TEXT,
            population INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        """
    )

    counts: Counter = Counter()
    batch: list[tuple] = []
    batch_size = 10_000

    def flush() -> None:
        if not batch:
            return
        con.executemany(
            "INSERT OR IGNORE INTO places "
            "(id, name, local_name, latitude, longitude, feature_code, "
            " admin1, admin2, admin3, population) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            batch,
        )
        batch.clear()

    with open(geonames_txt, encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 19:
                continue
            feature_class = parts[6]
            feature_code = parts[7]
            if feature_class not in FEATURE_CLASSES:
                continue

            name = parts[1].strip()
            ascii_name = parts[2].strip() or name
            if not name or not ascii_name:
                continue

            if feature_code == "ADM2":
                name = re.sub(r"^(District|Zila)\s+", "", name, flags=re.I)
                name = re.sub(r"\s+(District|district|Zila|zila|Division|division)$", "", name).strip()
                ascii_name = re.sub(r"^(District|Zila)\s+", "", ascii_name, flags=re.I)
                ascii_name = re.sub(r"\s+(District|district|Zila|zila|Division|division)$", "", ascii_name).strip()

            try:
                lat = float(parts[4])
                lon = float(parts[5])
            except ValueError:
                continue
            if not valid_coord(lat, lon):
                continue

            try:
                population = int(parts[14] or 0)
            except ValueError:
                population = 0

            a1_code, a2_code, a3_code = parts[10], parts[11], parts[12]
            a1 = admin1.get(a1_code, a1_code) if a1_code else ""
            a2 = admin2.get((a1_code, a2_code), a2_code) if a2_code else ""
            a3 = admin3.get((a1_code, a2_code, a3_code), "") if a3_code else ""

            batch.append(
                (
                    int(parts[0]),
                    ascii_name,
                    name,
                    lat,
                    lon,
                    feature_code,
                    a1,
                    a2,
                    a3,
                    population,
                )
            )
            counts[feature_code] += 1
            if len(batch) >= batch_size:
                flush()

    flush()
    con.execute("CREATE INDEX idx_places_name ON places(name COLLATE NOCASE)")
    con.execute("CREATE INDEX idx_places_population ON places(population DESC)")
    con.execute("CREATE INDEX idx_places_admin2 ON places(admin2 COLLATE NOCASE)")
    con.execute("CREATE INDEX idx_places_admin1 ON places(admin1 COLLATE NOCASE)")
    con.execute("CREATE INDEX idx_places_feature ON places(feature_code)")
    con.executemany(
        "INSERT INTO meta(key, value) VALUES (?, ?)",
        [
            ("source", "GeoNames IN.zip"),
            ("license", "CC BY 4.0"),
            ("snapshot", date.today().isoformat()),
            ("rows", str(sum(counts.values()))),
        ],
    )
    con.commit()
    con.execute("VACUUM")
    con.commit()
    con.close()
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="Path to GeoNames IN.txt")
    parser.add_argument("--admin1", type=Path, help="Path to admin1CodesASCII.txt")
    parser.add_argument("--admin2", type=Path, help="Path to admin2Codes.txt")
    parser.add_argument("--output", type=Path, default=DEFAULT_DB)
    parser.add_argument("--gz", type=Path, default=DEFAULT_GZ)
    parser.add_argument(
        "--keep-sqlite",
        action="store_true",
        help="Keep the uncompressed .sqlite after gzipping it",
    )
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="kyw-geonames-") as tmp:
        tmp_dir = Path(tmp)
        if args.input:
            geonames_txt = args.input
        else:
            zip_path = tmp_dir / "IN.zip"
            download(FILES["IN.zip"], zip_path)
            print("Extracting IN.zip ...", flush=True)
            import zipfile

            with zipfile.ZipFile(zip_path) as zf:
                zf.extract("IN.txt", tmp_dir)
            geonames_txt = tmp_dir / "IN.txt"

        admin1_path = args.admin1 or (tmp_dir / "admin1CodesASCII.txt")
        admin2_path = args.admin2 or (tmp_dir / "admin2Codes.txt")
        if not args.admin1:
            download(FILES["admin1CodesASCII.txt"], admin1_path)
        if not args.admin2:
            download(FILES["admin2Codes.txt"], admin2_path)

        print(f"Building {args.output} ...", flush=True)
        counts = build(geonames_txt, admin1_path, admin2_path, args.output)

    print("\nFeature counts:")
    for code, count in counts.most_common(20):
        print(f"  {code:8s} {count:>8,}")
    print(f"  {'TOTAL':8s} {sum(counts.values()):>8,}")

    args.gz.parent.mkdir(parents=True, exist_ok=True)
    print(f"\nCompressing to {args.gz} ...", flush=True)
    with open(args.output, "rb") as src, gzip.open(args.gz, "wb", compresslevel=9) as dst:
        shutil.copyfileobj(src, dst, length=1024 * 1024)

    print(f"  sqlite: {args.output.stat().st_size / 1024 / 1024:.1f} MB")
    print(f"  gzip:   {args.gz.stat().st_size / 1024 / 1024:.1f} MB")

    if not args.keep_sqlite:
        args.output.unlink()
    return 0


if __name__ == "__main__":
    sys.exit(main())
