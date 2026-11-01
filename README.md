# Live Weather Tracker

A clean and lightweight weather web application built with Python and Streamlit. It offers instant weather forecasts for cities, districts, and villages across India without requiring any API keys.

## Overview

Most mainstream weather apps cater only to major metropolitan cities. Live Weather Tracker includes an offline database covering all 763 Indian districts and over 550,000 villages, ensuring that people in rural areas can easily look up their local weather. The application also supports three languages: English, Hindi, and Bhojpuri.

## Features

- **All-India Place Search**: Search any Indian village, tehsil, or district with autocomplete suggestions. You can type village names, district names (such as "Sitamarhi district"), or combinations like "Bajpatti Sitamarhi" and "Sitamarhi Bajpatti".
- **Trilingual Interface**: Switch easily between English, Hindi, and Bhojpuri.
- **5 Focused Modes**:
  1. **Single Place**: Current weather, feels-like temperature, humidity, wind speed, and a 7-day forecast.
  2. **Travel Packer**: Packing tips based on temperature, rain probability, and wind.
  3. **Farmer Mode**: Soil temperature (6 cm depth), soil moisture, 7-day rain history, and farming advisories.
  4. **Morning Alerts**: Alerts for extreme heat, cold waves, thunderstorms, or heavy rain.
  5. **Compare Places**: Side by side weather comparison for 2 to 4 locations.
- **Fast and Privacy-Friendly**: Local SQLite index ensures sub-millisecond search without tracking or third-party ads.

## Tech Stack

- **Framework**: Streamlit
- **Language**: Python 3.9+
- **Weather API**: Open-Meteo (free, no API key needed)
- **Place Search**: Bundled GeoNames India SQLite database with OSM Photon fallback
- **Dependencies**: pandas, requests, streamlit-searchbox

## Installation and Setup

### 1. Clone the repository
```bash
git clone https://github.com/sonalikumari09/live-weather-tracker.git
cd live-weather-tracker
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the app
```bash
streamlit run app.py
```

Then visit `http://localhost:8501` in your web browser.

## Project Structure

```text
├── app.py                     # Main application and page layout
├── places.py                  # Local search engine for districts and villages
├── geo.py                     # Geocoding and autocomplete helpers
├── weather.py                 # Weather data fetching and packing logic
├── i18n.py                    # Translations for English, Hindi, and Bhojpuri
├── ui_effects.py              # Custom CSS and animated banners
├── build_india_places.py      # Script to rebuild the places SQLite database
├── data/
│   └── india_places.sqlite.gz # Compressed SQLite database of Indian places
├── requirements.txt           # Python package dependencies
├── LICENSE                    # MIT License
└── README.md                  # Project documentation
```

## License

This project is licensed under the MIT License. Place data is sourced from GeoNames under the CC BY 4.0 license.
