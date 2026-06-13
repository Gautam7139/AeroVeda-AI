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
# CSS — Cyan + Earth
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Exo+2:wght@200;300;400;500;600;700&family=Share+Tech+Mono&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body,[class*="css"]{font-family:'Exo 2',sans-serif;background:#040d12!important;color:#b8e8f0}
.stApp{
  background: radial-gradient(ellipse 70% 50% at 20% 20%, rgba(0,180,220,0.06) 0%,transparent 50%),
              radial-gradient(ellipse 60% 40% at 80% 80%, rgba(20,120,80,0.05) 0%,transparent 45%),
              #040d12!important;
}
</style>
""", unsafe_allow_html=True)

# ─── Corrected Mathematical Helper ────────────────────────────
def ll3d(la, lo, r):
    """Converts latitude/longitude to 3D Cartesian coordinates."""
    p = la * math.pi / 180
    l = lo * math.pi / 180
    return [
        r * math.cos(p) * math.cos(l),
        r * math.sin(p),
        r * math.cos(p) * math.sin(l)
    ]

# ─── Helpers ──────────────────────────────────────────────────
@st.cache_resource
def get_groq():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

def fetch_weather(lat, lon):
    url = (f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
           f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m&daily=precipitation_sum,temperature_2m_max&forecast_days=7&timezone=auto")
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
            return res["latitude"], res["longitude"], res.get("name",city)
        return None
    except: return None

# ══════════════════════════════════════════════════════════════
# MAIN INTERFACE
# ══════════════════════════════════════════════════════════════
st.title("AEROVEDA OS")

# Location Setup
if "city" not in st.session_state: st.session_state["city"] = "Bengaluru"

col1, col2 = st.columns([3, 1])
with col1:
    city_input = st.text_input("Enter Location", st.session_state["city"])
    if city_input: st.session_state["city"] = city_input

with col2:
    if st.button("📍 Use GPS"):
        location = get_geolocation()
        if location and "coords" in location:
            st.session_state["lat"] = location["coords"]["latitude"]
            st.session_state["lon"] = location["coords"]["longitude"]
            st.rerun()

# Processing Data
geo = geocode(st.session_state["city"])
if geo:
    lat, lon, name = geo
    weather = fetch_weather(lat, lon)
    
    if weather:
        st.subheader(f"Data for {name}")
        st.metric("Temperature", f"{weather['current']['temperature_2m']}°C")
        
        # Testing the corrected function
        coords_3d = ll3d(lat, lon, 1)
        st.write(f"3D Vector Projection: {coords_3d}")
    else:
        st.error("Could not fetch weather data.")
else:
    st.warning("City not found.")
