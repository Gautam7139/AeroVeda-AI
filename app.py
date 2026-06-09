import streamlit as st
import streamlit.components.v1 as components
import requests
import json
from datetime import datetime
import pandas as pd
from groq import Groq
import math

st.set_page_config(
    page_title="Aeroveda",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Handle GPS from query params ────────────────────────────────────────────
params = st.query_params
gps_raw = params.get("gps", "")
if gps_raw and "," in str(gps_raw):
    try:
        parts = str(gps_raw).split(",")
        gps_lat = float(parts[0])
        gps_lon = float(parts[1])
        r = requests.get(
            f"https://nominatim.openstreetmap.org/reverse?lat={gps_lat}&lon={gps_lon}&format=json",
            headers={"User-Agent": "Aeroveda/2.0"}, timeout=6
        )
        data = r.json()
        detected = (data.get("address",{}).get("city") or
                    data.get("address",{}).get("town") or
                    data.get("address",{}).get("village",""))
        if detected:
            st.session_state["city"] = detected
            st.query_params.clear()
    except:
        pass

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background: #000a04 !important;
    color: #b8ffcf;
    overflow-x: hidden;
}

/* ── Animated starfield background ── */
.stApp::before {
    content: '';
    position: fixed; inset: 0;
    background:
        radial-gradient(ellipse at 20% 50%, rgba(0,255,100,0.03) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 20%, rgba(0,200,80,0.04) 0%, transparent 40%),
        radial-gradient(ellipse at 50% 80%, rgba(0,150,60,0.03) 0%, transparent 50%);
    pointer-events: none; z-index: 0;
    animation: breathe 8s ease-in-out infinite;
}
@keyframes breathe {
    0%,100% { opacity: 0.6; }
    50% { opacity: 1; }
}

/* ── Hex grid overlay ── */
.stApp::after {
    content: '';
    position: fixed; inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='60' height='104'%3E%3Cpath d='M30 2 L58 17 L58 47 L30 62 L2 47 L2 17 Z' fill='none' stroke='rgba(0,255,100,0.03)' stroke-width='0.5'/%3E%3Cpath d='M30 62 L58 77 L58 107 L30 122 L2 107 L2 77 Z' fill='none' stroke='rgba(0,255,100,0.03)' stroke-width='0.5'/%3E%3C/svg%3E");
    pointer-events: none; z-index: 0;
}

.main .block-container {
    padding: 0 2.5rem 5rem !important;
    max-width: 1500px !important;
    position: relative; z-index: 1;
}

/* ── HERO HEADER ── */
.av-hero {
    position: relative;
    padding: 3rem 0 2.5rem;
    text-align: center;
    overflow: hidden;
}
.av-hero-ring {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: 600px; height: 600px;
    border-radius: 50%;
    border: 1px solid rgba(0,255,100,0.05);
    animation: spin-slow 30s linear infinite;
    pointer-events: none;
}
.av-hero-ring-2 {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: 400px; height: 400px;
    border-radius: 50%;
    border: 1px solid rgba(0,255,100,0.08);
    animation: spin-slow 20s linear infinite reverse;
    pointer-events: none;
}
.av-hero-ring::before {
    content: '';
    position: absolute;
    top: -3px; left: 50%;
    width: 6px; height: 6px;
    background: #00ff64;
    border-radius: 50%;
    box-shadow: 0 0 12px #00ff64, 0 0 24px #00ff64;
}
@keyframes spin-slow { to { transform: translate(-50%,-50%) rotate(360deg); } }

.av-logo {
    position: relative;
    z-index: 2;
    font-family: 'Orbitron', sans-serif;
    font-size: 3.5rem;
    font-weight: 900;
    letter-spacing: 0.08em;
    color: #fff;
    text-shadow:
        0 0 30px rgba(0,255,100,0.5),
        0 0 60px rgba(0,255,100,0.2);
    line-height: 1;
}
.av-logo span { color: #00ff64; }
.av-subtitle {
    position: relative; z-index: 2;
    font-size: 0.7rem;
    letter-spacing: 0.35em;
    text-transform: uppercase;
    color: #00cc50;
    margin-top: 0.6rem;
    font-family: 'JetBrains Mono', monospace;
}
.av-location-bar {
    position: relative; z-index: 2;
    display: inline-flex;
    align-items: center;
    gap: 10px;
    background: rgba(0,255,100,0.04);
    border: 1px solid rgba(0,255,100,0.15);
    border-radius: 999px;
    padding: 0.5rem 1.4rem;
    margin-top: 1.2rem;
    font-size: 0.8rem;
    color: #00ff64;
    font-family: 'JetBrains Mono', monospace;
    backdrop-filter: blur(10px);
}
.av-live-dot {
    width: 8px; height: 8px;
    background: #00ff64;
    border-radius: 50%;
    box-shadow: 0 0 8px #00ff64;
    animation: blink 1.5s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1;} 50%{opacity:0.3;} }

/* ── SCORE UNIVERSE ── */
.score-universe {
    display: flex;
    justify-content: center;
    gap: 2rem;
    flex-wrap: wrap;
    margin: 2rem 0;
}
.score-orb {
    position: relative;
    width: 140px;
    cursor: default;
}
.score-orb svg { width: 140px; height: 140px; display: block; }
.score-orb-inner {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%,-50%);
    text-align: center;
}
.score-orb-num {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: #fff;
    line-height: 1;
    text-shadow: 0 0 20px currentColor;
}
.score-orb-lbl {
    font-size: 0.55rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #00cc50;
    margin-top: 3px;
    font-family: 'JetBrains Mono', monospace;
}
.score-orb-title {
    text-align: center;
    margin-top: 0.6rem;
    font-size: 0.62rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #4dff8a;
    font-family: 'JetBrains Mono', monospace;
}
.score-orb-grade {
    text-align: center;
    font-size: 0.7rem;
    font-weight: 600;
    font-family: 'Orbitron', sans-serif;
    margin-top: 2px;
    letter-spacing: 0.1em;
}

/* ── PANELS ── */
.av-panel {
    background: linear-gradient(135deg, rgba(0,20,8,0.9), rgba(0,10,4,0.95));
    border: 1px solid rgba(0,255,100,0.1);
    border-radius: 16px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(12px);
    transition: border-color 0.3s;
}
.av-panel:hover { border-color: rgba(0,255,100,0.25); }
.av-panel::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg,
        transparent, rgba(0,255,100,0.4), transparent);
}
.av-panel::after {
    content: '';
    position: absolute;
    bottom: 0; right: 0;
    width: 60px; height: 60px;
    background: radial-gradient(circle, rgba(0,255,100,0.04), transparent);
    border-radius: 50%;
}

.av-panel-label {
    font-size: 0.6rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #00cc50;
    margin-bottom: 0.4rem;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 500;
}
.av-panel-value {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.9rem;
    font-weight: 700;
    color: #fff;
    line-height: 1;
    text-shadow: 0 0 20px rgba(0,255,100,0.3);
}
.av-panel-unit {
    font-size: 0.75rem;
    color: #4dff8a;
    margin-left: 3px;
    font-family: 'Inter', sans-serif;
}
.av-panel-sub {
    font-size: 0.7rem;
    color: #00cc50;
    margin-top: 5px;
    font-family: 'JetBrains Mono', monospace;
}

/* ── SECTION HEADER ── */
.av-section {
    display: flex;
    align-items: center;
    gap: 14px;
    margin: 2.5rem 0 1.5rem;
}
.av-section-badge {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.62rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #000a04;
    background: linear-gradient(135deg, #00ff64, #00cc50);
    padding: 4px 12px;
    border-radius: 4px;
    font-weight: 700;
    white-space: nowrap;
}
.av-section-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(0,255,100,0.3), transparent);
}
.av-section-dots {
    display: flex; gap: 4px;
}
.av-section-dots span {
    width: 4px; height: 4px;
    border-radius: 50%;
    background: rgba(0,255,100,0.3);
}
.av-section-dots span:first-child { background: #00ff64; }

/* ── POLLUTANT BARS ── */
.pol-row { margin-bottom: 1.2rem; }
.pol-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 6px;
}
.pol-name {
    font-size: 0.68rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #4dff8a;
    font-family: 'JetBrains Mono', monospace;
}
.pol-value {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
}
.pol-track {
    height: 4px;
    background: rgba(0,255,100,0.08);
    border-radius: 99px;
    overflow: visible;
    position: relative;
}
.pol-fill {
    height: 4px;
    border-radius: 99px;
    position: relative;
    transition: width 1s cubic-bezier(.4,0,.2,1);
}
.pol-fill::after {
    content: '';
    position: absolute;
    right: -1px; top: -2px;
    width: 8px; height: 8px;
    border-radius: 50%;
    background: currentColor;
    box-shadow: 0 0 6px currentColor, 0 0 12px currentColor;
}

/* ── ALERT CARDS ── */
.av-alert {
    display: flex;
    gap: 14px;
    padding: 1.1rem 1.3rem;
    border-radius: 12px;
    margin-bottom: 0.7rem;
    position: relative;
    overflow: hidden;
}
.av-alert::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
}
.av-alert-crisis {
    background: rgba(255,30,30,0.06);
    border: 1px solid rgba(255,30,30,0.2);
}
.av-alert-crisis::before { background: #ff1e1e; }
.av-alert-warning {
    background: rgba(255,200,0,0.06);
    border: 1px solid rgba(255,200,0,0.2);
}
.av-alert-warning::before { background: #ffc800; }
.av-alert-safe {
    background: rgba(0,255,100,0.05);
    border: 1px solid rgba(0,255,100,0.18);
}
.av-alert-safe::before { background: #00ff64; }
.av-alert-icon { font-size: 1.3rem; flex-shrink: 0; }
.av-alert-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.65rem;
    letter-spacing: 0.18em;
    font-weight: 700;
    margin-bottom: 4px;
}
.av-alert-crisis .av-alert-title { color: #ff6b6b; }
.av-alert-warning .av-alert-title { color: #ffd700; }
.av-alert-safe .av-alert-title { color: #00ff64; }
.av-alert-msg { font-size: 0.82rem; line-height: 1.6; }
.av-alert-crisis .av-alert-msg { color: #ffb3b3; }
.av-alert-warning .av-alert-msg { color: #fff3b0; }
.av-alert-safe .av-alert-msg { color: #b3ffd0; }

/* ── CROP CARDS ── */
.crop-card {
    display: flex;
    align-items: center;
    gap: 1.2rem;
    padding: 1.1rem 1.4rem;
    background: linear-gradient(135deg, rgba(0,20,8,0.8), rgba(0,10,4,0.9));
    border: 1px solid rgba(0,255,100,0.1);
    border-radius: 14px;
    margin-bottom: 0.7rem;
    position: relative;
    overflow: hidden;
    transition: all 0.3s;
}
.crop-card:hover {
    border-color: rgba(0,255,100,0.3);
    transform: translateX(4px);
}
.crop-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    background: linear-gradient(180deg, #00ff64, #00cc50);
    border-radius: 3px 0 0 3px;
}
.crop-emoji-big { font-size: 2.2rem; flex-shrink: 0; }
.crop-info { flex: 1; }
.crop-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: #fff;
    letter-spacing: 0.05em;
}
.crop-reason { font-size: 0.75rem; color: #4dff8a; margin-top: 3px; }
.crop-care {
    font-size: 0.68rem;
    color: #00cc50;
    margin-top: 5px;
    font-family: 'JetBrains Mono', monospace;
}
.crop-compat-ring { flex-shrink: 0; }

/* ── CHAT ── */
.chat-wrap { margin-bottom: 0.8rem; }
.chat-msg {
    padding: 0.9rem 1.2rem;
    border-radius: 14px;
    font-size: 0.84rem;
    line-height: 1.7;
    max-width: 85%;
}
.chat-user-wrap { display: flex; justify-content: flex-end; }
.chat-user {
    background: rgba(0,255,100,0.08);
    border: 1px solid rgba(0,255,100,0.2);
    color: #d0ffe0;
    border-radius: 14px 14px 4px 14px;
}
.chat-ai-wrap { display: flex; justify-content: flex-start; }
.chat-ai {
    background: rgba(0,20,8,0.9);
    border: 1px solid rgba(0,255,100,0.1);
    color: #b8ffcf;
    border-radius: 14px 14px 14px 4px;
}
.chat-label-user {
    font-size: 0.58rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #00ff64;
    margin-bottom: 5px;
    text-align: right;
    font-family: 'JetBrains Mono', monospace;
}
.chat-label-ai {
    font-size: 0.58rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #00cc50;
    margin-bottom: 5px;
    font-family: 'JetBrains Mono', monospace;
}

/* ── AI OUTPUT ── */
.av-ai-box {
    background: rgba(0,10,4,0.95);
    border: 1px solid rgba(0,255,100,0.15);
    border-radius: 16px;
    padding: 1.8rem;
    color: #c8ffd8;
    line-height: 1.9;
    font-size: 0.87rem;
    position: relative;
    margin-top: 1rem;
}
.av-ai-box-tag {
    position: absolute;
    top: -11px; left: 20px;
    background: #000a04;
    padding: 0 10px;
    font-size: 0.58rem;
    letter-spacing: 0.22em;
    color: #00ff64;
    font-weight: 700;
    font-family: 'Orbitron', sans-serif;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(0,255,100,0.1) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    color: #00cc50 !important;
    padding: 0.9rem 1.6rem !important;
    background: transparent !important;
    border: none !important;
    font-weight: 500 !important;
}
.stTabs [aria-selected="true"] {
    color: #00ff64 !important;
    border-bottom: 2px solid #00ff64 !important;
    background: rgba(0,255,100,0.04) !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding: 2rem 0 0 !important;
    background: transparent !important;
}

/* ── INPUTS ── */
.stTextInput input, .stTextInput textarea {
    background: rgba(0,20,8,0.8) !important;
    border: 1px solid rgba(0,255,100,0.18) !important;
    border-radius: 10px !important;
    color: #d0ffe0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
}
.stTextInput input:focus {
    border-color: rgba(0,255,100,0.45) !important;
    box-shadow: 0 0 0 3px rgba(0,255,100,0.06) !important;
}
.stTextInput label {
    color: #4dff8a !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* ── BUTTONS ── */
.stButton button {
    background: rgba(0,255,100,0.06) !important;
    border: 1px solid rgba(0,255,100,0.25) !important;
    color: #00ff64 !important;
    border-radius: 8px !important;
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}
.stButton button:hover {
    background: rgba(0,255,100,0.15) !important;
    border-color: #00ff64 !important;
    box-shadow: 0 0 20px rgba(0,255,100,0.15) !important;
    color: #fff !important;
}
button[kind="primary"] {
    background: linear-gradient(135deg, #005c20, #00a336) !important;
    border: 1px solid #00ff64 !important;
    color: #fff !important;
    box-shadow: 0 0 20px rgba(0,255,100,0.2) !important;
}

/* ── SELECT ── */
[data-baseweb="select"] > div {
    background: rgba(0,20,8,0.9) !important;
    border-color: rgba(0,255,100,0.18) !important;
    color: #d0ffe0 !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── SLIDER ── */
.stSlider [data-baseweb="slider"] { padding: 0 !important; }
.stSlider [data-testid="stThumbValue"] {
    color: #00ff64 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem !important;
}

/* ── DATAFRAME ── */
[data-testid="stDataFrameResizable"] {
    border: 1px solid rgba(0,255,100,0.12) !important;
    border-radius: 12px !important;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: rgba(0,5,2,0.98) !important;
    border-right: 1px solid rgba(0,255,100,0.1) !important;
}

/* ── HIDE BRANDING ── */
#MainMenu, footer, header { visibility: hidden; }
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-thumb { background: rgba(0,255,100,0.2); border-radius: 99px; }
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
            model="llama-3.3-70b-versatile", max_tokens=max_tokens,
            messages=[{"role":"system","content":system},{"role":"user","content":prompt}]
        )
        return r.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def ask_groq_chat(messages, system, max_tokens=700):
    try:
        client = get_groq_client()
        r = client.chat.completions.create(
            model="llama-3.3-70b-versatile", max_tokens=max_tokens,
            messages=[{"role":"system","content":system}]+messages
        )
        return r.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# ─── Data Fetchers ────────────────────────────────────────────────────────────
@st.cache_data(ttl=1800)
def fetch_weather(lat, lon):
    url = (f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
           f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
           f"precipitation,rain,wind_speed_10m,wind_direction_10m,"
           f"surface_pressure,cloud_cover,uv_index,weather_code"
           f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,"
           f"wind_speed_10m_max,uv_index_max,precipitation_probability_max"
           f"&forecast_days=7&timezone=auto")
    try:
        r = requests.get(url, timeout=20); r.raise_for_status(); return r.json()
    except Exception as e:
        st.error(f"Weather unavailable: {e}"); return None

@st.cache_data(ttl=1800)
def fetch_air_quality(lat, lon):
    url = (f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}"
           f"&current=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,european_aqi,us_aqi")
    try:
        r = requests.get(url, timeout=20); r.raise_for_status(); return r.json()
    except: return None

@st.cache_data(ttl=3600)
def geocode_city(city):
    try:
        r = requests.get(
            f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json",
            timeout=10)
        data = r.json()
        if data.get("results"):
            res = data["results"][0]
            return res["latitude"], res["longitude"], res.get("country",""), res.get("name", city)
        return None
    except: return None

# ─── Intelligence Engine ──────────────────────────────────────────────────────
def compute_weather_score(w):
    c = w["current"]
    s = 100
    t=c["temperature_2m"]; h=c["relative_humidity_2m"]
    wnd=c["wind_speed_10m"]; uv=c.get("uv_index",0) or 0
    pr=c.get("precipitation",0) or 0
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
    if s>=80: return "#00ff64","OPTIMAL"
    elif s>=65: return "#4dff8a","GOOD"
    elif s>=45: return "#ffd700","MODERATE"
    elif s>=25: return "#ff8c00","STRESSED"
    else: return "#ff3030","CRITICAL"

def bcolor(val, good, bad):
    if val<=good: return "#00ff64"
    elif val<=bad: return "#ffd700"
    else: return "#ff4444"

WMO={0:"Clear sky",1:"Mainly clear",2:"Partly cloudy",3:"Overcast",
     45:"Fog",51:"Light drizzle",53:"Drizzle",55:"Heavy drizzle",
     61:"Slight rain",63:"Moderate rain",65:"Heavy rain",
     80:"Showers",81:"Moderate showers",82:"Violent showers",
     95:"Thunderstorm",96:"Thunderstorm + hail"}
def wdesc(code): return WMO.get(code,"—")

def predict_crises(w, aq_cur):
    alerts=[]
    daily=w["daily"]
    if aq_cur:
        aqi=aq_cur.get("european_aqi") or aq_cur.get("us_aqi")
        if aqi and aqi>80:
            alerts.append(("crisis","AIR QUALITY CRISIS",f"AQI {aqi} — Hazardous. Severe crop and health risk."))
        elif aqi and aqi>50:
            alerts.append(("warning","POLLUTION ADVISORY",f"AQI {aqi} — Poor air quality. Sensitive crops may show stress."))
    hot=sum(1 for t in daily["temperature_2m_max"] if t and t>38)
    if hot>=3: alerts.append(("crisis","HEAT WAVE DETECTED",f"{hot} days above 38°C forecast. Extreme crop stress probability."))
    elif hot>=1: alerts.append(("warning","HEAT ADVISORY",f"{hot} day(s) above 38°C. Monitor irrigation closely."))
    rain=sum(p for p in daily["precipitation_sum"] if p is not None)
    if rain<2: alerts.append(("crisis","DROUGHT RISK","Near-zero rainfall over 7 days. Activate emergency irrigation."))
    elif rain<8: alerts.append(("warning","LOW RAINFALL","Below-normal precipitation. Schedule supplemental irrigation."))
    heavy=sum(1 for p in daily["precipitation_sum"] if p and p>25)
    if heavy>=2: alerts.append(("crisis","FLOOD PROBABILITY",f"{heavy} high-rainfall days forecast. Severe waterlogging risk."))
    elif heavy==1: alerts.append(("warning","HEAVY RAIN ALERT","One intense rainfall day. Clear drainage channels."))
    maxw=max((v for v in daily["wind_speed_10m_max"] if v),default=0)
    if maxw>70: alerts.append(("crisis","STORM WARNING",f"Gusts up to {maxw:.0f} km/h. Secure all structures."))
    elif maxw>45: alerts.append(("warning","HIGH WIND ADVISORY",f"Winds up to {maxw:.0f} km/h expected."))
    if not alerts:
        alerts.append(("safe","CONDITIONS STABLE","No environmental crises detected in 7-day forecast window."))
    return alerts

def recommend_crops(w):
    c=w["current"]; t=c["temperature_2m"]; h=c["relative_humidity_2m"]
    pl=[p for p in w["daily"]["precipitation_sum"] if p is not None]
    ar=sum(pl)/len(pl) if pl else 0
    crops=[]
    if 20<=t<=38 and h>50:
        crops.append(("🌾","Rice",95,"Optimal temperature-humidity matrix","High water · 3–4 month cycle · transplant at 21 days"))
        crops.append(("🌿","Sugarcane",88,"Strong heat-humidity compatibility","Weekly deep irrigation · monthly NPK · 10–12 months"))
    if 18<=t<=35:
        crops.append(("🥜","Groundnut",85,"Temperature range aligned","Well-drained sandy loam · dry finish required"))
        crops.append(("🌽","Maize",82,"Thermophilic conditions met","Moderate water · high nitrogen · 90-day cycle"))
    if t>=25 and h<70:
        crops.append(("🍅","Tomato",78,"Warm-dry matrix ideal","Consistent drip · stake · blight monitoring"))
        crops.append(("🌶️","Chilli",76,"Low humidity reduces fungal risk","Potassium-rich · drip preferred"))
    if t<22:
        crops.append(("🥬","Spinach",90,"Cool threshold optimal","Direct sow · 6–8 week harvest"))
        crops.append(("🥕","Carrot",84,"Root development favoured","Deep loose bed · thin at 4cm · 70 days"))
        crops.append(("🧅","Onion",80,"Bulb initiation suits cool air","Reduce water at bulbing"))
    if ar<3 and t>20:
        crops.append(("🌻","Sunflower",88,"Drought-tolerance matched","Deep taproot · minimal input · 80–95 days"))
        crops.append(("🫘","Moong Dal",83,"Short season drought legume","Sandy loam · fixes nitrogen · 60–70 days"))
    crops.sort(key=lambda x:-x[2])
    return crops[:5]

# ─── SVG Ring ─────────────────────────────────────────────────────────────────
def ring_svg(score, color, size=140, stroke=10):
    val = score if score is not None else 0
    r = (size/2) - stroke
    circ = 2*math.pi*r
    dash = (val/100)*circ
    glow_id = f"glow_{val}_{size}"
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
  <defs>
    <filter id="{glow_id}">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <circle cx="{size/2}" cy="{size/2}" r="{r}" fill="none"
    stroke="rgba(0,255,100,0.06)" stroke-width="{stroke}"/>
  <circle cx="{size/2}" cy="{size/2}" r="{r}" fill="none"
    stroke="{color}" stroke-width="{stroke}" stroke-linecap="round"
    stroke-dasharray="{dash:.1f} {circ:.1f}"
    transform="rotate(-90 {size/2} {size/2})"
    filter="url(#{glow_id})"/>
  <circle cx="{size/2}" cy="{size/2}" r="{r-stroke/2-2}" fill="none"
    stroke="rgba(0,255,100,0.03)" stroke-width="1"/>
</svg>"""

# ─── Mini ring for crop compat ────────────────────────────────────────────────
def mini_ring(score, color="#00ff64", size=60):
    r=(size/2)-5; circ=2*math.pi*r; dash=(score/100)*circ
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
  <circle cx="{size/2}" cy="{size/2}" r="{r}" fill="none"
    stroke="rgba(0,255,100,0.08)" stroke-width="4"/>
  <circle cx="{size/2}" cy="{size/2}" r="{r}" fill="none"
    stroke="{color}" stroke-width="4" stroke-linecap="round"
    stroke-dasharray="{dash:.1f} {circ:.1f}"
    transform="rotate(-90 {size/2} {size/2})"/>
  <text x="{size/2}" y="{size/2+4}" text-anchor="middle"
    font-family="Orbitron,sans-serif" font-size="10" font-weight="700"
    fill="{color}">{score}</text>
</svg>"""

# ════════════════════════════════════════════════════════
# SIDEBAR — GPS + City
# ════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="font-family:'Orbitron',sans-serif;font-size:0.6rem;
         letter-spacing:0.25em;color:#00ff64;margin-bottom:1.5rem;font-weight:700">
        ◈ LOCATION NODE
    </div>
    """, unsafe_allow_html=True)

    # GPS Button — reloads page with ?gps=lat,lon
    components.html("""
    <style>
    #gps-btn {
        width:100%; padding:10px 0;
        background: linear-gradient(135deg, rgba(0,255,100,0.08), rgba(0,200,70,0.12));
        border: 1px solid rgba(0,255,100,0.3);
        border-radius: 8px;
        color: #00ff64;
        font-family: 'Orbitron', monospace;
        font-size: 0.6rem;
        letter-spacing: 0.2em;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.2s;
        text-transform: uppercase;
    }
    #gps-btn:hover {
        background: rgba(0,255,100,0.18);
        box-shadow: 0 0 16px rgba(0,255,100,0.2);
        color: #fff;
    }
    #gps-status {
        font-family: monospace;
        font-size: 0.7rem;
        color: #00cc50;
        margin-top: 6px;
        min-height: 16px;
        text-align: center;
    }
    </style>
    <button id="gps-btn" onclick="getGPS()">⊕ USE MY LOCATION</button>
    <div id="gps-status"></div>
    <script>
    function getGPS() {
        var btn = document.getElementById('gps-btn');
        var status = document.getElementById('gps-status');
        btn.innerText = '⏳ ACQUIRING...';
        btn.disabled = true;
        if (!navigator.geolocation) {
            status.innerText = '✗ Not supported';
            status.style.color = '#ff4444';
            btn.innerText = '⊕ USE MY LOCATION';
            btn.disabled = false;
            return;
        }
        navigator.geolocation.getCurrentPosition(
            function(pos) {
                var lat = pos.coords.latitude.toFixed(6);
                var lon = pos.coords.longitude.toFixed(6);
                status.innerText = '✓ ' + lat + ', ' + lon;
                status.style.color = '#00ff64';
                btn.innerText = '✓ LOCATION FOUND';
                var base = window.parent.location.href.split('?')[0];
                window.parent.location.href = base + '?gps=' + lat + ',' + lon;
            },
            function(err) {
                status.style.color = '#ff4444';
                var msgs = {1:'Permission denied',2:'Position unavailable',3:'Timeout'};
                status.innerText = '✗ ' + (msgs[err.code] || 'Unknown error');
                btn.innerText = '⊕ USE MY LOCATION';
                btn.disabled = false;
            },
            { timeout: 12000, enableHighAccuracy: true, maximumAge: 0 }
        );
    }
    </script>
    """, height=72)

    city = st.text_input(
        "Or Type City",
        value=st.session_state.get("city","Bengaluru"),
        placeholder="City name..."
    )
    st.session_state["city"] = city

    st.markdown("""
    <div style="margin-top:2rem;padding-top:1.5rem;
         border-top:1px solid rgba(0,255,100,0.08)">
    <div style="font-family:'Orbitron',sans-serif;font-size:0.55rem;
         letter-spacing:0.22em;color:#00cc50;margin-bottom:0.8rem;font-weight:700">
        DATA NETWORK
    </div>
    <div style="font-family:monospace;font-size:0.72rem;
         color:#4dff8a;line-height:2.1">
        ◦ Open-Meteo Weather<br>
        ◦ Open-Meteo Air Quality<br>
        ◦ Nominatim Geocoding<br>
        ◦ Groq · LLaMA-3.3-70B
    </div>
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# FETCH
# ════════════════════════════════════════════════════════
geo = geocode_city(city)
if not geo:
    st.error(f"Location '{city}' not found. Try a different spelling.")
    st.stop()

lat, lon, country, city_name = geo
weather = fetch_weather(lat, lon)
if not weather: st.stop()

aq      = fetch_air_quality(lat, lon)
cur     = weather["current"]
daily   = weather["daily"]
aq_cur  = aq.get("current",{}) if aq else {}
ws      = compute_weather_score(weather)
ps      = compute_pollution_score(aq)
es      = compute_env_score(ws, ps)
ag      = max(0, min(100, round(es*0.7 + ws*0.3)))

# ════════════════════════════════════════════════════════
# HERO
# ════════════════════════════════════════════════════════
st.markdown(f"""
<div class="av-hero">
    <div class="av-hero-ring"></div>
    <div class="av-hero-ring-2"></div>
    <div class="av-logo">AERO<span>VEDA</span></div>
    <div class="av-subtitle">Agricultural Intelligence Platform · AI-Driven Environmental Analytics</div>
    <div style="display:flex;justify-content:center;margin-top:1rem">
        <div class="av-location-bar">
            <div class="av-live-dot"></div>
            <span>{city_name}, {country} &nbsp;·&nbsp; {lat:.4f}°N {lon:.4f}°E &nbsp;·&nbsp; {wdesc(cur['weather_code'])} &nbsp;·&nbsp; {datetime.now().strftime('%H:%M')} LOCAL</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# SCORE UNIVERSE
# ════════════════════════════════════════════════════════
st.markdown("""
<div class="av-section">
    <div class="av-section-badge">Intelligence Scores</div>
    <div class="av-section-line"></div>
    <div class="av-section-dots"><span></span><span></span><span></span></div>
</div>
""", unsafe_allow_html=True)

sc1,sc2,sc3,sc4 = st.columns(4)
score_data = [
    (sc1, ps, "POLLUTION", "Higher = Cleaner Air"),
    (sc2, ws, "WEATHER", "Temp · Wind · UV · Rain"),
    (sc3, es, "ENVIRONMENT", "55% Weather + 45% Air"),
    (sc4, ag, "AG POTENTIAL", "Overall Farm Suitability"),
]
for col, score, title, sub in score_data:
    val = score if score is not None else 0
    color, grade = score_grade(val)
    display = str(score) if score is not None else "N/A"
    with col:
        st.markdown(f"""
<div class="av-panel" style="text-align:center;padding:1.8rem 1rem">
    <div style="position:relative;width:140px;margin:0 auto">
        {ring_svg(val, color)}
        <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center">
            <div class="score-orb-num" style="color:{color};text-shadow:0 0 15px {color}">{display}</div>
            <div class="score-orb-lbl">/ 100</div>
        </div>
    </div>
    <div class="score-orb-title" style="margin-top:0.7rem">{title}</div>
    <div class="score-orb-grade" style="color:{color}">{grade}</div>
    <div style="font-size:0.6rem;color:#00cc50;margin-top:3px;font-family:monospace">{sub}</div>
</div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "◈  ENVIRONMENT",
    "⚠  CRISIS INTEL",
    "◈  CROP ENGINE",
    "◈  SIMULATION",
    "◈  FIELD AI"
])

# ══════════════════════════════════════════
# TAB 1
# ══════════════════════════════════════════
with tab1:
    st.markdown("""<div class="av-section">
        <div class="av-section-badge">Live Atmospheric Data</div>
        <div class="av-section-line"></div>
    </div>""", unsafe_allow_html=True)

    cols = st.columns(6)
    wx_data = [
        ("TEMPERATURE", f"{cur['temperature_2m']:.1f}", "°C"),
        ("HUMIDITY",    f"{cur['relative_humidity_2m']}", "%"),
        ("WIND SPEED",  f"{cur['wind_speed_10m']:.1f}", "km/h"),
        ("PRECIP",      f"{cur['precipitation']:.1f}", "mm"),
        ("UV INDEX",    f"{cur.get('uv_index',0) or 0:.0f}", ""),
        ("FEELS LIKE",  f"{cur['apparent_temperature']:.1f}", "°C"),
    ]
    for i,(lbl,val,unit) in enumerate(wx_data):
        with cols[i]:
            st.markdown(f"""<div class="av-panel">
    <div class="av-panel-label">{lbl}</div>
    <div><span class="av-panel-value">{val}</span><span class="av-panel-unit">{unit}</span></div>
</div>""", unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)
    for col, lbl, val, unit in [
        (c1,"CLOUD COVER",f"{cur['cloud_cover']}","%"),
        (c2,"PRESSURE",f"{cur['surface_pressure']:.0f}","hPa"),
        (c3,"WIND DIR",f"{cur['wind_direction_10m']:.0f}","°"),
    ]:
        with col:
            st.markdown(f"""<div class="av-panel">
    <div class="av-panel-label">{lbl}</div>
    <div><span class="av-panel-value">{val}</span><span class="av-panel-unit">{unit}</span></div>
</div>""", unsafe_allow_html=True)

    # Air Quality
    st.markdown("""<div class="av-section">
        <div class="av-section-badge">Air Quality Matrix</div>
        <div class="av-section-line"></div>
    </div>""", unsafe_allow_html=True)

    if aq_cur:
        pm25 = float(aq_cur.get("pm2_5",0) or 0)
        pm10 = float(aq_cur.get("pm10",0) or 0)
        no2  = float(aq_cur.get("nitrogen_dioxide",0) or 0)
        so2  = float(aq_cur.get("sulphur_dioxide",0) or 0)
        o3   = float(aq_cur.get("ozone",0) or 0)
        co   = float(aq_cur.get("carbon_monoxide",0) or 0)
        eu   = int(aq_cur.get("european_aqi",0) or 0)
        us   = int(aq_cur.get("us_aqi",0) or 0)

        pols = [
            ("PM₂.₅  Fine Particles",  pm25,   12,  35, "μg/m³", min(100,int(pm25/2.5))),
            ("PM₁₀  Coarse Particles", pm10,   20,  50, "μg/m³", min(100,int(pm10/1.5))),
            ("NO₂  Nitrogen Dioxide",  no2,    40, 100, "μg/m³", min(100,int(no2))),
            ("SO₂  Sulphur Dioxide",   so2,    20,  80, "μg/m³", min(100,int(so2))),
            ("O₃   Ozone",             o3,     60, 120, "μg/m³", min(100,int(o3/1.8))),
            ("CO   Carbon Monoxide",   co/1000,0.5,  2, "mg/m³", min(100,int(co/700))),
        ]

        aq1,aq2 = st.columns(2)
        for i,(name,val,good,bad,unit,pct) in enumerate(pols):
            bc = bcolor(val, good, bad)
            tgt = aq1 if i<3 else aq2
            with tgt:
                st.markdown(f"""
<div class="pol-row">
    <div class="pol-header">
        <span class="pol-name">{name}</span>
        <span class="pol-value" style="color:{bc}">{val:.2f}
            <span style="font-size:0.6rem;color:#4dff8a;font-family:monospace">{unit}</span>
        </span>
    </div>
    <div class="pol-track">
        <div class="pol-fill" style="width:{pct}%;background:{bc};color:{bc}"></div>
    </div>
</div>""", unsafe_allow_html=True)

        aqi_col1, aqi_col2 = st.columns(2)
        eu_c = bcolor(eu,20,60); us_c = bcolor(us,50,100)
        ps_v = ps if ps is not None else 0
        ps_c, ps_g = score_grade(ps_v)
        with aqi_col1:
            st.markdown(f"""<div class="av-panel" style="display:flex;gap:2rem;align-items:center">
    <div><div class="av-panel-label">EUROPEAN AQI</div>
    <div><span class="av-panel-value" style="color:{eu_c}">{eu}</span></div></div>
    <div style="width:1px;height:40px;background:rgba(0,255,100,0.1)"></div>
    <div><div class="av-panel-label">US AQI</div>
    <div><span class="av-panel-value" style="color:{us_c}">{us}</span></div></div>
</div>""", unsafe_allow_html=True)
        with aqi_col2:
            st.markdown(f"""<div class="av-panel" style="display:flex;align-items:center;gap:1rem">
    <div style="flex:1">
        <div class="av-panel-label">POLLUTION SCORE</div>
        <div><span class="av-panel-value" style="color:{ps_c}">{ps_v}</span>
        <span class="av-panel-unit">/ 100</span></div>
        <div class="av-panel-sub">{ps_g} · {"Higher = Cleaner"}</div>
    </div>
    <div style="font-size:2rem">{"🟢" if ps_v>=65 else "🟡" if ps_v>=40 else "🔴"}</div>
</div>""", unsafe_allow_html=True)
    else:
        st.info("Air quality data unavailable for this location.")

    # Forecast
    st.markdown("""<div class="av-section">
        <div class="av-section-badge">7-Day Forecast</div>
        <div class="av-section-line"></div>
    </div>""", unsafe_allow_html=True)

    rows=[]
    for i,day in enumerate(daily["time"]):
        d=datetime.strptime(day,"%Y-%m-%d")
        rows.append({"Date":d.strftime("%a %d %b"),
            "Max °C":f"{daily['temperature_2m_max'][i]:.1f}",
            "Min °C":f"{daily['temperature_2m_min'][i]:.1f}",
            "Rain mm":f"{daily['precipitation_sum'][i]:.1f}",
            "Rain %":f"{daily['precipitation_probability_max'][i]}%",
            "Wind km/h":f"{daily['wind_speed_10m_max'][i]:.1f}",
            "UV":f"{daily['uv_index_max'][i]:.0f}"})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════
# TAB 2
# ══════════════════════════════════════════
with tab2:
    st.markdown("""<div class="av-section">
        <div class="av-section-badge">Predictive Crisis Detection</div>
        <div class="av-section-line"></div>
    </div>""", unsafe_allow_html=True)

    for level,title,msg in predict_crises(weather, aq_cur):
        icon="🚨" if level=="crisis" else "⚠️" if level=="warning" else "✅"
        st.markdown(f"""
<div class="av-alert av-alert-{level}">
    <div class="av-alert-icon">{icon}</div>
    <div>
        <div class="av-alert-title">{title}</div>
        <div class="av-alert-msg">{msg}</div>
    </div>
</div>""", unsafe_allow_html=True)

    st.markdown("""<div class="av-section">
        <div class="av-section-badge">AI Risk Analysis</div>
        <div class="av-section-line"></div>
    </div>""", unsafe_allow_html=True)

    if st.button("▶ RUN CRISIS ANALYSIS", type="primary"):
        summary = {"location":f"{city_name},{country}","temp":cur["temperature_2m"],
            "humidity":cur["relative_humidity_2m"],"wind":cur["wind_speed_10m"],
            "eu_aqi":aq_cur.get("european_aqi"),"pm2_5":aq_cur.get("pm2_5"),
            "pollution_score":ps,"weather_score":ws,"env_score":es,
            "7d_max_temps":daily["temperature_2m_max"],"7d_rain":daily["precipitation_sum"]}
        with st.spinner("Analysing environmental risk vectors..."):
            result=ask_groq(
                f"Deep environmental crisis analysis for agricultural region {city_name}:\n{json.dumps(summary,indent=2)}\n\n"
                f"Provide:\n1. Multi-hazard risk assessment with probability estimates\n"
                f"2. Agricultural impact by crop category\n3. Priority action list with timelines\n"
                f"4. 30-day climate outlook\n5. Resource allocation recommendations",
                system="You are a senior environmental risk analyst for agricultural systems. Be precise, quantitative, and actionable."
            )
        st.markdown(f'<div class="av-ai-box"><div class="av-ai-box-tag">AI CRISIS REPORT</div>{result.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════
# TAB 3
# ══════════════════════════════════════════
with tab3:
    st.markdown("""<div class="av-section">
        <div class="av-section-badge">AI Crop Recommendation Engine</div>
        <div class="av-section-line"></div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""
<div style="padding:0.8rem 1.2rem;background:rgba(0,255,100,0.03);
     border:1px solid rgba(0,255,100,0.1);border-radius:10px;margin-bottom:1.5rem;
     font-family:monospace;font-size:0.75rem;color:#4dff8a">
    ◈ ANALYSING · {city_name.upper()} · {cur['temperature_2m']:.1f}°C · {cur['relative_humidity_2m']}% RH ·
    AQI {aq_cur.get('european_aqi','N/A')} · ENV SCORE {es}/100
</div>""", unsafe_allow_html=True)

    crops = recommend_crops(weather)
    for emoji,name,compat,reason,care in crops:
        cc,_ = score_grade(compat)
        st.markdown(f"""
<div class="crop-card">
    <div class="crop-emoji-big">{emoji}</div>
    <div class="crop-info">
        <div class="crop-title">{name}</div>
        <div class="crop-reason">{reason}</div>
        <div class="crop-care">▸ {care}</div>
    </div>
    <div class="crop-compat-ring">
        {mini_ring(compat, cc)}
    </div>
</div>""", unsafe_allow_html=True)

    st.markdown("""<div class="av-section">
        <div class="av-section-badge">Precision Management Plan</div>
        <div class="av-section-line"></div>
    </div>""", unsafe_allow_html=True)

    opts=[f"{e} {n}" for e,n,*_ in crops] if crops else ["No crops"]
    sel=st.selectbox("Select crop", opts)

    if st.button("▶ GENERATE PLAN", type="primary") and crops:
        with st.spinner("Building precision agriculture plan..."):
            result=ask_groq(
                f"Precision agriculture management plan for {sel} in {city_name}, {country}.\n"
                f"Conditions: {cur['temperature_2m']:.1f}°C, {cur['relative_humidity_2m']}% RH, "
                f"UV {cur.get('uv_index',0) or 0:.0f}, Wind {cur['wind_speed_10m']:.1f}km/h, "
                f"AQI {aq_cur.get('european_aqi','N/A')}, PM2.5 {aq_cur.get('pm2_5','N/A')}μg/m³, "
                f"Pollution Score {ps}/100, Env Score {es}/100.\n\n"
                f"Include: 1)Precision sowing protocol 2)Smart irrigation with exact quantities "
                f"3)NPK nutrient timeline 4)IPM pest monitoring 5)Pollution stress mitigation "
                f"6)Yield optimisation 7)Harvest timeline 8)Risk contingencies",
                system="You are a precision agriculture specialist. Provide specific, quantitative recommendations."
            )
        st.markdown(f'<div class="av-ai-box"><div class="av-ai-box-tag">MANAGEMENT PLAN</div>{result.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════
# TAB 4 — SIMULATION
# ══════════════════════════════════════════
with tab4:
    st.markdown("""<div class="av-section">
        <div class="av-section-badge">Farm Digital Twin · Scenario Engine</div>
        <div class="av-section-line"></div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
<div style="padding:1rem 1.2rem;background:rgba(0,255,100,0.03);
     border:1px solid rgba(0,255,100,0.08);border-radius:10px;margin-bottom:1.5rem;
     font-size:0.78rem;color:#4dff8a;line-height:1.7">
    Adjust environmental parameters to simulate future farming scenarios.
    The AI models potential outcomes and strategic responses.
</div>""", unsafe_allow_html=True)

    s1,s2=st.columns(2)
    with s1:
        temp_d=st.slider("Temperature Δ (°C)",-10,+15,0)
        rain_d=st.slider("Rainfall Δ (%)",-90,+150,0)
    with s2:
        aqi_d=st.slider("AQI Δ",-50,+200,0)
        sim_crop=st.text_input("Crop to simulate",placeholder="e.g. Rice, Wheat, Tomato...")

    # Show simulated values
    sim_t = cur["temperature_2m"]+temp_d
    base_r = sum(p for p in daily["precipitation_sum"] if p)/7
    sim_r = base_r*(1+rain_d/100)
    sim_aqi = (aq_cur.get("european_aqi") or 30)+aqi_d

    sv1,sv2,sv3 = st.columns(3)
    for col,lbl,baseline,simval,unit in [
        (sv1,"TEMPERATURE",cur["temperature_2m"],sim_t,"°C"),
        (sv2,"DAILY RAINFALL",base_r,sim_r,"mm"),
        (sv3,"EU AQI",aq_cur.get("european_aqi",30),sim_aqi,""),
    ]:
        delta = simval-baseline
        dc = "#00ff64" if delta<=0 else "#ff4444"
        with col:
            st.markdown(f"""
<div class="av-panel">
    <div class="av-panel-label">{lbl}</div>
    <div><span class="av-panel-value">{simval:.1f}</span><span class="av-panel-unit">{unit}</span></div>
    <div class="av-panel-sub" style="color:{dc}">{'▲' if delta>0 else '▼'} {abs(delta):.1f}{unit} from baseline</div>
</div>""", unsafe_allow_html=True)

    if st.button("▶ RUN SIMULATION", type="primary"):
        with st.spinner("Running farm simulation model..."):
            result=ask_groq(
                f"Farm simulation for {city_name}, {country}.\n"
                f"BASELINE: Temp {cur['temperature_2m']:.1f}°C, Rain {base_r:.1f}mm/day, "
                f"AQI {aq_cur.get('european_aqi','N/A')}, Env Score {es}/100\n"
                f"SCENARIO: Temp {sim_t:.1f}°C (+{temp_d}°C), Rain {sim_r:.1f}mm/day ({rain_d:+}%), "
                f"AQI {sim_aqi:.0f} ({aqi_d:+})\n"
                f"{'Target crop: '+sim_crop if sim_crop else ''}\n\n"
                f"Provide: 1)Quantified risk delta vs baseline (%) 2)Predicted yield impact "
                f"3)Water/resource changes 4)Adaptive strategies 5)Early warning signals "
                f"6)Best/worst case projections with probabilities",
                system="You are an agricultural simulation expert. Provide quantitative projections with specific numbers and probabilities."
            )
        st.markdown(f'<div class="av-ai-box"><div class="av-ai-box-tag">SIMULATION RESULTS</div>{result.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════
# TAB 5 — FIELD AI
# ══════════════════════════════════════════
with tab5:
    st.markdown("""<div class="av-section">
        <div class="av-section-badge">Intelligent Field Assistant</div>
        <div class="av-section-line"></div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""
<div style="padding:0.8rem 1.2rem;background:rgba(0,255,100,0.03);
     border:1px solid rgba(0,255,100,0.08);border-radius:10px;margin-bottom:1rem;
     font-family:monospace;font-size:0.72rem;color:#4dff8a">
    ◈ CONTEXT LOADED · {city_name}, {country} · {cur['temperature_2m']:.1f}°C ·
    {cur['relative_humidity_2m']}% RH · AQI {aq_cur.get('european_aqi','N/A')} · ENV {es}/100
</div>""", unsafe_allow_html=True)

    focus=st.text_input("Crop Focus", placeholder="e.g. Rice, Tomato, Groundnut...")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history=[]

    if not st.session_state.chat_history:
        st.markdown("""
<div style="font-family:'Orbitron',sans-serif;font-size:0.55rem;
     letter-spacing:0.2em;color:#00cc50;margin-bottom:0.7rem">
    SUGGESTED QUERIES
</div>""", unsafe_allow_html=True)
        sq=st.columns(2)
        for i,q in enumerate([
            "What pests should I watch for now?",
            "How much water does my crop need?",
            "Is current AQI harming my crops?",
            "What fertiliser should I apply?"
        ]):
            with sq[i%2]:
                st.markdown(f"""
<div style="padding:0.6rem 0.9rem;background:rgba(0,255,100,0.04);
     border:1px solid rgba(0,255,100,0.1);border-radius:8px;
     font-size:0.75rem;color:#4dff8a;margin-bottom:0.5rem;
     font-family:monospace">▸ {q}</div>""", unsafe_allow_html=True)

    for msg in st.session_state.chat_history:
        if msg["role"]=="user":
            st.markdown(f"""
<div class="chat-wrap chat-user-wrap">
    <div class="chat-msg chat-user">
        <div class="chat-label-user">YOU</div>
        {msg['content']}
    </div>
</div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
<div class="chat-wrap chat-ai-wrap">
    <div class="chat-msg chat-ai">
        <div class="chat-label-ai">◈ AEROVEDA AI</div>
        {msg['content']}
    </div>
</div>""", unsafe_allow_html=True)

    user_in=st.chat_input("Ask about crops, soil, pests, irrigation, pollution effects...")
    if user_in:
        st.session_state.chat_history.append({"role":"user","content":user_in})
        with st.spinner("Processing..."):
            reply=ask_groq_chat(
                st.session_state.chat_history,
                system=f"""You are Aeroveda's intelligent field assistant — expert agronomist with real-time data awareness.
Location: {city_name}, {country} ({lat:.4f}°N, {lon:.4f}°E)
Temperature: {cur['temperature_2m']:.1f}°C | Humidity: {cur['relative_humidity_2m']}%
Wind: {cur['wind_speed_10m']:.1f}km/h | UV: {cur.get('uv_index',0) or 0:.0f}
Conditions: {wdesc(cur['weather_code'])}
EU AQI: {aq_cur.get('european_aqi','N/A')} | PM2.5: {aq_cur.get('pm2_5','N/A')}μg/m³
Pollution Score: {ps if ps is not None else 'N/A'}/100 | Env Score: {es}/100
{'Crop focus: '+focus if focus else ''}
Be precise, contextual, and practical. Use bullet points. Reference the actual conditions above.""",
                max_tokens=800
            )
        st.session_state.chat_history.append({"role":"assistant","content":reply})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("↺ CLEAR SESSION"):
            st.session_state.chat_history=[]
            st.rerun()
