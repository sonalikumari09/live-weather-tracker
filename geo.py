"""Geocoding for entire India: city + district + village + PIN code.

Sources (all free, no API key):
- Local bundled SQLite GeoNames index: 565,000+ Indian villages, 763 districts,
  subdistricts, towns, and cities. Instant prefix suggestions with zero lag.
- Photon (photon.komoot.io): prefix-aware autocomplete backed by OSM.
- Nominatim: village/PIN accuracy, used as a fallback and for PIN codes.
- Open-Meteo geocoding: fast city-level backup.
Results are merged, de-duplicated and ranked by match quality + place size.
"""
from __future__ import annotations

import re
import unicodedata
import requests

from places import search_local

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
NOM_URL = "https://nominatim.openstreetmap.org/search"
PHOTON_URL = "https://photon.komoot.io/api/"
HEADERS = {"User-Agent": "KnowYourWeather/1.0 (learning-project)"}

# Open-Meteo uses GeoNames feature codes; map them to friendly words.
_OM_TYPES = {
    "PPLC": "city", "PPLA": "city", "PPLA2": "district", "PPLA3": "district",
    "PPLA4": "district", "PPL": "town", "PPLL": "village", "PPLX": "suburb",
    "PPLQ": "locality", "ADM1": "state", "ADM2": "district", "ADM3": "district",
    "PCLI": "country",
}

# Ranking priority: Postcode > City > District > Town > Village > Subdistrict
_TYPE_RANK = {
    "postcode": 0, "city": 1, "district": 2, "town": 3, "village": 4, "hamlet": 5,
    "suburb": 5, "locality": 5, "subdistrict": 6, "administrative": 6,
    "county": 6, "state": 7, "place": 8, "other": 9,
}


def _norm(s: str) -> str:
    """Lowercase + strip accents so 'Sītāmarhi' matches 'sitamarhi'."""
    s = unicodedata.normalize("NFKD", s or "")
    return "".join(c for c in s if not unicodedata.combining(c)).lower().strip()


def _match_rank(place: dict, query: str) -> int:
    name = _norm(place.get("name", ""))
    q = _norm(query)
    if name == q:
        return 0
    if name.startswith(q) or any(w.startswith(q) for w in name.split()):
        return 1
    return 2 if q in name else 3


_SOURCE_RANK = {"geonames": 0, "photon": 1, "osm": 2, "open-meteo": 3}


def _short_type(place: dict) -> str:
    return (place.get("type") or "").split("/")[-1]


def _is_admin(place: dict) -> bool:
    return _short_type(place) in ("administrative", "district", "subdistrict", "county", "state")


def _rank_places(places: list, query: str, count: int) -> list:
    # For autocomplete, prefer names that actually start with what was typed.
    prefix = [p for p in places if _match_rank(p, query) <= 1]
    pool = prefix or places
    pool.sort(key=lambda p: (
        _TYPE_RANK.get(_short_type(p), 7),
        _match_rank(p, query),
        -int(p.get("population") or 0),
        _norm(p.get("name", "")),
    ))
    return pool[:count]


def _merge_places(groups: list, query: str, count: int) -> list:
    """Merge source lists, drop true duplicates, keep distinct districts & settlements."""
    merged, seen = [], set()
    for places in groups:
        for p in places:
            try:
                key = (round(float(p["latitude"]), 3), round(float(p["longitude"]), 3))
            except Exception:
                continue
            if key in seen:
                continue
            seen.add(key)
            merged.append(p)

    # Sort so cities/districts appear cleanly
    merged.sort(key=lambda p: (
        _TYPE_RANK.get(_short_type(p), 7),
        _SOURCE_RANK.get(p.get("source", ""), 9),
        -int(p.get("population") or 0),
        _norm(p.get("name", "")),
    ))
    unique = []
    for p in merged:
        dup = False
        for q in unique:
            if _norm(p.get("name", "")) != _norm(q.get("name", "")):
                continue
            if _norm(p.get("admin1", "")) != _norm(q.get("admin1", "")):
                continue
            # Keep both if one is a district and the other is a settlement (city/town/village)
            if _short_type(p) != _short_type(q):
                continue
            near = (abs(float(p["latitude"]) - float(q["latitude"])) < 0.05 and
                    abs(float(p["longitude"]) - float(q["longitude"])) < 0.05)
            if near:
                dup = True
                break
        if not dup:
            unique.append(p)
    return _rank_places(unique, query, count)


def _open_meteo(query: str, count=5):
    try:
        r = requests.get(
            GEO_URL,
            params={"name": query.split(",")[0].strip() or query,
                    "count": count, "language": "en", "format": "json"},
            timeout=10,
        )
        r.raise_for_status()
        out = []
        for x in (r.json().get("results") or []):
            if x.get("country_code") not in ("IN", None, ""):
                continue
            code = x.get("feature_code", "")
            out.append({
                "name": x.get("name", ""),
                "latitude": x.get("latitude"),
                "longitude": x.get("longitude"),
                "admin2": x.get("admin2", ""),
                "admin1": x.get("admin1", ""),
                "country": x.get("country", ""),
                "country_code": x.get("country_code", ""),
                "type": _OM_TYPES.get(code, "place"),
                "type_label": _OM_TYPES.get(code, "place"),
                "source": "open-meteo",
            })
        return out
    except Exception:
        return []


def _photon(query: str, count=8):
    """Prefix-aware OSM autocomplete. Handles partial words like 'Sitam'."""
    query = query.strip()
    if len(query) < 2:
        return []
    try:
        r = requests.get(
            PHOTON_URL,
            params={"q": query, "limit": max(count * 3, 24), "lang": "en"},
            headers=HEADERS, timeout=10,
        )
        r.raise_for_status()
        features = r.json().get("features") or []
    except Exception:
        return []
    out = []
    for f in features:
        p = f.get("properties") or {}
        if p.get("countrycode") != "IN":
            continue
        key, val = p.get("osm_key", ""), p.get("osm_value", "")
        if not (key == "place" or (key == "boundary" and val == "administrative")):
            continue
        coords = (f.get("geometry") or {}).get("coordinates") or []
        if len(coords) < 2:
            continue
        name = p.get("name") or query
        typ = val or "place"
        if key == "boundary" and val == "administrative":
            typ = "district"
        out.append({
            "name": name,
            "latitude": float(coords[1]),
            "longitude": float(coords[0]),
            "admin2": p.get("district") or p.get("county") or p.get("city") or "",
            "admin1": p.get("state") or "",
            "country": "India",
            "postcode": p.get("postcode", ""),
            "type": typ,
            "type_label": typ,
            "display": ", ".join(x for x in [name, p.get("county"), p.get("state")] if x),
            "source": "photon",
        })
        if len(out) >= count * 2:
            break
    return out


def _nominatim(query: str, count=5):
    """India-only search. Handles villages, districts, tehsils, PIN codes."""
    query = query.strip()
    if not query:
        return []
    params = {"q": f"{query}, India", "format": "jsonv2",
              "addressdetails": 1, "limit": count,
              "countrycodes": "in", "accept-language": "en"}
    if re.fullmatch(r"\d{6}", query):
        params = {"postalcode": query, "countrycodes": "in",
                  "format": "jsonv2", "addressdetails": 1, "limit": count,
                  "accept-language": "en"}
    try:
        r = requests.get(NOM_URL, params=params, headers=HEADERS, timeout=12)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return []
    out = []
    for x in data:
        try:
            addr = x.get("address", {})
            name = (addr.get("village") or addr.get("town") or addr.get("city")
                    or addr.get("suburb") or addr.get("county") or addr.get("state_district")
                    or x.get("name", "").split(",")[0])
            typ = f"{x.get('class','')}/{x.get('type','')}"
            display_type = "village" if "village" in typ else ("district" if "administrative" in typ or "county" in typ else "place")
            out.append({
                "name": name or x.get("name", query),
                "latitude": float(x["lat"]),
                "longitude": float(x["lon"]),
                "admin2": addr.get("state_district") or addr.get("county") or "",
                "admin1": addr.get("state") or "",
                "country": "India",
                "type": display_type,
                "type_label": display_type,
                "display": x.get("display_name", ""),
                "source": "osm",
            })
        except Exception:
            continue
    return out


def find_places(query: str, count: int = 10):
    """India-wide search, local index first, live APIs as fallback.

    Raises RuntimeError('not_found'/'no_internet').
    """
    query = (query or "").strip()
    if not query:
        raise RuntimeError("not_found")

    # The bundled index covers states, districts, subdistricts and ~558k
    # populated places. PIN codes are not in it, so those go straight to live sources.
    if not re.fullmatch(r"\d{6}", query):
        try:
            local = search_local(query, limit=count)
        except Exception:
            local = []
        if local:
            return local[:count]

    merged = _merge_places([
        _photon(query, count=count),
        _nominatim(query, count=count),
        _open_meteo(query, count=count),
    ], query, count)
    if not merged:
        raise RuntimeError("not_found")
    return merged


def suggest_places(query: str, count: int = 10):
    """Fast prefix-aware suggestions for the autocomplete search box.

    The bundled GeoNames index answers almost every keystroke locally (no
    network round-trip). Photon/Nominatim/Open-Meteo are only used for PIN
    codes, Devanagari queries, and places newer than the local snapshot.
    """
    query = (query or "").strip()
    if len(query) < 2:
        return []

    if not re.fullmatch(r"\d{6}", query):
        try:
            local = search_local(query, limit=count)
        except Exception:
            local = []
        if local:
            return local[:count]

    photon = _photon(query, count=count)
    if photon:
        return _merge_places([photon], query, count)
    return _merge_places([
        _nominatim(query, count=count),
        _open_meteo(query, count=count),
    ], query, count)


def label(place: dict) -> str:
    """Compact, human-friendly label for the autocomplete dropdown."""
    typ = place.get("type_label") or ""
    if not typ:
        raw = place.get("type", "")
        typ = raw.split("/")[-1] if "/" in raw else raw

    name = place.get("name", "?")
    if typ == "district":
        name = re.sub(r"^(District|Zila)\s+", "", name, flags=re.IGNORECASE)
        name = re.sub(r"\s+(District|district|Zila|zila|Division|division)$", "", name).strip()

    admin3 = place.get("admin3", "")
    admin2 = place.get("admin2", "")
    if admin2:
        admin2 = re.sub(r"^(District|Zila)\s+", "", admin2, flags=re.IGNORECASE)
        admin2 = re.sub(r"\s+(District|district|Zila|zila|Division|division)$", "", admin2).strip()
    admin1 = place.get("admin1", "")

    parts = []
    for x in [name, admin3, admin2, admin1]:
        if x and all(_norm(x) != _norm(p) for p in parts):
            parts.append(x)
    extra = f" [{typ}]" if typ and typ != "place" else ""
    return ", ".join(parts) + extra
