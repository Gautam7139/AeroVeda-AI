import streamlit as st
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

# ─── Data Fetchers ─────────────────────────────────────────────────────────────
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
        st.error(f"Weather unavailable — refresh to retry: {e}"); return None

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
    if s>=80: return "#00f5c3","OPTIMAL"
    elif s>=65: return "#4dffb4","GOOD"
    elif s>=45: return "#f5c842","MODERATE"
    elif s>=25: return "#ff8c3a","STRESSED"
    else: return "#ff3a5c","CRITICAL"

def bcol(v,g,b):
    if v<=g: return "#00f5c3"
    elif v<=b: return "#f5c842"
    else: return "#ff3a5c"

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
    pl=[p for p in daily["precipitation_sum"] if p is not None]
    total_7d=sum(pl); max_day=max(pl) if pl else 0
    max_temps=[t for t in daily["temperature_2m_max"] if t]
    min_temps=[t for t in daily["temperature_2m_min"] if t]
    max_wind=max((v for v in daily["wind_speed_10m_max"] if v),default=0)
    hum=cur.get("relative_humidity_2m",0)
    if aq_cur:
        aqi=aq_cur.get("european_aqi") or aq_cur.get("us_aqi")
        if aqi and aqi>100: alerts.append(("crisis","AIR QUALITY HAZARD",f"AQI {aqi} — Extremely hazardous. Halt outdoor farming operations."))
        elif aqi and aqi>80: alerts.append(("crisis","SEVERE POLLUTION",f"AQI {aqi} — Severe pollution. Sensitive crops under critical stress."))
        elif aqi and aqi>50: alerts.append(("warning","POOR AIR QUALITY",f"AQI {aqi} — Elevated pollution reducing crop productivity."))
    if max_day>80 or total_7d>200:
        alerts.append(("crisis","FLASH FLOOD RISK",f"Extreme rainfall: {max_day:.0f}mm peak, {total_7d:.0f}mm/7d. Waterlogging imminent."))
    elif max_day>40 or total_7d>120:
        alerts.append(("crisis","FLOOD PROBABILITY HIGH",f"{total_7d:.0f}mm weekly. Clear drainage channels immediately."))
    elif total_7d>60:
        alerts.append(("warning","HEAVY RAINFALL",f"{total_7d:.0f}mm forecast. Reduce irrigation, monitor drainage."))
    if is_monsoon and hum>85 and total_7d>30:
        alerts.append(("warning","MONSOON DISEASE RISK",f"Active monsoon: {hum}% RH. High fungal pressure. Apply preventive fungicide."))
    if total_7d<2 and cur.get("precipitation",0)<0.5:
        avg_max=sum(max_temps)/len(max_temps) if max_temps else 30
        if avg_max>28: alerts.append(("crisis","DROUGHT CONDITIONS",f"Near-zero rain ({total_7d:.1f}mm/7d), {avg_max:.1f}°C avg. Emergency irrigation required."))
        elif avg_max>18: alerts.append(("warning","LOW RAINFALL",f"Only {total_7d:.1f}mm forecast. Monitor soil moisture."))
    ex_heat=sum(1 for t in max_temps if t>42)
    hi_heat=sum(1 for t in max_temps if t>38)
    if ex_heat>=2: alerts.append(("crisis","EXTREME HEAT WAVE",f"{ex_heat} days >42°C. Increase irrigation 40–60%."))
    elif hi_heat>=3: alerts.append(("warning","HEAT STRESS",f"{hi_heat} days >38°C. Shift irrigation to morning/evening."))
    frost=sum(1 for t in min_temps if t<2)
    if frost>=1: alerts.append(("crisis","FROST WARNING",f"{frost} night(s) sub-2°C. Cover sensitive crops."))
    if max_wind>80: alerts.append(("crisis","STORM FORCE WINDS",f"Gusts to {max_wind:.0f}km/h. Secure infrastructure."))
    elif max_wind>50: alerts.append(("warning","HIGH WIND",f"Winds to {max_wind:.0f}km/h. Avoid spraying."))
    if not alerts: alerts.append(("safe","ALL SYSTEMS NOMINAL",f"No threats. {cur['temperature_2m']:.1f}°C, {hum}% RH, {total_7d:.0f}mm/7d. Conditions normal."))
    return alerts

def recommend_crops(w):
    c=w["current"]; t=c["temperature_2m"]; h=c["relative_humidity_2m"]
    pl=[p for p in w["daily"]["precipitation_sum"] if p is not None]
    ar=sum(pl)/len(pl) if pl else 0; result=[]
    if 20<=t<=38 and h>50:
        result.append(("🌾","RICE",95,"Optimal temp-humidity matrix","High water · 3–4 month cycle"))
        result.append(("🌿","SUGARCANE",88,"Heat-humidity match","Weekly irrigation · 10–12 months"))
    if 18<=t<=35:
        result.append(("🥜","GROUNDNUT",85,"Temperature envelope aligned","Sandy loam · dry finish required"))
        result.append(("🌽","MAIZE",82,"Thermophilic conditions","Moderate water · high N · 90d"))
    if t>=25 and h<70:
        result.append(("🍅","TOMATO",78,"Warm-dry matrix ideal","Drip irrigation · blight monitoring"))
        result.append(("🌶️","CHILLI",76,"Low humidity = low fungal risk","Potassium feed · drip preferred"))
    if t<22:
        result.append(("🥬","SPINACH",90,"Cool threshold optimal","Direct sow · 6–8 week harvest"))
        result.append(("🥕","CARROT",84,"Root growth favoured","Deep loose bed · 70d cycle"))
    if ar<3 and t>20:
        result.append(("🌻","SUNFLOWER",88,"Drought-tolerant","Minimal input · 80–95d"))
        result.append(("🫘","MOONG DAL",83,"Short-season legume","Sandy loam · 60–70d"))
    result.sort(key=lambda x:-x[2]); return result[:5]

def make_ring(score, color, sz=120, sw=8):
    v=score if score is not None else 0
    r=(sz/2)-sw; circ=2*math.pi*r; dash=(v/100)*circ
    gid=f"r{abs(hash(str(v)+color+str(sz)))%99999}"
    return (f'<svg width="{sz}" height="{sz}" viewBox="0 0 {sz} {sz}">'
            f'<defs>'
            f'<filter id="{gid}x"><feGaussianBlur stdDeviation="2.5" result="b"/>'
            f'<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
            f'<linearGradient id="{gid}g" x1="0%" y1="0%" x2="100%" y2="100%">'
            f'<stop offset="0%" style="stop-color:#00c8ff"/>'
            f'<stop offset="50%" style="stop-color:{color}"/>'
            f'<stop offset="100%" style="stop-color:#22d4a0;stop-opacity:0.7"/>'
            f'</linearGradient></defs>'
            f'<circle cx="{sz/2}" cy="{sz/2}" r="{r}" fill="none" stroke="rgba(0,200,255,0.08)" stroke-width="{sw}"/>'
            f'<circle cx="{sz/2}" cy="{sz/2}" r="{r}" fill="none" stroke="url(#{gid}g)" stroke-width="{sw}"'
            f' stroke-linecap="round" stroke-dasharray="{dash:.1f} {circ:.1f}"'
            f' transform="rotate(-90 {sz/2} {sz/2})" filter="url(#{gid}x)"/>'
            f'</svg>')

def mini_ring(score, color="#00c8ff", sz=60):
    r=(sz/2)-5; circ=2*math.pi*r; dash=(score/100)*circ
    return (f'<svg width="{sz}" height="{sz}" viewBox="0 0 {sz} {sz}">'
            f'<circle cx="{sz/2}" cy="{sz/2}" r="{r}" fill="none" stroke="rgba(0,200,255,0.08)" stroke-width="4"/>'
            f'<circle cx="{sz/2}" cy="{sz/2}" r="{r}" fill="none" stroke="{color}" stroke-width="4"'
            f' stroke-linecap="round" stroke-dasharray="{dash:.1f} {circ:.1f}" transform="rotate(-90 {sz/2} {sz/2})"/>'
            f'<text x="{sz/2}" y="{sz/2+4}" text-anchor="middle" font-family="Orbitron,sans-serif"'
            f' font-size="10" font-weight="800" fill="{color}">{score}</text>'
            f'</svg>')

# ══════════════════════════════════════════════════════════════════════
# CITY INPUT — Clean, simple, always at top
# ══════════════════════════════════════════════════════════════════════
# Inject CSS first (before any widgets)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Exo+2:wght@200;300;400;500;600;700&family=Share+Tech+Mono&display=swap');

*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body,[class*="css"]{font-family:'Exo 2',sans-serif;background:#030b10!important;color:#b0e8f0}

/* ── PARTICLE CANVAS (background) ── */
#particle-bg{position:fixed;inset:0;z-index:0;pointer-events:none}

.stApp{
  background:
    radial-gradient(ellipse 80% 60% at 10% 10%, rgba(0,220,180,0.06) 0%,transparent 50%),
    radial-gradient(ellipse 60% 50% at 90% 90%, rgba(0,160,255,0.05) 0%,transparent 45%),
    #030b10!important;
  overflow-x:hidden;
}
.stApp::before{
  content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
  background-image:
    linear-gradient(rgba(0,220,180,0.018) 1px,transparent 1px),
    linear-gradient(90deg,rgba(0,220,180,0.018) 1px,transparent 1px);
  background-size:55px 55px;
}
.main .block-container{
  padding:0 0 4rem!important;max-width:100%!important;
  position:relative;z-index:1;
}

/* ── LOCATION BAR ── */
.loc-bar{
  background:linear-gradient(90deg,rgba(0,15,25,0.98),rgba(0,10,18,0.99));
  border-bottom:1px solid rgba(0,220,180,0.12);
  padding:10px 2rem;
  display:flex;align-items:center;gap:1rem;
  position:relative;overflow:hidden;
}
.loc-bar::after{
  content:'';position:absolute;bottom:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,#00f5c3,#00c8ff,#00f5c3,transparent);
  animation:lb-sweep 5s ease-in-out infinite;opacity:0.5;
}
@keyframes lb-sweep{0%,100%{opacity:0.3}50%{opacity:0.7}}
.loc-label{
  font-family:'Orbitron',sans-serif;font-size:0.52rem;font-weight:700;
  letter-spacing:0.22em;color:rgba(0,200,180,0.55);white-space:nowrap;
}

/* ── HERO ── */
.hero-wrap{
  position:relative;min-height:340px;
  display:flex;align-items:center;
  padding:2.5rem 2.5rem;
  overflow:hidden;
}
/* Animated leaf particles */
.hero-wrap::before{
  content:'';position:absolute;inset:0;
  background:
    radial-gradient(ellipse 70% 80% at 70% 50%,rgba(0,220,180,0.07) 0%,transparent 60%),
    radial-gradient(ellipse 50% 40% at 20% 30%,rgba(0,160,255,0.05) 0%,transparent 55%);
  animation:hero-pulse 8s ease-in-out infinite;
}
@keyframes hero-pulse{0%,100%{opacity:0.6}50%{opacity:1}}

.hero-title{
  font-family:'Orbitron',sans-serif;
  font-size:clamp(2rem,4vw,3.5rem);
  font-weight:900;color:#fff;
  line-height:1.05;letter-spacing:-0.01em;
  text-shadow:0 0 50px rgba(0,220,180,0.3);
  position:relative;z-index:2;
}
.hero-title .hl{
  background:linear-gradient(135deg,#00f5c3 0%,#00c8ff 50%,#4dffcc 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}
.hero-sub{
  font-size:0.9rem;color:rgba(0,180,200,0.6);
  margin-top:0.6rem;font-weight:300;letter-spacing:0.04em;
  position:relative;z-index:2;
}
.hero-right{position:relative;z-index:2;text-align:right}
.kpi-row{
  display:flex;flex-direction:column;gap:6px;align-items:flex-end;
}
.kpi-item{
  display:flex;align-items:center;gap:10px;
  font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:rgba(0,160,190,0.5);
}
.kpi-val{font-family:'Orbitron',sans-serif;font-size:1.05rem;font-weight:800}

/* ── FLOATING LEAF PARTICLES (CSS) ── */
.leaf-container{position:absolute;inset:0;overflow:hidden;pointer-events:none;z-index:1}
.leaf{
  position:absolute;
  font-size:1.2rem;
  opacity:0;
  animation:leaf-fall linear infinite;
}
@keyframes leaf-fall{
  0%{transform:translateY(-60px) rotate(0deg) translateX(0);opacity:0}
  10%{opacity:0.6}
  90%{opacity:0.3}
  100%{transform:translateY(380px) rotate(360deg) translateX(40px);opacity:0}
}

/* ── TICKER ── */
.ticker{
  padding:7px 0;background:rgba(2,6,14,0.98);
  border-bottom:1px solid rgba(0,220,180,0.07);
  overflow:hidden;white-space:nowrap;position:relative;
}
.ticker::before,.ticker::after{content:'';position:absolute;top:0;bottom:0;width:80px;z-index:2}
.ticker::before{left:0;background:linear-gradient(90deg,rgba(2,6,14,0.98),transparent)}
.ticker::after{right:0;background:linear-gradient(-90deg,rgba(2,6,14,0.98),transparent)}
.ticker-inner{
  display:inline-block;animation:tick 50s linear infinite;
  font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:rgba(0,160,180,0.5);
  letter-spacing:0.07em;
}
@keyframes tick{0%{transform:translateX(100vw)}100%{transform:translateX(-100%)}}
.tsep{color:#00f5c3;margin:0 14px;opacity:0.4}

/* ── SCORE GRID ── */
.score-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:rgba(0,220,180,0.05)}
.score-cell{
  background:linear-gradient(135deg,rgba(0,18,28,0.95),rgba(0,8,16,0.98));
  padding:1.6rem 1rem;text-align:center;position:relative;overflow:hidden;transition:all 0.3s;
}
.score-cell:hover{background:rgba(0,22,34,0.97);transform:translateY(-2px);box-shadow:0 8px 30px rgba(0,220,180,0.08)}
.score-cell::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(0,220,180,0.4),rgba(0,200,255,0.25),transparent)}
.ring-host{position:relative;width:120px;height:120px;margin:0 auto}
.ring-host svg{width:120px;height:120px}
.ring-center{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;width:70px}
.ring-num{font-family:'Orbitron',sans-serif;font-size:1.8rem;font-weight:800;color:#fff;line-height:1}
.ring-den{font-family:'Share Tech Mono',monospace;font-size:0.5rem;color:rgba(0,160,190,0.55);margin-top:2px}
.score-lbl{font-family:'Orbitron',sans-serif;font-size:0.52rem;font-weight:700;letter-spacing:0.16em;color:rgba(0,160,190,0.65);margin-top:10px}
.score-grade{font-family:'Orbitron',sans-serif;font-size:0.7rem;font-weight:700;letter-spacing:0.09em;margin-top:3px}
.score-hint{font-size:0.55rem;color:rgba(0,100,130,0.5);margin-top:3px;font-family:'Share Tech Mono',monospace}

/* ── SECTION LABELS ── */
.sec-label{
  display:flex;align-items:center;gap:14px;
  padding:0.8rem 2rem;
  background:rgba(0,8,14,0.6);
  border-bottom:1px solid rgba(0,220,180,0.07);
}
.sl-tag{
  font-family:'Orbitron',sans-serif;font-size:0.54rem;font-weight:700;
  letter-spacing:0.18em;color:#030b10;
  background:linear-gradient(135deg,#00f5c3,#00c8ff);
  padding:4px 12px;border-radius:2px;
  box-shadow:0 0 12px rgba(0,220,180,0.2);
}
.sl-line{flex:1;height:1px;background:linear-gradient(90deg,rgba(0,220,180,0.25),rgba(0,200,255,0.1),transparent)}
.sl-code{font-family:'Share Tech Mono',monospace;font-size:0.53rem;color:rgba(0,180,200,0.2)}

/* ── GLASS CARDS ── */
.gc{
  background:linear-gradient(135deg,rgba(0,18,28,0.93),rgba(0,8,16,0.97));
  border:1px solid rgba(0,220,180,0.08);
  position:relative;overflow:hidden;transition:all 0.35s;
}
.gc:hover{border-color:rgba(0,220,180,0.22);box-shadow:0 0 30px rgba(0,220,180,0.06)}
.gc::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(0,220,180,0.4),rgba(0,200,255,0.2),transparent)}
.gcp{padding:1.3rem 1.5rem}
.gct{font-family:'Orbitron',sans-serif;font-size:0.54rem;font-weight:700;letter-spacing:0.18em;
  color:rgba(0,170,190,0.65);margin-bottom:0.9rem;text-transform:uppercase}
.gct::before{content:'◈ ';color:rgba(0,220,180,0.5)}

/* ── DATA VALUES ── */
.dv-l{font-family:'Share Tech Mono',monospace;font-size:0.54rem;letter-spacing:0.15em;
  color:rgba(0,130,170,0.6);margin-bottom:4px;text-transform:uppercase}
.dv-n{font-family:'Orbitron',sans-serif;font-size:1.9rem;font-weight:700;color:#fff;line-height:1;
  text-shadow:0 0 12px rgba(0,220,180,0.15)}
.dv-u{font-size:0.73rem;color:#00f5c3;margin-left:3px;font-weight:300}
.dv-s{font-size:0.63rem;color:rgba(0,110,140,0.55);margin-top:4px;font-family:'Share Tech Mono',monospace}

/* ── WEATHER WIDGET ── */
.wx-hero{
  background:linear-gradient(135deg,rgba(0,20,35,0.95),rgba(0,10,20,0.98));
  border:1px solid rgba(0,220,180,0.1);
  border-radius:0;position:relative;overflow:hidden;
  padding:2rem 2rem;
  display:flex;align-items:center;justify-content:space-between;
  gap:2rem;
}
.wx-hero::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,transparent,#00f5c3,#00c8ff,transparent)}
.wx-temp{
  font-family:'Orbitron',sans-serif;font-size:5rem;font-weight:900;
  color:#fff;line-height:1;
  text-shadow:0 0 40px rgba(0,220,180,0.4),0 0 80px rgba(0,220,180,0.1);
}
.wx-unit{font-size:2rem;color:#00f5c3;vertical-align:super}
.wx-condition{font-size:0.9rem;color:rgba(0,200,220,0.7);margin-top:0.4rem;font-family:'Share Tech Mono',monospace;letter-spacing:0.15em}
.wx-loc{font-family:'Orbitron',sans-serif;font-size:1.2rem;font-weight:700;color:#fff;margin-bottom:0.3rem}
.wx-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem}
.wx-item{text-align:center}
.wx-icon{font-size:1.5rem;margin-bottom:4px}
.wx-val{font-family:'Orbitron',sans-serif;font-size:0.9rem;font-weight:700;color:#fff}
.wx-lbl{font-family:'Share Tech Mono',monospace;font-size:0.52rem;color:rgba(0,160,190,0.5);letter-spacing:0.12em}

/* ── SATELLITE IMAGE CARD ── */
.sat-card{
  background:linear-gradient(135deg,rgba(0,15,25,0.97),rgba(0,8,16,0.99));
  border:1px solid rgba(0,220,180,0.1);
  position:relative;overflow:hidden;
}
.sat-inner{
  width:100%;height:220px;position:relative;overflow:hidden;
  background:linear-gradient(135deg,#000810,#001428,#000c18);
}
.sat-grid{
  position:absolute;inset:0;
  background-image:
    linear-gradient(rgba(0,220,180,0.06) 1px,transparent 1px),
    linear-gradient(90deg,rgba(0,220,180,0.06) 1px,transparent 1px);
  background-size:20px 20px;
}
/* Animated satellite ping */
.sat-ping{
  position:absolute;top:50%;left:50%;
  transform:translate(-50%,-50%);
}
.sat-ping-ring{
  position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
  border-radius:50%;border:1px solid rgba(0,220,180,0.4);
  animation:ping-expand 3s ease-out infinite;
}
@keyframes ping-expand{
  0%{width:10px;height:10px;opacity:1}
  100%{width:200px;height:200px;opacity:0}
}
.sat-dot{
  width:10px;height:10px;border-radius:50%;
  background:#00f5c3;box-shadow:0 0 12px #00f5c3,0 0 24px rgba(0,220,180,0.4);
  position:relative;z-index:2;
}
/* Data blips on grid */
.sat-blip{
  position:absolute;width:4px;height:4px;border-radius:50%;
  animation:blip-blink 2s ease-in-out infinite;
}
@keyframes blip-blink{0%,100%{opacity:0}50%{opacity:1}}

/* ── POLLUTANT BARS ── */
.pol{margin-bottom:1rem}
.pol-h{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:5px}
.pol-n{font-family:'Share Tech Mono',monospace;font-size:0.57rem;letter-spacing:0.1em;color:rgba(0,160,190,0.65)}
.pol-v{font-family:'Orbitron',sans-serif;font-size:0.8rem;font-weight:600}
.pol-t{height:3px;background:rgba(0,220,180,0.06);border-radius:99px;overflow:visible;position:relative}
.pol-f{height:3px;border-radius:99px;position:relative;transition:width 1s ease}
.pol-f::after{content:'';position:absolute;right:-1px;top:-3px;width:9px;height:9px;border-radius:50%;
  background:currentColor;box-shadow:0 0 8px currentColor,0 0 16px currentColor}

/* ── ALERTS ── */
.alert{display:flex;gap:12px;padding:0.9rem 1.2rem;border-radius:6px;margin-bottom:0.6rem;position:relative}
.alert::before{content:'';position:absolute;left:0;top:0;bottom:0;width:3px;border-radius:3px 0 0 3px}
.a-crisis{background:rgba(255,40,80,0.06);border:1px solid rgba(255,40,80,0.2)}
.a-crisis::before{background:linear-gradient(180deg,#ff2850,#cc0020)}
.a-warning{background:rgba(245,200,66,0.06);border:1px solid rgba(245,200,66,0.18)}
.a-warning::before{background:linear-gradient(180deg,#f5c842,#c09a00)}
.a-safe{background:rgba(0,220,180,0.05);border:1px solid rgba(0,220,180,0.15)}
.a-safe::before{background:linear-gradient(180deg,#00f5c3,#00c8a0)}
.a-icon{font-size:1.1rem;flex-shrink:0;padding-top:1px}
.a-title{font-family:'Orbitron',sans-serif;font-size:0.57rem;font-weight:700;letter-spacing:0.14em;margin-bottom:4px}
.a-crisis .a-title{color:#ff6878}.a-warning .a-title{color:#f5d060}.a-safe .a-title{color:#00f5c3}
.a-msg{font-size:0.8rem;line-height:1.6}
.a-crisis .a-msg{color:#ffb0bc}.a-warning .a-msg{color:#fdeaa0}.a-safe .a-msg{color:#9ef5d8}

/* ── CROP CARDS ── */
.cc{display:flex;align-items:center;gap:1.1rem;padding:0.9rem 1.3rem;
  background:linear-gradient(135deg,rgba(0,18,28,0.88),rgba(0,8,16,0.94));
  border:1px solid rgba(0,220,180,0.09);border-left:3px solid rgba(0,220,180,0.4);
  border-radius:6px;margin-bottom:0.6rem;transition:all 0.3s}
.cc:hover{border-color:rgba(0,220,180,0.3);transform:translateX(5px);box-shadow:0 4px 25px rgba(0,220,180,0.07)}
.cc-em{font-size:2rem;flex-shrink:0}
.cc-bd{flex:1}
.cc-nm{font-family:'Orbitron',sans-serif;font-size:0.85rem;font-weight:700;color:#e8fff4;letter-spacing:0.04em}
.cc-rs{font-size:0.73rem;color:rgba(0,200,180,0.75);margin-top:3px}
.cc-cr{font-size:0.62rem;color:rgba(0,130,110,0.6);margin-top:4px;font-family:'Share Tech Mono',monospace}

/* ── CHAT ── */
.cu-r{display:flex;justify-content:flex-end;margin-bottom:0.6rem}
.ca-r{display:flex;justify-content:flex-start;margin-bottom:0.6rem}
.cbub{padding:0.85rem 1.1rem;border-radius:8px;font-size:0.83rem;line-height:1.7;max-width:82%}
.cu-b{background:rgba(0,220,180,0.07);border:1px solid rgba(0,220,180,0.18);color:#d0fff0;border-radius:8px 8px 2px 8px}
.ca-b{background:rgba(0,10,18,0.97);border:1px solid rgba(0,220,180,0.09);color:#a8f5e8;border-radius:8px 8px 8px 2px}
.cfrom{font-family:'Share Tech Mono',monospace;font-size:0.52rem;letter-spacing:0.18em;margin-bottom:5px}
.cf-u{text-align:right;color:#00f5c3}.cf-a{color:#00c8ff}

/* ── AI BOX ── */
.ai-box{background:rgba(0,6,12,0.98);border:1px solid rgba(0,220,180,0.12);
  border-radius:8px;padding:1.6rem;margin-top:1rem;
  color:#a8f5e0;line-height:1.9;font-size:0.86rem;position:relative}
.ai-tag{position:absolute;top:-10px;left:16px;background:#030b10;padding:0 10px;
  font-family:'Orbitron',sans-serif;font-size:0.48rem;letter-spacing:0.2em;font-weight:700;
  background:linear-gradient(135deg,#00f5c3,#00c8ff);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}

/* ── MAP ── */
.map-wrap{border:1px solid rgba(0,220,180,0.1);position:relative;overflow:hidden}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"]{
  background:rgba(2,6,14,0.98)!important;
  border-bottom:1px solid rgba(0,220,180,0.08)!important;
  gap:0!important;padding:0 2rem!important;
}
.stTabs [data-baseweb="tab"]{
  font-family:'Orbitron',sans-serif!important;font-size:0.53rem!important;
  letter-spacing:0.14em!important;text-transform:uppercase!important;
  color:rgba(0,170,190,0.38)!important;padding:0.9rem 1.3rem!important;
  background:transparent!important;border:none!important;font-weight:600!important;
}
.stTabs [aria-selected="true"]{
  color:#00f5c3!important;border-bottom:2px solid #00f5c3!important;
  background:rgba(0,220,180,0.03)!important;text-shadow:0 0 10px rgba(0,220,180,0.5)!important;
}
.stTabs [data-baseweb="tab-panel"]{padding:0!important;background:transparent!important}

/* ── INPUTS ── */
.stTextInput input{
  background:rgba(0,10,20,0.92)!important;border:1px solid rgba(0,220,180,0.18)!important;
  border-radius:6px!important;color:#c8f0f8!important;
  font-family:'Exo 2',sans-serif!important;font-size:0.95rem!important;
}
.stTextInput input:focus{border-color:rgba(0,220,180,0.5)!important;box-shadow:0 0 0 2px rgba(0,220,180,0.07)!important}
.stTextInput label{color:rgba(0,170,190,0.6)!important;font-family:'Share Tech Mono',monospace!important;font-size:0.56rem!important;letter-spacing:0.18em!important}
.stTextArea textarea{background:rgba(0,10,20,0.92)!important;border:1px solid rgba(0,220,180,0.16)!important;border-radius:6px!important;color:#c8f0f8!important}

/* ── BUTTONS ── */
.stButton button{
  background:rgba(0,220,180,0.06)!important;border:1px solid rgba(0,220,180,0.22)!important;
  color:#00f5c3!important;border-radius:4px!important;
  font-family:'Orbitron',sans-serif!important;font-size:0.53rem!important;
  letter-spacing:0.13em!important;font-weight:700!important;transition:all 0.2s!important;
}
.stButton button:hover{background:rgba(0,220,180,0.14)!important;border-color:#00f5c3!important;
  color:#fff!important;box-shadow:0 0 20px rgba(0,220,180,0.18)!important}
button[kind="primary"]{
  background:linear-gradient(135deg,rgba(0,100,80,0.6),rgba(0,200,160,0.4))!important;
  border:1px solid #00f5c3!important;color:#fff!important;
}

/* ── SELECT / SLIDER ── */
[data-baseweb="select"]>div{background:rgba(0,10,20,0.92)!important;border-color:rgba(0,220,180,0.16)!important;color:#c8f0f8!important;border-radius:6px!important}
.stSlider [data-testid="stThumbValue"]{color:#00f5c3!important;font-family:'Share Tech Mono',monospace!important}

/* ── DATAFRAME ── */
[data-testid="stDataFrameResizable"]{border:1px solid rgba(0,220,180,0.08)!important;border-radius:6px!important}
[data-testid="stFileUploader"]{background:rgba(0,10,20,0.8)!important;border:1px dashed rgba(0,220,180,0.18)!important;border-radius:8px!important}

/* ── STATUS BAR ── */
.sbar{display:flex;align-items:center;justify-content:space-between;
  padding:7px 2rem;background:rgba(2,6,14,0.99);
  border-top:1px solid rgba(0,220,180,0.07);
  font-family:'Share Tech Mono',monospace;font-size:0.57rem;color:rgba(0,130,160,0.5)}
.sb-i{display:flex;align-items:center;gap:5px;white-space:nowrap}
.sb-v{color:#00f5c3;font-weight:700}
.live-dot{width:6px;height:6px;border-radius:50%;background:#00f5c3;
  box-shadow:0 0 8px #00f5c3;display:inline-block;margin-right:4px;
  animation:ld 2s ease-in-out infinite}
@keyframes ld{0%,100%{opacity:1}50%{opacity:0.1}}

/* ── SIDEBAR ── */
[data-testid="stSidebar"]{background:rgba(0,5,10,0.99)!important;border-right:1px solid rgba(0,220,180,0.08)!important}

/* ── MISC ── */
#MainMenu,footer,header{visibility:hidden}
::-webkit-scrollbar{width:3px}
::-webkit-scrollbar-thumb{background:linear-gradient(180deg,#00f5c3,#00c8ff);border-radius:99px}
.stSpinner>div{border-top-color:#00f5c3!important}
</style>
""", unsafe_allow_html=True)

# ── City input ─────────────────────────────────────────────────────────────────
st.markdown('<div class="loc-bar"><span class="loc-label">◈ LOCATION NODE</span>', unsafe_allow_html=True)
city_col, _ = st.columns([3,1])
with city_col:
    city_input = st.text_input(
        "city",
        value=st.session_state.get("city","Bengaluru"),
        placeholder="Type city — Delhi, Mumbai, Chennai, Hyderabad, Pune...",
        label_visibility="collapsed"
    )
    if city_input:
        st.session_state["city"] = city_input
st.markdown('</div>', unsafe_allow_html=True)

# ── Geocode & Fetch ─────────────────────────────────────────────────────────────
active_city = st.session_state.get("city","Bengaluru")
geo = geocode(active_city)
if not geo:
    st.error(f"⚠ Location '{active_city}' not found. Check spelling and try again.")
    st.stop()

lat, lon, country, city_name, region = geo
weather = fetch_weather(lat, lon)
if not weather: st.stop()

aq = fetch_aq(lat, lon)
cur = weather["current"]
daily = weather["daily"]
aq_cur = aq.get("current",{}) if aq else {}
ws = w_score(weather); ps = p_score(aq); es = e_score(ws,ps)
ag = max(0,min(100,round(es*0.7+ws*0.3)))
now = datetime.now()
total_rain = sum(p for p in daily["precipitation_sum"] if p)
ec, eg = grade(es)

# Compute crisis list once here so it's available everywhere
crisis_data = detect_crises(weather, aq_cur, lat)
has_crisis = any(c[0]=="crisis" for c in crisis_data)
has_warning = any(c[0]=="warning" for c in crisis_data)

# ── TOP BAR (logo + location only, no dummy buttons) ──────────────────────────
st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
  padding:0 2rem;height:52px;
  background:rgba(2,6,14,0.99);border-bottom:1px solid rgba(0,220,180,0.1);
  position:relative;">
  <div style="position:absolute;bottom:0;left:0;right:0;height:1px;
    background:linear-gradient(90deg,transparent,#00f5c3,#00c8ff,transparent);opacity:0.5"></div>
  <div style="font-family:'Orbitron',sans-serif;font-size:1.3rem;font-weight:900;
    letter-spacing:0.14em;
    background:linear-gradient(135deg,#00f5c3,#00c8ff,#4dffcc);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
    filter:drop-shadow(0 0 8px rgba(0,220,180,0.4))">AEROVEDA</div>
  <div style="display:flex;align-items:center;gap:20px;font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:rgba(0,160,190,0.5)">
    <span><span class="live-dot"></span>LIVE DATA</span>
    <span style="color:rgba(0,140,170,0.35)">|</span>
    <span style="color:rgba(0,180,200,0.6)">{city_name.upper()}, {country.upper()}</span>
    <span style="color:rgba(0,140,170,0.35)">|</span>
    <span>{now.strftime('%H:%M')} UTC</span>
    <span style="color:rgba(0,140,170,0.35)">|</span>
    <span style="color:{'#ff3a5c' if has_crisis else '#f5c842' if has_warning else '#00f5c3'}">
      {'⚠ ALERTS' if has_crisis or has_warning else '✓ NOMINAL'}
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── HERO with animated leaves ──────────────────────────────────────────────────
leaves = "".join([
    f'<div class="leaf" style="left:{5+i*9}%;animation-delay:{i*0.7}s;animation-duration:{4+i*0.5}s;font-size:{0.9+0.4*(i%3)}rem">'
    + ["🌿","🍃","🌱","🌾","🍀"][i%5] + '</div>'
    for i in range(11)
])

status_color = "#ff3a5c" if has_crisis else "#f5c842" if has_warning else "#00f5c3"
status_text = "⚠ ALERTS ACTIVE" if has_crisis or has_warning else "✓ OPTIMAL"

st.markdown(f"""
<div class="hero-wrap">
  <div class="leaf-container">{leaves}</div>
  <div style="position:relative;z-index:2;flex:1">
    <div class="hero-title">INTELLIGENCE<br><span class="hl">BEYOND PLANET</span></div>
    <div class="hero-sub">Real-time agricultural intelligence · {city_name}, {country} · AI-powered environmental analytics</div>
  </div>
  <div class="hero-right">
    <div class="kpi-row">
      <div class="kpi-item">
        <span style="color:rgba(0,140,160,0.4)">STATUS</span>
        <span class="kpi-val" style="color:{status_color}">{status_text}</span>
      </div>
      <div class="kpi-item">
        <span style="color:rgba(0,140,160,0.4)">ENV SCORE</span>
        <span class="kpi-val" style="color:{ec}">{es}<span style="font-size:0.55rem;color:rgba(0,140,160,0.4)">/100</span></span>
      </div>
      <div class="kpi-item">
        <span style="color:rgba(0,140,160,0.4)">AG POTENTIAL</span>
        <span class="kpi-val" style="color:#4dffcc">{ag}%</span>
      </div>
      <div class="kpi-item">
        <span style="color:rgba(0,140,160,0.4)">{lat:.3f}°{'N' if lat>=0 else 'S'} {lon:.3f}°{'E' if lon>=0 else 'W'}</span>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── TICKER ──────────────────────────────────────────────────────────────────────
pm25v = float(aq_cur.get("pm2_5",0) or 0)
ti = [f"TEMP: {cur['temperature_2m']:.1f}°C", f"HUMIDITY: {cur['relative_humidity_2m']}%",
      f"WIND: {cur['wind_speed_10m']:.1f}km/h", f"UV: {cur.get('uv_index',0) or 0:.0f}",
      f"PM2.5: {pm25v:.1f}μg/m³", f"AQI: {aq_cur.get('european_aqi','N/A')}",
      f"7D RAIN: {total_rain:.0f}mm", f"CONDITIONS: {wdesc(cur['weather_code']).upper()}",
      f"ENV SCORE: {es}/100", f"AG POTENTIAL: {ag}/100",
      f"LOCATION: {city_name.upper()}, {country.upper()}", f"{now.strftime('%d %b %Y')}"]
sep='<span class="tsep">//</span>'
ts = sep.join(ti)
st.markdown(f'<div class="ticker"><div class="ticker-inner">{ts}&nbsp;&nbsp;&nbsp;&nbsp;{ts}</div></div>', unsafe_allow_html=True)

# ── SCORE ROW ──────────────────────────────────────────────────────────────────
st.markdown('<div class="score-grid">', unsafe_allow_html=True)
sc = st.columns(4)
for col, score, name, hint in [
    (sc[0],ps,"POLLUTION INDEX","Higher = Cleaner"),
    (sc[1],ws,"WEATHER SCORE","Temp · Wind · UV"),
    (sc[2],es,"ENV SCORE","55% Wx + 45% AQ"),
    (sc[3],ag,"AG POTENTIAL","Farm Suitability"),
]:
    v = score if score is not None else 0
    color, gr = grade(v)
    disp = str(score) if score is not None else "N/A"
    with col:
        st.markdown(f"""
<div class="score-cell">
  <div class="ring-host">{make_ring(v,color)}
    <div class="ring-center">
      <div class="ring-num" style="color:{color};text-shadow:0 0 12px {color}80">{disp}</div>
      <div class="ring-den">/ 100</div>
    </div>
  </div>
  <div class="score-lbl">{name}</div>
  <div class="score-grade" style="color:{color}">{gr}</div>
  <div class="score-hint">{hint}</div>
</div>""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── TABS (functional only) ────────────────────────────────────────────────────
tabs = st.tabs(["🌤 WEATHER","💨 AIR QUALITY","⚠ CRISIS INTEL","🌱 CROP ENGINE","🔬 SIMULATION","🔍 CROP SCANNER","◈ FIELD AI"])

# ══════════════════════════════════════════
# TAB 0 — WEATHER (rich visual)
# ══════════════════════════════════════════
with tabs[0]:
    # Big weather hero
    wx_icon = {"Clear Sky":"☀️","Mainly Clear":"🌤","Partly Cloudy":"⛅","Overcast":"☁️",
               "Fog":"🌫","Drizzle":"🌦","Light Drizzle":"🌦","Heavy Drizzle":"🌧",
               "Slight Rain":"🌧","Moderate Rain":"🌧","Heavy Rain":"⛈",
               "Rain Showers":"🌦","Moderate Showers":"🌧","Violent Showers":"⛈",
               "Thunderstorm":"⛈","Thunderstorm+Hail":"⛈",
               "Slight Snow":"❄️","Moderate Snow":"🌨","Heavy Snow":"🌨"}.get(wdesc(cur["weather_code"]),"🌡")

    st.markdown(f"""
<div class="wx-hero">
  <div>
    <div style="font-size:4rem;margin-bottom:0.5rem">{wx_icon}</div>
    <div class="wx-temp">{cur['temperature_2m']:.0f}<span class="wx-unit">°C</span></div>
    <div class="wx-condition">{wdesc(cur['weather_code']).upper()}</div>
  </div>
  <div style="flex:1;padding:0 2rem">
    <div class="wx-loc">{city_name}, {country}</div>
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:rgba(0,160,190,0.5);margin-bottom:1rem">
      {lat:.3f}°{'N' if lat>=0 else 'S'} · {lon:.3f}°{'E' if lon>=0 else 'W'} · Updated {now.strftime('%H:%M')}
    </div>
    <div style="display:flex;gap:1.5rem;flex-wrap:wrap">
      <div><div class="dv-l">FEELS LIKE</div><div style="font-family:Orbitron,sans-serif;font-size:1.4rem;font-weight:700;color:#fff">{cur['apparent_temperature']:.1f}°C</div></div>
      <div><div class="dv-l">HUMIDITY</div><div style="font-family:Orbitron,sans-serif;font-size:1.4rem;font-weight:700;color:#00c8ff">{cur['relative_humidity_2m']}%</div></div>
      <div><div class="dv-l">WIND</div><div style="font-family:Orbitron,sans-serif;font-size:1.4rem;font-weight:700;color:#4dffcc">{cur['wind_speed_10m']:.0f} km/h</div></div>
      <div><div class="dv-l">UV INDEX</div><div style="font-family:Orbitron,sans-serif;font-size:1.4rem;font-weight:700;color:#f5c842">{cur.get('uv_index',0) or 0:.0f}</div></div>
      <div><div class="dv-l">PRECIP</div><div style="font-family:Orbitron,sans-serif;font-size:1.4rem;font-weight:700;color:#00c8ff">{cur['precipitation']:.1f} mm</div></div>
      <div><div class="dv-l">PRESSURE</div><div style="font-family:Orbitron,sans-serif;font-size:1.4rem;font-weight:700;color:#fff">{cur['surface_pressure']:.0f} hPa</div></div>
    </div>
  </div>
  <div style="text-align:center;min-width:120px">
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.55rem;color:rgba(0,160,190,0.5);letter-spacing:0.15em;margin-bottom:8px">CLOUD COVER</div>
    <div style="font-family:'Orbitron',sans-serif;font-size:2.5rem;font-weight:800;color:#fff">{cur['cloud_cover']}<span style="font-size:1rem;color:#00f5c3">%</span></div>
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.55rem;color:rgba(0,160,190,0.5);letter-spacing:0.15em;margin-top:12px">7D RAIN</div>
    <div style="font-family:'Orbitron',sans-serif;font-size:1.8rem;font-weight:800;color:#00c8ff">{total_rain:.0f}<span style="font-size:0.9rem">mm</span></div>
  </div>
</div>
""", unsafe_allow_html=True)

    # Animated satellite-feed style panel
    import streamlit.components.v1 as components

    sat_blips = "".join([
        f'<div class="sat-blip" style="left:{10+i*12}%;top:{15+((i*31)%70)}%;background:{"#00f5c3" if i%3==0 else "#00c8ff" if i%3==1 else "#f5c842"};animation-delay:{i*0.4}s"></div>'
        for i in range(14)
    ])
    sat_html = (
        "<div style='width:100%;height:220px;background:linear-gradient(135deg,#000810,#001428,#000c18);"
        "position:relative;overflow:hidden;font-family:Orbitron,monospace'>"
        "<div style='position:absolute;inset:0;background-image:linear-gradient(rgba(0,220,180,0.06) 1px,transparent 1px),"
        "linear-gradient(90deg,rgba(0,220,180,0.06) 1px,transparent 1px);background-size:22px 22px'></div>"
        + sat_blips +
        "<div style='position:absolute;top:50%;left:50%;transform:translate(-50%,-50%)'>"
        "<div style='position:relative;width:10px;height:10px'>"
        "<div style='width:10px;height:10px;border-radius:50%;background:#00f5c3;"
        "box-shadow:0 0 12px #00f5c3,0 0 24px rgba(0,220,180,0.4);position:relative;z-index:2'></div>"
        "</div>"
        "</div>"
        "<div style='position:absolute;top:50%;left:50%;transform:translate(-50%,-50%)'>"
        "<div style='border-radius:50%;border:1px solid rgba(0,220,180,0.35);animation:ping-expand 2.5s ease-out infinite;position:absolute;top:50%;left:50%;transform:translate(-50%,-50%)'></div>"
        "</div>"
        "<div style='position:absolute;bottom:10px;left:14px;font-size:9px;color:rgba(0,220,180,0.55);letter-spacing:2px'>"
        f"◈ LIVE SATELLITE FEED · {city_name.upper()} · {now.strftime('%H:%M:%S')}</div>"
        "<div style='position:absolute;top:10px;right:14px;font-size:9px;color:rgba(0,220,180,0.4);letter-spacing:2px'>"
        f"ENV SCORE: {es}/100 · AQ: {aq_cur.get('european_aqi','N/A')}</div>"
        "</div>"
        "<style>@keyframes ping-expand{0%{width:10px;height:10px;opacity:1}100%{width:220px;height:220px;opacity:0}}</style>"
    )

    # 7-day forecast + satellite side by side
    f1, f2 = st.columns([1,1])
    with f1:
        st.markdown('<div class="gc gcp"><div class="gct">7-DAY FORECAST</div>', unsafe_allow_html=True)
        rows=[]
        for i,day in enumerate(daily["time"]):
            d=datetime.strptime(day,"%Y-%m-%d")
            rows.append({"DATE":d.strftime("%a %d %b").upper(),
                "MAX °C":f"{daily['temperature_2m_max'][i]:.1f}",
                "MIN °C":f"{daily['temperature_2m_min'][i]:.1f}",
                "RAIN mm":f"{daily['precipitation_sum'][i]:.1f}",
                "RAIN %":f"{daily['precipitation_probability_max'][i]}%",
                "WIND":f"{daily['wind_speed_10m_max'][i]:.1f}",
                "UV":f"{daily['uv_index_max'][i]:.0f}"})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with f2:
        st.markdown('<div class="gc"><div class="gcp" style="padding-bottom:0"><div class="gct">LIVE SATELLITE FEED</div></div>', unsafe_allow_html=True)
        components.html(sat_html, height=230, scrolling=False)
        st.markdown('</div>', unsafe_allow_html=True)

    # Agricultural Zone Map
    st.markdown("""<div style="padding:0.8rem 2rem 0.4rem">
      <div class="sec-label" style="padding:0.6rem 0"><div class="sl-tag">AGRICULTURAL ZONE INTELLIGENCE MAP</div><div class="sl-line"></div><div class="sl-code">SAT::ZONE_v2</div></div>
    </div>""", unsafe_allow_html=True)

    map_col, zone_col = st.columns([2,1])

    with map_col:
        layer_options = ["🌱 Crop Suitability","💧 Water Availability","🌡 Temperature",
                         "🌊 Flood Risk","🏜 Drought","🟢 Vegetation Index","🦗 Pest Pressure","🌍 Soil Health"]
        lc_map = {
            "🌱 Crop Suitability":["#00f5c3","#4dffcc","#f5c842","#ff8c3a","#ff3a5c"],
            "💧 Water Availability":["#00c8ff","#4ddbff","#f5c842","#ff8c3a","#ff3a5c"],
            "🌡 Temperature":["#ff3a5c","#ff8c3a","#f5c842","#4dffcc","#00f5c3"],
            "🌊 Flood Risk":["#0040ff","#0088ff","#00c8ff","#f5c842","#00f5c3"],
            "🏜 Drought":["#ff3a5c","#ff8c3a","#f5c842","#4dffcc","#00f5c3"],
            "🟢 Vegetation Index":["#00f500","#4dff4d","#a0c040","#886600","#442200"],
            "🦗 Pest Pressure":["#ff3a5c","#ff8c3a","#f5c842","#4dffcc","#00f5c3"],
            "🌍 Soil Health":["#00f5c3","#4dffaa","#a0904a","#886628","#442210"],
        }
        sel_layer = st.selectbox("◈ INTELLIGENCE LAYER", layer_options, key="map_sel")
        lc = lc_map.get(sel_layer, lc_map["🌱 Crop Suitability"])

        # Build map via string concat — no f-string around JS
        _mlat=str(lat); _mlon=str(lon); _mcity=city_name.upper()
        _mcoords=f"{lat:.3f}°{'N' if lat>=0 else 'S'} {lon:.3f}°{'E' if lon>=0 else 'W'}"
        _es=str(es); _alert="⚠ ALERTS" if has_crisis or has_warning else "✓ NOMINAL"
        _alert_col="#ff3a5c" if has_crisis else "#f5c842" if has_warning else "#00f5c3"

        zones_js = (
            "var zones=["
            "["+str(round(lat+0.13,4))+","+str(round(lon-0.10,4))+",0,0.19,'ZONE-A · OPTIMAL'],"
            "["+str(round(lat-0.09,4))+","+str(round(lon+0.20,4))+",1,0.15,'ZONE-B · GOOD'],"
            "["+str(round(lat+0.21,4))+","+str(round(lon+0.11,4))+",2,0.13,'ZONE-C · MODERATE'],"
            "["+str(round(lat-0.16,4))+","+str(round(lon-0.13,4))+",1,0.17,'ZONE-D · GOOD'],"
            "["+str(round(lat+0.07,4))+","+str(round(lon-0.22,4))+",3,0.11,'ZONE-E · STRESSED'],"
            "["+str(round(lat-0.06,4))+","+str(round(lon+0.26,4))+",0,0.14,'ZONE-F · OPTIMAL'],"
            "["+str(round(lat+0.28,4))+","+str(round(lon+0.03,4))+",4,0.09,'ZONE-G · CRITICAL'],"
            "["+str(round(lat-0.23,4))+","+str(round(lon-0.02,4))+",2,0.12,'ZONE-H · MODERATE']"
            "];"
        )

        map_html = (
            "<!DOCTYPE html><html><head><meta charset='utf-8'/>"
            "<link rel='stylesheet' href='https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'/>"
            "<script src='https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'></script>"
            "<style>*{margin:0;padding:0}body{background:#030b10}"
            "#m{width:100%;height:300px}"
            ".leaflet-container{background:#020a12!important}"
            ".leaflet-tile{filter:brightness(0.2) saturate(0.12) hue-rotate(160deg)!important}"
            ".leaflet-popup-content-wrapper{background:rgba(0,10,20,0.97);border:1px solid rgba(0,220,180,0.3);color:#00f5c3;border-radius:4px}"
            ".leaflet-popup-tip{background:rgba(0,10,20,0.97)}"
            ".leaflet-popup-content{font-family:Orbitron,monospace;font-size:10px;letter-spacing:1px}"
            ".leaflet-control-zoom a{background:rgba(0,10,20,0.9)!important;border-color:rgba(0,220,180,0.2)!important;color:#00f5c3!important}"
            ".scan{position:absolute;left:0;right:0;height:1px;pointer-events:none;z-index:1000;"
            "background:linear-gradient(90deg,transparent,rgba(0,220,180,0.45),rgba(0,200,255,0.3),transparent);"
            "animation:s 5s linear infinite}@keyframes s{0%{top:0%}100%{top:100%}}"
            ".htl{position:absolute;top:10px;left:10px;z-index:1000;pointer-events:none}"
            ".htr{position:absolute;top:10px;right:10px;z-index:1000;pointer-events:none;text-align:right}"
            ".hbl{position:absolute;bottom:10px;left:10px;z-index:1000;pointer-events:none}"
            ".b{display:inline-block;background:rgba(0,6,16,0.93);border:1px solid rgba(0,220,180,0.28);"
            "border-radius:3px;padding:4px 10px;font-size:9px;color:#00f5c3;letter-spacing:2px;margin-bottom:4px}"
            ".b.g{border-color:rgba(0,220,180,0.4)}"
            ".leg{background:rgba(0,6,16,0.93);border:1px solid rgba(0,220,180,0.18);border-radius:4px;padding:8px 10px}"
            ".lt{font-size:7px;color:rgba(0,160,180,0.7);letter-spacing:2px;margin-bottom:6px}"
            ".lr{display:flex;align-items:center;gap:6px;margin-bottom:3px}"
            ".ld{width:10px;height:10px;border-radius:2px;flex-shrink:0}"
            ".ll{font-size:8px;color:#9ef5e8}"
            "</style></head><body>"
            "<div id='m' style='position:relative'>"
            "<div class='scan'></div>"
            "<div class='htl'>"
            "<div class='b'>◈ " + sel_layer.upper() + "</div><br>"
            "<div class='b'>" + _mcity + "</div><br>"
            "<div class='b'>" + _mcoords + "</div>"
            "</div>"
            "<div class='htr'>"
            "<div class='b g'>ENV: " + _es + "/100</div><br>"
            "<div class='b' style='border-color:rgba(" + ("255,40,80" if has_crisis else "245,200,66" if has_warning else "0,220,180") + ",0.4);color:" + _alert_col + "'>" + _alert + "</div>"
            "</div>"
            "<div class='hbl'><div class='leg'><div class='lt'>ZONE CLASSIFICATION</div>"
            + "".join([f"<div class='lr'><div class='ld' style='background:{lc[i]}'></div><div class='ll'>{['OPTIMAL','GOOD','MODERATE','STRESSED','CRITICAL'][i]}</div></div>" for i in range(5)])
            + "</div></div></div>"
            "<script>"
            "var map=L.map('m',{zoomControl:false,attributionControl:false}).setView([" + _mlat + "," + _mlon + "],10);"
            "L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);"
            "L.control.zoom({position:'bottomright'}).addTo(map);"
            "var zc=['" + lc[0] + "','" + lc[1] + "','" + lc[2] + "','" + lc[3] + "','" + lc[4] + "'];"
            + zones_js +
            "zones.forEach(function(z){var c=L.circle([z[0],z[1]],{color:zc[z[2]],fillColor:zc[z[2]],"
            "fillOpacity:0.18,weight:1.5,opacity:0.75,radius:z[3]*111000}).addTo(map);"
            "c.bindPopup('<span style=\"font-family:Orbitron,monospace;font-size:10px;letter-spacing:1px\">◈ '+z[4]+'</span>');});"
            "for(var i=-5;i<=5;i++){"
            "L.polyline([[" + _mlat + "+i*0.06," + _mlon + "-0.7],[" + _mlat + "+i*0.06," + _mlon + "+0.7]],{color:'rgba(0,220,180,0.04)',weight:0.5}).addTo(map);"
            "L.polyline([[" + _mlat + "-0.4," + _mlon + "+i*0.09],[" + _mlat + "+0.4," + _mlon + "+i*0.09]],{color:'rgba(0,220,180,0.04)',weight:0.5}).addTo(map);}"
            "var ic=L.divIcon({html:'<div style=\"width:14px;height:14px;border-radius:50%;"
            "background:#00f5c3;border:2px solid #fff;box-shadow:0 0 12px #00f5c3,0 0 24px rgba(0,220,180,0.5)\"></div>',"
            "iconSize:[14,14],iconAnchor:[7,7]});"
            "L.marker([" + _mlat + "," + _mlon + "],{icon:ic}).addTo(map)"
            ".bindPopup('<span style=\"font-family:Orbitron,monospace;font-size:10px;color:#00f5c3;letter-spacing:1px\">◈ " + _mcity + "</span>');"
            "</script></body></html>"
        )

        st.markdown('<div class="map-wrap">', unsafe_allow_html=True)
        components.html(map_html, height=312, scrolling=False)
        st.markdown(f"""
<div style="display:flex;gap:8px;flex-wrap:wrap;padding:0.6rem 1rem;background:rgba(0,8,16,0.8);border-top:1px solid rgba(0,220,180,0.07)">
  <span style="padding:2px 8px;border-radius:3px;background:rgba(0,220,180,0.09);border:1px solid rgba(0,220,180,0.25);color:#00f5c3;font-family:Share Tech Mono,monospace;font-size:0.52rem">OPTIMAL 38%</span>
  <span style="padding:2px 8px;border-radius:3px;background:rgba(0,200,255,0.08);border:1px solid rgba(0,200,255,0.2);color:#00c8ff;font-family:Share Tech Mono,monospace;font-size:0.52rem">GOOD 27%</span>
  <span style="padding:2px 8px;border-radius:3px;background:rgba(245,200,66,0.08);border:1px solid rgba(245,200,66,0.2);color:#f5c842;font-family:Share Tech Mono,monospace;font-size:0.52rem">MODERATE 21%</span>
  <span style="padding:2px 8px;border-radius:3px;background:rgba(255,58,92,0.08);border:1px solid rgba(255,58,92,0.2);color:#ff3a5c;font-family:Share Tech Mono,monospace;font-size:0.52rem">STRESSED/CRITICAL 14%</span>
</div></div>""", unsafe_allow_html=True)

    with zone_col:
        pm25_z = float(aq_cur.get("pm2_5",0) or 0)
        eu_z = int(aq_cur.get("european_aqi",0) or 0)
        st.markdown(f"""
<div class="gc gcp" style="height:100%">
  <div class="gct">ZONE ANALYSIS</div>
  {"".join([
    f'<div style="display:flex;justify-content:space-between;align-items:center;padding:7px 0;border-bottom:1px solid rgba(0,220,180,0.06)">'
    f'<span style="font-family:Share Tech Mono,monospace;font-size:0.56rem;color:rgba(0,130,160,0.6);text-transform:uppercase">{k}</span>'
    f'<span style="font-family:Orbitron,sans-serif;font-size:0.8rem;font-weight:700;color:{v2}">{v1}</span>'
    f'</div>'
    for k,v1,v2 in [
      ("Soil Quality",f"{min(99,ws+8)}%","#00f5c3"),
      ("Water Access",f"{max(55,100-int(pm25_z*0.9))}%","#00c8ff"),
      ("Climate Fit",f"{ws}%",ec),
      ("Biodiversity",f"{min(99,es+5)}%","#4dffcc"),
      ("Air Quality",str(eu_z) if eu_z else "N/A",bcol(eu_z,20,60)),
      ("AG Potential",f"{ag}%","#00f5c3"),
    ]
  ])}
  <div style="margin-top:1rem;padding-top:0.8rem;border-top:1px solid rgba(0,220,180,0.06)">
    <div style="font-family:Share Tech Mono,monospace;font-size:0.54rem;color:rgba(0,130,160,0.5);margin-bottom:8px;text-transform:uppercase">Risk Factors</div>
    {"".join([
      f'<div style="display:flex;justify-content:space-between;margin-bottom:4px">'
      f'<span style="font-family:Share Tech Mono,monospace;font-size:0.57rem;color:rgba(0,130,160,0.5)">• {rk}</span>'
      f'<span style="font-family:Orbitron,sans-serif;font-size:0.6rem;font-weight:700;color:{rc}">{rv}</span>'
      f'</div>'
      for rk,rv,rc in [
        ("Drought","HIGH" if total_rain<5 else "LOW" if total_rain>30 else "MED",
         "#ff3a5c" if total_rain<5 else "#00f5c3" if total_rain>30 else "#f5c842"),
        ("Flood","HIGH" if total_rain>100 else "MED" if total_rain>50 else "LOW",
         "#ff3a5c" if total_rain>100 else "#f5c842" if total_rain>50 else "#00f5c3"),
        ("Pest","MED" if cur["relative_humidity_2m"]>70 else "LOW",
         "#f5c842" if cur["relative_humidity_2m"]>70 else "#00f5c3"),
        ("Heat","HIGH" if cur["temperature_2m"]>38 else "LOW",
         "#ff3a5c" if cur["temperature_2m"]>38 else "#00f5c3"),
      ]
    ])}
  </div>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# TAB 1 — AIR QUALITY
# ══════════════════════════════════════════
with tabs[1]:
    st.markdown('<div style="padding:1.5rem 2rem">', unsafe_allow_html=True)
    if aq_cur:
        pm25=float(aq_cur.get("pm2_5",0) or 0); pm10=float(aq_cur.get("pm10",0) or 0)
        no2=float(aq_cur.get("nitrogen_dioxide",0) or 0); so2=float(aq_cur.get("sulphur_dioxide",0) or 0)
        o3=float(aq_cur.get("ozone",0) or 0); co=float(aq_cur.get("carbon_monoxide",0) or 0)
        eu=int(aq_cur.get("european_aqi",0) or 0); us=int(aq_cur.get("us_aqi",0) or 0)
        ps_v = ps if ps is not None else 0; psc,psg = grade(ps_v)

        a1,a2,a3 = st.columns(3)
        with a1:
            st.markdown(f"""<div class="gc gcp"><div class="gct">EUROPEAN AQI</div>
<div class="dv-n" style="color:{bcol(eu,20,60)};font-size:3rem">{eu}</div>
<div class="dv-s">{"GOOD" if eu<20 else "MODERATE" if eu<50 else "POOR" if eu<80 else "HAZARDOUS"}</div></div>""", unsafe_allow_html=True)
        with a2:
            st.markdown(f"""<div class="gc gcp"><div class="gct">US AQI</div>
<div class="dv-n" style="color:{bcol(us,50,100)};font-size:3rem">{us}</div>
<div class="dv-s">{"GOOD" if us<50 else "MODERATE" if us<100 else "UNHEALTHY"}</div></div>""", unsafe_allow_html=True)
        with a3:
            st.markdown(f"""<div class="gc gcp"><div class="gct">POLLUTION SCORE</div>
<div class="dv-n" style="color:{psc};font-size:3rem">{ps_v}<span style="font-size:1rem;color:rgba(0,160,190,0.4)">/100</span></div>
<div class="dv-s">{psg} · HIGHER = CLEANER</div></div>""", unsafe_allow_html=True)

        pols=[("PM₂.₅  FINE PARTICLES",pm25,12,35,"μg/m³",min(100,int(pm25/2.5))),
              ("PM₁₀  COARSE PARTICLES",pm10,20,50,"μg/m³",min(100,int(pm10/1.5))),
              ("NO₂  NITROGEN DIOXIDE",no2,40,100,"μg/m³",min(100,int(no2))),
              ("SO₂  SULPHUR DIOXIDE",so2,20,80,"μg/m³",min(100,int(so2))),
              ("O₃   OZONE",o3,60,120,"μg/m³",min(100,int(o3/1.8))),
              ("CO   CARBON MONOXIDE",co/1000,0.5,2,"mg/m³",min(100,int(co/700)))]
        p1,p2=st.columns(2)
        for i,(nm,val,g,b,unit,pct) in enumerate(pols):
            bc=bcol(val,g,b)
            with (p1 if i<3 else p2):
                st.markdown(f"""<div style="padding:0.6rem 0">
<div class="pol"><div class="pol-h"><span class="pol-n">{nm}</span>
<span class="pol-v" style="color:{bc}">{val:.1f}<span style="font-size:0.58rem;color:rgba(0,110,140,0.5);margin-left:3px">{unit}</span></span></div>
<div class="pol-t"><div class="pol-f" style="width:{pct}%;background:{bc};color:{bc}"></div></div></div></div>""", unsafe_allow_html=True)
    else:
        st.info("Air quality data unavailable.")
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════
# TAB 2 — CRISIS INTEL
# ══════════════════════════════════════════
with tabs[2]:
    st.markdown('<div style="padding:1.5rem 2rem">', unsafe_allow_html=True)
    max_rain_day=max((p for p in daily["precipitation_sum"] if p),default=0)
    max_temp_v=max((t for t in daily["temperature_2m_max"] if t),default=0)
    st.markdown(f"""<div style="padding:0.7rem 1.1rem;background:rgba(0,220,180,0.03);border:1px solid rgba(0,220,180,0.1);
border-radius:6px;margin-bottom:1rem;font-family:Share Tech Mono,monospace;font-size:0.61rem;color:rgba(0,140,170,0.6)">
◈ 7D RAIN: {total_rain:.0f}MM · PEAK: {max_rain_day:.0f}MM/DAY · MAX TEMP: {max_temp_v:.1f}°C · RH: {cur['relative_humidity_2m']}% · AQI: {aq_cur.get('european_aqi','N/A')} · {now.strftime('%B').upper()}
</div>""", unsafe_allow_html=True)
    for level,title,msg in crisis_data:
        icon="🚨" if level=="crisis" else "⚠️" if level=="warning" else "✅"
        st.markdown(f"""<div class="alert a-{level[0]}"><div class="a-icon">{icon}</div>
<div><div class="a-title">{title}</div><div class="a-msg">{msg}</div></div></div>""", unsafe_allow_html=True)
    if st.button("▶ RUN AI CRISIS ANALYSIS", type="primary"):
        s={"location":f"{city_name},{country}","lat":lat,"temp":cur["temperature_2m"],
           "rh":cur["relative_humidity_2m"],"aqi":aq_cur.get("european_aqi"),
           "7d_rain":total_rain,"peak_day":max_rain_day,"max_temp":max_temp_v,"month":now.month}
        with st.spinner("Analysing..."):
            result=ask_groq(f"Agricultural crisis analysis for {city_name},{country} ({now.strftime('%B')},lat:{lat:.1f}):\n{json.dumps(s,indent=2)}\n1)Threats from actual data 2)Crop impact 3)48h actions 4)30d outlook",
                system=f"Agricultural risk analyst for {country}. {now.strftime('%B')}: high rain→flood/disease focus, low rain→drought. Accurate to the numbers.")
        st.markdown(f'<div class="ai-box"><div class="ai-tag">AI CRISIS REPORT · {city_name.upper()}</div>{result.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════
# TAB 3 — CROP ENGINE
# ══════════════════════════════════════════
with tabs[3]:
    st.markdown('<div style="padding:1.5rem 2rem">', unsafe_allow_html=True)
    crop_list=recommend_crops(weather)
    for emoji,name,compat,reason,care in crop_list:
        cc,_=grade(compat)
        st.markdown(f"""<div class="cc"><div class="cc-em">{emoji}</div>
<div class="cc-bd"><div class="cc-nm">{name}</div><div class="cc-rs">▸ {reason}</div>
<div class="cc-cr">◦ {care}</div></div>
<div>{mini_ring(compat,cc)}</div></div>""", unsafe_allow_html=True)
    opts=[f"{e} {n}" for e,n,*_ in crop_list] if crop_list else ["N/A"]
    sel=st.selectbox("Select crop for detailed plan",opts)
    if st.button("▶ GENERATE MANAGEMENT PLAN", type="primary") and crop_list:
        with st.spinner("Building plan..."):
            result=ask_groq(
                f"Precision plan for {sel} in {city_name},{country} ({now.strftime('%B')}). "
                f"{cur['temperature_2m']:.1f}°C, {cur['relative_humidity_2m']}% RH, "
                f"AQI {aq_cur.get('european_aqi','N/A')}, 7D rain {total_rain:.0f}mm. "
                "Include: sowing timing, irrigation quantities, NPK plan, pest monitoring, harvest timeline.",
                system=f"Precision agriculture specialist for {country} {now.strftime('%B')}.")
        st.markdown(f'<div class="ai-box"><div class="ai-tag">MANAGEMENT PLAN · {sel.upper()}</div>{result.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════
# TAB 4 — SIMULATION
# ══════════════════════════════════════════
with tabs[4]:
    st.markdown('<div style="padding:1.5rem 2rem">', unsafe_allow_html=True)
    s1,s2=st.columns(2)
    with s1:
        t_d=st.slider("Temperature Δ (°C)",-10,+20,0)
        r_d=st.slider("Rainfall Δ (%)",-100,+200,0)
        h_d=st.slider("Humidity Δ (%)",-40,+40,0)
    with s2:
        aqi_d=st.slider("AQI Δ",-60,+200,0)
        w_d=st.slider("Wind Δ (km/h)",-20,+60,0)
        sim_crop=st.text_input("Target Crop",placeholder="Rice, Wheat, Tomato...")
    base_r=total_rain/7; sim_t=cur["temperature_2m"]+t_d
    sim_r=base_r*(1+r_d/100); sim_aqi=(aq_cur.get("european_aqi") or 30)+aqi_d
    sim_h=min(100,max(0,cur["relative_humidity_2m"]+h_d)); sim_w=max(0,cur["wind_speed_10m"]+w_d)
    sv=st.columns(5)
    for col,lbl,bv,sv_val,unit in [(sv[0],"TEMP",cur["temperature_2m"],sim_t,"°C"),
        (sv[1],"RAIN/D",base_r,sim_r,"mm"),(sv[2],"RH",cur["relative_humidity_2m"],sim_h,"%"),
        (sv[3],"AQI",aq_cur.get("european_aqi",30),sim_aqi,""),(sv[4],"WIND",cur["wind_speed_10m"],sim_w,"km/h")]:
        dlt=sv_val-bv; dc="#00f5c3" if dlt<=0 else "#ff3a5c"
        with col:
            st.markdown(f"""<div class="gc gcp"><div class="dv-l">{lbl}</div>
<div class="dv-n" style="font-size:1.4rem">{sv_val:.1f}<span class="dv-u">{unit}</span></div>
<div class="dv-s" style="color:{dc}">{'▲' if dlt>0 else '▼'} {abs(dlt):.1f}{unit}</div></div>""", unsafe_allow_html=True)
    if st.button("▶ RUN SIMULATION", type="primary"):
        with st.spinner("Running simulation..."):
            result=ask_groq(
                f"Farm Digital Twin for {city_name},{country} ({now.strftime('%B')}). "
                f"BASELINE: {cur['temperature_2m']:.1f}°C, {base_r:.1f}mm/d, RH {cur['relative_humidity_2m']}%, AQI {aq_cur.get('european_aqi','N/A')}. "
                f"SCENARIO: {sim_t:.1f}°C, {sim_r:.1f}mm/d, RH {sim_h:.0f}%, AQI {sim_aqi:.0f}. "
                f"{'Crop: '+sim_crop if sim_crop else ''}. "
                "Give: 1)Risk delta % 2)Yield impact with numbers 3)Resource changes 4)Strategies",
                system=f"Agricultural simulation expert for {country}.")
        st.markdown(f'<div class="ai-box"><div class="ai-tag">SIMULATION RESULTS</div>{result.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════
# TAB 5 — CROP SCANNER
# ══════════════════════════════════════════
with tabs[5]:
    st.markdown('<div style="padding:1.5rem 2rem">', unsafe_allow_html=True)
    sc1,sc2=st.columns([1,1])
    with sc1:
        uploaded=st.file_uploader("UPLOAD PLANT IMAGE",type=["jpg","jpeg","png","webp"])
        crop_name_s=st.text_input("Crop Name",placeholder="Tomato, Rice, Wheat...")
        scan_ctx=st.text_area("Describe Symptoms",placeholder="Yellow leaves, brown spots...",height=80)
    with sc2:
        if uploaded: st.image(uploaded,caption="UPLOADED SAMPLE",use_container_width=True)
        else: st.markdown("""<div style="width:100%;height:200px;background:rgba(0,220,180,0.02);
border:1px dashed rgba(0,220,180,0.16);border-radius:6px;display:flex;align-items:center;justify-content:center;
font-family:Share Tech Mono,monospace;font-size:0.6rem;color:rgba(0,120,140,0.5);text-align:center">
◈ AWAITING PLANT SAMPLE<br><br>JPG · PNG · WEBP</div>""", unsafe_allow_html=True)
    if st.button("▶ SCAN PLANT HEALTH", type="primary"):
        if uploaded or scan_ctx or crop_name_s:
            with st.spinner("Scanning..."):
                if uploaded:
                    img_b=uploaded.read(); img_b64=base64.b64encode(img_b).decode()
                    ext=uploaded.name.split('.')[-1].lower(); mime="image/jpeg" if ext in ["jpg","jpeg"] else f"image/{ext}"
                    try:
                        resp=get_groq().chat.completions.create(model="llama-3.3-70b-versatile",max_tokens=1000,
                            messages=[{"role":"user","content":[
                                {"type":"text","text":f"Plant pathologist analysis. Crop:{crop_name_s or 'Unknown'}. Symptoms:{scan_ctx or 'see image'}. {city_name},{now.strftime('%B')},{cur['temperature_2m']:.1f}°C,{cur['relative_humidity_2m']}% RH. Provide:1)Diagnosis 2)Severity 3)Treatment 4)Prevention 5)Timeline."},
                                {"type":"image_url","image_url":{"url":f"data:{mime};base64,{img_b64}"}}]}])
                        result=resp.choices[0].message.content
                    except: result=ask_groq(f"Plant health: {crop_name_s or 'crop'}. Symptoms:{scan_ctx}. {city_name},{now.strftime('%B')},{cur['temperature_2m']:.1f}°C,{cur['relative_humidity_2m']}% RH.")
                else: result=ask_groq(f"Plant health. Crop:{crop_name_s}. Symptoms:{scan_ctx}. {city_name},{now.strftime('%B')},{cur['temperature_2m']:.1f}°C,{cur['relative_humidity_2m']}% RH.")
            st.markdown(f'<div class="ai-box"><div class="ai-tag">CROP HEALTH REPORT</div>{result.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)
        else: st.warning("Upload an image or describe symptoms.")
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════
# TAB 6 — FIELD AI
# ══════════════════════════════════════════
with tabs[6]:
    st.markdown('<div style="padding:1.5rem 2rem">', unsafe_allow_html=True)
    st.markdown(f"""<div style="padding:0.7rem 1.1rem;background:rgba(0,220,180,0.03);border:1px solid rgba(0,220,180,0.08);
border-radius:5px;margin-bottom:1rem;font-family:Share Tech Mono,monospace;font-size:0.6rem;color:rgba(0,130,160,0.55)">
◈ CONTEXT · {city_name.upper()},{country.upper()} · {now.strftime('%B %Y')} · {cur['temperature_2m']:.1f}°C · {cur['relative_humidity_2m']}% RH · AQI {aq_cur.get('european_aqi','N/A')} · 7D RAIN: {total_rain:.0f}MM · ENV {es}/100
</div>""", unsafe_allow_html=True)
    focus=st.text_input("CROP FOCUS (optional)",placeholder="Rice, Tomato, Groundnut...")
    if "chat" not in st.session_state: st.session_state.chat=[]
    if not st.session_state.chat:
        sqc=st.columns(2)
        for i,q in enumerate(["What diseases to watch this month?","Water requirement this week?",
            "Safe to spray pesticide today?","Create 30-day farming schedule",
            "Flood/drought risk for my location?","Which fertiliser to apply now?"]):
            with sqc[i%2]:
                st.markdown(f"""<div style="padding:0.6rem 0.9rem;background:rgba(0,220,180,0.03);
border:1px solid rgba(0,220,180,0.09);border-radius:4px;margin-bottom:0.5rem;
font-size:0.72rem;color:rgba(0,160,180,0.65);font-family:Share Tech Mono,monospace">▸ {q}</div>""", unsafe_allow_html=True)
    for msg in st.session_state.chat:
        if msg["role"]=="user":
            st.markdown(f"""<div class="cu-r"><div class="cbub cu-b"><div class="cfrom cf-u">◈ YOU</div>{msg['content']}</div></div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="ca-r"><div class="cbub ca-b"><div class="cfrom cf-a">◈ AEROVEDA AI</div>{msg['content']}</div></div>""", unsafe_allow_html=True)
    user_in=st.chat_input("Ask the Field Intelligence System...")
    if user_in:
        st.session_state.chat.append({"role":"user","content":user_in})
        with st.spinner("Processing..."):
            reply=ask_groq_chat(st.session_state.chat,
                system=f"""Aeroveda Field AI — expert agronomist with real-time data.
LOCATION: {city_name},{region},{country} | {lat:.4f}°N,{lon:.4f}°E
DATE: {now.strftime('%d %B %Y')} | {'MONSOON' if (abs(lat)<25 and now.month in [6,7,8,9,10]) else 'SEASON'}
WEATHER: {cur['temperature_2m']:.1f}°C | {cur['relative_humidity_2m']}% RH | {cur['wind_speed_10m']:.1f}km/h | {wdesc(cur['weather_code'])}
AIR: AQI {aq_cur.get('european_aqi','N/A')} | PM2.5 {aq_cur.get('pm2_5','N/A')}
RAIN 7D: {total_rain:.0f}mm | ENV {es}/100 | AG {ag}/100
{'CROP: '+focus if focus else ''}
Give precise, location-specific answers referencing actual conditions.""",max_tokens=900)
        st.session_state.chat.append({"role":"assistant","content":reply}); st.rerun()
    if st.session_state.chat:
        if st.button("↺ CLEAR"): st.session_state.chat=[]; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ── STATUS BAR ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="sbar">
  <div class="sb-i">🌍 <span style="color:rgba(0,140,160,0.4)">AEROVEDA OS</span> <span class="sb-v">v4.0</span></div>
  <div class="sb-i">📍 <span class="sb-v">{city_name.upper()}, {country.upper()}</span></div>
  <div class="sb-i">⏱ <span class="sb-v">{now.strftime('%H:%M:%S')}</span></div>
  <div class="sb-i">DATA STREAM <span class="sb-v" style="color:#00f5c3">● LIVE</span></div>
  <div class="sb-i">ENV <span class="sb-v" style="color:{ec}">{es}/100</span></div>
  <div class="sb-i">AQI <span class="sb-v">{aq_cur.get('european_aqi','N/A')}</span></div>
  <div class="sb-i">🔒 <span class="sb-v" style="color:#00f5c3">SECURE</span></div>
</div>
""", unsafe_allow_html=True)
