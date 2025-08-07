import streamlit as st
import boto3
import json
import pandas as pd
from datetime import datetime
from collections import defaultdict

# AWS S3 Configuration
BUCKET_NAME = "iot-sensor-data-bucket"

# Initialize Boto3 S3 client (uses IAM role or ~/.aws/credentials)
s3 = boto3.client("s3")


@st.cache_data(ttl=60)
def fetch_all_sensor_data():
    """Fetch and parse all sensor data from all folders in the S3 bucket."""
    paginator = s3.get_paginator("list_objects_v2")
    operation_parameters = {"Bucket": BUCKET_NAME}
    page_iterator = paginator.paginate(**operation_parameters)

    data = []

    for page in page_iterator:
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.endswith(".json"):
                obj_body = s3.get_object(Bucket=BUCKET_NAME, Key=key)["Body"].read().decode("utf-8")
                try:
                    record = json.loads(obj_body)
                    data.append(record)
                except json.JSONDecodeError:
                    st.warning(f"Could not parse JSON: {key}")

    return data


# UI - Title
st.title("📡 IoT Sensor Monitoring Dashboard")

with st.spinner("Fetching data from S3..."):
    records = fetch_all_sensor_data()

if not records:
    st.warning("No data found in S3 bucket.")
    st.stop()

# Convert to DataFrame
df = pd.DataFrame(records)

# Convert timestamp
df["timestamp"] = pd.to_datetime(df["timestamp_utc"])

# Show latest readings from each device
st.header("🟢 Latest Readings Per Device")

latest_readings = df.sort_values("timestamp").groupby("device_id").tail(1)
st.dataframe(latest_readings[["device_id", "timestamp_utc", "temperature_C", "pressure_kPa", "humidity_percent"]])

# Average reading plots
st.header("📈 Average Sensor Readings Over Time")

df_sorted = df.sort_values("timestamp")
df_grouped = df_sorted.groupby("timestamp").agg({
    "temperature_C": "mean",
    "pressure_kPa": "mean",
    "humidity_percent": "mean"
}).reset_index()

# Plot: Average Temperature
st.subheader("🌡️ Average Temperature (°C)")
st.line_chart(df_grouped.set_index("timestamp")["temperature_C"])

# Plot: Average Pressure
st.subheader("🧭 Average Pressure (kPa)")
st.line_chart(df_grouped.set_index("timestamp")["pressure_kPa"])

# Plot: Average Humidity
st.subheader("💧 Average Humidity (%)")
st.line_chart(df_grouped.set_index("timestamp")["humidity_percent"])
