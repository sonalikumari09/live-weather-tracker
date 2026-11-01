"""Know Your Weather — trilingual city + village weather website (Python + Streamlit)."""
import streamlit as st
import pandas as pd
from streamlit_searchbox import st_searchbox

from i18n import t, weather_name
from geo import find_places, suggest_places, label
from places import warm_up
from weather import get_current_and_daily, get_farmer_data, travel_packing, check_alerts
from ui_effects import GLOBAL_CSS, banner_html

st.set_page_config(page_title="Know Your Weather", page_icon="🌦️", layout="wide")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# Decompress the all-India place index once, before the first keystroke.
# If the bundled file is missing, search_local() simply falls back to live APIs.
warm_up()

# ---------- Sidebar: language + mode ----------
lang_map = {"English": "en", "हिन्दी": "hi", "भोजपुरी": "bho"}
lang_choice = st.sidebar.selectbox("Language / भाषा", list(lang_map.keys()))
lang = lang_map[lang_choice]

def T(key): return t(lang, key)

st.sidebar.title("🌦️ Know Your Weather")
mode = st.sidebar.radio(
    T("mode_label"),
    [T("mode_single"), T("mode_travel"), T("mode_farmer"), T("mode_alert"), T("mode_compare")],
)

st.title(T("app_title"))
st.caption(T("app_sub"))

# ---------- Helpers ----------
@st.cache_data(ttl=3600, max_entries=1000, show_spinner=False)
def cached_search(q):
    return find_places(q)

@st.cache_data(ttl=3600, max_entries=1000, show_spinner=False)
def cached_suggest(q):
    return suggest_places(q)

@st.cache_data(ttl=600, max_entries=2000, show_spinner=False)
def cached_weather(lat, lon):
    return get_current_and_daily(lat, lon)

@st.cache_data(ttl=600, max_entries=1000, show_spinner=False)
def cached_farmer(lat, lon):
    return get_farmer_data(lat, lon)

# Shown when the box is empty so users immediately see the search works.
POPULAR_PLACES = [
    {"name": "Delhi", "latitude": 28.6139, "longitude": 77.2090, "admin2": "New Delhi", "admin1": "Delhi", "country": "India", "type": "city", "type_label": "city"},
    {"name": "Mumbai", "latitude": 19.0760, "longitude": 72.8777, "admin2": "Mumbai", "admin1": "Maharashtra", "country": "India", "type": "city", "type_label": "city"},
    {"name": "Bengaluru", "latitude": 12.9716, "longitude": 77.5946, "admin2": "Bangalore Urban", "admin1": "Karnataka", "country": "India", "type": "city", "type_label": "city"},
    {"name": "Kolkata", "latitude": 22.5726, "longitude": 88.3639, "admin2": "Kolkata", "admin1": "West Bengal", "country": "India", "type": "city", "type_label": "city"},
    {"name": "Pune", "latitude": 18.5204, "longitude": 73.8567, "admin2": "Pune", "admin1": "Maharashtra", "country": "India", "type": "district", "type_label": "district"},
    {"name": "Patna", "latitude": 25.6093, "longitude": 85.1235, "admin2": "Patna", "admin1": "Bihar", "country": "India", "type": "city", "type_label": "city"},
]

def search_places(query: str):
    """Autocomplete callback: returns [(label, place), ...] for the dropdown."""
    q = (query or "").strip()
    if len(q) < 2:
        return []
    try:
        results = cached_suggest(q)
    except RuntimeError:
        # The searchbox shows "No options"; the weather section reports API errors.
        return []

    labels = [label(p) for p in results]
    seen = {}
    for text in labels:
        seen[text] = seen.get(text, 0) + 1
    options = []
    for text, place in zip(labels, results):
        if seen[text] > 1:
            try:
                text = f"{text} ({float(place['latitude']):.2f}, {float(place['longitude']):.2f})"
            except (KeyError, TypeError, ValueError):
                pass
        options.append((text, place))
    return options

def place_picker(key_prefix: str, default_text=""):
    """Autocomplete search box — suggestions appear as the user types."""
    selected = st_searchbox(
        search_places,
        label=T("search_label"),
        placeholder=T("search_placeholder"),
        default_searchterm=default_text,
        default_options=[(label(p), p) for p in POPULAR_PLACES],
        edit_after_submit="option",
        debounce=300,
        key=f"{key_prefix}_searchbox",
    )
    st.caption(T("search_hint"))
    if isinstance(selected, dict) and selected.get("latitude") is not None:
        return selected
    return None

def show_current(place, current, daily):
    code = current.get("weather_code", 0)
    full_loc = label(place)
    # Animated weather banner: rainy droplets / shiny sun / clouds / storm / snow / fog
    st.markdown(
        banner_html(
            code,
            temp_c=current.get("temperature_2m"),
            cond_name=weather_name(code, lang),
            place=place.get("name", ""),
        ),
        unsafe_allow_html=True,
    )
    st.caption(f"📍 **{full_loc}**")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(T("temp"), f"{current.get('temperature_2m')}°C", f"{T('feels_like')}: {current.get('apparent_temperature')}°C")
    c2.metric(T("condition"), weather_name(code, lang))
    c3.metric(T("humidity"), f"{current.get('relative_humidity_2m')}%")
    c4.metric(T("wind"), f"{current.get('wind_speed_10m')} km/h")
    st.info(f"{T('rain_prob')}: {daily['precipitation_probability_max'][0]}%  |  "
            f"{T('max_min')}: {daily['temperature_2m_max'][0]}°C / {daily['temperature_2m_min'][0]}°C")

def show_7day(daily):
    st.subheader(T("forecast7"))
    from ui_effects import THEME_STYLE, get_theme
    icons = [THEME_STYLE[get_theme(c)]["emoji"] for c in daily["weather_code"]]
    df = pd.DataFrame({
        "": icons,
        "Date": daily["time"],
        "Max°C": daily["temperature_2m_max"],
        "Min°C": daily["temperature_2m_min"],
        "Rain%": daily["precipitation_probability_max"],
        "Rain mm": daily["precipitation_sum"],
        "Condition": [weather_name(c, lang) for c in daily["weather_code"]],
    })
    st.dataframe(df, use_container_width=True)
    st.line_chart(df.set_index("Date")[["Max°C", "Min°C"]])
    st.bar_chart(df.set_index("Date")[["Rain%"]])

# ================= MODES =================

# 1. SINGLE PLACE
if mode == T("mode_single"):
    place = place_picker("single")
    if place:
        try:
            current, daily, _tz = cached_weather(place["latitude"], place["longitude"])
            st.subheader(f"{T('current_weather')}: {place['name']}")
            show_current(place, current, daily)
            show_7day(daily)
        except RuntimeError:
            st.error(T("no_internet"))

# 2. TRAVEL PACKER
elif mode == T("mode_travel"):
    st.header(T("travel_title"))
    st.write(T("travel_desc"))
    place = place_picker("travel")
    if place:
        try:
            current, daily, _tz = cached_weather(place["latitude"], place["longitude"])
            show_current(place, current, daily)
            rain_p = daily["precipitation_probability_max"][0]
            tmax = daily["temperature_2m_max"][0]
            wind = current.get("wind_speed_10m", 0)
            items = travel_packing(tmax, rain_p, wind, current.get("weather_code", 0))
            st.subheader(T("packing_list"))
            # Render trilingually
            if "umbrella" in items:
                st.warning("☂️ " + T("take_umbrella").format(p=rain_p))
            else:
                st.success("☀️ " + T("no_umbrella").format(p=rain_p))
            if "heat" in items:
                st.warning("🧢 " + T("heat_pack"))
            if "cold" in items:
                st.warning("🧥 " + T("cold_pack"))
            if "wind" in items:
                st.warning("🧥 " + T("wind_pack"))
            if "normal" in items:
                st.info("🎒 " + T("normal_pack"))
            show_7day(daily)
        except RuntimeError:
            st.error(T("no_internet"))

# 3. FARMER MODE
elif mode == T("mode_farmer"):
    st.header(T("farmer_title"))
    st.write(T("farmer_desc"))
    place = place_picker("farmer", default_text="")
    if place:
        try:
            fj = cached_farmer(place["latitude"], place["longitude"])
            cur = fj.get("current", {})
            daily = fj["daily"]
            st.metric(T("soil_temp"), f"{cur.get('soil_temperature_6cm')}°C")
            st.metric(T("soil_moist"), f"{cur.get('soil_moisture_3_9cm')} m³/m³")
            # Last 7 days rain table
            past_dates = daily["time"][:7]
            past_rain = daily["precipitation_sum"][:7]
            df = pd.DataFrame({"Date": past_dates, "Rain mm": past_rain,
                               "Max°C": daily["temperature_2m_max"][:7]})
            st.subheader(T("rain_last7"))
            st.dataframe(df, use_container_width=True)
            st.bar_chart(df.set_index("Date")["Rain mm"])
            total = sum(x or 0 for x in past_rain)
            next_p = (daily.get("precipitation_probability_max") or [0])[-1]
            # Advisory — trilingual templates
            st.subheader(T("advisory"))
            if lang == "en":
                st.write(f"Total rain past 7 days: **{total:.1f} mm**.")
                if next_p > 70:
                    st.error("Heavy rain in 48h → postpone spray/fertilizer, delay harvesting.")
                elif next_p < 20 and daily["temperature_2m_max"][-1] > 35:
                    st.warning("No rain + heat → irrigate in 1–2 days, use mulch.")
                else:
                    st.success("OK for field work. Spray morning/evening only.")
                if total > 50:
                    st.info("Soil likely wet → avoid tractor, check drainage.")
                elif total < 5:
                    st.info("Dry week → check 6cm soil moisture before sowing.")
            elif lang == "hi":
                st.write(f"पिछले 7 दिन कुल बारिश: **{total:.1f} mm**।")
                if next_p > 70:
                    st.error("48 घंटे में भारी बारिश → स्प्रे/खाद रोकें, कटाई टालें।")
                elif next_p < 20 and daily["temperature_2m_max"][-1] > 35:
                    st.warning("बारिश नहीं + गर्मी → 1-2 दिन में सिंचाई करें, मल्च use करें।")
                else:
                    st.success("खेत के काम के लिए ठीक। स्प्रे सुबह/शाम ही करें।")
                if total > 50:
                    st.info("मिट्टी गीली होगी → ट्रैक्टर न चलाएं, जल निकासी देखें।")
                elif total < 5:
                    st.info("सूखा सप्ताह → बुवाई से पहले नमी जांचें।")
            else:
                st.write(f"पिछला 7 दिन कुल बरखा: **{total:.1f} mm**।")
                if next_p > 70:
                    st.error("48 घंटा में भारी बरखा → दवाई/खाद रोक दीं, कटाई टाल दीं।")
                elif next_p < 20 and daily["temperature_2m_max"][-1] > 35:
                    st.warning("बरखा नईखे + गर्मी → 1-2 दिन में पटवन करीं।")
                else:
                    st.success("खेत के काम खातिर ठीक बा। दवाई बिहान भा सांझे छिड़कीं।")
                if total > 50:
                    st.info("माटी भींजल होई → ट्रैक्टर मत चलाईं, नाली देख लीं।")
                elif total < 5:
                    st.info("सूखा हफ्ता → बुवाई से पहिले नमी जांच लीं।")
        except RuntimeError:
            st.error(T("no_internet"))

# 4. ALERT MODE
elif mode == T("mode_alert"):
    st.header(T("alert_title"))
    st.write(T("alert_desc"))
    place = place_picker("alert")
    if place:
        try:
            current, daily, _tz = cached_weather(place["latitude"], place["longitude"])
            alerts = check_alerts(current, daily)
            if not alerts:
                st.success("✅ " + T("no_alert"))
            else:
                st.error("🚨 " + T("has_alert"))
                # Beep in browser when extreme
                st.markdown(
                    "<audio autoplay><source src='https://www.soundjay.com/buttons/beep-01a.mp3'></audio>",
                    unsafe_allow_html=True,
                )
                for sev, msg in alerts:
                    (st.error if sev == "high" else st.warning)(msg)
                # Copy-paste / email text
                msg_text = f"Know Your Weather Alert {place['name']}: " + " | ".join(m for _, m in alerts)
                st.code(msg_text)
                st.caption("To get this every morning 7 AM: run this app daily, or ask me to add email (SMTP) / cron setup.")
        except RuntimeError:
            st.error(T("no_internet"))

# 5. COMPARE MODE
else:
    st.header(T("compare_title"))
    st.write(T("compare_desc"))
    with st.form(key="cmp_form", clear_on_submit=False):
        q = st.text_input(T("compare_places_label"), placeholder=T("compare_placeholder"),
                          key="cmp_q", max_chars=200)
        cmp_submit = st.form_submit_button(T("compare_button"))
    if cmp_submit or st.session_state.get("cmp_done"):
        names = [x.strip() for x in (q or "").split(",") if x.strip()][:4]
        if not names:
            st.session_state["cmp_done"] = False
            st.warning(T("compare_empty"))
            st.stop()
        st.session_state["cmp_done"] = True
        rows = []
        for name in names:
            try:
                p = cached_search(name)[0]
                cur, daily, _ = cached_weather(p["latitude"], p["longitude"])
                rows.append({
                    "Place": f"{p['name']} ({p.get('admin1','')})",
                    "Temp°C": cur["temperature_2m"],
                    "Feels°C": cur["apparent_temperature"],
                    "Condition": weather_name(cur["weather_code"], lang),
                    "Humidity%": cur["relative_humidity_2m"],
                    "Wind km/h": cur["wind_speed_10m"],
                    "Today Rain%": daily["precipitation_probability_max"][0],
                    "Max/Min": f"{daily['temperature_2m_max'][0]}/{daily['temperature_2m_min'][0]}",
                })
            except RuntimeError as e:
                rows.append({"Place": name, "Temp°C": T("not_found") if str(e) == "not_found" else T("no_internet")})
        df = pd.DataFrame(rows).set_index("Place")
        st.dataframe(df, use_container_width=True)
        # numeric chart only
        try:
            st.bar_chart(df[["Temp°C", "Today Rain%"]])
        except Exception:
            pass

st.divider()
st.caption(T("footer"))
