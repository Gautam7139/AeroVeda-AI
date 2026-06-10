import streamlit as st
import streamlit.components.v1 as components
import requests
import json
from datetime import datetime
import pandas as pd
from groq import Groq
import math
import base64

st.set_page_config(
    page_title="AEROVEDA // AGR-OS v2.0",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── GPS from query params ─────────────────────────────────────────────────────
params = st.query_params
gps_raw = params.get("gps", "")
if gps_raw and "," in str(gps_raw):
    try:
        parts = str(gps_raw).split(",")
        r = requests.get(
            f"https://nominatim.openstreetmap.org/reverse?lat={parts[0]}&lon={parts[1]}&format=json",
            headers={"User-Agent": "Aeroveda/4.0"}, timeout=6
        )
        d = r.json()
        detected = (d.get("address",{}).get("city") or
                    d.get("address",{}).get("town") or
                    d.get("address",{}).get("village",""))
        if detected:
            st.session_state["city"] = detected
        st.query_params.clear()
    except: pass

# ─────────────────────────────────────────────────────────────────────────────
# MASTER CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&family=Share+Tech+Mono&display=swap');

*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body,[class*="css"]{font-family:'Rajdhani',sans-serif;background:#000!important;color:#00ff88}

/* ══ DEEP SPACE BACKGROUND ══ */
.stApp{
  background:
    radial-gradient(ellipse at 15% 25%,rgba(0,255,100,0.04) 0%,transparent 45%),
    radial-gradient(ellipse at 85% 75%,rgba(0,180,80,0.03) 0%,transparent 40%),
    radial-gradient(ellipse at 50% 50%,rgba(0,50,20,0.15) 0%,transparent 70%),
    #000!important;
  overflow-x:hidden;
}

/* Scanline effect */
.stApp::before{
  content:'';position:fixed;inset:0;pointer-events:none;z-index:9999;
  background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,0.03) 2px,rgba(0,0,0,0.03) 4px);
  animation:scanlines 8s linear infinite;
}
@keyframes scanlines{0%{background-position:0 0}100%{background-position:0 100px}}

/* Hex grid */
.stApp::after{
  content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='56' height='100'%3E%3Cpath d='M28 2L54 16v28L28 58 2 44V16z' fill='none' stroke='rgba(0,255,100,0.025)' stroke-width='0.5'/%3E%3C/svg%3E");
  opacity:0.7;
}

.main .block-container{
  padding:0 2rem 5rem!important;
  max-width:1600px!important;
  position:relative;z-index:1;
}

/* ══ COMMAND HEADER ══ */
.cmd-header{
  position:relative;
  padding:1.5rem 2rem;
  border-bottom:1px solid rgba(0,255,100,0.15);
  display:flex;align-items:center;justify-content:space-between;
  background:linear-gradient(90deg,rgba(0,20,8,0.95),rgba(0,10,4,0.98));
  margin:0 -2rem 2rem;
  overflow:hidden;
}
.cmd-header::before{
  content:'';position:absolute;bottom:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,#00ff64,rgba(0,255,100,0.3),transparent);
  animation:sweep 4s ease-in-out infinite;
}
@keyframes sweep{0%,100%{opacity:0.4}50%{opacity:1}}

.logo-block{display:flex;flex-direction:column;gap:3px}
.logo-text{
  font-family:'Orbitron',sans-serif;
  font-size:1.8rem;font-weight:900;
  letter-spacing:0.2em;color:#fff;
  text-shadow:0 0 20px rgba(0,255,100,0.6),0 0 40px rgba(0,255,100,0.2);
}
.logo-text span{color:#00ff64}
.logo-sub{
  font-family:'Share Tech Mono',monospace;
  font-size:0.6rem;letter-spacing:0.25em;color:#00cc50;
}
.sys-status{
  display:flex;align-items:center;gap:20px;
  font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:#00cc50;
}
.status-item{display:flex;align-items:center;gap:6px}
.status-dot{
  width:7px;height:7px;border-radius:50%;background:#00ff64;
  box-shadow:0 0 8px #00ff64;
  animation:blink 1.4s ease-in-out infinite;
}
.status-dot.warn{background:#ffd700;box-shadow:0 0 8px #ffd700}
@keyframes blink{0%,100%{opacity:1}50%{opacity:0.3}}
.location-tag{
  display:flex;align-items:center;gap:8px;
  background:rgba(0,255,100,0.06);
  border:1px solid rgba(0,255,100,0.2);
  border-radius:4px;padding:6px 14px;
  font-family:'Share Tech Mono',monospace;font-size:0.7rem;color:#00ff88;
}

/* ══ SECTION HEADERS ══ */
.av-sec{
  display:flex;align-items:center;gap:12px;
  margin:2rem 0 1.2rem;
}
.av-sec-tag{
  font-family:'Orbitron',sans-serif;font-size:0.58rem;font-weight:700;
  letter-spacing:0.2em;color:#000;
  background:linear-gradient(135deg,#00ff64,#00cc40);
  padding:4px 12px;border-radius:2px;white-space:nowrap;
}
.av-sec-line{
  flex:1;height:1px;
  background:linear-gradient(90deg,rgba(0,255,100,0.4),transparent);
}
.av-sec-code{
  font-family:'Share Tech Mono',monospace;font-size:0.58rem;
  color:rgba(0,255,100,0.4);white-space:nowrap;
}

/* ══ HOLOGRAPHIC PANELS ══ */
.holo-panel{
  background:linear-gradient(135deg,rgba(0,18,6,0.95),rgba(0,8,3,0.98));
  border:1px solid rgba(0,255,100,0.12);
  border-radius:8px;
  position:relative;overflow:hidden;
  backdrop-filter:blur(20px);
  transition:all 0.3s;
}
.holo-panel:hover{
  border-color:rgba(0,255,100,0.3);
  box-shadow:0 0 30px rgba(0,255,100,0.06),inset 0 0 30px rgba(0,255,100,0.02);
}
.holo-panel::before{
  content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(0,255,100,0.5),transparent);
}
.holo-panel::after{
  content:'';position:absolute;
  top:-50%;right:-50%;width:100%;height:100%;
  background:radial-gradient(circle,rgba(0,255,100,0.03),transparent 60%);
  pointer-events:none;
}
.panel-pad{padding:1.2rem 1.4rem}
.panel-label{
  font-family:'Share Tech Mono',monospace;font-size:0.58rem;
  letter-spacing:0.22em;color:#00cc50;margin-bottom:6px;
}
.panel-value{
  font-family:'Orbitron',sans-serif;font-size:2rem;
  font-weight:700;color:#fff;line-height:1;
  text-shadow:0 0 15px rgba(0,255,100,0.3);
}
.panel-unit{font-size:0.75rem;color:#00ff64;margin-left:3px;font-family:'Rajdhani',sans-serif}
.panel-sub{font-size:0.68rem;color:#009940;margin-top:5px;font-family:'Share Tech Mono',monospace}

/* ══ SCORE RINGS ══ */
.score-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:2rem}
.score-cell{
  background:linear-gradient(135deg,rgba(0,18,6,0.95),rgba(0,8,3,0.98));
  border:1px solid rgba(0,255,100,0.12);
  border-radius:8px;padding:1.5rem 1rem;
  text-align:center;position:relative;overflow:hidden;
  transition:all 0.3s;
}
.score-cell:hover{border-color:rgba(0,255,100,0.3);transform:translateY(-2px)}
.score-cell::before{
  content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(0,255,100,0.4),transparent);
}
.ring-wrap{position:relative;width:130px;height:130px;margin:0 auto}
.ring-wrap svg{width:130px;height:130px}
.ring-center{
  position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
  text-align:center;
}
.ring-num{
  font-family:'Orbitron',sans-serif;font-size:1.9rem;font-weight:800;color:#fff;
  line-height:1;
}
.ring-denom{font-size:0.55rem;color:#00cc50;font-family:'Share Tech Mono',monospace;margin-top:2px}
.score-name{
  font-family:'Orbitron',sans-serif;font-size:0.55rem;font-weight:700;
  letter-spacing:0.18em;margin-top:10px;color:#00cc50;
}
.score-grade{
  font-family:'Orbitron',sans-serif;font-size:0.75rem;font-weight:700;
  margin-top:3px;letter-spacing:0.1em;
}

/* ══ MAP CONTAINER ══ */
.map-shell{
  background:rgba(0,8,3,0.98);
  border:1px solid rgba(0,255,100,0.18);
  border-radius:8px;overflow:hidden;position:relative;
}
.map-hud{
  position:absolute;top:12px;left:12px;right:12px;
  display:flex;justify-content:space-between;align-items:flex-start;
  pointer-events:none;z-index:10;
}
.map-badge{
  background:rgba(0,10,4,0.92);border:1px solid rgba(0,255,100,0.3);
  border-radius:4px;padding:5px 10px;
  font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:#00ff64;
}
.map-coords{
  background:rgba(0,10,4,0.92);border:1px solid rgba(0,255,100,0.2);
  border-radius:4px;padding:5px 10px;
  font-family:'Share Tech Mono',monospace;font-size:0.58rem;color:#00cc50;
  text-align:right;
}

/* ══ POLLUTANT BARS ══ */
.pol-wrap{margin-bottom:1.1rem}
.pol-head{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:5px}
.pol-name{font-family:'Share Tech Mono',monospace;font-size:0.62rem;letter-spacing:0.12em;color:#00cc50}
.pol-val{font-family:'Orbitron',monospace;font-size:0.82rem;font-weight:600}
.pol-track{height:3px;background:rgba(0,255,100,0.07);border-radius:99px;position:relative}
.pol-bar{height:3px;border-radius:99px;position:relative;transition:width 1.2s ease}
.pol-bar::after{
  content:'';position:absolute;right:-1px;top:-3px;
  width:9px;height:9px;border-radius:50%;background:currentColor;
  box-shadow:0 0 8px currentColor,0 0 16px currentColor;
}

/* ══ ALERT CARDS ══ */
.alert-card{
  display:flex;gap:14px;padding:1rem 1.3rem;
  border-radius:6px;margin-bottom:0.6rem;position:relative;overflow:hidden;
}
.alert-card::before{content:'';position:absolute;left:0;top:0;bottom:0;width:2px}
.alert-crisis{background:rgba(255,20,20,0.06);border:1px solid rgba(255,20,20,0.2)}
.alert-crisis::before{background:linear-gradient(180deg,#ff1414,#cc0000)}
.alert-warning{background:rgba(255,200,0,0.05);border:1px solid rgba(255,200,0,0.18)}
.alert-warning::before{background:linear-gradient(180deg,#ffd700,#cc9900)}
.alert-safe{background:rgba(0,255,100,0.04);border:1px solid rgba(0,255,100,0.15)}
.alert-safe::before{background:linear-gradient(180deg,#00ff64,#00cc44)}
.alert-icon{font-size:1.2rem;flex-shrink:0;padding-top:1px}
.alert-title{
  font-family:'Orbitron',sans-serif;font-size:0.6rem;font-weight:700;
  letter-spacing:0.18em;margin-bottom:4px;
}
.alert-crisis .alert-title{color:#ff5555}
.alert-warning .alert-title{color:#ffd700}
.alert-safe .alert-title{color:#00ff64}
.alert-msg{font-size:0.8rem;line-height:1.6}
.alert-crisis .alert-msg{color:#ffaaaa}
.alert-warning .alert-msg{color:#fff3aa}
.alert-safe .alert-msg{color:#aaffcc}

/* ══ CROP CARDS ══ */
.crop-row{
  display:flex;align-items:center;gap:1.2rem;
  padding:1rem 1.4rem;
  background:linear-gradient(135deg,rgba(0,15,5,0.9),rgba(0,8,3,0.95));
  border:1px solid rgba(0,255,100,0.1);border-radius:6px;
  margin-bottom:0.6rem;position:relative;overflow:hidden;
  transition:all 0.3s;
}
.crop-row:hover{border-color:rgba(0,255,100,0.3);transform:translateX(4px)}
.crop-row::before{
  content:'';position:absolute;left:0;top:0;bottom:0;width:2px;
  background:linear-gradient(180deg,#00ff64,rgba(0,255,100,0.2));
}
.crop-icon{font-size:2rem;flex-shrink:0}
.crop-body{flex:1}
.crop-name-big{
  font-family:'Orbitron',sans-serif;font-size:0.9rem;font-weight:700;
  color:#fff;letter-spacing:0.06em;
}
.crop-reason{font-size:0.75rem;color:#00cc50;margin-top:3px}
.crop-care{font-size:0.65rem;color:#007730;margin-top:4px;font-family:'Share Tech Mono',monospace}
.crop-pct-wrap{flex-shrink:0;text-align:center}

/* ══ CHAT ══ */
.chat-user-row{display:flex;justify-content:flex-end;margin-bottom:0.7rem}
.chat-ai-row{display:flex;justify-content:flex-start;margin-bottom:0.7rem}
.chat-bubble{padding:0.9rem 1.2rem;border-radius:8px;font-size:0.83rem;line-height:1.7;max-width:84%}
.chat-user-bub{
  background:rgba(0,255,100,0.07);border:1px solid rgba(0,255,100,0.18);
  color:#d0ffe0;border-radius:8px 8px 2px 8px;
}
.chat-ai-bub{
  background:rgba(0,12,4,0.95);border:1px solid rgba(0,255,100,0.1);
  color:#b8ffcf;border-radius:8px 8px 8px 2px;
}
.chat-from{
  font-family:'Share Tech Mono',monospace;font-size:0.55rem;
  letter-spacing:0.2em;margin-bottom:5px;color:#00cc50;
}
.chat-from-u{text-align:right;color:#00ff64}

/* ══ AI OUTPUT BOX ══ */
.ai-out{
  background:rgba(0,8,3,0.97);border:1px solid rgba(0,255,100,0.15);
  border-radius:8px;padding:1.8rem;margin-top:1rem;
  color:#c0ffd4;line-height:1.9;font-size:0.86rem;
  position:relative;
}
.ai-out-tag{
  position:absolute;top:-10px;left:18px;
  background:#000;padding:0 10px;
  font-family:'Orbitron',sans-serif;font-size:0.52rem;
  letter-spacing:0.22em;color:#00ff64;font-weight:700;
}

/* ══ TABS ══ */
.stTabs [data-baseweb="tab-list"]{
  background:rgba(0,8,3,0.95)!important;
  border-bottom:1px solid rgba(0,255,100,0.12)!important;
  gap:0!important;padding:0 1rem!important;
}
.stTabs [data-baseweb="tab"]{
  font-family:'Orbitron',sans-serif!important;font-size:0.58rem!important;
  letter-spacing:0.18em!important;text-transform:uppercase!important;
  color:rgba(0,255,100,0.5)!important;padding:1rem 1.4rem!important;
  background:transparent!important;border:none!important;font-weight:600!important;
}
.stTabs [aria-selected="true"]{
  color:#00ff64!important;
  border-bottom:2px solid #00ff64!important;
  background:rgba(0,255,100,0.04)!important;
  text-shadow:0 0 10px rgba(0,255,100,0.5)!important;
}
.stTabs [data-baseweb="tab-panel"]{padding:2rem 0 0!important;background:transparent!important}

/* ══ INPUTS ══ */
.stTextInput input{
  background:rgba(0,12,4,0.9)!important;
  border:1px solid rgba(0,255,100,0.2)!important;
  border-radius:6px!important;color:#d0ffe0!important;
  font-family:'Rajdhani',sans-serif!important;font-size:0.95rem!important;
}
.stTextInput input:focus{border-color:rgba(0,255,100,0.5)!important;box-shadow:0 0 0 2px rgba(0,255,100,0.07)!important}
.stTextInput label{
  color:#00cc50!important;font-family:'Share Tech Mono',monospace!important;
  font-size:0.6rem!important;letter-spacing:0.2em!important;text-transform:uppercase!important;
}

/* ══ BUTTONS ══ */
.stButton button{
  background:rgba(0,255,100,0.06)!important;
  border:1px solid rgba(0,255,100,0.25)!important;
  color:#00ff64!important;border-radius:4px!important;
  font-family:'Orbitron',sans-serif!important;font-size:0.58rem!important;
  letter-spacing:0.15em!important;font-weight:700!important;
  transition:all 0.2s!important;
}
.stButton button:hover{
  background:rgba(0,255,100,0.14)!important;
  border-color:#00ff64!important;color:#fff!important;
  box-shadow:0 0 20px rgba(0,255,100,0.2)!important;
}
button[kind="primary"]{
  background:linear-gradient(135deg,rgba(0,100,40,0.8),rgba(0,180,70,0.6))!important;
  border:1px solid #00ff64!important;color:#fff!important;
  box-shadow:0 0 20px rgba(0,255,100,0.2)!important;
}

/* ══ SELECT / SLIDER ══ */
[data-baseweb="select"]>div{
  background:rgba(0,12,4,0.9)!important;
  border-color:rgba(0,255,100,0.2)!important;
  color:#d0ffe0!important;border-radius:6px!important;
}
.stSlider [data-testid="stThumbValue"]{
  color:#00ff64!important;font-family:'Share Tech Mono',monospace!important;
}

/* ══ FILE UPLOADER ══ */
[data-testid="stFileUploader"]{
  background:rgba(0,12,4,0.8)!important;
  border:1px dashed rgba(0,255,100,0.25)!important;
  border-radius:8px!important;
}
[data-testid="stFileUploader"] label{color:#00cc50!important}

/* ══ DATAFRAME ══ */
[data-testid="stDataFrameResizable"]{border:1px solid rgba(0,255,100,0.1)!important;border-radius:6px!important}

/* ══ SIDEBAR ══ */
[data-testid="stSidebar"]{
  background:rgba(0,4,2,0.99)!important;
  border-right:1px solid rgba(0,255,100,0.1)!important;
}

/* ══ MISC ══ */
#MainMenu,footer,header{visibility:hidden}
::-webkit-scrollbar{width:3px}
::-webkit-scrollbar-thumb{background:rgba(0,255,100,0.2);border-radius:99px}
.stSpinner>div{border-top-color:#00ff64!important}

/* ══ PROGRESS/STATS BAR ══ */
.stat-row{display:flex;align-items:center;gap:10px;margin-bottom:0.8rem}
.stat-label{font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:#00cc50;width:120px;flex-shrink:0}
.stat-track{flex:1;height:4px;background:rgba(0,255,100,0.07);border-radius:99px;overflow:visible;position:relative}
.stat-fill{height:4px;border-radius:99px}
.stat-val{font-family:'Orbitron',sans-serif;font-size:0.7rem;font-weight:700;width:40px;text-align:right;flex-shrink:0}

/* ══ TERRAIN MAP ══ */
.terrain-wrap{
  width:100%;height:480px;
  background:rgba(0,8,3,0.98);
  border:1px solid rgba(0,255,100,0.15);
  border-radius:8px;overflow:hidden;position:relative;
}
.layer-panel{
  position:absolute;top:12px;right:12px;
  background:rgba(0,8,3,0.92);border:1px solid rgba(0,255,100,0.2);
  border-radius:6px;padding:10px;z-index:20;width:160px;
}
.layer-title{font-family:'Orbitron',sans-serif;font-size:0.52rem;letter-spacing:0.18em;color:#00cc50;margin-bottom:8px}
.layer-item{
  display:flex;align-items:center;gap:6px;
  font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:#00ff88;
  padding:3px 0;cursor:pointer;
}
.layer-dot{width:8px;height:8px;border-radius:2px;flex-shrink:0}

/* ══ CORNER DECORATIONS ══ */
.corner-tl,.corner-tr,.corner-bl,.corner-br{position:absolute;width:16px;height:16px;pointer-events:none}
.corner-tl{top:8px;left:8px;border-top:2px solid rgba(0,255,100,0.4);border-left:2px solid rgba(0,255,100,0.4)}
.corner-tr{top:8px;right:8px;border-top:2px solid rgba(0,255,100,0.4);border-right:2px solid rgba(0,255,100,0.4)}
.corner-bl{bottom:8px;left:8px;border-bottom:2px solid rgba(0,255,100,0.4);border-left:2px solid rgba(0,255,100,0.4)}
.corner-br{bottom:8px;right:8px;border-bottom:2px solid rgba(0,255,100,0.4);border-right:2px solid rgba(0,255,100,0.4)}

/* ══ TICKER ══ */
.ticker-wrap{
  background:rgba(0,8,3,0.95);border-top:1px solid rgba(0,255,100,0.12);
  border-bottom:1px solid rgba(0,255,100,0.12);
  padding:6px 0;overflow:hidden;white-space:nowrap;margin:0 -2rem 2rem;
}
.ticker-inner{
  display:inline-block;
  animation:ticker 30s linear infinite;
  font-family:'Share Tech Mono',monospace;font-size:0.62rem;color:#00cc50;
  letter-spacing:0.1em;
}
@keyframes ticker{0%{transform:translateX(100vw)}100%{transform:translateX(-100%)}}
.ticker-sep{color:#00ff64;margin:0 20px}
</style>
""", unsafe_allow_html=True)

# ─── Helpers ─────────────────────────────────────────────────────────────────
@st.cache_resource
def get_groq():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

def ask_groq(prompt, system="You are an expert agricultural AI.", max_tokens=1000):
    try:
        r = get_groq().chat.completions.create(
            model="llama-3.3-70b-versatile", max_tokens=max_tokens,
            messages=[{"role":"system","content":system},{"role":"user","content":prompt}])
        return r.choices[0].message.content
    except Exception as e: return f"Error: {e}"

def ask_groq_chat(msgs, system, max_tokens=800):
    try:
        r = get_groq().chat.completions.create(
            model="llama-3.3-70b-versatile", max_tokens=max_tokens,
            messages=[{"role":"system","content":system}]+msgs)
        return r.choices[0].message.content
    except Exception as e: return f"Error: {e}"

@st.cache_data(ttl=1800)
def fetch_weather(lat, lon):
    url=(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
         f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
         f"precipitation,rain,wind_speed_10m,wind_direction_10m,"
         f"surface_pressure,cloud_cover,uv_index,weather_code"
         f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,"
         f"wind_speed_10m_max,uv_index_max,precipitation_probability_max"
         f"&forecast_days=7&timezone=auto")
    try:
        r=requests.get(url,timeout=20); r.raise_for_status(); return r.json()
    except Exception as e: st.error(f"Weather unavailable: {e}"); return None

@st.cache_data(ttl=1800)
def fetch_aq(lat, lon):
    url=(f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}"
         f"&current=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,european_aqi,us_aqi")
    try:
        r=requests.get(url,timeout=20); r.raise_for_status(); return r.json()
    except: return None

@st.cache_data(ttl=3600)
def geocode(city):
    try:
        r=requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json",timeout=10)
        d=r.json()
        if d.get("results"):
            res=d["results"][0]
            return res["latitude"],res["longitude"],res.get("country",""),res.get("name",city)
        return None
    except: return None

def w_score(w):
    c=w["current"]; s=100
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

def p_score(aq):
    if not aq: return None
    aqi=aq.get("current",{}).get("european_aqi") or aq.get("current",{}).get("us_aqi")
    if aqi is None: return None
    return max(0,min(100,round(100-aqi)))

def e_score(ws,ps):
    if ps is None: return ws
    return max(0,min(100,round(ws*0.55+ps*0.45)))

def grade(s):
    s=s if s is not None else 0
    if s>=80: return "#00ff64","OPTIMAL"
    elif s>=65: return "#4dff8a","GOOD"
    elif s>=45: return "#ffd700","MODERATE"
    elif s>=25: return "#ff8c00","STRESSED"
    else: return "#ff3030","CRITICAL"

def bcol(v,g,b):
    if v<=g: return "#00ff64"
    elif v<=b: return "#ffd700"
    else: return "#ff4444"

WMO={0:"CLEAR SKY",1:"MAINLY CLEAR",2:"PARTLY CLOUDY",3:"OVERCAST",
     45:"FOG",51:"LIGHT DRIZZLE",53:"DRIZZLE",55:"HEAVY DRIZZLE",
     61:"SLIGHT RAIN",63:"MODERATE RAIN",65:"HEAVY RAIN",
     80:"SHOWERS",81:"MODERATE SHOWERS",82:"VIOLENT SHOWERS",
     95:"THUNDERSTORM",96:"THUNDERSTORM+HAIL"}
def wdesc(c): return WMO.get(c,"UNKNOWN")

def ring(score, color, sz=130, sw=9):
    v=score if score is not None else 0
    r=(sz/2)-sw; circ=2*math.pi*r; dash=(v/100)*circ
    gid=f"g{v}{sz}"
    return f"""<svg width="{sz}" height="{sz}" viewBox="0 0 {sz} {sz}">
  <defs>
    <filter id="{gid}"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <linearGradient id="lg{gid}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{color};stop-opacity:1"/>
      <stop offset="100%" style="stop-color:{color};stop-opacity:0.6"/>
    </linearGradient>
  </defs>
  <circle cx="{sz/2}" cy="{sz/2}" r="{r}" fill="none" stroke="rgba(0,255,100,0.06)" stroke-width="{sw}"/>
  <circle cx="{sz/2}" cy="{sz/2}" r="{r}" fill="none"
    stroke="url(#lg{gid})" stroke-width="{sw}" stroke-linecap="round"
    stroke-dasharray="{dash:.1f} {circ:.1f}"
    transform="rotate(-90 {sz/2} {sz/2})" filter="url(#{gid})"/>
  <circle cx="{sz/2}" cy="{sz/2}" r="{r-sw}" fill="rgba(0,255,100,0.01)" stroke="rgba(0,255,100,0.04)" stroke-width="0.5"/>
</svg>"""

def mini_ring(score, color="#00ff64", sz=65):
    r=(sz/2)-5; circ=2*math.pi*r; dash=(score/100)*circ
    return f"""<svg width="{sz}" height="{sz}" viewBox="0 0 {sz} {sz}">
  <circle cx="{sz/2}" cy="{sz/2}" r="{r}" fill="none" stroke="rgba(0,255,100,0.07)" stroke-width="4"/>
  <circle cx="{sz/2}" cy="{sz/2}" r="{r}" fill="none" stroke="{color}" stroke-width="4"
    stroke-linecap="round" stroke-dasharray="{dash:.1f} {circ:.1f}"
    transform="rotate(-90 {sz/2} {sz/2})"/>
  <text x="{sz/2}" y="{sz/2+4}" text-anchor="middle"
    font-family="Orbitron,sans-serif" font-size="11" font-weight="800" fill="{color}">{score}</text>
</svg>"""

def crises(w, aq_cur):
    alerts=[]
    daily=w["daily"]
    if aq_cur:
        aqi=aq_cur.get("european_aqi") or aq_cur.get("us_aqi")
        if aqi and aqi>80: alerts.append(("crisis","AIR QUALITY CRISIS",f"AQI {aqi} — Hazardous pollution. Severe agricultural and health risk detected."))
        elif aqi and aqi>50: alerts.append(("warning","POLLUTION ADVISORY",f"AQI {aqi} — Poor air quality. Sensitive crop stress likely."))
    hot=sum(1 for t in daily["temperature_2m_max"] if t and t>38)
    if hot>=3: alerts.append(("crisis","HEAT WAVE DETECTED",f"{hot} consecutive days above 38°C. Extreme crop stress probability HIGH."))
    elif hot>=1: alerts.append(("warning","HEAT ADVISORY",f"{hot} day(s) above 38°C forecast. Increase irrigation frequency."))
    rain=sum(p for p in daily["precipitation_sum"] if p is not None)
    if rain<2: alerts.append(("crisis","DROUGHT RISK ACTIVE","Near-zero rainfall over 7-day window. Emergency irrigation protocols recommended."))
    elif rain<8: alerts.append(("warning","LOW RAINFALL WARNING","Below-threshold precipitation. Supplemental irrigation required."))
    heavy=sum(1 for p in daily["precipitation_sum"] if p and p>25)
    if heavy>=2: alerts.append(("crisis","FLOOD PROBABILITY HIGH",f"{heavy} extreme rainfall days forecast. Severe waterlogging and crop loss risk."))
    elif heavy==1: alerts.append(("warning","HEAVY RAIN ALERT","Intense rainfall day forecast. Clear drainage channels immediately."))
    maxw=max((v for v in daily["wind_speed_10m_max"] if v),default=0)
    if maxw>70: alerts.append(("crisis","STORM WARNING",f"Extreme gusts up to {maxw:.0f} km/h. Secure all crop infrastructure."))
    elif maxw>45: alerts.append(("warning","HIGH WIND ADVISORY",f"Wind speeds up to {maxw:.0f} km/h expected."))
    if not alerts: alerts.append(("safe","SYSTEMS NOMINAL","No environmental crises detected in 7-day forecast window. Conditions stable."))
    return alerts

def crops(w):
    c=w["current"]; t=c["temperature_2m"]; h=c["relative_humidity_2m"]
    pl=[p for p in w["daily"]["precipitation_sum"] if p is not None]
    ar=sum(pl)/len(pl) if pl else 0
    result=[]
    if 20<=t<=38 and h>50:
        result.append(("🌾","RICE",95,"Optimal temperature-humidity matrix aligned","High water demand · 3–4 month cycle · transplant at 21 days"))
        result.append(("🌿","SUGARCANE",88,"Strong heat-humidity compatibility confirmed","Weekly deep irrigation · monthly NPK · 10–12 month cycle"))
    if 18<=t<=35:
        result.append(("🥜","GROUNDNUT",85,"Temperature envelope within optimal range","Sandy loam · well-drained · dry finish window required"))
        result.append(("🌽","MAIZE",82,"Thermophilic growth conditions satisfied","Moderate irrigation · high N input · 90-day rapid cycle"))
    if t>=25 and h<70:
        result.append(("🍅","TOMATO",78,"Warm-dry conditions matrix optimal","Consistent drip irrigation · stake support · blight protocol"))
        result.append(("🌶️","CHILLI",76,"Low humidity suppresses fungal pressure","Potassium-rich feed · drip preferred · 3–4 month harvest"))
    if t<22:
        result.append(("🥬","SPINACH",90,"Cool temperature threshold perfectly matched","Direct sow · 6–8 week harvest · high nitrogen feed"))
        result.append(("🥕","CARROT",84,"Root development optimised in cool soil","Deep loose bed · thin at 4cm · 70-day full cycle"))
        result.append(("🧅","ONION",80,"Bulb initiation favoured by cool dry air","Reduce water at bulbing stage · raised bed drainage"))
    if ar<3 and t>20:
        result.append(("🌻","SUNFLOWER",88,"Drought-tolerance profile matches conditions","Deep taproot system · minimal input · 80–95 day cycle"))
        result.append(("🫘","MOONG DAL",83,"Short-season drought-tolerant legume","Sandy loam · nitrogen fixation · 60–70 day cycle"))
    result.sort(key=lambda x:-x[2])
    return result[:5]

# ════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="font-family:'Orbitron',sans-serif;font-size:0.55rem;
         letter-spacing:0.25em;color:#00ff64;margin-bottom:1.5rem;font-weight:700">
        ◈ LOCATION NODE
    </div>""", unsafe_allow_html=True)

    components.html("""
    <style>
    #gb{width:100%;padding:10px;
      background:linear-gradient(135deg,rgba(0,255,100,0.06),rgba(0,180,60,0.1));
      border:1px solid rgba(0,255,100,0.28);border-radius:4px;
      color:#00ff64;font-family:'Orbitron',monospace;font-size:0.58rem;
      letter-spacing:0.18em;font-weight:700;cursor:pointer;transition:all 0.2s;
      text-transform:uppercase;}
    #gb:hover{background:rgba(0,255,100,0.16);box-shadow:0 0 16px rgba(0,255,100,0.2);color:#fff}
    #gs{font-family:monospace;font-size:0.68rem;color:#00cc50;
      margin-top:6px;min-height:16px;text-align:center}
    </style>
    <button id="gb" onclick="go()">⊕ ACQUIRE GPS LOCK</button>
    <div id="gs"></div>
    <script>
    function go(){
      var b=document.getElementById('gb'),s=document.getElementById('gs');
      b.innerText='⏳ ACQUIRING LOCK...';b.disabled=true;
      if(!navigator.geolocation){s.innerText='✗ GPS NOT AVAILABLE';s.style.color='#ff4444';b.innerText='⊕ ACQUIRE GPS LOCK';b.disabled=false;return}
      navigator.geolocation.getCurrentPosition(
        function(p){
          var la=p.coords.latitude.toFixed(6),lo=p.coords.longitude.toFixed(6);
          s.innerText='✓ LOCK: '+la+', '+lo;s.style.color='#00ff64';
          b.innerText='✓ GPS LOCKED';
          var u=window.parent.location.href.split('?')[0]+'?gps='+la+','+lo;
          window.parent.location.href=u;
        },
        function(e){
          s.style.color='#ff4444';
          var m={1:'PERMISSION DENIED',2:'SIGNAL UNAVAILABLE',3:'LOCK TIMEOUT'};
          s.innerText='✗ '+(m[e.code]||'UNKNOWN ERROR');
          b.innerText='⊕ ACQUIRE GPS LOCK';b.disabled=false;
        },
        {timeout:12000,enableHighAccuracy:true,maximumAge:0}
      );
    }
    </script>""", height=72)

    city_in = st.text_input("Manual Override", value=st.session_state.get("city","Bengaluru"), placeholder="City...")
    st.session_state["city"] = city_in

    st.markdown("""
    <div style="margin-top:2rem;padding-top:1.5rem;border-top:1px solid rgba(0,255,100,0.08)">
    <div style="font-family:'Orbitron',sans-serif;font-size:0.52rem;
         letter-spacing:0.22em;color:#00cc50;margin-bottom:0.8rem;font-weight:700">
      ACTIVE DATA FEEDS
    </div>
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.68rem;
         color:#4dff8a;line-height:2.2">
      ◦ OPEN-METEO WEATHER API<br>
      ◦ OPEN-METEO AIR QUALITY<br>
      ◦ NOMINATIM GEOCODING<br>
      ◦ GROQ · LLAMA-3.3-70B<br>
      ◦ OPENSTREETMAP TERRAIN
    </div>
    </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# FETCH
# ════════════════════════════════════════════════════════
geo = geocode(city_in)
if not geo:
    st.error(f"LOCATION NOT FOUND: {city_in}"); st.stop()

lat, lon, country, city_name = geo
weather = fetch_weather(lat, lon)
if not weather: st.stop()

aq      = fetch_aq(lat, lon)
cur     = weather["current"]
daily   = weather["daily"]
aq_cur  = aq.get("current",{}) if aq else {}
ws      = w_score(weather)
ps      = p_score(aq)
es      = e_score(ws, ps)
ag      = max(0,min(100,round(es*0.7+ws*0.3)))

now = datetime.now()

# ════════════════════════════════════════════════════════
# COMMAND HEADER
# ════════════════════════════════════════════════════════
st.markdown(f"""
<div class="cmd-header">
  <div class="logo-block">
    <div class="logo-text">AERO<span>VEDA</span></div>
    <div class="logo-sub">AGR-OS v2.0 · AGRICULTURAL INTELLIGENCE OPERATING SYSTEM</div>
  </div>
  <div class="sys-status">
    <div class="status-item"><div class="status-dot"></div>WEATHER FEED LIVE</div>
    <div class="status-item"><div class="status-dot"></div>AQ SENSORS ONLINE</div>
    <div class="status-item"><div class="status-dot"></div>AI ENGINE READY</div>
    <div class="status-item"><div class="status-dot {'warn' if es<45 else ''}"></div>ENV SCORE {es}</div>
  </div>
  <div class="location-tag">
    <div class="status-dot"></div>
    {city_name.upper()}, {country.upper()} &nbsp;·&nbsp; {lat:.4f}°N {lon:.4f}°E &nbsp;·&nbsp; {now.strftime('%H:%M:%S UTC')}
  </div>
</div>
""", unsafe_allow_html=True)

# TICKER
pm25_val = float(aq_cur.get("pm2_5",0) or 0)
ticker_data = (f"TEMP: {cur['temperature_2m']:.1f}°C "
               f"<span class='ticker-sep'>//</span> HUMIDITY: {cur['relative_humidity_2m']}% "
               f"<span class='ticker-sep'>//</span> WIND: {cur['wind_speed_10m']:.1f} KM/H "
               f"<span class='ticker-sep'>//</span> UV INDEX: {cur.get('uv_index',0) or 0:.0f} "
               f"<span class='ticker-sep'>//</span> PM2.5: {pm25_val:.1f} μG/M³ "
               f"<span class='ticker-sep'>//</span> CONDITIONS: {wdesc(cur['weather_code'])} "
               f"<span class='ticker-sep'>//</span> ENV SCORE: {es}/100 "
               f"<span class='ticker-sep'>//</span> AG POTENTIAL: {ag}/100 "
               f"<span class='ticker-sep'>//</span> LOCATION: {city_name.upper()}, {country.upper()} "
               f"<span class='ticker-sep'>//</span> {now.strftime('%d %b %Y  %H:%M')} ")
st.markdown(f"""
<div class="ticker-wrap">
  <div class="ticker-inner">{ticker_data}&nbsp;&nbsp;&nbsp;&nbsp;{ticker_data}</div>
</div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# SCORE GRID
# ════════════════════════════════════════════════════════
st.markdown("""<div class="av-sec">
  <div class="av-sec-tag">INTELLIGENCE SCORES</div>
  <div class="av-sec-line"></div>
  <div class="av-sec-code">SYS::SCORE_ENGINE_v2</div>
</div>""", unsafe_allow_html=True)

sc1,sc2,sc3,sc4 = st.columns(4)
for col, score, name, sub in [
    (sc1, ps, "POLLUTION INDEX", "Higher = Cleaner Air"),
    (sc2, ws, "WEATHER SCORE", "Temp · Wind · UV · Rain"),
    (sc3, es, "ENV SCORE", "55% Weather + 45% AQ"),
    (sc4, ag, "AG POTENTIAL", "Overall Farm Suitability"),
]:
    v = score if score is not None else 0
    color, gr = grade(v)
    display = str(score) if score is not None else "N/A"
    with col:
        st.markdown(f"""
<div class="score-cell">
  <div class="corner-tl"></div><div class="corner-tr"></div>
  <div class="corner-bl"></div><div class="corner-br"></div>
  <div class="ring-wrap">
    {ring(v, color)}
    <div class="ring-center">
      <div class="ring-num" style="color:{color};text-shadow:0 0 12px {color}">{display}</div>
      <div class="ring-denom">/ 100</div>
    </div>
  </div>
  <div class="score-name">{name}</div>
  <div class="score-grade" style="color:{color}">{gr}</div>
  <div style="font-size:0.6rem;color:#007730;margin-top:3px;font-family:'Share Tech Mono',monospace">{sub}</div>
</div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════
tabs = st.tabs([
    "🛰 ZONE MAP",
    "◈ ENVIRONMENT",
    "⚠ CRISIS INTEL",
    "🌱 CROP ENGINE",
    "🔬 SIMULATION",
    "🔍 CROP SCANNER",
    "◈ FIELD AI"
])

# ══════════════════════════════════════════
# TAB 0 — ZONE MAP
# ══════════════════════════════════════════
with tabs[0]:
    st.markdown("""<div class="av-sec">
      <div class="av-sec-tag">AGRICULTURAL ZONE INTELLIGENCE MAP</div>
      <div class="av-sec-line"></div>
      <div class="av-sec-code">SAT::TERRAIN_ANALYSIS</div>
    </div>""", unsafe_allow_html=True)

    layer_opt = st.selectbox("Active Intelligence Layer", [
        "🌱 Crop Suitability", "💧 Water Availability", "🌡 Temperature Distribution",
        "💨 Humidity Map", "🟢 Vegetation Index (NDVI)", "🏜 Drought Probability",
        "🌊 Flood Risk Zones", "🦗 Pest Risk Assessment", "🌍 Soil Health Index",
        "☁ Climate Stress Analysis", "🌧 Rainfall Patterns"
    ])

    layer_colors = {
        "🌱 Crop Suitability": ["#00ff64","#4dff4d","#ffd700","#ff8c00","#ff3030"],
        "💧 Water Availability": ["#00aaff","#0066ff","#ffd700","#ff8c00","#ff3030"],
        "🌡 Temperature Distribution": ["#ff3030","#ff8c00","#ffd700","#00ff64","#00ccff"],
        "💨 Humidity Map": ["#00ccff","#0099ff","#4dff4d","#ffd700","#ff8c00"],
        "🟢 Vegetation Index (NDVI)": ["#00ff00","#44ff44","#88ff00","#cccc00","#884400"],
        "🏜 Drought Probability": ["#ff3030","#ff6600","#ffd700","#88cc44","#00ff64"],
        "🌊 Flood Risk Zones": ["#0033ff","#0066ff","#00aaff","#ffd700","#00ff64"],
        "🦗 Pest Risk Assessment": ["#ff3030","#ff6600","#ffd700","#88ff44","#00ff64"],
        "🌍 Soil Health Index": ["#00ff64","#44cc44","#888800","#884400","#440000"],
        "☁ Climate Stress Analysis": ["#ff3030","#ff8c00","#ffd700","#44ff44","#00ff64"],
        "🌧 Rainfall Patterns": ["#0044ff","#0088ff","#00aaff","#ffd700","#ff8c00"],
    }
    lc = layer_colors.get(layer_opt, ["#00ff64","#4dff4d","#ffd700","#ff8c00","#ff3030"])

    map_html = f"""
<!DOCTYPE html><html>
<head>
<meta charset="utf-8"/>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  body{{margin:0;background:#000;font-family:'Orbitron',sans-serif}}
  #map{{width:100%;height:470px;background:#000a04}}
  .leaflet-container{{background:#000a04!important}}
  .leaflet-tile{{filter:brightness(0.3) saturate(0.2) hue-rotate(100deg) brightness(0.8)!important}}
  .hud-top{{position:absolute;top:10px;left:10px;right:10px;display:flex;justify-content:space-between;z-index:1000;pointer-events:none}}
  .hud-badge{{background:rgba(0,8,3,0.92);border:1px solid rgba(0,255,100,0.3);
    border-radius:3px;padding:5px 10px;font-family:'Orbitron',sans-serif;
    font-size:10px;color:#00ff64;letter-spacing:2px}}
  .hud-coords{{background:rgba(0,8,3,0.92);border:1px solid rgba(0,255,100,0.18);
    border-radius:3px;padding:5px 10px;font-family:monospace;
    font-size:9px;color:#00cc50;text-align:right}}
  .legend{{position:absolute;bottom:15px;left:15px;z-index:1000;
    background:rgba(0,8,3,0.92);border:1px solid rgba(0,255,100,0.2);
    border-radius:4px;padding:10px 12px;}}
  .legend-title{{font-family:'Orbitron',sans-serif;font-size:8px;color:#00cc50;letter-spacing:2px;margin-bottom:8px}}
  .legend-item{{display:flex;align-items:center;gap:7px;margin-bottom:4px}}
  .legend-dot{{width:10px;height:10px;border-radius:2px}}
  .legend-lbl{{font-family:monospace;font-size:8px;color:#00ff88}}
  .scan-line{{position:absolute;top:0;left:0;right:0;height:2px;
    background:linear-gradient(90deg,transparent,rgba(0,255,100,0.6),transparent);
    animation:scan 4s linear infinite;z-index:999;pointer-events:none}}
  @keyframes scan{{0%{{top:0%}}100%{{top:100%}}}}
  .leaflet-popup-content-wrapper{{background:rgba(0,15,5,0.95);border:1px solid rgba(0,255,100,0.3);color:#00ff88;border-radius:4px}}
  .leaflet-popup-tip{{background:rgba(0,15,5,0.95)}}
</style>
</head>
<body>
<div id="map">
  <div class="scan-line"></div>
  <div class="hud-top">
    <div class="hud-badge">◈ {layer_opt.upper()}</div>
    <div class="hud-coords">LAT: {lat:.4f}° &nbsp; LON: {lon:.4f}° &nbsp; ALT: ~{int(abs(lat*10))}M</div>
  </div>
  <div class="legend">
    <div class="legend-title">ZONE CLASSIFICATION</div>
    <div class="legend-item"><div class="legend-dot" style="background:{lc[0]}"></div><div class="legend-lbl">OPTIMAL</div></div>
    <div class="legend-item"><div class="legend-dot" style="background:{lc[1]}"></div><div class="legend-lbl">GOOD</div></div>
    <div class="legend-item"><div class="legend-dot" style="background:{lc[2]}"></div><div class="legend-lbl">MODERATE</div></div>
    <div class="legend-item"><div class="legend-dot" style="background:{lc[3]}"></div><div class="legend-lbl">STRESSED</div></div>
    <div class="legend-item"><div class="legend-dot" style="background:{lc[4]}"></div><div class="legend-lbl">CRITICAL</div></div>
  </div>
</div>
<script>
var map = L.map('map', {{zoomControl:false, attributionControl:false}}).setView([{lat},{lon}], 9);
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{maxZoom:16}}).addTo(map);

// Add zoom control with custom styling
L.control.zoom({{position:'bottomright'}}).addTo(map);

// Generate intel zones around location
var colors = {json.dumps(lc)};
var zones = [
  [{{lat:{lat+0.12},lng:{lon-0.08}}}, 0, 0.18, "ZONE-A1: OPTIMAL CULTIVATION"],
  [{{lat:{lat-0.06},lng:{lon+0.15}}}, 1, 0.14, "ZONE-B2: GOOD CONDITIONS"],
  [{{lat:{lat+0.08},lng:{lon+0.12}}}, 2, 0.12, "ZONE-C3: MODERATE SUITABILITY"],
  [{{lat:{lat-0.14},lng:{lon-0.06}}}, 1, 0.16, "ZONE-D1: GOOD CONDITIONS"],
  [{{lat:{lat+0.04},lng:{lon-0.16}}}, 3, 0.10, "ZONE-E4: STRESSED ZONE"],
  [{{lat:{lat-0.10},lng:{lon+0.08}}}, 0, 0.13, "ZONE-F1: OPTIMAL CULTIVATION"],
  [{{lat:{lat+0.16},lng:{lon+0.04}}}, 4, 0.11, "ZONE-G5: CRITICAL ZONE"],
  [{{lat:{lat-0.04},lng:{lon-0.18}}}, 2, 0.15, "ZONE-H3: MODERATE SUITABILITY"],
];

zones.forEach(function(z) {{
  var circle = L.circle([z[0].lat, z[0].lng], {{
    color: colors[z[1]], fillColor: colors[z[1]],
    fillOpacity: 0.25, weight: 1.5, opacity: 0.8,
    radius: z[2] * 111000
  }}).addTo(map);
  circle.bindPopup('<div style="font-family:Orbitron,sans-serif;font-size:10px;letter-spacing:1px;color:#00ff88">◈ ' + z[3] + '</div>');
}});

// Center marker
var centerIcon = L.divIcon({{
  html: '<div style="width:14px;height:14px;border-radius:50%;background:#00ff64;border:2px solid #fff;box-shadow:0 0 12px #00ff64,0 0 24px rgba(0,255,100,0.4)"></div>',
  iconSize:[14,14], iconAnchor:[7,7]
}});
L.marker([{lat},{lon}], {{icon:centerIcon}}).addTo(map)
  .bindPopup('<div style="font-family:Orbitron,sans-serif;font-size:10px;color:#00ff88">◈ {city_name.upper()}<br><span style="color:#00cc50">{lat:.4f}°N, {lon:.4f}°E</span></div>');

// Grid lines
for(var i=-3;i<=3;i++) {{
  L.polyline([[{lat}+i*0.05,{lon}-0.5],[{lat}+i*0.05,{lon}+0.5]],
    {{color:'rgba(0,255,100,0.05)',weight:0.5}}).addTo(map);
  L.polyline([[{lat}-0.3,{lon}+i*0.08],[{lat}+0.3,{lon}+i*0.08]],
    {{color:'rgba(0,255,100,0.05)',weight:0.5}}).addTo(map);
}}
</script>
</body></html>"""

    components.html(map_html, height=480, scrolling=False)

    # Zone stats
    st.markdown("""<div class="av-sec" style="margin-top:1.5rem">
      <div class="av-sec-tag">ZONE ANALYSIS SUMMARY</div>
      <div class="av-sec-line"></div>
    </div>""", unsafe_allow_html=True)

    z1,z2,z3,z4 = st.columns(4)
    zone_stats = [
        (z1,"OPTIMAL ZONES","38%","#00ff64"),
        (z2,"GOOD ZONES","27%","#4dff4d"),
        (z3,"MODERATE ZONES","21%","#ffd700"),
        (z4,"STRESSED/CRITICAL","14%","#ff4444"),
    ]
    for col,lbl,val,color in zone_stats:
        with col:
            st.markdown(f"""
<div class="holo-panel panel-pad">
  <div class="panel-label">{lbl}</div>
  <div style="font-family:'Orbitron',sans-serif;font-size:2rem;font-weight:800;color:{color};
    text-shadow:0 0 15px {color}">{val}</div>
  <div class="panel-sub">OF TOTAL MAPPED AREA</div>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# TAB 1 — ENVIRONMENT
# ══════════════════════════════════════════
with tabs[1]:
    st.markdown("""<div class="av-sec">
      <div class="av-sec-tag">LIVE ATMOSPHERIC DATA</div>
      <div class="av-sec-line"></div>
      <div class="av-sec-code">FEED::OPEN_METEO_v3</div>
    </div>""", unsafe_allow_html=True)

    wx_cols = st.columns(6)
    for col,lbl,val,unit in [
        (wx_cols[0],"TEMPERATURE",f"{cur['temperature_2m']:.1f}","°C"),
        (wx_cols[1],"HUMIDITY",f"{cur['relative_humidity_2m']}","%"),
        (wx_cols[2],"WIND SPEED",f"{cur['wind_speed_10m']:.1f}","KM/H"),
        (wx_cols[3],"PRECIPITATION",f"{cur['precipitation']:.1f}","MM"),
        (wx_cols[4],"UV INDEX",f"{cur.get('uv_index',0) or 0:.0f}",""),
        (wx_cols[5],"FEELS LIKE",f"{cur['apparent_temperature']:.1f}","°C"),
    ]:
        with col:
            st.markdown(f"""
<div class="holo-panel panel-pad">
  <div class="corner-tl"></div><div class="corner-tr"></div>
  <div class="panel-label">{lbl}</div>
  <div><span class="panel-value">{val}</span><span class="panel-unit">{unit}</span></div>
</div>""", unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)
    for col,lbl,val,unit in [
        (c1,"CLOUD COVER",f"{cur['cloud_cover']}","%"),
        (c2,"SURFACE PRESSURE",f"{cur['surface_pressure']:.0f}","HPA"),
        (c3,"WIND DIRECTION",f"{cur['wind_direction_10m']:.0f}","°"),
    ]:
        with col:
            st.markdown(f"""
<div class="holo-panel panel-pad">
  <div class="panel-label">{lbl}</div>
  <div><span class="panel-value">{val}</span><span class="panel-unit">{unit}</span></div>
  <div class="panel-sub">CONDITION: {wdesc(cur['weather_code'])}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("""<div class="av-sec">
      <div class="av-sec-tag">AIR QUALITY MATRIX</div>
      <div class="av-sec-line"></div>
      <div class="av-sec-code">FEED::AQ_SENSORS</div>
    </div>""", unsafe_allow_html=True)

    if aq_cur:
        pm25=float(aq_cur.get("pm2_5",0) or 0)
        pm10=float(aq_cur.get("pm10",0) or 0)
        no2=float(aq_cur.get("nitrogen_dioxide",0) or 0)
        so2=float(aq_cur.get("sulphur_dioxide",0) or 0)
        o3=float(aq_cur.get("ozone",0) or 0)
        co=float(aq_cur.get("carbon_monoxide",0) or 0)
        eu=int(aq_cur.get("european_aqi",0) or 0)
        us=int(aq_cur.get("us_aqi",0) or 0)
        pols=[
            ("PM₂.₅  FINE PARTICLES",pm25,12,35,"μg/m³",min(100,int(pm25/2.5))),
            ("PM₁₀  COARSE PARTICLES",pm10,20,50,"μg/m³",min(100,int(pm10/1.5))),
            ("NO₂  NITROGEN DIOXIDE",no2,40,100,"μg/m³",min(100,int(no2))),
            ("SO₂  SULPHUR DIOXIDE",so2,20,80,"μg/m³",min(100,int(so2))),
            ("O₃   OZONE",o3,60,120,"μg/m³",min(100,int(o3/1.8))),
            ("CO   CARBON MONOXIDE",co/1000,0.5,2,"mg/m³",min(100,int(co/700))),
        ]
        aq1,aq2=st.columns(2)
        for i,(nm,val,g,b,unit,pct) in enumerate(pols):
            bc=bcol(val,g,b)
            tgt=aq1 if i<3 else aq2
            with tgt:
                st.markdown(f"""
<div class="pol-wrap">
  <div class="pol-head">
    <span class="pol-name">{nm}</span>
    <span class="pol-val" style="color:{bc}">{val:.2f}<span style="font-size:0.6rem;color:#007730;margin-left:3px">{unit}</span></span>
  </div>
  <div class="pol-track">
    <div class="pol-bar" style="width:{pct}%;background:{bc};color:{bc}"></div>
  </div>
</div>""", unsafe_allow_html=True)

        aq_s1,aq_s2=st.columns(2)
        ec=bcol(eu,20,60); uc=bcol(us,50,100)
        ps_v=ps if ps is not None else 0; psc,psg=grade(ps_v)
        with aq_s1:
            st.markdown(f"""
<div class="holo-panel panel-pad" style="display:flex;gap:2rem;align-items:center">
  <div><div class="panel-label">EUROPEAN AQI</div>
  <div><span class="panel-value" style="color:{ec};text-shadow:0 0 10px {ec}">{eu}</span></div></div>
  <div style="width:1px;height:45px;background:rgba(0,255,100,0.1)"></div>
  <div><div class="panel-label">US AQI</div>
  <div><span class="panel-value" style="color:{uc};text-shadow:0 0 10px {uc}">{us}</span></div></div>
</div>""", unsafe_allow_html=True)
        with aq_s2:
            st.markdown(f"""
<div class="holo-panel panel-pad" style="display:flex;align-items:center;gap:1rem">
  <div style="flex:1">
    <div class="panel-label">POLLUTION SCORE</div>
    <div><span class="panel-value" style="color:{psc};text-shadow:0 0 10px {psc}">{ps_v}</span>
    <span class="panel-unit">/ 100</span></div>
    <div class="panel-sub">{psg} · HIGHER = CLEANER</div>
  </div>
  <div style="font-size:2.5rem">{"🟢" if ps_v>=65 else "🟡" if ps_v>=40 else "🔴"}</div>
</div>""", unsafe_allow_html=True)
    else:
        st.info("Air quality data unavailable.")

    st.markdown("""<div class="av-sec">
      <div class="av-sec-tag">7-DAY FORECAST MATRIX</div>
      <div class="av-sec-line"></div>
    </div>""", unsafe_allow_html=True)

    rows=[]
    for i,day in enumerate(daily["time"]):
        d=datetime.strptime(day,"%Y-%m-%d")
        rows.append({"DATE":d.strftime("%a %d %b").upper(),
            "MAX °C":f"{daily['temperature_2m_max'][i]:.1f}",
            "MIN °C":f"{daily['temperature_2m_min'][i]:.1f}",
            "RAIN MM":f"{daily['precipitation_sum'][i]:.1f}",
            "RAIN %":f"{daily['precipitation_probability_max'][i]}%",
            "WIND KM/H":f"{daily['wind_speed_10m_max'][i]:.1f}",
            "UV":f"{daily['uv_index_max'][i]:.0f}"})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════
# TAB 2 — CRISIS INTEL
# ══════════════════════════════════════════
with tabs[2]:
    st.markdown("""<div class="av-sec">
      <div class="av-sec-tag">PREDICTIVE CRISIS DETECTION</div>
      <div class="av-sec-line"></div>
      <div class="av-sec-code">AI::THREAT_ANALYSIS_v2</div>
    </div>""", unsafe_allow_html=True)

    for level,title,msg in crises(weather, aq_cur):
        icon="🚨" if level=="crisis" else "⚠️" if level=="warning" else "✅"
        st.markdown(f"""
<div class="alert-card alert-{level}">
  <div class="alert-icon">{icon}</div>
  <div>
    <div class="alert-title">{title}</div>
    <div class="alert-msg">{msg}</div>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown("""<div class="av-sec">
      <div class="av-sec-tag">AI DEEP RISK ANALYSIS</div>
      <div class="av-sec-line"></div>
    </div>""", unsafe_allow_html=True)

    if st.button("▶ INITIATE CRISIS ANALYSIS", type="primary"):
        summary={"location":f"{city_name},{country}",
            "temp":cur["temperature_2m"],"humidity":cur["relative_humidity_2m"],
            "wind":cur["wind_speed_10m"],"eu_aqi":aq_cur.get("european_aqi"),
            "pm2_5":aq_cur.get("pm2_5"),"pollution_score":ps,
            "weather_score":ws,"env_score":es,"ag_potential":ag,
            "7d_max_temps":daily["temperature_2m_max"],"7d_rain":daily["precipitation_sum"]}
        with st.spinner("ANALYSING ENVIRONMENTAL RISK VECTORS..."):
            result=ask_groq(
                f"Deep agricultural crisis analysis for {city_name}:\n{json.dumps(summary,indent=2)}\n\n"
                "Provide: 1)Multi-hazard risk matrix with probability % 2)Crop-specific impact by category "
                "3)Priority action list with timelines 4)30-day climate outlook 5)Resource reallocation plan",
                system="You are a senior agricultural risk analyst. Be precise, quantitative, use probability estimates."
            )
        st.markdown(f'<div class="ai-out"><div class="ai-out-tag">AI CRISIS REPORT · {city_name.upper()}</div>{result.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════
# TAB 3 — CROP ENGINE
# ══════════════════════════════════════════
with tabs[3]:
    st.markdown("""<div class="av-sec">
      <div class="av-sec-tag">AI CROP RECOMMENDATION ENGINE</div>
      <div class="av-sec-line"></div>
      <div class="av-sec-code">AI::CROP_MATCH_v3</div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""
<div style="padding:0.8rem 1.2rem;background:rgba(0,255,100,0.03);
  border:1px solid rgba(0,255,100,0.1);border-radius:4px;margin-bottom:1.5rem;
  font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:#00cc50;letter-spacing:0.08em">
  ◈ ANALYSING · {city_name.upper()}, {country.upper()} ·
  TEMP: {cur['temperature_2m']:.1f}°C · RH: {cur['relative_humidity_2m']}% ·
  AQI: {aq_cur.get('european_aqi','N/A')} · ENV: {es}/100 · RUNNING COMPATIBILITY MATRIX...
</div>""", unsafe_allow_html=True)

    crop_list = crops(weather)
    for emoji,name,compat,reason,care in crop_list:
        cc,_ = grade(compat)
        st.markdown(f"""
<div class="crop-row">
  <div class="crop-icon">{emoji}</div>
  <div class="crop-body">
    <div class="crop-name-big">{name}</div>
    <div class="crop-reason">▸ {reason}</div>
    <div class="crop-care">◦ {care}</div>
  </div>
  <div class="crop-pct-wrap">{mini_ring(compat, cc)}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("""<div class="av-sec">
      <div class="av-sec-tag">PRECISION MANAGEMENT PLAN</div>
      <div class="av-sec-line"></div>
    </div>""", unsafe_allow_html=True)

    opts=[f"{e} {n}" for e,n,*_ in crop_list] if crop_list else ["N/A"]
    sel=st.selectbox("Select Crop", opts)

    if st.button("▶ GENERATE PLAN", type="primary") and crop_list:
        with st.spinner("BUILDING PRECISION AGRICULTURE PROTOCOL..."):
            result=ask_groq(
                f"Precision agriculture plan for {sel} in {city_name}, {country}.\n"
                f"Conditions: {cur['temperature_2m']:.1f}°C, {cur['relative_humidity_2m']}% RH, "
                f"UV {cur.get('uv_index',0) or 0:.0f}, Wind {cur['wind_speed_10m']:.1f}km/h, "
                f"AQI {aq_cur.get('european_aqi','N/A')}, PM2.5 {aq_cur.get('pm2_5','N/A')}μg/m³, "
                f"Pollution {ps}/100, Env {es}/100.\n\n"
                "Include: 1)Precision sowing protocol with exact timing 2)Smart irrigation schedule "
                "with quantities per day 3)NPK fertiliser timeline with ratios 4)IPM pest programme "
                "5)Pollution stress mitigation 6)Yield optimisation tactics 7)Harvest window prediction "
                "8)Climate contingency plans",
                system="You are a precision agriculture scientist. Provide specific quantities, timings, and measurable targets."
            )
        st.markdown(f'<div class="ai-out"><div class="ai-out-tag">MANAGEMENT PROTOCOL · {sel.upper()}</div>{result.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════
# TAB 4 — SIMULATION
# ══════════════════════════════════════════
with tabs[4]:
    st.markdown("""<div class="av-sec">
      <div class="av-sec-tag">FARM DIGITAL TWIN · SCENARIO ENGINE</div>
      <div class="av-sec-line"></div>
      <div class="av-sec-code">SIM::FARM_TWIN_v2</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
<div style="padding:0.9rem 1.2rem;background:rgba(0,255,100,0.03);
  border:1px solid rgba(0,255,100,0.08);border-radius:4px;margin-bottom:1.5rem;
  font-size:0.78rem;color:#00cc50;line-height:1.7">
  Adjust parameters to simulate future agricultural scenarios.
  The AI Digital Twin models environmental changes and predicts crop outcomes.
</div>""", unsafe_allow_html=True)

    sim1,sim2=st.columns(2)
    with sim1:
        t_d=st.slider("Temperature Δ (°C)",-10,+20,0)
        r_d=st.slider("Rainfall Δ (%)",-100,+200,0)
        h_d=st.slider("Humidity Δ (%)",-40,+40,0)
    with sim2:
        aqi_d=st.slider("AQI Δ",-60,+200,0)
        w_d=st.slider("Wind Speed Δ (km/h)",-20,+60,0)
        sim_crop=st.text_input("Target Crop",placeholder="e.g. Rice, Wheat, Tomato...")

    sim_t=cur["temperature_2m"]+t_d
    base_r=sum(p for p in daily["precipitation_sum"] if p)/7
    sim_r=base_r*(1+r_d/100)
    sim_aqi=(aq_cur.get("european_aqi") or 30)+aqi_d
    sim_h=min(100,max(0,cur["relative_humidity_2m"]+h_d))
    sim_w=max(0,cur["wind_speed_10m"]+w_d)

    sv_cols=st.columns(5)
    for col,lbl,bv,sv,unit in [
        (sv_cols[0],"TEMPERATURE",cur["temperature_2m"],sim_t,"°C"),
        (sv_cols[1],"RAINFALL",base_r,sim_r,"mm/d"),
        (sv_cols[2],"HUMIDITY",cur["relative_humidity_2m"],sim_h,"%"),
        (sv_cols[3],"AQI",aq_cur.get("european_aqi",30),sim_aqi,""),
        (sv_cols[4],"WIND",cur["wind_speed_10m"],sim_w,"km/h"),
    ]:
        dlt=sv-bv; dc="#00ff64" if dlt<=0 else "#ff4444"
        with col:
            st.markdown(f"""
<div class="holo-panel panel-pad">
  <div class="panel-label">{lbl}</div>
  <div><span class="panel-value" style="font-size:1.4rem">{sv:.1f}</span><span class="panel-unit">{unit}</span></div>
  <div class="panel-sub" style="color:{dc}">{'▲' if dlt>0 else '▼'} {abs(dlt):.1f}{unit}</div>
</div>""", unsafe_allow_html=True)

    if st.button("▶ RUN DIGITAL TWIN SIMULATION", type="primary"):
        with st.spinner("RUNNING FARM SIMULATION MODEL..."):
            result=ask_groq(
                f"Farm Digital Twin simulation for {city_name}, {country}.\n"
                f"BASELINE: Temp {cur['temperature_2m']:.1f}°C, Rain {base_r:.1f}mm/d, "
                f"RH {cur['relative_humidity_2m']}%, AQI {aq_cur.get('european_aqi','N/A')}, "
                f"Wind {cur['wind_speed_10m']:.1f}km/h, Env Score {es}/100\n"
                f"SIMULATION: Temp {sim_t:.1f}°C, Rain {sim_r:.1f}mm/d, RH {sim_h:.0f}%, "
                f"AQI {sim_aqi:.0f}, Wind {sim_w:.1f}km/h\n"
                f"{'Target crop: '+sim_crop if sim_crop else ''}\n\n"
                "Provide: 1)Quantified risk delta vs baseline with % changes "
                "2)Predicted yield impact per crop type with numbers "
                "3)Water and input requirement changes in specific quantities "
                "4)Adaptive management strategies with timelines "
                "5)Early warning indicators to monitor "
                "6)Best case / worst case / most likely projections",
                system="You are an agricultural simulation scientist. Provide quantitative projections with specific numbers, percentages, and probabilities."
            )
        st.markdown(f'<div class="ai-out"><div class="ai-out-tag">SIMULATION RESULTS · DIGITAL TWIN</div>{result.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════
# TAB 5 — CROP SCANNER
# ══════════════════════════════════════════
with tabs[5]:
    st.markdown("""<div class="av-sec">
      <div class="av-sec-tag">AI CROP HEALTH SCANNER</div>
      <div class="av-sec-line"></div>
      <div class="av-sec-code">CV::PLANT_VISION_v1</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
<div style="padding:0.9rem 1.2rem;background:rgba(0,255,100,0.03);
  border:1px solid rgba(0,255,100,0.08);border-radius:4px;margin-bottom:1.5rem;
  font-size:0.78rem;color:#00cc50;line-height:1.7">
  Upload a photo of your plant or crop. The AI vision system will analyse visible symptoms,
  detect diseases, nutrient deficiencies, stress conditions, and generate a treatment protocol.
</div>""", unsafe_allow_html=True)

    sc1,sc2=st.columns([1,1])
    with sc1:
        uploaded = st.file_uploader("UPLOAD CROP IMAGE", type=["jpg","jpeg","png","webp"])
        crop_name_scan = st.text_input("Crop Name (helps accuracy)", placeholder="e.g. Tomato, Rice, Wheat...")
        scan_context = st.text_area("Describe symptoms (optional)",
            placeholder="e.g. Yellow leaves, brown spots, wilting, stunted growth...",
            height=80)

    with sc2:
        if uploaded:
            st.image(uploaded, caption="UPLOADED SAMPLE", use_container_width=True)
        else:
            st.markdown("""
<div style="width:100%;height:200px;background:rgba(0,255,100,0.03);
  border:1px dashed rgba(0,255,100,0.2);border-radius:6px;
  display:flex;align-items:center;justify-content:center;
  font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:#007730;
  letter-spacing:0.15em;text-align:center">
  ◈ AWAITING SAMPLE UPLOAD<br><br>
  SUPPORTED: JPG · PNG · WEBP
</div>""", unsafe_allow_html=True)

    if st.button("▶ INITIATE SCAN", type="primary"):
        if uploaded:
            img_bytes = uploaded.read()
            img_b64 = base64.b64encode(img_bytes).decode()
            ext = uploaded.name.split('.')[-1].lower()
            mime = "image/jpeg" if ext in ["jpg","jpeg"] else f"image/{ext}"

            with st.spinner("RUNNING COMPUTER VISION ANALYSIS..."):
                try:
                    client = get_groq()
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        max_tokens=1000,
                        messages=[{
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"""You are an expert plant pathologist and agronomist.
Analyse this crop image and provide:
1. DIAGNOSIS: Visible diseases, infections, or deficiencies detected
2. SEVERITY: Rate the condition (Healthy/Mild/Moderate/Severe/Critical)
3. ROOT CAUSE: Likely environmental or biological cause
4. IMMEDIATE ACTIONS: Steps to take in the next 24-48 hours
5. TREATMENT PROTOCOL: Specific treatments, chemicals, or organic remedies
6. PREVENTION: How to prevent recurrence
7. RECOVERY TIMELINE: Expected recovery with proper treatment

{'Crop: ' + crop_name_scan if crop_name_scan else ''}
{'Reported symptoms: ' + scan_context if scan_context else ''}
Location conditions: {cur['temperature_2m']:.1f}°C, {cur['relative_humidity_2m']}% RH, {wdesc(cur['weather_code'])}

Be specific and actionable. If the image is unclear, provide analysis based on reported symptoms."""
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:{mime};base64,{img_b64}"}
                                }
                            ]
                        }]
                    )
                    result = response.choices[0].message.content
                except Exception:
                    result = ask_groq(
                        f"""Plant health analysis based on reported symptoms.
{'Crop: ' + crop_name_scan if crop_name_scan else 'Unknown crop'}
{'Symptoms: ' + scan_context if scan_context else 'No symptoms described'}
Location: {city_name}, {country}
Conditions: {cur['temperature_2m']:.1f}°C, {cur['relative_humidity_2m']}% RH, AQI {aq_cur.get('european_aqi','N/A')}

Provide: 1)Likely diagnosis based on conditions 2)Severity assessment 3)Treatment protocol
4)Immediate actions 5)Prevention strategies 6)Recovery timeline""",
                        system="You are an expert plant pathologist. Provide specific, actionable diagnoses."
                    )

            st.markdown(f'<div class="ai-out"><div class="ai-out-tag">CROP HEALTH SCAN REPORT</div>{result.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)
        else:
            if scan_context or crop_name_scan:
                with st.spinner("ANALYSING SYMPTOMS..."):
                    result=ask_groq(
                        f"Plant health analysis. Crop: {crop_name_scan or 'Unknown'}. "
                        f"Symptoms: {scan_context or 'None described'}. "
                        f"Location: {city_name}. Conditions: {cur['temperature_2m']:.1f}°C, "
                        f"{cur['relative_humidity_2m']}% RH, AQI {aq_cur.get('european_aqi','N/A')}.\n"
                        "Provide: 1)Likely diagnosis 2)Severity 3)Immediate actions 4)Treatment protocol 5)Prevention",
                        system="You are an expert plant pathologist."
                    )
                st.markdown(f'<div class="ai-out"><div class="ai-out-tag">SYMPTOM ANALYSIS REPORT</div>{result.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)
            else:
                st.warning("Upload an image or describe symptoms to run the scanner.")

# ══════════════════════════════════════════
# TAB 6 — FIELD AI
# ══════════════════════════════════════════
with tabs[6]:
    st.markdown("""<div class="av-sec">
      <div class="av-sec-tag">AEROVEDA FIELD INTELLIGENCE SYSTEM</div>
      <div class="av-sec-line"></div>
      <div class="av-sec-code">AI::FIELD_ASSISTANT_v3</div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""
<div style="padding:0.8rem 1.2rem;background:rgba(0,255,100,0.03);
  border:1px solid rgba(0,255,100,0.08);border-radius:4px;margin-bottom:1rem;
  font-family:'Share Tech Mono',monospace;font-size:0.62rem;color:#00cc50;letter-spacing:0.07em">
  ◈ CONTEXT MATRIX LOADED · {city_name.upper()}, {country.upper()} ·
  {cur['temperature_2m']:.1f}°C · {cur['relative_humidity_2m']}% RH ·
  AQI {aq_cur.get('european_aqi','N/A')} · PM2.5 {aq_cur.get('pm2_5','N/A')}μg/m³ ·
  ENV SCORE {es}/100 · AG POTENTIAL {ag}/100
</div>""", unsafe_allow_html=True)

    focus=st.text_input("CROP FOCUS", placeholder="e.g. Rice, Tomato, Groundnut, Wheat...")

    if "chat" not in st.session_state:
        st.session_state.chat=[]

    if not st.session_state.chat:
        st.markdown("""
<div style="font-family:'Orbitron',sans-serif;font-size:0.52rem;
  letter-spacing:0.2em;color:#00cc50;margin-bottom:0.7rem;font-weight:700">
  ◈ SUGGESTED INTELLIGENCE QUERIES
</div>""", unsafe_allow_html=True)
        sq=st.columns(2)
        for i,q in enumerate([
            "What pests are likely at current AQI and temperature?",
            "Exact water requirement for my crop this week?",
            "How is air pollution affecting crop growth right now?",
            "What fertiliser NPK ratio should I apply today?",
            "Is it safe to spray pesticide in current wind conditions?",
            "Generate a 30-day farming schedule for my conditions",
        ]):
            with sq[i%2]:
                st.markdown(f"""
<div style="padding:0.6rem 0.9rem;background:rgba(0,255,100,0.03);
  border:1px solid rgba(0,255,100,0.1);border-radius:4px;margin-bottom:0.5rem;
  font-size:0.72rem;color:#00cc50;font-family:'Share Tech Mono',monospace;cursor:pointer">
  ▸ {q}</div>""", unsafe_allow_html=True)

    for msg in st.session_state.chat:
        if msg["role"]=="user":
            st.markdown(f"""
<div class="chat-user-row">
  <div class="chat-bubble chat-user-bub">
    <div class="chat-from chat-from-u">◈ OPERATOR INPUT</div>
    {msg['content']}
  </div>
</div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
<div class="chat-ai-row">
  <div class="chat-bubble chat-ai-bub">
    <div class="chat-from">◈ AEROVEDA FIELD AI</div>
    {msg['content']}
  </div>
</div>""", unsafe_allow_html=True)

    user_in=st.chat_input("Query the Field Intelligence System...")
    if user_in:
        st.session_state.chat.append({"role":"user","content":user_in})
        with st.spinner("PROCESSING FIELD QUERY..."):
            reply=ask_groq_chat(
                st.session_state.chat,
                system=f"""You are Aeroveda's Field Intelligence System — an advanced AI agronomist with complete real-time environmental awareness.

LOCATION DATA: {city_name}, {country} | Coordinates: {lat:.4f}°N, {lon:.4f}°E
ATMOSPHERIC: Temp {cur['temperature_2m']:.1f}°C | RH {cur['relative_humidity_2m']}% | Wind {cur['wind_speed_10m']:.1f}km/h
UV INDEX: {cur.get('uv_index',0) or 0:.0f} | CONDITIONS: {wdesc(cur['weather_code'])}
PRECIPITATION: {cur['precipitation']:.1f}mm current | PRESSURE: {cur['surface_pressure']:.0f}hPa
AIR QUALITY: EU AQI {aq_cur.get('european_aqi','N/A')} | PM2.5 {aq_cur.get('pm2_5','N/A')}μg/m³ | PM10 {aq_cur.get('pm10','N/A')}μg/m³
INTELLIGENCE SCORES: Pollution {ps if ps is not None else 'N/A'}/100 | Weather {ws}/100 | Env {es}/100 | AG Potential {ag}/100
{'CROP FOCUS: '+focus if focus else 'NO SPECIFIC CROP FOCUS SET'}

Provide precise, data-driven responses grounded in the exact conditions above.
Never give generic advice. Always reference the actual numbers.
Use bullet points and specific quantities where relevant.
Be concise but comprehensive.""",
                max_tokens=900
            )
        st.session_state.chat.append({"role":"assistant","content":reply})
        st.rerun()

    if st.session_state.chat:
        if st.button("↺ CLEAR SESSION"):
            st.session_state.chat=[]; st.rerun()
