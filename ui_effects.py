"""Dynamic weather-themed UI banners with pure CSS animations.
No external assets. Works inside Streamlit via st.markdown(unsafe_allow_html=True).

Themes:
  clear   -> shining sun + rotating rays
  partcloud -> sun + drifting clouds
  cloudy  -> grey drifting clouds
  fog     -> sliding fog bands
  drizzle -> light rain dots
  rain    -> heavy falling droplets + splash + clouds
  snow    -> falling snowflakes
  storm   -> dark sky + rain + lightning flash
"""

def get_theme(code: int) -> str:
    """Map WMO weather code to theme key."""
    try:
        code = int(code)
    except Exception:
        return "clear"
    if code in (0, 1):
        return "clear"
    if code == 2:
        return "partcloud"
    if code == 3:
        return "cloudy"
    if code in (45, 48):
        return "fog"
    if code in (51, 53, 55):
        return "drizzle"
    if code in (71, 73, 75, 77, 85, 86):
        return "snow"
    if code in (95, 96, 99):
        return "storm"
    # 61,63,65,80,81,82 + fallback
    if code in (61, 63, 65, 80, 81, 82):
        return "rain"
    return "clear"


THEME_STYLE = {
    "clear": {
        "bg": "linear-gradient(135deg,#1e90ff 0%,#4facfe 45%,#fef9c3 100%)",
        "emoji": "☀️",
        "label": "Clear / Sunny",
        "text": "#0f2a44",
    },
    "partcloud": {
        "bg": "linear-gradient(135deg,#7dd3fc 0%,#bae6fd 50%,#fef9c3 100%)",
        "emoji": "⛅",
        "label": "Partly Cloudy",
        "text": "#0f2a44",
    },
    "cloudy": {
        "bg": "linear-gradient(135deg,#64748b 0%,#94a3b8 55%,#cbd5e1 100%)",
        "emoji": "☁️",
        "label": "Cloudy",
        "text": "#0f172a",
    },
    "fog": {
        "bg": "linear-gradient(135deg,#94a3b8 0%,#cbd5e1 50%,#e2e8f0 100%)",
        "emoji": "🌫️",
        "label": "Fog",
        "text": "#1e293b",
    },
    "drizzle": {
        "bg": "linear-gradient(135deg,#334155 0%,#64748b 60%,#a5c4fc 100%)",
        "emoji": "🌦️",
        "label": "Drizzle",
        "text": "#ffffff",
    },
    "rain": {
        "bg": "linear-gradient(135deg,#0f172a 0%,#1e3a5f 55%,#2563eb 100%)",
        "emoji": "🌧️",
        "label": "Rainy",
        "text": "#ffffff",
    },
    "snow": {
        "bg": "linear-gradient(135deg,#475569 0%,#93c5fd 55%,#f8fafc 100%)",
        "emoji": "❄️",
        "label": "Snow",
        "text": "#0f172a",
    },
    "storm": {
        "bg": "linear-gradient(135deg,#020617 0%,#1e1b4b 50%,#4c1d95 100%)",
        "emoji": "⛈️",
        "label": "Storm",
        "text": "#ffffff",
    },
}

GLOBAL_CSS = """
<style>
.wx-banner{
  position:relative; overflow:hidden; border-radius:18px;
  padding:18px 20px; margin:10px 0 16px 0; min-height:170px;
  box-shadow:0 8px 28px rgba(0,0,0,.22);
  border:1px solid rgba(255,255,255,.35);
}
.wx-main{ position:relative; z-index:5; display:flex; align-items:center; gap:16px; }
.wx-emoji{ font-size:64px; line-height:1; filter:drop-shadow(0 4px 10px rgba(0,0,0,.3)); }
.wx-title{ font-size:26px; font-weight:800; margin:0; }
.wx-sub{ font-size:15px; opacity:.92; margin:2px 0 0 0; }
.wx-temp{ font-size:44px; font-weight:900; margin-left:auto; text-shadow:0 2px 12px rgba(0,0,0,.25); white-space:nowrap; }

/* ---- SUN ---- */
.wx-sun{
  position:absolute; top:18px; right:30px; width:84px; height:84px; z-index:2;
  background:radial-gradient(circle at 35% 35%, #fffde7, #ffeb3b 45%, #ff9800 75%, #f57c00);
  border-radius:50%; box-shadow:0 0 30px 12px rgba(255,235,59,.85), 0 0 80px 30px rgba(255,152,0,.45);
  animation:wx-spin-glow 6s ease-in-out infinite alternate;
}
.wx-sun::before{
  content:""; position:absolute; inset:-22px;
  background:repeating-conic-gradient(rgba(255,255,255,.85) 0 8deg, transparent 8deg 22deg);
  border-radius:50%; z-index:-1; animation:wx-rotate 18s linear infinite;
  -webkit-mask:radial-gradient(circle, transparent 58px, black 60px);
  mask:radial-gradient(circle, transparent 58px, black 60px);
}
@keyframes wx-rotate{ to{ transform:rotate(360deg);} }
@keyframes wx-spin-glow{ from{ transform:scale(1);} to{ transform:scale(1.08);} }

/* ---- CLOUDS ---- */
.wx-cloud{
  position:absolute; background:#fff; border-radius:50px; opacity:.95; z-index:3;
  box-shadow:0 6px 18px rgba(0,0,0,.18);
  animation:wx-drift linear infinite;
}
.wx-cloud::before,.wx-cloud::after{
  content:""; position:absolute; background:#fff; border-radius:50%;
}
.wx-cloud::before{ width:55%; height:140%; top:-70%; left:12%; }
.wx-cloud::after{ width:38%; height:95%; top:-45%; right:12%; }
@keyframes wx-drift{ from{ transform:translateX(-160px);} to{ transform:translateX(110%);} }

/* ---- RAIN ---- */
.wx-drop{
  position:absolute; top:-20px; width:3px; height:18px; z-index:4;
  background:linear-gradient(to bottom, rgba(255,255,255,0), #bae6fd 60%, #fff);
  border-radius:0 0 6px 6px; opacity:.9;
  animation:wx-fall linear infinite;
}
@keyframes wx-fall{ to{ transform:translateY(230px); } }

/* ---- SNOW ---- */
.wx-flake{ position:absolute; top:-24px; z-index:4; animation:wx-snow linear infinite; }
@keyframes wx-snow{
  0%{ transform:translate(0,-10px) rotate(0deg); opacity:0; }
  10%{ opacity:1; }
  100%{ transform:translate(-60px,230px) rotate(320deg); opacity:.9; }
}

/* ---- FOG ---- */
.wx-fogband{
  position:absolute; left:-20%; width:140%; height:26px; z-index:3;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.85) 20%,rgba(255,255,255,.85) 80%,transparent);
  filter:blur(6px); border-radius:20px; opacity:.8;
  animation:wx-fogslide ease-in-out infinite alternate;
}
@keyframes wx-fogslide{ from{ transform:translateX(-40px);} to{ transform:translateX(40px);} }

/* ---- STORM ---- */
.wx-bolt{
  position:absolute; top:8px; font-size:54px; z-index:5;
  animation:wx-flash 2.8s steps(1) infinite;
  filter:drop-shadow(0 0 14px #fde047);
}
@keyframes wx-flash{
  0%,52%,58%,100%{ opacity:0; transform:scale(1); }
  54%,56%{ opacity:1; transform:scale(1.12); }
}
.wx-stormflash{
  position:absolute; inset:0; z-index:1; pointer-events:none;
  background:#fef08a; opacity:0; animation:wx-skyflash 2.8s steps(1) infinite;
}
@keyframes wx-skyflash{ 0%,53%,57%,100%{opacity:0;} 54%,56%{opacity:.35;} }

/* metric cards polish */
div[data-testid="stMetric"]{
  background:rgba(255,255,255,.75); border-radius:14px; padding:10px 12px;
  border:1px solid rgba(0,0,0,.06); box-shadow:0 2px 10px rgba(0,0,0,.06);
}
</style>
"""


def _drops(n=28, cls="wx-drop", extra="") -> str:
    import random
    random.seed(7)
    out = []
    for i in range(n):
        left = random.randint(2, 98)
        delay = round(random.uniform(0, 1.6), 2)
        dur = round(random.uniform(0.6, 1.3), 2)
        h = random.randint(12, 24)
        out.append(
            f'<div class="{cls}" style="left:{left}%;animation-delay:{delay}s;'
            f'animation-duration:{dur}s;height:{h}px;{extra}"></div>'
        )
    return "".join(out)


def _clouds(n=3, dark=False) -> str:
    import random
    random.seed(11)
    out = []
    for i in range(n):
        top = [18, 55, 95][i % 3]
        w = random.randint(90, 150)
        dur = random.randint(18, 38)
        delay = random.randint(-20, 0)
        op = 0.55 if dark else 0.95
        bg = "#cbd5e1" if dark else "#ffffff"
        out.append(
            f'<div class="wx-cloud" style="top:{top}px;width:{w}px;height:{w//3}px;'
            f'background:{bg};opacity:{op};animation-duration:{dur}s;'
            f'animation-delay:{delay}s;"></div>'
        )
    return "".join(out)


def _flakes(n=24) -> str:
    import random
    random.seed(21)
    out = []
    for _ in range(n):
        left = random.randint(2, 98)
        delay = round(random.uniform(0, 2.5), 2)
        dur = round(random.uniform(2.2, 4.5), 2)
        size = random.randint(12, 24)
        out.append(
            f'<div class="wx-flake" style="left:{left}%;font-size:{size}px;'
            f'animation-delay:{delay}s;animation-duration:{dur}s;">❄</div>'
        )
    return "".join(out)


def banner_html(code: int, temp_c=None, cond_name: str = "", place: str = "") -> str:
    """Full banner HTML for a WMO code."""
    theme = get_theme(code)
    s = THEME_STYLE[theme]
    fx = ""
    if theme == "clear":
        fx = '<div class="wx-sun"></div>'
    elif theme == "partcloud":
        fx = '<div class="wx-sun" style="width:64px;height:64px;"></div>' + _clouds(3)
    elif theme == "cloudy":
        fx = _clouds(4, dark=False)
    elif theme == "fog":
        fx = (_clouds(2, dark=True)
              + '<div class="wx-fogband" style="top:60px;animation-duration:5s;"></div>'
              + '<div class="wx-fogband" style="top:95px;animation-duration:7s;"></div>'
              + '<div class="wx-fogband" style="top:128px;animation-duration:6s;"></div>')
    elif theme == "drizzle":
        fx = _clouds(2) + _drops(16)
    elif theme == "rain":
        fx = _clouds(2, dark=True) + _drops(34)
    elif theme == "snow":
        fx = _clouds(2) + _flakes(26)
    elif theme == "storm":
        fx = ('<div class="wx-stormflash"></div>'
              + _clouds(3, dark=True) + _drops(30)
              + '<div class="wx-bolt" style="left:22%;">⚡</div>'
              + '<div class="wx-bolt" style="left:68%;animation-delay:1.4s;">⚡</div>')

    temp_txt = f"{temp_c}°C" if temp_c is not None else ""
    sub = " • ".join([x for x in [place, cond_name or s["label"]] if x])

    return f"""
<div class="wx-banner" style="background:{s['bg']};color:{s['text']};">
  {fx}
  <div class="wx-main">
    <div class="wx-emoji">{s['emoji']}</div>
    <div>
      <p class="wx-title">{s['label']}</p>
      <p class="wx-sub">{sub}</p>
    </div>
    <div class="wx-temp">{temp_txt}</div>
  </div>
</div>
"""
