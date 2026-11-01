# Know Your Weather — Architecture

> Trilingual (English / Hindi / Bhojpuri) city + village + PIN weather site for travellers, farmers & families. Python + Streamlit, free APIs, no keys, no DB.

## 1. Goals / Non-goals

**Solves:**
1. City-only weather apps → must support villages, tehsils, districts, 6-digit PINs (e.g. `Bajpatti, Sitamarhi`, `843301`).
2. English-only jargon → full UI + advisories in Hindi + Bhojpuri (Devanagari).
3. Ad-clutter / 3-clicks → one search → answer; side-by-side compare for 2–4 places.
4. Travel indecision → packing rules (umbrella / heat / cold / wind).
5. Crop loss → soil temp/moisture + last-7-day rain + spray/harvest advisory.
6. Safety → heat / cold / storm / rain / wind alerts with beep + copy-paste text.

**Non-goals (v1):** no accounts, no DB, no push notifications, no radar maps, no payments.

## 2. Tech stack

| Layer | Choice | Why |
|---|---|---|
| UI | Streamlit ≥1.32 + streamlit-searchbox | Fastest Python web UI; searchbox gives instant city/village suggestions, free deploy |
| Data manip | pandas ≥2.0 | 7-day tables + `line_chart` / `bar_chart` in 3 lines |
| HTTP | requests ≥2.31 | Simple sync calls to free APIs |
| Geocoding | Photon (autocomplete) + OSM Nominatim + Open-Meteo (backup) | Photon understands partial words (`Sitam` → Sitamarhi); Nominatim has strong village/PIN coverage; Open-Meteo fills city gaps. All keyless |
| Weather | Open-Meteo Forecast (no key) | Free, CORS-friendly, WMO codes, `timezone=auto` |
| Animations | `ui_effects.py` pure CSS | No image/JS assets, works offline after load |

Run: `pip install -r requirements.txt && streamlit run app.py --server.port 8501`

## 3. Repo map

```
new/
├── app.py           # 275 lines. Streamlit shell: sidebar, 5 modes, forms, charts
├── geo.py           # 114 lines. find_places() + label(). Nominatim + Open-Meteo merge
├── weather.py       # 106 lines. API fetch + pure rules: travel_packing, check_alerts, farm_advisory_en
├── i18n.py          # 197 lines. STRINGS[en|hi|bho] + WEATHER_NAMES[WMO] + t(), weather_name()
├── ui_effects.py    # 286 lines. get_theme(), THEME_STYLE[8], GLOBAL_CSS, banner_html()
├── requirements.txt # streamlit, requests, pandas
├── ARCHITECTURE.md  # this file
└── .gitignore       # python/streamlit/os/ide/lock-file ignores
```

No `__pycache__/`, no secrets, no data files — everything is fetched live.

## 4. Runtime architecture

```
                 ┌─────────────┐
                 │   Browser   │  Type → pick an autocomplete suggestion
                 └──────┬──────┘
                        │ HTTP :8501
              ┌─────────▼──────────┐
              │  app.py (Streamlit)│
              │ sidebar lang + mode│── session_state (selected place)
              │ place_picker box   │
              └──┬───────────┬─────┘
                 │           │
        ┌────────▼───┐ ┌─────▼────────┐
        │  geo.py    │ │  weather.py  │
        │ Photon     │ │ Open-Meteo   │
        │ Nominatim  │ │ forecast     │
        │ Open-Meteo │ │ current+daily│
        └────────┬───┘ └─────┬────────┘
                 │           │
        ┌────────▼───────────▼─────┐
        │ i18n.py + ui_effects.py  │
        │ translate + banner/charts│
        └──────────────────────────┘
```

All calls are synchronous + cached (`@st.cache_data(ttl=600)`). No background jobs.

## 5. Data flow (single search)

1. User types `843301` / `Sitam` / `Bajpatti` in the `place_picker()` autocomplete. After 2+ characters, `cached_suggest(q)` calls `geo.suggest_places(q)` and the dropdown fills instantly.
2. `suggest_places()` uses `_photon()` (OSM, prefix-aware) and falls back to Nominatim/Open-Meteo only if Photon has no hits. Results are ranked city → town → village → hamlet → admin area; duplicate admin outlines are collapsed.
3. Clicking a suggestion returns its place dict. `st_searchbox` keeps that selection across reruns, language switches and mode changes.
4. Full/compare searches use `cached_search(q)` → `geo.find_places(q)`, which merges Photon + Nominatim + Open-Meteo:
   - `_nominatim()`: `q + ", India"`, `countrycodes=in`, `addressdetails=1`; pure 6-digit → `postalcode=` search.
   - `_open_meteo()`: `name=q.split(",")[0]`, India-only, `count=5`.
   - Dedupe by rounded coords + same name/state, then rank. Raises `not_found` if empty.
5. `cached_weather(lat, lon)` → `weather.get_current_and_daily()`:
   - `current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m`
   - `daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum`
   - `forecast_days=7, timezone=auto` → returns `(current, daily, tz)` 3-tuple.
6. Render: `banner_html(code)` → 4 metric cards → info line → `show_7day()` table + line + bar charts.

Farmer mode swaps step 5 for `get_farmer_data()` (`past_days=7`, soil fields). Compare mode loops steps 4–6 for ≤4 names.

## 6. External API contracts

### 6.1 Photon `https://photon.komoot.io/api/`
- Params: `q=query`, `limit=24`, `lang=en`; header `User-Agent: KnowYourWeather/1.0`.
- Used for the autocomplete dropdown because it matches partial words (`Sitam` → Sitamarhi) and understands PIN codes.
- Filter client-side: `properties.countrycode == "IN"`; keep `osm_key=place` and administrative boundaries; skip streets/shops/stations.
- Returns GeoJSON: `geometry.coordinates=[lon,lat]`, `properties{name, county, state, postcode, osm_value}`.
- Failures swallowed → empty list; caller falls back to Nominatim + Open-Meteo.

### 6.2 Nominatim `https://nominatim.openstreetmap.org/search`
- Params: `q="{query}, India"`, `format=jsonv2`, `addressdetails=1`, `limit=6`, `countrycodes=in`, `accept-language=en`; header `User-Agent: KnowYourWeather/1.0`.
- PIN path: `postalcode={6 digits}` instead of `q`.
- Returns: `lat/lon`, `address{village|town|city|suburb|county|state_district|state}`, `class/type`, `display_name`.
- Limits: ~1 req/s policy, no key. Failures swallowed → empty list (fallback to Open-Meteo).

### 6.3 Open-Meteo geocoding `https://geocoding-api.open-meteo.com/v1/search`
- Params: `name=first-part`, `count=5`, `language=en`, `format=json`.
- Returns: `name, latitude, longitude, admin1/admin2, country, feature_code`.

### 6.4 Open-Meteo forecast `https://api.open-meteo.com/v1/forecast`
- Current + 7-day as above; farmer variant adds `hourly=soil_temperature_6cm,soil_moisture_3_9cm,precipitation` + `current=soil_*` + `past_days=7, forecast_days=2`.
- Errors (`Timeout/Connection/HTTP/ValueError`) → `RuntimeError("no_internet")` → UI shows trilingual retry message.

## 7. Module contracts

**`geo.py`**
- `find_places(query, count=6) -> list[dict{name,latitude,longitude,admin2,admin1,country,type,source}]`, raises `RuntimeError("not_found")`.
- `suggest_places(query, count=6) -> list[dict]` — fast Photon-only autocomplete, empty list for queries under 2 chars or no hits.
- `label(place) -> str` e.g. `Bajpatti, Sitamarhi, Bihar [village]`.

**`weather.py`** (all pure except fetchers)
- `get_current_and_daily(lat, lon) -> (current: dict, daily: dict, tz: str)`
- `get_farmer_data(lat, lon) -> full JSON {current, daily, hourly}`
- `travel_packing(tmax, rain_prob, wind, wcode) -> ["umbrella"|"heat"|"cold"|"wind"|"normal"]` (thresholds: rain>60, ≥35 heat, ≤10 cold, wind≥40, storm codes 95/96/99)
- `check_alerts(current, daily) -> [(severity, msg)]` (heat≥40, cold≤5, storm now, rain≥80%, wind≥60)
- `farm_advisory_en(farmer_json) -> [tips]` (past-total >50 wet / <5 dry; next-48h >70 postpone / <20+>35 irrigate)

**`i18n.py`**
- `t(lang, key)`, `weather_name(code, lang)` with nearest-code fallback. ~55 keys × 3 langs.

**`ui_effects.py`**
- `get_theme(code) -> clear|partcloud|cloudy|fog|drizzle|rain|snow|storm`
- `banner_html(code, temp_c, cond_name, place) -> html` + `GLOBAL_CSS` injected once.

## 8. UI modes (`app.py`)

| Mode | Input | Output |
|---|---|---|
| 🔍 Single | `single_searchbox` | banner + 4 metrics + info + 7-day table/charts |
| 🎒 Travel | `travel_searchbox` | same + packing list (umbrella/heat/cold/wind/normal) + 7-day |
| 🌾 Farmer | `farmer_searchbox` | soil temp/moisture + last-7d rain table/bar + trilingual advisory |
| ⚠️ Alert | `alert_searchbox` | `check_alerts` + beep audio + copy-paste code block |
| ⚖️ Compare | `cmp_form` | table for ≤4 places + Temp vs Rain% bar chart |

Modes 1–4 use the `st_searchbox` autocomplete (type → click suggestion). Compare keeps `st.form` so **Enter = submit**. Session keys: `{prefix}_searchbox`, `cmp_q`, `cmp_done`.

## 9. UI themes (8 banners)

| Theme | WMO | Look |
|---|---|---|
| clear | 0,1 | blue-yellow gradient, glowing sun + rotating rays + sparkles |
| partcloud | 2 | small sun + 3 drifting clouds |
| cloudy | 3 | grey gradient + 4 drifting clouds |
| fog | 45,48 | sliding blurred white bands |
| drizzle | 51,53,55 | clouds + 16 light drops |
| rain | 61,63,65,80,81,82 | dark blue + 34 falling droplets |
| snow | 71,73,75,77,85,86 | 26 falling ❄ |
| storm | 95,96,99 | near-black + rain + flashing ⚡ + sky flash |

7-day table prepends the theme emoji per row. Metric cards are white rounded cards via `GLOBAL_CSS`.

## 10. State, caching, errors

- Cache: `cached_search / cached_weather / cached_farmer`, `ttl=600`, `show_spinner=False`.
- Errors: `not_found` → "Try 'Name, District'"; `no_internet` → "Check connection". Geo helpers swallow per-source errors and let merge decide.
- No secrets, no local storage, no cookies. Query text only lives in session_state.

## 11. Security / cost / privacy

- No keys, no auth, no DB → ₹0 cost, nothing to leak. `User-Agent` header identifies Nominatim traffic.
- No PII sent except the typed place name + browser IP (inherent to API calls).

## 12. Limitations

- Hourly strip, AQI, UV, sunrise/sunset intentionally **removed** (caused import mismatch); re-add as single `weather.py` change + `app.py` unpack fix.
- No offline mode, no tests, `use_container_width` deprecated warnings (cosmetic), Nominatim 1 req/s throttle not enforced client-side.

## 13. Roadmap

1. Re-add hourly-24h + AQI/UV/sun in one atomic commit (both files together).
2. GPS `?lat=&lon=` + share links.
3. `pytest` for `travel_packing / check_alerts / farm_advisory_en / get_theme`.
4. `st.map` / folium rain view, voice input, PWA install.
5. Deploy: Streamlit Community Cloud; secrets via `.streamlit/secrets.toml` (gitignored).

## 14. Python language features used (file-by-file, and why)

This project deliberately uses only a small, boring subset of Python — no classes, no async, no threads — so a student can read every file top-to-bottom. What it *does* use, it uses heavily:

### 14.1 Functions + docstrings + type hints (all files)
- Every unit of work is a plain module-level `def` with a docstring: `find_places()` / `suggest_places()` / `label()` in `geo.py`, `get_current_and_daily()` / `travel_packing()` / `check_alerts()` in `weather.py`, `t()` / `weather_name()` in `i18n.py`, `get_theme()` / `banner_html()` in `ui_effects.py`, `place_picker()` / `show_current()` / `show_7day()` in `app.py`.
- Why: functions are testable without Streamlit running (e.g. `travel_packing(38, 80, 10, 0)` can be unit-tested). Classes would add nothing — there is no persistent state to encapsulate; state lives in Streamlit's `session_state` and cache instead.
- Light type hints (`query: str, count: int = 6`, `lat: float, lon: float`, `-> str/list`) are documentation, not enforcement — they tell the reader the shape without adding pydantic-style overhead.

### 14.2 Dictionaries as the core data model (all files)
- API JSON is never converted to objects — it stays as `dict`/`list` end-to-end: `current.get("temperature_2m")`, `daily["temperature_2m_max"][0]`, `place.get("admin1","")`.
- `.get(key, default)` is used everywhere instead of `[]` where a field may be missing (humidity, wind, soil moisture), so one missing field degrades to `—` instead of crashing the page.
- `i18n.py` is literally `STRINGS = {"en": {...}, "hi": {...}, "bho": {...}}` plus `WEATHER_NAMES = {0: (en, hi, bho), ...}` — a dict-of-dicts + dict-of-tuples. Lookup `t(lang, key)` is `STRINGS.get(lang, STRINGS["en"]).get(key, ...)` — two chained `.get()` calls give language fallback and key fallback for free.
- Why dicts and not dataclasses/SQL: the upstream APIs already return JSON dicts; converting would be boilerplate with zero benefit for a 7-day display app.

### 14.3 Exception handling as control flow (`geo.py`, `weather.py`, `app.py`)
- `weather._get()` catches the precise tuple `(requests.Timeout, requests.ConnectionError, requests.HTTPError, ValueError)` and re-raises a single domain error `RuntimeError("no_internet")`. `app.py` catches only that and shows a trilingual retry message. Callers never see HTTP details.
- `geo._nominatim()` / `_open_meteo()` do the opposite: `except Exception: return []` — one dead source must not kill the other; the merge step decides. `find_places()` only raises `RuntimeError("not_found")` when *both* are empty.
- Per-item `try/except: continue` inside the Nominatim loop (`float(x["lat"])`, address parsing) skips one malformed result instead of dropping all 6.
- EAFP (`try` first, ask later) is used over `if "key" in dict` checks because API shapes vary by place type (village vs postcode have different address keys).

### 14.4 String tools: f-strings, `strip/split/join`, regex (`geo.py`, `app.py`, `ui_effects.py`)
- f-strings for all user-visible text: `f"{place['name']}"`, `f"Total rain past 7 days: **{total:.1f} mm**."` (`:.1f` formatting), `T("take_umbrella").format(p=rain_p)` for `{p}` placeholders across 3 languages.
- `query.split(",")[0].strip()` (Open-Meteo only wants the first token — `"Bajpatti, Sitamarhi"` → `"Bajpatti"`), `", ".join([x for x in [name, admin2, admin1] if x])` to skip empty admin parts, `"".join(drops)` to build banner HTML.
- `re.fullmatch(r"\d{6}", query)` is the *only* regex in the project — it detects a pure 6-digit PIN and switches Nominatim from `q=` to `postalcode=` search. Regex is used once because it is the clearest tool for "exactly 6 digits"; everything else is plain string ops.

### 14.5 Lists, slicing, generators, comprehensions (`weather.py`, `app.py`, `geo.py`)
- Slicing: `past_rain = daily["precipitation_sum"][:7]`, `names[:4]` (compare cap), `str(iso).split("T")[1][:5]`-style time trims.
- Generator inside `sum`: `sum(x or 0 for x in past_rain)` — handles `None` rain values without building a temp list.
- Comprehensions: `[weather_name(c, lang) for c in daily["weather_code"]]`, `[THEME_STYLE[get_theme(c)]["emoji"] for c in ...]`, `[x.strip() for x in q.split(",") if x.strip()]`.
- `photon + osm + om` list concatenation then a `seen: set` of `(round(lat,3), round(lon,3))` tuples for O(1) dedupe, followed by same-name/state collapsing — the merge that lets three geocoders act as one.
- Why: these keep 7-day/24-row transforms to one line each; pandas takes over only when a table/chart is needed.

### 14.6 First-class functions + decorators (`app.py`)
- `(st.error if sev == "high" else st.warning)(msg)` — functions as values, no if/else duplication.
- `@st.cache_data(ttl=600, show_spinner=False)` on `cached_search/cached_weather/cached_farmer` — memoization with time expiry. Same lat/lon or query within 10 min returns instantly with zero new HTTP calls. This one decorator is the entire "backend scaling" strategy.
- `format_func=lambda i: options[i]` in `selectbox` — a lambda adapter so the widget stores an int index but displays a label string.
- Local import (`from ui_effects import THEME_STYLE, get_theme` inside `show_7day`) keeps startup fast and avoids a top-level cycle; `import random` inside `ui_effects` helpers with fixed `random.seed(7/11/21)` gives deterministic-but-varied raindrop/cloud positions on every rerun.

### 14.7 What is deliberately NOT used (and why)
- No `class`, no ORM, no DB — no persistent entities exist.
- No `asyncio`/`threading` — two sequential HTTP calls (~1–2 s) are simpler and Streamlit caching hides the cost; concurrency would complicate error messages for beginners.
- No `argparse`/CLI — the UI *is* the interface.
- Stdlib used is minimal: `re` (PIN detect) and `random` (banner scatter). Everything else is third-party (below).

## 15. APIs and tech stack deep-dive — what each does and why it was chosen

### 15.1 Third-party Python packages (`requirements.txt` — only 3)

**`requests>=2.31` — all HTTP.**
- Used as `requests.get(url, params={...}, headers={...}, timeout=10/12)` + `r.raise_for_status()` + `r.json()`. `params=` handles URL-encoding of `"Bajpatti, Sitamarhi"` automatically; `timeout=` prevents a hung API from freezing the UI forever.
- Why not `urllib` (stdlib) or `httpx/aiohttp`: `urllib` needs manual encoding/error handling (~20 extra lines per call); async clients need an event loop Streamlit doesn't natively run per-widget. `requests` sync matches Streamlit's rerun model perfectly.

**`pandas>=2.0` — tables + charts input.**
- Used as `pd.DataFrame({...})`, `.set_index("Date")`, then `st.dataframe / st.line_chart / st.bar_chart`. Example: 7-day dict-of-lists → one DataFrame → temp line chart + rain bar chart in 3 lines.
- Why not raw lists or `plotly/matplotlib`: Streamlit's native charts accept DataFrames directly with zero figure code; pandas also gives `set_index` and column selection the charts need. No plotting lib is even installed.

**`streamlit>=1.32` — entire frontend + server.**
- Features actually used: `set_page_config`, `sidebar.selectbox/radio/caption`, `title/caption/header/write`, `st_searchbox` (typeahead search in modes 1–4), `form + text_input + form_submit_button` (Compare mode), `selectbox(format_func=)`, `columns`, `metric`, `info/success/warning/error`, `dataframe/line_chart/bar_chart`, `markdown(unsafe_allow_html=True)` (banner + beep audio), `code/divider`, `session_state`, `cache_data`, `audio-via-HTML`.
- Why Streamlit over Flask/Django/React: zero HTML/JS files, zero routes, hot-reload (`streamlit run app.py`), free one-click deploy (Community Cloud). Trade-off accepted: Streamlit reruns the whole script per interaction (hence `session_state` + cache), and custom JS (e.g. real GPS button) needs `components.html` hacks.

### 15.2 Geocoding: Photon (autocomplete) + OSM Nominatim + Open-Meteo (backup)

**Photon — `https://photon.komoot.io/api/` — why autocomplete.**
- Photon is an OSM-backed prefix search engine: `Sitam` returns Sitamarhi, `Bajpa` returns Bajpatti, and `843301` returns the PIN. Nominatim/Open-Meteo only match complete names, which made typeahead suggestions feel empty.
- We call it with `q=`, `limit=24`, `lang=en`, a `User-Agent` header, then keep `countrycode == "IN"` and settlement/admin features only (no streets/shops/stations).
- Free, keyless, no strict 1 req/s limit. We still debounce typing (500 ms) and cache every query for 10 minutes. If Photon returns nothing, `suggest_places()` falls back to Nominatim + Open-Meteo.

**Nominatim — `https://nominatim.openstreetmap.org/search` — why full-search primary.**
- Problem it solves: Google-style geocoders know cities, not `Bajpatti, Sitamarhi` or `843301`. Nominatim is built on OpenStreetMap, which has the best free village/tehsil/district/postcode coverage in India.
- How we call it (`geo._nominatim`): append `", India"`, set `countrycodes=in` (never return Nepal/Bihar-confusion results), `addressdetails=1` (get `village/town/city/suburb/county/state_district/state` separately), `accept-language=en`, and a required `User-Agent: KnowYourWeather/1.0` header (Nominatim policy blocks anonymous clients). Pure-6-digit input switches to `postalcode=` mode, which is far more accurate for PINs than free-text `q=`.
- Response handling: pick display name with fallback chain `village or town or city or suburb or county or state_district`, keep `class/type` (e.g. `place/village`, `boundary/postcode`) for the `[village]` tag in labels.
- Cost/limits: free, no key — but ~1 req/s usage policy. Accepted because `cache_data(ttl=600)` means repeat searches cost zero calls.
- Why not Google/Mapbox/Positionstack: all need paid keys and still have weaker Bihar-village data.

**Open-Meteo geocoding — `https://geocoding-api.open-meteo.com/v1/search` — why backup.**
- Fast city-level search (`name=`, `count=`, `language=en`, `format=json`), same provider as weather (one less dependency to trust). Fills gaps when Nominatim returns nothing (new spellings, transliterations).
- Merge rule: Photon first (settlement-accurate), then Nominatim, then Open-Meteo. Dedupe by rounded coords and same name/state; collapse a district/county outline when the actual town/village is present. Either source can fail alone without breaking search.

### 15.3 Weather: Open-Meteo Forecast — `https://api.open-meteo.com/v1/forecast` — why this API
- One call returns everything the UI needs: `current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m` + `daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum` + `timezone=auto, forecast_days=7`. Farmer variant adds `soil_temperature_6cm,soil_moisture_3_9cm,precipitation` with `past_days=7`.
- Why Open-Meteo over OpenWeatherMap / IMD / AccuWeather: no API key, no signup, no quota card, generous free rate, WMO standard weather codes (easy `weather_name()` mapping to 3 languages), `timezone=auto` (daily boundaries match the village, not UTC). IMD has the most local authority but no simple free JSON API for this use-case.
- WMO codes drive *everything*: banner theme (`get_theme`), condition text (`WEATHER_NAMES`), packing (`95/96/99` = storm → umbrella), alerts (storm-now, heat/cold thresholds on top of codes).

### 15.4 Presentation tech: Streamlit widgets + pandas charts + pure-CSS banner
- No React/Vue, no image assets, no icon fonts. The 8 weather themes are hand-written CSS (`linear-gradient` backgrounds, `radial-gradient` sun, `repeating-conic-gradient` rays, `@keyframes wx-fall/wx-drift/wx-snow/wx-flash`, `filter: blur()` fog) injected once via `GLOBAL_CSS` and per-result via `banner_html()`. Rationale: works offline after first load, zero extra downloads for 2G village networks, and a student can tweak one gradient without a build step.
- Charts are Streamlit-native over pandas (`line_chart` temps, `bar_chart` rain) — chosen over matplotlib/plotly to keep `requirements.txt` at 4 lines.

## 16. Appendix A — real request/response examples (trimmed, Sep 2026)

### A.1 PIN search → Nominatim (`postalcode=843301`)
Request:
```
GET https://nominatim.openstreetmap.org/search
  ?postalcode=843301&countrycodes=in&format=jsonv2&addressdetails=1&limit=1
  Header: User-Agent: KnowYourWeather/1.0 (learning-project)
```
Response (200, 1 hit — note `address` has no `village`, so `label()` falls back to `county`):
```json
{
  "lat": "26.5884755", "lon": "85.5031484",
  "name": "843301", "type": "postcode",
  "display_name": "843301, Dumra, Sitamarhi, Bihar, India",
  "address": {
    "postcode": "843301", "county": "Dumra",
    "state_district": "Sitamarhi", "state": "Bihar", "country": "India"
  }
}
```
Normalized by `geo._nominatim()` to:
```python
{"name": "Dumra", "latitude": 26.588, "longitude": 85.503,
 "admin2": "Sitamarhi", "admin1": "Bihar", "country": "India",
 "type": "place/postcode", "source": "osm"}
```

### A.2 Forecast (`26.59, 85.50` Sitamarhi, `forecast_days=2`)
Request params: `current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m`, `daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum`, `timezone=auto`.
```json
"current": {
  "time": "2026-09-13T19:30", "temperature_2m": 27.3,
  "relative_humidity_2m": 93, "apparent_temperature": 33.3,
  "weather_code": 2, "wind_speed_10m": 9.9
},
"daily": {
  "time": ["2026-09-13", "2026-09-14"],
  "weather_code": [2, 80], "temperature_2m_max": [31.8, 32.1],
  "temperature_2m_min": [25.0, 24.8],
  "precipitation_probability_max": [100, 95], "precipitation_sum": [0.0, 1.2]
}
```
`weather_code 2` → `weather_name()` = Partly cloudy / आंशिक बादल / कुछ बादल → `get_theme()` = `partcloud` → sun + drifting-clouds banner.

## 17. Appendix B — complete function reference

| Module | Function | In → Out | Pure? |
|---|---|---|---|
| geo | `_open_meteo(q, count)` | str → list[dict] (`[]` on any error) | No (HTTP) |
| geo | `_nominatim(q, count)` | str → list[dict], PIN-aware | No (HTTP) |
| geo | `find_places(q, count=6)` | str → merged list, raises `not_found` | No (HTTP ×2) |
| geo | `label(p)` | dict → `"Dumra, Sitamarhi, Bihar [postcode] (26.59, 85.50)"` | Yes |
| weather | `_get(url, params)` | → JSON, raises `no_internet` | No (HTTP) |
| weather | `get_current_and_daily(lat, lon)` | floats → `(current, daily, tz)` | No (HTTP) |
| weather | `get_farmer_data(lat, lon)` | floats → full JSON | No (HTTP) |
| weather | `travel_packing(tmax, rain, wind, wcode)` | numbers → keyword list | Yes |
| weather | `check_alerts(cur, daily)` | dicts → `[(severity, msg)]` | Yes |
| weather | `farm_advisory_en(json)` | farmer JSON → `[tips]` | Yes |
| i18n | `t(lang, key)` | → translated string w/ en-fallback | Yes |
| i18n | `weather_name(code, lang)` | WMO int → trilingual name w/ nearest-fallback | Yes |
| ui_effects | `get_theme(code)` | WMO int → 1 of 8 theme keys | Yes |
| ui_effects | `banner_html(...)` | code/temp/name/place → HTML string | Yes (seeded random) |
| app | `cached_suggest/search/weather/farmer` | cached wrappers, ttl=600 | Memoized HTTP |
| app | `place_picker(prefix)` | autocomplete → selected place dict \| None | No (UI+HTTP) |
| app | `show_current / show_7day` | dicts → rendered widgets | No (UI) |

## 18. Appendix C — state, cache & error inventory

Session keys: `{single,travel,farmer,alert}_searchbox` (selected place + dropdown state), `cmp_q`, `cmp_done`.
Cache: `cached_suggest(q)`, `cached_search(q)`, `cached_weather(lat,lon)`, `cached_farmer(lat,lon)` — all `ttl=600`, keyed on args (code changes invalidate).
Errors: `RuntimeError("not_found")` → trilingual "Try Name, District"; `RuntimeError("no_internet")` → trilingual retry. Geo per-source failures degrade to `[]`, never raise.

## 19. Appendix D — deploy runbook

```bash
pip install -r requirements.txt
python -m py_compile app.py geo.py weather.py i18n.py ui_effects.py
streamlit run app.py --server.port 8501 --server.headless true
# open http://localhost:8501 ; type 843301 + Enter
```
Streamlit Community Cloud: push this folder, set main file `app.py`, Python 3.11+, no secrets needed. Custom domain + reboot on `requirements.txt` change. Logs: `~/.streamlit/logs/` locally.

## 20. Verify

```bash
pip install -r requirements.txt
python -m py_compile app.py geo.py weather.py i18n.py ui_effects.py
python -c "from geo import find_places; print(find_places('843301')[0])"
streamlit run app.py --server.port 8501
# Enter `843301` → Dumra; `Bajpatti, Sitamarhi` → village result
```
