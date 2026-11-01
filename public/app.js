/**
 * Live Weather Tracker - Client Application
 * Compatible with Cloudflare Pages Functions & D1 Database.
 */

// Trilingual Dictionary (English, Hindi, Bhojpuri)
const I18N = {
  en: {
    app_title: "Live Weather Tracker",
    app_sub: "Fast, clean weather for all Indian districts, towns, and villages.",
    tab_single: "Single Place",
    tab_travel: "Travel Packer",
    tab_farmer: "Farmer Mode",
    tab_alert: "Morning Alerts",
    tab_compare: "Compare",
    search_placeholder: "Search city, district, village, or PIN code (e.g. Pune, Patna, 110001)",
    search_hint: "Type 2 or more letters to search all Indian villages, districts, and cities.",
    lbl_temp: "Temperature",
    lbl_feels: "Feels like",
    lbl_humidity: "Humidity",
    lbl_comfort: "Relative humidity",
    lbl_wind: "Wind Speed",
    lbl_wind_dir: "10m elevation",
    lbl_rain: "Rain Chance",
    lbl_forecast7: "7-Day Forecast",
    lbl_temp_trend: "Temperature Trend (°C)",
    lbl_rain_prob: "Rain Probability (%)",
    travel_title: "Travel Packing Advice",
    travel_desc: "Smart clothing and gear recommendations based on temperature, rain probability, and wind.",
    farmer_title: "Farmer Mode (Village Special)",
    farmer_desc: "Soil temperature, moisture levels, past 7 days rainfall history, and agricultural guidance for your village.",
    lbl_soil_temp: "Soil Temp (6cm)",
    lbl_soil_moist: "Soil Moisture",
    lbl_rain_last7: "Rainfall Past 7 Days",
    lbl_advisory: "Farm Advisory",
    alert_title: "Morning Severe Weather Alerts",
    alert_desc: "Checks for extreme conditions: heatwaves, coldwaves, thunderstorms, heavy rain, or high winds.",
    no_alert: "All clear. No extreme weather conditions detected.",
    has_alert: "Attention needed! Severe weather detected.",
    compare_title: "Compare Places",
    compare_desc: "Compare up to 4 cities, districts, or villages side by side.",
    compare_placeholder: "Type city or village names separated by comma, e.g. Delhi, Mumbai, Pune",
    compare_btn: "Compare",
    not_found: "Place not found. Check spelling or try nearby district.",
    footer: "Data: Open-Meteo & GeoNames. Built with clean HTML, CSS, JavaScript & Cloudflare Pages.",
    take_umbrella: "Take umbrella or raincoat (Rain chance: {p}%)",
    no_umbrella: "No umbrella needed (Rain chance: {p}%)",
    heat_pack: "Heat alert: Sunscreen, cap, light clothes, 2L water",
    cold_pack: "Cold alert: Heavy jacket, gloves, warm socks",
    wind_pack: "High wind: Secure windcheater jacket",
    normal_pack: "Weather normal: Light clothes and water bottle",
  },
  hi: {
    app_title: "लाइव वेदर ट्रैकर",
    app_sub: "भारत के सभी जिलों, शहरों और गाँवों के लिए स्वच्छ और तेज़ मौसम।",
    tab_single: "एक जगह का मौसम",
    tab_travel: "यात्रा पैकर",
    tab_farmer: "किसान मोड",
    tab_alert: "सुबह की चेतावनी",
    tab_compare: "तुलना करें",
    search_placeholder: "शहर, जिला, गाँव या पिन कोड खोजें (उदा. Pune, Patna, 110001)",
    search_hint: "भारत के सभी गाँवों, जिलों और शहरों को खोजने के लिए 2 या अधिक अक्षर टाइप करें।",
    lbl_temp: "तापमान",
    lbl_feels: "महसूस होगा",
    lbl_humidity: "नमी",
    lbl_comfort: "सापेक्ष आर्द्रता",
    lbl_wind: "हवा की गति",
    lbl_wind_dir: "10 मीटर ऊंचाई पर",
    lbl_rain: "बारिश की संभावना",
    lbl_forecast7: "7 दिन का पूर्वानुमान",
    lbl_temp_trend: "तापमान का रुझान (°C)",
    lbl_rain_prob: "बारिश की संभावना (%)",
    travel_title: "यात्रा पैकिंग सलाह",
    travel_desc: "तापमान, बारिश और हवा के आधार पर कपड़े और सामान की सलाह।",
    farmer_title: "किसान मोड (गाँव स्पेशल)",
    farmer_desc: "आपके गाँव की मिट्टी का तापमान, नमी और पिछले 7 दिन की बारिश।",
    lbl_soil_temp: "मिट्टी तापमान (6cm)",
    lbl_soil_moist: "मिट्टी नमी",
    lbl_rain_last7: "पिछले 7 दिन की बारिश",
    lbl_advisory: "खेती सलाह",
    alert_title: "सुबह की मौसम चेतावनी",
    alert_desc: "खतरनाक मौसम: लू, ठंड, आंधी, भारी बारिश या तेज हवा की जांच।",
    no_alert: "मौसम सामान्य है। कोई खतरा नहीं है।",
    has_alert: "सावधानी जरूरी! गंभीर मौसम चेतावनी।",
    compare_title: "शहरों / गाँवों की तुलना",
    compare_desc: "एक साथ 2 से 4 जगहों के मौसम की तुलना करें।",
    compare_placeholder: "जगहों के नाम अल्पविराम से लिखें, उदा. Delhi, Mumbai, Pune",
    compare_btn: "तुलना करें",
    not_found: "जगह नहीं मिली। वर्तनी जांचें।",
    footer: "डेटा: Open-Meteo और GeoNames। Cloudflare Pages के लिए निर्मित।",
    take_umbrella: "छाता या रेनकोट साथ रखें (बारिश: {p}%)",
    no_umbrella: "छाते की जरूरत नहीं (बारिश: {p}%)",
    heat_pack: "गर्मी से बचाव: सनस्क्रीन, टोपी, 2 लीटर पानी",
    cold_pack: "ठंड से बचाव: भारी जैकेट, दस्ताने",
    wind_pack: "तेज हवा: विंडचीटर पहनें",
    normal_pack: "मौसम सामान्य: हल्के कपड़े और पानी की बोतल",
  },
  bho: {
    app_title: "लाइव वेदर ट्रैकर",
    app_sub: "भारत के सभे जिला, शहर आ गाँव खातिर आसान आ तेज मौसम।",
    tab_single: "एगो जगह के मौसम",
    tab_travel: "यात्रा के सामान",
    tab_farmer: "किसान मोड",
    tab_alert: "चेतावनी मोड",
    tab_compare: "तुलना करीं",
    search_placeholder: "शहर, जिला, गाँव भा पिन कोड खोजीं (उदा. Pune, Patna, 110001)",
    search_hint: "भारत के सभे गाँव, जिला आ शहर खोजे खातिर 2 भा ढेर अक्षर लिखीं।",
    lbl_temp: "तापमान",
    lbl_feels: "महसूस होई",
    lbl_humidity: "नमी",
    lbl_comfort: "सापेक्ष नमी",
    lbl_wind: "हवा के गति",
    lbl_wind_dir: "10 मीटर ऊंचाई पर",
    lbl_rain: "बरखा के संभावना",
    lbl_forecast7: "7 दिन के हाल",
    lbl_temp_trend: "तापमान के चाल (°C)",
    lbl_rain_prob: "बरखा के संभावना (%)",
    travel_title: "यात्रा के सामान के सलाह",
    travel_desc: "तापमान, बरखा आ हवा के देख के सामान बांधे के सलाह।",
    farmer_title: "किसान मोड (गाँव स्पेशल)",
    farmer_desc: "राउर गाँव के माटी के तापमान, नमी आ पिछला 7 दिन के बरखा।",
    lbl_soil_temp: "माटी के तापमान (6cm)",
    lbl_soil_moist: "माटी के नमी",
    lbl_rain_last7: "पिछला 7 दिन के बरखा",
    lbl_advisory: "खेती के सलाह",
    alert_title: "सुबह के मौसम चेतावनी",
    alert_desc: "खतरनाक मौसम: लू, जाड़ा, आंधी, भारी बरखा भा तेज हवा के जांच।",
    no_alert: "मौसम एकदम ठीक बा। कौनों खतरा नइखे।",
    has_alert: "सावधानी जरूरी बा! खराब मौसम बा।",
    compare_title: "शहर / गाँव के तुलना",
    compare_desc: "एक संगे 2 से 4 जगह के मौसम देखल जा सकेला।",
    compare_placeholder: "जगह के नाम अल्पविराम से लिखीं, जैसे Delhi, Mumbai, Pune",
    compare_btn: "तुलना करीं",
    not_found: "जगह ना मिलल। नाम जांच लीं।",
    footer: "डेटा: Open-Meteo आ GeoNames। Cloudflare Pages खातिर बनल बा।",
    take_umbrella: "छाता भा रेनकोट ले लीं (बरखा: {p}%)",
    no_umbrella: "छाता के जरूरत नइखे (बरखा: {p}%)",
    heat_pack: "घाम से बचाव: टोपी, सनस्क्रीन, 2L पानी",
    cold_pack: "जाड़ा से बचाव: भारी जैकेट, टोपी",
    wind_pack: "तेज हवा: विंडचीटर पहिनीं",
    normal_pack: "मौसम सामान्य: पातर कपड़ा आ पानी के बोतल",
  },
};

// WMO Weather Codes mapping
const WMO_MAP = {
  0: { en: "Clear sky", hi: "साफ आसमान", bho: "साफ आसमान", icon: "☀️", theme: "clear" },
  1: { en: "Mainly clear", hi: "ज्यादातर साफ", bho: "अधिकतर साफ", icon: "🌤️", theme: "clear" },
  2: { en: "Partly cloudy", hi: "हल्के बादल", bho: "हल्का बादर", icon: "⛅", theme: "partcloud" },
  3: { en: "Overcast", hi: "घने बादल", bho: "घनघोर बादर", icon: "☁️", theme: "cloudy" },
  45: { en: "Foggy", hi: "कोहरा", bho: "कुहासा", icon: "🌫️", theme: "fog" },
  48: { en: "Depositing rime fog", hi: "सख्त कोहरा", bho: "कड़ा कुहासा", icon: "🌫️", theme: "fog" },
  51: { en: "Light drizzle", hi: "हल्की बूंदाबांदी", bho: "फुहार", icon: "🌦️", theme: "drizzle" },
  53: { en: "Moderate drizzle", hi: "बूंदाबांदी", bho: "बूंदाबांदी", icon: "🌦️", theme: "drizzle" },
  55: { en: "Dense drizzle", hi: "घनी बूंदाबांदी", bho: "गाढ़ा फुहार", icon: "🌧️", theme: "drizzle" },
  61: { en: "Slight rain", hi: "हल्की बारिश", bho: "हल्का बरखा", icon: "🌧️", theme: "rainy" },
  63: { en: "Moderate rain", hi: "मध्यम बारिश", bho: "मध्यम बरखा", icon: "🌧️", theme: "rainy" },
  65: { en: "Heavy rain", hi: "भारी बारिश", bho: "भारी बरखा", icon: "⛈️", theme: "rainy" },
  71: { en: "Slight snow", hi: "हल्की बर्फबारी", bho: "हल्का बर्फ", icon: "🌨️", theme: "snow" },
  73: { en: "Moderate snow", hi: "मध्यम बर्फबारी", bho: "बर्फबारी", icon: "🌨️", theme: "snow" },
  75: { en: "Heavy snow", hi: "भारी बर्फबारी", bho: "भारी बर्फबारी", icon: "❄️", theme: "snow" },
  80: { en: "Rain showers", hi: "तेज बौछारें", bho: "बरखा के झोंका", icon: "🌦️", theme: "rainy" },
  81: { en: "Heavy showers", hi: "भारी बौछारें", bho: "भारी बौछार", icon: "🌧️", theme: "rainy" },
  95: { en: "Thunderstorm", hi: "आंधी-तूफान", bho: "आंधी-तूफान", icon: "⛈️", theme: "thunder" },
  96: { en: "Thunderstorm with hail", hi: "ओलावृष्टि तूफान", bho: "ओला वाला तूफान", icon: "⛈️", theme: "thunder" },
  99: { en: "Heavy thunderstorm with hail", hi: "भीषण तूफान और ओले", bho: "भीषण तूफान आ पाथर", icon: "⛈️", theme: "thunder" },
};

function getWeatherInfo(code, lang) {
  const item = WMO_MAP[code] || {
    en: "Scattered clouds",
    hi: "बादल",
    bho: "बादर",
    icon: "⛅",
    theme: "cloudy",
  };
  return {
    name: item[lang] || item.en,
    icon: item.icon,
    theme: item.theme,
  };
}

// Popular Places for default suggestions
const POPULAR_PLACES = [
  { name: "Delhi", latitude: 28.6139, longitude: 77.209, admin2: "New Delhi", admin1: "Delhi", type: "city", type_label: "city", label: "Delhi, New Delhi, Delhi [city]" },
  { name: "Mumbai", latitude: 19.076, longitude: 72.8777, admin2: "Mumbai", admin1: "Maharashtra", type: "city", type_label: "city", label: "Mumbai, Maharashtra [city]" },
  { name: "Bengaluru", latitude: 12.9716, longitude: 77.5946, admin2: "Bangalore Urban", admin1: "Karnataka", type: "city", type_label: "city", label: "Bengaluru, Bangalore Urban, Karnataka [city]" },
  { name: "Kolkata", latitude: 22.5726, longitude: 88.3639, admin2: "Kolkata", admin1: "West Bengal", type: "city", type_label: "city", label: "Kolkata, West Bengal [city]" },
  { name: "Pune", latitude: 18.5204, longitude: 73.8567, admin2: "Pune", admin1: "Maharashtra", type: "district", type_label: "district", label: "Pune, Maharashtra [district]" },
  { name: "Patna", latitude: 25.6093, longitude: 85.1235, admin2: "Patna", admin1: "Bihar", type: "city", type_label: "city", label: "Patna, Bihar [city]" },
];

// App State
let currentLang = "en";
let currentMode = "single";
let selectedPlace = POPULAR_PLACES[0];
let weatherData = null;
let farmerData = null;
let searchDebounceTimer = null;
let selectedDayIndex = 0;
let selectedHourIndex = null;

// DOM Elements
const langSelect = document.getElementById("lang-select");
const searchInput = document.getElementById("place-search");
const clearBtn = document.getElementById("clear-search");
const searchSpinner = document.getElementById("search-spinner");
const suggestionsList = document.getElementById("suggestions-list");

// Initialize
document.addEventListener("DOMContentLoaded", () => {
  setupThemeToggle();
  setupLanguage();
  setupNavigation();
  setupSearch();
  loadPlace(selectedPlace);
});

// ----------------- Light / Dark Mode Handling -----------------
function setupThemeToggle() {
  const toggleBtn = document.getElementById("theme-toggle");
  const themeIcon = document.getElementById("theme-icon");
  if (!toggleBtn || !themeIcon) return;

  const savedTheme = localStorage.getItem("weather_theme");
  const systemPrefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  const currentTheme = savedTheme || (systemPrefersDark ? "dark" : "light");

  applyTheme(currentTheme);

  toggleBtn.addEventListener("click", () => {
    const isDark = document.documentElement.getAttribute("data-theme") === "dark";
    const nextTheme = isDark ? "light" : "dark";
    applyTheme(nextTheme);
    localStorage.setItem("weather_theme", nextTheme);
  });

  if (window.matchMedia) {
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
      if (!localStorage.getItem("weather_theme")) {
        applyTheme(e.matches ? "dark" : "light");
      }
    });
  }
}

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  const toggleBtn = document.getElementById("theme-toggle");
  if (toggleBtn) {
    toggleBtn.setAttribute("aria-label", `Currently ${theme} mode. Click to toggle.`);
    toggleBtn.title = theme === "dark" ? "Switch to Light Mode" : "Switch to Dark Mode";
  }
}

// ----------------- Language Handling -----------------
function setupLanguage() {
  langSelect.addEventListener("change", (e) => {
    currentLang = e.target.value;
    updateLanguageStrings();
    if (weatherData) renderWeatherView();
    if (farmerData) renderFarmerView();
  });
}

function updateLanguageStrings() {
  const dict = I18N[currentLang];
  document.getElementById("app-title").textContent = dict.app_title;
  document.getElementById("app-sub").textContent = dict.app_sub;
  document.getElementById("tab-single").textContent = dict.tab_single;
  document.getElementById("tab-travel").textContent = dict.tab_travel;
  document.getElementById("tab-farmer").textContent = dict.tab_farmer;
  document.getElementById("tab-alert").textContent = dict.tab_alert;
  document.getElementById("tab-compare").textContent = dict.tab_compare;
  searchInput.placeholder = dict.search_placeholder;
  document.getElementById("search-hint").textContent = dict.search_hint;
  document.getElementById("lbl-temp").textContent = dict.lbl_temp;
  document.getElementById("lbl-humidity").textContent = dict.lbl_humidity;
  document.getElementById("lbl-comfort").textContent = dict.lbl_comfort;
  document.getElementById("lbl-wind").textContent = dict.lbl_wind;
  document.getElementById("lbl-wind-dir").textContent = dict.lbl_wind_dir;
  document.getElementById("lbl-rain").textContent = dict.lbl_rain;
  document.getElementById("lbl-forecast7").textContent = dict.lbl_forecast7;
  document.getElementById("lbl-temp-trend").textContent = dict.lbl_temp_trend;
  document.getElementById("lbl-rain-prob").textContent = dict.lbl_rain_prob;
  document.getElementById("lbl-travel-title").textContent = dict.travel_title;
  document.getElementById("lbl-travel-desc").textContent = dict.travel_desc;
  document.getElementById("lbl-farmer-title").textContent = dict.farmer_title;
  document.getElementById("lbl-farmer-desc").textContent = dict.farmer_desc;
  document.getElementById("lbl-soil-temp").textContent = dict.lbl_soil_temp;
  document.getElementById("lbl-soil-moist").textContent = dict.lbl_soil_moist;
  document.getElementById("lbl-rain-last7").textContent = dict.lbl_rain_last7;
  document.getElementById("lbl-advisory").textContent = dict.lbl_advisory;
  document.getElementById("lbl-alert-title").textContent = dict.alert_title;
  document.getElementById("lbl-alert-desc").textContent = dict.alert_desc;
  document.getElementById("lbl-compare-title").textContent = dict.compare_title;
  document.getElementById("lbl-compare-desc").textContent = dict.compare_desc;
  document.getElementById("compare-input").placeholder = dict.compare_placeholder;
  document.getElementById("compare-btn").textContent = dict.compare_btn;
  document.getElementById("lbl-footer").textContent = dict.footer;
}

// ----------------- Navigation Tabs -----------------
function setupNavigation() {
  document.querySelectorAll(".nav-tab").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".nav-tab").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      currentMode = btn.dataset.mode;

      document.querySelectorAll(".mode-view").forEach((v) => v.classList.remove("active"));
      document.getElementById(`mode-${currentMode}-view`).classList.add("active");

      if (currentMode === "farmer" && !farmerData) {
        fetchFarmerData(selectedPlace.latitude, selectedPlace.longitude);
      }
    });
  });

  document.getElementById("compare-btn").addEventListener("click", handleCompareSubmit);
}

// ----------------- Autocomplete Search -----------------
function setupSearch() {
  searchInput.addEventListener("input", (e) => {
    const val = e.target.value.trim();
    clearBtn.style.display = val ? "block" : "none";

    clearTimeout(searchDebounceTimer);
    if (val.length < 2) {
      showDefaultSuggestions();
      return;
    }

    searchSpinner.style.display = "block";
    searchDebounceTimer = setTimeout(() => {
      fetchSuggestions(val);
    }, 280);
  });

  searchInput.addEventListener("focus", () => {
    if (!searchInput.value.trim()) {
      showDefaultSuggestions();
    }
  });

  clearBtn.addEventListener("click", () => {
    searchInput.value = "";
    clearBtn.style.display = "none";
    suggestionsList.style.display = "none";
    searchInput.focus();
  });

  document.addEventListener("click", (e) => {
    if (!e.target.closest(".search-wrapper")) {
      suggestionsList.style.display = "none";
    }
  });
}

function showDefaultSuggestions() {
  renderDropdown(POPULAR_PLACES);
}

async function fetchSuggestions(query) {
  try {
    const res = await fetch(`/api/suggest?q=${encodeURIComponent(query)}&limit=8`);
    if (!res.ok) throw new Error("Network error");
    const places = await res.json();
    renderDropdown(places);
  } catch (err) {
    suggestionsList.style.display = "none";
  } finally {
    searchSpinner.style.display = "none";
  }
}

function renderDropdown(places) {
  suggestionsList.innerHTML = "";
  if (!places || places.length === 0) {
    const empty = document.createElement("li");
    empty.className = "suggestion-item";
    empty.innerHTML = `<span class="suggestion-text">${I18N[currentLang].not_found}</span>`;
    suggestionsList.appendChild(empty);
    suggestionsList.style.display = "block";
    return;
  }

  places.forEach((p) => {
    const li = document.createElement("li");
    li.className = "suggestion-item";

    const badgeClass =
      p.type === "district"
        ? "badge-district"
        : p.type === "city"
        ? "badge-city"
        : p.type === "village"
        ? "badge-village"
        : "badge-subdistrict";

    li.innerHTML = `
      <span class="suggestion-text">${escapeHtml(p.label || p.name)}</span>
      <span class="suggestion-badge ${badgeClass}">${p.type_label || p.type || "place"}</span>
    `;

    li.addEventListener("click", () => {
      selectedPlace = p;
      searchInput.value = p.name;
      suggestionsList.style.display = "none";
      loadPlace(p);
    });

    suggestionsList.appendChild(li);
  });
  suggestionsList.style.display = "block";
}

// ----------------- Data Loading & Weather Fetching -----------------
async function loadPlace(place) {
  updateLocationBadges(place);
  await fetchWeatherData(place.latitude, place.longitude);
  if (currentMode === "farmer") {
    await fetchFarmerData(place.latitude, place.longitude);
  }
}

function updateLocationBadges(place) {
  const badgeText = `📍 ${place.label || place.name}`;
  document.getElementById("travel-location-badge").textContent = badgeText;
  document.getElementById("farmer-location-badge").textContent = badgeText;
  document.getElementById("alert-location-badge").textContent = badgeText;
}

async function fetchWeatherData(lat, lon) {
  try {
    const res = await fetch(`/api/weather?lat=${lat}&lon=${lon}`);
    if (!res.ok) throw new Error("Failed to load weather");
    weatherData = await res.json();
    renderWeatherView();
    renderTravelView();
    renderAlertsView();
  } catch (err) {
    console.error(err);
  }
}

async function fetchFarmerData(lat, lon) {
  try {
    const res = await fetch(`/api/farmer?lat=${lat}&lon=${lon}`);
    if (!res.ok) throw new Error("Failed to load farmer data");
    farmerData = await res.json();
    renderFarmerView();
  } catch (err) {
    console.error(err);
  }
}

// ----------------- Rendering Views -----------------
function renderWeatherView() {
  if (!weatherData) return;
  const current = weatherData.current || {};
  const daily = weatherData.daily || {};
  const code = current.weather_code || 0;
  const weather = getWeatherInfo(code, currentLang);

  const isDay = current.is_day !== undefined ? (current.is_day === 1) : true;
  let activeTheme = weather.theme;
  let dynamicIcon = weather.icon;

  if (!isDay) {
    if (weather.theme === "clear") {
      activeTheme = "clear-night";
      dynamicIcon = "🌙";
    } else if (weather.theme === "partcloud") {
      activeTheme = "partcloud-night";
      dynamicIcon = "☁️";
    }
  } else {
    if (weather.theme === "clear") {
      dynamicIcon = "☀️";
    }
  }

  // Weather Banner
  const banner = document.getElementById("weather-banner");
  banner.className = `weather-banner weather-${activeTheme}`;
  document.getElementById("banner-icon").textContent = dynamicIcon;
  document.getElementById("banner-temp").textContent = Math.round(current.temperature_2m);
  document.getElementById("banner-condition").textContent = weather.name;
  document.getElementById("banner-place-name").textContent = selectedPlace.name;
  document.getElementById("banner-full-loc").textContent =
    selectedPlace.label || `${selectedPlace.name}, ${selectedPlace.admin1}`;

  // Sunrise / Sunset display
  const suntimeEl = document.getElementById("banner-suntime");
  if (suntimeEl && daily.sunrise && daily.sunrise[0] && daily.sunset && daily.sunset[0]) {
    const sunriseStr = formatTime(daily.sunrise[0]);
    const sunsetStr = formatTime(daily.sunset[0]);
    suntimeEl.textContent = `🌅 Sunrise: ${sunriseStr}  •  🌇 Sunset: ${sunsetStr}`;
  }

  // Render pure CSS animated weather effects
  renderBannerFx(weather.theme, isDay);

  // Metrics Grid
  document.getElementById("val-temp").textContent = `${current.temperature_2m}°C`;
  document.getElementById(
    "val-feels"
  ).textContent = `${I18N[currentLang].lbl_feels}: ${current.apparent_temperature}°C`;
  document.getElementById("val-humidity").textContent = `${current.relative_humidity_2m}%`;
  document.getElementById("val-wind").textContent = `${current.wind_speed_10m} km/h`;

  const rainProb = (daily.precipitation_probability_max && daily.precipitation_probability_max[0]) ?? 0;
  document.getElementById("val-rain").textContent = `${rainProb}%`;

  const tMax = (daily.temperature_2m_max && daily.temperature_2m_max[0]) ?? "--";
  const tMin = (daily.temperature_2m_min && daily.temperature_2m_min[0]) ?? "--";
  document.getElementById("val-maxmin").textContent = `Max: ${tMax}°C / Min: ${tMin}°C`;

  // 7-Day Forecast Cards
  renderForecastCards(daily);

  // Charts
  renderTemperatureChart(daily);
  renderRainChart(daily);
}

function formatTime(isoStr) {
  try {
    const d = new Date(isoStr);
    let hours = d.getHours();
    const minutes = d.getMinutes();
    const ampm = hours >= 12 ? "PM" : "AM";
    hours = hours % 12;
    hours = hours ? hours : 12;
    const mStr = minutes < 10 ? `0${minutes}` : minutes;
    const hStr = hours < 10 ? `0${hours}` : hours;
    return `${hStr}:${mStr} ${ampm}`;
  } catch (e) {
    return isoStr ? isoStr.slice(-5) : "--";
  }
}

function renderBannerFx(theme, isDay) {
  const container = document.getElementById("banner-fx");
  if (!container) return;
  container.innerHTML = "";

  const currentWind = (weatherData && weatherData.current && weatherData.current.wind_speed_10m) || 0;
  const isWindy = currentWind >= 18;

  if (theme === "clear") {
    let html = isDay ? '<div class="wx-sun"></div>' : "";
    if (isWindy) html += generateWindStreams(4);
    container.innerHTML = html;
    return;
  }

  if (theme === "partcloud") {
    let html = isDay
      ? '<div class="wx-sun" style="width:68px;height:68px;top:20px;right:40px;"></div>'
      : "";
    html += generateClouds(3, !isDay);
    if (isWindy) html += generateWindStreams(4);
    container.innerHTML = html;
    return;
  }

  if (theme === "cloudy") {
    let html = generateClouds(4, false);
    if (isWindy) html += generateWindStreams(5);
    container.innerHTML = html;
    return;
  }

  if (theme === "fog") {
    let html = generateClouds(2, true);
    html += '<div class="wx-fogband" style="top:55px;animation-duration:5s;"></div>';
    html += '<div class="wx-fogband" style="top:90px;animation-duration:7s;"></div>';
    html += '<div class="wx-fogband" style="top:125px;animation-duration:6s;"></div>';
    if (isWindy) html += generateWindStreams(3);
    container.innerHTML = html;
    return;
  }

  if (theme === "drizzle") {
    let html = generateClouds(2, false) + generateDrops(18);
    if (isWindy) html += generateWindStreams(4);
    container.innerHTML = html;
    return;
  }

  if (theme === "rainy") {
    let html = generateClouds(3, true) + generateDrops(32);
    if (isWindy) html += generateWindStreams(5);
    container.innerHTML = html;
    return;
  }

  if (theme === "thunder") {
    let html = '<div class="wx-stormflash"></div>';
    html += generateClouds(3, true);
    html += generateDrops(28);
    if (isWindy) html += generateWindStreams(5);
    html += '<div class="wx-bolt" style="left:22%;">⚡</div>';
    html += '<div class="wx-bolt" style="left:68%;animation-delay:1.5s;">⚡</div>';
    container.innerHTML = html;
    return;
  }

  if (theme === "snow") {
    let html = generateClouds(2, false) + generateFlakes(24);
    if (isWindy) html += generateWindStreams(4);
    container.innerHTML = html;
    return;
  }
}

function generateClouds(n, dark) {
  let html = "";
  const tops = [15, 48, 85, 115];
  for (let i = 0; i < n; i++) {
    const top = tops[i % tops.length];
    const w = 90 + ((i * 37) % 55);
    const dur = 20 + ((i * 9) % 18);
    const delay = -(i * 7);
    const bg = dark ? "#94a3b8" : "#ffffff";
    const op = dark ? 0.65 : 0.92;
    html += `<div class="wx-cloud" style="top:${top}px;width:${w}px;height:${Math.round(w / 3)}px;background:${bg};opacity:${op};animation-duration:${dur}s;animation-delay:${delay}s;"></div>`;
  }
  return html;
}

function generateDrops(n) {
  let html = "";
  for (let i = 0; i < n; i++) {
    const left = 3 + ((i * 31) % 94);
    const delay = ((i * 0.17) % 1.5).toFixed(2);
    const dur = (0.7 + ((i * 0.13) % 0.6)).toFixed(2);
    const h = 14 + ((i * 5) % 12);
    html += `<div class="wx-drop" style="left:${left}%;animation-delay:${delay}s;animation-duration:${dur}s;height:${h}px;"></div>`;
  }
  return html;
}

function generateFlakes(n) {
  let html = "";
  for (let i = 0; i < n; i++) {
    const left = 3 + ((i * 29) % 94);
    const delay = ((i * 0.23) % 2.5).toFixed(2);
    const dur = (2.2 + ((i * 0.31) % 2.3)).toFixed(2);
    const size = 12 + ((i * 3) % 12);
    html += `<div class="wx-flake" style="left:${left}%;font-size:${size}px;animation-delay:${delay}s;animation-duration:${dur}s;">❄</div>`;
  }
  return html;
}

function generateWindStreams(n) {
  let html = "";
  for (let i = 0; i < n; i++) {
    const top = 16 + ((i * 24) % 92);
    const w = 70 + ((i * 35) % 85);
    const dur = (1.4 + ((i * 0.25) % 1.2)).toFixed(2);
    const delay = -(i * 0.35).toFixed(2);
    html += `<div class="wx-windstream" style="top:${top}px;width:${w}px;animation-duration:${dur}s;animation-delay:${delay}s;"></div>`;
  }
  return html;
}

function renderForecastCards(daily) {
  const container = document.getElementById("forecast-cards-container");
  container.innerHTML = "";
  if (!daily || !daily.time) return;

  if (selectedDayIndex >= daily.time.length) {
    selectedDayIndex = 0;
  }

  daily.time.forEach((t, i) => {
    const card = document.createElement("div");
    card.className = `forecast-card ${i === selectedDayIndex ? "selected" : ""}`;
    card.dataset.dayIndex = i;

    const date = new Date(t);
    const dayName = i === 0
      ? (currentLang === "hi" ? "आज" : currentLang === "bho" ? "आजु" : "Today")
      : i === 1
      ? (currentLang === "hi" ? "कल" : currentLang === "bho" ? "बिहाने" : "Tomorrow")
      : date.toLocaleDateString(currentLang === "en" ? "en-US" : "hi-IN", { weekday: "short" });

    const dateStr = date.toLocaleDateString(currentLang === "en" ? "en-US" : "hi-IN", {
      day: "numeric",
      month: "short",
    });
    const code = daily.weather_code[i];
    const w = getWeatherInfo(code, currentLang);
    const rain = daily.precipitation_probability_max ? daily.precipitation_probability_max[i] : 0;

    card.innerHTML = `
      <div class="fc-day">${dayName}</div>
      <div class="fc-date">${dateStr}</div>
      <div class="fc-icon">${w.icon}</div>
      <div class="fc-temps">${daily.temperature_2m_max[i]}° <span class="fc-min">${daily.temperature_2m_min[i]}°</span></div>
      <div class="fc-rain">💧 ${rain}%</div>
    `;

    card.addEventListener("click", () => {
      selectedDayIndex = i;
      container.querySelectorAll(".forecast-card").forEach((c) => c.classList.remove("selected"));
      card.classList.add("selected");
      renderHourlyDetail(i);
    });

    container.appendChild(card);
  });

  renderHourlyDetail(selectedDayIndex);
}

function renderHourlyDetail(dayIndex) {
  selectedDayIndex = dayIndex;
  const panel = document.getElementById("hourly-detail-section");
  if (!panel) return;
  panel.style.display = "block";

  if (!weatherData || !weatherData.hourly || !weatherData.hourly.time) {
    return;
  }

  const daily = weatherData.daily || {};
  const hourly = weatherData.hourly;
  const startIdx = dayIndex * 24;
  const endIdx = startIdx + 24;

  const times = hourly.time.slice(startIdx, endIdx);
  const temps = hourly.temperature_2m.slice(startIdx, endIdx);
  const humids = hourly.relative_humidity_2m ? hourly.relative_humidity_2m.slice(startIdx, endIdx) : [];
  const rains = hourly.precipitation_probability ? hourly.precipitation_probability.slice(startIdx, endIdx) : [];
  const codes = hourly.weather_code ? hourly.weather_code.slice(startIdx, endIdx) : [];
  const winds = hourly.wind_speed_10m ? hourly.wind_speed_10m.slice(startIdx, endIdx) : [];
  const feels = hourly.apparent_temperature ? hourly.apparent_temperature.slice(startIdx, endIdx) : temps;

  if (times.length === 0) return;

  const dayDate = daily.time && daily.time[dayIndex] ? new Date(daily.time[dayIndex]) : new Date();
  const dayName = dayIndex === 0
    ? (currentLang === "hi" ? "आज" : currentLang === "bho" ? "आजु" : "Today")
    : dayIndex === 1
    ? (currentLang === "hi" ? "कल" : currentLang === "bho" ? "बिहाने" : "Tomorrow")
    : dayDate.toLocaleDateString(currentLang === "en" ? "en-US" : "hi-IN", { weekday: "long" });

  const dateText = dayDate.toLocaleDateString(currentLang === "en" ? "en-US" : "hi-IN", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });

  const badgeEl = document.getElementById("hourly-selected-day-badge");
  if (badgeEl) badgeEl.textContent = dayName;

  const titleEl = document.getElementById("hourly-selected-date-text");
  if (titleEl) {
    titleEl.textContent = `${dayName} - 24-Hour Detailed Breakdown (${dateText})`;
  }

  const maxT = Math.round(Math.max(...temps));
  const minT = Math.round(Math.min(...temps));
  const maxR = rains.length ? Math.max(...rains) : 0;
  const maxW = winds.length ? Math.round(Math.max(...winds)) : 0;
  const avgH = humids.length ? Math.round(humids.reduce((a, b) => a + b, 0) / humids.length) : 0;

  const metaEl = document.getElementById("hourly-meta-stats");
  if (metaEl) {
    metaEl.innerHTML = `
      <span class="meta-chip">🌡️ Range: <strong>${minT}°C - ${maxT}°C</strong></span>
      <span class="meta-chip">🌧️ Peak Rain: <strong>${maxR}%</strong></span>
      <span class="meta-chip">💨 Peak Wind: <strong>${maxW} km/h</strong></span>
      <span class="meta-chip">💧 Humidity: <strong>${avgH}%</strong></span>
    `;
  }

  let activeHour = 12;
  if (dayIndex === 0) {
    const curH = new Date().getHours();
    activeHour = curH >= 0 && curH < 24 ? curH : 12;
  }
  selectedHourIndex = activeHour;

  const timelineContainer = document.getElementById("hourly-timeline-container");
  if (timelineContainer) {
    timelineContainer.innerHTML = "";
    times.forEach((t, h) => {
      const card = document.createElement("div");
      card.className = `hourly-timeline-card ${h === activeHour ? "active" : ""}`;
      card.dataset.hour = h;

      const code = codes[h] !== undefined ? codes[h] : 0;
      const w = getWeatherInfo(code, currentLang);
      const isDay = h >= 6 && h < 19;
      const icon = (!isDay && w.theme === "clear") ? "🌙" : w.icon;
      const tempVal = Math.round(temps[h]);
      const rainVal = rains[h] !== undefined ? rains[h] : 0;
      const windVal = winds[h] !== undefined ? Math.round(winds[h]) : 0;
      const hourLabel = formatHourAmPm(h);

      card.innerHTML = `
        <div class="hc-time">${hourLabel}</div>
        <div class="hc-icon">${icon}</div>
        <div class="hc-temp">${tempVal}°C</div>
        <div class="hc-rain">💧 ${rainVal}%</div>
        <div class="hc-wind">💨 ${windVal}k</div>
      `;

      card.addEventListener("click", () => {
        timelineContainer.querySelectorAll(".hourly-timeline-card").forEach((c) => c.classList.remove("active"));
        card.classList.add("active");
        selectedHourIndex = h;
        updateHourlyPreview(dayIndex, h);
      });

      timelineContainer.appendChild(card);
    });

    setTimeout(() => {
      const activeCard = timelineContainer.querySelector(".hourly-timeline-card.active");
      if (activeCard) {
        activeCard.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
      }
    }, 60);
  }

  updateHourlyPreview(dayIndex, activeHour);
}

function updateHourlyPreview(dayIndex, hourIndex) {
  if (!weatherData || !weatherData.hourly) return;
  const hourly = weatherData.hourly;
  const idx = dayIndex * 24 + hourIndex;

  const temp = Math.round(hourly.temperature_2m[idx]);
  const feels = hourly.apparent_temperature ? Math.round(hourly.apparent_temperature[idx]) : temp;
  const rain = hourly.precipitation_probability ? hourly.precipitation_probability[idx] : 0;
  const wind = hourly.wind_speed_10m ? Math.round(hourly.wind_speed_10m[idx]) : 0;
  const code = hourly.weather_code ? hourly.weather_code[idx] : 0;
  const w = getWeatherInfo(code, currentLang);

  const isDay = hourIndex >= 6 && hourIndex < 19;
  let activeTheme = w.theme;
  let dynamicIcon = w.icon;

  if (!isDay) {
    if (w.theme === "clear") {
      activeTheme = "clear-night";
      dynamicIcon = "🌙";
    } else if (w.theme === "partcloud") {
      activeTheme = "partcloud-night";
      dynamicIcon = "☁️";
    }
  } else {
    if (w.theme === "clear") {
      dynamicIcon = "☀️";
    }
  }

  const previewBox = document.getElementById("hourly-weather-fx-preview");
  if (previewBox) {
    previewBox.className = `hourly-fx-preview weather-${activeTheme}`;
  }

  const iconEl = document.getElementById("hourly-preview-icon");
  if (iconEl) iconEl.textContent = dynamicIcon;

  const tempEl = document.getElementById("hourly-preview-temp");
  if (tempEl) tempEl.textContent = `${temp}°C`;

  const condEl = document.getElementById("hourly-preview-cond");
  const hourLabel = formatHourAmPm(hourIndex);
  if (condEl) {
    condEl.textContent = `${w.name} • ${hourLabel} • Feels ${feels}°C`;
  }

  const fxContainer = document.getElementById("hourly-banner-fx");
  const tagEl = document.getElementById("hourly-preview-dynamic-tag");

  let fxHtml = "";
  let tagText = "";

  const isMorningSunrise = isDay && hourIndex >= 6 && hourIndex <= 9;
  const hasStrongWind = wind >= 18;
  const hasRain = rain >= 40 || w.theme === "rainy" || w.theme === "drizzle";

  if (hasRain && hasStrongWind) {
    fxHtml = generateClouds(3, true) + generateDrops(28) + generateWindStreams(5);
    tagText = `🌧️ Wind-driven Rain Active (${wind} km/h, ${rain}% Rain)`;
  } else if (hasRain) {
    const dropCount = rain >= 70 ? 36 : 22;
    fxHtml = generateClouds(3, true) + generateDrops(dropCount);
    tagText = `🌧️ Rain Falling Animation Active (${rain}% Chance)`;
  } else if (hasStrongWind) {
    fxHtml = generateClouds(2, false) + generateWindStreams(6);
    tagText = `💨 Wind Stream Gusts Active (${wind} km/h Wind)`;
  } else if (w.theme === "thunder") {
    fxHtml = '<div class="wx-stormflash"></div>' + generateClouds(3, true) + generateDrops(28) + '<div class="wx-bolt" style="left:25%;">⚡</div><div class="wx-bolt" style="left:72%;animation-delay:1.5s;">⚡</div>';
    tagText = "⚡ Thunderstorm & Heavy Rain Active";
  } else if (w.theme === "snow") {
    fxHtml = generateClouds(2, false) + generateFlakes(24);
    tagText = "❄️ Snow Flurry Active";
  } else if (w.theme === "fog") {
    fxHtml = generateClouds(2, true) + '<div class="wx-fogband" style="top:25px;"></div><div class="wx-fogband" style="top:65px;"></div>';
    tagText = "🌫️ Fog Bands Active";
  } else if (isDay && (w.theme === "clear" || w.theme === "partcloud")) {
    if (isMorningSunrise) {
      fxHtml = '<div class="wx-sun wx-sunrise"></div>';
      if (w.theme === "partcloud") fxHtml += generateClouds(2, false);
      tagText = `🌅 Sun Rising Animation Active (${hourLabel})`;
    } else {
      fxHtml = '<div class="wx-sun"></div>';
      if (w.theme === "partcloud") fxHtml += generateClouds(2, false);
      tagText = `☀️ Radiant Sunlight Active (${hourLabel})`;
    }
  } else if (w.theme === "cloudy") {
    fxHtml = generateClouds(4, false);
    tagText = "☁️ Overcast Cloud Drift Active";
  } else {
    fxHtml = "";
    tagText = isDay ? `🌤️ Calm Sky (${wind} km/h)` : "🌙 Clear Night Sky";
  }

  if (fxContainer) fxContainer.innerHTML = fxHtml;
  if (tagEl) {
    tagEl.innerHTML = `<span class="hourly-fx-tag">${tagText}</span>`;
  }
}

function formatHourAmPm(h) {
  if (h === 0) return "12 AM";
  if (h === 12) return "12 PM";
  return h > 12 ? `${h - 12} PM` : `${h} AM`;
}

// ----------------- Interactive SVG Charts -----------------
function renderTemperatureChart(daily) {
  const container = document.getElementById("temp-chart-svg");
  if (!daily || !daily.temperature_2m_max) return;

  const maxs = daily.temperature_2m_max;
  const mins = daily.temperature_2m_min;
  const len = maxs.length;

  const w = 450;
  const h = 180;
  const padX = 35;
  const padY = 25;

  const allVals = [...maxs, ...mins];
  const minVal = Math.min(...allVals) - 2;
  const maxVal = Math.max(...allVals) + 2;
  const range = maxVal - minVal || 1;

  const getX = (idx) => padX + (idx / (len - 1)) * (w - 2 * padX);
  const getY = (val) => h - padY - ((val - minVal) / range) * (h - 2 * padY);

  let pathMax = "";
  let pathMin = "";
  let circles = "";

  for (let i = 0; i < len; i++) {
    const x = getX(i);
    const yMax = getY(maxs[i]);
    const yMin = getY(mins[i]);

    pathMax += `${i === 0 ? "M" : "L"} ${x} ${yMax} `;
    pathMin += `${i === 0 ? "M" : "L"} ${x} ${yMin} `;

    circles += `<circle cx="${x}" cy="${yMax}" r="4" fill="#ef4444" />
                <text x="${x}" y="${yMax - 8}" font-size="10" fill="#ef4444" font-weight="bold" text-anchor="middle">${maxs[i]}°</text>
                <circle cx="${x}" cy="${yMin}" r="4" fill="#3b82f6" />
                <text x="${x}" y="${yMin + 14}" font-size="10" fill="#3b82f6" font-weight="bold" text-anchor="middle">${mins[i]}°</text>`;
  }

  container.innerHTML = `
    <svg viewBox="0 0 ${w} ${h}">
      <path d="${pathMax}" fill="none" stroke="#ef4444" stroke-width="2.5" />
      <path d="${pathMin}" fill="none" stroke="#3b82f6" stroke-width="2.5" />
      ${circles}
    </svg>
  `;
}

function renderRainChart(daily) {
  const container = document.getElementById("rain-chart-svg");
  if (!daily || !daily.precipitation_probability_max) return;

  const probs = daily.precipitation_probability_max;
  const len = probs.length;

  const w = 450;
  const h = 180;
  const padX = 25;
  const padY = 30;
  const colW = (w - 2 * padX) / len - 10;

  let bars = "";

  probs.forEach((p, i) => {
    const x = padX + i * ((w - 2 * padX) / len) + 5;
    const barH = (p / 100) * (h - 2 * padY);
    const y = h - padY - barH;

    bars += `
      <rect x="${x}" y="${y}" width="${colW}" height="${barH}" rx="4" fill="#3b82f6" opacity="0.85" />
      <text x="${x + colW / 2}" y="${y - 6}" font-size="10" fill="#3b82f6" font-weight="bold" text-anchor="middle">${p}%</text>
    `;
  });

  container.innerHTML = `
    <svg viewBox="0 0 ${w} ${h}">
      ${bars}
    </svg>
  `;
}

// ----------------- Mode 2: Travel Packer -----------------
function renderTravelView() {
  if (!weatherData) return;
  const container = document.getElementById("packing-list-container");
  container.innerHTML = "";

  const current = weatherData.current || {};
  const daily = weatherData.daily || {};
  const dict = I18N[currentLang];

  const rainP = daily.precipitation_probability_max ? daily.precipitation_probability_max[0] : 0;
  const tMax = daily.temperature_2m_max ? daily.temperature_2m_max[0] : 25;
  const tMin = daily.temperature_2m_min ? daily.temperature_2m_min[0] : 15;
  const wind = current.wind_speed_10m || 0;

  const items = [];

  // Rain logic
  if (rainP > 60) {
    items.push({ text: dict.take_umbrella.replace("{p}", rainP), type: "warning", icon: "☂️" });
  } else {
    items.push({ text: dict.no_umbrella.replace("{p}", rainP), type: "success", icon: "☀️" });
  }

  // Heat / Cold logic
  if (tMax >= 35) {
    items.push({ text: dict.heat_pack, type: "warning", icon: "🧢" });
  }
  if (tMin <= 10) {
    items.push({ text: dict.cold_pack, type: "warning", icon: "🧥" });
  }
  if (wind >= 40) {
    items.push({ text: dict.wind_pack, type: "warning", icon: "💨" });
  }
  if (tMax < 35 && tMin > 10 && wind < 40) {
    items.push({ text: dict.normal_pack, type: "info", icon: "🎒" });
  }

  items.forEach((item) => {
    const el = document.createElement("div");
    el.className = `packing-item pack-${item.type}`;
    el.innerHTML = `<span>${item.icon}</span> <span>${item.text}</span>`;
    container.appendChild(el);
  });
}

// ----------------- Mode 3: Farmer Mode -----------------
function renderFarmerView() {
  if (!farmerData) return;
  const current = farmerData.current || {};
  const daily = farmerData.daily || {};

  document.getElementById("val-soil-temp").textContent = `${current.soil_temperature_6cm ?? "--"}°C`;
  document.getElementById("val-soil-moist").textContent = `${current.soil_moisture_3_9cm ?? "--"} m³/m³`;

  // Rainfall history
  const grid = document.getElementById("rain-history-container");
  grid.innerHTML = "";

  const pastDates = (daily.time || []).slice(0, 7);
  const pastRain = (daily.precipitation_sum || []).slice(0, 7);
  let totalRain = 0;

  pastDates.forEach((d, i) => {
    const rain = pastRain[i] || 0;
    totalRain += rain;
    const card = document.createElement("div");
    card.className = "rain-day-card";
    const dateObj = new Date(d);
    card.innerHTML = `
      <div class="date">${dateObj.toLocaleDateString("en-US", { weekday: "short" })}</div>
      <div class="val">${rain.toFixed(1)} mm</div>
    `;
    grid.appendChild(card);
  });

  // Advisory logic
  const nextProb = (daily.precipitation_probability_max || [])[daily.precipitation_probability_max.length - 1] || 0;
  const tMax = (daily.temperature_2m_max || [])[daily.temperature_2m_max.length - 1] || 30;

  let advisory = "";
  if (currentLang === "en") {
    advisory = `Total rain past 7 days: <strong>${totalRain.toFixed(1)} mm</strong>.<br/><br/>`;
    if (nextProb > 70) advisory += "⚠️ <strong>Heavy rain in 48h:</strong> Postpone chemical spraying, fertilizer application, and harvesting.<br/>";
    else if (nextProb < 20 && tMax > 35) advisory += "☀️ <strong>Hot and dry:</strong> Irrigate crops within 1-2 days and use mulch to conserve soil moisture.<br/>";
    else advisory += "✅ <strong>Good field conditions:</strong> Safe for normal intercultural operations. Spray chemicals in early morning or late evening.<br/>";
    if (totalRain > 50) advisory += "🚜 <strong>Soil is wet:</strong> Avoid running heavy tractors to prevent soil compaction and check field drainage.";
  } else if (currentLang === "hi") {
    advisory = `पिछले 7 दिनों में कुल बारिश: <strong>${totalRain.toFixed(1)} mm</strong>।<br/><br/>`;
    if (nextProb > 70) advisory += "⚠️ <strong>48 घंटे में भारी बारिश:</strong> कीटनाशक/खाद का छिड़काव रोकें और कटाई टालें।<br/>";
    else if (nextProb < 20 && tMax > 35) advisory += "☀️ <strong>सूखा और गर्मी:</strong> 1-2 दिन में सिंचाई करें और मिट्टी की नमी बनाए रखने के लिए मल्चिंग करें।<br/>";
    else advisory += "✅ <strong>खेत के काम के लिए अनुकूल:</strong> सामान्य जुताई-बुवाई जारी रखें। छिड़काव सुबह या शाम ही करें।<br/>";
    if (totalRain > 50) advisory += "🚜 <strong>खेत गीला है:</strong> भारी ट्रैक्टर चलाने से बचें और जल निकासी सुनिश्चित करें।";
  } else {
    advisory = `पिछला 7 दिन में कुल बरखा: <strong>${totalRain.toFixed(1)} mm</strong>।<br/><br/>`;
    if (nextProb > 70) advisory += "⚠️ <strong>48 घंटा में भारी बरखा:</strong> दवाई भा खाद के छिड़काव रोक दीं, कटाई टाल दीं।<br/>";
    else if (nextProb < 20 && tMax > 35) advisory += "☀️ <strong>घाम आ सूखा:</strong> 1-2 दिन में पटवन करीं आ माटी के नमी बचावे खातिर खर-पतवार ढंकीं।<br/>";
    else advisory += "✅ <strong>खेत के काम खातिर नीक समय:</strong> सामान्य काम चालू रखीं। दवाई बिहाने भा सांझे छिड़कीं।<br/>";
    if (totalRain > 50) advisory += "🚜 <strong>माटी भींजल बा:</strong> भारी ट्रैक्टर मत चलाईं आ खेत के नाली देख लीं।";
  }

  document.getElementById("farmer-advisory-text").innerHTML = advisory;
}

// ----------------- Mode 4: Morning Alerts -----------------
function renderAlertsView() {
  if (!weatherData) return;
  const current = weatherData.current || {};
  const daily = weatherData.daily || {};
  const dict = I18N[currentLang];

  const statusBox = document.getElementById("alerts-status-box");
  const listContainer = document.getElementById("alerts-list-container");
  listContainer.innerHTML = "";

  const alerts = [];
  const tMax = daily.temperature_2m_max ? daily.temperature_2m_max[0] : 25;
  const tMin = daily.temperature_2m_min ? daily.temperature_2m_min[0] : 15;
  const rainP = daily.precipitation_probability_max ? daily.precipitation_probability_max[0] : 0;
  const wind = current.wind_speed_10m || 0;
  const code = current.weather_code || 0;

  if (tMax >= 40) {
    alerts.push({ level: "high", text: `🔥 Heat Wave Warning: Today's maximum reaches ${tMax}°C. Avoid afternoon exposure.` });
  }
  if (tMin <= 5) {
    alerts.push({ level: "high", text: `❄️ Cold Wave Warning: Minimum temperature drops to ${tMin}°C tonight.` });
  }
  if ([95, 96, 99].includes(code)) {
    alerts.push({ level: "high", text: "⚡ Severe Thunderstorm Warning: Seek indoor shelter immediately." });
  }
  if (rainP >= 80) {
    alerts.push({ level: "medium", text: `🌧️ Heavy Rain Alert: ${rainP}% chance of precipitation today.` });
  }
  if (wind >= 50) {
    alerts.push({ level: "medium", text: `💨 Gale Wind Alert: Wind gusts up to ${wind} km/h.` });
  }

  if (alerts.length === 0) {
    statusBox.className = "alert-status-box pack-success";
    statusBox.textContent = `✅ ${dict.no_alert}`;
  } else {
    statusBox.className = "alert-status-box pack-warning";
    statusBox.textContent = `🚨 ${dict.has_alert}`;

    alerts.forEach((a) => {
      const item = document.createElement("div");
      item.className = `alert-item alert-${a.level}`;
      item.textContent = a.text;
      listContainer.appendChild(item);
    });
  }
}

// ----------------- Mode 5: Compare Places -----------------
async function handleCompareSubmit() {
  const input = document.getElementById("compare-input").value.trim();
  if (!input) return;

  const names = input.split(",").map((s) => s.trim()).filter((s) => s.length > 0).slice(0, 4);
  if (names.length === 0) return;

  const resultsDiv = document.getElementById("compare-results");
  const table = document.getElementById("compare-table");
  table.innerHTML = "<tr><th>Loading places...</th></tr>";
  resultsDiv.style.display = "block";

  const rows = [];
  for (const name of names) {
    try {
      const sRes = await fetch(`/api/suggest?q=${encodeURIComponent(name)}&limit=1`);
      const places = await sRes.json();
      if (!places || places.length === 0) throw new Error("Not found");
      const p = places[0];
      const wRes = await fetch(`/api/weather?lat=${p.latitude}&lon=${p.longitude}`);
      const wData = await wRes.json();
      const cur = wData.current || {};
      const d = wData.daily || {};

      rows.push({
        place: `${p.name} (${p.admin1 || ""})`,
        temp: cur.temperature_2m,
        feels: cur.apparent_temperature,
        condition: getWeatherInfo(cur.weather_code, currentLang).name,
        humidity: cur.relative_humidity_2m,
        wind: cur.wind_speed_10m,
        rainProb: d.precipitation_probability_max ? d.precipitation_probability_max[0] : 0,
        maxMin: `${d.temperature_2m_max ? d.temperature_2m_max[0] : "--"}° / ${d.temperature_2m_min ? d.temperature_2m_min[0] : "--"}°`,
      });
    } catch (e) {
      rows.push({ place: name, temp: "--", feels: "--", condition: "Not found", humidity: "--", wind: "--", rainProb: "--", maxMin: "--" });
    }
  }

  // Render Table
  let html = `
    <thead>
      <tr>
        <th>Place</th>
        <th>Temp (°C)</th>
        <th>Feels Like</th>
        <th>Condition</th>
        <th>Humidity</th>
        <th>Wind</th>
        <th>Rain %</th>
        <th>Max/Min</th>
      </tr>
    </thead>
    <tbody>
  `;
  rows.forEach((r) => {
    html += `
      <tr>
        <td><strong>${escapeHtml(r.place)}</strong></td>
        <td>${r.temp}°C</td>
        <td>${r.feels}°C</td>
        <td>${escapeHtml(r.condition)}</td>
        <td>${r.humidity}%</td>
        <td>${r.wind} km/h</td>
        <td>${r.rainProb}%</td>
        <td>${r.maxMin}</td>
      </tr>
    `;
  });
  html += "</tbody>";
  table.innerHTML = html;
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text || "";
  return div.innerHTML;
}
