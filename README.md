# Live Weather Tracker

A clean, modern, and privacy-friendly weather web application designed for all 763 districts and over 550,000 villages across India. Fully compatible with Cloudflare Pages and Streamlit.

## Overview

Most mainstream weather services cater only to major metropolitan cities. Live Weather Tracker provides instant weather forecasts for cities, towns, and remote rural villages across India with zero API keys required. It offers a trilingual interface in English, Hindi, and Bhojpuri.

## Features

- **All-India Place Search**: Look up any Indian village, tehsil, city, or district with live autocomplete.
- **Trilingual Interface**: Switch easily between English, Hindi, and Bhojpuri.
- **5 Focused Modes**:
  1. **Single Place**: Current temperature, feels-like, humidity, wind speed, animated condition banners, and 7-day forecast.
  2. **Travel Packer**: Smart clothing and packing tips based on temperature, rain probability, and wind.
  3. **Farmer Mode**: Soil temperature (6 cm depth), soil moisture, 7-day rainfall history, and farming advisories.
  4. **Morning Alerts**: Early alerts for extreme heat, cold waves, thunderstorms, or heavy rain.
  5. **Compare Places**: Side by side weather comparison for 2 to 4 locations.
- **Dual Deployment Ready**: Runs natively on Cloudflare Pages (with serverless edge functions) or on Streamlit.

## Deployment on Cloudflare Pages (Recommended)

This project includes a native Cloudflare Pages architecture with edge Functions (`functions/api/`) and a static frontend (`public/`).

### One-Click Cloudflare Pages Setup

1. Log in to the [Cloudflare Dashboard](https://dash.cloudflare.com/) and go to **Workers & Pages**.
2. Click **Create Application** > **Pages** > **Connect to Git**.
3. Select your repository: `sonalikumari09/live-weather-tracker`.
4. In the build settings:
   - **Framework preset**: None
   - **Build command**: (leave empty)
   - **Build output directory**: `public`
5. Click **Save and Deploy**.

Your app is now live worldwide on your free `*.pages.dev` domain with free SSL and global CDN caching.

### Optional: Cloudflare D1 Edge Database

To back autocomplete search with the full local index on Cloudflare edge:
1. Create a D1 database:
   ```bash
   npx wrangler d1 create live_weather_db
   ```
2. Bind the database in your Cloudflare Pages dashboard under **Settings > Functions > D1 database bindings** with variable name `DB`.
3. Seed the database using the export script:
   ```bash
   python scripts/export_d1.py
   npx wrangler d1 execute live_weather_db --file=d1_export/schema.sql
   npx wrangler d1 execute live_weather_db --file=d1_export/seed_districts_and_cities.sql
   ```

## Local Development

### Option A: Cloudflare Pages Local Preview
```bash
npx wrangler pages dev public --port 8788
```
Open `http://localhost:8788` in your browser.

### Option B: Python Streamlit App
```bash
pip install -r requirements.txt
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

## Project Structure

```text
├── public/                    # Cloudflare Pages frontend
│   ├── index.html             # Responsive HTML5 layout
│   ├── style.css              # Custom themes and animated weather banners
│   └── app.js                 # Client application and trilingual logic
├── functions/api/             # Cloudflare Pages serverless functions
│   ├── suggest.js             # Autocomplete API (D1 + OSM fallback)
│   ├── weather.js             # Forecast API with edge caching
│   └── farmer.js              # Soil and agricultural weather API
├── scripts/
│   └── export_d1.py           # D1 SQLite exporter and seed generator
├── wrangler.toml              # Cloudflare configuration
├── app.py                     # Streamlit application
├── places.py                  # Local Python search engine
├── geo.py                     # Geocoding helpers
├── weather.py                 # Open-Meteo Python client
├── i18n.py                    # Python translations
├── ui_effects.py              # Streamlit CSS banners
├── data/
│   └── india_places.sqlite.gz # Bundled places index
├── requirements.txt           # Python dependencies
├── LICENSE                    # MIT License
└── README.md                  # Project documentation
```

## License

This project is licensed under the MIT License. Place data is sourced from GeoNames under the CC BY 4.0 license.
