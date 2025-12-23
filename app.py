import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
import utils

# --------------------------------------------------
# Load environment variables (.env for local testing)
# --------------------------------------------------
load_dotenv()

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="AQI Analyst MVP",
    page_icon="🌤️",
    layout="wide"
)

st.title("🌤️ Spatio-Temporal AQI Analysis & Forecasting (MVP)")
st.write(
    "Upload a CSV file to analyze air quality trends using **Google Gemini**. "
    "This is a research-oriented MVP focusing on AI-based reasoning."
)

# --------------------------------------------------
# Sidebar: Configuration
# --------------------------------------------------
st.sidebar.header("Configuration")

# API Key: environment variable first, fallback to user input
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

uploaded_file = st.sidebar.file_uploader(
    "Upload AQI Dataset (CSV)",
    type=["csv"]
)

# --------------------------------------------------
# Session State Initialization
# --------------------------------------------------
if "data_summary" not in st.session_state:
    st.session_state.data_summary = None

if "trend_response" not in st.session_state:
    st.session_state.trend_response = None

if "city_response" not in st.session_state:
    st.session_state.city_response = None

if "forecast_response" not in st.session_state:
    st.session_state.forecast_response = None

# --------------------------------------------------
# Main Application Logic
# --------------------------------------------------
if uploaded_file is not None:
    try:
        # Load and validate data
        df = utils.load_data(uploaded_file)

        # Sort data by Date (important for time series)
        df = df.sort_values("Date")

        # -----------------------------
        # Section 1: Data Preview
        # -----------------------------
        st.subheader("1️⃣ Data Preview")
        st.dataframe(df.head())

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Cities", df["City"].nunique())
        col_b.metric("Records", len(df))
        col_c.metric(
            "Date Range",
            f"{df['Date'].min().date()} → {df['Date'].max().date()}"
        )

        # -----------------------------
        # Section 2: AQI Visualization
        # -----------------------------
        st.subheader("2️⃣ AQI Trends Visualization")

        chart_data = df.pivot_table(
            index="Date",
            columns="City",
            values="AQI",
            aggfunc="mean"
        )
        st.line_chart(chart_data)

        # -----------------------------
        # Section 3: AI-Powered Insights
        # -----------------------------
        st.subheader("3️⃣ AI-Powered Insights")

        if not api_key:
            st.warning(
                "⚠️ Please enter your Google Gemini API Key in the sidebar "
                "to enable AI analysis."
            )
        else:
            # Generate data summary once
            if st.session_state.data_summary is None:
                st.session_state.data_summary = utils.summarize_data(df)

            data_summary = st.session_state.data_summary

            col1, col2, col3 = st.columns(3)

            # -------- Button 1: Analyze Trends --------
            with col1:
                if st.button("📈 Analyze Trends"):
                    with st.spinner("Analyzing temporal trends with Gemini..."):
                        prompt = (
                            "You are an environmental data analyst.\n\n"
                            "Analyze the following AQI data summary and identify:\n"
                            "- Overall AQI trend (increasing/decreasing)\n"
                            "- Seasonal patterns\n"
                            "- Any notable pollution spikes\n\n"
                            "Do not provide numeric predictions.\n\n"
                            f"{data_summary}"
                        )
                        st.session_state.trend_response = utils.get_gemini_response(
                            prompt, api_key
                        )

            if st.session_state.trend_response:
                st.markdown("### 📈 Trend Analysis")
                st.write(st.session_state.trend_response)

            # -------- Button 2: Compare Cities --------
            with col2:
                if st.button("🏙️ Compare Cities"):
                    with st.spinner("Comparing cities with Gemini..."):
                        prompt = (
                            "You are an environmental scientist.\n\n"
                            "Using the AQI data summary below:\n"
                            "- Compare air quality across cities\n"
                            "- Identify which city is generally cleaner\n"
                            "- Identify which city shows the most variability\n\n"
                            "Base your reasoning strictly on the summary.\n\n"
                            f"{data_summary}"
                        )
                        st.session_state.city_response = utils.get_gemini_response(
                            prompt, api_key
                        )

            if st.session_state.city_response:
                st.markdown("### 🏙️ City Comparison")
                st.write(st.session_state.city_response)

            # -------- Button 3: Forecast AQI --------
            with col3:
                if st.button("🔮 Forecast AQI"):
                    with st.spinner("Forecasting AQI outlook with Gemini..."):
                        prompt = (
                            "Based on the historical AQI trends in the summary below:\n\n"
                            "Predict ONLY the qualitative AQI outlook for the next month.\n"
                            "Choose exactly ONE label:\n"
                            "- IMPROVE\n"
                            "- WORSEN\n"
                            "- STABLE\n\n"
                            "Do NOT provide numeric values.\n"
                            "After the label, give a short explanation.\n\n"
                            f"{data_summary}"
                        )
                        st.session_state.forecast_response = utils.get_gemini_response(
                            prompt, api_key
                        )

            if st.session_state.forecast_response:
                st.markdown("### 🔮 Future AQI Outlook")
                st.write(st.session_state.forecast_response)

        st.caption(
            "⚠️ Note: AI-generated insights are interpretive and intended "
            "for academic and research purposes only."
        )

    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

else:
    st.info(
        "⬅️ Upload a CSV file from the sidebar to begin.\n\n"
        "The dataset must contain **Date**, **City**, and **AQI** columns."
    )
