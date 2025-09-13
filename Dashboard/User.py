import streamlit as st
import pandas as pd
import sqlite3
import os
from cryptography.fernet import Fernet
import joblib
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Telematics User Dashboard",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded"
)
DB_FILE = "telematics.db"
KEY_FILE = "secret.key"
MODEL_PATH = "stacking_model.pkl"
OPENWEATHER_API_KEY = "your_openweather_api_key"  # Replace with your API key
LAT, LON = 37.5485, -121.9886  # Example: Fremont, CA coordinates

# ---------------- MODEL ----------------
model = joblib.load(MODEL_PATH)

def calculate_realistic_premium(risk_score, base_premium=2285, max_risk_score=100):
    normalized_risk = np.clip(risk_score / max_risk_score, 0, 1)
    scaling_factor = 1 + 0.5 * normalized_risk
    premium_annual = base_premium * scaling_factor
    premium_monthly = premium_annual / 12
    return premium_annual, premium_monthly

def predict_risk_and_premium(df):
    features = df.drop(columns=['driver_id'])
    predicted_risk = model.predict(features)
    premium_list = [calculate_realistic_premium(r) for r in predicted_risk]
    df['predicted_risk_score'] = predicted_risk
    df['premium_annual'] = [p[0] for p in premium_list]
    df['premium_monthly'] = [p[1] for p in premium_list]
    return df

# ---------------- DATABASE ----------------
def get_connection():
    db_path = os.path.join(os.path.dirname(__file__), DB_FILE)
    return sqlite3.connect(db_path)

def load_key():
    key_path = os.path.join(os.path.dirname(__file__), KEY_FILE)
    with open(key_path, "rb") as f:
        return f.read()

def decrypt_column(series, fernet):
    decrypted = []
    for val in series:
        try:
            decrypted_val = fernet.decrypt(val.encode()).decode()
            decrypted.append(float(decrypted_val))
        except:
            decrypted.append(None)
    return decrypted

@st.cache_data
def load_data():
    with get_connection() as conn:
        drivers = pd.read_sql("SELECT * FROM drivers", conn)
        trips = pd.read_sql("SELECT * FROM trips", conn)
        telemetry = pd.read_sql("SELECT * FROM telemetry_secure", conn)
    key = load_key()
    fernet = Fernet(key)
    telemetry["lat"] = decrypt_column(telemetry["lat"], fernet)
    telemetry["lon"] = decrypt_column(telemetry["lon"], fernet)
    if 'lat_dec' in telemetry.columns: telemetry.drop(columns=['lat_dec'], inplace=True)
    if 'lon_dec' in telemetry.columns: telemetry.drop(columns=['lon_dec'], inplace=True)
    return drivers, trips, telemetry

drivers_df, trips_df, telemetry_df = load_data()

# ---------------- PREDICT RISK FOR ALL DRIVERS ----------------
drivers_risk_df = predict_risk_and_premium(drivers_df.copy())

# ---------------- DRIVER SELECTION ----------------
driver_ids = drivers_df["driver_id"].unique()
selected_driver = st.sidebar.selectbox("Choose Your Driver ID", driver_ids)

driver_info = drivers_df[drivers_df["driver_id"] == selected_driver]
driver_trips = trips_df[trips_df["driver_id"] == selected_driver]
driver_risk_df = drivers_risk_df[drivers_risk_df["driver_id"] == selected_driver]

risk_score = driver_risk_df['predicted_risk_score'].values[0]
premium_annual = driver_risk_df['premium_annual'].values[0]
premium_monthly = driver_risk_df['premium_monthly'].values[0]

# ---------------- WEATHER ALERTS ----------------
def get_weather_alerts():
    url = f"http://api.openweathermap.org/data/2.5/onecall?lat={LAT}&lon={LON}&exclude=hourly,daily&appid={OPENWEATHER_API_KEY}"
    response = requests.get(url)
    data = response.json()
    return data.get("alerts", [])

weather_alerts = get_weather_alerts()
if weather_alerts:
    st.subheader("⚠️ Weather Alerts")
    for alert in weather_alerts:
        st.write(f"**{alert['event']}**")
        st.write(f"{alert['description']}")
else:
    st.write("🌤 No active hazardous weather alerts.")

# ---------------- DASHBOARD ----------------
st.title(f"🚗 Driving Adventure Dashboard for {selected_driver}!")

# --- Summary Cards ---
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Trips", driver_info["num_trips"].values[0])
col2.metric("Total Miles", round(driver_info["total_miles"].values[0],2))
col3.metric("Risk Score", round(risk_score,2))
col4.metric("Annual Premium", f"${premium_annual:.2f}")  

# --- Night Driving Highlight Rectangle ---
st.subheader("🌙 Night Driving Overview")
night_pct = driver_info['night_trip_pct_overall'].values[0]
fig_night, ax_night = plt.subplots(figsize=(6,0.1))
ax_night.add_patch(plt.Rectangle((0,0), 1, 1, color='lightgray'))
ax_night.add_patch(plt.Rectangle((0,0), night_pct, 1, color='skyblue'))
ax_night.set_xlim(0,1)
ax_night.set_ylim(0,1)
ax_night.axis('off')
st.pyplot(fig_night)
st.markdown(f"<h3 style='text-align:center; color:black;'>{round(night_pct*100,2)}% of trips occur at night</h3>", unsafe_allow_html=True)

# --- Driving Behavior Insights ---
# --- Driving Behavior Graphs ---
st.subheader("📊 Driving Behavior Insights")

graph_choice = st.selectbox(
    "Choose a graph to view:",
    ["Harsh Acceleration Over Time", "Harsh Braking Over Time", "Speed Distribution", "Trip Duration Distribution"]
)

if graph_choice == "Harsh Acceleration Over Time":
    fig, ax = plt.subplots(figsize=(6,3))
    sns.lineplot(data=driver_trips, x="trip_id", y="num_harsh_accels", marker="o", color="orange", ax=ax)
    ax.set_title("Harsh Acceleration Events Over Time")
    ax.set_xlabel("Trip ID")
    ax.set_ylabel("Count")
    plt.setp(ax.get_xticklabels(), rotation=90)  # Rotate trip_id labels
    st.pyplot(fig)

elif graph_choice == "Harsh Braking Over Time":
    fig, ax = plt.subplots(figsize=(6,3))
    sns.lineplot(data=driver_trips, x="trip_id", y="num_harsh_brakes", marker="o", color="red", ax=ax)
    ax.set_title("Harsh Braking Events Over Time")
    ax.set_xlabel("Trip ID")
    ax.set_ylabel("Count")
    plt.setp(ax.get_xticklabels(), rotation=90)  # Rotate trip_id labels
    st.pyplot(fig)

elif graph_choice == "Speed Distribution":
    if "avg_speed" in driver_trips.columns:
        fig, ax = plt.subplots(figsize=(6,3))
        sns.histplot(driver_trips["avg_speed"], bins=10, kde=True, color="green", ax=ax)
        ax.set_title("Speed Distribution")
        ax.set_xlabel("Average Speed (mph)")
        st.pyplot(fig)
    else:
        st.write("⚠️ No average speed data available for these trips.")

elif graph_choice == "Trip Duration Distribution":
    fig, ax = plt.subplots(figsize=(6,3))
    sns.histplot(driver_trips['trip_duration_min'], bins=10, kde=True, color='skyblue', ax=ax)
    ax.set_title("Trip Duration Distribution")
    ax.set_xlabel("Minutes")
    st.pyplot(fig)
# --- Gamification & Badges ---
st.subheader("🏅 Achievements & Badges")
badges = []
if driver_info["avg_num_harsh_brakes"].values[0] < 1:
    badges.append("✅ Safe Driver Badge")
if driver_info["night_trip_pct_overall"].values[0] > 0.3:
    badges.append("🌙 Night Owl Badge (Caution: night driving > 30%)")
if badges:
    for badge in badges:
        st.write(badge)
else:
    st.write("No badges yet, keep driving safely!")

# --- Peer Comparison ---
st.subheader("📈 Comparison Against Peers")
avg_harsh_brakes = drivers_df["avg_num_harsh_brakes"].mean()
avg_harsh_accels = drivers_df["avg_num_harsh_accels"].mean()
st.write(f"- Your harsh brakes: {driver_info['avg_num_harsh_brakes'].values[0]} vs Avg: {round(avg_harsh_brakes,2)}")
st.write(f"- Your harsh accels: {driver_info['avg_num_harsh_accels'].values[0]} vs Avg: {round(avg_harsh_accels,2)}")

# --- Leaderboard ---
st.subheader("🏆 Leaderboard")
drivers_risk_df_sorted = drivers_risk_df.sort_values("predicted_risk_score")
rank = drivers_risk_df_sorted.reset_index().query("driver_id == @selected_driver").index[0] + 1
total_drivers = drivers_risk_df.shape[0]
st.write(f"You are ranked **#{rank}** out of **{total_drivers}** drivers based on safe driving!")

# --- Driving Tips Based on Current Behavior ---
st.subheader("💡 Driving Recommendations")
tips = []
base_premium = 2285
if driver_info["avg_num_harsh_brakes"].values[0] > 1:
    reduction_risk = max(0, risk_score - 10)
    new_premium, _ = calculate_realistic_premium(reduction_risk, base_premium)
    tips.append(f"- Reduce harsh braking to lower your risk score to {round(reduction_risk,2)}, your annual premium could reduce to ${round(new_premium,2)}")
else:
    tips.append("- Keep up the good work on braking!")

if driver_info["avg_num_harsh_accels"].values[0] > 1:
    reduction_risk = max(0, risk_score - 5)
    new_premium, _ = calculate_realistic_premium(reduction_risk, base_premium)
    tips.append(f"- Reduce harsh acceleration to lower your risk score to {round(reduction_risk,2)}, your annual premium could reduce to ${round(new_premium,2)}")
else:
    tips.append("- Keep up the good work on acceleration!")

for tip in tips:
    st.write(tip)

# --- Expanded Alerts Panel ---
st.subheader("🔔 Recent Alerts")
alerts = []

# Harsh brakes/accelerations
if 'num_harsh_brakes' in driver_trips.columns and driver_trips['num_harsh_brakes'].sum() > 0:
    alerts.append(f"⚠️ {driver_trips['num_harsh_brakes'].sum()} harsh brakes detected in recent trips")
if 'num_harsh_accels' in driver_trips.columns and driver_trips['num_harsh_accels'].sum() > 0:
    alerts.append(f"⚠️ {driver_trips['num_harsh_accels'].sum()} harsh accelerations detected in recent trips")


# Night driving alert
if driver_info['night_trip_pct_overall'].values[0] > 0.5:
    alerts.append(f"🌙 High night driving percentage ({round(driver_info['night_trip_pct_overall'].values[0]*100,2)}%) – drive cautiously at night")

# High predicted risk score
if risk_score > 70:
    alerts.append(f"⚠️ High predicted risk score ({round(risk_score,2)}) – consider safer driving habits")

# Claims / violations alert
if driver_info['num_claims'].values[0] > 0:
    alerts.append(f"⚠️ You have {driver_info['num_claims'].values[0]} insurance claims on record")
if driver_info['num_violations'].values[0] > 0:
    alerts.append(f"⚠️ You have {driver_info['num_violations'].values[0]} driving violations on record")

# Display alerts
if alerts:
    for alert in alerts:
        st.write(alert)
else:
    st.write("No recent alerts!")

# --- Trip Table ---
st.subheader("📋 Trip Summaries")
columns_to_exclude = ['driver_id','trip_duration_min','total_miles']  # keep trip_id
trip_df_display = driver_trips.drop(columns=[c for c in columns_to_exclude if c in driver_trips.columns])
# Sort columns numerically after trip_id
cols_sorted = ['trip_id'] + sorted([c for c in trip_df_display.columns if c != 'trip_id'], key=lambda x: (int(x) if x.isdigit() else x))
trip_df_display = trip_df_display[cols_sorted]
st.dataframe(trip_df_display)
