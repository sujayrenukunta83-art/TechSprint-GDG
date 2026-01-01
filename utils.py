import pandas as pd
import os
import requests
import google.genai as genai
import streamlit as st

# ===================== CSV ANALYSIS =====================

def load_data(file):
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()

    required = {"Date", "City", "AQI"}
    if not required.issubset(df.columns):
        raise ValueError("CSV must contain Date, City, AQI columns")

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["AQI"] = pd.to_numeric(df["AQI"], errors="coerce")
    df = df.dropna(subset=["Date", "AQI"])

    return df


def summarize_data(df):
    lines = []
    lines.append(f"Date Range: {df.Date.min().date()} to {df.Date.max().date()}")
    lines.append(f"Cities: {', '.join(df.City.unique())}")

    for city in df.City.unique():
        c = df[df.City == city]
        lines.append(
            f"{city} → Avg AQI {c.AQI.mean():.1f}, "
            f"Min {c.AQI.min():.1f}, Max {c.AQI.max():.1f}"
        )

    return "\n".join(lines)


def get_gemini_response(prompt):
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "Gemini API key missing."

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt
    )
    return response.text if response and response.text else "No response from Gemini."


# ===================== LIVE AQI (OPENWEATHER) =====================

def get_city_coordinates(city):
    key = os.getenv("OPENWEATHER_API_KEY")
    if not key:
        return {"error": "OpenWeather API key missing"}

    url = "https://api.openweathermap.org/geo/1.0/direct"
    r = requests.get(url, params={"q": city, "limit": 1, "appid": key}, timeout=10)

    if not r.json():
        return {"error": "City not found"}

    return {
        "lat": r.json()[0]["lat"],
        "lon": r.json()[0]["lon"]
    }


def fetch_air_pollution(lat, lon):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return {"error": "OpenWeather API key missing."}

    url = "https://api.openweathermap.org/data/2.5/air_pollution"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "list" not in data or not data["list"]:
            return {"error": "Air quality data unavailable from OpenWeather."}

        return {
            "current": data["list"][0],
            "forecast": data["list"][:3]  # approx next 48 hrs
        }

    except requests.exceptions.Timeout:
        return {"error": "OpenWeather request timed out."}
    except requests.exceptions.RequestException:
        return {"error": "Failed to connect to OpenWeather service."}


def fetch_live_aqi(city_name):
    """
    Returns:
    - current AQI
    - AQI category
    - pollutant components
    - Next 24h and following 24h outlook (TEXT)
    """

    location = get_city_coordinates(city_name)
    if "error" in location:
        return {"error": "Failed to resolve city location."}

    pollution = fetch_air_pollution(location["lat"], location["lon"])
    if "error" in pollution:
        return {"error": "Failed to fetch air pollution data."}

    if "current" not in pollution:
        return {"error": "Air quality data unavailable at the moment."}

    current = pollution["current"]
    components = current.get("components", {})

    aqi_value = current.get("main", {}).get("aqi")

    aqi_category_map = {
        1: "Good",
        2: "Fair",
        3: "Moderate",
        4: "Poor",
        5: "Very Poor"
    }

    category_now = aqi_category_map.get(aqi_value, "Unknown")

    forecast_list = pollution.get("forecast", [])

    # Default values
    category_24h = category_now
    category_48h = category_now

    if len(forecast_list) >= 1:
        category_24h = aqi_category_map.get(
            forecast_list[0]["main"]["aqi"], category_now
        )

    if len(forecast_list) >= 2:
        category_48h = aqi_category_map.get(
            forecast_list[1]["main"]["aqi"], category_now
        )

    # ✅ EXACT FORMAT YOU WANT
    forecast_text = (
        f"Next 24 Hours: {category_24h}\n"
        f"Following 24 Hours: {category_48h}"
    )

    return {
        "aqi": aqi_value,
        "category": category_now,
        "components": components,
        "forecast_text": forecast_text,
        "next_2_days_trend": forecast_text,
        "forecast": forecast_list
    }


# ===================== UI HELPERS =====================

def display_components(components):
    cols = st.columns(4)

    pollutants = [
        ("CO", components.get("co")),
        ("NO", components.get("no")),
        ("NO₂", components.get("no2")),
        ("O₃", components.get("o3")),
        ("SO₂", components.get("so2")),
        ("PM2.5", components.get("pm2_5")),
        ("PM10", components.get("pm10")),
        ("NH₃", components.get("nh3")),
    ]

    for i, (name, value) in enumerate(pollutants):
        with cols[i % 4]:
            st.metric(name, f"{value}" if value is not None else "N/A")

