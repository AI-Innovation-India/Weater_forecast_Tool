import os
import requests
import streamlit as st
from datetime import datetime

# Try to load dotenv only for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# -------------------------------
# Load API Key securely
# -------------------------------
API_KEY = os.getenv("OPENWEATHER_API_KEY")  # Local (.env)

if not API_KEY:  # If running on Streamlit Cloud
    try:
        API_KEY = st.secrets["api_keys"]["openweather"]
    except Exception:
        API_KEY = None

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


# -------------------------------
# Get weather data
# -------------------------------
def get_weather(city):
    if not API_KEY:
        return None

    params = {"q": city, "appid": API_KEY, "units": "metric"}
    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        # Show exact API error in Streamlit
        st.error(f"API error {response.status_code}: {response.text}")
        return None



# -------------------------------
# Alerts Logic
# -------------------------------
def get_alerts(weather_data):
    rain_alert = "Green"
    flood_alert = "Green"

    # Rain logic
    if "rain" in weather_data:
        rain_volume = weather_data["rain"].get("1h", 0)  # mm in last hour
        if rain_volume > 30:
            rain_alert = "Red"
        elif rain_volume > 10:
            rain_alert = "Yellow"

    # Flood logic (based on humidity + rain + clouds)
    humidity = weather_data["main"]["humidity"]
    if humidity > 85 and "rain" in weather_data:
        if rain_alert == "Red":
            flood_alert = "Red"
        elif rain_alert == "Yellow":
            flood_alert = "Yellow"

    return rain_alert, flood_alert


# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="Weather & Flood Alert", layout="centered")
st.title("🌦️ Weather Forecast & Alerts")

city = st.text_input("Enter City Name", "Mumbai")

if st.button("Get Weather"):
    if not API_KEY:
        st.error("❌ API key not found. Please set it in `.env` or Streamlit secrets.")
    else:
        weather_data = get_weather(city)

        if weather_data:
            st.subheader(f"📍 Weather in {city}")
            st.write(f"**Condition:** {weather_data['weather'][0]['description'].title()}")
            st.write(f"**Temperature:** {weather_data['main']['temp']} °C")
            st.write(f"**Humidity:** {weather_data['main']['humidity']}%")
            st.write(f"**Wind Speed:** {weather_data['wind']['speed']} m/s")
            st.write(f"**Cloudiness:** {weather_data['clouds']['all']}%")
            st.write(f"**Updated at:** {datetime.utcfromtimestamp(weather_data['dt']).strftime('%Y-%m-%d %H:%M:%S')} UTC")

            # Alerts
            rain_alert, flood_alert = get_alerts(weather_data)

            def show_alert(label, status):
                colors = {"Green": "🟢 Safe", "Yellow": "🟡 Moderate", "Red": "🔴 Severe"}
                st.markdown(f"**{label}:** {colors[status]}")

            st.subheader("🚨 Alerts")
            show_alert("Rain Alert", rain_alert)
            show_alert("Flood Alert", flood_alert)
        else:
            st.error("❌ Could not fetch weather data. Check city name or try again.")
