import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
from groq import Groq
import math
import base64

# streamlit-js-eval for real GPS
from streamlit_js_eval import get_geolocation

st.set_page_config(
    page_title="AEROVEDA OS",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════
# CSS — Cyan + Earth (deep teal, soil amber, forest, ocean blue)
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Exo+2:wght@200;300;400;500;600;700&family=Share+Tech+Mono&display=swap');

*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body,[class*="css"]{font-family:'Exo 2',sans-serif;background:#040d12!important;color:#b8e8f0}

/* Deep ocean-space background */
.stApp{
  background:
    radial-gradient(ellipse 70% 50% at 20% 20%, rgba(0,180,220,0.06) 0%,transparent 50%),
    radial-gradient(ellipse 60% 40% at 80% 80%, rgba(20,120,80,0.05) 0%,transparent 45%),
    radial-gradient(ellipse 80% 60% at 50% 50%, rgba(0,80,120,0.08) 0%,transparent 60%),
    #040d12!important;
  overflow-x:hidden;
}
/* Subtle grid */
.stApp::before{
  content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
  background-image:
    linear-gradient(rgba(0,200,255,0.018) 1px,transparent 1px),
    linear-gradient(90deg,rgba(0,200,255,0.018) 1px,transparent 1px);
  background-size:50px 50px;
}
/* Scanlines */
.stApp::after{
  content:'';position:fixed;inset:0;pointer-events:none;z-index:9997;
  background:repeating-linear-gradient(0deg,transparent,transparent 3px,rgba(0,0,0,0.015) 3px,rgba(0,0,0,0.015) 4px);
}
.main .block-container{padding:0 0 4rem!important;max-width:100%!important;position:relative;z-index:1}

/* ══ TOP BAR ══ */
.topbar{
  display:flex;align-items:center;justify-content:space-between;
  padding:0 2rem;height:54px;
  background:rgba(4,13,18,0.98);
  border-bottom:1px solid rgba(0,200,255,0.1);
  position:relative;overflow:hidden;
}
.topbar::after{
  content:'';position:absolute;bottom:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent 0%,#00c8ff 30%,#22d4a0 60%,#00c8ff 80%,transparent 100%);
  animation:tb-sweep 5s ease-in-out infinite;opacity:0.6;
}
@keyframes tb-sweep{0%,100%{opacity:0.3}50%{opacity:0.7}}

.logo{
  font-family:'Orbitron',sans-serif;font-size:1.35rem;font-weight:900;
  letter-spacing:0.14em;
  background:linear-gradient(135deg,#00c8ff 0%,#22d4a0 50%,#7ee8a2 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  filter:drop-shadow(0 0 10px rgba(0,200,255,0.4));
}
.nav-items{display:flex;align-items:center;gap:0}
.nav-item{
  font-family:'Orbitron',sans-serif;font-size:0.54rem;font-weight:600;
  letter-spacing:0.13em;color:rgba(0,180,220,0.4);
  padding:0 1.1rem;height:54px;display:flex;align-items:center;
  border-bottom:2px solid transparent;transition:all 0.2s;
}
.nav-item.active{color:#00c8ff;border-bottom-color:#00c8ff}
.hdr-right{display:flex;align-items:center;gap:14px;font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:rgba(0,180,200,0.5)}
.live-dot{width:6px;height:6px;border-radius:50%;background:#00c8ff;box-shadow:0 0 8px #00c8ff;animation:ld 1.8s ease-in-out infinite;display:inline-block;margin-right:5px}
@keyframes ld{0%,100%{opacity:1}50%{opacity:0.15}}

/* ══ HERO ══ */
.hero{
  padding:2.8rem 2.5rem 2rem;
  background:linear-gradient(180deg,rgba(0,200,255,0.04) 0%,transparent 100%);
  border-bottom:1px solid rgba(0,200,255,0.07);
  display:flex;align-items:flex-start;justify-content:space-between;
}
.hero-title{
  font-family:'Orbitron',sans-serif;font-size:2.9rem;font-weight:900;
  color:#fff;letter-spacing:-0.01em;line-height:1.06;
  text-shadow:0 0 40px rgba(0,200,255,0.25);
}
.hero-title .hl{
  background:linear-gradient(135deg,#00c8ff,#22d4a0,#7ee8a2);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}
.hero-sub{font-size:0.85rem;color:rgba(0,160,200,0.6);margin-top:0.6rem;font-weight:300;letter-spacing:0.04em}
.hero-kpis{display:flex;flex-direction:column;gap:8px;align-items:flex-end;padding-top:0.3rem}
.kpi{display:flex;align-items:center;gap:10px;font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:rgba(0,160,190,0.55)}
.kpi-val{font-family:'Orbitron',sans-serif;font-size:1.05rem;font-weight:800}

/* ══ TICKER ══ */
.ticker{
  padding:6px 0;background:rgba(4,8,14,0.98);
  border-bottom:1px solid rgba(0,200,255,0.07);
  overflow:hidden;white-space:nowrap;
  position:relative;
}
.ticker::before,.ticker::after{content:'';position:absolute;top:0;bottom:0;width:80px;z-index:2}
.ticker::before{left:0;background:linear-gradient(90deg,rgba(4,8,14,0.98),transparent)}
.ticker::after{right:0;background:linear-gradient(-90deg,rgba(4,8,14,0.98),transparent)}
.ticker-inner{display:inline-block;animation:tick 50s linear infinite;font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:rgba(0,160,180,0.55);letter-spacing:0.07em}
@keyframes tick{0%{transform:translateX(100vw)}100%{transform:translateX(-100%)}}
.tsep{color:#00c8ff;margin:0 14px;opacity:0.4}

/* ══ SECTION LABELS ══ */
.sec-label{
  display:flex;align-items:center;gap:12px;
  padding:0.6rem 2rem;
  background:rgba(0,10,18,0.5);
  border-bottom:1px solid rgba(0,200,255,0.06);
}
.sl-badge{
  font-family:'Orbitron',sans-serif;font-size:0.54rem;font-weight:700;
  letter-spacing:0.18em;color:#040d12;
  background:linear-gradient(135deg,#00c8ff,#22d4a0);
  padding:4px 12px;border-radius:2px;
  box-shadow:0 0 12px rgba(0,200,255,0.25);
}
.sl-line{flex:1;height:1px;background:linear-gradient(90deg,rgba(0,200,255,0.25),rgba(34,212,160,0.1),transparent)}
.sl-code{font-family:'Share Tech Mono',monospace;font-size:0.53rem;color:rgba(0,180,220,0.22)}

/* ══ GLASS CARDS ══ */
.card{
  background:linear-gradient(135deg,rgba(0,20,32,0.94),rgba(0,10,18,0.97));
  border:1px solid rgba(0,200,255,0.08);
  position:relative;overflow:hidden;
  transition:border-color 0.3s;
}
.card:hover{border-color:rgba(0,200,255,0.22)}
.card::before{
  content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(0,200,255,0.4),rgba(34,212,160,0.2),transparent);
}
/* earth-toned card variant */
.card-earth{
  background:linear-gradient(135deg,rgba(15,28,20,0.94),rgba(8,18,12,0.97));
  border:1px solid rgba(34,160,80,0.1);
}
.card-earth::before{background:linear-gradient(90deg,transparent,rgba(34,160,80,0.3),rgba(120,200,80,0.15),transparent)}
.card-soil{
  background:linear-gradient(135deg,rgba(28,20,10,0.94),rgba(18,12,6,0.97));
  border:1px solid rgba(180,120,40,0.12);
}
.card-soil::before{background:linear-gradient(90deg,transparent,rgba(180,120,40,0.3),rgba(220,160,60,0.15),transparent)}

.cp{padding:1.3rem 1.5rem}
.ct{font-family:'Orbitron',sans-serif;font-size:0.56rem;font-weight:700;letter-spacing:0.18em;color:rgba(0,170,200,0.7);margin-bottom:0.9rem;text-transform:uppercase}
.ct::before{content:'◈ '}

/* ══ DATA VALUES ══ */
.dv-l{font-family:'Share Tech Mono',monospace;font-size:0.55rem;letter-spacing:0.15em;color:rgba(0,140,180,0.6);margin-bottom:4px;text-transform:uppercase}
.dv-n{font-family:'Orbitron',sans-serif;font-size:1.9rem;font-weight:700;color:#fff;line-height:1;text-shadow:0 0 12px rgba(0,200,255,0.15)}
.dv-u{font-size:0.73rem;color:#00c8ff;margin-left:3px;font-weight:300;font-family:'Exo 2',sans-serif}
.dv-s{font-size:0.63rem;color:rgba(0,110,150,0.6);margin-top:4px;font-family:'Share Tech Mono',monospace}

/* ══ SCORE RINGS ══ */
.score-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:rgba(0,200,255,0.05)}
.score-cell{background:linear-gradient(135deg,rgba(0,18,28,0.96),rgba(0,8,16,0.98));padding:1.6rem 1rem;text-align:center;position:relative;overflow:hidden;transition:all 0.3s}
.score-cell:hover{background:linear-gradient(135deg,rgba(0,22,34,0.97),rgba(0,10,20,0.99));box-shadow:inset 0 0 30px rgba(0,200,255,0.03)}
.score-cell::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(0,200,255,0.35),rgba(34,212,160,0.2),transparent)}
.rh{position:relative;width:120px;height:120px;margin:0 auto}
.rh svg{width:120px;height:120px}
.rc{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;width:70px}
.rn{font-family:'Orbitron',sans-serif;font-size:1.8rem;font-weight:800;color:#fff;line-height:1}
.rd{font-family:'Share Tech Mono',monospace;font-size:0.5rem;color:rgba(0,150,180,0.6);margin-top:2px}
.st{font-family:'Orbitron',sans-serif;font-size:0.53rem;font-weight:700;letter-spacing:0.16em;color:rgba(0,150,180,0.7);margin-top:10px;text-transform:uppercase}
.sg{font-family:'Orbitron',sans-serif;font-size:0.7rem;font-weight:700;letter-spacing:0.09em;margin-top:3px}
.sh{font-size:0.55rem;color:rgba(0,100,130,0.55);margin-top:3px;font-family:'Share Tech Mono',monospace}

/* ══ POLLUTANT BARS ══ */
.pol{margin-bottom:1rem}
.pol-h{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:5px}
.pol-n{font-family:'Share Tech Mono',monospace;font-size:0.58rem;letter-spacing:0.1em;color:rgba(0,150,190,0.7);text-transform:uppercase}
.pol-v{font-family:'Orbitron',sans-serif;font-size:0.8rem;font-weight:600}
.pol-t{height:3px;background:rgba(0,200,255,0.06);border-radius:99px;position:relative;overflow:visible}
.pol-f{height:3px;border-radius:99px;position:relative;transition:width 1s ease}
.pol-f::after{content:'';position:absolute;right:-1px;top:-3px;width:9px;height:9px;border-radius:50%;background:currentColor;box-shadow:0 0 8px currentColor,0 0 16px currentColor}

/* ══ ALERTS ══ */
.alert{display:flex;gap:12px;padding:0.9rem 1.2rem;border-radius:6px;margin-bottom:0.6rem;position:relative}
.alert::before{content:'';position:absolute;left:0;top:0;bottom:0;width:3px;border-radius:3px 0 0 3px}
.a-c{background:rgba(255,40,70,0.06);border:1px solid rgba(255,40,70,0.18)}
.a-c::before{background:linear-gradient(180deg,#ff2846,#cc001a)}
.a-w{background:rgba(220,160,20,0.06);border:1px solid rgba(220,160,20,0.18)}
.a-w::before{background:linear-gradient(180deg,#dca014,#a87800)}
.a-s{background:rgba(0,200,255,0.04);border:1px solid rgba(0,200,255,0.14)}
.a-s::before{background:linear-gradient(180deg,#00c8ff,#0096cc)}
.ai{font-size:1.1rem;flex-shrink:0;padding-top:1px}
.at{font-family:'Orbitron',sans-serif;font-size:0.57rem;font-weight:700;letter-spacing:0.13em;margin-bottom:4px}
.a-c .at{color:#ff6878}.a-w .at{color:#dcc040}.a-s .at{color:#00c8ff}
.am{font-size:0.8rem;line-height:1.6}
.a-c .am{color:#ffaaaa}.a-w .am{color:#f8e090}.a-s .am{color:#90e0f0}

/* ══ CROP CARDS ══ */
.cc-row{display:flex;align-items:center;gap:1.1rem;padding:0.9rem 1.3rem;
  background:linear-gradient(135deg,rgba(8,22,18,0.9),rgba(4,14,10,0.95));
  border:1px solid rgba(34,180,100,0.1);border-left:3px solid rgba(34,180,100,0.5);
  border-radius:6px;margin-bottom:0.6rem;transition:all 0.3s}
.cc-row:hover{border-color:rgba(34,200,120,0.3);transform:translateX(5px);box-shadow:0 3px 20px rgba(34,180,100,0.08)}
.cc-em{font-size:2rem;flex-shrink:0}
.cc-bd{flex:1}
.cc-nm{font-family:'Orbitron',sans-serif;font-size:0.86rem;font-weight:700;color:#e8fff4;letter-spacing:0.04em}
.cc-rs{font-size:0.73rem;color:rgba(34,180,100,0.8);margin-top:3px}
.cc-cr{font-size:0.62rem;color:rgba(20,120,60,0.6);margin-top:4px;font-family:'Share Tech Mono',monospace}

/* ══ CHAT ══ */
.cu-r{display:flex;justify-content:flex-end;margin-bottom:0.6rem}
.ca-r{display:flex;justify-content:flex-start;margin-bottom:0.6rem}
.cbub{padding:0.85rem 1.1rem;border-radius:8px;font-size:0.83rem;line-height:1.7;max-width:82%}
.cu-b{background:rgba(0,200,255,0.07);border:1px solid rgba(0,200,255,0.18);color:#c8f0f8;border-radius:8px 8px 2px 8px}
.ca-b{background:rgba(0,12,22,0.97);border:1px solid rgba(0,200,255,0.09);color:#a8e8f0;border-radius:8px 8px 8px 2px}
.cfrom{font-family:'Share Tech Mono',monospace;font-size:0.52rem;letter-spacing:0.18em;margin-bottom:5px;text-transform:uppercase}
.cf-u{text-align:right;color:#00c8ff}.cf-a{color:#22d4a0}

/* ══ AI OUTPUT ══ */
.ai-box{background:rgba(2,8,14,0.98);border:1px solid rgba(0,200,255,0.12);border-radius:8px;padding:1.6rem;margin-top:1rem;color:#a8f0e8;line-height:1.9;font-size:0.86rem;position:relative}
.ai-tag{position:absolute;top:-10px;left:16px;background:#040d12;padding:0 10px;font-family:'Orbitron',sans-serif;font-size:0.48rem;letter-spacing:0.2em;font-weight:700;
  background:linear-gradient(135deg,#00c8ff,#22d4a0);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}

/* ══ TABS ══ */
.stTabs [data-baseweb="tab-list"]{background:rgba(4,8,14,0.98)!important;border-bottom:1px solid rgba(0,200,255,0.09)!important;gap:0!important;padding:0 2rem!important}
.stTabs [data-baseweb="tab"]{font-family:'Orbitron',sans-serif!important;font-size:0.54rem!important;letter-spacing:0.13em!important;text-transform:uppercase!important;color:rgba(0,160,200,0.38)!important;padding:0.9rem 1.3rem!important;background:transparent!important;border:none!important;font-weight:600!important}
.stTabs [aria-selected="true"]{color:#00c8ff!important;border-bottom:2px solid #00c8ff!important;background:rgba(0,200,255,0.03)!important;text-shadow:0 0 10px rgba(0,200,255,0.5)!important}
.stTabs [data-baseweb="tab-panel"]{padding:0!important;background:transparent!important}

/* ══ INPUTS ══ */
.stTextInput input{background:rgba(0,12,22,0.92)!important;border:1px solid rgba(0,200,255,0.16)!important;border-radius:6px!important;color:#c8eef8!important;font-family:'Exo 2',sans-serif!important;font-size:0.95rem!important}
.stTextInput input:focus{border-color:rgba(0,200,255,0.48)!important;box-shadow:0 0 0 2px rgba(0,200,255,0.07)!important}
.stTextInput label{color:#007aaa!important;font-family:'Share Tech Mono',monospace!important;font-size:0.56rem!important;letter-spacing:0.18em!important}
.stTextArea textarea{background:rgba(0,12,22,0.92)!important;border:1px solid rgba(0,200,255,0.16)!important;border-radius:6px!important;color:#c8eef8!important}

/* ══ BUTTONS ══ */
.stButton button{background:rgba(0,200,255,0.06)!important;border:1px solid rgba(0,200,255,0.22)!important;color:#00c8ff!important;border-radius:4px!important;font-family:'Orbitron',sans-serif!important;font-size:0.54rem!important;letter-spacing:0.13em!important;font-weight:700!important}
.stButton button:hover{background:rgba(0,200,255,0.14)!important;border-color:#00c8ff!important;color:#fff!important;box-shadow:0 0 20px rgba(0,200,255,0.18)!important}
button[kind="primary"]{background:linear-gradient(135deg,rgba(0,80,120,0.6),rgba(0,180,220,0.4))!important;border:1px solid #00c8ff!important;color:#fff!important}

/* ══ SELECT ══ */
[data-baseweb="select"]>div{background:rgba(0,12,22,0.92)!important;border-color:rgba(0,200,255,0.16)!important;color:#c8eef8!important;border-radius:6px!important}

/* ══ SLIDER ══ */
.stSlider [data-testid="stThumbValue"]{color:#00c8ff!important;font-family:'Share Tech Mono',monospace!important}

/* ══ FILE UPLOADER ══ */
[data-testid="stFileUploader"]{background:rgba(0,12,22,0.8)!important;border:1px dashed rgba(0,200,255,0.18)!important;border-radius:8px!important}

/* ══ DATAFRAME ══ */
[data-testid="stDataFrameResizable"]{border:1px solid rgba(0,200,255,0.08)!important;border-radius:6px!important}

/* ══ SIDEBAR ══ */
[data-testid="stSidebar"]{background:rgba(2,6,12,0.99)!important;border-right:1px solid rgba(0,200,255,0.08)!important}

/* ══ MISC ══ */
#MainMenu,footer,header{visibility:hidden}
::-webkit-scrollbar{width:3px}
::-webkit-scrollbar-thumb{background:linear-gradient(180deg,#00c8ff,#22d4a0);border-radius:99px}
.stSpinner>div{border-top-color:#00c8ff!important}

/* ══ STATUS BAR ══ */
.sbar{display:flex;align-items:center;justify-content:space-between;padding:7px 2rem;
  background:rgba(4,8,14,0.99);border-top:1px solid rgba(0,200,255,0.08);
  font-family:'Share Tech Mono',monospace;font-size:0.57rem;color:rgba(0,140,180,0.5);gap:2rem}
.sb-i{display:flex;align-items:center;gap:5px;white-space:nowrap}
.sb-v{color:#00c8ff;font-weight:700}

/* ══ TAG BADGES ══ */
.tag{display:inline-block;padding:2px 8px;border-radius:3px;font-family:'Share Tech Mono',monospace;font-size:0.53rem;letter-spacing:0.08em;font-weight:700}
.tg{background:rgba(0,200,255,0.1);border:1px solid rgba(0,200,255,0.28);color:#00c8ff}
.te{background:rgba(34,180,100,0.1);border:1px solid rgba(34,180,100,0.25);color:#22d4a0}
.tw{background:rgba(220,160,20,0.1);border:1px solid rgba(220,160,20,0.22);color:#dca014}
.tr{background:rgba(255,40,70,0.1);border:1px solid rgba(255,40,70,0.22);color:#ff2846}
</style>
""", unsafe_allow_html=True)

# ─── Helpers ───────────────────────────────────────────────────────────────────
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
        st.error(f"Weather unavailable — please refresh: {e}"); return None

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

@st.cache_data(ttl=3600)
def reverse_geocode(lat, lon):
    try:
        r = requests.get(
            f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json",
            headers={"User-Agent":"Aeroveda/8.0"}, timeout=8)
        d = r.json()
        city = (d.get("address",{}).get("city") or
                d.get("address",{}).get("town") or
                d.get("address",{}).get("village",""))
        return city or None
    except: return None

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
    if s>=80: return "#00c8ff","OPTIMAL"
    elif s>=65: return "#22d4a0","GOOD"
    elif s>=45: return "#dca014","MODERATE"
    elif s>=25: return "#e07832","STRESSED"
    else: return "#ff2846","CRITICAL"

def bcol(v,g,b):
    if v<=g: return "#22d4a0"
    elif v<=b: return "#dca014"
    else: return "#ff2846"

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
        if aqi and aqi>100: alerts.append(("crisis","AIR QUALITY HAZARD",f"AQI {aqi} — Extremely hazardous. Halt outdoor farming operations immediately."))
        elif aqi and aqi>80: alerts.append(("crisis","SEVERE POLLUTION",f"AQI {aqi} — Severe pollution. Sensitive crops under critical stress."))
        elif aqi and aqi>50: alerts.append(("warning","POOR AIR QUALITY",f"AQI {aqi} — Elevated pollution reducing photosynthesis efficiency."))
    if max_day>80 or total_7d>200:
        alerts.append(("crisis","FLASH FLOOD RISK — EXTREME",f"Extreme rainfall: {max_day:.0f}mm peak day, {total_7d:.0f}mm / 7 days. Severe waterlogging imminent."))
    elif max_day>40 or total_7d>120:
        alerts.append(("crisis","FLOOD PROBABILITY HIGH",f"{total_7d:.0f}mm weekly rainfall. Waterlogging risk high. Clear drainage channels."))
    elif total_7d>60:
        alerts.append(("warning","HEAVY RAINFALL",f"{total_7d:.0f}mm forecast. Reduce irrigation, monitor drainage."))
    if is_monsoon and hum>85 and total_7d>30:
        alerts.append(("warning","MONSOON DISEASE RISK",f"Active monsoon: {hum}% RH + {total_7d:.0f}mm rain. High fungal disease pressure. Apply preventive fungicide."))
    if total_7d<2 and cur.get("precipitation",0)<0.5:
        avg_max=sum(max_temps)/len(max_temps) if max_temps else 30
        if avg_max>28: alerts.append(("crisis","DROUGHT CONDITIONS",f"Near-zero rainfall ({total_7d:.1f}mm / 7d) with {avg_max:.1f}°C avg max. Emergency irrigation required."))
        elif avg_max>18: alerts.append(("warning","LOW RAINFALL",f"Only {total_7d:.1f}mm forecast. Monitor soil moisture carefully."))
    ex_heat=sum(1 for t in max_temps if t>42); hi_heat=sum(1 for t in max_temps if t>38)
    if ex_heat>=2: alerts.append(("crisis","EXTREME HEAT WAVE",f"{ex_heat} days above 42°C. Critical crop stress. Increase irrigation 40–60%."))
    elif hi_heat>=3: alerts.append(("warning","HEAT STRESS",f"{hi_heat} days above 38°C. Shift irrigation to morning and evening."))
    frost=sum(1 for t in min_temps if t<2)
    if frost>=1: alerts.append(("crisis","FROST WARNING",f"{frost} night(s) sub-2°C. Cover sensitive crops immediately."))
    if max_wind>80: alerts.append(("crisis","STORM FORCE WINDS",f"Gusts up to {max_wind:.0f} km/h. Secure all crop infrastructure."))
    elif max_wind>50: alerts.append(("warning","HIGH WIND",f"Wind speeds up to {max_wind:.0f} km/h. Avoid pesticide application."))
    if not alerts: alerts.append(("safe","ALL SYSTEMS NOMINAL",f"No threats detected. {cur['temperature_2m']:.1f}°C, {hum}% RH, {total_7d:.0f}mm / 7 days. Conditions within normal parameters."))
    return alerts

def recommend_crops(w):
    c=w["current"]; t=c["temperature_2m"]; h=c["relative_humidity_2m"]
    pl=[p for p in w["daily"]["precipitation_sum"] if p is not None]
    ar=sum(pl)/len(pl) if pl else 0; result=[]
    if 20<=t<=38 and h>50:
        result.append(("🌾","RICE",95,"Optimal temperature-humidity matrix","High water · 3–4 month cycle · transplant at 21 days"))
        result.append(("🌿","SUGARCANE",88,"Heat-humidity compatibility confirmed","Weekly deep irrigation · monthly NPK · 10–12 months"))
    if 18<=t<=35:
        result.append(("🥜","GROUNDNUT",85,"Temperature envelope aligned","Well-drained sandy loam · dry finish period required"))
        result.append(("🌽","MAIZE",82,"Thermophilic conditions met","Moderate water · high nitrogen · 90-day cycle"))
    if t>=25 and h<70:
        result.append(("🍅","TOMATO",78,"Warm-dry matrix ideal","Consistent drip irrigation · blight monitoring essential"))
        result.append(("🌶️","CHILLI",76,"Low humidity suppresses fungal risk","Potassium-rich feed · drip irrigation preferred"))
    if t<22:
        result.append(("🥬","SPINACH",90,"Cool threshold perfectly matched","Direct sow · 6–8 week harvest · high nitrogen"))
        result.append(("🥕","CARROT",84,"Root growth favoured by cool soil","Deep loose bed · thin at 4cm · 70-day cycle"))
        result.append(("🧅","ONION",80,"Bulb initiation suits cool dry air","Reduce water at bulbing · raised bed drainage"))
    if ar<3 and t>20:
        result.append(("🌻","SUNFLOWER",88,"Drought-tolerance profile matched","Minimal input · deep taproot · 80–95 days"))
        result.append(("🫘","MOONG DAL",83,"Short-season drought legume","Sandy loam · nitrogen fixing · 60–70 days"))
    result.sort(key=lambda x:-x[2]); return result[:5]

def make_ring(score, color, sz=120, sw=8):
    v=score if score is not None else 0
    r=(sz/2)-sw; circ=2*math.pi*r; dash=(v/100)*circ
    gid=f"r{abs(hash(f'{v}{color}{sz}'))%99999}"
    return f"""<svg width="{sz}" height="{sz}" viewBox="0 0 {sz} {sz}">
  <defs>
    <filter id="{gid}x"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <linearGradient id="{gid}g" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#00c8ff"/>
      <stop offset="50%" style="stop-color:{color}"/>
      <stop offset="100%" style="stop-color:#22d4a0;stop-opacity:0.7"/>
    </linearGradient>
  </defs>
  <circle cx="{sz/2}" cy="{sz/2}" r="{r}" fill="none" stroke="rgba(0,200,255,0.07)" stroke-width="{sw}"/>
  <circle cx="{sz/2}" cy="{sz/2}" r="{r}" fill="none" stroke="url(#{gid}g)" stroke-width="{sw}"
    stroke-linecap="round" stroke-dasharray="{dash:.1f} {circ:.1f}"
    transform="rotate(-90 {sz/2} {sz/2})" filter="url(#{gid}x)"/>
  <circle cx="{sz/2}" cy="{sz/2}" r="{r-sw-2}" fill="none" stroke="rgba(0,200,255,0.04)" stroke-width="0.5"/>
</svg>"""

def mini_ring(score, color="#00c8ff", sz=60):
    r=(sz/2)-5; circ=2*math.pi*r; dash=(score/100)*circ
    return f"""<svg width="{sz}" height="{sz}" viewBox="0 0 {sz} {sz}">
  <circle cx="{sz/2}" cy="{sz/2}" r="{r}" fill="none" stroke="rgba(0,200,255,0.07)" stroke-width="4"/>
  <circle cx="{sz/2}" cy="{sz/2}" r="{r}" fill="none" stroke="{color}" stroke-width="4"
    stroke-linecap="round" stroke-dasharray="{dash:.1f} {circ:.1f}" transform="rotate(-90 {sz/2} {sz/2})"/>
  <text x="{sz/2}" y="{sz/2+4}" text-anchor="middle" font-family="Orbitron,sans-serif"
    font-size="10" font-weight="800" fill="{color}">{score}</text>
</svg>"""

# ══════════════════════════════════════════════════════════════
# LOCATION SYSTEM using streamlit-js-eval
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div style="background:linear-gradient(135deg,rgba(0,20,32,0.97),rgba(0,10,18,0.99));
  border-bottom:1px solid rgba(0,200,255,0.1);padding:12px 2rem;
  display:flex;align-items:center;gap:16px;position:relative;overflow:hidden;">
  <div style="position:absolute;top:0;left:0;right:0;height:2px;
    background:linear-gradient(90deg,transparent,#00c8ff,#22d4a0,transparent);opacity:0.7"></div>
  <span style="font-family:Orbitron,sans-serif;font-size:0.54rem;font-weight:700;
    letter-spacing:0.18em;color:rgba(0,180,220,0.6);white-space:nowrap;">◈ LOCATION NODE</span>
""", unsafe_allow_html=True)

loc1, loc2, loc3 = st.columns([3, 1, 1])
with loc1:
    city_input = st.text_input(
        "CITY / REGION",
        value=st.session_state.get("city", "Bengaluru"),
        placeholder="Type any city — Delhi, Mumbai, Chennai, Hyderabad...",
        label_visibility="collapsed"
    )
    if city_input:
        st.session_state["city"] = city_input

with loc2:
    use_gps = st.button("📍 USE MY LOCATION", type="primary", use_container_width=True)

with loc3:
    st.markdown(f"""<div style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;
      color:rgba(0,160,190,0.5);padding-top:8px;text-align:center">
      {st.session_state.get('city','Bengaluru').upper()}
    </div>""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ── GPS using streamlit-js-eval ──────────────────────────────
if use_gps:
    with st.spinner("Acquiring GPS signal — please allow location access in your browser..."):
        location = get_geolocation()

    if location and location.get("coords"):
        gps_lat = location["coords"]["latitude"]
        gps_lon = location["coords"]["longitude"]
        detected_city = reverse_geocode(gps_lat, gps_lon)
        if detected_city:
            st.session_state["city"] = detected_city
            st.success(f"📍 Location detected: **{detected_city}** ({gps_lat:.4f}°, {gps_lon:.4f}°)")
            st.rerun()
        else:
            # Fall back to coordinates directly
            st.session_state["gps_lat"] = gps_lat
            st.session_state["gps_lon"] = gps_lon
            st.success(f"📍 GPS acquired: {gps_lat:.4f}°N, {gps_lon:.4f}°E")
            st.rerun()
    elif location is None:
        st.warning("Browser did not return location. Please allow location access and try again.")
    else:
        st.error("Could not read GPS coordinates. Try typing your city manually.")

# ─── Geocode / use GPS coords directly ────────────────────────────────────────
active_city = st.session_state.get("city", "Bengaluru")
gps_lat_direct = st.session_state.get("gps_lat")
gps_lon_direct = st.session_state.get("gps_lon")

if gps_lat_direct and gps_lon_direct and not st.session_state.get("city_from_gps"):
    lat, lon = float(gps_lat_direct), float(gps_lon_direct)
    country, city_name, region = "Unknown", f"{lat:.2f}°N", ""
    geo_result = None
else:
    geo_result = geocode(active_city)
    if not geo_result:
        st.error(f"⚠ Location '{active_city}' not found. Please check spelling.")
        st.stop()
    lat, lon, country, city_name, region = geo_result

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
ec, eg = grade(es)

# ══════════════════════════════════════════════════════════════
# TOP NAV
# ══════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="topbar">
  <div class="logo">AEROVEDA</div>
  <div class="nav-items">
    <span class="nav-item active">OVERVIEW</span>
    <span class="nav-item">ENVIRONMENT</span>
    <span class="nav-item">AGRICULTURE</span>
    <span class="nav-item">PREDICTIONS</span>
    <span class="nav-item">AI CORE</span>
  </div>
  <div class="hdr-right">
    <span><span class="live-dot"></span>LIVE DATA</span>
    <span style="color:rgba(0,160,200,0.35)">|</span>
    <span style="color:rgba(0,180,220,0.5)">{city_name.upper()}, {country.upper()}</span>
    <span style="color:rgba(0,160,200,0.35)">|</span>
    <span>{now.strftime('%H:%M')} UTC</span>
  </div>
</div>
""", unsafe_allow_html=True)

# HERO
st.markdown(f"""
<div class="hero">
  <div>
    <div class="hero-title">INTELLIGENCE<br><span class="hl">BEYOND PLANET</span></div>
    <div class="hero-sub">Real-time agricultural intelligence for {city_name}, {country} · AI-powered environmental analytics</div>
  </div>
  <div class="hero-kpis">
    <div class="kpi"><span style="color:rgba(0,140,180,0.4)">STATUS</span> <span class="kpi-val" style="color:{'#ff2846' if any(c[0]=='crisis' for c in detect_crises(weather,aq_cur,lat)) else '#00c8ff'}">{'⚠ ALERTS' if any(c[0]=='crisis' for c in detect_crises(weather,aq_cur,lat)) else 'OPTIMAL'}</span></div>
    <div class="kpi"><span style="color:rgba(0,140,180,0.4)">ENV SCORE</span> <span class="kpi-val" style="color:{ec}">{es}.0 <span style="font-size:0.5rem;color:rgba(0,140,180,0.4)">/100</span></span></div>
    <div class="kpi"><span style="color:rgba(0,140,180,0.4)">AG POTENTIAL</span> <span class="kpi-val" style="color:#22d4a0">{ag}%</span></div>
    <div class="kpi"><span style="color:rgba(0,140,180,0.4)">{lat:.3f}°{'N' if lat>=0 else 'S'} {lon:.3f}°{'E' if lon>=0 else 'W'}</span></div>
  </div>
</div>
""", unsafe_allow_html=True)

# TICKER
pm25v = float(aq_cur.get("pm2_5",0) or 0)
ti = [f"TEMP: {cur['temperature_2m']:.1f}°C",f"HUMIDITY: {cur['relative_humidity_2m']}%",
      f"WIND: {cur['wind_speed_10m']:.1f}km/h",f"UV: {cur.get('uv_index',0) or 0:.0f}",
      f"PM2.5: {pm25v:.1f}μg/m³",f"AQI: {aq_cur.get('european_aqi','N/A')}",
      f"7D RAIN: {total_rain:.0f}mm",f"CONDITIONS: {wdesc(cur['weather_code']).upper()}",
      f"ENV: {es}/100",f"AG: {ag}/100",f"LOCATION: {city_name.upper()},{country.upper()}",
      f"DATA: LIVE",f"{now.strftime('%d %b %Y')}"]
sep='<span class="tsep">//</span>'
ts=sep.join(ti)
st.markdown(f'<div class="ticker"><div class="ticker-inner">{ts}&nbsp;&nbsp;&nbsp;&nbsp;{ts}</div></div>', unsafe_allow_html=True)

# SCORE ROW
st.markdown('<div class="score-grid">', unsafe_allow_html=True)
sc = st.columns(4)
for col, score, name, hint in [
    (sc[0],ps,"POLLUTION INDEX","Higher = Cleaner"),
    (sc[1],ws,"WEATHER SCORE","Temp · Wind · UV"),
    (sc[2],es,"ENV SCORE","55% Wx + 45% AQ"),
    (sc[3],ag,"AG POTENTIAL","Farm Suitability"),
]:
    v=score if score is not None else 0; color,gr=grade(v); disp=str(score) if score is not None else "N/A"
    with col:
        st.markdown(f"""
<div class="score-cell">
  <div class="rh">{make_ring(v,color)}
    <div class="rc"><div class="rn" style="color:{color};text-shadow:0 0 12px {color}80">{disp}</div><div class="rd">/ 100</div></div>
  </div>
  <div class="st">{name}</div><div class="sg" style="color:{color}">{gr}</div>
  <div class="sh">{hint}</div>
</div>""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# TABS
tabs = st.tabs(["🌍 OVERVIEW","◈ ENVIRONMENT","⚠ CRISIS INTEL","🌱 CROP ENGINE","🔬 SIMULATION","🔍 CROP SCANNER","◈ FIELD AI"])

# ══════════════════════════════════════════════
# TAB 0 — OVERVIEW
# ══════════════════════════════════════════════
with tabs[0]:
    r1 = st.columns([1.2, 1, 0.9])

    # ── Globe (realistic Earth) ──
    with r1[0]:
        # Build globe HTML — use .replace() to inject Python vars safely, avoid f-string JS brace conflicts
        globe_html = """<!DOCTYPE html><html><head><meta charset="utf-8"/>
<style>*{margin:0;padding:0;box-sizing:border-box}body{background:#040d12;overflow:hidden}canvas{display:block;width:100%;height:380px}</style>
</head><body>
<canvas id="c" width="520" height="380"></canvas>
<script>
var c=document.getElementById('c'),ctx=c.getContext('2d');
var W=520,H=380,cx=W/2,cy=H/2+10,R=Math.min(W,H)*0.4,t=0,speed=0.004;
var tlat=__LAT__*Math.PI/180,tlon=__LON__*Math.PI/180;
var rotY=Math.PI-tlon,rotX=-tlat*0.45;

// Stars
var stars=[];
for(var i=0;i<250;i++) stars.push([Math.random()*W,Math.random()*H,Math.random()]);

// Real continent outlines (simplified but recognisable)
var LAND=[
  // SOUTH ASIA (India)
  [[37,68],[37,78],[25,62],[22,68],[20,73],[15,74],[10,77],[8,77],[8,80],[13,80],[18,84],[20,87],[22,88],[24,92],[26,92],[28,97],[30,97],[34,76],[36,74],[37,68]],
  // SOUTHEAST ASIA
  [[28,97],[22,100],[18,100],[15,100],[12,102],[10,104],[4,108],[1,104],[-6,107],[-8,115],[-8,125],[0,120],[5,115],[10,119],[18,110],[22,114],[25,120],[30,122],[22,108],[28,97]],
  // CHINA/EAST ASIA
  [[22,108],[25,120],[30,122],[35,120],[38,118],[40,120],[42,130],[48,135],[52,142],[54,138],[52,130],[46,122],[40,118],[36,110],[32,114],[28,112],[25,112],[22,108]],
  // CENTRAL/WEST ASIA
  [[37,68],[40,72],[42,78],[44,82],[50,80],[55,70],[58,60],[55,50],[48,45],[40,40],[37,42],[36,36],[37,30],[36,28],[37,22],[37,15],[37,10],[36,8],[37,2],[37,-6],[34,36],[37,68]],
  // EUROPE
  [[36,-6],[36,28],[48,40],[55,38],[60,30],[65,26],[70,28],[72,26],[68,18],[60,22],[58,14],[54,10],[50,8],[48,6],[44,2],[42,-2],[40,-8],[36,-6]],
  // AFRICA
  [[37,10],[36,36],[25,38],[12,44],[10,42],[4,40],[-5,40],[-16,38],[-26,33],[-35,18],[-35,-16],[-26,-32],[-14,-36],[-6,-35],[0,-8],[4,8],[15,12],[22,38],[37,10]],
  // NORTH AMERICA
  [[72,-140],[68,-136],[60,-145],[58,-136],[54,-130],[48,-124],[38,-122],[32,-118],[24,-110],[20,-110],[20,-98],[16,-92],[14,-90],[18,-88],[24,-80],[30,-80],[38,-75],[44,-66],[50,-54],[56,-60],[66,-62],[72,-80],[74,-90],[72,-110],[72,-140]],
  // SOUTH AMERICA
  [[10,-62],[8,-60],[4,-52],[0,-50],[-4,-42],[-10,-38],[-24,-44],[-34,-54],[-56,-68],[-56,-64],[-42,-64],[-24,-44],[-18,-70],[-16,-72],[-8,-78],[0,-80],[6,-77],[10,-72],[10,-62]],
  // AUSTRALIA
  [[-14,128],[-12,136],[-16,140],[-24,154],[-38,148],[-38,116],[-22,114],[-14,128]],
  // JAPAN
  [[30,130],[34,136],[36,140],[40,142],[42,144],[44,142],[42,140],[38,140],[34,136],[30,130]],
  // UK/IRELAND
  [[50,-6],[58,-6],[60,-2],[58,0],[52,2],[50,2],[50,-6]],
  // INDONESIA main
  [[-2,106],[0,104],[4,100],[2,108],[-2,114],[-8,115],[-8,114],[-2,106]],
];

// Ocean color zones (simulated depth)
var OCEAN_ZONES = [
  // Pacific deep
  {la:10,lo:-160,r:28,c:'rgba(0,30,60,0.6)'},
  {la:-20,lo:-120,r:22,c:'rgba(0,20,50,0.5)'},
  // Indian Ocean
  {la:-10,lo:75,r:20,c:'rgba(0,25,55,0.5)'},
  // Atlantic
  {la:25,lo:-40,r:22,c:'rgba(0,28,58,0.5)'},
  // Arctic
  {la:80,lo:0,r:18,c:'rgba(180,220,240,0.15)'},
];

function ll3d(la,lo,r){var p=la*Math.PI/180,l=lo*Math.PI/180;return[r*Math.cos(p)*Math.cos(l),r*Math.sin(p),r*Math.cos(p)*Math.sin(l)]}
function rot3(x,y,z,ry,rx){var x1=x*Math.cos(ry)-z*Math.sin(ry),z1=x*Math.sin(ry)+z*Math.cos(ry),y2=y*Math.cos(rx)-z1*Math.sin(rx),z2=y*Math.sin(rx)+z1*Math.cos(rx);return[x1,y2,z2]}
function proj(x,y,z){var f=520,s=f/(f+z+R*0.3);return[cx+x*s,cy-y*s,s]}
function vis(z){return z>-R*0.12}

function drawFrame(){
  ctx.clearRect(0,0,W,H);

  // Background
  var bg=ctx.createRadialGradient(cx,cy-20,R*0.1,cx,cy,W*0.75);
  bg.addColorStop(0,'rgba(0,20,35,1)');
  bg.addColorStop(0.5,'rgba(0,10,20,1)');
  bg.addColorStop(1,'rgba(4,8,18,1)');
  ctx.fillStyle=bg;ctx.fillRect(0,0,W,H);

  // Stars with slight colour variation (cyan/warm)
  stars.forEach(function(s){
    var cols=['rgba(180,230,255,','rgba(200,255,220,','rgba(255,240,200,'];
    ctx.fillStyle=cols[Math.floor(s[2]*3)]+(0.1+s[2]*0.5)+')';
    ctx.beginPath();ctx.arc(s[0],s[1],s[2]*1.2,0,Math.PI*2);ctx.fill();
  });

  // Outer atmosphere glow
  var atm2=ctx.createRadialGradient(cx,cy,R*0.9,cx,cy,R*1.25);
  atm2.addColorStop(0,'rgba(0,160,220,0.1)');
  atm2.addColorStop(0.4,'rgba(0,100,180,0.06)');
  atm2.addColorStop(0.8,'rgba(0,60,120,0.03)');
  atm2.addColorStop(1,'transparent');
  ctx.fillStyle=atm2;ctx.beginPath();ctx.arc(cx,cy,R*1.25,0,Math.PI*2);ctx.fill();

  // Clip to globe
  ctx.save();
  ctx.beginPath();ctx.arc(cx,cy,R,0,Math.PI*2);ctx.clip();

  // ── OCEAN BASE (deep blue-teal, Earth-like) ──
  var oceanGrad=ctx.createRadialGradient(cx-R*0.25,cy-R*0.2,R*0.05,cx+R*0.1,cy+R*0.1,R);
  oceanGrad.addColorStop(0,'rgba(0,80,140,0.95)');
  oceanGrad.addColorStop(0.3,'rgba(0,55,110,0.97)');
  oceanGrad.addColorStop(0.6,'rgba(0,35,80,0.98)');
  oceanGrad.addColorStop(1,'rgba(0,15,45,1)');
  ctx.fillStyle=oceanGrad;
  ctx.fillRect(cx-R-2,cy-R-2,R*2+4,R*2+4);

  // Ocean depth variation
  var cr=rotY+t*speed;
  OCEAN_ZONES.forEach(function(oz){
    var p3=ll3d(oz.la,oz.lo,R*0.99),rr=rot3(p3[0],p3[1],p3[2],cr,rotX);
    if(!vis(rr[2]))return;
    var pr=proj(rr[0],rr[1],rr[2]);
    var rr2=oz.r*R/180*pr[2];
    var og=ctx.createRadialGradient(pr[0],pr[1],0,pr[0],pr[1],rr2);
    og.addColorStop(0,oz.c);og.addColorStop(1,'transparent');
    ctx.fillStyle=og;ctx.beginPath();ctx.arc(pr[0],pr[1],rr2,0,Math.PI*2);ctx.fill();
  });

  // ── LAT/LON GRID (subtle ocean lines) ──
  ctx.globalAlpha=0.18;
  for(var la=-80;la<=80;la+=20){
    ctx.beginPath();var fi=true;
    for(var lo=-180;lo<=180;lo+=4){
      var p3=ll3d(la,lo,R);var rr=rot3(p3[0],p3[1],p3[2],cr,rotX);
      if(!vis(rr[2])){fi=true;continue}
      var pr=proj(rr[0],rr[1],rr[2]);
      if(fi){ctx.moveTo(pr[0],pr[1]);fi=false}else ctx.lineTo(pr[0],pr[1]);
    }
    ctx.strokeStyle=la===0?'rgba(0,200,255,0.5)':'rgba(0,160,220,0.3)';
    ctx.lineWidth=la===0?0.7:0.3;ctx.stroke();
  }
  for(var lo2=-180;lo2<180;lo2+=30){
    ctx.beginPath();var fi2=true;
    for(var la2=-85;la2<=85;la2+=3){
      var p32=ll3d(la2,lo2,R);var rr2=rot3(p32[0],p32[1],p32[2],cr,rotX);
      if(!vis(rr2[2])){fi2=true;continue}
      var pr2=proj(rr2[0],rr2[1],rr2[2]);
      if(fi2){ctx.moveTo(pr2[0],pr2[1]);fi2=false}else ctx.lineTo(pr2[0],pr2[1]);
    }
    ctx.strokeStyle='rgba(0,140,200,0.2)';ctx.lineWidth=0.25;ctx.stroke();
  }
  ctx.globalAlpha=1;

  // ── LANDMASSES ──
  LAND.forEach(function(pts){
    ctx.beginPath();var fc=true;
    pts.forEach(function(p){
      var p3=ll3d(p[0],p[1],R*1.001),rr=rot3(p3[0],p3[1],p3[2],cr,rotX);
      if(rr[2]<-R*0.15){fc=true;return}
      var pr=proj(rr[0],rr[1],rr[2]);
      if(fc){ctx.moveTo(pr[0],pr[1]);fc=false}else ctx.lineTo(pr[0],pr[1]);
    });
    ctx.closePath();
    // Earth-like land: green-brown gradient
    ctx.fillStyle='rgba(34,90,40,0.82)';ctx.fill();
    ctx.strokeStyle='rgba(60,160,80,0.55)';ctx.lineWidth=0.7;ctx.stroke();
  });

  // ── ICE CAPS ──
  [[88,0],[89,60],[88,120],[88,180],[88,240],[88,300],[-88,0],[-88,60],[-88,120],[-88,180],[-88,240],[-88,300]].forEach(function(ic){
    var p3=ll3d(ic[0],ic[1],R*1.001),rr=rot3(p3[0],p3[1],p3[2],cr,rotX);
    if(!vis(rr[2]))return;
    var pr=proj(rr[0],rr[1],rr[2]);
    ctx.fillStyle='rgba(200,235,255,0.6)';
    ctx.beginPath();ctx.arc(pr[0],pr[1],10*pr[2],0,Math.PI*2);ctx.fill();
  });

  // ── AGRICULTURAL ZONES (holographic overlay) ──
  var zones=[
    [__ZA__,__ZB__,0],
    [__ZC__,__ZD__,1],
    [__ZE__,__ZF__,2],
    [__ZG__,__ZH__,1],
    [__ZI__,__ZJ__,3],
    [__ZK__,__ZL__,0],
  ];
  var zc=['#00c8ff','#22d4a0','#dca014','#e07832','#ff2846'];
  zones.forEach(function(z){
    var p3=ll3d(z[0],z[1],R*1.003),rr=rot3(p3[0],p3[1],p3[2],cr,rotX);
    if(!vis(rr[2]))return;
    var pr=proj(rr[0],rr[1],rr[2]);
    var col=zc[z[2]];
    var rads=20*pr[2];
    var rgb=col==='#00c8ff'?'0,200,255':col==='#22d4a0'?'34,212,160':col==='#dca014'?'220,160,20':col==='#e07832'?'224,120,50':'255,40,70';
    var zg=ctx.createRadialGradient(pr[0],pr[1],0,pr[0],pr[1],rads);
    zg.addColorStop(0,'rgba('+rgb+',0.3)');zg.addColorStop(0.5,'rgba('+rgb+',0.1)');zg.addColorStop(1,'transparent');
    ctx.fillStyle=zg;ctx.beginPath();ctx.arc(pr[0],pr[1],rads,0,Math.PI*2);ctx.fill();
    var pr2=rads*(1+0.07*Math.sin(t*0.06+z[2]));
    ctx.strokeStyle='rgba('+rgb+',0.6)';ctx.lineWidth=1;
    ctx.beginPath();ctx.arc(pr[0],pr[1],pr2,0,Math.PI*2);ctx.stroke();
  });

  ctx.restore();

  // ── GLOBE BORDER ──
  var brd=ctx.createLinearGradient(cx-R,cy,cx+R,cy);
  brd.addColorStop(0,'rgba(0,200,255,0.5)');brd.addColorStop(0.5,'rgba(34,212,160,0.3)');brd.addColorStop(1,'rgba(0,150,220,0.4)');
  ctx.strokeStyle=brd;ctx.lineWidth=1.5;
  ctx.beginPath();ctx.arc(cx,cy,R,0,Math.PI*2);ctx.stroke();

  // Atmosphere thin ring
  ctx.strokeStyle='rgba(0,180,255,0.12)';ctx.lineWidth=3;
  ctx.beginPath();ctx.arc(cx,cy,R+4,0,Math.PI*2);ctx.stroke();
  ctx.strokeStyle='rgba(0,200,255,0.05)';ctx.lineWidth=8;
  ctx.beginPath();ctx.arc(cx,cy,R+8,0,Math.PI*2);ctx.stroke();

  // ── EQUATORIAL HOLOGRAM RING ──
  ctx.save();ctx.translate(cx,cy);ctx.scale(1,0.2);
  ctx.strokeStyle='rgba(0,200,255,0.15)';ctx.lineWidth=1.5;
  ctx.beginPath();ctx.ellipse(0,0,R*1.08,R*1.08,0,0,Math.PI*2);ctx.stroke();
  ctx.strokeStyle='rgba(34,212,160,0.07)';ctx.lineWidth=8;
  ctx.beginPath();ctx.ellipse(0,0,R*1.14,R*1.14,0,0,Math.PI*2);ctx.stroke();
  ctx.restore();

  // ── TARGET LOCATION ──
  var tp=ll3d(__LAT__,__LON__,R*1.012),tr=rot3(tp[0],tp[1],tp[2],cr,rotX);
  if(vis(tr[2])){
    var tpr=proj(tr[0],tr[1],tr[2]);
    // Pulsing rings
    for(var ri=1;ri<=4;ri++){
      var pulse=0.5+0.5*Math.sin(t*0.08-ri*0.5);
      ctx.strokeStyle='rgba(0,200,255,'+(0.55-ri*0.1)+')';
      ctx.lineWidth=1+pulse*0.4;
      ctx.beginPath();ctx.arc(tpr[0],tpr[1],(ri*9+3*pulse)*tpr[2],0,Math.PI*2);ctx.stroke();
    }
    // Crosshair
    var ch=22*tpr[2];
    ctx.strokeStyle='rgba(0,200,255,0.7)';ctx.lineWidth=0.8;
    ctx.beginPath();ctx.moveTo(tpr[0]-ch,tpr[1]);ctx.lineTo(tpr[0]+ch,tpr[1]);ctx.stroke();
    ctx.beginPath();ctx.moveTo(tpr[0],tpr[1]-ch);ctx.lineTo(tpr[0],tpr[1]+ch);ctx.stroke();
    // Glow dot
    var cg=ctx.createRadialGradient(tpr[0],tpr[1],0,tpr[0],tpr[1],12*tpr[2]);
    cg.addColorStop(0,'rgba(255,255,255,1)');cg.addColorStop(0.25,'rgba(0,220,255,0.9)');
    cg.addColorStop(0.6,'rgba(34,212,160,0.4)');cg.addColorStop(1,'transparent');
    ctx.fillStyle=cg;ctx.beginPath();ctx.arc(tpr[0],tpr[1],10*tpr[2],0,Math.PI*2);ctx.fill();
  }

  // ── AXIS ──
  ctx.strokeStyle='rgba(0,200,255,0.08)';ctx.lineWidth=0.5;ctx.setLineDash([4,5]);
  ctx.beginPath();ctx.moveTo(cx,cy-R*1.15);ctx.lineTo(cx,cy+R*1.15);ctx.stroke();
  ctx.setLineDash([]);

  // HUD labels
  ctx.fillStyle='rgba(0,200,255,0.5)';ctx.font='9px Orbitron,monospace';
  ctx.fillText('__CITY__',cx-20,cy-R-14);
  ctx.fillStyle='rgba(0,160,190,0.4)';ctx.font='8px monospace';
  ctx.fillText('__COORDS__',cx-24,cy-R-4);

  t++;requestAnimationFrame(drawFrame);
}
drawFrame();
</script></body></html>"""
        # Inject Python variables safely
        globe_html = (globe_html
            .replace("__LAT__", str(lat))
            .replace("__LON__", str(lon))
            .replace("__CITY__", f"◈ {city_name.upper()}")
            .replace("__COORDS__", f"{lat:.2f}°N {lon:.2f}°E")
            .replace("__TLAT__", str(lat))
            .replace("__TLON__", str(lon))
            .replace("__ZA__", str(lat+0.12))
            .replace("__ZB__", str(lon-0.09))
            .replace("__ZC__", str(lat-0.08))
            .replace("__ZD__", str(lon+0.18))
            .replace("__ZE__", str(lat+0.20))
            .replace("__ZF__", str(lon+0.10))
            .replace("__ZG__", str(lat-0.16))
            .replace("__ZH__", str(lon-0.12))
            .replace("__ZI__", str(lat+0.06))
            .replace("__ZJ__", str(lon-0.22))
            .replace("__ZK__", str(lat-0.05))
            .replace("__ZL__", str(lon+0.26))
        )
        st.markdown('<div class="card cp" style="padding:1rem 1.4rem"><div class="ct">PLANETARY OVERVIEW</div>', unsafe_allow_html=True)
        import streamlit.components.v1 as components
        components.html(globe_html, height=390, scrolling=False)
        st.markdown(f"""
<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px;padding-top:8px;border-top:1px solid rgba(0,200,255,0.06)">
  <div><div class="dv-l">TEMPERATURE</div><div style="font-family:Orbitron,sans-serif;font-size:1.3rem;font-weight:700;color:#fff">{cur['temperature_2m']:.1f}<span style="font-size:0.7rem;color:#00c8ff">°C</span></div></div>
  <div><div class="dv-l">HUMIDITY</div><div style="font-family:Orbitron,sans-serif;font-size:1.3rem;font-weight:700;color:#22d4a0">{cur['relative_humidity_2m']}<span style="font-size:0.7rem;color:#22d4a0">%</span></div></div>
  <div><div class="dv-l">CONDITIONS</div><div style="font-family:Share Tech Mono,monospace;font-size:0.65rem;color:#00c8ff;margin-top:4px">{wdesc(cur['weather_code']).upper()}</div></div>
  <div><div class="dv-l">AQI</div><div style="font-family:Orbitron,sans-serif;font-size:1.3rem;font-weight:700;color:{'#22d4a0' if (aq_cur.get('european_aqi') or 100)<50 else '#dca014'}">{aq_cur.get('european_aqi','N/A')}</div></div>
</div></div>""", unsafe_allow_html=True)

    # ── Environmental Matrix ──
    with r1[1]:
        pm25=float(aq_cur.get("pm2_5",0) or 0); no2=float(aq_cur.get("nitrogen_dioxide",0) or 0)
        o3=float(aq_cur.get("ozone",0) or 0)
        st.markdown(f"""
<div class="card-earth cp" style="height:100%">
  <div class="ct" style="color:rgba(34,160,80,0.7)">ENVIRONMENTAL MATRIX</div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:1.2rem">
    <div><div class="dv-l">CO₂</div><div style="font-family:Orbitron,sans-serif;font-size:1.4rem;font-weight:700;color:#22d4a0">{int(no2*4+380)}</div><div class="dv-s">ppm</div></div>
    <div><div class="dv-l">O₂ IDX</div><div style="font-family:Orbitron,sans-serif;font-size:1.4rem;font-weight:700;color:#00c8ff">21.{max(0,9-int(pm25/10))}</div><div class="dv-s">%</div></div>
    <div><div class="dv-l">BIOD.</div><div style="font-family:Orbitron,sans-serif;font-size:1.4rem;font-weight:700;color:{'#22d4a0' if es>60 else '#dca014'}">{min(99,es+8)}%</div><div class="dv-s">idx</div></div>
    <div><div class="dv-l">WATER</div><div style="font-family:Orbitron,sans-serif;font-size:1.3rem;font-weight:700;color:#00c8ff">{max(60,100-int(pm25*0.8))}%</div></div>
    <div><div class="dv-l">SOIL</div><div style="font-family:Orbitron,sans-serif;font-size:1.3rem;font-weight:700;color:{'#22d4a0' if ws>60 else '#dca014'}">{min(99,ws+5)}%</div></div>
    <div><div class="dv-l">ENERGY</div><div style="font-family:Orbitron,sans-serif;font-size:1.3rem;font-weight:700;color:#7ee8a2">{min(99,ag+7)}%</div></div>
  </div>
  <div style="border-top:1px solid rgba(34,160,80,0.1);padding-top:0.9rem">
    <div class="dv-l" style="margin-bottom:8px">AIR QUALITY SENSORS</div>
    <div class="pol"><div class="pol-h"><span class="pol-n">PM2.5</span><span class="pol-v" style="color:{bcol(pm25,12,35)}">{pm25:.1f} <span style="font-size:0.58rem;color:rgba(0,120,100,0.6)">μg/m³</span></span></div><div class="pol-t"><div class="pol-f" style="width:{min(100,int(pm25/2.5))}%;background:{bcol(pm25,12,35)};color:{bcol(pm25,12,35)}"></div></div></div>
    <div class="pol"><div class="pol-h"><span class="pol-n">OZONE</span><span class="pol-v" style="color:{bcol(o3,60,120)}">{o3:.0f} <span style="font-size:0.58rem;color:rgba(0,120,100,0.6)">μg/m³</span></span></div><div class="pol-t"><div class="pol-f" style="width:{min(100,int(o3/1.8))}%;background:{bcol(o3,60,120)};color:{bcol(o3,60,120)}"></div></div></div>
    <div class="pol"><div class="pol-h"><span class="pol-n">NO₂</span><span class="pol-v" style="color:{bcol(no2,40,100)}">{no2:.0f} <span style="font-size:0.58rem;color:rgba(0,120,100,0.6)">μg/m³</span></span></div><div class="pol-t"><div class="pol-f" style="width:{min(100,int(no2))}%;background:{bcol(no2,40,100)};color:{bcol(no2,40,100)}"></div></div></div>
  </div>
  <div style="display:flex;align-items:center;justify-content:space-between;margin-top:0.9rem;padding-top:0.9rem;border-top:1px solid rgba(34,160,80,0.1)">
    <div><div class="dv-l">EU AQI</div><div style="font-family:Orbitron,sans-serif;font-size:1.6rem;font-weight:800;color:{bcol(aq_cur.get('european_aqi') or 30,20,60)}">{aq_cur.get('european_aqi','N/A')}</div></div>
    <div><div class="dv-l">POLLUTION SCORE</div><div style="font-family:Orbitron,sans-serif;font-size:1.6rem;font-weight:800;color:{ec}">{ps if ps is not None else 'N/A'}<span style="font-size:0.7rem;color:rgba(0,140,160,0.5)">/100</span></div></div>
  </div>
</div>""", unsafe_allow_html=True)

    # ── Crop recommendations + alerts ──
    with r1[2]:
        crops = recommend_crops(weather)
        st.markdown('<div class="card cp" style="height:100%"><div class="ct">RECOMMENDED CROPS</div>', unsafe_allow_html=True)
        for emoji,name,compat,reason,care in crops[:4]:
            cc,_=grade(compat)
            st.markdown(f"""
<div style="display:flex;align-items:center;gap:10px;padding:7px 0;border-bottom:1px solid rgba(0,200,255,0.05)">
  <div style="font-size:1.4rem">{emoji}</div>
  <div style="flex:1">
    <div style="font-family:Orbitron,sans-serif;font-size:0.68rem;font-weight:700;color:#e8f8f0">{name}</div>
    <div style="height:3px;background:rgba(0,200,255,0.07);border-radius:99px;margin-top:5px;overflow:hidden"><div style="width:{compat}%;height:3px;background:{cc};border-radius:99px"></div></div>
  </div>
  <div style="font-family:Orbitron,sans-serif;font-size:0.68rem;font-weight:800;color:{cc}">{compat}%</div>
</div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Crisis summary
        st.markdown('<div class="card cp" style="margin-top:1px"><div class="ct">CRISIS SUMMARY</div>', unsafe_allow_html=True)
        for level,title,msg in detect_crises(weather,aq_cur,lat)[:3]:
            icon="🚨" if level=="crisis" else "⚠️" if level=="warning" else "✅"
            col={"crisis":"#ff2846","warning":"#dca014","safe":"#00c8ff"}[level]
            st.markdown(f"""
<div style="padding:7px 0;border-bottom:1px solid rgba(0,200,255,0.05)">
  <div style="font-family:Orbitron,sans-serif;font-size:0.54rem;font-weight:700;color:{col};letter-spacing:0.1em;margin-bottom:2px">{icon} {title}</div>
  <div style="font-size:0.72rem;color:rgba(180,230,245,0.6);line-height:1.4">{msg[:90]}{"…" if len(msg)>90 else ""}</div>
</div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 1 — ENVIRONMENT
# ══════════════════════════════════════════════
with tabs[1]:
    st.markdown('<div style="padding:1.5rem 2rem">', unsafe_allow_html=True)
    wx=st.columns(6)
    for col,lbl,val,unit in [(wx[0],"TEMPERATURE",f"{cur['temperature_2m']:.1f}","°C"),(wx[1],"HUMIDITY",f"{cur['relative_humidity_2m']}","%"),(wx[2],"WIND",f"{cur['wind_speed_10m']:.1f}","km/h"),(wx[3],"PRECIP",f"{cur['precipitation']:.1f}","mm"),(wx[4],"UV INDEX",f"{cur.get('uv_index',0) or 0:.0f}",""),(wx[5],"FEELS LIKE",f"{cur['apparent_temperature']:.1f}","°C")]:
        with col:
            st.markdown(f"""<div class="card cp"><div class="dv-l">{lbl}</div><div class="dv-n">{val}<span class="dv-u">{unit}</span></div></div>""", unsafe_allow_html=True)
    if aq_cur:
        pm25=float(aq_cur.get("pm2_5",0) or 0); pm10=float(aq_cur.get("pm10",0) or 0)
        no2=float(aq_cur.get("nitrogen_dioxide",0) or 0); so2=float(aq_cur.get("sulphur_dioxide",0) or 0)
        o3=float(aq_cur.get("ozone",0) or 0); co=float(aq_cur.get("carbon_monoxide",0) or 0)
        aq1,aq2=st.columns(2)
        pols=[("PM₂.₅",pm25,12,35,"μg/m³",min(100,int(pm25/2.5))),("PM₁₀",pm10,20,50,"μg/m³",min(100,int(pm10/1.5))),("NO₂",no2,40,100,"μg/m³",min(100,int(no2))),("SO₂",so2,20,80,"μg/m³",min(100,int(so2))),("O₃",o3,60,120,"μg/m³",min(100,int(o3/1.8))),("CO",co/1000,0.5,2,"mg/m³",min(100,int(co/700)))]
        for i,(nm,val,g,b,unit,pct) in enumerate(pols):
            bc=bcol(val,g,b)
            with (aq1 if i<3 else aq2):
                st.markdown(f"""<div style="padding:0.6rem 0"><div class="pol"><div class="pol-h"><span class="pol-n">{nm}</span><span class="pol-v" style="color:{bc}">{val:.1f} <span style="font-size:0.56rem;color:rgba(0,110,140,0.5)">{unit}</span></span></div><div class="pol-t"><div class="pol-f" style="width:{pct}%;background:{bc};color:{bc}"></div></div></div></div>""", unsafe_allow_html=True)
    rows=[]
    for i,day in enumerate(daily["time"]):
        d=datetime.strptime(day,"%Y-%m-%d")
        rows.append({"DATE":d.strftime("%a %d %b").upper(),"MAX °C":f"{daily['temperature_2m_max'][i]:.1f}","MIN °C":f"{daily['temperature_2m_min'][i]:.1f}","RAIN mm":f"{daily['precipitation_sum'][i]:.1f}","RAIN %":f"{daily['precipitation_probability_max'][i]}%","WIND":f"{daily['wind_speed_10m_max'][i]:.1f}","UV":f"{daily['uv_index_max'][i]:.0f}"})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 2 — CRISIS
# ══════════════════════════════════════════════
with tabs[2]:
    st.markdown('<div style="padding:1.5rem 2rem">', unsafe_allow_html=True)
    max_rain_day=max((p for p in daily["precipitation_sum"] if p),default=0)
    max_temp=max((t for t in daily["temperature_2m_max"] if t),default=0)
    st.markdown(f"""<div style="padding:0.7rem 1.1rem;background:rgba(0,200,255,0.03);border:1px solid rgba(0,200,255,0.1);border-radius:6px;margin-bottom:1rem;font-family:Share Tech Mono,monospace;font-size:0.61rem;color:rgba(0,140,180,0.6)">◈ 7D RAIN: {total_rain:.0f}MM · PEAK: {max_rain_day:.0f}MM/DAY · MAX TEMP: {max_temp:.1f}°C · RH: {cur['relative_humidity_2m']}% · AQI: {aq_cur.get('european_aqi','N/A')} · MONTH: {now.strftime('%B').upper()}</div>""", unsafe_allow_html=True)
    for level,title,msg in detect_crises(weather,aq_cur,lat):
        icon="🚨" if level=="crisis" else "⚠️" if level=="warning" else "✅"
        st.markdown(f"""<div class="alert a-{level[0]}"><div class="ai">{icon}</div><div><div class="at">{title}</div><div class="am">{msg}</div></div></div>""", unsafe_allow_html=True)
    if st.button("▶ RUN AI CRISIS ANALYSIS", type="primary"):
        s={"location":f"{city_name},{country}","lat":lat,"lon":lon,"temp":cur["temperature_2m"],"rh":cur["relative_humidity_2m"],"aqi":aq_cur.get("european_aqi"),"7d_rain":total_rain,"peak_rain_day":max_rain_day,"max_temp":max_temp,"month":now.month}
        with st.spinner("Analysing..."):
            result=ask_groq(f"Agricultural crisis for {city_name},{country} ({now.strftime('%B')},lat:{lat:.1f}):\n{json.dumps(s,indent=2)}\n1)Threats from actual data 2)Crop impact 3)48h actions 4)30d outlook",system=f"Agricultural risk analyst for {country}. {now.strftime('%B')}: high rain→flood/disease focus, low rain→drought focus. Be accurate to the numbers.")
        st.markdown(f'<div class="ai-box"><div class="ai-tag">AI CRISIS REPORT · {city_name.upper()}</div>{result.replace(chr(10),"<br>")}</div>',unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 3 — CROPS
# ══════════════════════════════════════════════
with tabs[3]:
    st.markdown('<div style="padding:1.5rem 2rem">', unsafe_allow_html=True)
    crop_list=recommend_crops(weather)
    for emoji,name,compat,reason,care in crop_list:
        cc,_=grade(compat)
        st.markdown(f"""<div class="cc-row"><div class="cc-em">{emoji}</div><div class="cc-bd"><div class="cc-nm">{name}</div><div class="cc-rs">▸ {reason}</div><div class="cc-cr">◦ {care}</div></div><div>{mini_ring(compat,cc)}</div></div>""", unsafe_allow_html=True)
    opts=[f"{e} {n}" for e,n,*_ in crop_list] if crop_list else ["N/A"]
    sel=st.selectbox("Select Crop for Detailed Plan",opts)
    if st.button("▶ GENERATE MANAGEMENT PLAN", type="primary") and crop_list:
        with st.spinner("Building plan..."):
            result=ask_groq(f"Precision agriculture plan for {sel} in {city_name},{country} ({now.strftime('%B')}). {cur['temperature_2m']:.1f}°C, {cur['relative_humidity_2m']}% RH, AQI {aq_cur.get('european_aqi','N/A')}, 7D rain {total_rain:.0f}mm. Include: sowing timing, irrigation with exact quantities, NPK timeline, pest monitoring, harvest window.",system=f"Precision agriculture specialist for {country} {now.strftime('%B')} season.")
        st.markdown(f'<div class="ai-box"><div class="ai-tag">MANAGEMENT PLAN · {sel.upper()}</div>{result.replace(chr(10),"<br>")}</div>',unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 4 — SIMULATION
# ══════════════════════════════════════════════
with tabs[4]:
    st.markdown('<div style="padding:1.5rem 2rem">', unsafe_allow_html=True)
    s1,s2=st.columns(2)
    with s1:
        t_d=st.slider("Temperature Δ (°C)",-10,+20,0); r_d=st.slider("Rainfall Δ (%)",-100,+200,0); h_d=st.slider("Humidity Δ (%)",-40,+40,0)
    with s2:
        aqi_d=st.slider("AQI Δ",-60,+200,0); w_d=st.slider("Wind Δ (km/h)",-20,+60,0); sim_crop=st.text_input("Target Crop",placeholder="Rice, Wheat, Tomato...")
    base_r=total_rain/7; sim_t=cur["temperature_2m"]+t_d; sim_r=base_r*(1+r_d/100); sim_aqi=(aq_cur.get("european_aqi") or 30)+aqi_d; sim_h=min(100,max(0,cur["relative_humidity_2m"]+h_d)); sim_w=max(0,cur["wind_speed_10m"]+w_d)
    sv=st.columns(5)
    for col,lbl,bv,sv_val,unit in [(sv[0],"TEMP",cur["temperature_2m"],sim_t,"°C"),(sv[1],"RAIN/D",base_r,sim_r,"mm"),(sv[2],"RH",cur["relative_humidity_2m"],sim_h,"%"),(sv[3],"AQI",aq_cur.get("european_aqi",30),sim_aqi,""),(sv[4],"WIND",cur["wind_speed_10m"],sim_w,"km/h")]:
        dlt=sv_val-bv; dc="#22d4a0" if dlt<=0 else "#ff2846"
        with col:
            st.markdown(f"""<div class="card cp"><div class="dv-l">{lbl}</div><div class="dv-n" style="font-size:1.5rem">{sv_val:.1f}<span class="dv-u">{unit}</span></div><div class="dv-s" style="color:{dc}">{'▲' if dlt>0 else '▼'} {abs(dlt):.1f}{unit}</div></div>""", unsafe_allow_html=True)
    if st.button("▶ RUN DIGITAL TWIN SIMULATION", type="primary"):
        with st.spinner("Running simulation..."):
            result=ask_groq(f"Farm Digital Twin for {city_name},{country} ({now.strftime('%B')}). BASELINE: {cur['temperature_2m']:.1f}°C, {base_r:.1f}mm/d, RH {cur['relative_humidity_2m']}%, AQI {aq_cur.get('european_aqi','N/A')}. SCENARIO: {sim_t:.1f}°C, {sim_r:.1f}mm/d, RH {sim_h:.0f}%, AQI {sim_aqi:.0f}. {'Crop: '+sim_crop if sim_crop else ''}. Give: 1)Risk delta % 2)Yield impact with numbers 3)Resource changes 4)Adaptive strategies",system=f"Agricultural simulation expert for {country}. Give specific numbers.")
        st.markdown(f'<div class="ai-box"><div class="ai-tag">SIMULATION RESULTS</div>{result.replace(chr(10),"<br>")}</div>',unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 5 — CROP SCANNER
# ══════════════════════════════════════════════
with tabs[5]:
    st.markdown('<div style="padding:1.5rem 2rem">', unsafe_allow_html=True)
    sc1,sc2=st.columns([1,1])
    with sc1:
        uploaded=st.file_uploader("UPLOAD PLANT IMAGE",type=["jpg","jpeg","png","webp"])
        crop_name_s=st.text_input("Crop Name",placeholder="Tomato, Rice, Wheat..."); scan_ctx=st.text_area("Describe Symptoms",placeholder="Yellow leaves, brown spots, wilting...",height=80)
    with sc2:
        if uploaded: st.image(uploaded,caption="UPLOADED SAMPLE",use_container_width=True)
        else: st.markdown("""<div style="width:100%;height:200px;background:rgba(0,200,255,0.02);border:1px dashed rgba(0,200,255,0.15);border-radius:6px;display:flex;align-items:center;justify-content:center;font-family:Share Tech Mono,monospace;font-size:0.6rem;color:rgba(0,120,150,0.5);text-align:center">◈ AWAITING PLANT SAMPLE<br><br>JPG · PNG · WEBP</div>""", unsafe_allow_html=True)
    if st.button("▶ SCAN PLANT HEALTH", type="primary"):
        if uploaded or scan_ctx or crop_name_s:
            with st.spinner("Scanning..."):
                if uploaded:
                    img_b=uploaded.read(); img_b64=base64.b64encode(img_b).decode(); ext=uploaded.name.split('.')[-1].lower(); mime="image/jpeg" if ext in ["jpg","jpeg"] else f"image/{ext}"
                    try:
                        resp=get_groq().chat.completions.create(model="llama-3.3-70b-versatile",max_tokens=1000,messages=[{"role":"user","content":[{"type":"text","text":f"Plant pathologist analysis. Crop: {crop_name_s or 'Unknown'}. Symptoms: {scan_ctx or 'See image'}. Location: {city_name},{country}. {now.strftime('%B')}, {cur['temperature_2m']:.1f}°C, {cur['relative_humidity_2m']}% RH. Provide: 1)Diagnosis with confidence 2)Severity 3)Treatment protocol 4)Prevention 5)Recovery timeline."},{"type":"image_url","image_url":{"url":f"data:{mime};base64,{img_b64}"}}]}])
                        result=resp.choices[0].message.content
                    except: result=ask_groq(f"Plant health: {crop_name_s or 'crop'}. Symptoms: {scan_ctx or 'unknown'}. {city_name},{now.strftime('%B')},{cur['temperature_2m']:.1f}°C,{cur['relative_humidity_2m']}% RH. Provide diagnosis, severity, treatment, prevention.")
                else: result=ask_groq(f"Plant health. Crop:{crop_name_s}. Symptoms:{scan_ctx}. {city_name},{now.strftime('%B')},{cur['temperature_2m']:.1f}°C,{cur['relative_humidity_2m']}% RH.",system="Expert plant pathologist for tropical and subtropical crops.")
            st.markdown(f'<div class="ai-box"><div class="ai-tag">CROP HEALTH SCAN REPORT</div>{result.replace(chr(10),"<br>")}</div>',unsafe_allow_html=True)
        else: st.warning("Please upload an image or describe symptoms.")
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 6 — FIELD AI
# ══════════════════════════════════════════════
with tabs[6]:
    st.markdown('<div style="padding:1.5rem 2rem">', unsafe_allow_html=True)
    st.markdown(f"""<div style="padding:0.7rem 1.1rem;background:rgba(0,200,255,0.03);border:1px solid rgba(0,200,255,0.08);border-radius:5px;margin-bottom:1rem;font-family:Share Tech Mono,monospace;font-size:0.6rem;color:rgba(0,130,170,0.55)">◈ CONTEXT · {city_name.upper()},{country.upper()} · {now.strftime('%B %Y')} · {cur['temperature_2m']:.1f}°C · {cur['relative_humidity_2m']}% RH · AQI {aq_cur.get('european_aqi','N/A')} · 7D RAIN: {total_rain:.0f}MM · ENV {es}/100 · AG {ag}/100</div>""", unsafe_allow_html=True)
    focus=st.text_input("CROP FOCUS (optional)",placeholder="e.g. Rice, Tomato, Groundnut, Wheat...")
    if "chat" not in st.session_state: st.session_state.chat=[]
    if not st.session_state.chat:
        sqc=st.columns(2)
        for i,q in enumerate(["What diseases to watch this month?","Water requirement for my crop this week?","Safe to spray pesticide in current conditions?","Create my 30-day farming schedule","Flood or drought risk for my location?","Which fertiliser should I apply now?"]):
            with sqc[i%2]:
                st.markdown(f"""<div style="padding:0.6rem 0.9rem;background:rgba(0,200,255,0.03);border:1px solid rgba(0,200,255,0.09);border-radius:4px;margin-bottom:0.5rem;font-size:0.72rem;color:rgba(0,150,190,0.65);font-family:Share Tech Mono,monospace">▸ {q}</div>""", unsafe_allow_html=True)
    for msg in st.session_state.chat:
        if msg["role"]=="user":
            st.markdown(f"""<div class="cu-r"><div class="cbub cu-b"><div class="cfrom cf-u">◈ YOU</div>{msg['content']}</div></div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="ca-r"><div class="cbub ca-b"><div class="cfrom cf-a">◈ AEROVEDA AI</div>{msg['content']}</div></div>""", unsafe_allow_html=True)
    user_in=st.chat_input("Ask the Field Intelligence System anything...")
    if user_in:
        st.session_state.chat.append({"role":"user","content":user_in})
        with st.spinner("Processing..."):
            reply=ask_groq_chat(st.session_state.chat,system=f"""Aeroveda Field Intelligence — expert agronomist with real-time data awareness.
LOCATION: {city_name},{region},{country} | {lat:.4f}°N,{lon:.4f}°E
DATE: {now.strftime('%d %B %Y')} | {'MONSOON SEASON' if (abs(lat)<25 and now.month in [6,7,8,9,10]) else 'CURRENT SEASON'}
WEATHER: {cur['temperature_2m']:.1f}°C | {cur['relative_humidity_2m']}% RH | {cur['wind_speed_10m']:.1f}km/h wind | UV {cur.get('uv_index',0) or 0:.0f} | {wdesc(cur['weather_code'])}
AIR: AQI {aq_cur.get('european_aqi','N/A')} | PM2.5 {aq_cur.get('pm2_5','N/A')} μg/m³
RAINFALL 7D: {total_rain:.0f}mm | ENV {es}/100 | AG {ag}/100
{'CROP FOCUS: '+focus if focus else ''}
Give precise, location-specific answers. Reference actual numbers. Account for current season and conditions.""",max_tokens=900)
        st.session_state.chat.append({"role":"assistant","content":reply}); st.rerun()
    if st.session_state.chat:
        if st.button("↺ CLEAR CHAT"): st.session_state.chat=[]; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# STATUS BAR
st.markdown(f"""
<div class="sbar">
  <div class="sb-i">🌍 <span style="color:rgba(0,150,180,0.4)">AEROVEDA OS</span> <span class="sb-v">v3.0</span></div>
  <div class="sb-i">📍 <span class="sb-v">{city_name.upper()}, {country.upper()}</span></div>
  <div class="sb-i">⏱ <span class="sb-v">{now.strftime('%H:%M:%S')}</span></div>
  <div class="sb-i">DATA STREAM <span class="sb-v" style="color:#22d4a0">● LIVE</span></div>
  <div class="sb-i">ENV <span class="sb-v" style="color:{ec}">{es}/100</span></div>
  <div class="sb-i">AQI <span class="sb-v">{aq_cur.get('european_aqi','N/A')}</span></div>
  <div class="sb-i">🔒 <span class="sb-v" style="color:#22d4a0">ENCRYPTED</span></div>
</div>
""", unsafe_allow_html=True)
