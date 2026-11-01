# 🌦️ Live Weather Tracker

A fast, privacy-friendly, and trilingual weather web application built with **Python** and **Streamlit**. Designed for everyday travelers, farmers, and families across India.

---

## ✨ Features

- **🇮🇳 All-India District & Village Coverage:** Instant, prefix-aware search across all **763 districts** and **550,000+ villages, towns, and cities** backed by a bundled high-speed SQLite index (no API key required).
- **🌐 Trilingual Support:** Fully translated interface in **English**, **हिन्दी (Hindi)**, and **भोजपुरी (Bhojpuri)**.
- **5 Versatile Modes:**
  1. **🔍 Single Place:** Current temperature, feels-like, wind, humidity, weather animation banners, and 7-day forecast.
  2. **🎒 Travel Packer:** Smart clothing and gear recommendations based on rain probability, wind speed, and temperature.
  3. **🌾 Farmer Mode (Village Special):** Soil temperature (6 cm depth), soil moisture (3–9 cm depth), past 7-day rainfall history, and actionable farming advisories.
  4. **⚠️ Alert Mode:** Instant detection of extreme conditions (heatwave, coldwave, storms, heavy rain, gale wind) with audio alert.
  5. **⚖️ Compare Mode:** Side-by-side comparison of 2–4 cities, districts, or villages.
- **🔒 Zero API Keys Required:** Powered by Open-Meteo and bundled GeoNames data under CC BY 4.0.

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/sonalikumari09/live-weather-tracker.git
cd live-weather-tracker
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📁 Project Structure

```text
├── app.py                   # Streamlit web application & UI logic
├── places.py                # High-speed local search engine for districts & villages
├── geo.py                   # Geocoding & autocomplete suggestion pipeline
├── weather.py               # Open-Meteo weather API integration & alerts
├── i18n.py                  # English, Hindi & Bhojpuri trilingual translations
├── ui_effects.py            # Custom CSS themes & animated weather banners
├── build_india_places.py    # Offline builder for the Indian places index
├── data/
│   └── india_places.sqlite.gz # Bundled index (763 districts, 550,000+ villages)
├── requirements.txt         # Python dependencies
└── LICENSE                  # MIT License
```

---

## 📜 License

This project is licensed under the [MIT License](LICENSE). GeoNames place data is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
