# 🌤️ Spatio-Temporal AQI Analysis & Forecasting

A data-driven web application for **historical air quality analysis** and **real-time AQI monitoring**, powered by **Google Gemini AI** and **OpenWeatherMap**.  
This project enables users to explore AQI trends, compare cities, understand health impacts, and view short-term air quality outlooks through an intuitive interface.

---

## 🚀 Project Overview

Air pollution is a critical environmental and public health challenge.  
This project aims to:

- Analyze **historical AQI datasets** to uncover patterns and trends
- Provide **AI-powered insights** for interpretation and decision-making
- Enable **real-time AQI lookup** for any city worldwide
- Present **qualitative short-term AQI outlooks** (next 24–48 hours)
- Bridge **data science + AI reasoning + environmental awareness**

The system is designed as a **research-oriented analytical tool**, not just a dashboard.

---

## ✨ Key Features

### 📊 AQI Analysis (Historical Data)
- Upload AQI CSV datasets (`Date`, `City`, `AQI`)
- Interactive AQI trend visualization
- AI-powered insights using Google Gemini:
  - 📈 Trend Analysis
  - 🏙️ City-wise Comparison
  - 🩺 Health Impact Assessment
  - 🔮 Qualitative AQI Forecast (Improve / Worsen / Stable)
- Insights are generated in **concise, research-grade bullet points**
- Spinner-based feedback during AI processing for better UX

---

### 🌍 Live AQI Lookup (Global)
- Fetch **real-time air quality data** for any city worldwide
- Powered by **OpenWeatherMap Air Pollution API**
- Displays:
  - Current AQI level
  - AQI category (Good, Fair, Moderate, Poor, Very Poor)
  - Pollutant components (PM2.5, PM10, CO, NO₂, O₃, SO₂, etc.)
  - Qualitative AQI outlook for the **next 24 and 48 hours**
- AI-generated explanation covering:
  - Current air quality condition
  - Short-term trend interpretation
  - General health implications
  - Precautionary advice

---

## 🧠 AI Integration

This project uses **Google Gemini** for:
- Interpreting AQI patterns
- Explaining trends in a research-oriented tone
- Providing health-related insights
- Generating qualitative forecasts without numeric speculation

> ⚠️ AI-generated insights are interpretive and intended for **academic and research purposes only**.

---

## 🛠️ Tech Stack

- **Frontend / UI**: Streamlit
- **Data Processing**: Pandas
- **AI Model**: Google Gemini (via `google.genai`)
- **Live AQI Data**: OpenWeatherMap API
- **Environment Management**: dotenv / Streamlit secrets
- **Language**: Python

---

## 📂 Project Structure


aqi-gemini/

|

├── app.py #Streamlit application

├── utils.py # Core logic (data processing, Gemini, AQI APIs)

├── requirements.txt # Ignored files

├── .gitignore # ignored files

├── README.md # Documentation


---

## 🔐 Environment Variables

Create a `.env` file (for local testing) or `.streamlit/secrets.toml` (for deployment) with the following:

```env
GEMINI_API_KEY=your_gemini_api_key
OPENWEATHER_API_KEY=your_openweather_api_key


---

## 🔐 Environment Variables

Create a `.env` file (for local testing) or `.streamlit/secrets.toml` (for deployment) with the following:

```env
GEMINI_API_KEY=your_gemini_api_key
OPENWEATHER_API_KEY=your_openweather_api_key

⚠️ Never commit API keys to GitHub.


