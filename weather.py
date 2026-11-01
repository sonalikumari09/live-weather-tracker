"""Weather fetching + business logic: travel / farmer / alert / compare."""
import requests

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

def _get(url, params):
    try:
        r = requests.get(url, params=params, timeout=12)
        r.raise_for_status()
        return r.json()
    except (requests.Timeout, requests.ConnectionError, requests.HTTPError, ValueError):
        raise RuntimeError("no_internet")

def get_current_and_daily(lat: float, lon: float):
    """Current + 7-day daily forecast."""
    params = {
        "latitude": lat, "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum",
        "timezone": "auto", "forecast_days": 7,
    }
    j = _get(FORECAST_URL, params)
    return j["current"], j["daily"], j.get("timezone", "")

def get_farmer_data(lat: float, lon: float):
    """Farmer mode: past 7 days rain + current soil temp/moisture + 2-day forecast."""
    params = {
        "latitude": lat, "longitude": lon,
        "hourly": "soil_temperature_6cm,soil_moisture_3_9cm,precipitation",
        "daily": "precipitation_sum,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "current": "soil_temperature_6cm,soil_moisture_3_9cm",
        "past_days": 7, "forecast_days": 2,
        "timezone": "auto",
    }
    j = _get(FORECAST_URL, params)
    return j

# ---------- Feature logic (pure functions, easy to test) ----------

def travel_packing(temp_max: float, rain_prob: int, wind: float, wcode: int):
    """Return list of packing keys."""
    items = []
    if rain_prob is not None and rain_prob > 60:
        items.append("umbrella")
    if temp_max is not None:
        if temp_max >= 35:
            items.append("heat")
        elif temp_max <= 10:
            items.append("cold")
    if wind is not None and wind >= 40:
        items.append("wind")
    if wcode in (95, 96, 99):
        if "umbrella" not in items:
            items.append("umbrella")
    if not items:
        items.append("normal")
    return items

def check_alerts(current: dict, daily: dict):
    """Return list of (severity, message_en) for extreme weather."""
    alerts = []
    t = current.get("temperature_2m")
    wind = current.get("wind_speed_10m", 0)
    wcode = current.get("weather_code", 0)
    try:
        today_max = daily["temperature_2m_max"][0]
        today_min = daily["temperature_2m_min"][0]
        today_rain_p = daily["precipitation_probability_max"][0]
    except Exception:
        today_max = today_min = today_rain_p = None

    if today_max is not None and today_max >= 40:
        alerts.append(("high", f"Heat wave: {today_max}°C today. Avoid 12–4 PM, drink water."))
    if today_min is not None and today_min <= 5:
        alerts.append(("high", f"Cold wave: {today_min}°C tonight. Protect crops/animals."))
    if wcode in (95, 96, 99):
        alerts.append(("high", "Thunderstorm now. Stay indoors, unplug equipment."))
    if today_rain_p is not None and today_rain_p >= 80:
        alerts.append(("medium", f"Heavy rain chance {today_rain_p}%. Postpone travel/spraying."))
    if wind is not None and wind >= 60:
        alerts.append(("medium", f"High wind {wind} km/h. Secure tin roofs, avoid highway driving."))
    return alerts

def farm_advisory_en(farmer_json: dict) -> list:
    """English advisory strings from farmer API JSON."""
    tips = []
    try:
        daily = farmer_json["daily"]
        past_rain = daily["precipitation_sum"][:7]  # last 7 days
        total_past = sum(x or 0 for x in past_rain)
        next_p = (daily.get("precipitation_probability_max") or [0])[-1]
        tmax = (daily.get("temperature_2m_max") or [0])[-1]
    except Exception:
        return ["Could not compute advisory."]
    tips.append(f"Total rain in past 7 days: {total_past:.1f} mm.")
    if next_p is not None and next_p > 70:
        tips.append("Heavy rain expected in 48h → postpone fertilizer/pesticide spray, delay harvesting.")
    elif next_p is not None and next_p < 20 and (tmax or 0) > 35:
        tips.append("No rain + heat → irrigation needed in 1–2 days. Mulch to retain moisture.")
    else:
        tips.append("Weather ok for normal field work. Spray only in morning/evening.")
    if total_past > 50:
        tips.append("Soil likely wet → avoid heavy tractor use (compaction), check drainage.")
    elif total_past < 5:
        tips.append("Very dry week → check soil moisture at 6cm before sowing.")
    return tips
