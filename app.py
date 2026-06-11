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
    page_title="AEROVEDA · AGRI-OS",
    page_icon="🌍",
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
            headers={"User-Agent":"Aeroveda/6.0"}, timeout=8)
        d = r.json()
        detected = (d.get("address",{}).get("city") or
                    d.get("address",{}).get("town") or
                    d.get("address",{}).get("village",""))
        if detected:
            st.session_state["city"] = detected
        st.query_params.clear()
        st.rerun()
    except: pass

# ═══════════════════════════════════════════════════════
# MASTER CSS — Cyan + Lime Holographic
# ═══════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Exo+2:ital,wght@0,200;0,300;0,400;0,500;0,600;0,700;1,300&family=Share+Tech+Mono&display=swap');

*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body,[class*="css"]{font-family:'Exo 2',sans-serif;background:#010d12!important;}

/* ══ DEEP EARTH BACKGROUND ══ */
.stApp{
  background:
    radial-gradient(ellipse at 15% 20%, rgba(0,255,200,0.06) 0%,transparent 40%),
    radial-gradient(ellipse at 85% 70%, rgba(160,255,0,0.04) 0%,transparent 35%),
    radial-gradient(ellipse at 60% 40%, rgba(0,200,180,0.03) 0%,transparent 50%),
    radial-gradient(ellipse at 30% 80%, rgba(100,255,50,0.03) 0%,transparent 40%),
    #010d12!important;
  color:#b2ffe8;overflow-x:hidden;
}

/* Scanline */
.stApp::before{
  content:'';position:fixed;inset:0;pointer-events:none;z-index:9997;
  background:repeating-linear-gradient(0deg,transparent,transparent 3px,rgba(0,0,0,0.015) 3px,rgba(0,0,0,0.015) 4px);
}

/* Circuit board bg */
.stApp::after{
  content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
  background-image:
    linear-gradient(rgba(0,255,180,0.015) 1px,transparent 1px),
    linear-gradient(90deg,rgba(0,255,180,0.015) 1px,transparent 1px),
    linear-gradient(rgba(160,255,0,0.008) 1px,transparent 1px),
    linear-gradient(90deg,rgba(160,255,0,0.008) 1px,transparent 1px);
  background-size:80px 80px,80px 80px,20px 20px,20px 20px;
}

.main .block-container{
  padding:0 2.2rem 5rem!important;
  max-width:1600px!important;position:relative;z-index:1;
}

/* ══ COMMAND HEADER ══ */
.av-header{
  position:relative;padding:1.6rem 2.2rem;
  background:linear-gradient(135deg,rgba(0,20,28,0.98) 0%,rgba(0,12,18,0.99) 100%);
  border-bottom:1px solid rgba(0,255,180,0.12);
  margin:0 -2.2rem 0;
  display:flex;align-items:center;justify-content:space-between;
  overflow:hidden;
}
.av-header::before{
  content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,transparent 0%,#00ffb4 20%,#a0ff00 50%,#00ffb4 80%,transparent 100%);
  animation:header-glow 4s ease-in-out infinite;
}
.av-header::after{
  content:'';position:absolute;bottom:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(0,255,180,0.4),rgba(160,255,0,0.3),transparent);
}
@keyframes header-glow{0%,100%{opacity:0.4;background-position:0% 0%}50%{opacity:1;background-position:100% 0%}}

.logo-block{display:flex;flex-direction:column;gap:5px}
.logo-text{
  font-family:'Orbitron',sans-serif;font-size:2rem;font-weight:900;
  letter-spacing:0.12em;
  background:linear-gradient(135deg,#00ffb4 0%,#a0ff00 50%,#00e5ff 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;
  filter:drop-shadow(0 0 20px rgba(0,255,180,0.5));
  line-height:1;
}
.logo-tagline{
  font-family:'Share Tech Mono',monospace;font-size:0.58rem;
  letter-spacing:0.25em;color:#00c896;text-transform:uppercase;
}

.hdr-stats{display:flex;align-items:center;gap:20px}
.hdr-chip{
  display:flex;align-items:center;gap:7px;
  font-family:'Share Tech Mono',monospace;font-size:0.6rem;
  color:#00c896;letter-spacing:0.08em;
}
.pulse-dot{
  width:7px;height:7px;border-radius:50%;
  box-shadow:0 0 10px currentColor;
  animation:pdot 1.8s ease-in-out infinite;
}
.pulse-dot.cyan{background:#00ffb4;color:#00ffb4}
.pulse-dot.lime{background:#a0ff00;color:#a0ff00}
.pulse-dot.red{background:#ff4060;color:#ff4060}
@keyframes pdot{0%,100%{opacity:1;transform:scale(1)}50%{opacity:0.2;transform:scale(0.7)}}

/* ══ LOCATION BAR (new prominent design) ══ */
.loc-bar{
  display:flex;align-items:center;gap:10px;
  background:linear-gradient(135deg,rgba(0,255,180,0.06),rgba(160,255,0,0.04));
  border:1px solid rgba(0,255,180,0.25);
  border-radius:6px;padding:8px 16px;
  font-family:'Share Tech Mono',monospace;font-size:0.7rem;color:#00ffb4;
  box-shadow:0 0 20px rgba(0,255,180,0.08),inset 0 0 20px rgba(0,255,180,0.03);
}

/* ══ TICKER ══ */
.ticker-wrap{
  background:rgba(0,8,12,0.98);
  border-bottom:1px solid rgba(0,255,180,0.1);
  padding:7px 0;overflow:hidden;white-space:nowrap;
  margin:0 -2.2rem 2rem;position:relative;
}
.ticker-wrap::before{content:'';position:absolute;left:0;top:0;bottom:0;width:60px;background:linear-gradient(90deg,rgba(0,8,12,0.98),transparent);z-index:2}
.ticker-wrap::after{content:'';position:absolute;right:0;top:0;bottom:0;width:60px;background:linear-gradient(-90deg,rgba(0,8,12,0.98),transparent);z-index:2}
.ticker-inner{
  display:inline-block;
  animation:ticker 45s linear infinite;
  font-family:'Share Tech Mono',monospace;font-size:0.62rem;color:#00a878;
  letter-spacing:0.07em;
}
@keyframes ticker{0%{transform:translateX(100vw)}100%{transform:translateX(-100%)}}
.tsep{color:#00ffb4;margin:0 16px;opacity:0.5}

/* ══ SECTION HEADERS ══ */
.av-section{display:flex;align-items:center;gap:14px;margin:2.2rem 0 1.4rem}
.av-section-badge{
  font-family:'Orbitron',sans-serif;font-size:0.56rem;font-weight:700;
  letter-spacing:0.18em;color:#010d12;
  background:linear-gradient(135deg,#00ffb4,#a0ff00);
  padding:5px 14px;border-radius:3px;white-space:nowrap;
  box-shadow:0 0 15px rgba(0,255,180,0.3);
}
.av-section-line{
  flex:1;height:1px;
  background:linear-gradient(90deg,rgba(0,255,180,0.3),rgba(160,255,0,0.1),transparent);
}
.av-section-code{
  font-family:'Share Tech Mono',monospace;font-size:0.55rem;
  color:rgba(0,255,180,0.25);white-space:nowrap;
}

/* ══ HOLOGRAPHIC PANELS ══ */
.holo{
  background:linear-gradient(135deg,rgba(0,22,32,0.92),rgba(0,12,20,0.96));
  border:1px solid rgba(0,255,180,0.1);
  border-radius:10px;position:relative;overflow:hidden;
  backdrop-filter:blur(20px);
  transition:all 0.35s cubic-bezier(.4,0,.2,1);
}
.holo:hover{
  border-color:rgba(0,255,180,0.3);
  box-shadow:0 0 40px rgba(0,255,180,0.07),0 0 80px rgba(160,255,0,0.03),inset 0 0 30px rgba(0,255,180,0.02);
  transform:translateY(-1px);
}
.holo::before{
  content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(0,255,180,0.5),rgba(160,255,0,0.3),transparent);
}
.holo::after{
  content:'';position:absolute;top:-50%;right:-30%;
  width:200px;height:200px;border-radius:50%;
  background:radial-gradient(circle,rgba(0,255,180,0.03),transparent 70%);
  pointer-events:none;
}
/* Corner markers */
.holo .ct,.holo .cb{position:absolute;width:14px;height:14px;pointer-events:none;z-index:3}
.holo .ct-l{top:7px;left:7px;border-top:1.5px solid rgba(0,255,180,0.5);border-left:1.5px solid rgba(0,255,180,0.5)}
.holo .ct-r{top:7px;right:7px;border-top:1.5px solid rgba(160,255,0,0.4);border-right:1.5px solid rgba(160,255,0,0.4)}
.holo .cb-l{bottom:7px;left:7px;border-bottom:1.5px solid rgba(0,255,180,0.3);border-left:1.5px solid rgba(0,255,180,0.3)}
.holo .cb-r{bottom:7px;right:7px;border-bottom:1.5px solid rgba(160,255,0,0.3);border-right:1.5px solid rgba(160,255,0,0.3)}
.hp{padding:1.3rem 1.5rem}
.hp-lbl{font-family:'Share Tech Mono',monospace;font-size:0.57rem;letter-spacing:0.2em;color:#00a878;margin-bottom:6px;text-transform:uppercase}
.hp-val{font-family:'Orbitron',sans-serif;font-size:1.9rem;font-weight:700;color:#fff;line-height:1}
.hp-unit{font-size:0.78rem;color:#00ffb4;margin-left:3px;font-family:'Exo 2',sans-serif;font-weight:300}
.hp-sub{font-size:0.67rem;color:#007a5e;margin-top:5px;font-family:'Share Tech Mono',monospace}

/* ══ SCORE RINGS ══ */
.score-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1.2rem;margin-bottom:2rem}
.score-orb{
  background:linear-gradient(135deg,rgba(0,20,28,0.94),rgba(0,10,16,0.97));
  border:1px solid rgba(0,255,180,0.1);
  border-radius:12px;padding:1.8rem 1rem 1.4rem;
  text-align:center;position:relative;overflow:hidden;
  transition:all 0.3s;
}
.score-orb:hover{
  border-color:rgba(0,255,180,0.35);
  transform:translateY(-4px);
  box-shadow:0 12px 40px rgba(0,255,180,0.1),0 0 60px rgba(160,255,0,0.04);
}
.score-orb::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(0,255,180,0.4),rgba(160,255,0,0.3),transparent)}
.score-orb::after{content:'';position:absolute;bottom:-40px;left:50%;transform:translateX(-50%);width:120px;height:80px;background:radial-gradient(ellipse,rgba(0,255,180,0.04),transparent 70%);pointer-events:none}
.ring-host{position:relative;width:130px;height:130px;margin:0 auto}
.ring-host svg{width:130px;height:130px}
.ring-center{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;width:80px}
.ring-num{font-family:'Orbitron',sans-serif;font-size:1.9rem;font-weight:800;color:#fff;line-height:1}
.ring-slash{font-family:'Share Tech Mono',monospace;font-size:0.52rem;color:#00a878;margin-top:2px}
.orb-title{font-family:'Orbitron',sans-serif;font-size:0.54rem;font-weight:700;letter-spacing:0.16em;color:#00a878;margin-top:12px;text-transform:uppercase}
.orb-grade{font-family:'Orbitron',sans-serif;font-size:0.72rem;font-weight:700;letter-spacing:0.1em;margin-top:4px}
.orb-hint{font-size:0.57rem;color:#004a38;margin-top:3px;font-family:'Share Tech Mono',monospace}

/* ══ POLLUTANT BARS ══ */
.pol{margin-bottom:1.2rem}
.pol-hd{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px}
.pol-nm{font-family:'Share Tech Mono',monospace;font-size:0.6rem;letter-spacing:0.1em;color:#00a878;text-transform:uppercase}
.pol-vl{font-family:'Orbitron',sans-serif;font-size:0.82rem;font-weight:600}
.pol-track{height:3px;background:rgba(0,255,180,0.07);border-radius:99px;position:relative;overflow:visible}
.pol-fill{height:3px;border-radius:99px;position:relative;transition:width 1.2s ease}
.pol-fill::after{content:'';position:absolute;right:-1px;top:-3px;width:9px;height:9px;border-radius:50%;background:currentColor;box-shadow:0 0 8px currentColor,0 0 16px currentColor,0 0 24px currentColor}

/* ══ ALERTS ══ */
.alert{display:flex;gap:14px;padding:1.1rem 1.4rem;border-radius:8px;margin-bottom:0.7rem;position:relative;overflow:hidden}
.alert::before{content:'';position:absolute;left:0;top:0;bottom:0;width:3px;border-radius:3px 0 0 3px}
.a-crisis{background:rgba(255,40,70,0.06);border:1px solid rgba(255,40,70,0.2)}
.a-crisis::before{background:linear-gradient(180deg,#ff2846,#cc0022)}
.a-warning{background:rgba(240,185,0,0.06);border:1px solid rgba(240,185,0,0.2)}
.a-warning::before{background:linear-gradient(180deg,#f0b900,#c09000)}
.a-safe{background:rgba(0,255,180,0.05);border:1px solid rgba(0,255,180,0.18)}
.a-safe::before{background:linear-gradient(180deg,#00ffb4,#00c896)}
.alert-icon{font-size:1.3rem;flex-shrink:0;padding-top:1px}
.alert-title{font-family:'Orbitron',sans-serif;font-size:0.6rem;font-weight:700;letter-spacing:0.15em;margin-bottom:5px}
.a-crisis .alert-title{color:#ff7090}
.a-warning .alert-title{color:#f0c840}
.a-safe .alert-title{color:#00ffb4}
.alert-msg{font-size:0.82rem;line-height:1.65}
.a-crisis .alert-msg{color:#ffb0bc}
.a-warning .alert-msg{color:#fde08a}
.a-safe .alert-msg{color:#9efff0}

/* ══ CROP CARDS ══ */
.crop-card{
  display:flex;align-items:center;gap:1.3rem;
  padding:1.1rem 1.5rem;
  background:linear-gradient(135deg,rgba(0,22,30,0.88),rgba(0,10,16,0.94));
  border:1px solid rgba(0,255,180,0.1);
  border-left:3px solid rgba(0,255,180,0.4);
  border-radius:8px;margin-bottom:0.7rem;
  position:relative;overflow:hidden;transition:all 0.3s;
}
.crop-card:hover{border-color:rgba(0,255,180,0.35);border-left-color:#00ffb4;transform:translateX(6px);box-shadow:0 4px 30px rgba(0,255,180,0.08)}
.crop-card::after{content:'';position:absolute;right:-20px;top:50%;transform:translateY(-50%);width:80px;height:80px;border-radius:50%;background:radial-gradient(circle,rgba(0,255,180,0.04),transparent 70%)}
.ce{font-size:2.2rem;flex-shrink:0}
.cb{flex:1}
.cn{font-family:'Orbitron',sans-serif;font-size:0.9rem;font-weight:700;color:#fff;letter-spacing:0.05em}
.cr{font-size:0.75rem;color:#00c896;margin-top:3px}
.cc{font-size:0.65rem;color:#007a5e;margin-top:5px;font-family:'Share Tech Mono',monospace}

/* ══ CHAT ══ */
.cu-row{display:flex;justify-content:flex-end;margin-bottom:0.7rem}
.ca-row{display:flex;justify-content:flex-start;margin-bottom:0.7rem}
.cbub{padding:0.9rem 1.2rem;border-radius:10px;font-size:0.84rem;line-height:1.7;max-width:84%}
.cu-bub{background:rgba(0,255,180,0.07);border:1px solid rgba(0,255,180,0.2);color:#d0fff0;border-radius:10px 10px 3px 10px}
.ca-bub{background:rgba(0,14,22,0.95);border:1px solid rgba(0,255,180,0.1);color:#b2ffe8;border-radius:10px 10px 10px 3px}
.cfrom{font-family:'Share Tech Mono',monospace;font-size:0.55rem;letter-spacing:0.2em;margin-bottom:5px;text-transform:uppercase}
.cfrom-u{text-align:right;color:#00ffb4}
.cfrom-a{color:#a0ff00}

/* ══ AI OUTPUT ══ */
.ai-out{
  background:rgba(0,8,14,0.97);border:1px solid rgba(0,255,180,0.15);
  border-radius:10px;padding:1.8rem;margin-top:1rem;
  color:#b8ffec;line-height:1.9;font-size:0.87rem;position:relative;
}
.ai-out-tag{
  position:absolute;top:-11px;left:20px;background:#010d12;
  padding:0 10px;font-family:'Orbitron',sans-serif;
  font-size:0.5rem;letter-spacing:0.22em;
  background:linear-gradient(135deg,#00ffb4,#a0ff00);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  font-weight:700;
}

/* ══ TABS ══ */
.stTabs [data-baseweb="tab-list"]{
  background:rgba(0,8,14,0.97)!important;
  border-bottom:1px solid rgba(0,255,180,0.1)!important;
  gap:0!important;padding:0 1rem!important;
}
.stTabs [data-baseweb="tab"]{
  font-family:'Orbitron',sans-serif!important;
  font-size:0.57rem!important;letter-spacing:0.15em!important;
  text-transform:uppercase!important;
  color:rgba(0,180,130,0.5)!important;
  padding:0.9rem 1.4rem!important;
  background:transparent!important;border:none!important;font-weight:600!important;
}
.stTabs [aria-selected="true"]{
  color:#00ffb4!important;
  border-bottom:2px solid #00ffb4!important;
  background:rgba(0,255,180,0.04)!important;
  text-shadow:0 0 12px rgba(0,255,180,0.6)!important;
}
.stTabs [data-baseweb="tab-panel"]{padding:2rem 0 0!important;background:transparent!important}

/* ══ INPUTS ══ */
.stTextInput input{
  background:rgba(0,16,24,0.9)!important;
  border:1px solid rgba(0,255,180,0.2)!important;
  border-radius:7px!important;color:#d0fff0!important;
  font-family:'Exo 2',sans-serif!important;font-size:0.95rem!important;
  transition:all 0.2s!important;
}
.stTextInput input:focus{
  border-color:rgba(0,255,180,0.55)!important;
  box-shadow:0 0 0 3px rgba(0,255,180,0.08),0 0 20px rgba(0,255,180,0.1)!important;
}
.stTextInput label{color:#00a878!important;font-family:'Share Tech Mono',monospace!important;font-size:0.58rem!important;letter-spacing:0.2em!important;text-transform:uppercase!important}
.stTextArea textarea{background:rgba(0,16,24,0.9)!important;border:1px solid rgba(0,255,180,0.18)!important;border-radius:7px!important;color:#d0fff0!important;font-family:'Exo 2',sans-serif!important}

/* ══ BUTTONS ══ */
.stButton button{
  background:rgba(0,255,180,0.06)!important;
  border:1px solid rgba(0,255,180,0.28)!important;
  color:#00ffb4!important;border-radius:5px!important;
  font-family:'Orbitron',sans-serif!important;
  font-size:0.57rem!important;letter-spacing:0.14em!important;
  font-weight:700!important;transition:all 0.2s!important;
}
.stButton button:hover{
  background:rgba(0,255,180,0.15)!important;
  border-color:#00ffb4!important;color:#fff!important;
  box-shadow:0 0 25px rgba(0,255,180,0.25),0 0 50px rgba(0,255,180,0.1)!important;
}
button[kind="primary"]{
  background:linear-gradient(135deg,rgba(0,120,90,0.7),rgba(0,200,140,0.5))!important;
  border:1px solid #00ffb4!important;color:#fff!important;
  box-shadow:0 0 25px rgba(0,255,180,0.2)!important;
}

/* ══ SELECT ══ */
[data-baseweb="select"]>div{background:rgba(0,16,24,0.9)!important;border-color:rgba(0,255,180,0.2)!important;color:#d0fff0!important;border-radius:7px!important}

/* ══ SLIDER ══ */
.stSlider [data-testid="stThumbValue"]{color:#00ffb4!important;font-family:'Share Tech Mono',monospace!important}

/* ══ FILE UPLOAD ══ */
[data-testid="stFileUploader"]{background:rgba(0,16,24,0.8)!important;border:1px dashed rgba(0,255,180,0.22)!important;border-radius:8px!important}

/* ══ DATAFRAME ══ */
[data-testid="stDataFrameResizable"]{border:1px solid rgba(0,255,180,0.1)!important;border-radius:8px!important}

/* ══ SIDEBAR ══ */
[data-testid="stSidebar"]{background:rgba(0,6,10,0.99)!important;border-right:1px solid rgba(0,255,180,0.1)!important}

/* ══ MISC ══ */
#MainMenu,footer,header{visibility:hidden}
::-webkit-scrollbar{width:3px}
::-webkit-scrollbar-thumb{background:linear-gradient(180deg,#00ffb4,#a0ff00);border-radius:99px}
.stSpinner>div{border-top-color:#00ffb4!important}

/* ══ GRADIENT TEXT UTILITY ══ */
.grad-text{
  background:linear-gradient(135deg,#00ffb4 0%,#a0ff00 50%,#00e5ff 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}
</style>
""", unsafe_allow_html=True)

# ─── Groq ─────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_groq():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

def ask_groq(prompt, system="You are an expert agricultural AI.", max_tokens=1000):
    try:
        r = get_groq().chat.completions.create(
            model="llama-3.3-70b-versatile", max_tokens=max_tokens,
            messages=[{"role":"system","content":system},{"role":"user","content":prompt}])
        return r.choices[0].message.content
    except Exception as e: return f"AI error: {e}"

def ask_groq_chat(msgs, system, max_tokens=800):
    try:
        r = get_groq().chat.completions.create(
            model="llama-3.3-70b-versatile", max_tokens=max_tokens,
            messages=[{"role":"system","content":system}]+msgs)
        return r.choices[0].message.content
    except Exception as e: return f"AI error: {e}"

# ─── Data Fetchers ─────────────────────────────────────────────────────────────
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
def fetch_aq(lat, lon):
    url = (f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}"
           f"&current=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,european_aqi,us_aqi")
    try:
        r = requests.get(url, timeout=20); r.raise_for_status(); return r.json()
    except: return None

@st.cache_data(ttl=3600)
def geocode(city):
    try:
        r = requests.get(
            f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json",
            timeout=10)
        d = r.json()
        if d.get("results"):
            res = d["results"][0]
            return res["latitude"], res["longitude"], res.get("country",""), res.get("name",city), res.get("admin1","")
        return None
    except: return None

# ─── Scoring ───────────────────────────────────────────────────────────────────
def w_score(w):
    c=w["current"]; s=100
    t=c["temperature_2m"]; h=c["relative_humidity_2m"]
    wnd=c["wind_speed_10m"]; uv=c.get("uv_index",0) or 0; pr=c.get("precipitation",0) or 0
    if t>42 or t<-2: s-=28
    elif t>38 or t<3: s-=14
    if h>95 or h<10: s-=18
    elif h>85 or h<20: s-=8
    if wnd>70: s-=22
    elif wnd>40: s-=10
    if uv>11: s-=16
    elif uv>8: s-=7
    if pr>30: s-=18
    elif pr>8: s-=6
    return max(0,min(100,s))

def p_score(aq):
    if not aq: return None
    aqi = aq.get("current",{}).get("european_aqi") or aq.get("current",{}).get("us_aqi")
    if aqi is None: return None
    return max(0,min(100,round(100-aqi)))

def e_score(ws,ps):
    if ps is None: return ws
    return max(0,min(100,round(ws*0.55+ps*0.45)))

def grade(s):
    s = s if s is not None else 0
    if s>=80: return "#00ffb4","OPTIMAL"
    elif s>=65: return "#a0ff00","GOOD"
    elif s>=45: return "#f0c040","MODERATE"
    elif s>=25: return "#ff8c42","STRESSED"
    else: return "#ff4060","CRITICAL"

def bcol(v,g,b):
    if v<=g: return "#00ffb4"
    elif v<=b: return "#f0c040"
    else: return "#ff4060"

WMO = {0:"CLEAR SKY",1:"MAINLY CLEAR",2:"PARTLY CLOUDY",3:"OVERCAST",
       45:"FOG",51:"LIGHT DRIZZLE",53:"DRIZZLE",55:"HEAVY DRIZZLE",
       61:"SLIGHT RAIN",63:"MODERATE RAIN",65:"HEAVY RAIN",
       71:"SLIGHT SNOW",73:"MODERATE SNOW",75:"HEAVY SNOW",
       80:"RAIN SHOWERS",81:"MODERATE SHOWERS",82:"VIOLENT SHOWERS",
       95:"THUNDERSTORM",96:"THUNDERSTORM+HAIL",99:"THUNDERSTORM+HEAVY HAIL"}
def wdesc(c): return WMO.get(c,"UNKNOWN")

def detect_crises(w, aq_cur, lat):
    alerts = []
    daily = w["daily"]; cur = w["current"]
    month = datetime.now().month
    is_tropical = abs(lat) < 25
    is_monsoon = is_tropical and month in [6,7,8,9,10]
    precip_list = [p for p in daily["precipitation_sum"] if p is not None]
    total_rain_7d = sum(precip_list)
    max_daily_rain = max(precip_list) if precip_list else 0
    max_temps = [t for t in daily["temperature_2m_max"] if t]
    min_temps = [t for t in daily["temperature_2m_min"] if t]
    max_wind = max((v for v in daily["wind_speed_10m_max"] if v), default=0)
    humidity = cur.get("relative_humidity_2m",0)

    if aq_cur:
        aqi = aq_cur.get("european_aqi") or aq_cur.get("us_aqi")
        if aqi and aqi>100:
            alerts.append(("crisis","AIR QUALITY HAZARD",f"AQI {aqi} — Extremely hazardous. Immediate crop and health risk. Halt outdoor farming operations."))
        elif aqi and aqi>80:
            alerts.append(("crisis","SEVERE AIR POLLUTION",f"AQI {aqi} — Severe pollution. Photosynthesis reduced, sensitive crops under high stress."))
        elif aqi and aqi>50:
            alerts.append(("warning","POOR AIR QUALITY",f"AQI {aqi} — Elevated pollution reducing crop productivity. Monitor leaf health."))

    if max_daily_rain > 80 or total_rain_7d > 200:
        alerts.append(("crisis","FLASH FLOOD RISK — EXTREME",
            f"Extreme rainfall: {max_daily_rain:.0f}mm peak single day, {total_rain_7d:.0f}mm total / 7 days. "
            f"Severe waterlogging and field flooding imminent. Activate drainage, move machinery to higher ground."))
    elif max_daily_rain > 40 or total_rain_7d > 120:
        alerts.append(("crisis","FLOOD PROBABILITY HIGH",
            f"{sum(1 for p in precip_list if p>40)} days with >40mm rainfall. {total_rain_7d:.0f}mm weekly total. "
            f"Waterlogging risk high. Clear drainage channels, avoid sowing."))
    elif total_rain_7d > 60:
        alerts.append(("warning","HEAVY RAINFALL ADVISORY",
            f"{total_rain_7d:.0f}mm forecast over 7 days. Reduce irrigation, monitor drainage capacity."))

    if is_monsoon and humidity > 85 and total_rain_7d > 30:
        alerts.append(("warning","ACTIVE MONSOON — DISEASE RISK",
            f"Monsoon conditions active. {humidity}% humidity + {total_rain_7d:.0f}mm rainfall creates optimal fungal pathogen environment. "
            f"High risk: blast, blight, leaf spot. Apply preventive fungicide, improve crop spacing."))

    if total_rain_7d < 2 and cur.get("precipitation",0) < 0.5:
        avg_max = sum(max_temps)/len(max_temps) if max_temps else 30
        if avg_max > 28:
            alerts.append(("crisis","DROUGHT CONDITIONS ACTIVE",
                f"Near-zero rainfall ({total_rain_7d:.1f}mm / 7 days) with avg max {avg_max:.1f}°C. "
                f"Critical soil moisture deficit. Emergency irrigation required immediately."))
        elif avg_max > 18:
            alerts.append(("warning","LOW RAINFALL",
                f"Only {total_rain_7d:.1f}mm forecast. Monitor soil moisture closely, schedule supplemental irrigation."))

    extreme_heat = sum(1 for t in max_temps if t>42)
    high_heat = sum(1 for t in max_temps if t>38)
    if extreme_heat >= 2:
        alerts.append(("crisis","EXTREME HEAT WAVE",
            f"{extreme_heat} days above 42°C. Critical crop stress. Increase irrigation 40–60%, apply mulch, deploy shade netting."))
    elif high_heat >= 3:
        alerts.append(("warning","HEAT STRESS ADVISORY",
            f"{high_heat} days above 38°C forecast. Adjust irrigation timing to early morning and evening."))

    frost_nights = sum(1 for t in min_temps if t<2)
    if frost_nights >= 1:
        alerts.append(("crisis","FROST WARNING",
            f"{frost_nights} night(s) with sub-2°C temperatures. Cover sensitive crops immediately."))

    if max_wind > 80:
        alerts.append(("crisis","STORM FORCE WINDS",
            f"Extreme gusts up to {max_wind:.0f} km/h. Secure all infrastructure, delay spraying."))
    elif max_wind > 50:
        alerts.append(("warning","HIGH WIND ADVISORY",
            f"Wind speeds up to {max_wind:.0f} km/h. Avoid pesticide application."))

    max_uv = max((v for v in daily["uv_index_max"] if v), default=0)
    if max_uv >= 11:
        alerts.append(("warning","EXTREME UV",
            f"UV index {max_uv:.0f}. Leaf scorch risk on sensitive crops. Deploy shade netting, schedule fieldwork for dawn."))

    if not alerts:
        alerts.append(("safe","ALL SYSTEMS NOMINAL",
            f"No significant agricultural threats detected. {cur['temperature_2m']:.1f}°C, {humidity}% RH, {total_rain_7d:.0f}mm/7d. Conditions within normal parameters."))
    return alerts

def recommend_crops(w):
    c=w["current"]; t=c["temperature_2m"]; h=c["relative_humidity_2m"]
    pl=[p for p in w["daily"]["precipitation_sum"] if p is not None]
    ar=sum(pl)/len(pl) if pl else 0; result=[]
    if 20<=t<=38 and h>50:
        result.append(("🌾","RICE",95,"Optimal temperature-humidity matrix","High water · 3–4 month cycle · transplant at 21 days"))
        result.append(("🌿","SUGARCANE",88,"Strong heat-humidity compatibility","Weekly deep irrigation · monthly NPK · 10–12 months"))
    if 18<=t<=35:
        result.append(("🥜","GROUNDNUT",85,"Temperature envelope aligned","Sandy loam · dry finish window required"))
        result.append(("🌽","MAIZE",82,"Thermophilic conditions met","Moderate water · high N · 90-day cycle"))
    if t>=25 and h<70:
        result.append(("🍅","TOMATO",78,"Warm-dry matrix ideal","Consistent drip · stake · blight monitoring"))
        result.append(("🌶️","CHILLI",76,"Low humidity reduces fungal risk","Potassium-rich · drip irrigation preferred"))
    if t<22:
        result.append(("🥬","SPINACH",90,"Cool threshold optimal","Direct sow · 6–8 week harvest · high N"))
        result.append(("🥕","CARROT",84,"Root development favoured","Deep loose bed · thin at 4cm · 70 days"))
        result.append(("🧅","ONION",80,"Bulb initiation suits cool air","Reduce water at bulbing · raised bed"))
    if ar<3 and t>20:
        result.append(("🌻","SUNFLOWER",88,"Drought-tolerance matched","Deep taproot · minimal input · 80–95 days"))
        result.append(("🫘","MOONG DAL",83,"Short-season drought legume","Sandy loam · 60–70 days"))
    result.sort(key=lambda x:-x[2]); return result[:5]

# ─── SVG Rings ────────────────────────────────────────────────────────────────
def make_ring(score, color, sz=130, sw=9):
    v = score if score is not None else 0
    r = (sz/2)-sw; circ = 2*math.pi*r; dash = (v/100)*circ
    gid = f"g{abs(hash(f'{v}{color}{sz}'))%99999}"
    return f"""<svg width="{sz}" height="{sz}" viewBox="0 0 {sz} {sz}">
  <defs>
    <filter id="{gid}"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <linearGradient id="lg{gid}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#00ffb4"/>
      <stop offset="50%" style="stop-color:{color}"/>
      <stop offset="100%" style="stop-color:#00e5ff;stop-opacity:0.7"/>
    </linearGradient>
  </defs>
  <circle cx="{sz/2}" cy="{sz/2}" r="{r}" fill="none" stroke="rgba(0,255,180,0.07)" stroke-width="{sw}"/>
  <circle cx="{sz/2}" cy="{sz/2}" r="{r}" fill="none" stroke="url(#lg{gid})" stroke-width="{sw}"
    stroke-linecap="round" stroke-dasharray="{dash:.1f} {circ:.1f}"
    transform="rotate(-90 {sz/2} {sz/2})" filter="url(#{gid})"/>
  <circle cx="{sz/2}" cy="{sz/2}" r="{r-sw-3}" fill="none" stroke="rgba(0,255,180,0.04)" stroke-width="0.5"/>
</svg>"""

def mini_ring(score, color="#00ffb4", sz=65):
    r=(sz/2)-5; circ=2*math.pi*r; dash=(score/100)*circ
    return f"""<svg width="{sz}" height="{sz}" viewBox="0 0 {sz} {sz}">
  <circle cx="{sz/2}" cy="{sz/2}" r="{r}" fill="none" stroke="rgba(0,255,180,0.08)" stroke-width="4"/>
  <circle cx="{sz/2}" cy="{sz/2}" r="{r}" fill="none" stroke="{color}" stroke-width="4"
    stroke-linecap="round" stroke-dasharray="{dash:.1f} {circ:.1f}" transform="rotate(-90 {sz/2} {sz/2})"/>
  <text x="{sz/2}" y="{sz/2+4}" text-anchor="middle" font-family="Orbitron,sans-serif"
    font-size="11" font-weight="800" fill="{color}">{score}</text>
</svg>"""

# ═════════════════════════════════════════════════════════════════════════════
# LOCATION SYSTEM — The fully working one
# ═════════════════════════════════════════════════════════════════════════════

# Show location input ABOVE everything else as a prominent bar
st.markdown("""
<div style="background:linear-gradient(135deg,rgba(0,22,32,0.97),rgba(0,12,20,0.99));
  border:1px solid rgba(0,255,180,0.15);border-radius:10px;
  padding:1.2rem 1.5rem;margin-bottom:1.5rem;position:relative;overflow:hidden;">
  <div style="position:absolute;top:0;left:0;right:0;height:1px;
    background:linear-gradient(90deg,transparent,#00ffb4,#a0ff00,transparent)"></div>
  <div style="font-family:'Orbitron',sans-serif;font-size:0.58rem;font-weight:700;
    letter-spacing:0.2em;color:#00a878;margin-bottom:0.8rem;">
    ◈ LOCATION ACQUISITION SYSTEM
  </div>
""", unsafe_allow_html=True)

loc_col1, loc_col2 = st.columns([2, 1])
with loc_col1:
    city_input = st.text_input(
        "ENTER CITY OR REGION",
        value=st.session_state.get("city", "Bengaluru"),
        placeholder="Type any city — e.g. Delhi, Mumbai, Chennai, Hyderabad...",
        key="city_text_input",
        label_visibility="visible"
    )
    if city_input != st.session_state.get("city", "Bengaluru"):
        st.session_state["city"] = city_input

with loc_col2:
    # GPS button with full working JS
    components.html("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');
    body{margin:0;background:transparent}
    #gps-btn{
        width:100%;height:44px;margin-top:22px;
        background:linear-gradient(135deg,rgba(0,255,180,0.08),rgba(160,255,0,0.12));
        border:1px solid rgba(0,255,180,0.35);
        border-radius:7px;color:#00ffb4;
        font-family:'Orbitron',sans-serif;font-size:0.58rem;
        letter-spacing:0.15em;font-weight:700;cursor:pointer;
        transition:all 0.25s;text-transform:uppercase;
        display:flex;align-items:center;justify-content:center;gap:8px;
    }
    #gps-btn:hover{
        background:rgba(0,255,180,0.18);
        box-shadow:0 0 25px rgba(0,255,180,0.25),0 0 50px rgba(0,255,180,0.1);
        color:#fff;border-color:#00ffb4;
    }
    #gps-btn:disabled{opacity:0.6;cursor:not-allowed}
    #gps-status{
        font-family:monospace;font-size:0.65rem;
        color:#00a878;margin-top:5px;min-height:16px;
        text-align:center;
    }
    </style>
    <button id="gps-btn" onclick="getMyLocation()">
        <span id="btn-icon">⊕</span>
        <span id="btn-txt">USE MY LOCATION</span>
    </button>
    <div id="gps-status"></div>
    <script>
    function getMyLocation() {
        var btn = document.getElementById('gps-btn');
        var icon = document.getElementById('btn-icon');
        var txt = document.getElementById('btn-txt');
        var status = document.getElementById('gps-status');
        
        icon.innerText = '⏳';
        txt.innerText = 'ACQUIRING GPS...';
        btn.disabled = true;
        status.style.color = '#00a878';
        status.innerText = 'Requesting location permission...';
        
        if (!navigator.geolocation) {
            status.innerText = '✗ GPS not supported by browser';
            status.style.color = '#ff4060';
            icon.innerText = '⊕';
            txt.innerText = 'USE MY LOCATION';
            btn.disabled = false;
            return;
        }
        
        navigator.geolocation.getCurrentPosition(
            function(position) {
                var lat = position.coords.latitude.toFixed(6);
                var lon = position.coords.longitude.toFixed(6);
                status.innerText = '✓ Lock acquired: ' + lat + ', ' + lon;
                status.style.color = '#00ffb4';
                icon.innerText = '✓';
                txt.innerText = 'LOCK ACQUIRED';
                
                // Navigate to same page with GPS params
                var currentUrl = window.parent.location.href.split('?')[0];
                var newUrl = currentUrl + '?gps=' + lat + ',' + lon;
                
                setTimeout(function() {
                    window.parent.location.href = newUrl;
                }, 500);
            },
            function(error) {
                icon.innerText = '⊕';
                txt.innerText = 'USE MY LOCATION';
                btn.disabled = false;
                status.style.color = '#ff4060';
                var messages = {
                    1: '✗ Permission denied — enable location in browser settings',
                    2: '✗ Position unavailable — try again',
                    3: '✗ Timeout — check signal and retry'
                };
                status.innerText = messages[error.code] || '✗ Unknown error';
            },
            {
                timeout: 15000,
                enableHighAccuracy: true,
                maximumAge: 0
            }
        );
    }
    </script>
    """, height=85)

st.markdown("</div>", unsafe_allow_html=True)

# ─── Use the city from text input ─────────────────────────────────────────────
active_city = st.session_state.get("city", "Bengaluru")

# ─── Geocode ──────────────────────────────────────────────────────────────────
geo = geocode(active_city)
if not geo:
    st.markdown(f"""
    <div style="background:rgba(255,40,60,0.08);border:1px solid rgba(255,40,60,0.25);
      border-radius:8px;padding:1rem 1.4rem;color:#ffaabc;font-family:'Share Tech Mono',monospace;font-size:0.8rem">
      ◈ LOCATION NOT FOUND: "{active_city}" — Please check spelling and try again.
    </div>""", unsafe_allow_html=True)
    st.stop()

lat, lon, country, city_name, region = geo
weather = fetch_weather(lat, lon)
if not weather: st.stop()

aq = fetch_aq(lat, lon)
cur = weather["current"]
daily = weather["daily"]
aq_cur = aq.get("current",{}) if aq else {}
ws = w_score(weather)
ps = p_score(aq)
es = e_score(ws, ps)
ag = max(0,min(100,round(es*0.7+ws*0.3)))
now = datetime.now()
total_rain = sum(p for p in daily["precipitation_sum"] if p)
crisis_list = detect_crises(weather, aq_cur, lat)
has_crisis = any(c[0]=="crisis" for c in crisis_list)
has_warning = any(c[0]=="warning" for c in crisis_list)

# ═════════════════════════════════════════════════════════════════════════════
# COMMAND HEADER
# ═════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="av-header">
  <div class="logo-block">
    <div class="logo-text">AEROVEDA</div>
    <div class="logo-tagline">AGRI-OS v3.0 · AI AGRICULTURAL INTELLIGENCE · EARTH EDITION</div>
  </div>
  <div class="hdr-stats">
    <div class="hdr-chip"><div class="pulse-dot cyan"></div>WEATHER LIVE</div>
    <div class="hdr-chip"><div class="pulse-dot lime"></div>AQ SENSORS</div>
    <div class="hdr-chip"><div class="pulse-dot lime"></div>AI ONLINE</div>
    <div class="hdr-chip">
      <div class="pulse-dot {'red' if has_crisis else 'cyan'}"></div>
      {'⚠ ALERTS ACTIVE' if has_crisis or has_warning else 'NOMINAL'}
    </div>
  </div>
  <div class="loc-bar">
    <div class="pulse-dot cyan"></div>
    <span>{city_name.upper()}{', '+region if region else ''}, {country.upper()} ·
    {lat:.4f}°{'N' if lat>=0 else 'S'} {lon:.4f}°{'E' if lon>=0 else 'W'} ·
    {now.strftime('%H:%M')} UTC</span>
  </div>
</div>
""", unsafe_allow_html=True)

# TICKER
pm25v = float(aq_cur.get("pm2_5",0) or 0)
t_chunks = [
    f"TEMP: {cur['temperature_2m']:.1f}°C",
    f"HUMIDITY: {cur['relative_humidity_2m']}%",
    f"WIND: {cur['wind_speed_10m']:.1f} KM/H",
    f"UV: {cur.get('uv_index',0) or 0:.0f}",
    f"PM2.5: {pm25v:.1f} μG/M³",
    f"AQI: {aq_cur.get('european_aqi','N/A')}",
    f"7D RAIN: {total_rain:.0f}MM",
    f"CONDITIONS: {wdesc(cur['weather_code'])}",
    f"ENV SCORE: {es}/100",
    f"AG POTENTIAL: {ag}/100",
    f"LOCATION: {city_name.upper()}, {country.upper()}",
    f"{now.strftime('%d %b %Y')}",
]
sep = '<span class="tsep">//</span>'
ts = sep.join(t_chunks)
st.markdown(f"""
<div class="ticker-wrap">
  <div class="ticker-inner">{ts}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{ts}</div>
</div>""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# SCORE GRID
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("""<div class="av-section">
  <div class="av-section-badge">INTELLIGENCE SCORES</div>
  <div class="av-section-line"></div>
  <div class="av-section-code">SCORE_ENGINE::v3.0</div>
</div>""", unsafe_allow_html=True)

sc = st.columns(4)
for col, score, name, hint in [
    (sc[0], ps, "POLLUTION INDEX", "Higher = Cleaner Air"),
    (sc[1], ws, "WEATHER SCORE", "Temp · Wind · UV · Rain"),
    (sc[2], es, "ENV SCORE", "55% Weather + 45% AQ"),
    (sc[3], ag, "AG POTENTIAL", "Overall Farm Suitability"),
]:
    v = score if score is not None else 0
    color, gr = grade(v)
    disp = str(score) if score is not None else "N/A"
    with col:
        st.markdown(f"""
<div class="score-orb">
  <div class="ct ct-l"></div><div class="ct ct-r"></div>
  <div class="cb cb-l"></div><div class="cb cb-r"></div>
  <div class="ring-host">
    {make_ring(v, color)}
    <div class="ring-center">
      <div class="ring-num" style="color:{color};text-shadow:0 0 15px {color}80">{disp}</div>
      <div class="ring-slash">/ 100</div>
    </div>
  </div>
  <div class="orb-title">{name}</div>
  <div class="orb-grade" style="color:{color}">{gr}</div>
  <div class="orb-hint">{hint}</div>
</div>""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# TABS
# ═════════════════════════════════════════════════════════════════════════════
tabs = st.tabs([
    "🌍 HOLO GLOBE",
    "◈ ENVIRONMENT",
    "⚠ CRISIS INTEL",
    "🌱 CROP ENGINE",
    "🔬 SIMULATION",
    "🔍 CROP SCANNER",
    "◈ FIELD AI"
])

# ══════════════════════════════════════════════════════════════════
# TAB 0 — 3D HOLOGRAPHIC GLOBE (Canvas-based, no external libs)
# ══════════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown("""<div class="av-section">
      <div class="av-section-badge">3D HOLOGRAPHIC TERRAIN INTELLIGENCE</div>
      <div class="av-section-line"></div>
      <div class="av-section-code">SAT::HOLO_TERRAIN_v4</div>
    </div>""", unsafe_allow_html=True)

    layer_opt = st.selectbox("◈ ACTIVE INTELLIGENCE LAYER", [
        "🌱 Crop Suitability","💧 Water Availability","🌡 Temperature Zones",
        "💨 Humidity Distribution","🟢 Vegetation Index (NDVI)","🏜 Drought Probability",
        "🌊 Flood Risk Zones","🦗 Pest Pressure","🌍 Soil Health",
        "☁ Climate Stress","🌧 Rainfall Patterns"
    ])

    layer_configs = {
        "🌱 Crop Suitability":      {"c0":"#00ffb4","c1":"#a0ff00","c2":"#f0c040","c3":"#ff8c42","c4":"#ff4060","name":"CROP SUITABILITY"},
        "💧 Water Availability":    {"c0":"#00e5ff","c1":"#00b8ff","c2":"#f0c040","c3":"#ff8c42","c4":"#ff4060","name":"WATER AVAILABILITY"},
        "🌡 Temperature Zones":     {"c0":"#ff4060","c1":"#ff8c42","c2":"#f0c040","c3":"#a0ff00","c4":"#00ffb4","name":"TEMPERATURE ZONES"},
        "💨 Humidity Distribution": {"c0":"#00e5ff","c1":"#00ffb4","c2":"#a0ff00","c3":"#f0c040","c4":"#ff8c42","name":"HUMIDITY MAP"},
        "🟢 Vegetation Index (NDVI)":{"c0":"#00ff80","c1":"#80ff40","c2":"#ccff00","c3":"#886600","c4":"#442200","name":"NDVI INDEX"},
        "🏜 Drought Probability":   {"c0":"#ff4060","c1":"#ff8c42","c2":"#f0c040","c3":"#a0ff00","c4":"#00ffb4","name":"DROUGHT RISK"},
        "🌊 Flood Risk Zones":      {"c0":"#0040ff","c1":"#0088ff","c2":"#00e5ff","c3":"#f0c040","c4":"#00ffb4","name":"FLOOD RISK"},
        "🦗 Pest Pressure":         {"c0":"#ff4060","c1":"#ff8c42","c2":"#f0c040","c3":"#a0ff00","c4":"#00ffb4","name":"PEST PRESSURE"},
        "🌍 Soil Health":           {"c0":"#00ffb4","c1":"#80ff60","c2":"#ccaa44","c3":"#886600","c4":"#442200","name":"SOIL HEALTH"},
        "☁ Climate Stress":         {"c0":"#ff4060","c1":"#ff8c42","c2":"#f0c040","c3":"#a0ff00","c4":"#00ffb4","name":"CLIMATE STRESS"},
        "🌧 Rainfall Patterns":     {"c0":"#0040ff","c1":"#0088ff","c2":"#00e5ff","c3":"#f0c040","c4":"#ff8c42","name":"RAINFALL"},
    }
    lc = layer_configs.get(layer_opt, layer_configs["🌱 Crop Suitability"])

    globe_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#010d12;overflow:hidden;font-family:'Orbitron',monospace}}
canvas{{display:block;width:100%;height:100%}}
#wrap{{position:relative;width:100%;height:540px}}
.hud{{position:absolute;inset:0;pointer-events:none}}
.hud-tl{{position:absolute;top:14px;left:14px}}
.hud-tr{{position:absolute;top:14px;right:14px;text-align:right}}
.hud-bl{{position:absolute;bottom:14px;left:14px}}
.hud-br{{position:absolute;bottom:14px;right:14px;text-align:right}}
.badge{{
  display:inline-block;
  background:rgba(1,13,18,0.92);
  border:1px solid rgba(0,255,180,0.3);
  border-radius:4px;padding:5px 12px;
  font-size:9px;color:#00ffb4;letter-spacing:2px;
  margin-bottom:5px;
  font-family:'Orbitron',monospace;
}}
.badge.lime{{border-color:rgba(160,255,0,0.3);color:#a0ff00}}
.badge.red{{border-color:rgba(255,64,96,0.4);color:#ff4060}}
.badge.blue{{border-color:rgba(0,229,255,0.3);color:#00e5ff}}
.legend{{
  background:rgba(1,13,18,0.92);
  border:1px solid rgba(0,255,180,0.2);
  border-radius:6px;padding:10px 13px;
  display:inline-block;
}}
.leg-t{{font-size:8px;color:#00a878;letter-spacing:2px;margin-bottom:8px;font-family:'Orbitron',monospace}}
.leg-row{{display:flex;align-items:center;gap:8px;margin-bottom:4px}}
.leg-dot{{width:10px;height:10px;border-radius:2px;flex-shrink:0;box-shadow:0 0 6px currentColor}}
.leg-l{{font-size:8px;color:#9efff0;font-family:monospace}}
.scan-line{{position:absolute;left:0;right:0;height:2px;pointer-events:none;
  background:linear-gradient(90deg,transparent,rgba(0,255,180,0.4),rgba(160,255,0,0.3),transparent);
  animation:scan 5s linear infinite;}}
@keyframes scan{{0%{{top:0%}}100%{{top:100%}}}}
</style>
</head>
<body>
<div id="wrap">
  <canvas id="c"></canvas>
  <div class="hud">
    <div class="scan-line"></div>
    <div class="hud-tl">
      <div class="badge">◈ {lc['name']}</div><br>
      <div class="badge blue">{city_name.upper()}, {country.upper()}</div><br>
      <div class="badge">{lat:.4f}°{'N' if lat>=0 else 'S'} {lon:.4f}°{'E' if lon>=0 else 'W'}</div>
    </div>
    <div class="hud-tr">
      <div class="badge {'lime' if es>=65 else 'red' if es<45 else ''}">ENV: {es}/100</div><br>
      <div class="badge">AG: {ag}/100</div><br>
      <div class="badge blue">{wdesc(cur['weather_code'])}</div>
    </div>
    <div class="hud-bl">
      <div class="legend">
        <div class="leg-t">ZONE CLASSIFICATION</div>
        <div class="leg-row"><div class="leg-dot" style="background:{lc['c0']};color:{lc['c0']}"></div><div class="leg-l">OPTIMAL</div></div>
        <div class="leg-row"><div class="leg-dot" style="background:{lc['c1']};color:{lc['c1']}"></div><div class="leg-l">GOOD</div></div>
        <div class="leg-row"><div class="leg-dot" style="background:{lc['c2']};color:{lc['c2']}"></div><div class="leg-l">MODERATE</div></div>
        <div class="leg-row"><div class="leg-dot" style="background:{lc['c3']};color:{lc['c3']}"></div><div class="leg-l">STRESSED</div></div>
        <div class="leg-row"><div class="leg-dot" style="background:{lc['c4']};color:{lc['c4']}"></div><div class="leg-l">CRITICAL</div></div>
      </div>
    </div>
    <div class="hud-br">
      <div class="badge">{cur['temperature_2m']:.1f}°C · {cur['relative_humidity_2m']}% RH</div><br>
      <div class="badge blue">RAIN 7D: {total_rain:.0f}MM</div>
    </div>
  </div>
</div>
<script>
var canvas = document.getElementById('c');
var wrap = document.getElementById('wrap');
canvas.width = wrap.offsetWidth || 900;
canvas.height = 540;
var ctx = canvas.getContext('2d');
var W = canvas.width, H = canvas.height;
var cx = W/2, cy = H/2;
var R = Math.min(W*0.38, H*0.42);

var targetLat = {lat} * Math.PI/180;
var targetLon = {lon} * Math.PI/180;
var rotY = Math.PI - targetLon;
var rotX = -targetLat * 0.5;
var t = 0;
var rotSpeed = 0.004;

var colors = ['{lc["c0"]}','{lc["c1"]}','{lc["c2"]}','{lc["c3"]}','{lc["c4"]}'];

function hexToRgba(hex, alpha) {{
  var r=parseInt(hex.slice(1,3),16),g=parseInt(hex.slice(3,5),16),b=parseInt(hex.slice(5,7),16);
  return 'rgba('+r+','+g+','+b+','+alpha+')';
}}

// Simplified continent outlines [lat, lon] pairs
var landmasses = [
  // South Asia / India
  [[8,77],[8,80],[10,80],[13,80],[15,80],[20,87],[22,88],[21,87],[24,88],[26,90],[28,97],[27,97],[35,77],[36,75],[37,72],[25,63],[22,68],[20,73],[18,73],[15,74],[10,77],[8,77]],
  // Southeast Asia
  [[22,100],[22,108],[18,109],[12,109],[10,104],[10,99],[15,98],[22,100]],
  // East Asia
  [[22,108],[22,122],[30,122],[38,122],[42,130],[50,140],[55,140],[55,130],[50,120],[45,120],[40,118],[35,120],[30,122]],
  // Africa
  [[37,10],[37,37],[11,44],[-5,40],[-35,20],[-35,-17],[-6,-14],[4,8],[15,12],[4,9],[37,10]],
  // Europe
  [[36,-9],[36,28],[48,40],[60,30],[71,28],[71,26],[55,21],[53,14],[48,8],[44,5],[36,-9]],
  // North America
  [[15,-92],[15,-88],[25,-80],[45,-65],[50,-55],[70,-55],[72,-140],[60,-145],[20,-110],[15,-92]],
  // South America
  [[-5,-80],[-5,-35],[-35,-55],[-55,-70],[-55,-66],[-20,-70],[0,-78],[-5,-80]],
  // Australia
  [[-15,130],[-15,138],[-25,153],[-38,148],[-38,115],[-22,114],[-15,130]],
];

var zones = [
  [{lat+0.15},{lon-0.10},0,0.28],
  [{lat-0.08},{lon+0.20},1,0.22],
  [{lat+0.22},{lon+0.12},2,0.19],
  [{lat-0.18},{lon-0.14},1,0.24],
  [{lat+0.06},{lon-0.26},3,0.17],
  [{lat-0.06},{lon+0.30},0,0.20],
  [{lat+0.32},{lon-0.06},4,0.15],
  [{lat-0.28},{lon+0.08},2,0.18],
  [{lat+0.10},{lon+0.35},1,0.16],
  [{lat-0.14},{lon-0.30},3,0.14],
];

function latLonTo3D(lat, lon, r) {{
  var phi = lat*Math.PI/180, lam = lon*Math.PI/180;
  return [r*Math.cos(phi)*Math.cos(lam), r*Math.sin(phi), r*Math.cos(phi)*Math.sin(lam)];
}}

function rotate(x,y,z,ry,rx) {{
  var x1=x*Math.cos(ry)-z*Math.sin(ry), z1=x*Math.sin(ry)+z*Math.cos(ry);
  var y2=y*Math.cos(rx)-z1*Math.sin(rx), z2=y*Math.sin(rx)+z1*Math.cos(rx);
  return [x1,y2,z2];
}}

function project(x,y,z) {{
  var f=600, s=f/(f+z+R*0.4);
  return [cx+x*s, cy-y*s, s];
}}

function isVisible(z) {{ return z>-R*0.15; }}

function drawFrame() {{
  ctx.clearRect(0,0,W,H);

  // ── DEEP SPACE BG ──
  var bg=ctx.createRadialGradient(cx,cy,R*0.05,cx,cy,W*0.8);
  bg.addColorStop(0,'rgba(0,35,50,0.98)');
  bg.addColorStop(0.3,'rgba(0,20,30,0.99)');
  bg.addColorStop(0.7,'rgba(0,8,14,1)');
  bg.addColorStop(1,'rgba(1,13,18,1)');
  ctx.fillStyle=bg; ctx.fillRect(0,0,W,H);

  // Stars
  if(t===0) {{
    ctx.fillStyle='rgba(0,255,180,0.15)';
    for(var i=0;i<200;i++) {{
      var sx=Math.random()*W,sy=Math.random()*H,ss=Math.random()*1.5;
      ctx.beginPath();ctx.arc(sx,sy,ss,0,Math.PI*2);ctx.fill();
    }}
  }}

  // ── OUTER GLOW ──
  var glow=ctx.createRadialGradient(cx,cy,R*0.9,cx,cy,R*1.4);
  glow.addColorStop(0,'rgba(0,255,180,0.08)');
  glow.addColorStop(0.4,'rgba(160,255,0,0.04)');
  glow.addColorStop(0.7,'rgba(0,229,255,0.02)');
  glow.addColorStop(1,'transparent');
  ctx.fillStyle=glow;
  ctx.beginPath();ctx.arc(cx,cy,R*1.4,0,Math.PI*2);ctx.fill();

  // ── ATMOSPHERE ──
  var atm=ctx.createRadialGradient(cx-R*0.2,cy-R*0.2,R*0.7,cx,cy,R*1.08);
  atm.addColorStop(0,'rgba(0,229,255,0.12)');
  atm.addColorStop(0.5,'rgba(0,255,180,0.06)');
  atm.addColorStop(0.8,'rgba(160,255,0,0.03)');
  atm.addColorStop(1,'transparent');
  ctx.fillStyle=atm;
  ctx.beginPath();ctx.arc(cx,cy,R*1.08,0,Math.PI*2);ctx.fill();

  // ── GLOBE BASE ──
  ctx.save();
  ctx.beginPath();ctx.arc(cx,cy,R,0,Math.PI*2);ctx.clip();

  var globeGrad=ctx.createRadialGradient(cx-R*0.3,cy-R*0.25,R*0.05,cx,cy,R);
  globeGrad.addColorStop(0,'rgba(0,60,80,0.97)');
  globeGrad.addColorStop(0.3,'rgba(0,35,55,0.98)');
  globeGrad.addColorStop(0.6,'rgba(0,20,38,0.99)');
  globeGrad.addColorStop(1,'rgba(0,8,16,1)');
  ctx.fillStyle=globeGrad;
  ctx.fillRect(cx-R,cy-R,R*2,R*2);

  // ── GRID LINES ──
  var currentRotY = rotY + t*rotSpeed;

  for(var la=-80;la<=80;la+=20) {{
    ctx.beginPath();var first=true;
    for(var lo=-180;lo<=180;lo+=4) {{
      var p3=latLonTo3D(la,lo,R);
      var rot=rotate(p3[0],p3[1],p3[2],currentRotY,rotX);
      if(!isVisible(rot[2])){{first=true;continue}}
      var pr=project(rot[0],rot[1],rot[2]);
      if(first){{ctx.moveTo(pr[0],pr[1]);first=false}}else ctx.lineTo(pr[0],pr[1]);
    }}
    var brightness=la===0?0.12:0.05;
    ctx.strokeStyle='rgba(0,255,180,'+brightness+')';ctx.lineWidth=la===0?0.8:0.4;ctx.stroke();
  }}
  for(var lo2=-180;lo2<180;lo2+=30) {{
    ctx.beginPath();var first2=true;
    for(var la2=-80;la2<=80;la2+=3) {{
      var p32=latLonTo3D(la2,lo2,R);
      var rot2=rotate(p32[0],p32[1],p32[2],currentRotY,rotX);
      if(!isVisible(rot2[2])){{first2=true;continue}}
      var pr2=project(rot2[0],rot2[1],rot2[2]);
      if(first2){{ctx.moveTo(pr2[0],pr2[1]);first2=false}}else ctx.lineTo(pr2[0],pr2[1]);
    }}
    ctx.strokeStyle='rgba(0,255,180,0.04)';ctx.lineWidth=0.3;ctx.stroke();
  }}

  // ── CONTINENTS ──
  landmasses.forEach(function(pts) {{
    ctx.beginPath();var fc=true;
    pts.forEach(function(p) {{
      var p3=latLonTo3D(p[0],p[1],R*1.002);
      var rot=rotate(p3[0],p3[1],p3[2],currentRotY,rotX);
      if(rot[2]<-R*0.18){{fc=true;return}}
      var pr=project(rot[0],rot[1],rot[2]);
      if(fc){{ctx.moveTo(pr[0],pr[1]);fc=false}}else ctx.lineTo(pr[0],pr[1]);
    }});
    ctx.closePath();
    ctx.fillStyle='rgba(0,120,80,0.22)';ctx.fill();
    ctx.strokeStyle='rgba(0,255,180,0.3)';ctx.lineWidth=0.6;ctx.stroke();
  }});

  // ── AGRICULTURAL ZONES ──
  zones.forEach(function(z) {{
    var zLat=z[0],zLon=z[1],ci=z[2],rad=z[3];
    var color=colors[ci];

    // Draw filled zone circle
    var centerP3=latLonTo3D(zLat,zLon,R*1.003);
    var centerRot=rotate(centerP3[0],centerP3[1],centerP3[2],currentRotY,rotX);
    if(!isVisible(centerRot[2])) return;
    var centerPr=project(centerRot[0],centerRot[1],centerRot[2]);
    var screenRad=rad*R*centerPr[2]*0.85;

    // Filled glow zone
    var zGrad=ctx.createRadialGradient(centerPr[0],centerPr[1],0,centerPr[0],centerPr[1],screenRad);
    var r=parseInt(color.slice(1,3),16),g=parseInt(color.slice(3,5),16),b=parseInt(color.slice(5,7),16);
    zGrad.addColorStop(0,'rgba('+r+','+g+','+b+',0.25)');
    zGrad.addColorStop(0.5,'rgba('+r+','+g+','+b+',0.12)');
    zGrad.addColorStop(1,'rgba('+r+','+g+','+b+',0)');
    ctx.fillStyle=zGrad;
    ctx.beginPath();ctx.arc(centerPr[0],centerPr[1],screenRad,0,Math.PI*2);ctx.fill();

    // Border ring with animation
    var pulseR=screenRad*(1+0.08*Math.sin(t*0.05+ci));
    ctx.beginPath();ctx.arc(centerPr[0],centerPr[1],pulseR,0,Math.PI*2);
    ctx.strokeStyle='rgba('+r+','+g+','+b+',0.7)';ctx.lineWidth=1.2;ctx.stroke();

    // Inner dot
    ctx.beginPath();ctx.arc(centerPr[0],centerPr[1],3*centerPr[2],0,Math.PI*2);
    ctx.fillStyle='rgba('+r+','+g+','+b+',0.9)';ctx.fill();
    ctx.shadowColor=color;ctx.shadowBlur=8;ctx.fill();ctx.shadowBlur=0;
  }});

  ctx.restore();

  // ── GLOBE BORDER ──
  ctx.save();
  var borderGrad=ctx.createLinearGradient(cx-R,cy-R,cx+R,cy+R);
  borderGrad.addColorStop(0,'rgba(0,255,180,0.5)');
  borderGrad.addColorStop(0.5,'rgba(160,255,0,0.3)');
  borderGrad.addColorStop(1,'rgba(0,229,255,0.4)');
  ctx.strokeStyle=borderGrad;ctx.lineWidth=1.5;
  ctx.beginPath();ctx.arc(cx,cy,R,0,Math.PI*2);ctx.stroke();

  // ── EQUATORIAL HOLOGRAPHIC RING ──
  ctx.save();ctx.translate(cx,cy);ctx.scale(1,0.22);
  ctx.strokeStyle='rgba(0,255,180,0.12)';ctx.lineWidth=1.5;
  ctx.beginPath();ctx.ellipse(0,0,R*1.06,R*1.06,0,0,Math.PI*2);ctx.stroke();
  ctx.strokeStyle='rgba(0,229,255,0.06)';ctx.lineWidth=8;
  ctx.beginPath();ctx.ellipse(0,0,R*1.12,R*1.12,0,0,Math.PI*2);ctx.stroke();
  ctx.restore();ctx.restore();

  // ── TARGET LOCATION ──
  var tP3=latLonTo3D({lat},{lon},R*1.01);
  var tRot=rotate(tP3[0],tP3[1],tP3[2],rotY+t*rotSpeed,rotX);
  if(isVisible(tRot[2])) {{
    var tPr=project(tRot[0],tRot[1],tRot[2]);
    // Pulsing rings
    for(var ri=1;ri<=4;ri++) {{
      var pulse=0.5+0.5*Math.sin(t*0.07-ri*0.6);
      var rr=(ri*10+pulse*5)*tPr[2];
      ctx.beginPath();ctx.arc(tPr[0],tPr[1],rr,0,Math.PI*2);
      ctx.strokeStyle='rgba(0,255,180,'+(0.5-ri*0.1)+')';
      ctx.lineWidth=1+pulse*0.5;ctx.stroke();
    }}
    // Cross hairs
    var ch=20*tPr[2];
    ctx.strokeStyle='rgba(0,255,180,0.8)';ctx.lineWidth=1;
    ctx.beginPath();ctx.moveTo(tPr[0]-ch,tPr[1]);ctx.lineTo(tPr[0]+ch,tPr[1]);ctx.stroke();
    ctx.beginPath();ctx.moveTo(tPr[0],tPr[1]-ch);ctx.lineTo(tPr[0],tPr[1]+ch);ctx.stroke();
    // Center glow
    var cg=ctx.createRadialGradient(tPr[0],tPr[1],0,tPr[0],tPr[1],12*tPr[2]);
    cg.addColorStop(0,'rgba(255,255,255,1)');
    cg.addColorStop(0.3,'rgba(0,255,180,0.9)');
    cg.addColorStop(0.7,'rgba(160,255,0,0.4)');
    cg.addColorStop(1,'transparent');
    ctx.fillStyle=cg;
    ctx.beginPath();ctx.arc(tPr[0],tPr[1],10*tPr[2],0,Math.PI*2);ctx.fill();
  }}

  // ── AXIS ──
  ctx.strokeStyle='rgba(0,255,180,0.1)';ctx.lineWidth=0.5;ctx.setLineDash([5,5]);
  ctx.beginPath();ctx.moveTo(cx,cy-R*1.18);ctx.lineTo(cx,cy+R*1.18);ctx.stroke();
  ctx.setLineDash([]);

  t++;
  requestAnimationFrame(drawFrame);
}}
drawFrame();
</script>
</body>
</html>"""

    components.html(globe_html, height=550, scrolling=False)

    st.markdown("""<div class="av-section" style="margin-top:1.5rem">
      <div class="av-section-badge">ZONE ANALYSIS</div>
      <div class="av-section-line"></div>
    </div>""", unsafe_allow_html=True)
    zc = st.columns(4)
    for col, lbl, val, color in [
        (zc[0],"OPTIMAL ZONES","38%","#00ffb4"),
        (zc[1],"GOOD ZONES","27%","#a0ff00"),
        (zc[2],"MODERATE ZONES","21%","#f0c040"),
        (zc[3],"STRESSED/CRITICAL","14%","#ff4060"),
    ]:
        with col:
            st.markdown(f"""
<div class="holo hp"><div class="ct ct-l"></div><div class="ct ct-r"></div>
  <div class="hp-lbl">{lbl}</div>
  <div style="font-family:'Orbitron',sans-serif;font-size:2.1rem;font-weight:800;
    color:{color};text-shadow:0 0 15px {color}80">{val}</div>
  <div class="hp-sub">OF MAPPED AREA</div>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# TAB 1 — ENVIRONMENT
# ══════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("""<div class="av-section">
      <div class="av-section-badge">LIVE ATMOSPHERIC CONDITIONS</div>
      <div class="av-section-line"></div>
    </div>""", unsafe_allow_html=True)
    wx = st.columns(6)
    for col,lbl,val,unit in [
        (wx[0],"TEMPERATURE",f"{cur['temperature_2m']:.1f}","°C"),
        (wx[1],"HUMIDITY",f"{cur['relative_humidity_2m']}","%"),
        (wx[2],"WIND SPEED",f"{cur['wind_speed_10m']:.1f}","KM/H"),
        (wx[3],"PRECIPITATION",f"{cur['precipitation']:.1f}","MM"),
        (wx[4],"UV INDEX",f"{cur.get('uv_index',0) or 0:.0f}",""),
        (wx[5],"FEELS LIKE",f"{cur['apparent_temperature']:.1f}","°C"),
    ]:
        with col:
            st.markdown(f"""
<div class="holo hp"><div class="ct ct-l"></div><div class="ct ct-r"></div>
  <div class="hp-lbl">{lbl}</div>
  <div><span class="hp-val">{val}</span><span class="hp-unit">{unit}</span></div>
</div>""", unsafe_allow_html=True)

    c3 = st.columns(3)
    for col,lbl,val,unit,sub in [
        (c3[0],"CLOUD COVER",f"{cur['cloud_cover']}","%",""),
        (c3[1],"SURFACE PRESSURE",f"{cur['surface_pressure']:.0f}","HPA",""),
        (c3[2],"CONDITIONS",wdesc(cur['weather_code']),"",""),
    ]:
        with col:
            st.markdown(f"""
<div class="holo hp">
  <div class="hp-lbl">{lbl}</div>
  <div><span class="hp-val" style="font-size:{'1.2rem' if len(val)>6 else '1.9rem'}">{val}</span><span class="hp-unit">{unit}</span></div>
</div>""", unsafe_allow_html=True)

    st.markdown("""<div class="av-section">
      <div class="av-section-badge">AIR QUALITY MATRIX</div>
      <div class="av-section-line"></div>
    </div>""", unsafe_allow_html=True)

    if aq_cur:
        pm25=float(aq_cur.get("pm2_5",0) or 0); pm10=float(aq_cur.get("pm10",0) or 0)
        no2=float(aq_cur.get("nitrogen_dioxide",0) or 0); so2=float(aq_cur.get("sulphur_dioxide",0) or 0)
        o3=float(aq_cur.get("ozone",0) or 0); co=float(aq_cur.get("carbon_monoxide",0) or 0)
        eu=int(aq_cur.get("european_aqi",0) or 0); us=int(aq_cur.get("us_aqi",0) or 0)
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
            with (aq1 if i<3 else aq2):
                st.markdown(f"""
<div class="pol">
  <div class="pol-hd">
    <span class="pol-nm">{nm}</span>
    <span class="pol-vl" style="color:{bc}">{val:.2f}<span style="font-size:0.6rem;color:#007a5e;margin-left:3px">{unit}</span></span>
  </div>
  <div class="pol-track"><div class="pol-fill" style="width:{pct}%;background:{bc};color:{bc}"></div></div>
</div>""", unsafe_allow_html=True)

        a1,a2=st.columns(2)
        ec=bcol(eu,20,60); psv=ps if ps is not None else 0; psc,psg=grade(psv)
        with a1:
            st.markdown(f"""
<div class="holo hp" style="display:flex;gap:2rem;align-items:center">
  <div><div class="hp-lbl">EUROPEAN AQI</div>
  <div><span class="hp-val" style="color:{ec};text-shadow:0 0 10px {ec}80">{eu}</span></div></div>
  <div style="width:1px;height:44px;background:rgba(0,255,180,0.1)"></div>
  <div><div class="hp-lbl">US AQI</div>
  <div><span class="hp-val" style="color:{bcol(us,50,100)}">{us}</span></div></div>
</div>""", unsafe_allow_html=True)
        with a2:
            st.markdown(f"""
<div class="holo hp" style="display:flex;align-items:center;gap:1rem">
  <div style="flex:1">
    <div class="hp-lbl">POLLUTION SCORE</div>
    <div><span class="hp-val" style="color:{psc};text-shadow:0 0 10px {psc}80">{psv}</span>
    <span class="hp-unit">/ 100</span></div>
    <div class="hp-sub">{psg} · HIGHER = CLEANER AIR</div>
  </div>
  <div style="font-size:2.5rem">{"🟢" if psv>=65 else "🟡" if psv>=40 else "🔴"}</div>
</div>""", unsafe_allow_html=True)
    else:
        st.info("Air quality data unavailable for this location.")

    st.markdown("""<div class="av-section"><div class="av-section-badge">7-DAY FORECAST</div><div class="av-section-line"></div></div>""", unsafe_allow_html=True)
    rows=[]
    for i,day in enumerate(daily["time"]):
        d=datetime.strptime(day,"%Y-%m-%d")
        rows.append({"DATE":d.strftime("%a %d %b").upper(),
            "MAX °C":f"{daily['temperature_2m_max'][i]:.1f}","MIN °C":f"{daily['temperature_2m_min'][i]:.1f}",
            "RAIN MM":f"{daily['precipitation_sum'][i]:.1f}","RAIN %":f"{daily['precipitation_probability_max'][i]}%",
            "WIND":f"{daily['wind_speed_10m_max'][i]:.1f}","UV":f"{daily['uv_index_max'][i]:.0f}"})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════
# TAB 2 — CRISIS INTEL
# ══════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("""<div class="av-section">
      <div class="av-section-badge">PREDICTIVE CRISIS INTELLIGENCE</div>
      <div class="av-section-line"></div>
    </div>""", unsafe_allow_html=True)

    max_rain_day = max((p for p in daily["precipitation_sum"] if p), default=0)
    max_temp = max((t for t in daily["temperature_2m_max"] if t), default=0)

    st.markdown(f"""
<div style="padding:0.8rem 1.2rem;background:rgba(0,255,180,0.03);
  border:1px solid rgba(0,255,180,0.1);border-radius:6px;margin-bottom:1.2rem;
  font-family:'Share Tech Mono',monospace;font-size:0.63rem;color:#00a878">
  ◈ LIVE FORECAST DATA · 7D TOTAL RAIN: {total_rain:.0f}MM · PEAK DAY: {max_rain_day:.0f}MM ·
  MAX TEMP: {max_temp:.1f}°C · RH: {cur['relative_humidity_2m']}% ·
  AQI: {aq_cur.get('european_aqi','N/A')} · WIND MAX: {max((v for v in daily['wind_speed_10m_max'] if v),default=0):.0f}KM/H
</div>""", unsafe_allow_html=True)

    for level,title,msg in detect_crises(weather, aq_cur, lat):
        icon="🚨" if level=="crisis" else "⚠️" if level=="warning" else "✅"
        st.markdown(f"""
<div class="alert a-{level}">
  <div class="alert-icon">{icon}</div>
  <div><div class="alert-title">{title}</div><div class="alert-msg">{msg}</div></div>
</div>""", unsafe_allow_html=True)

    st.markdown("""<div class="av-section"><div class="av-section-badge">AI DEEP RISK ANALYSIS</div><div class="av-section-line"></div></div>""", unsafe_allow_html=True)
    if st.button("▶ RUN AI CRISIS ANALYSIS", type="primary"):
        summary={"location":f"{city_name},{country}","lat":lat,"lon":lon,
            "temp":cur["temperature_2m"],"humidity":cur["relative_humidity_2m"],
            "wind":cur["wind_speed_10m"],"precip_today":cur["precipitation"],
            "conditions":wdesc(cur['weather_code']),"eu_aqi":aq_cur.get("european_aqi"),
            "7d_total_rain_mm":total_rain,"7d_peak_day_mm":max_rain_day,
            "7d_max_temp":max_temp,"7d_daily_rain":daily["precipitation_sum"],
            "month":now.month}
        with st.spinner("ANALYSING..."):
            result=ask_groq(
                f"Agricultural crisis analysis for {city_name}, {country} (lat:{lat:.2f}, month:{now.strftime('%B')}):\n{json.dumps(summary,indent=2)}\n\n"
                "Provide accurate, location-specific analysis:\n1)Current threat assessment based on ACTUAL forecast data\n2)Crop impact\n3)48-hour action plan\n4)30-day outlook",
                system=f"Expert agricultural risk analyst for {country}. Month is {now.strftime('%B')}. If total 7d rainfall is high (>60mm) focus on flood/disease risks. If very low (<5mm) focus on drought. Be accurate to the data provided.")
        st.markdown(f'<div class="ai-out"><div class="ai-out-tag">AI CRISIS REPORT · {city_name.upper()}</div>{result.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# TAB 3 — CROP ENGINE
# ══════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("""<div class="av-section"><div class="av-section-badge">AI CROP RECOMMENDATION ENGINE</div><div class="av-section-line"></div></div>""", unsafe_allow_html=True)
    st.markdown(f"""
<div style="padding:0.8rem 1.2rem;background:rgba(0,255,180,0.03);border:1px solid rgba(0,255,180,0.1);
  border-radius:6px;margin-bottom:1.4rem;font-family:'Share Tech Mono',monospace;font-size:0.63rem;color:#00a878">
  ◈ ANALYSING · {city_name.upper()} · {cur['temperature_2m']:.1f}°C · {cur['relative_humidity_2m']}% RH · AQI {aq_cur.get('european_aqi','N/A')} · {now.strftime('%B')}
</div>""", unsafe_allow_html=True)
    crop_list=recommend_crops(weather)
    for emoji,name,compat,reason,care in crop_list:
        cc,_=grade(compat)
        st.markdown(f"""
<div class="crop-card">
  <div class="ce">{emoji}</div>
  <div class="cb">
    <div class="cn">{name}</div>
    <div class="cr">▸ {reason}</div>
    <div class="cc">◦ {care}</div>
  </div>
  <div>{mini_ring(compat,cc)}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("""<div class="av-section"><div class="av-section-badge">PRECISION MANAGEMENT PLAN</div><div class="av-section-line"></div></div>""", unsafe_allow_html=True)
    opts=[f"{e} {n}" for e,n,*_ in crop_list] if crop_list else ["No crops available"]
    sel=st.selectbox("Select Crop",opts)
    if st.button("▶ GENERATE PLAN", type="primary") and crop_list:
        with st.spinner("BUILDING PLAN..."):
            result=ask_groq(
                f"Precision plan for {sel} in {city_name}, {country} ({now.strftime('%B')}).\n"
                f"Conditions: {cur['temperature_2m']:.1f}°C, {cur['relative_humidity_2m']}% RH, "
                f"UV {cur.get('uv_index',0) or 0:.0f}, Wind {cur['wind_speed_10m']:.1f}km/h, "
                f"AQI {aq_cur.get('european_aqi','N/A')}, 7D rain {total_rain:.0f}mm.\n"
                "Include: sowing timing, irrigation with quantities, NPK plan, pest monitoring, harvest timeline.",
                system=f"Precision agriculture specialist for {country}, {now.strftime('%B')} season.")
        st.markdown(f'<div class="ai-out"><div class="ai-out-tag">MANAGEMENT PLAN · {sel.upper()}</div>{result.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# TAB 4 — SIMULATION
# ══════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("""<div class="av-section"><div class="av-section-badge">FARM DIGITAL TWIN · SCENARIO ENGINE</div><div class="av-section-line"></div></div>""", unsafe_allow_html=True)
    s1,s2=st.columns(2)
    with s1:
        t_d=st.slider("Temperature Δ (°C)",-10,+20,0)
        r_d=st.slider("Rainfall Δ (%)",-100,+200,0)
        h_d=st.slider("Humidity Δ (%)",-40,+40,0)
    with s2:
        aqi_d=st.slider("AQI Δ",-60,+200,0)
        w_d=st.slider("Wind Δ (km/h)",-20,+60,0)
        sim_crop=st.text_input("Target Crop",placeholder="Rice, Wheat, Tomato...")
    sim_t=cur["temperature_2m"]+t_d; base_r=total_rain/7
    sim_r=base_r*(1+r_d/100); sim_aqi=(aq_cur.get("european_aqi") or 30)+aqi_d
    sim_h=min(100,max(0,cur["relative_humidity_2m"]+h_d)); sim_w=max(0,cur["wind_speed_10m"]+w_d)
    sv=st.columns(5)
    for col,lbl,bv,sv_val,unit in [
        (sv[0],"TEMPERATURE",cur["temperature_2m"],sim_t,"°C"),
        (sv[1],"RAIN/DAY",base_r,sim_r,"mm"),
        (sv[2],"HUMIDITY",cur["relative_humidity_2m"],sim_h,"%"),
        (sv[3],"AQI",aq_cur.get("european_aqi",30),sim_aqi,""),
        (sv[4],"WIND",cur["wind_speed_10m"],sim_w,"km/h"),
    ]:
        dlt=sv_val-bv; dc="#00ffb4" if dlt<=0 else "#ff4060"
        with col:
            st.markdown(f"""
<div class="holo hp">
  <div class="hp-lbl">{lbl}</div>
  <div><span class="hp-val" style="font-size:1.5rem">{sv_val:.1f}</span><span class="hp-unit">{unit}</span></div>
  <div class="hp-sub" style="color:{dc}">{'▲' if dlt>0 else '▼'} {abs(dlt):.1f}{unit}</div>
</div>""", unsafe_allow_html=True)
    if st.button("▶ RUN SIMULATION", type="primary"):
        with st.spinner("RUNNING SIMULATION..."):
            result=ask_groq(
                f"Farm simulation for {city_name}, {country} ({now.strftime('%B')}).\n"
                f"BASELINE: {cur['temperature_2m']:.1f}°C, {base_r:.1f}mm/d, RH {cur['relative_humidity_2m']}%, AQI {aq_cur.get('european_aqi','N/A')}\n"
                f"SCENARIO: {sim_t:.1f}°C, {sim_r:.1f}mm/d, RH {sim_h:.0f}%, AQI {sim_aqi:.0f}, Wind {sim_w:.1f}km/h\n"
                f"{'Crop: '+sim_crop if sim_crop else ''}\n"
                "Quantified: 1)Risk delta % 2)Yield impact 3)Resource changes 4)Adaptive strategies 5)Projections",
                system=f"Agricultural simulation expert for {country}. Give specific numbers and probabilities.")
        st.markdown(f'<div class="ai-out"><div class="ai-out-tag">SIMULATION RESULTS</div>{result.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# TAB 5 — CROP SCANNER
# ══════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown("""<div class="av-section"><div class="av-section-badge">AI CROP HEALTH SCANNER</div><div class="av-section-line"></div></div>""", unsafe_allow_html=True)
    sc1,sc2=st.columns([1,1])
    with sc1:
        uploaded=st.file_uploader("UPLOAD CROP IMAGE",type=["jpg","jpeg","png","webp"])
        crop_name_s=st.text_input("Crop Name",placeholder="Tomato, Rice, Wheat...")
        scan_ctx=st.text_area("Describe Symptoms",placeholder="Yellow leaves, spots, wilting...",height=80)
    with sc2:
        if uploaded:
            st.image(uploaded,caption="UPLOADED SAMPLE",use_container_width=True)
        else:
            st.markdown("""
<div style="width:100%;height:200px;background:rgba(0,255,180,0.02);
  border:1px dashed rgba(0,255,180,0.2);border-radius:8px;
  display:flex;align-items:center;justify-content:center;
  font-family:'Share Tech Mono',monospace;font-size:0.62rem;
  color:#006a50;letter-spacing:0.15em;text-align:center">
  ◈ AWAITING SAMPLE UPLOAD<br><br>JPG · PNG · WEBP SUPPORTED
</div>""", unsafe_allow_html=True)
    if st.button("▶ SCAN CROP", type="primary"):
        if uploaded or scan_ctx or crop_name_s:
            with st.spinner("SCANNING..."):
                if uploaded:
                    img_bytes=uploaded.read()
                    img_b64=base64.b64encode(img_bytes).decode()
                    ext=uploaded.name.split('.')[-1].lower()
                    mime="image/jpeg" if ext in ["jpg","jpeg"] else f"image/{ext}"
                    try:
                        resp=get_groq().chat.completions.create(
                            model="llama-3.3-70b-versatile",max_tokens=1000,
                            messages=[{"role":"user","content":[
                                {"type":"text","text":f"Plant pathologist analysis. Crop: {crop_name_s or 'Unknown'}. Symptoms: {scan_ctx or 'See image'}. Location: {city_name}, {country}. {now.strftime('%B')}, {cur['temperature_2m']:.1f}°C, {cur['relative_humidity_2m']}% RH. Provide: 1)Diagnosis 2)Severity 3)Treatment 4)Prevention 5)Recovery timeline."},
                                {"type":"image_url","image_url":{"url":f"data:{mime};base64,{img_b64}"}}
                            ]}])
                        result=resp.choices[0].message.content
                    except:
                        result=ask_groq(f"Plant health: {crop_name_s}, symptoms: {scan_ctx}, {city_name} {now.strftime('%B')}, {cur['temperature_2m']:.1f}°C {cur['relative_humidity_2m']}% RH. Diagnosis, treatment, prevention.")
                else:
                    result=ask_groq(f"Plant health analysis. Crop: {crop_name_s}. Symptoms: {scan_ctx}. {city_name}, {now.strftime('%B')}, {cur['temperature_2m']:.1f}°C, {cur['relative_humidity_2m']}% RH.")
            st.markdown(f'<div class="ai-out"><div class="ai-out-tag">CROP HEALTH REPORT</div>{result.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)
        else:
            st.warning("Upload an image or describe symptoms.")

# ══════════════════════════════════════════════════════════
# TAB 6 — FIELD AI
# ══════════════════════════════════════════════════════════
with tabs[6]:
    st.markdown("""<div class="av-section"><div class="av-section-badge">AEROVEDA FIELD INTELLIGENCE</div><div class="av-section-line"></div></div>""", unsafe_allow_html=True)
    st.markdown(f"""
<div style="padding:0.75rem 1.1rem;background:rgba(0,255,180,0.03);border:1px solid rgba(0,255,180,0.08);
  border-radius:6px;margin-bottom:1rem;font-family:'Share Tech Mono',monospace;font-size:0.62rem;color:#00a878">
  ◈ CONTEXT LOADED · {city_name.upper()}, {country.upper()} · {now.strftime('%B %Y')} ·
  {cur['temperature_2m']:.1f}°C · {cur['relative_humidity_2m']}% RH ·
  AQI {aq_cur.get('european_aqi','N/A')} · 7D RAIN: {total_rain:.0f}MM · ENV {es}/100
</div>""", unsafe_allow_html=True)
    focus=st.text_input("CROP FOCUS",placeholder="Rice, Tomato, Groundnut...")
    if "chat" not in st.session_state:
        st.session_state.chat=[]
    if not st.session_state.chat:
        st.markdown("""<div style="font-family:'Orbitron',sans-serif;font-size:0.52rem;letter-spacing:0.2em;color:#00a878;margin-bottom:0.7rem;font-weight:700">◈ SUGGESTED QUERIES</div>""", unsafe_allow_html=True)
        sqc=st.columns(2)
        for i,q in enumerate(["What diseases should I watch for this month?","How much water does my crop need this week?",
            "Is it safe to spray pesticide today?","Generate my 30-day farming schedule",
            "What is the flood/drought risk for my crops?","Which fertiliser should I apply now?"]):
            with sqc[i%2]:
                st.markdown(f"""<div style="padding:0.6rem 0.9rem;background:rgba(0,255,180,0.03);border:1px solid rgba(0,255,180,0.1);
  border-radius:5px;margin-bottom:0.5rem;font-size:0.72rem;color:#00a878;font-family:'Share Tech Mono',monospace">▸ {q}</div>""", unsafe_allow_html=True)
    for msg in st.session_state.chat:
        if msg["role"]=="user":
            st.markdown(f"""<div class="cu-row"><div class="cbub cu-bub"><div class="cfrom cfrom-u">◈ YOU</div>{msg['content']}</div></div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="ca-row"><div class="cbub ca-bub"><div class="cfrom cfrom-a">◈ AEROVEDA AI</div>{msg['content']}</div></div>""", unsafe_allow_html=True)
    user_in=st.chat_input("Query the Field Intelligence System...")
    if user_in:
        st.session_state.chat.append({"role":"user","content":user_in})
        with st.spinner("PROCESSING..."):
            reply=ask_groq_chat(
                st.session_state.chat,
                system=f"""Aeroveda Field Intelligence — expert agronomist with real-time data.
LOCATION: {city_name}, {region}, {country} | {lat:.4f}°N, {lon:.4f}°E
DATE: {now.strftime('%d %B %Y')} | SEASON: {'Monsoon' if (abs(lat)<25 and now.month in [6,7,8,9,10]) else 'Current season'}
WEATHER: {cur['temperature_2m']:.1f}°C | RH {cur['relative_humidity_2m']}% | Wind {cur['wind_speed_10m']:.1f}km/h | UV {cur.get('uv_index',0) or 0:.0f}
CONDITIONS: {wdesc(cur['weather_code'])} | Precip today: {cur['precipitation']:.1f}mm
AIR: EU AQI {aq_cur.get('european_aqi','N/A')} | PM2.5 {aq_cur.get('pm2_5','N/A')}μg/m³
RAINFALL 7D: {total_rain:.0f}mm | Pollution {ps}/100 | Env {es}/100 | AG {ag}/100
{'CROP: '+focus if focus else ''}
Give precise, location-specific answers. Reference actual numbers. Account for season.""",
                max_tokens=900)
        st.session_state.chat.append({"role":"assistant","content":reply})
        st.rerun()
    if st.session_state.chat:
        if st.button("↺ CLEAR"):
            st.session_state.chat=[]; st.rerun()
