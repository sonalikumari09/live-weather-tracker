# Know Your Weather — Complete Beginner Guide (Start to End)

> Read this first if you are new to Python, APIs, or Streamlit. By the end you will be able to run, understand, break, fix, and deploy this project — and explain **why** every tech choice was made.

---

## 0. What you built (in one paragraph)

A website where a user types a city, village, or PIN code (like `Sitamarhi`, `Bajpatti, Sitamarhi`, or `843301`), picks a language (English / Hindi / Bhojpuri), and gets current weather + 7-day forecast + farmer/travel/alert advice. There is no database, no login, no API key. Every answer is fetched live from free public APIs when you pick a suggestion.

---

## 1. What you need before starting (prerequisites)

| Need | Why | How to check |
|---|---|---|
| Python 3.10+ | The whole app is Python; Streamlit needs 3.9+ | `python3 --version` |
| `pip` | Installs the 4 libraries | `pip --version` |
| Internet | All weather/place data comes from live APIs | Open `https://api.open-meteo.com` in browser |
| A browser | Streamlit renders as a web page | Any Chrome/Firefox |
| A terminal | To run install + launch commands | VS Code terminal is fine |

No Git, Docker, Node.js, or database needed. That is intentional — see §3.

---

## 2. Run it in 3 commands (do this first, understand later)

```bash
pip install -r requirements.txt
streamlit run app.py --server.port 8501
# open http://localhost:8501, type 843301, pick the suggestion
```

What each command does:
1. `pip install -r requirements.txt` — downloads exactly 4 libraries: `streamlit` (website), `streamlit-searchbox` (autocomplete dropdown), `requests` (talk to APIs), `pandas` (tables/charts). Nothing else.
2. `streamlit run app.py` — starts a small web server on your laptop and opens the app. `--server.port 8501` just fixes the address so it is always the same.
3. Typing + clicking a suggestion — triggers the search (explained in §5).

If it fails, jump to §10 (common errors) before changing any code.

---

## 3. The big "why" — tech stack decisions for a beginner

### 3.1 Why Python at all?
- You already know basic Python (variables, functions, dicts, loops). This project uses **only that level** — no classes, no async, no frameworks-with-magic. Every file is readable top-to-bottom.
- Weather APIs return JSON, and Python's `dict`/`list` map 1:1 to JSON. In JavaScript you would fight callbacks; in Java you would write model classes. In Python: `data["current"]["temperature_2m"]` and done.
- Alternative rejected: JavaScript/Node frontend — would need HTML + CSS + JS + build tools for the same result. Python + Streamlit does it in one language.

### 3.2 Why Streamlit (and not Flask / Django / React)?
- **Flask/Django** make you write routes (`@app.route("/weather")`), HTML templates, form handling, and deployment config. For 5 screens that is ~500 extra lines a beginner must learn first.
- **React** needs Node, npm, components, state hooks, and a separate Python backend anyway.
- **Streamlit** turns a Python script into a website line-by-line: `st_searchbox()` *is* the typeahead search box, `st.dataframe()` *is* the table. Rerun model: every interaction re-runs `app.py` from top — no routes to manage. The searchbox component adds a real dropdown with city/village suggestions as you type.
- Trade-off you accept: Streamlit is bad at custom JavaScript (real GPS button needs hacks) and pixel-perfect design. For a data-display village tool, speed of building beats beauty.

### 3.3 Why `requests` (and not `urllib` or `httpx`)?
- `urllib` is stdlib but verbose: manual URL-encoding, manual error checks, manual JSON decode (~20 lines per call).
- `httpx/aiohttp` are async — powerful, but then you must learn `async/await` + event loops, which Streamlit doesn't natively run per-widget.
- `requests.get(url, params={...}, timeout=12)` does encoding + timeout + `raise_for_status()` + `.json()` in 4 lines, synchronously — matching Streamlit's "run top to bottom and wait" model. Timeout matters: without it one dead API freezes your whole page forever.

### 3.4 Why `pandas` (and not plain lists or matplotlib)?
- The forecast API returns columns: `time=[...], temperature_2m_max=[...], ...`. That is already a table. `pd.DataFrame({...})` wraps it, `.set_index("Date")` picks the x-axis, and `st.line_chart / st.bar_chart` draw directly from it.
- Plain lists would need manual HTML tables. Matplotlib/Plotly would need figure/axis code + new dependencies. Pandas + Streamlit-native charts = 3 lines, zero figure code, and `requirements.txt` stays at 3 lines.

### 3.5 Why THREE geocoders — Photon + Nominatim + Open-Meteo?
- The core problem: Google-type search knows *cities*, not `Bajpatti, Sitamarhi` or `843301`. A normal text input also gives no feedback until you submit.
- **Photon (OpenStreetMap)** is a prefix-aware autocomplete engine: `Sitam` → Sitamarhi, `Bajpa` → Bajpatti, `843301` → the PIN. This powers the dropdown as you type. Free, no key. We keep only Indian settlements/admin areas and ignore streets/shops.
- **Nominatim (OpenStreetMap)** has deep *village/tehsil/district/postcode* data for India. We force `countrycodes=in` + append `", India"` so "Bihar" never matches another country, and use `postalcode=` mode for pure 6-digit input. It needs a `User-Agent` header (anti-abuse policy) and asks for ~1 req/s, so it is used for full searches and as a fallback — not for every keystroke.
- **Open-Meteo geocoding** is fast city-level search from the same provider as weather. Weakness: poor villages and noisy fuzzy matches.
- So we call Photon first for suggestions, then merge Photon + Nominatim + Open-Meteo for full searches, dedupe by rounded coordinates/name, and survive any one source dying (`except → []`). Paid options (Google/Mapbox) were rejected: they need billing keys and still have weaker Bihar-village coverage.

### 3.6 Why Open-Meteo forecast (and not OpenWeatherMap / IMD)?
- **No key, no signup, generous free quota.** A student can clone and run instantly; a village kiosk never pays.
- One call returns everything: current temp/humidity/feels-like/code/wind + 7-day max/min/rain% + `timezone=auto` (day boundaries match the village, not UTC) + optional soil fields for farmers.
- **WMO standard weather codes** (0=clear … 99=severe storm) drive *everything*: banner theme, trilingual condition text, packing rules (95/96/99 → umbrella), alerts. Learn one number system, reuse 5 times.
- OpenWeatherMap needs a key + card for scale; IMD is authoritative for India but has no simple free JSON API for this use-case.

### 3.7 Why NO database, NO login, NO JavaScript framework?
- There is nothing to store: places and weather are public and change every 10 minutes — caching (`@st.cache_data(ttl=600)`) beats a database.
- No login → no passwords to leak, no GDPR headache, kiosk-friendly.
- Animations are pure CSS (`ui_effects.py`) — zero image/JS downloads, works on 2G after first load. A student edits one gradient, refreshes, sees it.

---

## 4. Project tour — what each file does (read in this order)

```
new/
├── app.py            # the website: sidebar, 5 modes, forms, charts
├── geo.py            # place search: village/PIN → lat/lon
├── weather.py        # weather fetch + travel/alert/farm rules
├── i18n.py           # English/Hindi/Bhojpuri translations
├── ui_effects.py     # animated banner (sun/rain/cloud/storm)
├── requirements.txt  # the only 4 libraries
├── ARCHITECTURE.md   # technical reference
└── BEGINNER_GUIDE.md # this file
```

1. **`requirements.txt`** — `streamlit`, `streamlit-searchbox`, `requests`, `pandas`. If you add a 5th library, ask "can an existing one already do this?" first.
2. **`geo.py` → `suggest_places("Sitam")`** — Photon prefix search → `"Sitamarhi"`. `find_places("843301")` merges Photon + Nominatim + Open-Meteo, dedupes and ranks, returning `[{name, latitude, longitude, admin1, admin2, ...}]`. `label()` turns one result into `"Sitamarhi, Dumra, Bihar [town]"`.
3. **`weather.py` → `get_current_and_daily(26.59, 85.50)`** — one Open-Meteo call → `(current, daily, timezone)`. Pure rule functions (`travel_packing`, `check_alerts`, `farm_advisory_en`) contain zero HTTP — test them without internet.
4. **`i18n.py`** — `STRINGS[lang][key]` + `WEATHER_NAMES[code]`. `t("hi","search_button")` → `"मौसम देखें"`. Missing key falls back to English so the app never shows a blank.
5. **`ui_effects.py`** — `get_theme(95)` → `"storm"` → `banner_html()` returns HTML with rain divs + flashing ⚡. Injected via `st.markdown(..., unsafe_allow_html=True)`.
6. **`app.py`** — glues it all: language picker → mode picker → `place_picker()` autocomplete → cached fetch → banner + metrics + charts. Five modes reuse the same two helpers (`show_current`, `show_7day`).

---

## 5. How data flows — follow one search (`843301` → suggestion)

1. You type `843301` in `place_picker()`'s autocomplete. After 2 characters, `cached_suggest(q)` → `geo.suggest_places(q)` → Photon returns the PIN's location. The dropdown updates without a page reload.
2. You click the suggestion → `st_searchbox` returns the place dict and keeps it across reruns/language switches. No `form_submit_button` needed.
3. `cached_weather(26.588, 85.503)` → Open-Meteo forecast → `current={temp 27.3, code 2, ...}`, `daily={max [...], min [...], rain% [...], ...}`.
   - Full/compare searches use `cached_search` → `find_places`, which merges Photon, Nominatim and Open-Meteo and dedupes by coordinates + name/state.
4. Render: `banner_html(2)` → partcloud banner (sun + drifting clouds) → 4 `st.metric` cards → info line → `show_7day()` DataFrame + line + bar charts.
5. Switch language to हिन्दी → same data, `weather_name(2,"hi")` → `"आंशिक बादल"`, all labels re-translate, no new API call (cache).

Farmer mode swaps step 3 for `get_farmer_data()` (`past_days=7` + soil fields). Compare uses `find_places` + weather for up to 4 names.

---

## 6. Key Python ideas you will actually learn here

- **Functions + docstrings** instead of classes — every rule is independently testable: `travel_packing(38, 80, 10, 0)`.
- **Dicts + `.get(key, default)`** — API JSON stays dicts; `.get` prevents one missing field from crashing the page.
- **try/except as design**: `weather._get` converts 4 HTTP errors into one `RuntimeError("no_internet")`; geo helpers return `[]` so one dead source doesn't kill search.
- **Comprehensions/generators/slicing**: `sum(x or 0 for x in past_rain)`, `daily["time"][:7]`, `[weather_name(c, lang) for c in codes]`.
- **Decorators = caching**: `@st.cache_data(ttl=600)` is memoization with expiry — same query within 10 min costs zero HTTP calls. This *is* the scaling strategy.
- **f-strings**: `f"{temp}°C"`, `f"**{total:.1f} mm**"`, `T("take_umbrella").format(p=rain_p)`.

---

## 7. Try it yourself (5 exercises, easy → hard)

1. Change the heat threshold: `weather.py` `temp_max >= 35` → `>= 38`. Search a hot city, watch the packing list change.
2. Add a language string: copy one `take_umbrella` line in `i18n.py` to a 4th message. See fallback (`t()` returns English if you forget a language).
3. Add a theme color: `ui_effects.py` `THEME_STYLE["rain"]["bg"]` → your gradient. Refresh, search a rainy place.
4. Add an alert: `check_alerts()` — add fog rule (`wcode in (45,48)` → "Drive slow" warning).
5. Break the API on purpose: disconnect internet, search, read the trilingual error. Reconnect, it works — no restart needed (cache + rerun).

---

## 8. How to deploy (share with friends)

- Easiest: Streamlit Community Cloud — push this folder to GitHub, set main file `app.py`, Python 3.11. No secrets needed (no keys exist).
- Any VPS: `pip install -r requirements.txt && streamlit run app.py --server.port 8501 --server.headless true`, open `http://YOUR-IP:8501`.

---

## 9. Glossary (words beginners fear)

- **API**: another computer that answers questions over HTTP. Nominatim answers "where is X?", Open-Meteo answers "how is weather at lat/lon?".
- **Geocoding**: text → coordinates. Reverse is coordinates → text.
- **JSON**: text format for dicts/lists over the wire. `r.json()` parses it.
- **WMO code**: standard weather number (0 clear … 99 severe storm). Our translator turns it into 3 languages + 8 animations.
- **`timezone=auto`**: API returns days in *village* time, not UTC — today's max is actually today there.
- **Cache (`ttl=600`)**: remember answers for 10 minutes instead of re-asking the API every click.
- **`session_state`**: Streamlit's per-visitor memory across reruns (your typed query lives here).
- **Rerun**: every click/Enter re-executes `app.py` top-to-bottom; widgets redraw from state + cache. That is why the script has `if mode == ...` at the bottom.

---

## 10. Common errors and fixes

| Error | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: streamlit` | Skipped install | `pip install -r requirements.txt` |
| `ImportError: cannot import name X from weather` | Edited `app.py` import without matching `weather.py` (or stale `__pycache__`) | Change both files atomically, `rm -rf __pycache__`, restart Streamlit |
| Place not found | Spelling, or bare village name | Try `"Bajpatti, Sitamarhi"` or PIN `843301` |
| No internet / server error | Offline or API down | Reconnect, retry (cache serves repeats for 10 min) |
| Port 8501 in use | Old Streamlit still running | Kill old PID or use `--server.port 8502` |
| `use_container_width` warning | Streamlit deprecation, cosmetic | Ignore, or replace with `width='stretch'` on new versions |

---

## 11. Where to go next

- Read `ARCHITECTURE.md` §14–§19 for the technical reference (function table, real JSON payloads, deploy runbook).
- Then implement the roadmap one item at a time: hourly strip → AQI/UV → GPS `?lat=&lon=` → `pytest` for the three pure rule functions.
