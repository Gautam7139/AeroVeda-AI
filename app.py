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
    page_title="AEROVEDA OS",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── GPS handler ───────────────────────────────────────────────────────────────
params = st.query_params
gps_raw = params.get("gps", "")
if gps_raw and "," in str(gps_raw):
    try:
        parts = str(gps_raw).split(",")
        r = requests.get(
            f"https://nominatim.openstreetmap.org/reverse?lat={parts[0]}&lon={parts[1]}&format=json",
            headers={"User-Agent":"Aeroveda/7.0"}, timeout=8)
        d = r.json()
        detected = (d.get("address",{}).get("city") or
                    d.get("address",{}).get("town") or
                    d.get("address",{}).get("village",""))
        if detected:
            st.session_state["city"] = detected
        st.query_params.clear()
        st.rerun()
    except: pass

# ═══════════════════════════════════════════════════════════════
# CSS — Reference-quality NASA/Sci-Fi Design
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Exo+2:wght@200;300;400;500;600;700&family=Share+Tech+Mono&display=swap');

*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body,[class*="css"]{font-family:'Exo 2',sans-serif;background:#050a0e!important;color:#c8ffe0}

.stApp{
  background:
    radial-gradient(ellipse 80% 50% at 50% -10%, rgba(0,255,140,0.07) 0%,transparent 60%),
    radial-gradient(ellipse 60% 40% at 90% 90%, rgba(0,200,100,0.04) 0%,transparent 50%),
    #050a0e!important;
}
/* Grid */
.stApp::before{
  content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
  background-image:
    linear-gradient(rgba(0,255,140,0.025) 1px,transparent 1px),
    linear-gradient(90deg,rgba(0,255,140,0.025) 1px,transparent 1px);
  background-size:60px 60px;
}
/* Scanlines */
.stApp::after{
  content:'';position:fixed;inset:0;pointer-events:none;z-index:9997;
  background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,0.02) 2px,rgba(0,0,0,0.02) 4px);
}
.main .block-container{padding:0 0 4rem!important;max-width:100%!important;position:relative;z-index:1}

/* ══ TOP NAV BAR ══ */
.topbar{
  display:flex;align-items:center;justify-content:space-between;
  padding:0 2rem;height:56px;
  background:rgba(5,10,14,0.97);
  border-bottom:1px solid rgba(0,255,140,0.12);
  position:relative;
}
.topbar::after{content:'';position:absolute;bottom:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,#00ff8c,#80ff40,#00ff8c,transparent);
  animation:bar-sweep 6s ease-in-out infinite;opacity:0.6}
@keyframes bar-sweep{0%,100%{opacity:0.3}50%{opacity:0.8}}

.nav-logo{
  font-family:'Orbitron',sans-serif;font-size:1.3rem;font-weight:900;
  letter-spacing:0.15em;
  background:linear-gradient(135deg,#00ff8c,#80ff40);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  filter:drop-shadow(0 0 8px rgba(0,255,140,0.4));
}
.nav-links{display:flex;align-items:center;gap:0}
.nav-link{
  font-family:'Orbitron',sans-serif;font-size:0.55rem;font-weight:600;
  letter-spacing:0.15em;color:rgba(0,200,100,0.5);
  padding:0 1.2rem;height:56px;display:flex;align-items:center;
  border-bottom:2px solid transparent;transition:all 0.2s;cursor:pointer;
  text-decoration:none;
}
.nav-link:hover{color:#00ff8c}
.nav-link.active{color:#00ff8c;border-bottom-color:#00ff8c}
.nav-right{display:flex;align-items:center;gap:12px}
.sys-badge{
  display:flex;align-items:center;gap:6px;
  font-family:'Share Tech Mono',monospace;font-size:0.6rem;
  color:#00cc78;
}
.sd{width:6px;height:6px;border-radius:50%;background:#00ff8c;box-shadow:0 0 8px #00ff8c;animation:sd-blink 2s infinite}
@keyframes sd-blink{0%,100%{opacity:1}50%{opacity:0.2}}

/* ══ HERO SECTION ══ */
.hero{
  position:relative;padding:3rem 2.5rem 2rem;
  overflow:hidden;
  background:linear-gradient(180deg,rgba(0,255,140,0.04) 0%,transparent 100%);
  border-bottom:1px solid rgba(0,255,140,0.08);
}
.hero-title{
  font-family:'Orbitron',sans-serif;font-size:3.2rem;font-weight:900;
  color:#fff;letter-spacing:-0.01em;line-height:1.05;
  text-shadow:0 0 40px rgba(0,255,140,0.3);
  max-width:600px;
}
.hero-title .hl{
  background:linear-gradient(135deg,#00ff8c,#80ff40);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}
.hero-sub{
  font-size:0.85rem;color:rgba(0,200,120,0.7);
  margin-top:0.6rem;font-weight:300;letter-spacing:0.05em;
}
.hero-btns{display:flex;gap:12px;margin-top:1.8rem}
.btn-primary{
  display:inline-flex;align-items:center;gap:8px;
  background:linear-gradient(135deg,rgba(0,180,90,0.3),rgba(0,255,140,0.2));
  border:1px solid #00ff8c;border-radius:4px;
  padding:10px 24px;font-family:'Orbitron',sans-serif;
  font-size:0.62rem;font-weight:700;letter-spacing:0.15em;color:#fff;
  cursor:pointer;transition:all 0.2s;
  box-shadow:0 0 20px rgba(0,255,140,0.15);
}
.btn-primary:hover{background:linear-gradient(135deg,rgba(0,180,90,0.5),rgba(0,255,140,0.35));box-shadow:0 0 35px rgba(0,255,140,0.3)}
.btn-secondary{
  display:inline-flex;align-items:center;gap:8px;
  background:transparent;border:1px solid rgba(0,255,140,0.25);
  border-radius:4px;padding:10px 24px;font-family:'Orbitron',sans-serif;
  font-size:0.62rem;font-weight:600;letter-spacing:0.15em;color:rgba(0,200,120,0.7);cursor:pointer;
}

/* Score top-right */
.hero-scores{
  position:absolute;top:2.5rem;right:2.5rem;
  display:flex;flex-direction:column;gap:8px;align-items:flex-end;
}
.score-line{
  display:flex;align-items:center;gap:10px;
  font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:rgba(0,200,120,0.6);
}
.score-line .sv{
  font-family:'Orbitron',sans-serif;font-size:1.1rem;font-weight:800;
}
.score-line .sl{font-size:0.55rem;color:rgba(0,180,100,0.5);letter-spacing:0.12em}

/* ══ MAIN GRID ══ */
.mg{display:grid;grid-template-columns:1fr 1fr 1fr;gap:1px;background:rgba(0,255,140,0.06);padding:0 0 0 0}
.mg2{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:1px;background:rgba(0,255,140,0.06)}

/* ══ GLASS CARDS ══ */
.gc{
  background:linear-gradient(135deg,rgba(0,18,26,0.95),rgba(0,10,16,0.98));
  padding:1.4rem 1.6rem;position:relative;overflow:hidden;
  transition:background 0.3s;
}
.gc::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(0,255,140,0.3),rgba(128,255,64,0.2),transparent)}
.gc:hover{background:linear-gradient(135deg,rgba(0,22,32,0.97),rgba(0,12,20,0.99))}
.gc-title{
  font-family:'Orbitron',sans-serif;font-size:0.58rem;font-weight:700;
  letter-spacing:0.2em;color:rgba(0,180,100,0.8);margin-bottom:1rem;
  display:flex;align-items:center;gap:8px;
}
.gc-title::before{content:'';width:8px;height:8px;border-radius:2px;background:linear-gradient(135deg,#00ff8c,#80ff40);box-shadow:0 0 8px rgba(0,255,140,0.5);flex-shrink:0}
.gc-dot{display:flex;align-items:center;gap:6px;font-family:'Share Tech Mono',monospace;font-size:0.58rem;color:rgba(0,200,120,0.5)}
.gc-dot .dot{width:5px;height:5px;border-radius:50%;background:#00ff8c;box-shadow:0 0 6px #00ff8c;animation:sd-blink 2s infinite}

/* ══ DATA VALUES ══ */
.dv{margin-bottom:1rem}
.dv-l{font-family:'Share Tech Mono',monospace;font-size:0.57rem;letter-spacing:0.15em;color:rgba(0,150,80,0.7);margin-bottom:4px;text-transform:uppercase}
.dv-n{font-family:'Orbitron',sans-serif;font-size:2rem;font-weight:700;color:#fff;line-height:1;text-shadow:0 0 15px rgba(0,255,140,0.2)}
.dv-u{font-size:0.75rem;color:#00ff8c;margin-left:3px;font-weight:300}
.dv-s{font-size:0.65rem;color:rgba(0,120,60,0.7);margin-top:4px;font-family:'Share Tech Mono',monospace}

/* ══ BIG SCORE DISPLAY ══ */
.big-score{text-align:center;padding:1rem 0}
.bs-num{font-family:'Orbitron',sans-serif;font-size:3.5rem;font-weight:900;line-height:1}
.bs-lbl{font-size:0.58rem;letter-spacing:0.2em;text-transform:uppercase;margin-top:6px;font-family:'Share Tech Mono',monospace}
.bs-sub{font-size:0.65rem;margin-top:4px;opacity:0.6}

/* ══ PROGRESS BARS ══ */
.pb-row{display:flex;align-items:center;gap:10px;margin-bottom:10px}
.pb-label{font-family:'Share Tech Mono',monospace;font-size:0.58rem;color:rgba(0,160,80,0.8);width:110px;flex-shrink:0;text-transform:uppercase}
.pb-track{flex:1;height:4px;background:rgba(0,255,140,0.08);border-radius:99px;overflow:visible;position:relative}
.pb-fill{height:4px;border-radius:99px;position:relative;transition:width 1s ease}
.pb-fill::after{content:'';position:absolute;right:-2px;top:-3px;width:10px;height:10px;border-radius:50%;background:currentColor;box-shadow:0 0 10px currentColor,0 0 20px currentColor}
.pb-val{font-family:'Orbitron',sans-serif;font-size:0.68rem;font-weight:700;width:38px;text-align:right;flex-shrink:0}

/* ══ CROP ROW ══ */
.cr-row{display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid rgba(0,255,140,0.06)}
.cr-icon{font-size:1.6rem;flex-shrink:0}
.cr-info{flex:1}
.cr-name{font-family:'Orbitron',sans-serif;font-size:0.72rem;font-weight:700;color:#fff;letter-spacing:0.05em}
.cr-bar{display:flex;align-items:center;gap:8px;margin-top:5px}
.cr-track{flex:1;height:3px;background:rgba(0,255,140,0.08);border-radius:99px;overflow:hidden}
.cr-fill{height:3px;border-radius:99px;transition:width 0.8s ease}
.cr-pct{font-family:'Orbitron',sans-serif;font-size:0.62rem;font-weight:800;flex-shrink:0}
.cr-tag{font-size:0.55rem;letter-spacing:0.1em;color:rgba(0,160,80,0.6);margin-top:2px;font-family:'Share Tech Mono',monospace}

/* ══ ALERTS ══ */
.av-alert{display:flex;gap:12px;padding:0.9rem 1.1rem;border-radius:6px;margin-bottom:0.6rem;position:relative;overflow:hidden}
.av-alert::before{content:'';position:absolute;left:0;top:0;bottom:0;width:3px;border-radius:3px 0 0 3px}
.a-crisis{background:rgba(255,30,60,0.06);border:1px solid rgba(255,30,60,0.18)}
.a-crisis::before{background:linear-gradient(180deg,#ff1e3c,#cc0022)}
.a-warning{background:rgba(255,190,0,0.06);border:1px solid rgba(255,190,0,0.18)}
.a-warning::before{background:linear-gradient(180deg,#ffbe00,#cc9000)}
.a-safe{background:rgba(0,255,140,0.05);border:1px solid rgba(0,255,140,0.15)}
.a-safe::before{background:linear-gradient(180deg,#00ff8c,#00cc70)}
.a-icon{font-size:1.1rem;flex-shrink:0;padding-top:1px}
.a-title{font-family:'Orbitron',sans-serif;font-size:0.58rem;font-weight:700;letter-spacing:0.14em;margin-bottom:4px}
.a-crisis .a-title{color:#ff6080}.a-warning .a-title{color:#ffcc44}.a-safe .a-title{color:#00ff8c}
.a-msg{font-size:0.8rem;line-height:1.6}
.a-crisis .a-msg{color:#ffaaaa}.a-warning .a-msg{color:#ffe088}.a-safe .a-msg{color:#9effc8}

/* ══ AI OUTPUT ══ */
.ai-out{background:rgba(0,6,10,0.98);border:1px solid rgba(0,255,140,0.12);border-radius:8px;
  padding:1.6rem;margin-top:1rem;color:#b8ffdc;line-height:1.9;font-size:0.86rem;position:relative}
.ai-tag{position:absolute;top:-10px;left:16px;background:#050a0e;padding:0 10px;
  font-family:'Orbitron',sans-serif;font-size:0.48rem;letter-spacing:0.2em;font-weight:700;
  background:linear-gradient(135deg,#00ff8c,#80ff40);-webkit-background-clip:text;
  -webkit-text-fill-color:transparent;background-clip:text}

/* ══ CHAT ══ */
.cu-row{display:flex;justify-content:flex-end;margin-bottom:0.6rem}
.ca-row{display:flex;justify-content:flex-start;margin-bottom:0.6rem}
.cbub{padding:0.85rem 1.1rem;border-radius:8px;font-size:0.83rem;line-height:1.7;max-width:82%}
.cu-bub{background:rgba(0,255,140,0.07);border:1px solid rgba(0,255,140,0.18);color:#d0ffe8;border-radius:8px 8px 2px 8px}
.ca-bub{background:rgba(0,10,18,0.97);border:1px solid rgba(0,255,140,0.1);color:#b2ffd4;border-radius:8px 8px 8px 2px}
.cfrom{font-family:'Share Tech Mono',monospace;font-size:0.53rem;letter-spacing:0.18em;margin-bottom:5px;text-transform:uppercase}
.cfrom-u{text-align:right;color:#00ff8c}.cfrom-a{color:#80ff40}

/* ══ SECTION CONTAINER ══ */
.sec-wrap{padding:1.5rem 2rem}

/* ══ TABS ══ */
.stTabs [data-baseweb="tab-list"]{
  background:rgba(5,10,14,0.98)!important;
  border-bottom:1px solid rgba(0,255,140,0.1)!important;
  gap:0!important;padding:0 2rem!important;
}
.stTabs [data-baseweb="tab"]{
  font-family:'Orbitron',sans-serif!important;font-size:0.55rem!important;
  letter-spacing:0.14em!important;text-transform:uppercase!important;
  color:rgba(0,160,80,0.45)!important;padding:1rem 1.4rem!important;
  background:transparent!important;border:none!important;font-weight:600!important;
}
.stTabs [aria-selected="true"]{
  color:#00ff8c!important;border-bottom:2px solid #00ff8c!important;
  background:rgba(0,255,140,0.03)!important;
  text-shadow:0 0 10px rgba(0,255,140,0.5)!important;
}
.stTabs [data-baseweb="tab-panel"]{padding:0!important;background:transparent!important}

/* ══ INPUTS ══ */
.stTextInput input{
  background:rgba(0,12,20,0.9)!important;border:1px solid rgba(0,255,140,0.18)!important;
  border-radius:6px!important;color:#d0ffe8!important;
  font-family:'Exo 2',sans-serif!important;font-size:0.95rem!important;
}
.stTextInput input:focus{border-color:rgba(0,255,140,0.5)!important;box-shadow:0 0 0 2px rgba(0,255,140,0.07)!important}
.stTextInput label{color:#00a060!important;font-family:'Share Tech Mono',monospace!important;font-size:0.57rem!important;letter-spacing:0.18em!important}
.stTextArea textarea{background:rgba(0,12,20,0.9)!important;border:1px solid rgba(0,255,140,0.18)!important;border-radius:6px!important;color:#d0ffe8!important}

/* ══ BUTTONS ══ */
.stButton button{
  background:rgba(0,255,140,0.06)!important;border:1px solid rgba(0,255,140,0.25)!important;
  color:#00ff8c!important;border-radius:4px!important;font-family:'Orbitron',sans-serif!important;
  font-size:0.55rem!important;letter-spacing:0.14em!important;font-weight:700!important;
}
.stButton button:hover{background:rgba(0,255,140,0.14)!important;border-color:#00ff8c!important;color:#fff!important;box-shadow:0 0 20px rgba(0,255,140,0.2)!important}
button[kind="primary"]{background:linear-gradient(135deg,rgba(0,100,60,0.6),rgba(0,200,100,0.4))!important;border:1px solid #00ff8c!important;color:#fff!important}

/* ══ SELECT ══ */
[data-baseweb="select"]>div{background:rgba(0,12,20,0.9)!important;border-color:rgba(0,255,140,0.18)!important;color:#d0ffe8!important;border-radius:6px!important}

/* ══ SLIDER ══ */
.stSlider [data-testid="stThumbValue"]{color:#00ff8c!important;font-family:'Share Tech Mono',monospace!important}

/* ══ DATAFRAME ══ */
[data-testid="stDataFrameResizable"]{border:1px solid rgba(0,255,140,0.08)!important;border-radius:6px!important}

/* ══ FILE UPLOADER ══ */
[data-testid="stFileUploader"]{background:rgba(0,12,20,0.8)!important;border:1px dashed rgba(0,255,140,0.2)!important;border-radius:8px!important}

/* ══ SIDEBAR ══ */
[data-testid="stSidebar"]{background:rgba(2,6,10,0.99)!important;border-right:1px solid rgba(0,255,140,0.08)!important}

/* ══ MISC ══ */
#MainMenu,footer,header{visibility:hidden}
::-webkit-scrollbar{width:3px}
::-webkit-scrollbar-thumb{background:linear-gradient(180deg,#00ff8c,#80ff40);border-radius:99px}
.stSpinner>div{border-top-color:#00ff8c!important}

/* ══ BOTTOM STATUS BAR ══ */
.status-bar{
  display:flex;align-items:center;justify-content:space-between;
  padding:8px 2rem;background:rgba(5,10,14,0.99);
  border-top:1px solid rgba(0,255,140,0.1);
  font-family:'Share Tech Mono',monospace;font-size:0.58rem;color:rgba(0,160,80,0.6);
  gap:2rem;
}
.sb-item{display:flex;align-items:center;gap:6px;white-space:nowrap}
.sb-val{color:#00ff8c;font-weight:700}

/* Hex grid overlay for map zone */
.hex-overlay{
  position:absolute;inset:0;pointer-events:none;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='70'%3E%3Cpath d='M20 2L38 12v20L20 42 2 32V12z' fill='none' stroke='rgba(0,255,140,0.06)' stroke-width='0.5'/%3E%3Cpath d='M20 42L38 52v20L20 82 2 72V52z' fill='none' stroke='rgba(0,255,140,0.04)' stroke-width='0.5'/%3E%3C/svg%3E");
}

/* ══ MAP ZONE CARD ══ */
.zone-info{padding:0.7rem 0;border-bottom:1px solid rgba(0,255,140,0.07);display:flex;justify-content:space-between;align-items:center}
.zi-key{font-family:'Share Tech Mono',monospace;font-size:0.57rem;color:rgba(0,160,80,0.6);text-transform:uppercase;letter-spacing:0.1em}
.zi-val{font-family:'Orbitron',sans-serif;font-size:0.75rem;font-weight:700;color:#fff}
.zi-val.good{color:#00ff8c}.zi-val.med{color:#80ff40}.zi-val.warn{color:#ffcc44}.zi-val.bad{color:#ff4060}

/* TAG BADGE */
.tag{display:inline-block;padding:2px 8px;border-radius:3px;font-family:'Share Tech Mono',monospace;font-size:0.55rem;letter-spacing:0.1em;font-weight:700}
.tag-green{background:rgba(0,255,140,0.12);border:1px solid rgba(0,255,140,0.3);color:#00ff8c}
.tag-lime{background:rgba(128,255,64,0.1);border:1px solid rgba(128,255,64,0.25);color:#80ff40}
.tag-warn{background:rgba(255,200,0,0.1);border:1px solid rgba(255,200,0,0.25);color:#ffc800}
.tag-red{background:rgba(255,40,60,0.1);border:1px solid rgba(255,40,60,0.25);color:#ff283c}
</style>
""", unsafe_allow_html=True)

# ─── AI ────────────────────────────────────────────────────────────────────────
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

# ─── Data ──────────────────────────────────────────────────────────────────────
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
        r = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json", timeout=10)
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
    if s>=80: return "#00ff8c","OPTIMAL","tag-green"
    elif s>=65: return "#80ff40","GOOD","tag-lime"
    elif s>=45: return "#ffcc44","MODERATE","tag-warn"
    elif s>=25: return "#ff8c42","STRESSED","tag-warn"
    else: return "#ff4060","CRITICAL","tag-red"

def bcol(v,g,b):
    if v<=g: return "#00ff8c"
    elif v<=b: return "#ffcc44"
    else: return "#ff4060"

WMO={0:"Clear Sky",1:"Mainly Clear",2:"Partly Cloudy",3:"Overcast",45:"Fog",
     51:"Light Drizzle",53:"Drizzle",55:"Heavy Drizzle",61:"Slight Rain",
     63:"Moderate Rain",65:"Heavy Rain",71:"Slight Snow",73:"Moderate Snow",
     75:"Heavy Snow",80:"Rain Showers",81:"Moderate Showers",82:"Violent Showers",
     95:"Thunderstorm",96:"Thunderstorm+Hail"}
def wdesc(c): return WMO.get(c,"Unknown")

def detect_crises(w, aq_cur, lat):
    alerts=[]; daily=w["daily"]; cur=w["current"]
    month=datetime.now().month; is_tropical=abs(lat)<25
    is_monsoon=is_tropical and month in [6,7,8,9,10]
    precip_list=[p for p in daily["precipitation_sum"] if p is not None]
    total_7d=sum(precip_list); max_day=max(precip_list) if precip_list else 0
    max_temps=[t for t in daily["temperature_2m_max"] if t]
    min_temps=[t for t in daily["temperature_2m_min"] if t]
    max_wind=max((v for v in daily["wind_speed_10m_max"] if v),default=0)
    hum=cur.get("relative_humidity_2m",0)
    if aq_cur:
        aqi=aq_cur.get("european_aqi") or aq_cur.get("us_aqi")
        if aqi and aqi>100: alerts.append(("crisis","AIR QUALITY HAZARD",f"AQI {aqi} — Extremely hazardous. Halt outdoor operations immediately."))
        elif aqi and aqi>80: alerts.append(("crisis","SEVERE POLLUTION",f"AQI {aqi} — Severe pollution. Sensitive crops under critical stress."))
        elif aqi and aqi>50: alerts.append(("warning","POOR AIR QUALITY",f"AQI {aqi} — Elevated pollution reducing photosynthesis efficiency."))
    if max_day>80 or total_7d>200:
        alerts.append(("crisis","FLASH FLOOD RISK — EXTREME",f"Extreme rainfall: {max_day:.0f}mm peak day, {total_7d:.0f}mm / 7 days. Severe waterlogging imminent. Activate drainage systems."))
    elif max_day>40 or total_7d>120:
        alerts.append(("crisis","FLOOD PROBABILITY HIGH",f"{total_7d:.0f}mm weekly rainfall. Waterlogging risk high. Clear drainage, avoid sowing."))
    elif total_7d>60:
        alerts.append(("warning","HEAVY RAINFALL",f"{total_7d:.0f}mm forecast. Reduce irrigation, monitor drainage."))
    if is_monsoon and hum>85 and total_7d>30:
        alerts.append(("warning","MONSOON DISEASE RISK",f"Active monsoon: {hum}% RH + {total_7d:.0f}mm rain. High fungal pathogen risk. Apply preventive fungicide."))
    if total_7d<2 and cur.get("precipitation",0)<0.5:
        avg_max=sum(max_temps)/len(max_temps) if max_temps else 30
        if avg_max>28: alerts.append(("crisis","DROUGHT CONDITIONS",f"Near-zero rainfall ({total_7d:.1f}mm/7d), avg max {avg_max:.1f}°C. Emergency irrigation required."))
        elif avg_max>18: alerts.append(("warning","LOW RAINFALL",f"Only {total_7d:.1f}mm forecast. Monitor soil moisture."))
    ex_heat=sum(1 for t in max_temps if t>42); hi_heat=sum(1 for t in max_temps if t>38)
    if ex_heat>=2: alerts.append(("crisis","EXTREME HEAT WAVE",f"{ex_heat} days >42°C. Critical crop stress. Increase irrigation 40–60%."))
    elif hi_heat>=3: alerts.append(("warning","HEAT STRESS",f"{hi_heat} days >38°C. Adjust irrigation to morning/evening."))
    frost=sum(1 for t in min_temps if t<2)
    if frost>=1: alerts.append(("crisis","FROST WARNING",f"{frost} night(s) sub-2°C. Cover sensitive crops immediately."))
    if max_wind>80: alerts.append(("crisis","STORM FORCE WINDS",f"Gusts up to {max_wind:.0f} km/h. Secure infrastructure."))
    elif max_wind>50: alerts.append(("warning","HIGH WIND",f"Wind speeds up to {max_wind:.0f} km/h."))
    if not alerts: alerts.append(("safe","ALL SYSTEMS NOMINAL",f"No threats detected. {cur['temperature_2m']:.1f}°C, {hum}% RH, {total_7d:.0f}mm/7d. Conditions normal."))
    return alerts

def recommend_crops(w):
    c=w["current"]; t=c["temperature_2m"]; h=c["relative_humidity_2m"]
    pl=[p for p in w["daily"]["precipitation_sum"] if p is not None]
    ar=sum(pl)/len(pl) if pl else 0; result=[]
    if 20<=t<=38 and h>50:
        result.append(("🌾","RICE",95,"Optimal temp-humidity matrix","High water · 3–4 month cycle"))
        result.append(("🌿","SUGARCANE",88,"Heat-humidity match confirmed","Weekly deep irrigation · 10–12 months"))
    if 18<=t<=35:
        result.append(("🥜","GROUNDNUT",85,"Temperature envelope aligned","Sandy loam · dry finish required"))
        result.append(("🌽","MAIZE",82,"Thermophilic conditions met","Moderate water · high N · 90 days"))
    if t>=25 and h<70:
        result.append(("🍅","TOMATO",78,"Warm-dry matrix ideal","Drip irrigation · blight monitoring"))
        result.append(("🌶️","CHILLI",76,"Low humidity = low fungal risk","Potassium-rich feed · drip preferred"))
    if t<22:
        result.append(("🥬","SPINACH",90,"Cool threshold optimal","Direct sow · 6–8 week harvest"))
        result.append(("🥕","CARROT",84,"Root growth favoured by cool soil","Deep loose bed · 70-day cycle"))
        result.append(("🧅","ONION",80,"Cool dry air suits bulb initiation","Reduce water at bulbing stage"))
    if ar<3 and t>20:
        result.append(("🌻","SUNFLOWER",88,"Drought-tolerance matched","Minimal input · 80–95 days"))
        result.append(("🫘","MOONG",83,"Short-season drought legume","Sandy loam · 60–70 days"))
    result.sort(key=lambda x:-x[2]); return result[:5]

def make_ring(score, color, sz=110, sw=8):
    v=score if score is not None else 0
    r=(sz/2)-sw; circ=2*math.pi*r; dash=(v/100)*circ
    gid=f"r{abs(hash(f'{v}{color}'))%99999}"
    return f"""<svg width="{sz}" height="{sz}" viewBox="0 0 {sz} {sz}">
  <defs>
    <filter id="{gid}x"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <linearGradient id="{gid}g" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#00ff8c"/><stop offset="50%" style="stop-color:{color}"/><stop offset="100%" style="stop-color:#80ff40;stop-opacity:0.7"/>
    </linearGradient>
  </defs>
  <circle cx="{sz/2}" cy="{sz/2}" r="{r}" fill="none" stroke="rgba(0,255,140,0.07)" stroke-width="{sw}"/>
  <circle cx="{sz/2}" cy="{sz/2}" r="{r}" fill="none" stroke="url(#{gid}g)" stroke-width="{sw}"
    stroke-linecap="round" stroke-dasharray="{dash:.1f} {circ:.1f}"
    transform="rotate(-90 {sz/2} {sz/2})" filter="url(#{gid}x)"/>
</svg>"""

# ═══════════════════════════════════════════════════════════════
# LOCATION SYSTEM — Prominently placed, always visible
# ═══════════════════════════════════════════════════════════════

# The GPS component — renders the button and captures location
# Then redirects with ?gps=lat,lon
gps_component = components.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Share+Tech+Mono&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
body{background:transparent;font-family:'Orbitron',sans-serif}
#wrapper{
  background:linear-gradient(135deg,rgba(0,18,26,0.97),rgba(0,10,16,0.99));
  border:1px solid rgba(0,255,140,0.15);
  border-top:2px solid #00ff8c;
  padding:14px 20px;
  display:flex;align-items:center;gap:16px;
  position:relative;overflow:hidden;
}
#wrapper::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,#00ff8c,#80ff40,transparent);opacity:0.8}
#title{font-size:9px;letter-spacing:3px;color:rgba(0,200,100,0.7);margin-bottom:5px;text-transform:uppercase}
#city-input{
  flex:1;background:rgba(0,8,14,0.9);border:1px solid rgba(0,255,140,0.2);
  border-radius:5px;padding:9px 14px;
  font-family:'Share Tech Mono',monospace;font-size:13px;color:#d0ffe8;
  outline:none;transition:border-color 0.2s;
}
#city-input:focus{border-color:rgba(0,255,140,0.55);box-shadow:0 0 0 2px rgba(0,255,140,0.08)}
#city-input::placeholder{color:rgba(0,160,80,0.4)}
#gps-btn{
  background:linear-gradient(135deg,rgba(0,160,80,0.2),rgba(0,255,140,0.15));
  border:1px solid rgba(0,255,140,0.4);
  border-radius:5px;padding:9px 18px;
  font-family:'Orbitron',sans-serif;font-size:9px;
  letter-spacing:2px;font-weight:700;color:#00ff8c;
  cursor:pointer;transition:all 0.2s;white-space:nowrap;
  display:flex;align-items:center;gap:8px;
}
#gps-btn:hover{background:rgba(0,255,140,0.25);box-shadow:0 0 20px rgba(0,255,140,0.25);color:#fff;border-color:#00ff8c}
#gps-btn:disabled{opacity:0.5;cursor:not-allowed}
#status{font-family:'Share Tech Mono',monospace;font-size:10px;color:#00a060;margin-top:3px;min-height:14px}
.col{display:flex;flex-direction:column;flex:1}
</style>
<div id="wrapper">
  <div class="col">
    <div id="title">◈ LOCATION ACQUISITION SYSTEM</div>
    <input id="city-input" placeholder="Type city — e.g. Delhi, Mumbai, Bengaluru, Chennai..." 
           value="" autocomplete="off"/>
    <div id="status">Ready — type a city or click GPS to detect your location</div>
  </div>
  <button id="gps-btn" onclick="acquireGPS()">
    <span id="btn-icon">⊕</span>
    <span id="btn-txt">USE MY LOCATION</span>
  </button>
  <button style="background:linear-gradient(135deg,rgba(0,80,40,0.4),rgba(0,160,80,0.3));
    border:1px solid #00ff8c;border-radius:5px;padding:9px 18px;
    font-family:Orbitron,sans-serif;font-size:9px;letter-spacing:2px;
    font-weight:700;color:#fff;cursor:pointer;white-space:nowrap;
    box-shadow:0 0 20px rgba(0,255,140,0.15);"
    onclick="searchCity()">▶ SEARCH</button>
</div>
<script>
// Read current city from URL if stored
var storedCity = sessionStorage.getItem('av_city') || '';
if(storedCity) document.getElementById('city-input').value = storedCity;

document.getElementById('city-input').addEventListener('keydown', function(e) {
  if(e.key === 'Enter') searchCity();
});

function searchCity() {
  var city = document.getElementById('city-input').value.trim();
  if(!city) return;
  sessionStorage.setItem('av_city', city);
  document.getElementById('status').innerText = 'Searching: ' + city + '...';
  document.getElementById('status').style.color = '#00ff8c';
  // Send to Streamlit
  window.parent.postMessage({type:'streamlit:setComponentValue', value: 'city:' + city}, '*');
}

function acquireGPS() {
  var btn = document.getElementById('gps-btn');
  var icon = document.getElementById('btn-icon');
  var txt = document.getElementById('btn-txt');
  var status = document.getElementById('status');
  
  if (!navigator.geolocation) {
    status.innerText = '✗ Geolocation not supported by this browser';
    status.style.color = '#ff4060';
    return;
  }
  
  icon.innerText = '⏳';
  txt.innerText = 'ACQUIRING GPS...';
  btn.disabled = true;
  status.style.color = '#ffcc44';
  status.innerText = 'Requesting GPS permission — please allow location access...';
  
  navigator.geolocation.getCurrentPosition(
    function(pos) {
      var lat = pos.coords.latitude.toFixed(6);
      var lon = pos.coords.longitude.toFixed(6);
      icon.innerText = '✓';
      txt.innerText = 'GPS LOCKED!';
      status.innerText = '✓ Location acquired: ' + lat + '°N, ' + lon + '°E — loading...';
      status.style.color = '#00ff8c';
      
      // Navigate with GPS coordinates
      var base = window.parent.location.href.split('?')[0];
      setTimeout(function() {
        window.parent.location.href = base + '?gps=' + lat + ',' + lon;
      }, 600);
    },
    function(err) {
      btn.disabled = false;
      icon.innerText = '⊕';
      txt.innerText = 'USE MY LOCATION';
      status.style.color = '#ff4060';
      var msgs = {
        1: '✗ Location DENIED — please allow location in your browser settings, then retry',
        2: '✗ Position unavailable — check your device GPS',
        3: '✗ GPS timeout — try again or type your city manually'
      };
      status.innerText = msgs[err.code] || ('✗ Error: ' + err.message);
    },
    { timeout: 15000, enableHighAccuracy: true, maximumAge: 0 }
  );
}
</script>
""", height=110)

# Read city from component value
if gps_component and isinstance(gps_component, str) and gps_component.startswith("city:"):
    new_city = gps_component[5:].strip()
    if new_city:
        st.session_state["city"] = new_city
        st.rerun()

# City from session state
active_city = st.session_state.get("city", "Bengaluru")

# ─── Geocode ──────────────────────────────────────────────────────────────────
geo = geocode(active_city)
if not geo:
    st.error(f"⚠ Location '{active_city}' not found. Please type a valid city name above.")
    st.stop()

lat, lon, country, city_name, region = geo
weather = fetch_weather(lat, lon)
if not weather: st.stop()

aq = fetch_aq(lat, lon)
cur = weather["current"]
daily = weather["daily"]
aq_cur = aq.get("current",{}) if aq else {}
ws = w_score(weather); ps = p_score(aq); es = e_score(ws, ps)
ag = max(0,min(100,round(es*0.7+ws*0.3)))
now = datetime.now()
total_rain = sum(p for p in daily["precipitation_sum"] if p)
crisis_list = detect_crises(weather, aq_cur, lat)
has_crisis = any(c[0]=="crisis" for c in crisis_list)
has_warning = any(c[0]=="warning" for c in crisis_list)

# ═══════════════════════════════════════════════════════════════
# TOP NAV BAR
# ═══════════════════════════════════════════════════════════════
es_color, es_grade, _ = grade(es)
st.markdown(f"""
<div class="topbar">
  <div class="nav-logo">AEROVEDA</div>
  <div class="nav-links">
    <span class="nav-link active">OVERVIEW</span>
    <span class="nav-link">ENVIRONMENT</span>
    <span class="nav-link">AGRICULTURE</span>
    <span class="nav-link">PREDICTIONS</span>
    <span class="nav-link">ANALYTICS</span>
    <span class="nav-link">AI CORE</span>
  </div>
  <div class="nav-right">
    <div class="sys-badge"><div class="sd"></div>SYSTEM LIVE</div>
    <div class="sys-badge" style="color:rgba(0,180,90,0.4)">
      {city_name.upper()}, {country.upper()}
    </div>
    <div style="background:rgba(0,255,140,0.08);border:1px solid rgba(0,255,140,0.25);
      border-radius:3px;padding:5px 14px;font-family:Orbitron,sans-serif;
      font-size:0.55rem;font-weight:700;letter-spacing:0.1em;color:#00ff8c;cursor:pointer">
      SIGN IN
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# HERO SECTION
# ═══════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hero">
  <div style="max-width:620px">
    <div class="hero-title">INTELLIGENCE<br><span class="hl">BEYOND PLANET</span></div>
    <div class="hero-sub">Real-time planetary agricultural intelligence for a sustainable future. {city_name}, {country}.</div>
    <div class="hero-btns">
      <div class="btn-primary">▶ LAUNCH SYSTEM</div>
      <div class="btn-secondary">EXPLORE FEATURES →</div>
    </div>
  </div>
  <div class="hero-scores">
    <div class="score-line">
      <div class="sl">SYSTEM STATUS</div>
      <div class="sv" style="color:#00ff8c;font-size:0.8rem">{'⚠ ALERTS' if has_crisis else 'OPTIMAL'}</div>
    </div>
    <div class="score-line">
      <div class="sl">ENV SCORE</div>
      <div class="sv" style="color:{es_color}">{es}.0 <span style="font-size:0.55rem;color:rgba(0,200,100,0.5)">/100</span></div>
    </div>
    <div class="score-line">
      <div class="sl">AG POTENTIAL</div>
      <div class="sv" style="color:#80ff40">{ag}%</div>
    </div>
    <div class="score-line">
      <div class="sl">ACTIVE NODES</div>
      <div class="sv" style="color:#00ff8c">4</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# TICKER
pm25v = float(aq_cur.get("pm2_5",0) or 0)
ticker_items = [
    f"TEMP: {cur['temperature_2m']:.1f}°C",
    f"RH: {cur['relative_humidity_2m']}%",
    f"WIND: {cur['wind_speed_10m']:.1f}km/h",
    f"UV: {cur.get('uv_index',0) or 0:.0f}",
    f"PM2.5: {pm25v:.1f}μg/m³",
    f"AQI: {aq_cur.get('european_aqi','N/A')}",
    f"7D RAIN: {total_rain:.0f}mm",
    f"CONDITIONS: {wdesc(cur['weather_code']).upper()}",
    f"ENV: {es}/100",
    f"AG: {ag}/100",
    f"LOCATION: {city_name.upper()}, {country.upper()}",
    f"DATA STREAM: ACTIVE",
    f"SECURITY: ENCRYPTED",
    f"{now.strftime('%d %b %Y  %H:%M')} UTC",
]
sep='<span class="tsep">//</span>'
ts=' '.join([f'{x}{sep}' for x in ticker_items])
st.markdown(f"""
<div class="status-bar" style="border-top:none;border-bottom:1px solid rgba(0,255,140,0.08)">
  <div style="overflow:hidden;white-space:nowrap;flex:1;position:relative">
    <div class="ticker-inner">{ts}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{ts}</div>
  </div>
</div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════
tabs = st.tabs(["🌍 OVERVIEW","◈ ENVIRONMENT","⚠ CRISIS INTEL","🌱 CROP ENGINE","🔬 SIMULATION","🔍 CROP SCANNER","◈ FIELD AI"])

# ══════════════════════════════════════════════════
# TAB 0 — OVERVIEW (like reference image)
# ══════════════════════════════════════════════════
with tabs[0]:
    # Row 1: 3 panels
    st.markdown('<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1px;background:rgba(0,255,140,0.06);margin-top:0">', unsafe_allow_html=True)

    # Panel 1: Planetary Overview (Globe)
    overview_globe = f"""<!DOCTYPE html><html><head><meta charset="utf-8"/>
<style>*{{margin:0;padding:0;box-sizing:border-box}}body{{background:rgba(0,10,18,0.97);overflow:hidden}}canvas{{display:block}}</style>
</head><body>
<canvas id="c" width="420" height="260"></canvas>
<script>
var canvas=document.getElementById('c'),ctx=canvas.getContext('2d');
var W=420,H=260,cx=W/2,cy=H/2,R=Math.min(W,H)*0.42,t=0;
var tlat={lat}*Math.PI/180,tlon={lon}*Math.PI/180;
var rotY=Math.PI-tlon,rotX=-tlat*0.5,speed=0.005;
var stars=[];for(var i=0;i<180;i++)stars.push([Math.random()*W,Math.random()*H,Math.random()*1.5]);
var continents=[
  [[8,77],[8,80],[13,80],[20,87],[22,88],[26,90],[28,97],[35,77],[36,75],[37,72],[25,63],[22,68],[20,73],[15,74],[10,77],[8,77]],
  [[22,100],[22,108],[18,109],[12,109],[10,99],[15,98],[22,100]],
  [[22,108],[38,122],[42,130],[55,140],[55,130],[45,120],[40,118],[35,120],[22,108]],
  [[37,10],[37,37],[11,44],[-5,40],[-35,20],[-35,-17],[4,8],[15,12],[37,10]],
  [[36,-9],[48,40],[60,30],[71,28],[55,21],[53,14],[48,8],[36,-9]],
  [[15,-92],[25,-80],[45,-65],[70,-55],[72,-140],[20,-110],[15,-92]],
  [[-5,-80],[-5,-35],[-35,-55],[-55,-70],[-20,-70],[0,-78],[-5,-80]],
  [[-15,130],[-15,138],[-25,153],[-38,148],[-38,115],[-22,114],[-15,130]],
];
function ll3d(la,lo,r){{var p=la*Math.PI/180,l=lo*Math.PI/180;return[r*Math.cos(p)*Math.cos(l),r*Math.sin(p),r*Math.cos(p)*Math.sin(l)]}}
function rot(x,y,z,ry,rx){{var x1=x*Math.cos(ry)-z*Math.sin(ry),z1=x*Math.sin(ry)+z*Math.cos(ry),y2=y*Math.cos(rx)-z1*Math.sin(rx),z2=y*Math.sin(rx)+z1*Math.cos(rx);return[x1,y2,z2]}}
function proj(x,y,z){{var f=500,s=f/(f+z+R*0.3);return[cx+x*s,cy-y*s,s]}}
function draw(){{
  ctx.clearRect(0,0,W,H);
  // BG
  var bg=ctx.createRadialGradient(cx,cy,0,cx,cy,W*0.7);
  bg.addColorStop(0,'rgba(0,25,40,0.98)');bg.addColorStop(1,'rgba(0,5,12,1)');
  ctx.fillStyle=bg;ctx.fillRect(0,0,W,H);
  // Stars
  stars.forEach(function(s){{ctx.fillStyle='rgba(0,255,140,'+(0.1+s[2]/3)+')';ctx.beginPath();ctx.arc(s[0],s[1],s[2]*0.4,0,Math.PI*2);ctx.fill()}});
  // Glow
  var gl=ctx.createRadialGradient(cx,cy,R*0.8,cx,cy,R*1.3);
  gl.addColorStop(0,'rgba(0,255,140,0.06)');gl.addColorStop(0.5,'rgba(128,255,64,0.03)');gl.addColorStop(1,'transparent');
  ctx.fillStyle=gl;ctx.beginPath();ctx.arc(cx,cy,R*1.3,0,Math.PI*2);ctx.fill();
  // Atm
  var at=ctx.createRadialGradient(cx-R*0.2,cy-R*0.2,R*0.6,cx,cy,R*1.06);
  at.addColorStop(0,'rgba(0,200,140,0.1)');at.addColorStop(0.6,'rgba(0,255,140,0.04)');at.addColorStop(1,'transparent');
  ctx.fillStyle=at;ctx.beginPath();ctx.arc(cx,cy,R*1.06,0,Math.PI*2);ctx.fill();
  // Globe
  ctx.save();ctx.beginPath();ctx.arc(cx,cy,R,0,Math.PI*2);ctx.clip();
  var gg=ctx.createRadialGradient(cx-R*0.3,cy-R*0.25,0,cx,cy,R);
  gg.addColorStop(0,'rgba(0,50,70,0.98)');gg.addColorStop(0.4,'rgba(0,28,45,0.99)');gg.addColorStop(1,'rgba(0,6,14,1)');
  ctx.fillStyle=gg;ctx.fillRect(cx-R,cy-R,R*2,R*2);
  var cr=rotY+t*speed;
  // Grid
  for(var la=-80;la<=80;la+=20){{ctx.beginPath();var fi=true;for(var lo=-180;lo<=180;lo+=4){{var p=ll3d(la,lo,R),r2=rot(p[0],p[1],p[2],cr,rotX);if(r2[2]<-R*0.1){{fi=true;continue}}var pr=proj(r2[0],r2[1],r2[2]);if(fi){{ctx.moveTo(pr[0],pr[1]);fi=false}}else ctx.lineTo(pr[0],pr[1])}}ctx.strokeStyle=la===0?'rgba(0,255,140,0.1)':'rgba(0,255,140,0.04)';ctx.lineWidth=la===0?0.8:0.35;ctx.stroke()}}
  for(var lo2=-180;lo2<180;lo2+=30){{ctx.beginPath();var fi2=true;for(var la2=-80;la2<=80;la2+=3){{var p2=ll3d(la2,lo2,R),r3=rot(p2[0],p2[1],p2[2],cr,rotX);if(r3[2]<-R*0.1){{fi2=true;continue}}var pr2=proj(r3[0],r3[1],r3[2]);if(fi2){{ctx.moveTo(pr2[0],pr2[1]);fi2=false}}else ctx.lineTo(pr2[0],pr2[1])}}ctx.strokeStyle='rgba(0,255,140,0.035)';ctx.lineWidth=0.3;ctx.stroke()}}
  // Continents
  continents.forEach(function(pts){{ctx.beginPath();var fc=true;pts.forEach(function(p){{var p3=ll3d(p[0],p[1],R*1.001),rr=rot(p3[0],p3[1],p3[2],cr,rotX);if(rr[2]<-R*0.15){{fc=true;return}}var pr=proj(rr[0],rr[1],rr[2]);if(fc){{ctx.moveTo(pr[0],pr[1]);fc=false}}else ctx.lineTo(pr[0],pr[1])}});ctx.closePath();ctx.fillStyle='rgba(0,100,60,0.22)';ctx.fill();ctx.strokeStyle='rgba(0,255,140,0.25)';ctx.lineWidth=0.5;ctx.stroke()}});
  // Zones (coloured circles on globe surface)
  var zones=[[{lat+0.15},{lon-0.1},0],[{lat-0.08},{lon+0.2},1],[{lat+0.2},{lon+0.1},2],[{lat-0.15},{lon-0.12},1],[{lat+0.05},{lon-0.22},3]];
  var zc=['#00ff8c','#80ff40','#ffcc44','#ff8c42','#ff4060'];
  zones.forEach(function(z){{var p3=ll3d(z[0],z[1],R*1.003),rr=rot(p3[0],p3[1],p3[2],cr,rotX);if(rr[2]<-R*0.1)return;var pr=proj(rr[0],rr[1],rr[2]);var col=zc[z[2]];var rads=18*pr[2];var zg=ctx.createRadialGradient(pr[0],pr[1],0,pr[0],pr[1],rads);var rgb=col==='#00ff8c'?'0,255,140':col==='#80ff40'?'128,255,64':col==='#ffcc44'?'255,204,68':col==='#ff8c42'?'255,140,66':'255,64,96';zg.addColorStop(0,'rgba('+rgb+',0.3)');zg.addColorStop(1,'rgba('+rgb+',0)');ctx.fillStyle=zg;ctx.beginPath();ctx.arc(pr[0],pr[1],rads,0,Math.PI*2);ctx.fill();ctx.strokeStyle='rgba('+rgb+',0.7)';ctx.lineWidth=1;ctx.beginPath();ctx.arc(pr[0],pr[1],rads*(1+0.06*Math.sin(t*0.05+z[2])),0,Math.PI*2);ctx.stroke()}});
  ctx.restore();
  // Target
  var tp=ll3d({lat},{lon},R*1.01),tr=rot(tp[0],tp[1],tp[2],cr,rotX);
  if(tr[2]>-R*0.1){{var tpr=proj(tr[0],tr[1],tr[2]);for(var ri=1;ri<=3;ri++){{ctx.beginPath();ctx.arc(tpr[0],tpr[1],(ri*8+2*Math.sin(t*0.07))*tpr[2],0,Math.PI*2);ctx.strokeStyle='rgba(0,255,140,'+(0.55-ri*0.12)+')';ctx.lineWidth=1;ctx.stroke()}}var cg=ctx.createRadialGradient(tpr[0],tpr[1],0,tpr[0],tpr[1],10*tpr[2]);cg.addColorStop(0,'rgba(255,255,255,0.9)');cg.addColorStop(0.3,'rgba(0,255,140,0.8)');cg.addColorStop(1,'transparent');ctx.fillStyle=cg;ctx.beginPath();ctx.arc(tpr[0],tpr[1],8*tpr[2],0,Math.PI*2);ctx.fill()}}
  // Globe border
  var brd=ctx.createLinearGradient(cx-R,cy,cx+R,cy);
  brd.addColorStop(0,'rgba(0,255,140,0.5)');brd.addColorStop(0.5,'rgba(128,255,64,0.3)');brd.addColorStop(1,'rgba(0,255,140,0.4)');
  ctx.strokeStyle=brd;ctx.lineWidth=1.5;ctx.beginPath();ctx.arc(cx,cy,R,0,Math.PI*2);ctx.stroke();
  // Equatorial ring
  ctx.save();ctx.translate(cx,cy);ctx.scale(1,0.2);ctx.strokeStyle='rgba(0,255,140,0.1)';ctx.lineWidth=2;ctx.beginPath();ctx.ellipse(0,0,R*1.05,R*1.05,0,0,Math.PI*2);ctx.stroke();ctx.restore();
  t++;requestAnimationFrame(draw);
}}
draw();
</script></body></html>"""

    # Panel 2: Environmental Matrix
    # Panel 3: Predictive Timeline
    # Use Streamlit columns for the 3-panel layout
    r1c1, r1c2, r1c3 = st.columns(3)

    with r1c1:
        st.markdown("""<div class="gc"><div class="gc-title">PLANETARY OVERVIEW <div class="gc-dot"><div class="dot"></div>LIVE</div></div>""", unsafe_allow_html=True)
        components.html(overview_globe, height=270, scrolling=False)
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px">
          <div><div class="dv-l">TEMPERATURE</div><div style="font-family:Orbitron,sans-serif;font-size:1.3rem;font-weight:700;color:#fff">{cur['temperature_2m']:.1f}<span style="font-size:0.7rem;color:#00ff8c">°C</span></div></div>
          <div><div class="dv-l">HUMIDITY</div><div style="font-family:Orbitron,sans-serif;font-size:1.3rem;font-weight:700;color:#80ff40">{cur['relative_humidity_2m']}<span style="font-size:0.7rem;color:#80ff40">%</span></div></div>
          <div style="margin-top:4px"><div class="dv-l">AIR QUALITY</div><div style="font-family:Orbitron,sans-serif;font-size:1.3rem;font-weight:700;color:{'#00ff8c' if (aq_cur.get('european_aqi') or 100)<50 else '#ffcc44'}">{aq_cur.get('european_aqi','N/A')}</div></div>
          <div style="margin-top:4px"><div class="dv-l">CONDITIONS</div><div style="font-family:Share Tech Mono,monospace;font-size:0.65rem;color:#00ff8c;margin-top:4px">{wdesc(cur['weather_code'])}</div></div>
        </div>
        </div>""", unsafe_allow_html=True)

    with r1c2:
        pm25=float(aq_cur.get("pm2_5",0) or 0); pm10=float(aq_cur.get("pm10",0) or 0)
        no2=float(aq_cur.get("nitrogen_dioxide",0) or 0); o3=float(aq_cur.get("ozone",0) or 0)
        st.markdown(f"""
<div class="gc" style="height:100%">
  <div class="gc-title">ENVIRONMENTAL MATRIX</div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:1rem">
    <div><div class="dv-l">CO₂ PROXY</div><div style="font-family:Orbitron,sans-serif;font-size:1.5rem;font-weight:700;color:#00ff8c">{int(no2*4+380)}</div><div class="dv-s">ppm</div></div>
    <div><div class="dv-l">OXYGEN IDX</div><div style="font-family:Orbitron,sans-serif;font-size:1.5rem;font-weight:700;color:#80ff40">21.{max(0,9-int(pm25/10))}</div><div class="dv-s">%</div></div>
    <div><div class="dv-l">BIODIVERSITY</div><div style="font-family:Orbitron,sans-serif;font-size:1.5rem;font-weight:700;color:{'#00ff8c' if es>60 else '#ffcc44'}">{min(100,es+8)}%</div><div class="dv-s">index</div></div>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px">
    <div><div class="dv-l">WATER QUAL</div><div style="font-family:Orbitron,sans-serif;font-size:1.4rem;font-weight:700;color:#80ff40">{max(60,100-int(pm25*0.8))}%</div></div>
    <div><div class="dv-l">SOIL HEALTH</div><div style="font-family:Orbitron,sans-serif;font-size:1.4rem;font-weight:700;color:{'#00ff8c' if ws>60 else '#ffcc44'}">{min(100,ws+5)}%</div></div>
    <div><div class="dv-l">ENERGY FLOW</div><div style="font-family:Orbitron,sans-serif;font-size:1.4rem;font-weight:700;color:#00ff8c">{min(100,ag+7)}%</div></div>
  </div>
  <div style="margin-top:1rem;padding-top:1rem;border-top:1px solid rgba(0,255,140,0.07)">
    <div class="dv-l" style="margin-bottom:8px">AIR POLLUTANTS</div>
    <div class="pb-row"><span class="pb-label">PM2.5</span><div class="pb-track"><div class="pb-fill" style="width:{min(100,int(pm25/2.5))}%;background:{bcol(pm25,12,35)};color:{bcol(pm25,12,35)}"></div></div><span class="pb-val" style="color:{bcol(pm25,12,35)}">{pm25:.1f}</span></div>
    <div class="pb-row"><span class="pb-label">OZONE O₃</span><div class="pb-track"><div class="pb-fill" style="width:{min(100,int(o3/1.8))}%;background:{bcol(o3,60,120)};color:{bcol(o3,60,120)}"></div></div><span class="pb-val" style="color:{bcol(o3,60,120)}">{o3:.0f}</span></div>
    <div class="pb-row"><span class="pb-label">NO₂</span><div class="pb-track"><div class="pb-fill" style="width:{min(100,int(no2))}%;background:{bcol(no2,40,100)};color:{bcol(no2,40,100)}"></div></div><span class="pb-val" style="color:{bcol(no2,40,100)}">{no2:.0f}</span></div>
  </div>
</div>""", unsafe_allow_html=True)

    with r1c3:
        # Score rings + crops
        crops = recommend_crops(weather)
        top3 = crops[:3] if crops else []
        ec, eg, etag = grade(es)
        st.markdown(f"""
<div class="gc" style="height:100%">
  <div class="gc-title">INTELLIGENCE SCORES</div>
  <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:1rem;margin-bottom:1rem">
    <div style="text-align:center">
      <div style="position:relative;width:100px;height:100px;margin:0 auto">
        {make_ring(es, ec, 100, 7)}
        <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center">
          <div style="font-family:Orbitron,sans-serif;font-size:1.5rem;font-weight:800;color:{ec}">{es}</div>
          <div style="font-size:0.5rem;color:rgba(0,180,80,0.6);font-family:Share Tech Mono,monospace">ENV</div>
        </div>
      </div>
      <div style="font-family:Orbitron,sans-serif;font-size:0.55rem;color:rgba(0,180,80,0.7);margin-top:5px;letter-spacing:0.1em">ENVIRONMENTAL</div>
      <div style="font-family:Orbitron,sans-serif;font-size:0.65rem;font-weight:700;color:{ec}">{eg}</div>
    </div>
    <div style="text-align:center">
      <div style="position:relative;width:100px;height:100px;margin:0 auto">
        {make_ring(ag, '#80ff40', 100, 7)}
        <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center">
          <div style="font-family:Orbitron,sans-serif;font-size:1.5rem;font-weight:800;color:#80ff40">{ag}</div>
          <div style="font-size:0.5rem;color:rgba(0,180,80,0.6);font-family:Share Tech Mono,monospace">HIGH</div>
        </div>
      </div>
      <div style="font-family:Orbitron,sans-serif;font-size:0.55rem;color:rgba(0,180,80,0.7);margin-top:5px;letter-spacing:0.1em">AG POTENTIAL</div>
      <div style="font-family:Orbitron,sans-serif;font-size:0.65rem;font-weight:700;color:#80ff40">{ag}%</div>
    </div>
  </div>
  <div class="gc-title" style="margin-top:0.5rem">RECOMMENDED CROPS</div>""", unsafe_allow_html=True)
        for emoji,name,compat,reason,care in top3:
            cc,_,_ = grade(compat)
            st.markdown(f"""
  <div class="cr-row">
    <div class="cr-icon">{emoji}</div>
    <div class="cr-info">
      <div class="cr-name">{name}</div>
      <div class="cr-bar">
        <div class="cr-track"><div class="cr-fill" style="width:{compat}%;background:{cc}"></div></div>
        <div class="cr-pct" style="color:{cc}">{compat}%</div>
      </div>
      <div class="cr-tag">HIGHLY SUITABLE</div>
    </div>
  </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Row 2: 4 cards
    st.markdown("<div style='height:1px;background:rgba(0,255,140,0.06);margin:0'></div>", unsafe_allow_html=True)
    r2c1, r2c2, r2c3, r2c4 = st.columns(4)

    with r2c1:
        # Zone Map (2D but styled nicely)
        layer_sel = st.selectbox("Layer", ["🌱 Crop Suitability","💧 Water","🌡 Temperature","🌊 Flood Risk","🏜 Drought"], label_visibility="collapsed", key="ov_layer")
        lc2 = {"🌱 Crop Suitability":["#00ff8c","#80ff40","#ffcc44","#ff8c42","#ff4060"],
               "💧 Water":["#00e5ff","#00b8ff","#ffcc44","#ff8c42","#ff4060"],
               "🌡 Temperature":["#ff4060","#ff8c42","#ffcc44","#80ff40","#00ff8c"],
               "🌊 Flood Risk":["#0040ff","#0088ff","#00e5ff","#ffcc44","#00ff8c"],
               "🏜 Drought":["#ff4060","#ff8c42","#ffcc44","#80ff40","#00ff8c"]}.get(layer_sel, ["#00ff8c","#80ff40","#ffcc44","#ff8c42","#ff4060"])

        map_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"/>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>*{{margin:0;padding:0}}body{{background:#020c10}}#m{{width:100%;height:240px}}
.leaflet-container{{background:#020c10!important}}
.leaflet-tile{{filter:brightness(0.25) saturate(0.1) hue-rotate(120deg)!important}}
.leaflet-popup-content-wrapper{{background:rgba(0,12,20,0.97);border:1px solid rgba(0,255,140,0.3);color:#00ff8c;border-radius:4px}}
.leaflet-popup-tip{{background:rgba(0,12,20,0.97)}}</style>
</head><body><div id="m"></div><script>
var map=L.map('m',{{zoomControl:false,attributionControl:false}}).setView([{lat},{lon}],9);
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png').addTo(map);
var zc={json.dumps(lc2)};
var zones=[[{lat+0.12},{lon-0.08},0,0.18],[{lat-0.06},{lon+0.15},1,0.14],[{lat+0.2},{lon+0.1},2,0.12],[{lat-0.15},{lon-0.1},1,0.16],[{lat+0.05},{lon-0.18},3,0.1],[{lat-0.05},{lon+0.25},0,0.13]];
zones.forEach(function(z){{L.circle([z[0],z[1]],{{color:zc[z[2]],fillColor:zc[z[2]],fillOpacity:0.2,weight:1.5,opacity:0.7,radius:z[3]*111000}}).addTo(map)}});
var ci=L.divIcon({{html:'<div style="width:14px;height:14px;border-radius:50%;background:#00ff8c;border:2px solid #fff;box-shadow:0 0 12px #00ff8c,0 0 24px rgba(0,255,140,0.4)"></div>',iconSize:[14,14],iconAnchor:[7,7]}});
L.marker([{lat},{lon}],{{icon:ci}}).addTo(map).bindPopup('<span style="font-family:Orbitron,sans-serif;font-size:10px">◈ {city_name.upper()}</span>');
for(var i=-4;i<=4;i++){{L.polyline([[{lat}+i*0.06,{lon}-0.6],[{lat}+i*0.06,{lon}+0.6]],{{color:'rgba(0,255,140,0.04)',weight:0.5}}).addTo(map);L.polyline([[{lat}-0.35,{lon}+i*0.09],[{lat}+0.35,{lon}+i*0.09]],{{color:'rgba(0,255,140,0.04)',weight:0.5}}).addTo(map)}}
</script></body></html>"""
        st.markdown('<div class="gc"><div class="gc-title">AGRICULTURAL ZONE MAP</div>', unsafe_allow_html=True)
        components.html(map_html, height=250, scrolling=False)
        st.markdown(f"""
<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px">
  <span class="tag tag-green">OPTIMAL 38%</span>
  <span class="tag tag-lime">GOOD 27%</span>
  <span class="tag tag-warn">MODERATE 21%</span>
  <span class="tag tag-red">STRESSED 14%</span>
</div></div>""", unsafe_allow_html=True)

    with r2c2:
        crop_list = recommend_crops(weather)
        st.markdown('<div class="gc" style="height:100%"><div class="gc-title">RECOMMENDED CROPS</div>', unsafe_allow_html=True)
        for emoji,name,compat,reason,care in crop_list:
            cc,_,_ = grade(compat)
            st.markdown(f"""
<div style="display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid rgba(0,255,140,0.06)">
  <div style="font-size:1.4rem">{emoji}</div>
  <div style="flex:1">
    <div style="font-family:Orbitron,sans-serif;font-size:0.7rem;font-weight:700;color:#fff">{name}</div>
    <div style="height:3px;background:rgba(0,255,140,0.08);border-radius:99px;margin-top:5px;overflow:hidden">
      <div style="width:{compat}%;height:3px;background:{cc};border-radius:99px"></div>
    </div>
  </div>
  <div style="font-family:Orbitron,sans-serif;font-size:0.7rem;font-weight:800;color:{cc}">{compat}%</div>
  <div style="font-size:0.52rem;color:rgba(0,160,80,0.6);font-family:Share Tech Mono,monospace;letter-spacing:0.08em">MATCH</div>
</div>""", unsafe_allow_html=True)
        st.markdown('<div style="margin-top:8px"><a style="font-family:Orbitron,sans-serif;font-size:0.52rem;color:rgba(0,200,100,0.5);letter-spacing:0.12em">VIEW ALL CROPS →</a></div></div>', unsafe_allow_html=True)

    with r2c3:
        # AI Core
        st.markdown(f"""
<div class="gc" style="height:100%">
  <div class="gc-title">AI CORE ASSISTANT</div>
  <div style="display:flex;align-items:center;justify-content:center;padding:1.5rem 0">
    <div style="position:relative;width:100px;height:100px">
      <svg width="100" height="100" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="40" fill="none" stroke="rgba(0,255,140,0.08)" stroke-width="2"/>
        <circle cx="50" cy="50" r="30" fill="none" stroke="rgba(0,255,140,0.12)" stroke-width="1.5"/>
        <circle cx="50" cy="50" r="20" fill="rgba(0,255,140,0.06)" stroke="rgba(0,255,140,0.3)" stroke-width="1"/>
        <circle cx="50" cy="50" r="8" fill="#00ff8c" opacity="0.9"/>
        <circle cx="50" cy="50" r="8">
          <animate attributeName="r" values="8;18;8" dur="2s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values="0.9;0;0.9" dur="2s" repeatCount="indefinite"/>
          <animate attributeName="fill" values="#00ff8c;#80ff40;#00ff8c" dur="2s" repeatCount="indefinite"/>
        </circle>
      </svg>
    </div>
  </div>
  <div style="font-family:Share Tech Mono,monospace;font-size:0.7rem;color:rgba(0,200,120,0.6);text-align:center;margin-bottom:1rem">
    How can I assist today?
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px">
    {''.join([f'<div style="background:rgba(0,255,140,0.05);border:1px solid rgba(0,255,140,0.12);border-radius:4px;padding:8px;text-align:center;font-family:Orbitron,sans-serif;font-size:0.5rem;color:rgba(0,200,100,0.6);letter-spacing:0.1em;cursor:pointer">{x}</div>' for x in ['SCAN','ANALYSE','PREDICT','OPTIMISE','SIMULATE','REPORT']])}
  </div>
</div>""", unsafe_allow_html=True)

    with r2c4:
        # Crisis summary
        st.markdown('<div class="gc" style="height:100%"><div class="gc-title">SYSTEM COMMAND</div>', unsafe_allow_html=True)
        for level,title,msg in crisis_list[:3]:
            icon="🚨" if level=="crisis" else "⚠️" if level=="warning" else "✅"
            col = "#ff4060" if level=="crisis" else "#ffcc44" if level=="warning" else "#00ff8c"
            st.markdown(f"""
<div style="padding:8px 10px;background:rgba({','.join(['255,40,60' if level=='crisis' else '255,190,0' if level=='warning' else '0,255,140'].pop().split(','))},0.06);
  border:1px solid rgba({','.join(['255,40,60' if level=='crisis' else '255,190,0' if level=='warning' else '0,255,140'].pop().split(','))},0.18);
  border-radius:5px;margin-bottom:6px">
  <div style="font-family:Orbitron,sans-serif;font-size:0.55rem;font-weight:700;color:{col};letter-spacing:0.12em;margin-bottom:3px">{icon} {title}</div>
  <div style="font-size:0.72rem;color:rgba(200,255,220,0.7);line-height:1.4">{msg[:100]}{"..." if len(msg)>100 else ""}</div>
</div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# TAB 1 — ENVIRONMENT
# ══════════════════════════════════════════════════
with tabs[1]:
    st.markdown('<div class="sec-wrap">', unsafe_allow_html=True)
    wx = st.columns(6)
    for col,lbl,val,unit in [(wx[0],"TEMPERATURE",f"{cur['temperature_2m']:.1f}","°C"),(wx[1],"HUMIDITY",f"{cur['relative_humidity_2m']}","%"),(wx[2],"WIND",f"{cur['wind_speed_10m']:.1f}","km/h"),(wx[3],"PRECIPITATION",f"{cur['precipitation']:.1f}","mm"),(wx[4],"UV INDEX",f"{cur.get('uv_index',0) or 0:.0f}",""),(wx[5],"FEELS LIKE",f"{cur['apparent_temperature']:.1f}","°C")]:
        with col:
            st.markdown(f"""<div class="gc hp" style="padding:1.2rem 1.4rem"><div class="dv-l">{lbl}</div><div class="dv-n">{val}<span class="dv-u">{unit}</span></div></div>""", unsafe_allow_html=True)
    c3=st.columns(3)
    for col,lbl,val,unit in [(c3[0],"CLOUD COVER",f"{cur['cloud_cover']}","%"),(c3[1],"PRESSURE",f"{cur['surface_pressure']:.0f}","hPa"),(c3[2],"CONDITIONS",wdesc(cur['weather_code']),"")]:
        with col:
            st.markdown(f"""<div class="gc" style="padding:1.2rem 1.4rem"><div class="dv-l">{lbl}</div><div class="dv-n" style="font-size:{'1.2rem' if len(val)>6 else '1.9rem'}">{val}<span class="dv-u">{unit}</span></div></div>""", unsafe_allow_html=True)
    if aq_cur:
        pm25=float(aq_cur.get("pm2_5",0) or 0); pm10=float(aq_cur.get("pm10",0) or 0)
        no2=float(aq_cur.get("nitrogen_dioxide",0) or 0); so2=float(aq_cur.get("sulphur_dioxide",0) or 0)
        o3=float(aq_cur.get("ozone",0) or 0); co=float(aq_cur.get("carbon_monoxide",0) or 0)
        eu=int(aq_cur.get("european_aqi",0) or 0); us=int(aq_cur.get("us_aqi",0) or 0)
        st.markdown('<div style="margin-top:1px;background:rgba(0,255,140,0.06);height:1px"></div>', unsafe_allow_html=True)
        aq1,aq2=st.columns(2)
        pols=[("PM₂.₅",pm25,12,35,"μg/m³",min(100,int(pm25/2.5))),("PM₁₀",pm10,20,50,"μg/m³",min(100,int(pm10/1.5))),("NO₂",no2,40,100,"μg/m³",min(100,int(no2))),("SO₂",so2,20,80,"μg/m³",min(100,int(so2))),("O₃",o3,60,120,"μg/m³",min(100,int(o3/1.8))),("CO",co/1000,0.5,2,"mg/m³",min(100,int(co/700)))]
        for i,(nm,val,g,b,unit,pct) in enumerate(pols):
            bc=bcol(val,g,b)
            with (aq1 if i<3 else aq2):
                st.markdown(f"""<div style="padding:0.7rem 1.4rem"><div class="pb-row"><span class="pb-label">{nm}</span><div class="pb-track"><div class="pb-fill" style="width:{pct}%;background:{bc};color:{bc}"></div></div><span class="pb-val" style="color:{bc}">{val:.1f}</span><span style="font-size:0.55rem;color:rgba(0,120,60,0.6);margin-left:3px">{unit}</span></div></div>""", unsafe_allow_html=True)
    st.markdown('<div style="margin-top:1px">', unsafe_allow_html=True)
    rows=[]
    for i,day in enumerate(daily["time"]):
        d=datetime.strptime(day,"%Y-%m-%d")
        rows.append({"DATE":d.strftime("%a %d %b").upper(),"MAX °C":f"{daily['temperature_2m_max'][i]:.1f}","MIN °C":f"{daily['temperature_2m_min'][i]:.1f}","RAIN mm":f"{daily['precipitation_sum'][i]:.1f}","RAIN %":f"{daily['precipitation_probability_max'][i]}%","WIND":f"{daily['wind_speed_10m_max'][i]:.1f}","UV":f"{daily['uv_index_max'][i]:.0f}"})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# TAB 2 — CRISIS
# ══════════════════════════════════════════════════
with tabs[2]:
    st.markdown('<div class="sec-wrap">', unsafe_allow_html=True)
    max_rain_day=max((p for p in daily["precipitation_sum"] if p),default=0)
    max_temp=max((t for t in daily["temperature_2m_max"] if t),default=0)
    st.markdown(f"""<div style="padding:0.7rem 1.1rem;background:rgba(0,255,140,0.03);border:1px solid rgba(0,255,140,0.1);border-radius:6px;margin-bottom:1rem;font-family:Share Tech Mono,monospace;font-size:0.62rem;color:rgba(0,160,80,0.7)">
◈ FORECAST DATA · 7D RAIN: {total_rain:.0f}MM · PEAK: {max_rain_day:.0f}MM/DAY · MAX TEMP: {max_temp:.1f}°C · RH: {cur['relative_humidity_2m']}% · AQI: {aq_cur.get('european_aqi','N/A')}
</div>""", unsafe_allow_html=True)
    for level,title,msg in detect_crises(weather, aq_cur, lat):
        icon="🚨" if level=="crisis" else "⚠️" if level=="warning" else "✅"
        st.markdown(f"""<div class="av-alert a-{level}"><div class="a-icon">{icon}</div><div><div class="a-title">{title}</div><div class="a-msg">{msg}</div></div></div>""", unsafe_allow_html=True)
    if st.button("▶ RUN AI CRISIS ANALYSIS", type="primary"):
        summary={"location":f"{city_name},{country}","lat":lat,"lon":lon,"temp":cur["temperature_2m"],"humidity":cur["relative_humidity_2m"],"eu_aqi":aq_cur.get("european_aqi"),"7d_total_rain":total_rain,"7d_peak_rain":max_rain_day,"7d_max_temp":max_temp,"month":now.month}
        with st.spinner("ANALYSING..."):
            result=ask_groq(f"Agricultural crisis analysis for {city_name},{country} (lat:{lat:.1f}, month:{now.strftime('%B')}):\n{json.dumps(summary,indent=2)}\n\n1)Threats based on ACTUAL data 2)Crop impact 3)48h actions 4)30-day outlook",system=f"Agricultural risk analyst for {country}. {now.strftime('%B')}: high rain = flood/disease focus, low rain = drought focus.")
        st.markdown(f'<div class="ai-out"><div class="ai-tag">AI CRISIS REPORT · {city_name.upper()}</div>{result.replace(chr(10),"<br>")}</div>',unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# TAB 3 — CROPS
# ══════════════════════════════════════════════════
with tabs[3]:
    st.markdown('<div class="sec-wrap">', unsafe_allow_html=True)
    crop_list=recommend_crops(weather)
    for emoji,name,compat,reason,care in crop_list:
        cc,_,_=grade(compat)
        st.markdown(f"""<div style="display:flex;align-items:center;gap:1.2rem;padding:1rem 1.4rem;background:linear-gradient(135deg,rgba(0,18,26,0.9),rgba(0,10,16,0.95));border:1px solid rgba(0,255,140,0.1);border-left:3px solid {cc};border-radius:6px;margin-bottom:0.6rem;transition:all 0.3s">
  <div style="font-size:2.1rem">{emoji}</div>
  <div style="flex:1"><div style="font-family:Orbitron,sans-serif;font-size:0.88rem;font-weight:700;color:#fff">{name}</div>
  <div style="font-size:0.74rem;color:rgba(0,180,90,0.8);margin-top:3px">▸ {reason}</div>
  <div style="font-size:0.64rem;color:rgba(0,120,60,0.6);margin-top:4px;font-family:Share Tech Mono,monospace">◦ {care}</div></div>
  <div style="text-align:center;flex-shrink:0">{make_ring(compat,cc,65,5)}</div>
</div>""", unsafe_allow_html=True)
    opts=[f"{e} {n}" for e,n,*_ in crop_list] if crop_list else ["N/A"]
    sel=st.selectbox("Select Crop",opts)
    if st.button("▶ GENERATE PLAN", type="primary") and crop_list:
        with st.spinner("BUILDING PLAN..."):
            result=ask_groq(f"Precision plan for {sel} in {city_name},{country} ({now.strftime('%B')}). {cur['temperature_2m']:.1f}°C, {cur['relative_humidity_2m']}% RH, AQI {aq_cur.get('european_aqi','N/A')}, 7D rain {total_rain:.0f}mm. Include: sowing, irrigation quantities, NPK, pest monitoring, harvest timeline.",system=f"Precision agriculture specialist for {country} {now.strftime('%B')}.")
        st.markdown(f'<div class="ai-out"><div class="ai-tag">MANAGEMENT PLAN · {sel.upper()}</div>{result.replace(chr(10),"<br>")}</div>',unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# TAB 4 — SIMULATION
# ══════════════════════════════════════════════════
with tabs[4]:
    st.markdown('<div class="sec-wrap">', unsafe_allow_html=True)
    s1,s2=st.columns(2)
    with s1:
        t_d=st.slider("Temp Δ (°C)",-10,+20,0); r_d=st.slider("Rainfall Δ (%)",-100,+200,0); h_d=st.slider("Humidity Δ (%)",-40,+40,0)
    with s2:
        aqi_d=st.slider("AQI Δ",-60,+200,0); w_d=st.slider("Wind Δ (km/h)",-20,+60,0); sim_crop=st.text_input("Target Crop",placeholder="Rice, Wheat...")
    base_r=total_rain/7; sim_t=cur["temperature_2m"]+t_d; sim_r=base_r*(1+r_d/100); sim_aqi=(aq_cur.get("european_aqi") or 30)+aqi_d; sim_h=min(100,max(0,cur["relative_humidity_2m"]+h_d)); sim_w=max(0,cur["wind_speed_10m"]+w_d)
    sv=st.columns(5)
    for col,lbl,bv,sv_val,unit in [(sv[0],"TEMP",cur["temperature_2m"],sim_t,"°C"),(sv[1],"RAIN/D",base_r,sim_r,"mm"),(sv[2],"RH",cur["relative_humidity_2m"],sim_h,"%"),(sv[3],"AQI",aq_cur.get("european_aqi",30),sim_aqi,""),(sv[4],"WIND",cur["wind_speed_10m"],sim_w,"km/h")]:
        dlt=sv_val-bv; dc="#00ff8c" if dlt<=0 else "#ff4060"
        with col:
            st.markdown(f"""<div class="gc" style="padding:1.2rem 1.4rem"><div class="dv-l">{lbl}</div><div class="dv-n" style="font-size:1.5rem">{sv_val:.1f}<span class="dv-u">{unit}</span></div><div class="dv-s" style="color:{dc}">{'▲' if dlt>0 else '▼'} {abs(dlt):.1f}{unit}</div></div>""", unsafe_allow_html=True)
    if st.button("▶ RUN SIMULATION", type="primary"):
        with st.spinner("SIMULATING..."):
            result=ask_groq(f"Farm sim for {city_name},{country} ({now.strftime('%B')}). BASELINE: {cur['temperature_2m']:.1f}°C, {base_r:.1f}mm/d, RH {cur['relative_humidity_2m']}%, AQI {aq_cur.get('european_aqi','N/A')}. SCENARIO: {sim_t:.1f}°C, {sim_r:.1f}mm/d, RH {sim_h:.0f}%, AQI {sim_aqi:.0f}. {'Crop: '+sim_crop if sim_crop else ''}. Quantified: 1)Risk delta % 2)Yield impact 3)Resource changes 4)Strategies",system=f"Agricultural simulation expert for {country}.")
        st.markdown(f'<div class="ai-out"><div class="ai-tag">SIMULATION RESULTS</div>{result.replace(chr(10),"<br>")}</div>',unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# TAB 5 — CROP SCANNER
# ══════════════════════════════════════════════════
with tabs[5]:
    st.markdown('<div class="sec-wrap">', unsafe_allow_html=True)
    sc1,sc2=st.columns([1,1])
    with sc1:
        uploaded=st.file_uploader("UPLOAD CROP IMAGE",type=["jpg","jpeg","png","webp"])
        crop_name_s=st.text_input("Crop Name",placeholder="Tomato, Rice..."); scan_ctx=st.text_area("Symptoms",placeholder="Yellow leaves, spots...",height=80)
    with sc2:
        if uploaded: st.image(uploaded,caption="SAMPLE",use_container_width=True)
        else: st.markdown("""<div style="width:100%;height:200px;background:rgba(0,255,140,0.02);border:1px dashed rgba(0,255,140,0.18);border-radius:6px;display:flex;align-items:center;justify-content:center;font-family:Share Tech Mono,monospace;font-size:0.6rem;color:rgba(0,120,60,0.5);text-align:center">◈ AWAITING SAMPLE<br><br>JPG · PNG · WEBP</div>""", unsafe_allow_html=True)
    if st.button("▶ SCAN", type="primary"):
        if uploaded or scan_ctx or crop_name_s:
            with st.spinner("SCANNING..."):
                if uploaded:
                    img_b=uploaded.read(); img_b64=base64.b64encode(img_b).decode(); ext=uploaded.name.split('.')[-1].lower(); mime="image/jpeg" if ext in ["jpg","jpeg"] else f"image/{ext}"
                    try:
                        resp=get_groq().chat.completions.create(model="llama-3.3-70b-versatile",max_tokens=1000,messages=[{"role":"user","content":[{"type":"text","text":f"Plant pathologist. Crop: {crop_name_s}. Symptoms: {scan_ctx}. {city_name},{now.strftime('%B')},{cur['temperature_2m']:.1f}°C,{cur['relative_humidity_2m']}% RH. Diagnosis, severity, treatment, prevention."},{"type":"image_url","image_url":{"url":f"data:{mime};base64,{img_b64}"}}]}])
                        result=resp.choices[0].message.content
                    except: result=ask_groq(f"Plant health: {crop_name_s},{scan_ctx},{city_name},{now.strftime('%B')},{cur['temperature_2m']:.1f}°C,{cur['relative_humidity_2m']}% RH.")
                else: result=ask_groq(f"Plant health. Crop:{crop_name_s}. Symptoms:{scan_ctx}. {city_name},{now.strftime('%B')},{cur['temperature_2m']:.1f}°C,{cur['relative_humidity_2m']}% RH.")
            st.markdown(f'<div class="ai-out"><div class="ai-tag">CROP HEALTH REPORT</div>{result.replace(chr(10),"<br>")}</div>',unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# TAB 6 — FIELD AI
# ══════════════════════════════════════════════════
with tabs[6]:
    st.markdown('<div class="sec-wrap">', unsafe_allow_html=True)
    st.markdown(f"""<div style="padding:0.7rem 1.1rem;background:rgba(0,255,140,0.03);border:1px solid rgba(0,255,140,0.08);border-radius:5px;margin-bottom:1rem;font-family:Share Tech Mono,monospace;font-size:0.6rem;color:rgba(0,160,80,0.6)">
◈ CONTEXT LOADED · {city_name.upper()},{country.upper()} · {now.strftime('%B %Y')} · {cur['temperature_2m']:.1f}°C · {cur['relative_humidity_2m']}% RH · AQI {aq_cur.get('european_aqi','N/A')} · 7D RAIN: {total_rain:.0f}MM · ENV {es}/100
</div>""", unsafe_allow_html=True)
    focus=st.text_input("CROP FOCUS",placeholder="Rice, Tomato, Groundnut...")
    if "chat" not in st.session_state: st.session_state.chat=[]
    if not st.session_state.chat:
        sqc=st.columns(2)
        for i,q in enumerate(["What diseases to watch for this month?","Water requirements this week?","Safe to spray pesticide today?","Generate 30-day farming schedule","Flood/drought risk for my crops?","Which fertiliser to apply now?"]):
            with sqc[i%2]:
                st.markdown(f"""<div style="padding:0.6rem 0.9rem;background:rgba(0,255,140,0.03);border:1px solid rgba(0,255,140,0.1);border-radius:4px;margin-bottom:0.5rem;font-size:0.72rem;color:rgba(0,180,80,0.7);font-family:Share Tech Mono,monospace">▸ {q}</div>""", unsafe_allow_html=True)
    for msg in st.session_state.chat:
        if msg["role"]=="user":
            st.markdown(f"""<div class="cu-row"><div class="cbub cu-bub"><div class="cfrom cfrom-u">◈ YOU</div>{msg['content']}</div></div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="ca-row"><div class="cbub ca-bub"><div class="cfrom cfrom-a">◈ AEROVEDA AI</div>{msg['content']}</div></div>""", unsafe_allow_html=True)
    user_in=st.chat_input("Query the Field Intelligence System...")
    if user_in:
        st.session_state.chat.append({"role":"user","content":user_in})
        with st.spinner("PROCESSING..."):
            reply=ask_groq_chat(st.session_state.chat,system=f"""Aeroveda Field AI — expert agronomist with real-time awareness.
LOCATION: {city_name},{region},{country} | {lat:.4f}°N,{lon:.4f}°E
DATE: {now.strftime('%d %B %Y')} | SEASON: {'Monsoon' if (abs(lat)<25 and now.month in [6,7,8,9,10]) else 'Current'}
WEATHER: {cur['temperature_2m']:.1f}°C | RH {cur['relative_humidity_2m']}% | Wind {cur['wind_speed_10m']:.1f}km/h | UV {cur.get('uv_index',0) or 0:.0f} | {wdesc(cur['weather_code'])}
AIR: AQI {aq_cur.get('european_aqi','N/A')} | PM2.5 {aq_cur.get('pm2_5','N/A')}
RAINFALL 7D: {total_rain:.0f}mm | ENV {es}/100 | AG {ag}/100
{'CROP: '+focus if focus else ''}
Give precise location-specific answers referencing actual conditions.""",max_tokens=900)
        st.session_state.chat.append({"role":"assistant","content":reply}); st.rerun()
    if st.session_state.chat:
        if st.button("↺ CLEAR"): st.session_state.chat=[]; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# BOTTOM STATUS BAR
# ══════════════════════════════════════════════════
st.markdown(f"""
<div class="status-bar">
  <div class="sb-item">🌱 <span style="color:rgba(0,200,80,0.5)">AEROVEDA OS</span> <span class="sb-val">v3.0</span></div>
  <div class="sb-item">📍 <span class="sb-val">{city_name.upper()}, {country.upper()}</span></div>
  <div class="sb-item">🕐 <span class="sb-val">{now.strftime('%H:%M:%S')} UTC</span></div>
  <div class="sb-item">DATA STREAM <span class="sb-val" style="color:#00ff8c">● ACTIVE</span></div>
  <div class="sb-item">ENV SCORE <span class="sb-val" style="color:{es_color}">{es}/100</span></div>
  <div class="sb-item">AQ INDEX <span class="sb-val">{aq_cur.get('european_aqi','N/A')}</span></div>
  <div class="sb-item">SECURITY <span class="sb-val" style="color:#80ff40">🔒 ENCRYPTED</span></div>
</div>
""", unsafe_allow_html=True)
