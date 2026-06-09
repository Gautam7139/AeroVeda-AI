import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
from groq import Groq
import math

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Aeroveda — Agricultural Intelligence",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Design System ────────────────────────────────────────────────────────────
# Palette: Deep forest night + bioluminescent greens + warm soil amber
# Typography: Space Grotesk (data/utility) + Fraunces (organic display)
# Signature: Hexagonal score rings + living grid background

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,700;1,9..144,400&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"], .stApp {
    font-family: 'Space Grotesk', sans-serif;
    background: #050e08 !important;
    color: #c8e6c3;
}

/* ── Living Grid Background ── */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(34,197,94,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(34,197,94,0.04) 1px, transparent 1px);
    background-size: 48px 48px;
    pointer-events: none;
    z-index: 0;
}

/* ── Ambient glow orbs ── */
.stApp::after {
    content: '';
    position: fixed;
    top: -20%;
    right: -10%;
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(34,197,94,0.06) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}

.main .block-container {
    padding: 0 2rem 4rem 2rem !important;
    max-width: 1400px !important;
    position: relative;
    z-index: 1;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(5,14,8,0.98) !important;
    border-right: 1px solid rgba(34,197,94,0.12) !important;
}
[data-testid="stSidebar"] .block-container { padding: 2rem 1.5rem !important; }

/* ── Masthead ── */
.av-masthead {
    padding: 3rem 0 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid rgba(34,197,94,0.1);
    margin-bottom: 2rem;
}
.av-wordmark {
    font-family: 'Fraunces', serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: #f0fdf4;
    letter-spacing: -0.02em;
    line-height: 1;
}
.av-wordmark span {
    color: #22c55e;
}
.av-tagline {
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #4ade80;
    margin-top: 4px;
    font-weight: 500;
}
.av-location-pill {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(34,197,94,0.08);
    border: 1px solid rgba(34,197,94,0.2);
    border-radius: 999px;
    padding: 0.5rem 1.2rem;
    font-size: 0.85rem;
    color: #86efac;
}
.av-location-pill .dot {
    width: 7px; height: 7px;
    background: #22c55e;
    border-radius: 50%;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.8); }
}

/* ── Hex Score Ring ── */
.hex-score-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.6rem;
}
.hex-ring {
    position: relative;
    width: 120px; height: 120px;
}
.hex-ring svg { width: 120px; height: 120px; }
.hex-ring .ring-val {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
}
.hex-ring .ring-val .num {
    font-family: 'Fraunces', serif;
    font-size: 2rem;
    font-weight: 700;
    line-height: 1;
    color: #f0fdf4;
}
.hex-ring .ring-val .lbl {
    font-size: 0.6rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #6ee7b7;
    margin-top: 2px;
}
.hex-score-title {
    font-size: 0.7rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #6ee7b7;
    text-align: center;
}
.hex-score-grade {
    font-family: 'Fraunces', serif;
    font-size: 0.9rem;
    font-weight: 700;
    text-align: center;
}

/* ── Data Panels ── */
.av-panel {
    background: rgba(10,26,15,0.8);
    border: 1px solid rgba(34,197,94,0.12);
    border-radius: 16px;
    padding: 1.4rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(8px);
    position: relative;
    overflow: hidden;
}
.av-panel::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(34,197,94,0.3), transparent);
}
.av-panel-label {
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #4ade80;
    margin-bottom: 0.3rem;
    font-weight: 600;
}
.av-panel-value {
    font-family: 'Fraunces', serif;
    font-size: 2rem;
    font-weight: 700;
    color: #f0fdf4;
    line-height: 1.1;
}
.av-panel-unit {
    font-size: 0.8rem;
    color: #6ee7b7;
    margin-left: 3px;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 400;
}
.av-panel-sub {
    font-size: 0.75rem;
    color: #4ade80;
    margin-top: 4px;
}

/* ── Section Header ── */
.av-section {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 2.5rem 0 1.2rem;
}
.av-section-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(34,197,94,0.3), transparent);
}
.av-section-label {
    font-size: 0.68rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #22c55e;
    font-weight: 600;
    white-space: nowrap;
}
.av-section-icon { font-size: 1rem; }

/* ── Pollutant Bar ── */
.pol-row { margin-bottom: 1rem; }
.pol-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 5px;
}
.pol-name {
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #86efac;
    font-weight: 500;
}
.pol-val {
    font-family: 'Fraunces', serif;
    font-size: 0.9rem;
    font-weight: 700;
}
.pol-track {
    height: 6px;
    background: rgba(255,255,255,0.06);
    border-radius: 99px;
    overflow: hidden;
}
.pol-fill {
    height: 6px;
    border-radius: 99px;
    transition: width 0.6s cubic-bezier(.4,0,.2,1);
}

/* ── Alert Cards ── */
.av-alert {
    display: flex;
    gap: 12px;
    align-items: flex-start;
    padding: 1rem 1.2rem;
    border-radius: 12px;
    margin-bottom: 0.6rem;
}
.av-alert-crisis {
    background: rgba(239,68,68,0.08);
    border: 1px solid rgba(239,68,68,0.25);
}
.av-alert-warning {
    background: rgba(234,179,8,0.07);
    border: 1px solid rgba(234,179,8,0.2);
}
.av-alert-safe {
    background: rgba(34,197,94,0.07);
    border: 1px solid rgba(34,197,94,0.2);
}
.av-alert-icon { font-size: 1.2rem; flex-shrink: 0; margin-top: 1px; }
.av-alert-body { flex: 1; }
.av-alert-title {
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    font-weight: 700;
    margin-bottom: 3px;
}
.av-alert-crisis .av-alert-title { color: #fca5a5; }
.av-alert-warning .av-alert-title { color: #fde047; }
.av-alert-safe .av-alert-title { color: #86efac; }
.av-alert-msg {
    font-size: 0.82rem;
    line-height: 1.5;
}
.av-alert-crisis .av-alert-msg { color: #fecaca; }
.av-alert-warning .av-alert-msg { color: #fef08a; }
.av-alert-safe .av-alert-msg { color: #bbf7d0; }

/* ── Crop Cards ── */
.crop-item {
    display: flex;
    gap: 1rem;
    align-items: center;
    padding: 1rem 1.2rem;
    background: rgba(10,26,15,0.6);
    border: 1px solid rgba(34,197,94,0.1);
    border-radius: 14px;
    margin-bottom: 0.6rem;
    transition: border-color 0.2s;
}
.crop-item:hover { border-color: rgba(34,197,94,0.35); }
.crop-emoji { font-size: 2rem; flex-shrink: 0; }
.crop-info { flex: 1; }
.crop-name-text {
    font-family: 'Fraunces', serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #f0fdf4;
}
.crop-reason { font-size: 0.78rem; color: #86efac; margin-top: 2px; }
.crop-care { font-size: 0.73rem; color: #4ade80; margin-top: 4px; }
.crop-compat {
    text-align: center;
    flex-shrink: 0;
}
.crop-compat .pct {
    font-family: 'Fraunces', serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: #22c55e;
    line-height: 1;
}
.crop-compat .pct-lbl {
    font-size: 0.6rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #4ade80;
}

/* ── Chat ── */
.chat-msg {
    padding: 0.8rem 1.1rem;
    border-radius: 14px;
    margin-bottom: 0.6rem;
    font-size: 0.85rem;
    line-height: 1.6;
    max-width: 88%;
}
.chat-user {
    background: rgba(34,197,94,0.12);
    border: 1px solid rgba(34,197,94,0.2);
    color: #d1fae5;
    margin-left: auto;
    border-radius: 14px 14px 4px 14px;
    text-align: right;
}
.chat-ai {
    background: rgba(10,26,15,0.8);
    border: 1px solid rgba(34,197,94,0.1);
    color: #c8e6c3;
    border-radius: 14px 14px 14px 4px;
}
.chat-label {
    font-size: 0.62rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-bottom: 4px;
    font-weight: 600;
}
.chat-user .chat-label { color: #4ade80; text-align: right; }
.chat-ai .chat-label { color: #22c55e; }

/* ── AI Output Box ── */
.av-ai-output {
    background: rgba(5,14,8,0.9);
    border: 1px solid rgba(34,197,94,0.18);
    border-radius: 16px;
    padding: 1.5rem;
    color: #c8e6c3;
    line-height: 1.8;
    font-size: 0.88rem;
    position: relative;
}
.av-ai-output::before {
    content: 'AI ANALYSIS';
    position: absolute;
    top: -10px; left: 20px;
    background: #050e08;
    padding: 0 8px;
    font-size: 0.6rem;
    letter-spacing: 0.2em;
    color: #22c55e;
    font-weight: 700;
}

/* ── Forecast Table ── */
.stDataFrame { border-radius: 12px !important; overflow: hidden; }
[data-testid="stDataFrameResizable"] {
    border: 1px solid rgba(34,197,94,0.12) !important;
    border-radius: 12px !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(34,197,94,0.12) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: #4ade80 !important;
    padding: 0.8rem 1.5rem !important;
    background: transparent !important;
    border: none !important;
    font-weight: 500 !important;
}
.stTabs [aria-selected="true"] {
    color: #f0fdf4 !important;
    border-bottom: 2px solid #22c55e !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding: 1.5rem 0 0 !important;
    background: transparent !important;
}

/* ── Inputs ── */
.stTextInput input {
    background: rgba(10,26,15,0.8) !important;
    border: 1px solid rgba(34,197,94,0.2) !important;
    border-radius: 10px !important;
    color: #f0fdf4 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 1rem !important;
}
.stTextInput input:focus {
    border-color: rgba(34,197,94,0.5) !important;
    box-shadow: 0 0 0 3px rgba(34,197,94,0.08) !important;
}
.stTextInput label {
    color: #6ee7b7 !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    font-weight: 600 !important;
}

/* ── Buttons ── */
.stButton button {
    background: rgba(34,197,94,0.1) !important;
    border: 1px solid rgba(34,197,94,0.3) !important;
    color: #4ade80 !important;
    border-radius: 10px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}
.stButton button:hover {
    background: rgba(34,197,94,0.2) !important;
    border-color: rgba(34,197,94,0.5) !important;
    color: #f0fdf4 !important;
}
button[kind="primary"] {
    background: linear-gradient(135deg, #15803d, #22c55e) !important;
    border: none !important;
    color: #052e16 !important;
    font-weight: 700 !important;
}

/* ── Selectbox ── */
.stSelectbox select, [data-baseweb="select"] {
    background: rgba(10,26,15,0.8) !important;
    border-color: rgba(34,197,94,0.2) !important;
    color: #f0fdf4 !important;
}
[data-baseweb="select"] > div {
    background: rgba(10,26,15,0.9) !important;
    border-color: rgba(34,197,94,0.2) !important;
    color: #f0fdf4 !important;
    border-radius: 10px !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: #22c55e !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(34,197,94,0.2); border-radius: 99px; }

/* ── Chat input ── */
[data-testid="stChatInput"] textarea {
    background: rgba(10,26,15,0.9) !important;
    border: 1px solid rgba(34,197,94,0.2) !important;
    color: #f0fdf4 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    border-radius: 12px !important;
}
[data-testid="stChatInputSubmitButton"] {
    color: #22c55e !important;
}

/* ── Nav tabs label fix ── */
.stTabs [data-baseweb="tab"] p {
    font-size: 0.75rem !important;
    letter-spacing: 0.12em !important;
}

/* hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─── Groq ────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_groq_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

def ask_groq(prompt, system="You are a helpful agricultural expert.", max_tokens=1000):
    try:
        client = get_groq_client()
        r = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=max_tokens,
            messages=[{"role":"system","content":system},{"role":"user","content":prompt}]
        )
        return r.choices[0].message.content
    except Exception as e:
        return f"AI error: {str(e)}"

def ask_groq_chat(messages, system, max_tokens=700):
    try:
        client = get_groq_client()
        r = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=max_tokens,
            messages=[{"role":"system","content":system}] + messages
        )
        return r.choices[0].message.content
    except Exception as e:
        return f"AI error: {str(e)}"

# ─── Data Fetchers ────────────────────────────────────────────────────────────
@st.cache_data(ttl=1800)
def fetch_weather(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
        f"precipitation,rain,wind_speed_10m,wind_direction_10m,"
        f"surface_pressure,cloud_cover,uv_index,weather_code"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,"
        f"wind_speed_10m_max,uv_index_max,precipitation_probability_max"
        f"&forecast_days=7&timezone=auto"
    )
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Weather data unavailable: {e}")
        return None

@st.cache_data(ttl=1800)
def fetch_air_quality(lat, lon):
    url = (
        f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}"
        f"&current=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,european_aqi,us_aqi"
    )
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        return r.json()
    except:
        return None

@st.cache_data(ttl=3600)
def geocode_city(city):
    try:
        r = requests.get(
            f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json",
            timeout=10
        )
        data = r.json()
        if data.get("results"):
            res = data["results"][0]
            return res["latitude"], res["longitude"], res.get("country","")
        return None
    except:
        return None

# ─── Intelligence Engine ──────────────────────────────────────────────────────
def compute_weather_score(w):
    c = w["current"]
    s = 100
    t = c["temperature_2m"]; h = c["relative_humidity_2m"]
    wnd = c["wind_speed_10m"]; uv = c.get("uv_index",0) or 0
    pr = c.get("precipitation",0) or 0
    if t>40 or t<0: s-=25
    elif t>35 or t<5: s-=12
    if h>90 or h<15: s-=15
    elif h>80 or h<25: s-=7
    if wnd>60: s-=20
    elif wnd>35: s-=8
    if uv>10: s-=15
    elif uv>7: s-=6
    if pr>20: s-=15
    elif pr>5: s-=4
    return max(0,min(100,s))

def compute_pollution_score(aq):
    if not aq: return None
    aqi = aq.get("current",{}).get("european_aqi") or aq.get("current",{}).get("us_aqi")
    if aqi is None: return None
    return max(0, min(100, round(100 - aqi)))

def compute_env_score(ws, ps):
    if ps is None: return ws
    return max(0, min(100, round(ws*0.55 + ps*0.45)))

def score_grade(s):
    if s>=80: return "#22c55e","OPTIMAL"
    elif s>=65: return "#4ade80","GOOD"
    elif s>=45: return "#facc15","MODERATE"
    elif s>=25: return "#fb923c","STRESSED"
    else: return "#ef4444","CRITICAL"

def bar_color(val, good, bad):
    if val<=good: return "#22c55e"
    elif val<=bad: return "#facc15"
    else: return "#ef4444"

def predict_crises(w, aq_cur):
    alerts = []
    daily = w["daily"]
    if aq_cur:
        aqi = aq_cur.get("european_aqi") or aq_cur.get("us_aqi")
        if aqi and aqi>80:
            alerts.append(("crisis","AIR QUALITY CRISIS",f"AQI {aqi} — Hazardous pollution detected. Severe agricultural and health risk."))
        elif aqi and aqi>50:
            alerts.append(("warning","POLLUTION ADVISORY",f"AQI {aqi} — Degraded air quality. Sensitive crops may show stress."))
    hot = sum(1 for t in daily["temperature_2m_max"] if t and t>38)
    if hot>=3: alerts.append(("crisis","HEAT WAVE",f"{hot} consecutive days above 38°C forecast. High crop stress probability."))
    elif hot>=1: alerts.append(("warning","HEAT ADVISORY",f"{hot} day(s) above 38°C. Monitor soil moisture closely."))
    rain_total = sum(p for p in daily["precipitation_sum"] if p is not None)
    if rain_total<2: alerts.append(("crisis","DROUGHT RISK","Near-zero rainfall over 7-day window. Activate irrigation systems immediately."))
    elif rain_total<8: alerts.append(("warning","LOW RAINFALL","Minimal precipitation forecast. Schedule supplemental irrigation."))
    heavy = sum(1 for p in daily["precipitation_sum"] if p and p>25)
    if heavy>=2: alerts.append(("crisis","FLOOD PROBABILITY",f"{heavy} high-rainfall days forecast. Waterlogging risk is severe."))
    elif heavy==1: alerts.append(("warning","HEAVY RAIN ALERT","One day of intense rainfall. Ensure drainage channels are clear."))
    max_w = max((v for v in daily["wind_speed_10m_max"] if v), default=0)
    if max_w>70: alerts.append(("crisis","STORM WARNING",f"Gusts up to {max_w:.0f} km/h forecast. Secure all crop structures."))
    elif max_w>45: alerts.append(("warning","HIGH WIND","Wind speeds up to {:.0f} km/h expected.".format(max_w)))
    if not alerts:
        alerts.append(("safe","CONDITIONS STABLE","No significant environmental crises detected in the 7-day forecast window."))
    return alerts

def recommend_crops(w):
    c = w["current"]
    t = c["temperature_2m"]; h = c["relative_humidity_2m"]
    pl = [p for p in w["daily"]["precipitation_sum"] if p is not None]
    ar = sum(pl)/len(pl) if pl else 0
    crops=[]
    if 20<=t<=38 and h>50:
        crops.append(("🌾","Rice",95,"Optimal temperature-humidity matrix","High water demand · 3–4 month cycle · transplant at 21 days"))
        crops.append(("🌿","Sugarcane",88,"Strong heat-humidity compatibility","Weekly deep irrigation · monthly NPK · 10–12 month cycle"))
    if 18<=t<=35:
        crops.append(("🥜","Groundnut",85,"Temperature range aligned","Well-drained sandy loam · dry finish period required"))
        crops.append(("🌽","Maize",82,"Thermophilic growth conditions met","Moderate water · high nitrogen · 90-day fast cycle"))
    if t>=25 and h<70:
        crops.append(("🍅","Tomato",78,"Warm-dry conditions ideal","Consistent drip · stake support · blight monitoring"))
        crops.append(("🌶️","Chilli",76,"Low humidity reduces fungal risk","Potassium-rich feed · drip irrigation preferred"))
    if t<22:
        crops.append(("🥬","Spinach",90,"Cool temperature threshold optimal","Direct sow · 6–8 week harvest · nitrogen feed"))
        crops.append(("🥕","Carrot",84,"Root development favoured by cool soil","Deep loose bed · thin at 4cm · 70-day crop"))
        crops.append(("🧅","Onion",80,"Bulb initiation suits cool dry air","Reduce water at bulbing · well-drained raised bed"))
    if ar<3 and t>20:
        crops.append(("🌻","Sunflower",88,"Drought-tolerance profile matches","Deep taproot · minimal input · 80–95 days"))
        crops.append(("🫘","Moong Dal",83,"Short season drought-tolerant legume","Sandy loam · fixes nitrogen · 60–70 day cycle"))
    crops.sort(key=lambda x:-x[2])
    return crops[:5]

WMO={0:"Clear sky",1:"Mainly clear",2:"Partly cloudy",3:"Overcast",
     45:"Fog",51:"Light drizzle",53:"Drizzle",55:"Heavy drizzle",
     61:"Slight rain",63:"Moderate rain",65:"Heavy rain",
     80:"Showers",81:"Moderate showers",82:"Violent showers",
     95:"Thunderstorm",96:"Thunderstorm + hail"}

def wdesc(code): return WMO.get(code,"—")

# ─── SVG Ring Helper ──────────────────────────────────────────────────────────
def ring_svg(score, color, size=120, stroke=8):
    r = (size/2) - stroke
    circ = 2 * math.pi * r
    dash = (score/100) * circ
    return f"""
<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
  <circle cx="{size/2}" cy="{size/2}" r="{r}"
    fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="{stroke}"/>
  <circle cx="{size/2}" cy="{size/2}" r="{r}"
    fill="none" stroke="{color}" stroke-width="{stroke}"
    stroke-linecap="round"
    stroke-dasharray="{dash:.1f} {circ:.1f}"
    transform="rotate(-90 {size/2} {size/2})"/>
</svg>"""

# ════════════════════════════════════════════════════════════════
# SIDEBAR — City Input
# ════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="font-size:0.65rem;letter-spacing:0.22em;text-transform:uppercase;
         color:#22c55e;font-weight:700;margin-bottom:1.2rem">
        ◈ Location Intelligence
    </div>
    """, unsafe_allow_html=True)

    city = st.text_input(
        "Farm Location",
        value=st.session_state.get("city","Bengaluru"),
        placeholder="City or region..."
    )
    st.session_state["city"] = city

    st.markdown("""
    <div style="margin-top:2rem;padding-top:1.5rem;border-top:1px solid rgba(34,197,94,0.1)">
    <div style="font-size:0.62rem;letter-spacing:0.18em;text-transform:uppercase;
         color:#22c55e;font-weight:600;margin-bottom:0.8rem">Data Network</div>
    <div style="font-size:0.78rem;color:#6ee7b7;line-height:2">
    ◦ Open-Meteo Weather API<br>
    ◦ Open-Meteo Air Quality<br>
    ◦ Groq · LLaMA 3.3 70B<br>
    ◦ Nominatim Geocoding
    </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:2rem;padding-top:1.5rem;border-top:1px solid rgba(34,197,94,0.1)">
    <div style="font-size:0.62rem;letter-spacing:0.18em;text-transform:uppercase;
         color:#22c55e;font-weight:600;margin-bottom:0.6rem">About</div>
    <div style="font-size:0.75rem;color:#6ee7b7;line-height:1.7">
    Aeroveda is an AI-driven agricultural intelligence platform. Environmental data converted into actionable farming decisions.
    </div>
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# FETCH DATA
# ════════════════════════════════════════════════════════════════
geo = geocode_city(city)
if not geo:
    st.error(f"Location '{city}' not found. Try a different city name.")
    st.stop()

lat, lon, country = geo
weather = fetch_weather(lat, lon)
if not weather: st.stop()

aq       = fetch_air_quality(lat, lon)
cur      = weather["current"]
daily    = weather["daily"]
aq_cur   = aq.get("current",{}) if aq else {}
ws       = compute_weather_score(weather)
ps       = compute_pollution_score(aq)
es       = compute_env_score(ws, ps)

# ════════════════════════════════════════════════════════════════
# MASTHEAD
# ════════════════════════════════════════════════════════════════
col_logo, col_loc = st.columns([1,1])
with col_logo:
    st.markdown("""
    <div class="av-masthead" style="border:none;padding:2rem 0 1rem">
        <div>
            <div class="av-wordmark">Aero<span>veda</span></div>
            <div class="av-tagline">Agricultural Intelligence Platform</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_loc:
    st.markdown(f"""
    <div style="display:flex;justify-content:flex-end;align-items:center;height:100%;padding-top:2rem">
        <div class="av-location-pill">
            <div class="dot"></div>
            <span>{city.title()}, {country} &nbsp;·&nbsp; {lat:.2f}°N {lon:.2f}°E &nbsp;·&nbsp; {wdesc(cur['weather_code'])}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div style="height:1px;background:linear-gradient(90deg,rgba(34,197,94,0.3),transparent);margin-bottom:2rem"></div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# SCORE TRINITY
# ════════════════════════════════════════════════════════════════
def score_card(score, title, subtitle, size=110):
    val = score if score is not None else 0
    color, grade = score_grade(val)
    svg = ring_svg(val, color, size)
    display = str(score) if score is not None else "—"
    return f"""
<div class="hex-score-wrap">
    <div class="hex-ring">
        {svg}
        <div class="ring-val">
            <div class="num">{display}</div>
        </div>
    </div>
    <div class="hex-score-title">{title}</div>
    <div class="hex-score-grade" style="color:{color}">{grade}</div>
    <div style="font-size:0.65rem;color:#4ade80;text-align:center;margin-top:2px">{subtitle}</div>
</div>"""

s1, s2, s3, s4 = st.columns(4)
with s1:
    st.markdown(f"""
    <div class="av-panel" style="text-align:center;padding:1.8rem 1rem">
        {score_card(ps, "POLLUTION SCORE", "Higher = Cleaner")}
    </div>""", unsafe_allow_html=True)
with s2:
    st.markdown(f"""
    <div class="av-panel" style="text-align:center;padding:1.8rem 1rem">
        {score_card(ws, "WEATHER SCORE", "Temp · Wind · UV · Rain")}
    </div>""", unsafe_allow_html=True)
with s3:
    st.markdown(f"""
    <div class="av-panel" style="text-align:center;padding:1.8rem 1rem">
        {score_card(es, "ENV SCORE", "55% Weather + 45% Air")}
    </div>""", unsafe_allow_html=True)
with s4:
    # Ag potential = blend of env score + crop suitability proxy
    ag_score = max(0, min(100, round(es * 0.7 + ws * 0.3)))
    st.markdown(f"""
    <div class="av-panel" style="text-align:center;padding:1.8rem 1rem;border-color:rgba(34,197,94,0.3)">
        {score_card(ag_score, "AG POTENTIAL", "Overall Farm Suitability")}
    </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "◈ Environment",
    "⚠ Crisis Intelligence",
    "◈ Crop Advisor",
    "◈ Farm Simulation",
    "◈ Field Assistant"
])

# ══════════════════════════════════════════════════════════════
# TAB 1 — ENVIRONMENT
# ══════════════════════════════════════════════════════════════
with tab1:

    # ── Weather Grid ──
    st.markdown("""
    <div class="av-section">
        <div class="av-section-icon">⛅</div>
        <div class="av-section-label">Live Atmospheric Conditions</div>
        <div class="av-section-line"></div>
    </div>
    """, unsafe_allow_html=True)

    w1,w2,w3,w4,w5,w6 = st.columns(6)
    for col, lbl, val, unit in [
        (w1,"Temperature",f"{cur['temperature_2m']:.1f}","°C"),
        (w2,"Humidity",f"{cur['relative_humidity_2m']}","%"),
        (w3,"Wind",f"{cur['wind_speed_10m']:.1f}","km/h"),
        (w4,"Precip",f"{cur['precipitation']:.1f}","mm"),
        (w5,"UV Index",f"{cur.get('uv_index',0) or 0:.0f}",""),
        (w6,"Feels Like",f"{cur['apparent_temperature']:.1f}","°C"),
    ]:
        with col:
            st.markdown(f"""
<div class="av-panel">
    <div class="av-panel-label">{lbl}</div>
    <div><span class="av-panel-value">{val}</span><span class="av-panel-unit">{unit}</span></div>
</div>""", unsafe_allow_html=True)

    w7,w8,w9 = st.columns(3)
    with w7:
        st.markdown(f"""
<div class="av-panel">
    <div class="av-panel-label">Cloud Cover</div>
    <div><span class="av-panel-value">{cur['cloud_cover']}</span><span class="av-panel-unit">%</span></div>
</div>""", unsafe_allow_html=True)
    with w8:
        st.markdown(f"""
<div class="av-panel">
    <div class="av-panel-label">Surface Pressure</div>
    <div><span class="av-panel-value">{cur['surface_pressure']:.0f}</span><span class="av-panel-unit">hPa</span></div>
</div>""", unsafe_allow_html=True)
    with w9:
        st.markdown(f"""
<div class="av-panel">
    <div class="av-panel-label">Wind Direction</div>
    <div><span class="av-panel-value">{cur['wind_direction_10m']:.0f}</span><span class="av-panel-unit">°</span></div>
    <div class="av-panel-sub">Updated {datetime.now().strftime('%H:%M')}</div>
</div>""", unsafe_allow_html=True)

    # ── Air Quality ──
    st.markdown("""
    <div class="av-section">
        <div class="av-section-icon">💨</div>
        <div class="av-section-label">Air Quality Matrix</div>
        <div class="av-section-line"></div>
    </div>
    """, unsafe_allow_html=True)

    if aq_cur:
        pm25  = float(aq_cur.get("pm2_5",0) or 0)
        pm10  = float(aq_cur.get("pm10",0) or 0)
        no2   = float(aq_cur.get("nitrogen_dioxide",0) or 0)
        so2   = float(aq_cur.get("sulphur_dioxide",0) or 0)
        o3    = float(aq_cur.get("ozone",0) or 0)
        co    = float(aq_cur.get("carbon_monoxide",0) or 0)
        eu_aqi= int(aq_cur.get("european_aqi",0) or 0)
        us_aqi= int(aq_cur.get("us_aqi",0) or 0)

        pollutants = [
            ("PM₂.₅ Fine Particles", pm25, 12, 35, "μg/m³", min(100,int(pm25/2.5))),
            ("PM₁₀ Coarse Particles",pm10, 20, 50, "μg/m³", min(100,int(pm10/1.5))),
            ("Nitrogen Dioxide NO₂", no2,  40,100, "μg/m³", min(100,int(no2))),
            ("Sulphur Dioxide SO₂",  so2,  20, 80, "μg/m³", min(100,int(so2))),
            ("Ozone O₃",             o3,   60,120, "μg/m³", min(100,int(o3/1.8))),
            ("Carbon Monoxide CO",   co/1000,0.5,2,"mg/m³", min(100,int(co/700))),
        ]

        aq1, aq2 = st.columns(2)
        for i, (name, val, good, bad, unit, pct) in enumerate(pollutants):
            col = aq1 if i < 3 else aq2
            bc = bar_color(val, good, bad)
            with col:
                st.markdown(f"""
<div class="pol-row">
    <div class="pol-header">
        <span class="pol-name">{name}</span>
        <span class="pol-val" style="color:{bc}">{val:.1f} <span style="font-size:0.65rem;color:#6ee7b7;font-family:'Space Grotesk',sans-serif">{unit}</span></span>
    </div>
    <div class="pol-track">
        <div class="pol-fill" style="width:{pct}%;background:{bc}"></div>
    </div>
</div>""", unsafe_allow_html=True)

        aqi_c, aqi_u = st.columns(2)
        eu_color = bar_color(eu_aqi, 20, 60)
        us_color = bar_color(us_aqi, 50, 100)
        with aqi_c:
            st.markdown(f"""
<div class="av-panel" style="display:flex;align-items:center;gap:1.5rem">
    <div>
        <div class="av-panel-label">European AQI</div>
        <div><span class="av-panel-value" style="color:{eu_color}">{eu_aqi}</span></div>
    </div>
    <div style="flex:1;height:1px;background:rgba(34,197,94,0.1)"></div>
    <div>
        <div class="av-panel-label">US AQI</div>
        <div><span class="av-panel-value" style="color:{us_color}">{us_aqi}</span></div>
    </div>
</div>""", unsafe_allow_html=True)
        with aqi_u:
            ps_display = ps if ps is not None else 0
            ps_color, ps_grade = score_grade(ps_display)
            st.markdown(f"""
<div class="av-panel" style="display:flex;align-items:center;gap:1rem">
    <div style="flex:1">
        <div class="av-panel-label">Pollution Score</div>
        <div><span class="av-panel-value" style="color:{ps_color}">{ps_display}</span><span class="av-panel-unit">/100</span></div>
        <div class="av-panel-sub">{ps_grade} — {"Higher is cleaner air"}</div>
    </div>
    <div style="font-size:2.5rem">{"🟢" if ps_display>=65 else "🟡" if ps_display>=40 else "🔴"}</div>
</div>""", unsafe_allow_html=True)
    else:
        st.info("Air quality data unavailable for this location.")

    # ── 7-Day Forecast ──
    st.markdown("""
    <div class="av-section">
        <div class="av-section-icon">📅</div>
        <div class="av-section-label">7-Day Forecast Matrix</div>
        <div class="av-section-line"></div>
    </div>
    """, unsafe_allow_html=True)

    rows = []
    for i, day in enumerate(daily["time"]):
        d = datetime.strptime(day, "%Y-%m-%d")
        rows.append({
            "Date": d.strftime("%a %d %b"),
            "Max °C": f"{daily['temperature_2m_max'][i]:.1f}",
            "Min °C": f"{daily['temperature_2m_min'][i]:.1f}",
            "Rain mm": f"{daily['precipitation_sum'][i]:.1f}",
            "Rain %": f"{daily['precipitation_probability_max'][i]}%",
            "Wind km/h": f"{daily['wind_speed_10m_max'][i]:.1f}",
            "UV": f"{daily['uv_index_max'][i]:.0f}",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════
# TAB 2 — CRISIS INTELLIGENCE
# ══════════════════════════════════════════════════════════════
with tab2:
    st.markdown("""
    <div class="av-section">
        <div class="av-section-icon">⚠</div>
        <div class="av-section-label">Predictive Crisis Detection</div>
        <div class="av-section-line"></div>
    </div>
    """, unsafe_allow_html=True)

    for level, title, msg in predict_crises(weather, aq_cur):
        cls = f"av-alert-{level}"
        icon = "🚨" if level=="crisis" else "⚠️" if level=="warning" else "✅"
        st.markdown(f"""
<div class="av-alert {cls}">
    <div class="av-alert-icon">{icon}</div>
    <div class="av-alert-body">
        <div class="av-alert-title">{title}</div>
        <div class="av-alert-msg">{msg}</div>
    </div>
</div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="av-section">
        <div class="av-section-icon">🤖</div>
        <div class="av-section-label">AI Risk Assessment</div>
        <div class="av-section-line"></div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("▶ RUN AI CRISIS ANALYSIS", type="primary"):
        summary = {
            "location": f"{city}, {country}",
            "temp": cur["temperature_2m"], "humidity": cur["relative_humidity_2m"],
            "wind": cur["wind_speed_10m"], "eu_aqi": aq_cur.get("european_aqi"),
            "pm2_5": aq_cur.get("pm2_5"), "pm10": aq_cur.get("pm10"),
            "pollution_score": ps, "weather_score": ws, "env_score": es,
            "7d_max_temps": daily["temperature_2m_max"],
            "7d_rain_mm": daily["precipitation_sum"],
        }
        with st.spinner("Analysing environmental risk vectors..."):
            result = ask_groq(
                f"Environmental crisis analysis for agricultural region {city}:\n{json.dumps(summary,indent=2)}\n\nProvide:\n1. Multi-hazard risk assessment\n2. Agricultural impact by crop category\n3. Priority action list for farmers\n4. 30-day climate outlook\n\nBe specific, data-driven and actionable.",
                system="You are an expert environmental risk analyst specialising in agricultural systems. Provide precise, actionable intelligence."
            )
        st.markdown(f'<div class="av-ai-output">{result.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TAB 3 — CROP ADVISOR
# ══════════════════════════════════════════════════════════════
with tab3:
    st.markdown("""
    <div class="av-section">
        <div class="av-section-icon">🌱</div>
        <div class="av-section-label">AI Crop Recommendation Engine</div>
        <div class="av-section-line"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="font-size:0.75rem;color:#6ee7b7;margin-bottom:1.2rem;
         padding:0.8rem 1rem;background:rgba(34,197,94,0.05);
         border:1px solid rgba(34,197,94,0.1);border-radius:10px">
        Analysing {city.title()} conditions: {cur['temperature_2m']:.1f}°C ·
        {cur['relative_humidity_2m']}% humidity ·
        Pollution Score {ps if ps is not None else 'N/A'}/100 ·
        Env Score {es}/100
    </div>
    """, unsafe_allow_html=True)

    crops = recommend_crops(weather)
    if crops:
        for emoji, name, compat, reason, care in crops:
            st.markdown(f"""
<div class="crop-item">
    <div class="crop-emoji">{emoji}</div>
    <div class="crop-info">
        <div class="crop-name-text">{name}</div>
        <div class="crop-reason">{reason}</div>
        <div class="crop-care">▸ {care}</div>
    </div>
    <div class="crop-compat">
        <div class="pct">{compat}</div>
        <div class="pct-lbl">% match</div>
    </div>
</div>""", unsafe_allow_html=True)
    else:
        st.info("Insufficient environmental data for crop recommendations.")

    st.markdown("""
    <div class="av-section">
        <div class="av-section-icon">📋</div>
        <div class="av-section-label">Personalised Management Plan</div>
        <div class="av-section-line"></div>
    </div>
    """, unsafe_allow_html=True)

    crop_options = [f"{e} {n}" for e,n,*_ in crops] if crops else ["No crops available"]
    selected = st.selectbox("Select crop for detailed plan", crop_options)

    if st.button("▶ GENERATE MANAGEMENT PLAN", type="primary") and crops:
        with st.spinner("Building precision agriculture plan..."):
            result = ask_groq(
                f"""Generate a precision agriculture management plan for {selected} in {city}, {country}.

Environmental conditions:
- Temperature: {cur['temperature_2m']:.1f}°C
- Humidity: {cur['relative_humidity_2m']}%
- UV Index: {cur.get('uv_index',0) or 0:.0f}
- Wind: {cur['wind_speed_10m']:.1f} km/h
- EU AQI: {aq_cur.get('european_aqi','N/A')}
- PM2.5: {aq_cur.get('pm2_5','N/A')} μg/m³
- Pollution Score: {ps}/100
- Environmental Score: {es}/100

Plan must include:
1. Precision sowing and planting protocol
2. Smart irrigation schedule with water quantities
3. Nutrient management timeline (NPK ratios)
4. Integrated pest and disease monitoring
5. Pollution stress mitigation strategies
6. Yield optimisation and harvest timeline
7. Climate risk contingencies""",
                system="You are a precision agriculture specialist. Provide data-driven, specific recommendations tailored to the exact environmental conditions."
            )
        st.markdown(f'<div class="av-ai-output">{result.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TAB 4 — FARM SIMULATION
# ══════════════════════════════════════════════════════════════
with tab4:
    st.markdown("""
    <div class="av-section">
        <div class="av-section-icon">🔬</div>
        <div class="av-section-label">Farm Digital Twin & Scenario Simulation</div>
        <div class="av-section-line"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:0.78rem;color:#6ee7b7;line-height:1.7;
         padding:1rem;background:rgba(34,197,94,0.04);
         border:1px solid rgba(34,197,94,0.1);border-radius:10px;margin-bottom:1.5rem">
    Simulate future farming scenarios by adjusting environmental parameters.
    The AI will model potential outcomes and provide strategic recommendations.
    </div>
    """, unsafe_allow_html=True)

    sim1, sim2 = st.columns(2)
    with sim1:
        temp_change = st.slider("Temperature Change (°C)", -5, +10, 0,
            help="Simulate temperature increase or decrease")
        rain_change = st.slider("Rainfall Change (%)", -80, +100, 0,
            help="Simulate drought or excess rainfall")
    with sim2:
        aqi_change = st.slider("AQI Change", -50, +150, 0,
            help="Simulate pollution increase or decrease")
        sim_crop = st.text_input("Target Crop", placeholder="e.g. Tomato, Rice, Wheat...")

    if st.button("▶ RUN FARM SIMULATION", type="primary"):
        sim_temp = cur["temperature_2m"] + temp_change
        base_rain = sum(p for p in daily["precipitation_sum"] if p) / 7
        sim_rain = base_rain * (1 + rain_change/100)
        sim_aqi = (aq_cur.get("european_aqi") or 30) + aqi_change

        with st.spinner("Running farm simulation model..."):
            result = ask_groq(
                f"""Run a farm simulation for {city}, {country}.

BASELINE CONDITIONS:
- Temperature: {cur['temperature_2m']:.1f}°C | Humidity: {cur['relative_humidity_2m']}%
- Avg daily rainfall: {base_rain:.1f}mm | EU AQI: {aq_cur.get('european_aqi','N/A')}
- Env Score: {es}/100

SIMULATED SCENARIO:
- Temperature: {sim_temp:.1f}°C (change: {temp_change:+.0f}°C)
- Daily rainfall: {sim_rain:.1f}mm (change: {rain_change:+.0f}%)
- EU AQI: {sim_aqi:.0f} (change: {aqi_change:+.0f})
{'- Target crop: ' + sim_crop if sim_crop else ''}

Provide:
1. Scenario risk assessment vs baseline
2. Predicted crop yield impact (% change estimates)
3. Water and resource requirement changes
4. Recommended adaptive strategies
5. Early warning indicators to monitor
6. Best and worst case projections""",
                system="You are an agricultural simulation expert. Model the scenario quantitatively with specific projections and probabilities where possible."
            )
        st.markdown(f'<div class="av-ai-output">{result.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TAB 5 — FIELD ASSISTANT
# ══════════════════════════════════════════════════════════════
with tab5:
    st.markdown("""
    <div class="av-section">
        <div class="av-section-icon">◈</div>
        <div class="av-section-label">Intelligent Field Assistant</div>
        <div class="av-section-line"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="font-size:0.75rem;color:#6ee7b7;line-height:1.6;
         padding:0.8rem 1rem;background:rgba(34,197,94,0.04);
         border:1px solid rgba(34,197,94,0.1);border-radius:10px;margin-bottom:1rem">
        Context-aware assistant · Location: {city.title()}, {country} ·
        {cur['temperature_2m']:.1f}°C · AQI {aq_cur.get('european_aqi','N/A')} ·
        Env Score {es}/100
    </div>
    """, unsafe_allow_html=True)

    crop_focus = st.text_input("Crop Focus (optional)", placeholder="e.g. Rice, Tomato, Groundnut...")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Suggested questions
    if not st.session_state.chat_history:
        st.markdown("""
        <div style="font-size:0.65rem;letter-spacing:0.15em;text-transform:uppercase;
             color:#22c55e;margin-bottom:0.6rem;font-weight:600">Suggested Queries</div>
        """, unsafe_allow_html=True)
        suggestions = [
            "What pests should I watch for in these conditions?",
            "How much water does my crop need this week?",
            "Is the air quality affecting my crop growth?",
            "What fertiliser should I apply right now?",
        ]
        sq_cols = st.columns(2)
        for i, s in enumerate(suggestions):
            with sq_cols[i%2]:
                st.markdown(f"""
<div style="padding:0.6rem 0.8rem;background:rgba(34,197,94,0.05);
     border:1px solid rgba(34,197,94,0.12);border-radius:8px;
     font-size:0.75rem;color:#86efac;margin-bottom:0.5rem;cursor:pointer">
    ▸ {s}
</div>""", unsafe_allow_html=True)

    # Chat history
    for msg in st.session_state.chat_history:
        if msg["role"]=="user":
            st.markdown(f"""
<div style="display:flex;justify-content:flex-end;margin-bottom:0.6rem">
    <div class="chat-msg chat-user">
        <div class="chat-label">You</div>
        {msg['content']}
    </div>
</div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
<div style="margin-bottom:0.6rem">
    <div class="chat-msg chat-ai">
        <div class="chat-label">◈ Aeroveda AI</div>
        {msg['content']}
    </div>
</div>""", unsafe_allow_html=True)

    user_input = st.chat_input("Ask anything about your farm, crops, soil, pests, or conditions...")
    if user_input:
        st.session_state.chat_history.append({"role":"user","content":user_input})
        with st.spinner("Processing..."):
            reply = ask_groq_chat(
                st.session_state.chat_history,
                system=f"""You are Aeroveda's intelligent field assistant — an expert agronomist with real-time environmental awareness.

Current context:
- Location: {city}, {country} ({lat:.2f}°N, {lon:.2f}°E)
- Temperature: {cur['temperature_2m']:.1f}°C | Humidity: {cur['relative_humidity_2m']}%
- Wind: {cur['wind_speed_10m']:.1f} km/h | UV: {cur.get('uv_index',0) or 0:.0f}
- Conditions: {wdesc(cur['weather_code'])}
- EU AQI: {aq_cur.get('european_aqi','N/A')} | Pollution Score: {ps if ps is not None else 'N/A'}/100
- Environmental Score: {es}/100
{'- Crop focus: ' + crop_focus if crop_focus else ''}

Provide precise, contextual advice. Use bullet points for clarity. Tailor all recommendations to the exact environmental conditions above.""",
                max_tokens=700
            )
        st.session_state.chat_history.append({"role":"assistant","content":reply})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("↺ CLEAR SESSION"):
            st.session_state.chat_history = []
            st.rerun()
