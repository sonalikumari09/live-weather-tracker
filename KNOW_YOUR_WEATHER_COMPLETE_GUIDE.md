# Know Your Weather — Complete Project Documentation & Explainer Guide

> **Document Purpose:** This document explains every single detail of the **Know Your Weather** project in simple, plain English. It is formatted cleanly so you can copy and paste it directly into a **Google Doc** for school/college submissions, team documentation, portfolios, or viva presentations.

---

## 1. Executive Summary: What is This Project?

**Know Your Weather** is a trilingual, lightweight web application built using **Python** and **Streamlit**. 

Unlike standard commercial weather apps (such as AccuWeather, Google Weather, or The Weather Channel), this project was designed specifically for **real-world Indian scenarios**:
1. It works not just for major metro cities (like Delhi or Mumbai), but for **small tehsils, rural villages, and 6-digit Indian PIN codes** (e.g., `843301` or `Bajpatti, Sitamarhi`).
2. It is completely **trilingual**: Available in **English**, **Hindi (हिन्दी)**, and **Bhojpuri (भोजपुरी)**.
3. It serves specific user personas:
   - **General Users / Families**: Instant current weather and 7-day charts without ads or clickbait.
   - **Travellers**: Automatic packing recommendations (e.g., umbrella, heavy jacket, heat protection).
   - **Farmers**: Crucial agricultural weather data (soil temperature at 6 cm, soil moisture, past 7 days of accumulated rainfall, and practical farming advisories).
   - **Public Safety**: Morning alerts with audio beeps for extreme heatwaves, cold waves, or thunderstorms.
4. **Zero Overhead Architecture**: It requires **no database**, **no user login**, **no paid API keys**, and only **three lightweight Python libraries**.

---

## 2. Real-World Problems This Project Solves

| # | The Real-World Problem | How "Know Your Weather" Solves It |
|---|---|---|
| **1** | **City-Centric Weather Apps:** Most apps only recognize registered municipalities or airport weather stations. When rural residents or farmers search their village name or local PIN code, the app returns "Location not found". | Combines OpenStreetMap Nominatim with Open-Meteo. Nominatim possesses deep crowd-sourced mapping of Indian villages, hamlets, gram panchayats, and PIN codes. |
| **2** | **Language Barrier & Technical Jargon:** Most weather services use complex English terminology (e.g., "Precipitation 82%", "Dew point 21°C") that rural users, elders, and regional farmers cannot easily interpret. | Full native interface in English, Hindi, and Bhojpuri. Jargon is translated into plain, actionable advice (e.g., "छाता + रेनकोट ले जाएं" / "दवाई/खाद रोक दीं"). |
| **3** | **Ad Clutter and Slow Multi-Click Navigation:** Checking weather on standard commercial websites requires navigating pop-up ads, cookie banners, auto-playing videos, and multiple page clicks. | A single-page, ad-free web dashboard where pressing **Enter** in a search box displays live conditions, 7-day forecasts, and temperature charts in under 2 seconds. |
| **4** | **Travel Indecision:** Travellers struggle to translate raw rain percentages or temperatures into actionable packing decisions. | A dedicated **Travel Packer** mode that checks wind, storm codes, rain probabilities, and temperatures to output an automated checklist (e.g., umbrella, windcheater, sunscreen, or warm jacket). |
| **5** | **Crop Damage & Agricultural Losses:** Farmers lose fertilizer investments or harvest crops right before heavy rainfall because they lack local soil moisture and rainfall history data. | A dedicated **Farmer Mode** displaying soil temperature at 6 cm, root-zone moisture, 7-day past rain totals, and advisories on when to spray pesticides or postpone field work. |
| **6** | **Disaster Safety & Lack of Timely Alerts:** Severe weather (heatwaves > 40°C, coldwaves < 5°C, or sudden lightning storms) often catches rural families off guard. | An **Alert Mode** that evaluates safety thresholds, sounds an audible alert tone in the browser, displays high-visibility warning banners, and generates ready-to-share SMS/WhatsApp warning text. |

---

## 3. Technology Stack: What Was Used & Why

This project follows the **KISS (Keep It Simple, Stupid)** software engineering principle. It uses only **three external Python libraries**, requiring no compilation, no JavaScript tooling, and zero database setup.

```
+-------------------------------------------------------------------+
|                        PRESENTATION LAYER                         |
|      Streamlit >= 1.32  +  Pure CSS Responsive Animations         |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                         DATA & LOGIC LAYER                        |
|       Pandas >= 2.0 (DataFrames & Visualizations)                 |
|       Requests >= 2.31 (Synchronous HTTP Client)                  |
|       Pure Python Business Rules (Travel, Alerts, Farmer)         |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                       EXTERNAL DATA SERVICES                      |
|   OpenStreetMap Nominatim API  |   Open-Meteo Weather API         |
|   (Village & PIN Geocoding)    |   (Live Forecast & Soil Metrics) |
+-------------------------------------------------------------------+
```

### Detailed Breakdown of Tech Choices

### 1. Python (Version 3.10+)
* **Why it was used:** Python is the premier language for rapid data manipulation and API integration. Its native dictionaries and lists match JSON responses 1:1, making parsing straightforward.
* **Why not JavaScript/Node or Java:** JavaScript requires setting up frontend frameworks (React/Vue), bundlers (Vite/Webpack), and separate backend servers. Java requires verbose object boilerplate (DTO classes) for simple JSON manipulation.

### 2. Streamlit (`streamlit>=1.32`)
* **What it does:** Serves both as the web server and the UI rendering engine.
* **Why it was used:**
  * Translates pure Python scripts into modern, interactive web interfaces.
  * Native interactive widgets (`st.text_input`, `st.selectbox`, `st.columns`, `st.metric`).
  * `st.form` provides native **"Press Enter to Submit"** capability without writing a line of JavaScript.
  * Built-in caching (`@st.cache_data`) makes scaling and memory caching trivial.
  * Free one-click cloud hosting via Streamlit Community Cloud.
* **Why not Flask or Django:** Flask and Django require route definitions (`@app.route`), HTML templates (Jinja2), CSS stylesheets, JavaScript event listeners, and form serialization. This would turn a 300-line project into 1,500+ lines of scaffolding.

### 3. Requests (`requests>=2.31`)
* **What it does:** Handles all outgoing HTTP calls to external APIs.
* **Why it was used:**
  * Provides synchronous HTTP calls that fit Streamlit’s execution model.
  * Handles query parameter URL-encoding automatically (`params={"q": "Bajpatti, Sitamarhi"}`).
  * Easy timeout enforcement (`timeout=12`), ensuring a slow or non-responsive API never hangs the user interface.
* **Why not standard library `urllib`:** `urllib` requires manual URL encoding, manual JSON string decoding, and multi-line exception handling.
* **Why not `httpx` or `aiohttp`:** Async libraries require an event loop (`async`/`await`), which adds needless complexity when Streamlit processes sequentially.

### 4. Pandas (`pandas>=2.0`)
* **What it does:** Structures multi-day weather arrays into tabular formats and feeds chart generators.
* **Why it was used:**
  * Open-Meteo returns daily forecasts as parallel lists (e.g., `time=[...]`, `temperature_2m_max=[...]`). Wrapping them in `pd.DataFrame({...})` takes one line.
  * Streamlit’s built-in chart components (`st.line_chart` and `st.bar_chart`) take Pandas DataFrames directly.
* **Why not Matplotlib or Plotly:** Matplotlib generates static image plots that are slow to render on mobile browsers and look dated. Plotly adds massive bundle sizes (~30 MB). Pandas + Streamlit native charts keep the dependencies lightweight.

### 5. OpenStreetMap (OSM) Nominatim API
* **Endpoint:** `https://nominatim.openstreetmap.org/search`
* **Why it was used:** It has the most detailed, crowd-sourced geographic database of Indian rural areas (villages, gram panchayats, post offices, and PIN codes).
* **Cost:** 100% Free, no API key, no credit card required.
* **Configuration:**
  * Appends `, India` and specifies `countrycodes=in` to eliminate ambiguous international results.
  * Detects 6-digit numbers (`re.fullmatch(r"\d{6}", query)`) to query via `postalcode=` rather than plain text search.
  * Includes `User-Agent: KnowYourWeather/1.0` header as required by OSM fair-use policy.

### 6. Open-Meteo Geocoding & Weather APIs
* **Endpoints:**
  * Geocoding: `https://geocoding-api.open-meteo.com/v1/search`
  * Weather Forecast: `https://api.open-meteo.com/v1/forecast`
* **Why it was used:**
  * **Zero Cost & No Key:** No sign-up, no tokens, no credit card required.
  * **Comprehensive Parameters:** Returns current weather, 7-day max/min temperatures, precipitation sums, rain probabilities, wind speeds, and agricultural metrics (soil temperature at 6 cm, soil moisture from 3–9 cm, past 7-day rain history).
  * **`timezone=auto` Parameter:** Returns daily time boundaries aligned with local Indian Standard Time (IST), rather than UTC midnight.
  * **Standard WMO Weather Codes:** Follows World Meteorological Organization standard codes (0 to 99), making icon mapping and translations reliable.
* **Why not OpenWeatherMap:** OpenWeatherMap requires account creation, API key management, credit cards for higher tiers, and does not provide free soil depth and moisture metrics.
* **Why not IMD (India Meteorological Department):** IMD provides authoritative Indian forecasts but lacks a simple, stable, publicly accessible, keyless REST JSON API.

### 7. Pure CSS Weather Animations (`ui_effects.py`)
* **Why it was used:** Instead of loading heavy video clips, animated GIFs, or external canvas libraries, the 8 weather banner themes (Sun, Clouds, Fog, Drizzle, Rain, Snow, Thunderstorm) use hand-crafted CSS (`linear-gradient`, `@keyframes`, `transform: rotate`, `opacity`).
* **Benefits:** Zero external image assets, loads instantly over slow 2G/3G mobile connections, and works offline once the page stylesheet is loaded.

### 8. Why No Database and No User Login?
* Weather data is publicly available and dynamic (it becomes stale every 10–15 minutes). Storing forecasts in SQL or MongoDB would consume storage without adding value.
* Avoiding user accounts eliminates password management, encrypted session cookies, and privacy compliance overhead (GDPR/DPDP).
* Instead, **Streamlit's in-memory TTL caching (`@st.cache_data(ttl=600)`)** acts as a temporary high-speed database.

---

## 4. Architecture & File Breakdown

The project structure is clean, modular, and separated into single-responsibility files:

```
weather/
├── app.py              # Main Streamlit web application & user interface
├── geo.py              # Geocoding engine (Nominatim + Open-Meteo)
├── weather.py          # API data fetching & business rule evaluation
├── i18n.py             # Trilingual dictionary (English, Hindi, Bhojpuri)
├── ui_effects.py       # Pure CSS weather animations and banner generation
├── requirements.txt    # Minimal dependencies (streamlit, requests, pandas)
├── ARCHITECTURE.md     # Engineering specification document
├── BEGINNER_GUIDE.md   # Step-by-step beginner guide
└── WINDOWS_SETUP.md    # Installation guide for Windows users
```

### Module Breakdown

### `app.py` (The Conductor / UI Layer)
* Initializes the page configuration (`layout="wide"`, page title, favicon).
* Injects `GLOBAL_CSS` for styled cards and banners.
* Houses the sidebar for language selection and mode navigation.
* Wraps backend calls with `@st.cache_data(ttl=600)` to prevent duplicate API hits.
* Implements the `place_picker()` helper using `st.form` (enables Enter-key search and persists queries across language changes via `st.session_state`).
* Renders the five application modes and reusable UI components (`show_current`, `show_7day`).

### `geo.py` (The Location Resolver)
* Contains two private fetchers:
  1. `_nominatim(query)`: Queries OpenStreetMap with India restrictions and 6-digit postal code logic.
  2. `_open_meteo(query)`: Queries Open-Meteo geocoding as a secondary backup.
* `find_places(query)`: Executes both searches, normalizes output into a unified dictionary structure, eliminates duplicate coordinates (rounded to 3 decimal places), prioritizes village-accurate OSM results, and returns up to 6 matches.
* `label(place)`: Formats location results into clean strings (e.g., `Dumra, Sitamarhi, Bihar [postcode] (26.59, 85.50)`).

### `weather.py` (The Domain Logic)
* Communicates directly with Open-Meteo's forecast API.
* `get_current_and_daily(lat, lon)`: Fetches current conditions plus 7-day daily forecasts.
* `get_farmer_data(lat, lon)`: Fetches soil temperature at 6 cm, root moisture (3–9 cm), past 7-day rain sum, and 2-day forward precipitation probabilities.
* Contains **pure business functions** (functions with zero HTTP calls, making them fully unit-testable):
  * `travel_packing()`: Evaluates temperature, rain probability, wind speed, and storm codes to return required items (`umbrella`, `heat`, `cold`, `wind`, `normal`).
  * `check_alerts()`: Tests current and daily maximums against safety thresholds (Heat > 40°C, Cold < 5°C, Storms, Rain > 80%, Wind > 60 km/h).
  * `farm_advisory_en()`: Translates past rain totals and forward forecasts into agricultural recommendations.

### `i18n.py` (The Trilingual Dictionary)
* Stores translations in a nested Python dictionary (`STRINGS = {"en": {...}, "hi": {...}, "bho": {...}}`).
* Stores WMO weather condition code translations across all 3 languages (`WEATHER_NAMES`).
* `t(lang, key)`: Looks up translation keys with automatic fallback to English if a key is missing in Hindi or Bhojpuri.
* `weather_name(code, lang)`: Maps WMO integer codes (0–99) to descriptive strings in the chosen language.

### `ui_effects.py` (Visual Effects & Banners)
* Maps WMO weather codes to one of 8 visual themes:
  * `clear` (0, 1): Sun with rotating rays and subtle sparkles.
  * `partcloud` (2): Sun with drifting clouds.
  * `cloudy` (3): Overcast with layered drifting clouds.
  * `fog` (45, 48): Sliding semi-transparent fog bands.
  * `drizzle` (51, 53, 55): Light drifting water drops.
  * `rain` (61, 63, 65, 80, 81, 82): Heavy falling rain droplets.
  * `snow` (71, 73, 75, 77, 85, 86): Falling snowflakes.
  * `storm` (95, 96, 99): Dark gradient sky with animated lightning flash effects.
* `banner_html()`: Returns standalone HTML/CSS with embedded styling and deterministic particle positioning using seeded pseudo-randomness.

---

## 5. How Data Flows (A Search from Start to Finish)

When a user types `843301` or `Bajpatti, Sitamarhi` and presses **Enter**, here is the exact sequence of events:

```
[ User types "843301" & presses Enter ]
                     |
                     v
  1. Streamlit Form captures submit event
     st.session_state["single_searched"] = "843301"
                     |
                     v
  2. cached_search("843301") checks memory cache (TTL: 10 mins)
     --> If cached: returns instantly
     --> If new: calls geo.find_places("843301")
                     |
                     v
  3. geo.py identifies 6-digit regex pattern:
     Calls OSM Nominatim: postalcode=843301&countrycodes=in
     Calls Open-Meteo as backup
     Merges & dedupes coordinates -> finds "Dumra, Sitamarhi, Bihar"
                     |
                     v
  4. Single match auto-selected (or dropdown displayed if multiple)
                     |
                     v
  5. cached_weather(lat=26.588, lon=85.503) called
     Calls Open-Meteo Forecast API with timezone=auto
     Returns: current conditions, 7-day daily forecast, timezone
                     |
                     v
  6. UI Rendering:
     - WMO code maps to theme (e.g., Code 2 -> "partcloud")
     - banner_html() renders animated banner with temperature & condition
     - 4 st.metric cards display Temp, Condition, Humidity, Wind
     - Pandas converts 7-day arrays into DataFrame
     - st.dataframe renders table with weather emojis
     - st.line_chart displays Max/Min temperature trends
     - st.bar_chart displays daily Rain %
```

---

## 6. The 5 Application Modes Explained

### 1. 🔍 Single Place Mode
* **Target Audience:** Everyday users, commuters, and families.
* **What it displays:**
  * Animated banner matching current weather conditions.
  * Four key metric cards: Temperature (with "Feels Like"), Condition description, Humidity percentage, and Wind speed in km/h.
  * Today's rain chance and Max/Min temperature summary.
  * 7-day forecast table containing dates, icons, temperature highs/lows, rain probabilities, and rain millimeter totals.
  * Interactive line charts showing temperature trends and bar charts showing rain likelihood.

### 2. 🎒 Travel Packer Mode
* **Target Audience:** Commuters, weekend travelers, and tourists planning a journey.
* **How the rules work:**
  * If rain probability > 60% or storm code detected: ☂️ Warning: "Take umbrella + raincoat".
  * If rain probability ≤ 60%: ☀️ Info: "No umbrella needed".
  * If maximum temperature ≥ 35°C: 🧢 Warning: "Heat alert: sunscreen, cap, 2L water".
  * If minimum temperature ≤ 10°C: 🧥 Warning: "Cold alert: heavy jacket, gloves".
  * If wind speed ≥ 40 km/h: 🧥 Warning: "Windy: secure windcheater".
  * If weather is mild: 🎒 Info: "Weather normal: light clothes + water bottle".
* All packing advice translates automatically into the selected language (English, Hindi, or Bhojpuri).

### 3. 🌾 Farmer Mode (Village Special)
* **Target Audience:** Agricultural workers, smallholders, and rural families.
* **Metrics Provided:**
  * **Soil Temperature at 6 cm Depth:** Crucial for seed germination and root health.
  * **Soil Moisture (3–9 cm depth):** Measured in $m^3/m^3$ to assess drought or waterlogging.
  * **Past 7 Days Rain History:** A complete table and bar chart showing actual rainfall received over the last week.
* **Automated Agronomic Advisory Engine:**
  * If rain > 70% in next 48h: *"Heavy rain in 48h -> postpone spray/fertilizer, delay harvesting."*
  * If rain < 20% and temp > 35°C: *"No rain + heat -> irrigate in 1–2 days, use mulch."*
  * If past 7 days rain > 50 mm: *"Soil likely wet -> avoid tractor, check drainage."*
  * If past 7 days rain < 5 mm: *"Dry week -> check 6cm soil moisture before sowing."*

### 4. ⚠️ Alert Mode
* **Target Audience:** Morning safety checks, field coordinators, school commute decisions.
* **Safety Rules Checked:**
  * **Heatwave:** Today's Max Temp ≥ 40°C.
  * **Coldwave:** Tonight's Min Temp ≤ 5°C.
  * **Severe Weather:** Thunderstorm active right now (WMO Codes 95, 96, 99).
  * **Heavy Downpour:** Rain chance today ≥ 80%.
  * **High Winds:** Sustained wind speed ≥ 60 km/h.
* **Alert Actions:**
  * If all clear: Displays a green confirmation banner ("All clear. No extreme weather.").
  * If dangerous: Triggers an **audible beep tone** through the browser via HTML5 audio, renders high-priority warning cards, and formats a copyable plain-text summary designed for SMS or WhatsApp distribution.

### 5. ⚖️ Compare Mode
* **Target Audience:** Comparing weather between home and destination, or comparing multiple farm locations.
* **Operation:**
  * Users enter 2 to 4 locations separated by commas (e.g., `Sitamarhi, Pupri, Bajpatti`).
  * Resolves each location in sequence and displays a consolidated side-by-side comparison table showing Temperatures, Feels Like, Conditions, Humidity, Wind, and Rain %.
  * Generates a comparative bar chart plotting **Temperature vs Rain Chance** for all places simultaneously.

---

## 7. Problems Encountered & How They Were Solved

During development and architectural review, several technical hurdles were resolved:

### 1. Village & PIN Code Search Failures
* **Problem:** Searching for Indian villages like `Bajpatti` or PIN codes like `843301` on global weather APIs yielded no results or returned places in other countries (e.g., matching a "Sitamarhi" street name in Nepal).
* **Solution:**
  1. Enforced `countrycodes=in` and appended `, India` to search queries.
  2. Implemented regex check `re.fullmatch(r"\d{6}", query)` to switch from general query `q=` to exact `postalcode=` matching in Nominatim.
  3. Implemented a dual-geocoder fallback: OpenStreetMap Nominatim runs as primary, Open-Meteo geocoding runs as backup, and results are merged and deduped.

### 2. Upstream Network Drops & API Failures
* **Problem:** Free public APIs occasionally experience rate limits, connection drops, or timeouts. A crashed API call crashed the entire Python script and presented an ugly traceback to the user.
* **Solution:**
  * Wrapped network calls in safe exception handlers. In `weather._get()`, `(requests.Timeout, requests.ConnectionError, requests.HTTPError, ValueError)` are caught and converted into a domain-specific `RuntimeError("no_internet")`.
  * The UI catches this single exception and displays a friendly, trilingual retry banner rather than a raw code error.
  * In `geo.py`, failures in individual geocoders return empty lists `[]` rather than throwing, allowing the alternate geocoder to succeed.

### 3. Missing Fields in API JSON (Crash Prevention)
* **Problem:** Different locations return varying JSON structures. For example, a village address might not contain a `"city"` key; a rural station might lack wind gust data. Accessing `data["address"]["city"]` caused `KeyError` crashes.
* **Solution:**
  * Eliminated direct bracket indexing on optional keys. Replaced with chained `.get()` lookups:
    `name = addr.get("village") or addr.get("town") or addr.get("city") or addr.get("county") or ...`
  * Missing numeric values default safely (e.g., `current.get("wind_speed_10m", 0)` or `sum(x or 0 for x in past_rain)`).

### 4. Streamlit Rerun Resets & Lost State
* **Problem:** Streamlit re-executes the entire script from top to bottom every time a user changes a dropdown, switches languages, or clicks a button. This initially caused the search box to clear and wiped the current weather results.
* **Solution:**
  * Encapsulated inputs within `st.form(key=...)`. Forms only submit when the button is clicked or Enter is pressed.
  * Stored confirmed queries inside `st.session_state[f"{prefix}_searched"]`.
  * When a user changes the language in the sidebar, the app reruns, reads the stored query from session state, and instantly re-renders the translated dashboard without requiring the user to retype their search.

### 5. Excessive API Calls & Rate Limits
* **Problem:** Re-fetching live weather on every widget toggle could exhaust free API usage limits and slow down the site.
* **Solution:**
  * Decorated all fetcher functions with `@st.cache_data(ttl=600, show_spinner=False)`.
  * If any user searches the same place or coordinates within 10 minutes (600 seconds), Streamlit serves the response directly from memory in 0.01 seconds without making an outbound HTTP request.

### 6. Dependency Bloat & Build Complexity
* **Problem:** Modern web weather templates often rely on heavy JavaScript packages, Node.js runtimes, CSS preprocessors, and charting engines (like Plotly or Highcharts), leading to slow startup and installation issues on low-end machines.
* **Solution:**
  * Kept external dependencies down to strictly **three packages**: `streamlit`, `requests`, and `pandas`.
  * Implemented all weather visuals as pure CSS animations directly inside `ui_effects.py`.

---

## 8. Common Setup & User Errors (Troubleshooting Guide)

| Error / Symptom | Root Cause | Exact Solution |
|---|---|---|
| `ModuleNotFoundError: No module named 'streamlit'` | Virtual environment not active or packages not installed | Run: `pip install -r requirements.txt` |
| `python is not recognized as an internal or external command` (Windows) | Python was installed without ticking "Add python.exe to PATH" | Re-run Python installer, select "Modify", and check **"Add Python to PATH"**; or run via `py` launcher |
| `Activate.ps1 cannot be loaded because running scripts is disabled` (Windows PowerShell) | Windows security policy restricts PowerShell scripts | Run PowerShell as User and execute: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`, then reactivate `.venv` |
| `Port 8501 is already in use` | A previous Streamlit server instance is still running in the background | Specify a different port: `streamlit run app.py --server.port 8502` or kill the running process |
| Hindi / Bhojpuri text appears as empty boxes `□□` | System lacks a Devanagari Unicode font | Install standard Indic fonts (such as Nirmala UI or Mangal), or run Windows Update to download language font packs |
| "Place not found" error on valid village | Village name alone is ambiguous in global database | Add the parent district name in the search box: e.g., type `Bajpatti, Sitamarhi` or use the 6-digit PIN code `843301` |

---

## 9. How to Run & Deploy the Project

### Local Execution (Linux / macOS / Windows)

```bash
# 1. Navigate to the project directory
cd weather

# 2. (Recommended) Create and activate a virtual environment
python -m venv .venv
# On Linux/macOS:
source .venv/bin/activate
# On Windows PowerShell:
# .\.venv\Scripts\Activate.ps1

# 3. Install the 3 dependencies
pip install -r requirements.txt

# 4. Verify code compilation
python -m py_compile app.py geo.py weather.py i18n.py ui_effects.py

# 5. Launch the application
streamlit run app.py --server.port 8501
```

Once running, open your web browser and navigate to:
**`http://localhost:8501`**

### Free Cloud Deployment (Streamlit Community Cloud)
1. Push this project folder to a GitHub repository.
2. Sign in to [share.streamlit.io](https://share.streamlit.io/) with your GitHub account.
3. Click **"New App"** -> Select your repository, branch, and set the main file path to `app.py`.
4. Click **"Deploy"**. The app will be live on a public URL in 2 minutes with automatic HTTPS. No environment secrets or database configurations are needed.

---

## 10. Beginner-Friendly Glossary

* **API (Application Programming Interface):** A standardized way for one computer program to ask questions and receive answers from another service over the internet.
* **Geocoding:** The process of converting human-readable location text (like "Sitamarhi" or "843301") into computer-readable coordinates (`latitude: 26.58, longitude: 85.50`).
* **JSON (JavaScript Object Notation):** A universal, human-readable text format structured with key-value pairs (which Python reads natively as dictionaries).
* **WMO Weather Code:** Standard international weather numbers defined by the World Meteorological Organization. For example: `0` = Clear sky, `2` = Partly cloudy, `61` = Slight rain, `95` = Thunderstorm.
* **TTL (Time-To-Live):** The duration for which cached data is remembered before being refreshed (in this app, 600 seconds = 10 minutes).
* **Pure Function:** A Python function that takes inputs and returns an answer without touching the internet, modifying global variables, or changing outside state (e.g., `travel_packing()` or `check_alerts()`).
