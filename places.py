"""Instant all-India place search backed by a bundled GeoNames index.

The index is built by ``build_india_places.py`` and stored compressed at
``data/india_places.sqlite.gz``. On first use it is decompressed once to a
temporary directory and queried read-only. If the file is missing the app
falls back to the existing live Nominatim/Open-Meteo search, so the feature
degrades gracefully.

Data: GeoNames India extract, CC BY 4.0.
https://www.geonames.org/
"""
from __future__ import annotations

import gzip
import os
import re
import shutil
import sqlite3
import tempfile
import threading
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_GZ = ROOT / "data" / "india_places.sqlite.gz"

# Bump this when the bundled database is rebuilt so old temp copies are not
# reused. Keep it in sync with build_india_places.py's snapshot date.
DB_VERSION = "2026-11-01-v2"

_DB_LOCK = threading.Lock()
_DB_PATH: Path | None = None

FEATURE_LABELS = {
    "PPLC": "capital",
    "PPLA": "city",
    "PPLA2": "city",
    "PPLA3": "town",
    "PPLA4": "town",
    "PPLA5": "town",
    "PPL": "village",
    "PPLX": "locality",
    "PPLQ": "abandoned place",
    "PPLL": "locality",
    "PPLF": "farm",
    "PPLR": "religious place",
    "PPLS": "place",
    "PPLH": "historic place",
    "PPLW": "destroyed place",
    "ADM1": "state",
    "ADM1H": "historic state",
    "ADM2": "district",
    "ADM3": "subdistrict",
    "ADM4": "subdistrict",
    "ADM5": "subdistrict",
    "ADMD": "divided administration",
    "ADMDH": "historic administration",
}

FEATURE_TYPES = {
    "PPLC": "city",
    "PPLA": "city",
    "PPLA2": "city",
    "PPLA3": "town",
    "PPLA4": "town",
    "PPLA5": "town",
    "PPL": "village",
    "PPLX": "locality",
    "PPLQ": "locality",
    "PPLL": "locality",
    "PPLF": "village",
    "PPLR": "village",
    "PPLS": "place",
    "PPLH": "locality",
    "PPLW": "locality",
    "ADM1": "state",
    "ADM1H": "state",
    "ADM2": "district",
    "ADM3": "subdistrict",
    "ADM4": "subdistrict",
    "ADM5": "subdistrict",
    "ADMD": "place",
    "ADMDH": "place",
}

# Base priority: Capitals > Cities > Districts > Towns > Villages > Subdistricts > States
FEATURE_PRIORITY = {
    "PPLC": 0,
    "PPLA": 1,
    "PPLA2": 1,
    "ADM2": 2,
    "PPLA3": 3,
    "PPLA4": 3,
    "PPLA5": 3,
    "PPL": 4,
    "ADM3": 5,
    "PPLL": 5,
    "PPLX": 6,
    "PPLF": 6,
    "PPLR": 6,
    "PPLS": 6,
    "ADM1": 7,
    "ADM4": 7,
    "ADM5": 7,
    "PPLQ": 9,
}

DISTRICT_KEYWORDS = {"district", "districts", "dist", "dt", "jila", "jilla", "zila"}
VILLAGE_KEYWORDS = {"village", "villages", "vill", "vil", "gaon", "gao", "gram", "grama", "kheda"}
SUBDISTRICT_KEYWORDS = {"subdistrict", "tehsil", "tahsil", "taluk", "taluka", "block", "mandal"}
CITY_KEYWORDS = {"city", "town", "nagar", "metro"}
NOISE_KEYWORDS = {"in", "of", "all", "the", "near", "district", "districts"}


def _normalize(text: str) -> str:
    """Lowercase, strip accents, and keep letters/digits for matching."""
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.casefold()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def _clean_district_name(name: str) -> str:
    """Strip redundant District/Division prefixes and suffixes for clean display."""
    if not name:
        return ""
    name = re.sub(r"^(District|Zila)\s+", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\s+(District|district|Zila|zila|Division|division)$", "", name).strip()
    return name


def _valid_sqlite(path: Path) -> bool:
    try:
        if not path.is_file() or path.stat().st_size < 1024:
            return False
        with open(path, "rb") as f:
            return f.read(16) == b"SQLite format 3\x00"
    except OSError:
        return False


def _database_path() -> Path | None:
    """Return the decompressed DB path, or None if the bundle is unavailable."""
    global _DB_PATH
    if _DB_PATH is not None and _valid_sqlite(_DB_PATH):
        return _DB_PATH

    with _DB_LOCK:
        if _DB_PATH is not None and _valid_sqlite(_DB_PATH):
            return _DB_PATH

        target = (
            Path(tempfile.gettempdir())
            / "know_your_weather"
            / f"india_places_{DB_VERSION}.sqlite"
        )
        if _valid_sqlite(target):
            _DB_PATH = target
            return target

        if not DB_GZ.is_file():
            return None

        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            tmp = target.with_name(f"{target.name}.{os.getpid()}.tmp")
            with gzip.open(DB_GZ, "rb") as src, open(tmp, "wb") as dst:
                shutil.copyfileobj(src, dst, length=1024 * 1024)
            if not _valid_sqlite(tmp):
                raise OSError("decompressed place database is not a SQLite file")
            
            # Ensure indexes exist for rapid prefix/admin lookups
            try:
                con = sqlite3.connect(tmp)
                con.execute("CREATE INDEX IF NOT EXISTS idx_places_name ON places(name COLLATE NOCASE)")
                con.execute("CREATE INDEX IF NOT EXISTS idx_places_population ON places(population DESC)")
                con.execute("CREATE INDEX IF NOT EXISTS idx_places_admin2 ON places(admin2 COLLATE NOCASE)")
                con.execute("CREATE INDEX IF NOT EXISTS idx_places_admin1 ON places(admin1 COLLATE NOCASE)")
                con.execute("CREATE INDEX IF NOT EXISTS idx_places_feature ON places(feature_code)")
                con.commit()
                con.close()
            except Exception:
                pass

            os.replace(tmp, target)
            _DB_PATH = target
            return target
        except (OSError, EOFError):
            try:
                tmp.unlink()
            except (OSError, UnboundLocalError):
                pass
            return None


def _connect() -> sqlite3.Connection | None:
    db = _database_path()
    if db is None:
        return None
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=5)
    con.row_factory = sqlite3.Row
    return con


def _escape_like(text: str) -> str:
    return text.replace("\\", r"\\").replace("%", r"\%").replace("_", r"\_")


def _display_type(feature_code: str, population: int) -> str:
    """Make generic GeoNames PPL rows read as village/town/city."""
    if feature_code == "PPL":
        if population >= 100_000:
            return "city"
        if population >= 10_000:
            return "town"
        return "village"
    return FEATURE_TYPES.get(feature_code, "place")


def search_local(query: str, limit: int = 10) -> list[dict]:
    """Search all Indian districts, villages, towns, and cities locally.

    Features:
    - Dedicated district support: "Sitamarhi district", "Pune district", "districts in Bihar".
    - Dedicated village support: "Bajpatti village", "villages in Sitamarhi", "Bajpatti Sitamarhi",
      "Sitamarhi Bajpatti" (district first or village first).
    - Multi-word and prefix-aware autocomplete with zero network delay.
    """
    raw_query = (query or "").strip()
    if limit <= 0 or len(raw_query) < 2 or re.fullmatch(r"\d{6}", raw_query):
        return []

    norm = _normalize(raw_query)
    if not norm:
        return []

    words = norm.split()
    target_type: str | None = None
    if any(w in DISTRICT_KEYWORDS for w in words):
        target_type = "district"
    elif any(w in VILLAGE_KEYWORDS for w in words):
        target_type = "village"
    elif any(w in SUBDISTRICT_KEYWORDS for w in words):
        target_type = "subdistrict"
    elif any(w in CITY_KEYWORDS for w in words):
        target_type = "city"

    content_words = [
        w for w in words
        if w not in (DISTRICT_KEYWORDS | VILLAGE_KEYWORDS | SUBDISTRICT_KEYWORDS | CITY_KEYWORDS | NOISE_KEYWORDS)
    ]
    if not content_words:
        content_words = [w for w in words if w not in NOISE_KEYWORDS] or words

    core_term = " ".join(content_words)
    con = _connect()
    if con is None:
        return []

    try:
        rows: list[sqlite3.Row] = []

        # Pattern 1: "villages in <District/State>" or "<District> villages"
        if target_type == "village" and (
            any(w in ("in", "of") for w in words)
            or (len(words) >= 2 and words[-1] in VILLAGE_KEYWORDS)
        ):
            like = f"{_escape_like(core_term)}%"
            sql = """
                SELECT id, name, latitude, longitude, feature_code,
                       admin1, admin2, admin3, population
                FROM places
                WHERE feature_code IN ('PPL', 'PPLL', 'PPLF', 'PPLR', 'PPLS')
                  AND (admin2 COLLATE NOCASE LIKE ? ESCAPE '\\' OR admin1 COLLATE NOCASE LIKE ? ESCAPE '\\')
                ORDER BY population DESC, name
                LIMIT ?
            """
            rows.extend(con.execute(sql, (like, like, limit * 3)))

        # Pattern 2: "districts in <State>" or "<State> districts"
        elif target_type == "district" and (
            any(w in ("in", "of") for w in words)
            or (len(words) >= 2 and words[-1] in DISTRICT_KEYWORDS)
        ):
            like = f"{_escape_like(core_term)}%"
            sql = """
                SELECT id, name, latitude, longitude, feature_code,
                       admin1, admin2, admin3, population
                FROM places
                WHERE feature_code = 'ADM2'
                  AND admin1 COLLATE NOCASE LIKE ? ESCAPE '\\'
                ORDER BY name
                LIMIT ?
            """
            rows.extend(con.execute(sql, (like, limit * 3)))

        # Pattern 3: Comma separated "<A>, <B>" (e.g. "Bajpatti, Sitamarhi")
        has_comma = "," in raw_query
        parts = [p.strip() for p in raw_query.split(",") if p.strip()]
        if has_comma and len(parts) >= 2:
            t1 = _normalize(parts[0])
            t2 = _normalize(parts[1])
            c_t1 = " ".join(w for w in t1.split() if w not in (DISTRICT_KEYWORDS | VILLAGE_KEYWORDS | NOISE_KEYWORDS)) or t1
            c_t2 = " ".join(w for w in t2.split() if w not in (DISTRICT_KEYWORDS | VILLAGE_KEYWORDS | NOISE_KEYWORDS)) or t2
            sql = """
                SELECT id, name, latitude, longitude, feature_code,
                       admin1, admin2, admin3, population
                FROM places
                WHERE (name COLLATE NOCASE LIKE ? ESCAPE '\\' AND (admin2 COLLATE NOCASE LIKE ? ESCAPE '\\' OR admin1 COLLATE NOCASE LIKE ? ESCAPE '\\' OR admin3 COLLATE NOCASE LIKE ? ESCAPE '\\'))
                   OR (name COLLATE NOCASE LIKE ? ESCAPE '\\' AND (admin2 COLLATE NOCASE LIKE ? ESCAPE '\\' OR admin1 COLLATE NOCASE LIKE ? ESCAPE '\\' OR admin3 COLLATE NOCASE LIKE ? ESCAPE '\\'))
                ORDER BY population DESC, name
                LIMIT ?
            """
            rows.extend(
                con.execute(
                    sql,
                    (
                        f"{_escape_like(c_t1)}%", f"%{_escape_like(c_t2)}%", f"%{_escape_like(c_t2)}%", f"%{_escape_like(c_t2)}%",
                        f"{_escape_like(c_t2)}%", f"%{_escape_like(c_t1)}%", f"%{_escape_like(c_t1)}%", f"%{_escape_like(c_t1)}%",
                        limit * 3,
                    ),
                )
            )

        # Pattern 4: Multi-word query without commas (e.g. "Bajpatti Sitamarhi", "Sitamarhi Bajpatti", "Samar Gopalpur Rohtak")
        elif len(content_words) >= 2:
            w0 = content_words[0]
            w1 = " ".join(content_words[1:])
            # Split candidate 1: first word is place name, remainder is district/state
            # Split candidate 2: last word is district/state, first N-1 words are place name
            cand_splits = [(w0, w1)]
            if len(content_words) > 2:
                cand_splits.append((" ".join(content_words[:-1]), content_words[-1]))

            for name_term, dist_term in cand_splits:
                sql = """
                    SELECT id, name, latitude, longitude, feature_code,
                           admin1, admin2, admin3, population
                    FROM places
                    WHERE (name COLLATE NOCASE LIKE ? ESCAPE '\\' AND (admin2 COLLATE NOCASE LIKE ? ESCAPE '\\' OR admin1 COLLATE NOCASE LIKE ? ESCAPE '\\' OR admin3 COLLATE NOCASE LIKE ? ESCAPE '\\'))
                       OR (name COLLATE NOCASE LIKE ? ESCAPE '\\' AND (admin2 COLLATE NOCASE LIKE ? ESCAPE '\\' OR admin1 COLLATE NOCASE LIKE ? ESCAPE '\\' OR admin3 COLLATE NOCASE LIKE ? ESCAPE '\\'))
                    ORDER BY population DESC, name
                    LIMIT ?
                """
                rows.extend(
                    con.execute(
                        sql,
                        (
                            f"{_escape_like(name_term)}%", f"%{_escape_like(dist_term)}%", f"%{_escape_like(dist_term)}%", f"%{_escape_like(dist_term)}%",
                            f"{_escape_like(dist_term)}%", f"%{_escape_like(name_term)}%", f"%{_escape_like(name_term)}%", f"%{_escape_like(name_term)}%",
                            limit * 3,
                        ),
                    )
                )

        # Pattern 5: Prefix search on name with target_type filter / boosts
        if target_type == "district":
            sql = """
                SELECT id, name, latitude, longitude, feature_code,
                       admin1, admin2, admin3, population
                FROM places
                WHERE feature_code = 'ADM2'
                  AND (name COLLATE NOCASE LIKE ? ESCAPE '\\' OR admin2 COLLATE NOCASE LIKE ? ESCAPE '\\')
                ORDER BY population DESC
                LIMIT ?
            """
            rows.extend(con.execute(sql, (f"{_escape_like(core_term)}%", f"{_escape_like(core_term)}%", limit * 3)))
        elif target_type == "village":
            sql = """
                SELECT id, name, latitude, longitude, feature_code,
                       admin1, admin2, admin3, population
                FROM places
                WHERE feature_code IN ('PPL', 'PPLL', 'PPLF', 'PPLR', 'PPLS')
                  AND name COLLATE NOCASE LIKE ? ESCAPE '\\'
                ORDER BY population DESC, name
                LIMIT ?
            """
            rows.extend(con.execute(sql, (f"{_escape_like(core_term)}%", limit * 3)))
        else:
            # General search: check name prefix
            sql = """
                SELECT id, name, latitude, longitude, feature_code,
                       admin1, admin2, admin3, population
                FROM places
                WHERE name COLLATE NOCASE LIKE ? ESCAPE '\\'
                ORDER BY population DESC, name
                LIMIT ?
            """
            rows.extend(con.execute(sql, (f"{_escape_like(core_term)}%", limit * 3)))

            # If core_term matches a district name/admin2, include the district entity
            if len(core_term) >= 3:
                sql_dist = """
                    SELECT id, name, latitude, longitude, feature_code,
                           admin1, admin2, admin3, population
                    FROM places
                    WHERE feature_code = 'ADM2'
                      AND (name COLLATE NOCASE LIKE ? ESCAPE '\\' OR admin2 COLLATE NOCASE LIKE ? ESCAPE '\\')
                    LIMIT 5
                """
                rows.extend(con.execute(sql_dist, (f"{_escape_like(core_term)}%", f"{_escape_like(core_term)}%")))

        # Pattern 6: Substring fallback ONLY when prefix search produced fewer than 2 results
        if len(rows) < 2 and len(core_term) >= 3:
            sql_sub = """
                SELECT id, name, latitude, longitude, feature_code,
                       admin1, admin2, admin3, population
                FROM places
                WHERE name COLLATE NOCASE LIKE ? ESCAPE '\\'
                ORDER BY population DESC, name
                LIMIT ?
            """
            rows.extend(con.execute(sql_sub, (f"%{_escape_like(core_term)}%", limit * 2)))

        # De-duplicate by GeoNames id
        unique: dict[int, sqlite3.Row] = {}
        for r in rows:
            rid = int(r["id"])
            if rid not in unique:
                unique[rid] = r

        q_clean = core_term.casefold()

        def sort_key(row: sqlite3.Row):
            raw_name = (row["name"] or "").casefold()
            clean_name = _clean_district_name(raw_name).casefold()
            fcode = row["feature_code"]
            pop = int(row["population"] or 0)

            # Match quality on name
            if clean_name == q_clean or raw_name == q_clean:
                match = 0
            elif clean_name.startswith(q_clean) or raw_name.startswith(q_clean):
                match = 1
            elif any(w.startswith(q_clean) for w in clean_name.split()):
                match = 2
            elif q_clean in clean_name:
                match = 3
            else:
                match = 4

            # Feature priority with explicit user intent overrides
            if target_type == "district":
                feat_priority = 0 if fcode == "ADM2" else 10
            elif target_type == "village":
                feat_priority = 0 if fcode in ("PPL", "PPLL", "PPLF", "PPLR", "PPLS") else 10
            elif target_type == "subdistrict":
                feat_priority = 0 if fcode in ("ADM3", "ADM4", "ADM5") else 10
            elif target_type == "city":
                feat_priority = 0 if fcode in ("PPLC", "PPLA", "PPLA2", "PPLA3") else 10
            else:
                feat_priority = FEATURE_PRIORITY.get(fcode, 8)

            return (match, feat_priority, -pop, len(clean_name), clean_name)

        ordered = sorted(unique.values(), key=sort_key)[:limit]
        results = []
        for row in ordered:
            population = int(row["population"] or 0)
            display_type = _display_type(row["feature_code"], population)
            name = _clean_district_name(row["name"]) if row["feature_code"] == "ADM2" else row["name"]
            admin2 = _clean_district_name(row["admin2"]) if row["admin2"] else ""
            results.append({
                "name": name,
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
                "admin1": row["admin1"] or "",
                "admin2": admin2,
                "admin3": row["admin3"] or "",
                "country": "India",
                "type": display_type,
                "type_label": (
                    FEATURE_LABELS.get(row["feature_code"], display_type)
                    if row["feature_code"] != "PPL"
                    else display_type
                ),
                "feature_code": row["feature_code"],
                "population": population,
                "source": "geonames",
            })
        return results
    except sqlite3.Error:
        return []
    finally:
        con.close()


def warm_up() -> bool:
    """Decompress/open the index early so the first keystroke is instant."""
    try:
        return _database_path() is not None
    except Exception:
        return False
