#!/usr/bin/env python3
"""Export Indian places SQLite database for Cloudflare D1.

Usage:
    python scripts/export_d1.py
"""
import gzip
import shutil
import sqlite3
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_GZ = ROOT / "data" / "india_places.sqlite.gz"
OUTPUT_DIR = ROOT / "d1_export"

SCHEMA_SQL = """-- Cloudflare D1 Schema for Live Weather Tracker
CREATE TABLE IF NOT EXISTS places (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    feature_code TEXT NOT NULL,
    admin1 TEXT,
    admin2 TEXT,
    admin3 TEXT,
    population INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_places_name ON places(name COLLATE NOCASE);
CREATE INDEX IF NOT EXISTS idx_places_population ON places(population DESC);
CREATE INDEX IF NOT EXISTS idx_places_admin2 ON places(admin2 COLLATE NOCASE);
CREATE INDEX IF NOT EXISTS idx_places_admin1 ON places(admin1 COLLATE NOCASE);
CREATE INDEX IF NOT EXISTS idx_places_feature ON places(feature_code);
"""


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    schema_path = OUTPUT_DIR / "schema.sql"
    with open(schema_path, "w", encoding="utf-8") as f:
        f.write(SCHEMA_SQL)
    print(f"Created schema at: {schema_path}")

    # Decompress database to temp
    with tempfile.NamedTemporaryFile(suffix=".sqlite") as tmp:
        print("Decompressing database...")
        with gzip.open(DB_GZ, "rb") as src, open(tmp.name, "wb") as dst:
            shutil.copyfileobj(src, dst, length=1024 * 1024)

        con = sqlite3.connect(tmp.name)
        cur = con.cursor()
        total = cur.execute("SELECT count(*) FROM places").fetchone()[0]
        print(f"Total places in database: {total:,}")

        # Export top populated places and districts for quick D1 seed (50,000 places seed)
        seed_path = OUTPUT_DIR / "seed_districts_and_cities.sql"
        print(f"Generating primary seed: {seed_path}...")
        cur.execute(
            """SELECT id, name, latitude, longitude, feature_code, admin1, admin2, admin3, population 
               FROM places 
               WHERE feature_code IN ('ADM2', 'PPLA', 'PPLA2', 'PPLC', 'PPLA3') OR population > 5000
               ORDER BY population DESC"""
        )
        rows = cur.fetchall()
        print(f"Writing {len(rows):,} key places (all districts, cities, towns) to seed...")

        with open(seed_path, "w", encoding="utf-8") as f:
            f.write("BEGIN TRANSACTION;\n")
            for r in rows:
                def sql_esc(v):
                    if v is None: return "NULL"
                    if isinstance(v, (int, float)): return str(v)
                    return "'" + str(v).replace("'", "''") + "'"

                vals = [str(r[0]), sql_esc(r[1]), str(r[2]), str(r[3]), sql_esc(r[4]), sql_esc(r[5]), sql_esc(r[6]), sql_esc(r[7]), str(r[8])]
                f.write(f"INSERT OR IGNORE INTO places VALUES ({', '.join(vals)});\n")
            f.write("COMMIT;\n")

        print("Export completed successfully!")


if __name__ == "__main__":
    main()
