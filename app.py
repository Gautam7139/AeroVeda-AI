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

# ─── Weather Fetcher ─────────────────────────────────────────────────────────
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

# ─── Helpers ─────────────────────────────────────────────────────────────────
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

def compute_env_score(w):
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

def score_color(score):
    if score >= 75:   return "#4ade80", "EXCELLENT"
    elif score >= 55: return "#a3e635", "GOOD"
    elif score >= 35: return "#facc15", "MODERATE"
    else:             return "#ef4444", "POOR"

def predict_crises(w):
    alerts = []
    daily = w["daily"]
    hot_days = sum(1 for t in daily["temperature_2m_max"] if t and t > 38)
    if hot_days >= 3:
        alerts.append(("crisis", f"🌡️ Heat Wave Risk — {hot_days} days forecast above 38°C. Risk of crop stress and wildfires."))
    elif hot_days >= 1:
        alerts.append(("warning", f"🌡️ High Temperature Alert — {hot_days} days above 38°C expected."))
    total_precip = sum(p for p in daily["precipitation_sum"] if p is not None)
    if total_precip < 2:
        alerts.append(("crisis", "🏜️ Drought Risk — Near-zero rainfall forecast over 7 days. Irrigation critical."))
    elif total_precip < 8:
        alerts.append(("warning", "💧 Low Rainfall — Minimal precipitation expected. Monitor soil moisture."))
    heavy_rain_days = sum(1 for p in daily["precipitation_sum"] if p and p > 25)
    if heavy_rain_days >= 2:
        alerts.append(("crisis", f"🌊 Flood Risk — {heavy_rain_days} days with >25mm rainfall forecast."))
    elif heavy_rain_days == 1:
        alerts.append(("warning", "🌧️ Heavy Rain Alert — Waterlogging possible. Ensure drainage."))
    max_wind = max((v for v in daily["wind_speed_10m_max"] if v), default=0)
    if max_wind > 70:
        alerts.append(("crisis", f"💨 Storm Wind Alert — Gusts up to {max_wind:.0f} km/h. Secure crops."))
    elif max_wind > 45:
        alerts.append(("warning", f"💨 High Wind Advisory — Up to {max_wind:.0f} km/h winds forecast."))
    max_uv = max((v for v in daily["uv_index_max"] if v), default=0)
    if max_uv > 10:
        alerts.append(("warning", f"☀️ Extreme UV Index ({max_uv:.0f}) — Risk of leaf scorch on sensitive crops."))
    if not alerts:
        alerts.append(("safe", "✅ No significant environmental crises forecast for the next 7 days."))
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
        crops.append(("🌾 Rice", 95, "Thrives in warm, humid conditions.", "High water; transplant seedlings; 3-4 month cycle."))
        crops.append(("🌿 Sugarcane", 88, "Loves heat and humidity.", "Deep watering weekly; fertilise monthly; 10-12 month crop."))
    if 18 <= temp <= 35:
        crops.append(("🥜 Groundnut", 85, "Well-suited to current temperatures.", "Light, well-drained soil; needs dry spell at end."))
        crops.append(("🌽 Maize", 82, "Good temperature match.", "Moderate irrigation; nitrogen-rich fertiliser; 90-day cycle."))
    if temp >= 25 and humidity < 70:
        crops.append(("🍅 Tomato", 78, "Warm and dry — tomatoes will thrive.", "Stake plants; consistent watering; watch for blight."))
        crops.append(("🌶️ Chilli", 76, "Ideal warm and dry conditions.", "Drip irrigation preferred; high potassium for fruiting."))
    if temp < 22:
        crops.append(("🥬 Spinach", 90, "Cool temperatures perfect for leafy greens.", "Sow directly; harvest in 6-8 weeks; high nitrogen."))
        crops.append(("🥕 Carrot", 84, "Cool soil promotes good root development.", "Deep loose soil; thin seedlings; 70-80 day crop."))
        crops.append(("🧅 Onion", 80, "Cool dry weather suits bulb development.", "Well-drained beds; reduce water at bulbing stage."))
    if avg_rain < 3 and temp > 20:
        crops.append(("🌻 Sunflower", 88, "Drought-tolerant and heat-resistant.", "Deep taproot; minimal irrigation; 80-95 day cycle."))
        crops.append(("🫘 Moong Dal", 83, "Excellent drought tolerance.", "Sandy loam; minimal inputs; harvest in 60-70 days."))
    crops.sort(key=lambda x: -x[1])
    return crops[:5]

# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="aeroveda-header">
    <h1>🌿 Aeroveda</h1>
    <p>Intelligent Agricultural & Environmental Intelligence</p>
</div>
""", unsafe_allow_html=True)

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📍 Location")

    # Step 1: GPS button — asks browser for coordinates
    components.html("""
        <button onclick="
            navigator.geolocation.getCurrentPosition(function(pos) {
                const val = pos.coords.latitude + ',' + pos.coords.longitude;
                localStorage.setItem('aeroveda_gps', val);
                document.getElementById('gps-status').innerText = '✅ Got location! Now click Load below.';
            }, function(err) {
                document.getElementById('gps-status').innerText = '❌ Permission denied. Type city manually.';
            });
        " style="
            background: linear-gradient(135deg, #16a34a, #4ade80);
            border: none; border-radius: 10px; color: #052e16;
            font-weight: 600; padding: 0.5rem 1rem;
            cursor: pointer; width: 100%; font-size: 0.9rem;
        ">📍 Use My Location</button>
        <div id="gps-status" style="color:#6ee7b7;font-size:0.78rem;margin-top:6px;"></div>
    """, height=70)

    # Step 2: Read GPS coords from query param passed via URL
    gps_coords = st.query_params.get("gps", "")
    if gps_coords and "," in gps_coords:
        try:
            gps_lat, gps_lon = map(float, gps_coords.split(","))
            city_detected = reverse_geocode(gps_lat, gps_lon)
            if city_detected:
                st.session_state.detected_city = city_detected
        except:
            pass

    # Step 3: Manual load button
    if st.button("🔄 Load My Location"):
        st.markdown("""
        <script>
        const gps = localStorage.getItem('aeroveda_gps');
        if (gps) {
            const url = new URL(window.location.href);
            url.searchParams.set('gps', gps);
            window.location.href = url.toString();
        } else {
            alert('Click "Use My Location" first and allow location access!');
        }
        </script>
        """, unsafe_allow_html=True)

    default_city = st.session_state.get("detected_city", "Bengaluru")
    city = st.text_input("Or type a city", value=default_city, placeholder="e.g. Delhi, Pune...")

    st.markdown("---")
    st.markdown("""
    <div style="color:#6ee7b7;font-size:0.78rem;line-height:1.8">
    <b>Data Sources</b><br>
    🌤 Open-Meteo (weather)<br>
    🤖 Groq AI — LLaMA 3.3 70B<br>
    📡 Real-time 7-day forecast
    </div>
    """, unsafe_allow_html=True)

# ─── Geocode & Fetch ─────────────────────────────────────────────────────────
geo = geocode_city(city)
if not geo:
    st.error(f"Could not find location: **{city}**. Try a different city name.")
    st.stop()

lat, lon, country = geo
weather = fetch_weather(lat, lon)
if not weather:
    st.stop()

cur = weather["current"]
daily = weather["daily"]

# ─── Tabs ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["🌤 Dashboard", "⚠️ Crisis Forecast", "🌾 Crop Advisor", "💬 Chatbot"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    env_score = compute_env_score(weather)
    s_color, s_label = score_color(env_score)

    loc_col, score_col = st.columns([2, 1])
    with loc_col:
        st.markdown(f"""
        <div style="padding:1.2rem;background:rgba(255,255,255,0.04);
             border:1px solid rgba(74,222,128,0.2);border-radius:16px;margin-bottom:1rem">
            <div style="font-size:0.75rem;letter-spacing:2px;color:#6ee7b7;text-transform:uppercase">
                Current Location
            </div>
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

    with score_col:
        st.markdown(f"""
        <div class="score-container">
            <div style="font-size:0.72rem;letter-spacing:2px;color:#6ee7b7;
                 text-transform:uppercase;margin-bottom:8px">
                Environmental Score
            </div>
            <div class="score-number" style="color:{s_color}">{env_score}</div>
            <div class="score-label" style="color:{s_color}">{s_label}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Current Conditions</div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    metrics = [
        (c1, "🌡️", "Temperature",  f"{cur['temperature_2m']:.1f}",             "°C"),
        (c2, "💧", "Humidity",      f"{cur['relative_humidity_2m']}",            "%"),
        (c3, "💨", "Wind Speed",    f"{cur['wind_speed_10m']:.1f}",              "km/h"),
        (c4, "🌧️", "Precipitation", f"{cur['precipitation']:.1f}",               "mm"),
        (c5, "☀️", "UV Index",      f"{cur.get('uv_index', 0) or 0:.0f}",        ""),
        (c6, "🌡️", "Feels Like",   f"{cur['apparent_temperature']:.1f}",        "°C"),
    ]
    for col, icon, label, val, unit in metrics:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <h4>{icon} {label}</h4>
                <span class="value">{val}</span><span class="unit">{unit}</span>
            </div>
            """, unsafe_allow_html=True)

    c7, c8 = st.columns(2)
    with c7:
        st.markdown(f"""
        <div class="metric-card">
            <h4>🌫️ Cloud Cover</h4>
            <span class="value">{cur['cloud_cover']}</span><span class="unit">%</span>
        </div>
        """, unsafe_allow_html=True)
    with c8:
        st.markdown(f"""
        <div class="metric-card">
            <h4>📊 Surface Pressure</h4>
            <span class="value">{cur['surface_pressure']:.0f}</span><span class="unit">hPa</span>
        </div>
        """, unsafe_allow_html=True)

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

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — CRISIS FORECAST
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">Environmental Crisis Prediction</div>', unsafe_allow_html=True)
    st.caption("Analysis of 7-day forecast data to detect potential crises before they occur.")

    for level, msg in predict_crises(weather):
        if level == "crisis":
            st.markdown(f'<div class="alert-crisis"><b>🚨 HIGH RISK</b><br>{msg}</div>', unsafe_allow_html=True)
        elif level == "warning":
            st.markdown(f'<div class="alert-warning"><b>⚠️ ADVISORY</b><br>{msg}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="alert-safe">{msg}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">AI Deep Analysis</div>', unsafe_allow_html=True)
    if st.button("🤖 Generate AI Crisis Report", type="primary"):
        weather_summary = {
            "location": f"{city}, {country}",
            "current_temp": cur["temperature_2m"],
            "humidity": cur["relative_humidity_2m"],
            "wind": cur["wind_speed_10m"],
            "precipitation": cur["precipitation"],
            "7_day_max_temps": daily["temperature_2m_max"],
            "7_day_precipitation": daily["precipitation_sum"],
            "7_day_wind_max": daily["wind_speed_10m_max"],
        }
        prompt = f"""Analyse this 7-day weather data for {city} and provide:
1. Risk assessment (heat, drought, flood, storm, frost)
2. Specific impact on agriculture
3. Recommended immediate actions for farmers
4. 30-day outlook

Weather data: {json.dumps(weather_summary, indent=2)}

Be specific and actionable."""

        with st.spinner("Generating AI analysis..."):
            result = ask_groq(
                prompt,
                system="You are an expert environmental analyst for agricultural regions. Be specific, practical and concise."
            )
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(74,222,128,0.2);
                 border-radius:14px;padding:1.2rem 1.4rem;color:#e8f4e8;line-height:1.7">
            {result.replace(chr(10), '<br>')}
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CROP ADVISOR
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">Recommended Crops</div>', unsafe_allow_html=True)
    st.caption(f"Based on current conditions in {city}: {cur['temperature_2m']:.1f}°C, {cur['relative_humidity_2m']}% humidity.")

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
        st.info("No crop recommendations available for current conditions.")

    st.markdown('<div class="section-title">AI Crop Management Plan</div>', unsafe_allow_html=True)
    selected_crop = st.selectbox(
        "Choose a crop for a detailed plan",
        [c[0] for c in crops] if crops else ["No crops available"]
    )

    if st.button("📋 Generate Management Plan", type="primary") and crops:
        prompt = f"""Provide a detailed crop management plan for:
Crop: {selected_crop}
Location: {city}, {country}
Temperature: {cur['temperature_2m']:.1f}°C
Humidity: {cur['relative_humidity_2m']}%
Rainfall: {cur['precipitation']:.1f}mm
UV Index: {cur.get('uv_index', 0) or 0:.0f}
Wind: {cur['wind_speed_10m']:.1f} km/h

Include:
1. Sowing/planting guidelines
2. Irrigation schedule
3. Fertilisation plan
4. Pest & disease watch
5. Harvest timeline
6. Special weather precautions"""

        with st.spinner("Generating management plan..."):
            result = ask_groq(
                prompt,
                system="You are an expert agronomist. Give specific, practical advice for small to medium farms."
            )
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(74,222,128,0.2);
                 border-radius:14px;padding:1.2rem 1.4rem;color:#e8f4e8;line-height:1.7">
            {result.replace(chr(10), '<br>')}
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — CHATBOT
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">Crop Care Chatbot</div>', unsafe_allow_html=True)
    st.caption("Ask anything about crop care, pest management, irrigation, soil health, or farming advice.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    crop_ctx = st.text_input("🌱 Specify a crop (optional)", placeholder="e.g. Tomato, Rice, Wheat...")

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-bubble-user">🧑‍🌾 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble-ai">🌿 {msg["content"]}</div>', unsafe_allow_html=True)

    user_input = st.chat_input("Ask about crop care, soil, pests, irrigation...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        system_prompt = f"""You are Aeroveda's expert crop care advisor — an experienced agronomist.
Location: {city}, {country}
Weather: {cur['temperature_2m']:.1f}°C, {cur['relative_humidity_2m']}% humidity, {weather_description(cur['weather_code'])}
{'Focused crop: ' + crop_ctx if crop_ctx else ''}
Be concise, practical, and specific. Use bullet points where helpful."""

        with st.spinner("Thinking..."):
            reply = ask_groq_chat(
                st.session_state.chat_history,
                system=system_prompt,
                max_tokens=700
            )

        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
