import streamlit as st
import streamlit.components.v1 as components
import requests
import json
from datetime import datetime
import pandas as pd
from groq import Groq

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Aeroveda",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp {
    background: linear-gradient(135deg, #0a1628 0%, #0d2137 50%, #0a1e0f 100%);
    color: #e8f4e8;
}
.aeroveda-header { text-align: center; padding: 2rem 0 1rem; }
.aeroveda-header h1 {
    font-family: 'Playfair Display', serif;
    font-size: 3.2rem;
    background: linear-gradient(90deg, #4ade80, #86efac, #a3e635);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0; letter-spacing: -1px;
}
.aeroveda-header p {
    color: #6ee7b7; font-size: 1rem; font-weight: 300;
    letter-spacing: 3px; text-transform: uppercase; margin-top: 0.3rem;
}
.metric-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(74,222,128,0.2);
    border-radius: 16px; padding: 1.2rem 1.4rem; margin-bottom: 1rem;
}
.metric-card h4 {
    color: #86efac; font-size: 0.75rem; font-weight: 500;
    letter-spacing: 2px; text-transform: uppercase; margin: 0 0 0.3rem 0;
}
.metric-card .value {
    color: #f0fdf4; font-size: 2rem; font-weight: 600;
    font-family: 'Playfair Display', serif; line-height: 1;
}
.metric-card .unit { color: #6ee7b7; font-size: 0.85rem; margin-left: 4px; }
.score-container {
    text-align: center; padding: 1.5rem;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(74,222,128,0.25); border-radius: 20px;
}
.score-number {
    font-family: 'Playfair Display', serif;
    font-size: 4rem; font-weight: 700; line-height: 1;
}
.score-label {
    font-size: 0.8rem; letter-spacing: 2px;
    text-transform: uppercase; margin-top: 0.3rem;
}
.alert-crisis {
    background: rgba(239,68,68,0.12); border-left: 4px solid #ef4444;
    border-radius: 8px; padding: 0.8rem 1rem; margin: 0.5rem 0; color: #fca5a5;
}
.alert-warning {
    background: rgba(234,179,8,0.12); border-left: 4px solid #eab308;
    border-radius: 8px; padding: 0.8rem 1rem; margin: 0.5rem 0; color: #fde047;
}
.alert-safe {
    background: rgba(74,222,128,0.1); border-left: 4px solid #4ade80;
    border-radius: 8px; padding: 0.8rem 1rem; margin: 0.5rem 0; color: #86efac;
}
.crop-card {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(74,222,128,0.15);
    border-radius: 14px; padding: 1rem 1.2rem; margin: 0.5rem 0;
}
.crop-name { font-family: 'Playfair Display', serif; font-size: 1.2rem; color: #d1fae5; }
.crop-score {
    background: rgba(74,222,128,0.2); color: #4ade80; border-radius: 20px;
    padding: 2px 10px; font-size: 0.78rem; font-weight: 500;
    display: inline-block; margin-top: 4px;
}
.chat-bubble-user {
    background: rgba(74,222,128,0.15); border: 1px solid rgba(74,222,128,0.3);
    border-radius: 14px 14px 4px 14px; padding: 0.7rem 1rem;
    margin: 0.5rem 0; color: #d1fae5; text-align: right;
}
.chat-bubble-ai {
    background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
    border-radius: 14px 14px 14px 4px; padding: 0.7rem 1rem;
    margin: 0.5rem 0; color: #e8f4e8;
}
.section-title {
    font-family: 'Playfair Display', serif; font-size: 1.6rem; color: #d1fae5;
    margin: 1.5rem 0 0.8rem 0;
    border-bottom: 1px solid rgba(74,222,128,0.2); padding-bottom: 0.4rem;
}
[data-testid="stSidebar"] {
    background: rgba(5,15,30,0.95) !important;
    border-right: 1px solid rgba(74,222,128,0.15);
}
.stTabs [data-baseweb="tab"] { color: #6ee7b7; }
.stTabs [aria-selected="true"] {
    color: #4ade80 !important; border-bottom-color: #4ade80 !important;
}
button[kind="primary"] {
    background: linear-gradient(135deg, #16a34a, #4ade80) !important;
    border: none !important; border-radius: 10px !important;
    color: #052e16 !important; font-weight: 600 !important;
}
.bar-bg {
    background: rgba(255,255,255,0.08); border-radius: 99px;
    height: 10px; width: 100%; margin: 4px 0 10px 0;
}
.bar-fill { height: 10px; border-radius: 99px; }
</style>
""", unsafe_allow_html=True)

# ─── Groq Client ─────────────────────────────────────────────────────────────
@st.cache_resource
def get_groq_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

def ask_groq(prompt, system="You are a helpful agricultural expert.", max_tokens=1000):
    try:
        client = get_groq_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI error: {str(e)}"

def ask_groq_chat(messages, system, max_tokens=700):
    try:
        client = get_groq_client()
        full_messages = [{"role": "system", "content": system}] + messages
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=max_tokens,
            messages=full_messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI error: {str(e)}"

# ─── API Fetchers ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=1800)
def fetch_weather(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
        f"precipitation,rain,wind_speed_10m,wind_direction_10m,"
        f"surface_pressure,cloud_cover,uv_index,weather_code"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,"
        f"wind_speed_10m_max,uv_index_max,precipitation_probability_max"
        f"&forecast_days=7&timezone=auto"
    )
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Weather fetch failed: {e}")
        return None

@st.cache_data(ttl=1800)
def fetch_air_quality(lat, lon):
    url = (
        f"https://air-quality-api.open-meteo.com/v1/air-quality"
        f"?latitude={lat}&longitude={lon}"
        f"&current=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,"
        f"sulphur_dioxide,ozone,european_aqi,us_aqi"
    )
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except:
        return None

@st.cache_data(ttl=3600)
def geocode_city(city):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
    try:
        r = requests.get(url, timeout=8)
        data = r.json()
        if data.get("results"):
            res = data["results"][0]
            return res["latitude"], res["longitude"], res.get("country", "")
        return None
    except:
        return None

def reverse_geocode(lat, lon):
    try:
        r = requests.get(
            f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json",
            headers={"User-Agent": "Aeroveda/1.0"},
            timeout=5
        )
        data = r.json()
        city = (
            data.get("address", {}).get("city") or
            data.get("address", {}).get("town") or
            data.get("address", {}).get("village", "")
        )
        return city if city else None
    except:
        return None

# ─── Scoring ──────────────────────────────────────────────────────────────────
def get_aqi_label(score):
    if score >= 80: return "#4ade80", "CLEAN"
    elif score >= 60: return "#a3e635", "GOOD"
    elif score >= 40: return "#facc15", "MODERATE"
    elif score >= 20: return "#fb923c", "POOR"
    else: return "#ef4444", "HAZARDOUS"

def compute_pollution_score(aq):
    """0=most polluted, 100=cleanest"""
    if not aq:
        return None
    cur = aq.get("current", {})
    aqi = cur.get("european_aqi") or cur.get("us_aqi")
    if aqi is None:
        return None
    return max(0, min(100, round(100 - aqi)))

def compute_weather_score(w):
    cur = w["current"]
    score = 100
    temp = cur["temperature_2m"]
    humidity = cur["relative_humidity_2m"]
    wind = cur["wind_speed_10m"]
    uv = cur.get("uv_index", 0) or 0
    precip = cur.get("precipitation", 0) or 0
    if temp > 40 or temp < 0:       score -= 25
    elif temp > 35 or temp < 5:     score -= 12
    if humidity > 90 or humidity < 15:   score -= 15
    elif humidity > 80 or humidity < 25: score -= 7
    if wind > 60:    score -= 20
    elif wind > 35:  score -= 8
    if uv > 10:      score -= 15
    elif uv > 7:     score -= 6
    if precip > 20:  score -= 15
    elif precip > 5: score -= 4
    return max(0, min(100, score))

def compute_env_score(weather_score, pollution_score):
    """Blend: 55% weather + 45% air quality"""
    if pollution_score is None:
        return weather_score
    return max(0, min(100, round(weather_score * 0.55 + pollution_score * 0.45)))

def score_color(score):
    if score >= 75:   return "#4ade80", "EXCELLENT"
    elif score >= 55: return "#a3e635", "GOOD"
    elif score >= 35: return "#facc15", "MODERATE"
    else:             return "#ef4444", "POOR"

# ─── Other Helpers ────────────────────────────────────────────────────────────
WMO_CODES = {
    0:"Clear sky", 1:"Mainly clear", 2:"Partly cloudy", 3:"Overcast",
    45:"Foggy", 48:"Icy fog", 51:"Light drizzle", 53:"Drizzle", 55:"Heavy drizzle",
    61:"Slight rain", 63:"Moderate rain", 65:"Heavy rain",
    71:"Slight snow", 73:"Moderate snow", 75:"Heavy snow",
    80:"Slight showers", 81:"Moderate showers", 82:"Violent showers",
    95:"Thunderstorm", 96:"Thunderstorm w/ hail", 99:"Thunderstorm w/ heavy hail"
}
def weather_description(code):
    return WMO_CODES.get(code, "Unknown")

def predict_crises(w, aq_cur):
    alerts = []
    daily = w["daily"]
    # Pollution
    if aq_cur:
        aqi = aq_cur.get("european_aqi") or aq_cur.get("us_aqi")
        if aqi and aqi > 80:
            alerts.append(("crisis", f"💨 Air Quality Crisis — AQI {aqi}. Hazardous pollution. Severe risk to crops and health."))
        elif aqi and aqi > 50:
            alerts.append(("warning", f"💨 Poor Air Quality — AQI {aqi}. May affect sensitive crops and outdoor workers."))
    # Weather
    hot_days = sum(1 for t in daily["temperature_2m_max"] if t and t > 38)
    if hot_days >= 3:
        alerts.append(("crisis", f"🌡️ Heat Wave Risk — {hot_days} days above 38°C forecast."))
    elif hot_days >= 1:
        alerts.append(("warning", f"🌡️ High Temperature — {hot_days} days above 38°C expected."))
    total_precip = sum(p for p in daily["precipitation_sum"] if p is not None)
    if total_precip < 2:
        alerts.append(("crisis", "🏜️ Drought Risk — Near-zero rainfall over 7 days. Irrigation critical."))
    elif total_precip < 8:
        alerts.append(("warning", "💧 Low Rainfall — Minimal precipitation expected."))
    heavy_rain = sum(1 for p in daily["precipitation_sum"] if p and p > 25)
    if heavy_rain >= 2:
        alerts.append(("crisis", f"🌊 Flood Risk — {heavy_rain} days with >25mm rainfall."))
    elif heavy_rain == 1:
        alerts.append(("warning", "🌧️ Heavy Rain Alert — Waterlogging possible."))
    max_wind = max((v for v in daily["wind_speed_10m_max"] if v), default=0)
    if max_wind > 70:
        alerts.append(("crisis", f"💨 Storm Alert — Gusts up to {max_wind:.0f} km/h."))
    elif max_wind > 45:
        alerts.append(("warning", f"💨 High Wind — Up to {max_wind:.0f} km/h forecast."))
    if not alerts:
        alerts.append(("safe", "✅ No significant crises forecast for the next 7 days."))
    return alerts

def recommend_crops(w):
    cur = w["current"]
    daily = w["daily"]
    temp = cur["temperature_2m"]
    humidity = cur["relative_humidity_2m"]
    precip_list = [p for p in daily["precipitation_sum"] if p is not None]
    avg_rain = sum(precip_list) / len(precip_list) if precip_list else 0
    crops = []
    if 20 <= temp <= 38 and humidity > 50:
        crops.append(("🌾 Rice", 95, "Thrives in warm humid conditions.", "High water; transplant seedlings; 3-4 month cycle."))
        crops.append(("🌿 Sugarcane", 88, "Loves heat and humidity.", "Deep watering weekly; fertilise monthly; 10-12 month crop."))
    if 18 <= temp <= 35:
        crops.append(("🥜 Groundnut", 85, "Well-suited to current temperatures.", "Light well-drained soil; needs dry spell at end."))
        crops.append(("🌽 Maize", 82, "Good temperature match.", "Moderate irrigation; nitrogen-rich fertiliser; 90-day cycle."))
    if temp >= 25 and humidity < 70:
        crops.append(("🍅 Tomato", 78, "Warm and dry — tomatoes will thrive.", "Stake plants; consistent watering; watch for blight."))
        crops.append(("🌶️ Chilli", 76, "Ideal warm and dry conditions.", "Drip irrigation; high potassium for fruiting."))
    if temp < 22:
        crops.append(("🥬 Spinach", 90, "Cool temperatures perfect for leafy greens.", "Sow directly; harvest in 6-8 weeks; high nitrogen."))
        crops.append(("🥕 Carrot", 84, "Cool soil promotes root development.", "Deep loose soil; thin seedlings; 70-80 day crop."))
        crops.append(("🧅 Onion", 80, "Cool dry weather suits bulb development.", "Well-drained beds; reduce water at bulbing stage."))
    if avg_rain < 3 and temp > 20:
        crops.append(("🌻 Sunflower", 88, "Drought-tolerant and heat-resistant.", "Minimal irrigation; 80-95 day cycle."))
        crops.append(("🫘 Moong Dal", 83, "Excellent drought tolerance.", "Sandy loam; minimal inputs; 60-70 days."))
    crops.sort(key=lambda x: -x[1])
    return crops[:5]

# ════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════
st.markdown("""
<div class="aeroveda-header">
    <h1>🌿 Aeroveda</h1>
    <p>Intelligent Agricultural & Environmental Intelligence</p>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# SIDEBAR — GPS Location
# ════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 📍 Location")

    # Read GPS from query params (set by JS below)
    params = st.query_params
    gps_raw = params.get("gps", "")
    if gps_raw and "," in str(gps_raw):
        try:
            parts = str(gps_raw).split(",")
            gps_lat = float(parts[0])
            gps_lon = float(parts[1])
            detected = reverse_geocode(gps_lat, gps_lon)
            if detected:
                st.session_state["detected_city"] = detected
        except:
            pass

    # JS button that gets GPS then reloads page with ?gps=lat,lon
    components.html("""
    <button id="locbtn" onclick="getLocation()" style="
        background: linear-gradient(135deg,#16a34a,#4ade80);
        border:none; border-radius:10px; color:#052e16;
        font-weight:600; padding:0.5rem 1rem;
        cursor:pointer; width:100%; font-size:0.9rem; margin-bottom:6px;
    ">📍 Use My Location</button>
    <div id="status" style="color:#6ee7b7;font-size:0.75rem;min-height:18px;"></div>
    <script>
    function getLocation() {
        var btn = document.getElementById('locbtn');
        var status = document.getElementById('status');
        btn.innerText = '⏳ Getting location...';
        btn.disabled = true;
        if (!navigator.geolocation) {
            status.innerText = '❌ Geolocation not supported.';
            btn.innerText = '📍 Use My Location';
            btn.disabled = false;
            return;
        }
        navigator.geolocation.getCurrentPosition(
            function(pos) {
                var lat = pos.coords.latitude.toFixed(5);
                var lon = pos.coords.longitude.toFixed(5);
                status.innerText = '✅ Found! Loading...';
                var url = window.parent.location.href.split('?')[0] + '?gps=' + lat + ',' + lon;
                window.parent.location.href = url;
            },
            function(err) {
                status.style.color = '#fca5a5';
                if (err.code === 1) status.innerText = '❌ Permission denied. Allow location in browser.';
                else if (err.code === 2) status.innerText = '❌ Location unavailable.';
                else status.innerText = '❌ Timed out. Try again.';
                btn.innerText = '📍 Use My Location';
                btn.disabled = false;
            },
            { timeout: 10000, enableHighAccuracy: true }
        );
    }
    </script>
    """, height=80)

    default_city = st.session_state.get("detected_city", "Bengaluru")
    city = st.text_input("Or type a city", value=default_city, placeholder="e.g. Delhi, Pune...")

    st.markdown("---")
    st.markdown("""
    <div style="color:#6ee7b7;font-size:0.78rem;line-height:1.8">
    <b>Data Sources</b><br>
    🌤 Open-Meteo (weather)<br>
    💨 Open-Meteo (air quality)<br>
    🤖 Groq AI — LLaMA 3.3 70B<br>
    📡 Real-time 7-day forecast
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# FETCH DATA
# ════════════════════════════════════════════════════════
geo = geocode_city(city)
if not geo:
    st.error(f"Could not find location: **{city}**. Try a different city name.")
    st.stop()

lat, lon, country = geo
weather = fetch_weather(lat, lon)
if not weather:
    st.stop()

air_quality = fetch_air_quality(lat, lon)
cur = weather["current"]
daily = weather["daily"]
aq_cur = air_quality.get("current", {}) if air_quality else {}

# Compute all scores
weather_score   = compute_weather_score(weather)
pollution_score = compute_pollution_score(air_quality)
env_score       = compute_env_score(weather_score, pollution_score)
s_color, s_label = score_color(env_score)

# ════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs(["🌤 Dashboard", "⚠️ Crisis Forecast", "🌾 Crop Advisor", "💬 Chatbot"])

# ══════════════════════════════════════════════════════════
# TAB 1 — DASHBOARD
# ══════════════════════════════════════════════════════════
with tab1:

    # Location bar
    st.markdown(f"""
    <div style="padding:1.2rem;background:rgba(255,255,255,0.04);
         border:1px solid rgba(74,222,128,0.2);border-radius:16px;margin-bottom:1.2rem">
        <div style="font-size:0.75rem;letter-spacing:2px;color:#6ee7b7;text-transform:uppercase">Current Location</div>
        <div style="font-family:'Playfair Display',serif;font-size:2rem;color:#d1fae5;margin:4px 0">
            {city.title()}{', ' + country if country else ''}
        </div>
        <div style="color:#6ee7b7;font-size:0.85rem">
            {lat:.3f}°N, {lon:.3f}°E &nbsp;·&nbsp;
            {weather_description(cur['weather_code'])} &nbsp;·&nbsp;
            Updated {datetime.now().strftime('%H:%M')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── THREE SCORE CARDS ──────────────────────────────────
    sc1, sc2, sc3 = st.columns(3)

    with sc1:
        p_color, p_label = get_aqi_label(pollution_score or 0)
        p_val = pollution_score if pollution_score is not None else "N/A"
        p_pct = pollution_score if pollution_score is not None else 0
        st.markdown(f"""
        <div class="score-container">
            <div style="font-size:0.7rem;letter-spacing:2px;color:#6ee7b7;
                 text-transform:uppercase;margin-bottom:6px">🌫️ Pollution Score</div>
            <div class="score-number" style="color:{p_color}">{p_val}</div>
            <div class="score-label" style="color:{p_color}">{p_label}</div>
            <div style="background:rgba(255,255,255,0.08);border-radius:99px;
                 height:8px;width:100%;margin:10px 0 4px 0">
                <div style="width:{p_pct}%;height:8px;border-radius:99px;
                     background:{p_color};transition:width 0.4s"></div>
            </div>
            <div style="font-size:0.68rem;color:#6ee7b7">Higher = Cleaner Air</div>
        </div>
        """, unsafe_allow_html=True)

    with sc2:
        w_color, w_label = score_color(weather_score)
        st.markdown(f"""
        <div class="score-container">
            <div style="font-size:0.7rem;letter-spacing:2px;color:#6ee7b7;
                 text-transform:uppercase;margin-bottom:6px">⛅ Weather Score</div>
            <div class="score-number" style="color:{w_color}">{weather_score}</div>
            <div class="score-label" style="color:{w_color}">{w_label}</div>
            <div style="background:rgba(255,255,255,0.08);border-radius:99px;
                 height:8px;width:100%;margin:10px 0 4px 0">
                <div style="width:{weather_score}%;height:8px;border-radius:99px;
                     background:{w_color};transition:width 0.4s"></div>
            </div>
            <div style="font-size:0.68rem;color:#6ee7b7">Based on temp, wind, UV, rain</div>
        </div>
        """, unsafe_allow_html=True)

    with sc3:
        st.markdown(f"""
        <div class="score-container" style="border-color:rgba(74,222,128,0.5)">
            <div style="font-size:0.7rem;letter-spacing:2px;color:#6ee7b7;
                 text-transform:uppercase;margin-bottom:6px">🌿 Overall Env Score</div>
            <div class="score-number" style="color:{s_color}">{env_score}</div>
            <div class="score-label" style="color:{s_color}">{s_label}</div>
            <div style="background:rgba(255,255,255,0.08);border-radius:99px;
                 height:8px;width:100%;margin:10px 0 4px 0">
                <div style="width:{env_score}%;height:8px;border-radius:99px;
                     background:{s_color};transition:width 0.4s"></div>
            </div>
            <div style="font-size:0.68rem;color:#6ee7b7">55% Weather + 45% Air Quality</div>
        </div>
        """, unsafe_allow_html=True)

    # ── AIR QUALITY DETAILS ────────────────────────────────
    st.markdown('<div class="section-title">💨 Air Quality Breakdown</div>', unsafe_allow_html=True)

    if aq_cur:
        pm25 = aq_cur.get("pm2_5", 0) or 0
        pm10 = aq_cur.get("pm10", 0) or 0
        no2  = aq_cur.get("nitrogen_dioxide", 0) or 0
        so2  = aq_cur.get("sulphur_dioxide", 0) or 0
        o3   = aq_cur.get("ozone", 0) or 0
        co   = aq_cur.get("carbon_monoxide", 0) or 0
        eu_aqi = aq_cur.get("european_aqi", 0) or 0
        us_aqi = aq_cur.get("us_aqi", 0) or 0

        def bar_color(val, good, bad):
            if val <= good: return "#4ade80"
            elif val <= bad: return "#facc15"
            else: return "#ef4444"

        aq1, aq2 = st.columns(2)
        with aq1:
            pm25c = bar_color(pm25, 12, 35)
            pm10c = bar_color(pm10, 20, 50)
            no2c  = bar_color(no2, 40, 100)
            st.markdown(f"""
            <div class="metric-card">
                <h4>🔴 PM2.5 — Fine Particles</h4>
                <span class="value" style="color:{pm25c};font-size:1.8rem">{pm25:.1f}</span>
                <span class="unit">μg/m³</span>
                <div class="bar-bg"><div class="bar-fill" style="width:{min(100,int(pm25/2.5))}%;background:{pm25c}"></div></div>

                <h4>🟠 PM10 — Coarse Particles</h4>
                <span class="value" style="color:{pm10c};font-size:1.8rem">{pm10:.1f}</span>
                <span class="unit">μg/m³</span>
                <div class="bar-bg"><div class="bar-fill" style="width:{min(100,int(pm10/1.5))}%;background:{pm10c}"></div></div>

                <h4>🟡 Nitrogen Dioxide (NO₂)</h4>
                <span class="value" style="color:{no2c};font-size:1.8rem">{no2:.1f}</span>
                <span class="unit">μg/m³</span>
                <div class="bar-bg"><div class="bar-fill" style="width:{min(100,int(no2))}%;background:{no2c}"></div></div>
            </div>
            """, unsafe_allow_html=True)

        with aq2:
            so2c = bar_color(so2, 20, 80)
            o3c  = bar_color(o3, 60, 120)
            st.markdown(f"""
            <div class="metric-card">
                <h4>🟤 Sulphur Dioxide (SO₂)</h4>
                <span class="value" style="color:{so2c};font-size:1.8rem">{so2:.1f}</span>
                <span class="unit">μg/m³</span>
                <div class="bar-bg"><div class="bar-fill" style="width:{min(100,int(so2))}%;background:{so2c}"></div></div>

                <h4>🔵 Ozone (O₃)</h4>
                <span class="value" style="color:{o3c};font-size:1.8rem">{o3:.1f}</span>
                <span class="unit">μg/m³</span>
                <div class="bar-bg"><div class="bar-fill" style="width:{min(100,int(o3/1.8))}%;background:{o3c}"></div></div>

                <h4>⚫ Carbon Monoxide (CO)</h4>
                <span class="value" style="font-size:1.8rem">{co/1000:.2f}</span>
                <span class="unit">mg/m³</span>

                <div style="display:flex;gap:1rem;margin-top:0.8rem">
                    <div>
                        <div style="font-size:0.7rem;color:#6ee7b7;letter-spacing:1px">EU AQI</div>
                        <div style="font-size:1.4rem;font-weight:700;color:#d1fae5">{eu_aqi}</div>
                    </div>
                    <div>
                        <div style="font-size:0.7rem;color:#6ee7b7;letter-spacing:1px">US AQI</div>
                        <div style="font-size:1.4rem;font-weight:700;color:#d1fae5">{us_aqi}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Air quality data not available for this location.")

    # ── WEATHER METRICS ────────────────────────────────────
    st.markdown('<div class="section-title">Current Weather Conditions</div>', unsafe_allow_html=True)
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    for col, icon, label, val, unit in [
        (c1,"🌡️","Temperature", f"{cur['temperature_2m']:.1f}","°C"),
        (c2,"💧","Humidity",    f"{cur['relative_humidity_2m']}","%"),
        (c3,"💨","Wind Speed",  f"{cur['wind_speed_10m']:.1f}","km/h"),
        (c4,"🌧️","Precipitation",f"{cur['precipitation']:.1f}","mm"),
        (c5,"☀️","UV Index",    f"{cur.get('uv_index',0) or 0:.0f}",""),
        (c6,"🌡️","Feels Like",  f"{cur['apparent_temperature']:.1f}","°C"),
    ]:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <h4>{icon} {label}</h4>
                <span class="value">{val}</span><span class="unit">{unit}</span>
            </div>
            """, unsafe_allow_html=True)

    c7,c8 = st.columns(2)
    with c7:
        st.markdown(f'<div class="metric-card"><h4>🌫️ Cloud Cover</h4><span class="value">{cur["cloud_cover"]}</span><span class="unit">%</span></div>', unsafe_allow_html=True)
    with c8:
        st.markdown(f'<div class="metric-card"><h4>📊 Surface Pressure</h4><span class="value">{cur["surface_pressure"]:.0f}</span><span class="unit">hPa</span></div>', unsafe_allow_html=True)

    # ── 7-DAY FORECAST ─────────────────────────────────────
    st.markdown('<div class="section-title">7-Day Forecast</div>', unsafe_allow_html=True)
    forecast_rows = []
    for i, day in enumerate(daily["time"]):
        d = datetime.strptime(day, "%Y-%m-%d")
        forecast_rows.append({
            "Date":      d.strftime("%a %d %b"),
            "Max °C":    f"{daily['temperature_2m_max'][i]:.1f}",
            "Min °C":    f"{daily['temperature_2m_min'][i]:.1f}",
            "Rain mm":   f"{daily['precipitation_sum'][i]:.1f}",
            "Rain %":    f"{daily['precipitation_probability_max'][i]}%",
            "Wind km/h": f"{daily['wind_speed_10m_max'][i]:.1f}",
            "UV":        f"{daily['uv_index_max'][i]:.0f}",
        })
    st.dataframe(pd.DataFrame(forecast_rows), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════
# TAB 2 — CRISIS FORECAST
# ══════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">Environmental Crisis Prediction</div>', unsafe_allow_html=True)
    st.caption("Real-time analysis of weather and air quality data.")

    for level, msg in predict_crises(weather, aq_cur):
        if level == "crisis":
            st.markdown(f'<div class="alert-crisis"><b>🚨 HIGH RISK</b><br>{msg}</div>', unsafe_allow_html=True)
        elif level == "warning":
            st.markdown(f'<div class="alert-warning"><b>⚠️ ADVISORY</b><br>{msg}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="alert-safe">{msg}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">AI Deep Analysis</div>', unsafe_allow_html=True)
    if st.button("🤖 Generate AI Crisis Report", type="primary"):
        summary = {
            "location": f"{city}, {country}",
            "temp": cur["temperature_2m"],
            "humidity": cur["relative_humidity_2m"],
            "wind": cur["wind_speed_10m"],
            "aqi_eu": aq_cur.get("european_aqi"),
            "pm2_5": aq_cur.get("pm2_5"),
            "pm10": aq_cur.get("pm10"),
            "pollution_score": pollution_score,
            "weather_score": weather_score,
            "overall_env_score": env_score,
            "7d_max_temps": daily["temperature_2m_max"],
            "7d_rain_mm": daily["precipitation_sum"],
        }
        with st.spinner("Generating AI analysis..."):
            result = ask_groq(
                f"Analyse weather+pollution data for {city}: {json.dumps(summary,indent=2)}\n\nProvide: 1) Risk assessment 2) Agriculture impact 3) Farmer action steps 4) 30-day outlook. Be specific.",
                system="You are an expert environmental and agricultural analyst. Be concise and actionable."
            )
            st.markdown(f'<div style="background:rgba(255,255,255,0.04);border:1px solid rgba(74,222,128,0.2);border-radius:14px;padding:1.2rem 1.4rem;color:#e8f4e8;line-height:1.7">{result.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# TAB 3 — CROP ADVISOR
# ══════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">Recommended Crops</div>', unsafe_allow_html=True)
    st.caption(f"{city.title()}: {cur['temperature_2m']:.1f}°C · {cur['relative_humidity_2m']}% humidity · Pollution Score {pollution_score or 'N/A'}")

    crops = recommend_crops(weather)
    if crops:
        for name, score, reason, care in crops:
            st.markdown(f"""
            <div class="crop-card">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <span class="crop-name">{name}</span>
                    <span class="crop-score">Match {score}%</span>
                </div>
                <div style="color:#a7f3d0;font-size:0.85rem;margin-top:6px">{reason}</div>
                <div style="color:#6ee7b7;font-size:0.8rem;margin-top:4px">📋 {care}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No crop recommendations for current conditions.")

    st.markdown('<div class="section-title">AI Crop Management Plan</div>', unsafe_allow_html=True)
    selected_crop = st.selectbox("Choose a crop", [c[0] for c in crops] if crops else ["No crops available"])

    if st.button("📋 Generate Management Plan", type="primary") and crops:
        with st.spinner("Generating plan..."):
            result = ask_groq(
                f"""Detailed management plan for {selected_crop} in {city}, {country}.
Conditions: {cur['temperature_2m']:.1f}°C, {cur['relative_humidity_2m']}% humidity,
UV {cur.get('uv_index',0) or 0:.0f}, Wind {cur['wind_speed_10m']:.1f} km/h,
AQI {aq_cur.get('european_aqi','N/A')}, PM2.5 {aq_cur.get('pm2_5','N/A')} μg/m³.
Include: sowing, irrigation, fertilisation, pest watch, pollution impact, harvest timeline.""",
                system="You are an expert agronomist. Practical advice for small to medium farms."
            )
            st.markdown(f'<div style="background:rgba(255,255,255,0.04);border:1px solid rgba(74,222,128,0.2);border-radius:14px;padding:1.2rem 1.4rem;color:#e8f4e8;line-height:1.7">{result.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# TAB 4 — CHATBOT
# ══════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">Crop Care Chatbot</div>', unsafe_allow_html=True)
    st.caption("Ask anything about crop care, pests, irrigation, soil health, or pollution effects.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    crop_ctx = st.text_input("🌱 Specify a crop (optional)", placeholder="e.g. Tomato, Rice, Wheat...")

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-bubble-user">🧑‍🌾 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble-ai">🌿 {msg["content"]}</div>', unsafe_allow_html=True)

    user_input = st.chat_input("Ask about crop care, soil, pests, irrigation, pollution...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.spinner("Thinking..."):
            reply = ask_groq_chat(
                st.session_state.chat_history,
                system=f"""You are Aeroveda's expert crop advisor.
Location: {city}, {country}
Weather: {cur['temperature_2m']:.1f}°C, {cur['relative_humidity_2m']}% humidity, {weather_description(cur['weather_code'])}
Air Quality: AQI {aq_cur.get('european_aqi','N/A')}, Pollution Score {pollution_score or 'N/A'}
{'Crop focus: ' + crop_ctx if crop_ctx else ''}
Be concise and practical. Use bullet points."""
            )
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
