# Know Your Weather — Complete Tech Stack & Architectural Justification

> **Google Doc Ready:** You can copy this entire document and paste it directly into a **Google Doc** (`Ctrl + A` → `Ctrl + C` → `Ctrl + V`). It is pre-formatted with clean headings, comparison matrices, and clear explanations written in simple, accessible language suitable for academic evaluation, project reports, and technical interviews.

---

## 1. Tech Stack Overview Matrix

Before diving into each technology individually, here is the complete summary of every tool, library, and service used in this project:

| Technology / Component | Layer | What It Does In This Project | Why Chosen Over Alternatives |
|---|---|---|---|
| **Python 3.10+ / 3.11** | Core Language | Runs all logic, parsing, and rule engines | Clean syntax, native JSON dicts, zero boilerplate |
| **Streamlit (≥1.32)** | Frontend & Web Server | Turns Python scripts into an interactive web UI | No HTML/JS/CSS build step needed; instant reactive reruns |
| **streamlit-searchbox (≥0.1.24)** | Autocomplete UI | Renders the searchable city/village dropdown | Prebuilt React component; 2 lines to wire to a Python search function |
| **Requests (≥2.31)** | Network / HTTP Client | Makes calls to geocoding & forecast APIs | Synchronous, automatic URL encoding, robust timeout control |
| **Pandas (≥2.0)** | Data Transformation & Charts | Structures 7-day weather arrays into tabular data | Prepares data for native Streamlit line/bar charts in 3 lines without plotting boilerplate |
| **Photon API (OSM)** | Autocomplete Geocoding | Prefix-matches partial words (`Sitam` → Sitamarhi) and PIN codes | Purpose-built for typeahead; free and keyless; great Indian village coverage |
| **OSM Nominatim API** | Full-Search Geocoding | Converts Indian villages, tehsils & PIN codes to lat/lon | Best free village & PIN coverage in India; ₹0 cost; no API key needed |
| **Open-Meteo Geocoding API** | Backup Geocoding | Fast fallback geocoding for city names | Redundancy; prevents search downtime if Photon/Nominatim throttle |
| **Open-Meteo Forecast API** | Weather & Soil Engine | Provides current, 7-day, and agricultural soil data | Free, no API key, WMO standard codes, local timezone matching, free soil temp/moisture |
| **Pure CSS Keyframe Banners** | Visual Effects | Renders 8 animated weather banners | Zero external image/video downloads; runs on 2G; works offline after initial page load |
| **Streamlit In-Memory Cache** | Performance & Throttling | Caches API responses for 10 minutes (`ttl=600`) | Eliminates duplicate HTTP requests; acts as a free high-speed database |
| **Custom Trilingual Dictionary** | Localization (i18n) | Translates UI to English, Hindi, and Bhojpuri | Lightweight Python dictionaries; instant switching; safe English fallback |
| **Stateless Architecture** | System Design | Zero database, zero user authentication | ₹0 operating cost, zero password/security liabilities, kiosk-ready |

---

## 2. Deep Dive: Programming Language — Python 3.10+

### What It Is
Python is a high-level, interpreted programming language known for readability, simplicity, and an extensive open-source library ecosystem.

### Where It Is Used in the Codebase
Every single backend and frontend file in this project is written in pure Python:
- `app.py`: Web dashboard and widget control
- `geo.py`: Address querying and coordinate calculation
- `weather.py`: Forecast retrieval and business rules
- `i18n.py`: Multi-language dictionary
- `ui_effects.py`: Dynamic CSS generator

### Why We Used It
1. **1:1 Mapping with JSON:** Weather APIs return data formatted in JSON (JavaScript Object Notation). In Python, JSON converts directly into native `dict` (dictionaries) and `list` structures. We access data with simple syntax like `data["current"]["temperature_2m"]`.
2. **Readability & Maintainability:** The project deliberately avoids complex Object-Oriented Programming (classes, inheritance, polymorphism) and asynchronous event loops (`async`/`await`). Every file consists of simple functions with docstrings that can be read top-to-bottom like a book.
3. **Rich Data Science & Web Ecosystem:** Python allows us to seamlessly combine web rendering (`streamlit`), networking (`requests`), and data analysis (`pandas`) within a single unified runtime.

### Alternatives Considered & Why Rejected
* **JavaScript / Node.js:** Building this in JavaScript would require a separate frontend framework (React, Vue, or Next.js), a backend server (Express), a package manager (npm), build bundlers (Vite/Webpack), and asynchronous callback management.
* **Java:** Requires verbose Model/DTO classes for every single API response field, compilation steps, and substantial memory overhead.
* **Go / C++:** Excellent raw execution speed, but development speed is much slower with unnecessary memory management overhead for a data dashboard.

---

## 3. Deep Dive: Web Framework — Streamlit (`streamlit>=1.32`)

### What It Is
Streamlit is an open-source Python framework designed specifically to build and deploy data applications and dashboards quickly, without writing frontend HTML, CSS, or JavaScript.

### Where It Is Used in the Codebase
Located entirely in `app.py`:
- `st.set_page_config()`: Configures the page title, favicon, and wide layout.
- `st.sidebar`: Houses the language picker (`selectbox`) and mode navigator (`radio`).
- `st_searchbox()`: Renders the typeahead search box in modes 1–4. Its Python callback returns matching `(label, place)` pairs while the user types.
- `st.form()` & `st.form_submit_button()`: Used only by Compare mode, which accepts a comma-separated list and submits on **Enter**.
- `st.metric()`: Renders KPI summary cards (Temperature, Feels Like, Humidity, Wind).
- `st.dataframe()`, `st.line_chart()`, `st.bar_chart()`: Renders tabular forecasts and visual trends.
- `st.session_state`: Preserves the selected place across page interactions and language switches.

### Why We Used It
1. **Elimination of Frontend Scaffolding:** Traditional web development requires three separate layers: HTML for structure, CSS for layout, and JavaScript for user events. In Streamlit, `st_searchbox()` automatically generates a responsive, mobile-ready autocomplete input.
2. **Reactive Execution Model:** Whenever a user interacts with a widget (e.g., changes language from English to Hindi), Streamlit re-runs the script from top to bottom. The searchbox keeps its selected place in component state, so the dashboard re-translates without losing the location.
3. **Debounced Typeahead:** `streamlit-searchbox` waits 500 ms after typing before calling our Python search function, then reruns only that search step. This gives live suggestions without hammering the geocoding APIs on every keystroke.
4. **Built-in Interactive Visualizations:** It connects natively to Pandas DataFrames, drawing interactive charts with zoom and hover tooltips using a single line of code (`st.line_chart(...)`).
5. **Free One-Click Cloud Deployment:** Streamlit applications can be deployed for free on Streamlit Community Cloud directly from GitHub with zero server configuration.

### Alternatives Considered & Why Rejected
* **Flask / Django:** Both frameworks require writing routing logic (`@app.route`), HTML templates (Jinja2), CSS styles, form submission handlers, and CORS headers. A simple 5-screen interface would have expanded from 275 lines to over 1,500 lines of boilerplate.
* **FastAPI + React:** Excellent for enterprise microservices, but requires maintaining two separate codebases, two build pipelines, and complex REST/state synchronization.

---

## 4. Deep Dive: HTTP Client — Requests (`requests>=2.31`)

### What It Is
`requests` is the standard HTTP library for Python, designed to send HTTP/1.1 requests effortlessly without manual configuration.

### Where It Is Used in the Codebase
- In `weather.py` (`_get()`): Sends GET requests to Open-Meteo's forecast and soil endpoints.
- In `geo.py` (`_nominatim()` and `_open_meteo()`): Queries location endpoints with search terms and coordinate limits.

### Why We Used It
1. **Automatic Query Parameter Encoding:** Indian place names often contain spaces, commas, and special characters (e.g., `"Bajpatti, Sitamarhi"`). Using `requests.get(url, params={"q": "Bajpatti, Sitamarhi"})` automatically encodes the string into standard URL syntax (`Bajpatti%2C%20Sitamarhi`) without manual string manipulation.
2. **Strict Timeout Enforcement (`timeout=12`):** When querying public APIs, network latency or server load can cause requests to hang indefinitely. Setting a strict timeout ensures that if an upstream API does not reply within 12 seconds, Python raises a `requests.Timeout` exception, preventing the web page from freezing.
3. **Synchronous Execution Matches Streamlit:** Streamlit scripts run sequentially from top to bottom. `requests` blocks execution until the data arrives, ensuring that data is fully loaded before the next UI element renders.
4. **Clean Error Handling:** Calling `r.raise_for_status()` immediately throws an exception if the remote server returns an HTTP error (such as 404 Not Found, 429 Too Many Requests, or 500 Server Error).

### Alternatives Considered & Why Rejected
* **Python Standard Library `urllib.request`:** Built into Python, but requires manual byte-decoding, manual query string formatting, and lacks intuitive response handling (~20 extra lines of code per API call).
* **`httpx` / `aiohttp`:** Asynchronous HTTP libraries designed for high-concurrency event loops. Because Streamlit operates on sequential script reruns, async functions require event loop managers (`asyncio.run()`), adding unnecessary complexity.

---

## 5. Deep Dive: Data Structuring & Charts — Pandas (`pandas>=2.0`)

### What It Is
Pandas is Python's premier data manipulation library, built around fast 2-dimensional tabular structures called **DataFrames**.

### Where It Is Used in the Codebase
- In `app.py` (`show_7day()`): Combines parallel forecast arrays (Date, Weather Icon, Max Temp, Min Temp, Rain %, Rain mm, and Condition) into a structured 7-day table.
- In `app.py` (`Farmer Mode`): Structures past 7-day rainfall history into a table and bar chart.
- In `app.py` (`Compare Mode`): Assembles side-by-side weather metrics for up to 4 locations.

### Why We Used It
1. **Parallel Array Harmonization:** Weather APIs return forecast data as multiple separate arrays:
   ```python
   time = ["2026-11-01", "2026-11-02", ...]
   max_temp = [31.5, 30.2, ...]
   rain_prob = [10, 85, ...]
   ```
   Pandas combines these separate lists into a single structured table in one step:
   ```python
   df = pd.DataFrame({"Date": time, "Max°C": max_temp, "Rain%": rain_prob})
   ```
2. **Direct Feeding into Streamlit Visualizations:** Streamlit's charting components (`st.line_chart` and `st.bar_chart`) are designed to take Pandas DataFrames directly. By calling `df.set_index("Date")`, the Date column automatically becomes the x-axis, while temperatures and rainfall percentages form the y-axis lines and bars.
3. **Missing Value Sanitization:** If an API returns missing or null numbers, Pandas handles them gracefully rather than crashing the rendering pipeline.

### Alternatives Considered & Why Rejected
* **Raw Python Dictionaries & HTML Tables:** Creating HTML tables manually using string formatting requires extensive boilerplate and cannot be rendered directly into interactive graphs.
* **Matplotlib / Seaborn:** Generates static `.png` images. These are slow to produce, look pixelated on high-DPI smartphone displays, and do not support interactive hover tooltips.
* **Plotly:** A powerful graphing library, but its client bundle exceeds 30 MB, which slows down initial page loading on slower rural connections.

---

## 6. Deep Dive: Location Resolution — Photon + OpenStreetMap Nominatim

### 6.1 Autocomplete: Photon (`photon.komoot.io`)
Photon is an OSM-backed prefix search engine built for autocomplete. It converts partial input such as `Sitam` → `Sitamarhi`, `Bajpa` → `Bajpatti`, and `843301` → the PIN location. We call it in `geo.py` (`_photon()`) with a `User-Agent` header, keep only `countrycode=IN` settlements/administrative areas/postcodes, and drop streets, shops and stations. This powers `suggest_places()` for the dropdown. If Photon returns nothing, the app falls back to Nominatim + Open-Meteo.

### 6.2 Full search: Nominatim
Nominatim is an open-source search engine that indexes OpenStreetMap (OSM) geographic data, converting search text into latitude and longitude coordinates. It is used for full/compare searches and as the autocomplete fallback.

### Where It Is Used in the Codebase
In `geo.py` (`_nominatim()`):
- Queries: `https://nominatim.openstreetmap.org/search`
- Target: Indian villages, tehsils, post offices, gram panchayats, and 6-digit postal codes.

### Why We Used It
1. **Unrivaled Indian Rural Coverage:** Commercial geocoders typically only index municipalities and major cities. OpenStreetMap is crowd-sourced and contains comprehensive geographic boundaries for remote Indian villages, hamlets, and rural landmarks.
2. **Exact 6-Digit PIN Code Detection:** When a user types a 6-digit postal code (e.g., `843301`), our code detects it via regex (`re.fullmatch(r"\d{6}", query)`) and switches the query parameter from free text `q=` to explicit `postalcode=`. This prevents confusing an Indian postal code with street numbers abroad.
3. **Country-Specific Filtering:** We enforce `countrycodes=in` and append `, India` to search terms. This prevents the search engine from returning similarly named places located in other countries.
4. **Detailed Address Breakdown (`addressdetails=1`):** Nominatim returns parsed address components (`village`, `town`, `city`, `suburb`, `county`, `state_district`, `state`). This allows our app to extract the exact settlement type to display clear labels like `Dumra, Sitamarhi, Bihar [postcode]`.
5. **₹0 Cost & No API Key:** Anyone can query Nominatim without signing contracts, creating developer accounts, or entering credit card details.

### Crucial Requirement Followed
* **Custom User-Agent Header:** Nominatim's fair-use policy blocks anonymous automated requests. We provide an explicit header: `{"User-Agent": "KnowYourWeather/1.0 (learning-project)"}` to guarantee reliable access.

### Alternatives Considered & Why Rejected
* **Google Maps Geocoding API:** Requires billing activation, credit card attachment, and charges $5.00 per 1,000 requests after free limits. It also frequently fails on unmapped rural hamlets.
* **Mapbox / Positionstack:** Both require personal API access tokens and have inferior indexing of Indian village boundaries.

---

## 7. Deep Dive: Backup Geocoding — Open-Meteo Geocoding API

### What It Is
Open-Meteo Geocoding is a fast, lightweight search API built specifically to convert city and district names into geographic coordinates.

### Where It Is Used in the Codebase
In `geo.py` (`_open_meteo()`):
- Queries: `https://geocoding-api.open-meteo.com/v1/search`
- Acts as an automatic fallback alongside Nominatim.

### Why We Used It
1. **Redundancy & High Availability:** Public services can occasionally experience brief rate limits or transient network drops. If Photon or Nominatim fails or throttles, Open-Meteo Geocoding automatically provides search results for towns and cities.
2. **Intelligent Result Merging (`find_places` in `geo.py`):** The application runs all three geocoders, dedupes by coordinates rounded to 3 decimal places (`round(lat, 3), round(lon, 3)`), collapses same-name admin outlines, and ranks city → town → village → hamlet → district. Partial queries use Photon only, so typing does not spend Nominatim's ~1 req/s budget.
3. **Shared Provider Efficiency:** Because Open-Meteo provides both geocoding and weather forecasts, it reduces external vendor dependencies.

---

## 8. Deep Dive: Weather & Agricultural Engine — Open-Meteo Forecast API

### What It Is
Open-Meteo is an open-source weather API that compiles global meteorological data from national weather services (including NOAA, DWD, ECMWF, and JMA).

### Where It Is Used in the Codebase
In `weather.py`:
- `get_current_and_daily()`: Fetches current temperature, humidity, apparent temperature ("feels like"), wind speed, weather condition codes, and 7-day daily forecasts.
- `get_farmer_data()`: Fetches agricultural indicators including soil temperature at 6 cm, root-zone soil moisture (3–9 cm depth), past 7-day rainfall history, and 2-day future rain probabilities.

### Why We Used It
1. **Zero Authentication & Completely Free:** No API keys, no developer tokens, and generous free usage tiers (up to 10,000 calls per day), making it ideal for open, accessible community software.
2. **Local Timezone Alignment (`timezone=auto`):** Standard meteorological APIs return daily forecast arrays bounded by UTC midnight (00:00 UTC = 05:30 AM IST). Specifying `timezone=auto` ensures that "Today's Maximum Temperature" aligns with actual daylight hours in the searched Indian village.
3. **Agricultural Soil Data:** Unlike standard consumer APIs that only report air temperature and clouds, Open-Meteo provides:
   - `soil_temperature_6cm`: Informs farmers if the ground is warm enough for seed germination.
   - `soil_moisture_3_9cm`: Informs farmers if the root zone has adequate moisture or requires irrigation.
   - `past_days=7`: Returns verified rainfall totals from the preceding week, helping farmers evaluate soil waterlogging before operating heavy equipment like tractors.
4. **Standardized WMO Weather Codes:** Returns condition codes standardized by the World Meteorological Organization (e.g., Code `0` = Clear, `61` = Slight Rain, `95` = Thunderstorm). This single standardized integer drives three separate parts of our app:
   - Visual animation banner (`ui_effects.py`)
   - Trilingual text translations (`i18n.py`)
   - Automated travel packing decisions (`weather.py`)

### Alternatives Considered & Why Rejected
* **OpenWeatherMap:** Requires registration, API key generation, credit card verification for higher tiers, and places severe limits on historical rainfall and soil data on its free tier.
* **IMD (India Meteorological Department):** While IMD is the official meteorological authority in India, it lacks an open, stable, well-documented REST JSON API suitable for integration into dynamic web applications.

---

## 9. Deep Dive: Visual Effects — Pure CSS Keyframe Banners (`ui_effects.py`)

### What It Is
A custom visual presentation module that generates dynamic animated banners for 8 weather states using hand-crafted CSS3 gradients and keyframe animations.

### Where It Is Used in the Codebase
- In `ui_effects.py`: Generates the HTML and CSS strings.
- In `app.py`: Injected at the top of the dashboard via `st.markdown(banner_html(...), unsafe_allow_html=True)`.

### Why We Used It
1. **Zero External Asset Overhead:** Traditional web applications display weather conditions using animated GIF files, MP4 background videos, or external icon sets (like FontAwesome or WeatherIcons). These assets add hundreds of kilobytes of network transfer. Our pure CSS solution requires **zero image downloads**.
2. **Optimized for 2G / 3G Rural Connectivity:** Because the animations consist entirely of text instructions rendered by the client's browser engine, the page loads instantly even on weak rural mobile connections.
3. **Deterministic Pseudo-Random Particles:** Raindrops, snowflakes, and cloud drifting animations are positioned across the banner using Python's `random` module seeded with fixed integers (`random.seed(7)`). This creates realistic visual variety while ensuring animations remain visually consistent across page refreshes.

### The 8 Dynamic Themes

| Theme Key | WMO Condition Codes | Visual Elements Rendered |
|---|---|---|
| `clear` | 0, 1 (Sunny, Clear) | Radial glowing sun, rotating solar rays, floating sparkle particles |
| `partcloud` | 2 (Partly Cloudy) | Subtle glowing sun with layered drifting clouds |
| `cloudy` | 3 (Overcast) | Multi-layered grey clouds drifting across a neutral sky |
| `fog` | 45, 48 (Fog, Depositing Rime) | Sliding semi-transparent white bands with CSS blur filters |
| `drizzle` | 51, 53, 55 (Light Drizzle) | Low-opacity clouds with 16 light vertical water drops |
| `rain` | 61, 63, 65, 80, 81, 82 (Showers, Heavy Rain) | Dark storm sky with 34 falling rain droplets and ground splash effects |
| `snow` | 71, 73, 75, 77, 85, 86 (Snow fall) | Slate blue sky with 26 gently rotating and falling snowflakes |
| `storm` | 95, 96, 99 (Thunderstorm) | Dark violet sky, driving rain, and random opacity flashes simulating lightning |

---

## 10. Deep Dive: Performance Architecture — In-Memory TTL Caching

### What It Is
A memory-based data caching system implemented via Streamlit's `@st.cache_data` decorator with a **Time-To-Live (TTL)** set to 600 seconds (10 minutes).

### Where It Is Used in the Codebase
In `app.py`:
- `@st.cache_data(ttl=600, show_spinner=False) def cached_search(q)`
- `@st.cache_data(ttl=600, show_spinner=False) def cached_weather(lat, lon)`
- `@st.cache_data(ttl=600, show_spinner=False) def cached_farmer(lat, lon)`

### Why We Used It
1. **Elimination of Redundant HTTP Traffic:** Weather conditions do not change from second to second. If a user searches `843301`, switches the language to Hindi, toggles between modes, and returns to the search, the app retrieves the data from RAM in less than 0.001 seconds without re-querying Open-Meteo.
2. **Upstream Rate-Limit Protection:** Suggestions are debounced 500 ms and go to Photon, not Nominatim. Nominatim's fair-use guidelines request clients to limit queries to approximately 1 request per second, so it is reserved for full/compare searches and fallbacks. Memoizing every query for 10 minutes means popular village queries are served entirely from cache.
3. **Zero Configuration:** Unlike Redis or Memcached, which require running separate server daemons and configuring port bindings, Streamlit’s cache runs directly inside Python’s application memory space.

---

## 11. Deep Dive: Localization — Custom Trilingual Engine (`i18n.py`)

### What It Is
A lightweight internationalization system supporting **English**, **Hindi (हिन्दी)**, and **Bhojpuri (भोजपुरी)** written in Devanagari script.

### Where It Is Used in the Codebase
- In `i18n.py`: Defines the `STRINGS` translation dictionary and `WEATHER_NAMES` table.
- In `app.py`: Called via the helper `T(key)` and `weather_name(code, lang)`.

### Why We Used It
1. **Regional Inclusion:** Millions of rural residents and agricultural workers in Bihar and Uttar Pradesh speak Bhojpuri. Providing weather data, soil alerts, and packing tips in their native language bridges the digital divide.
2. **Chained Fallback Architecture:**
   ```python
   def t(lang: str, key: str) -> str:
       return STRINGS.get(lang, STRINGS["en"]).get(key, STRINGS["en"].get(key, key))
   ```
   If a newly added feature or advisory is translated into Hindi but not yet into Bhojpuri, the function gracefully falls back to English rather than throwing an exception or rendering a blank label.
3. **Zero Dependencies:** Rather than importing heavy internationalization libraries like `gettext` or `Babel` (which require compiling `.po` and `.mo` binary translation files), our system uses native Python dictionaries that can be edited in any text editor.

---

## 12. Architectural Philosophy: Why No Database and No User Login?

A common question in software evaluations is: *"Why doesn't this project have a SQL database or a user login system?"* This was a deliberate architectural choice based on three engineering principles:

1. **Ephemerality of Weather Data:** Weather forecasts become obsolete within 15–30 minutes. Storing forecasts in MySQL or PostgreSQL would consume disk storage and require complex data cleanup jobs without providing any real benefit.
2. **Zero Maintenance & Privacy Protection:** Adding user accounts requires storing passwords (requiring bcrypt hashing), handling email verification, managing JWT tokens or session cookies, and complying with data privacy laws (like the Digital Personal Data Protection Act). By remaining stateless, the app collects zero personal user data.
3. **Public Kiosk & Low-End Device Readiness:** The application is designed to be opened on village common service center (CSC) computers, shared family tablets, or mobile phones without requiring anyone to remember passwords or log in.

---

## 13. Summary: How All Pieces Connect

```
+-----------------------------------------------------------------------------------+
| 1. USER INTERFACE LAYER (app.py)                                                  |
|    - User types "843301" into the autocomplete and selects "भोजपुरी" in sidebar  |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| 2. CACHING & PERFORMANCE LAYER (Streamlit @st.cache_data)                         |
|    - Checks RAM: Has "843301" been queried in the last 10 minutes?               |
|    - If YES: Return cached coordinates instantly (0 ms)                           |
|    - If NO: Pass query to Geocoding Engine                                        |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| 3. GEOCODING ENGINE (geo.py + requests)                                           |
|    - Photon returns prefix matches while typing ("Sitam" -> Sitamarhi)            |
|    - Full search merges Photon + Nominatim (PIN -> postalcode=843301) + Open-Meteo|
|    - Dedupes/ranks -> Resolves to: Sitamarhi, Bihar (26.59, 85.50)                |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| 4. METEOROLOGICAL ENGINE (weather.py + requests)                                  |
|    - Queries Open-Meteo Forecast API with coordinates (26.58, 85.50)              |
|    - Returns: current conditions, 7-day forecast, soil moisture, past rain history|
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| 5. BUSINESS RULES & LOCALIZATION LAYER (weather.py + i18n.py)                     |
|    - travel_packing(): checks rain % & wind -> determines gear                   |
|    - check_alerts(): tests for heatwave / coldwave / thunderstorm                 |
|    - farm_advisory_en(): evaluates soil moisture and advises spray timing         |
|    - i18n.py: maps WMO code to Bhojpuri description ("कुछ बादल")                  |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| 6. PRESENTATION & VISUALIZATION LAYER (ui_effects.py + pandas + Streamlit)        |
|    - ui_effects.py generates pure CSS animated banner                             |
|    - pandas structures 7-day forecast array into DataFrame                        |
|    - Streamlit renders KPI metric cards, data tables, line charts, and bar charts |
+-----------------------------------------------------------------------------------+
```
