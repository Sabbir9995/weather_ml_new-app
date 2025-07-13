
import streamlit as st
import pandas as pd
import altair as alt
from fpdf import FPDF
import base64
import tempfile
from datetime import datetime
import random

st.set_page_config(page_title="Weather Range Report Generator", layout="wide")
st.title("📈 Weather Forecasting (Range-Based Prediction & Report)")

st.sidebar.header("📅 Select Date Range")
start_year = st.sidebar.number_input("Start Year", min_value=1961, max_value=2025, value=2022)
start_month = st.sidebar.number_input("Start Month", min_value=1, max_value=12, value=1)
end_year = st.sidebar.number_input("End Year", min_value=1961, max_value=2025, value=2023)
end_month = st.sidebar.number_input("End Month", min_value=1, max_value=12, value=12)

st.sidebar.header("🌦️ Input Parameters")
humidity = st.sidebar.slider("Humidity (%)", 0, 100, 75)
max_temp = st.sidebar.slider("Max Temperature (°C)", 10, 50, 35)
min_temp = st.sidebar.slider("Min Temperature (°C)", 0, 40, 22)
sunshine = st.sidebar.slider("Sunshine (hours)", 0, 15, 7)
cloud_coverage = st.sidebar.slider("Cloud Coverage (oktas)", 0, 100, 60)

def predict_weather(humidity, max_temp, min_temp, sunshine, cloud_coverage):
    if humidity > 80 and min_temp < 20:
        rainfall = 180 + random.uniform(-25, 25)
    elif humidity > 60 and max_temp < 35:
        rainfall = 80 + random.uniform(-20, 20)
    else:
        rainfall = 20 + random.uniform(-5, 5)

    if sunshine < 5 and cloud_coverage > 60:
        wind_speed = 4.0 + random.uniform(-0.5, 0.5)
    elif sunshine < 8 and cloud_coverage > 30:
        wind_speed = 2.5 + random.uniform(-0.4, 0.4)
    else:
        wind_speed = 1.0 + random.uniform(-0.25, 0.25)

    return round(rainfall, 2), round(wind_speed, 2)

# Generate data for the selected range
if st.button("🔮 Generate Forecast and Report"):
    try:
        date_range = pd.date_range(start=f"{start_year}-{start_month:02d}", end=f"{end_year}-{end_month:02d}", freq='MS')
        data = []

        for date in date_range:
            rainfall, wind_speed = predict_weather(humidity, max_temp, min_temp, sunshine, cloud_coverage)
            data.append({
                "Year": date.year,
                "Month": date.month,
                "Rainfall": rainfall,
                "WindSpeed": wind_speed
            })

        df = pd.DataFrame(data)

        st.subheader("📊 Predicted Data")
        st.dataframe(df)

        # Bar charts
        st.subheader("🌧️ Rainfall Prediction Chart")
        st.altair_chart(alt.Chart(df).mark_bar().encode(
            x=alt.X("Month:O", title="Month"),
            y=alt.Y("Rainfall:Q", title="Rainfall (mm)"),
            color="Year:N"
        ).properties(height=300), use_container_width=True)

        st.subheader("💨 Wind Speed Prediction Chart")
        st.altair_chart(alt.Chart(df).mark_bar().encode(
            x=alt.X("Month:O", title="Month"),
            y=alt.Y("WindSpeed:Q", title="Wind Speed (m/s)"),
            color="Year:N"
        ).properties(height=300), use_container_width=True)

        # Generate PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Weather Forecast Report", ln=True, align="C")
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Date Range: {start_year}-{start_month:02d} to {end_year}-{end_month:02d}", ln=True)
        pdf.cell(200, 10, txt=f"Humidity: {humidity}%, Max Temp: {max_temp}°C, Min Temp: {min_temp}°C", ln=True)
        pdf.cell(200, 10, txt=f"Sunshine: {sunshine} hrs, Cloud Coverage: {cloud_coverage}%", ln=True)
        pdf.ln(5)

        for _, row in df.iterrows():
            pdf.cell(200, 10, txt=f"{int(row['Year'])}-{int(row['Month']):02d} | Rainfall: {row['Rainfall']} mm | Wind: {row['WindSpeed']} m/s", ln=True)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
            pdf.output(tmpfile.name)
            tmpfile_path = tmpfile.name

        with open(tmpfile_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode("utf-8")
        href = f'<a href="data:application/octet-stream;base64,{base64_pdf}" download="weather_range_report.pdf">📥 Download PDF Report</a>'
        st.markdown(href, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error generating forecast: {e}")
