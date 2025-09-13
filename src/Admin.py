import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import os
from cryptography.fernet import Fernet
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

def show_dashboard():
    st.set_page_config(
        page_title="Telematics Admin Dashboard",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    DB_FILE = "telematics.db"
    KEY_FILE = "secret.key"
    MODEL_PATH = "stacking_model.pkl"


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
        return drivers, trips, telemetry


    drivers_df, trips_df, telemetry_df = load_data()
    drivers_df = drivers_df.fillna(0)


    drivers_risk_df = predict_risk_and_premium(drivers_df.copy())


    st.sidebar.markdown(
        "<h2 style='color:#37474F;font-family:Arial;'>🚦 Select Driver</h2>", unsafe_allow_html=True
    )
    driver_ids = sorted(drivers_risk_df["driver_id"].unique())
    selected_driver = st.sidebar.selectbox("Choose a Driver", driver_ids)


    driver_info = drivers_risk_df[drivers_risk_df["driver_id"] == selected_driver].iloc[0]
    driver_trips = trips_df[trips_df["driver_id"] == selected_driver]
    driver_telemetry = telemetry_df[telemetry_df["driver_id"] == selected_driver]


    st.markdown("""
    <style>
    .section-title {font-size:26px;margin-bottom:14px;color:#205b9b !important;font-family:Arial;}
    .card {
        background:#ECEFF1;
        padding:20px 22px 12px 22px;
        border-radius:14px;
        margin-bottom:8px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    .metric-label {font-weight:700;color:#800000 !important;font-size:18px;}
    .big-metric {font-size:38px;color:#4a6741 !important;font-weight:700;font-family:Arial;}
    td {font-size:14px;}
    </style>
    """, unsafe_allow_html=True)


    def safe_round(val):
        try:
            return round(float(val), 2)
        except:
            return val


    st.markdown(f"<div class='section-title'>🛡️ Telematics Admin Dashboard</div>", unsafe_allow_html=True)
    st.markdown(f"<span class='metric-label'>Driver: {selected_driver}</span>", unsafe_allow_html=True)


    col1, col2, col3, col4, col5 = st.columns(5)
    col1.markdown(f"<div class='big-metric'>{safe_round(driver_info['num_trips'])}</div><div class='metric-label'>Trips</div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='big-metric'>{safe_round(driver_info['total_miles'])}</div><div class='metric-label'>Miles</div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='big-metric'>{safe_round(driver_info['predicted_risk_score'])}</div><div class='metric-label'>Risk Score</div>", unsafe_allow_html=True)
    col4.markdown(f"<div class='big-metric'>${safe_round(driver_info['premium_annual'])}</div><div class='metric-label'>Annual</div>", unsafe_allow_html=True)
    col5.markdown(f"<div class='big-metric'>${safe_round(driver_info['premium_monthly'])}</div><div class='metric-label'>Monthly</div>", unsafe_allow_html=True)


    st.markdown("<div class='section-title'>📋 Driver Profile & Behavior</div>", unsafe_allow_html=True)
    profile_grid = [
        ("Total Minutes", "total_drive_time_min"),
        ("Avg Trip Duration", "avg_trip_duration_min"),
        ("Avg Trip Miles", "avg_trip_miles"),
        ("Avg Speed", "avg_speed_overall"),
        ("Max Speed", "max_speed_overall"),
        ("Total Harsh Brakes", "total_harsh_brakes"),
        ("Total Harsh Accels", "total_harsh_accels"),
        ("Avg Harsh Brakes/Trip", "avg_num_harsh_brakes"),
        ("Avg Harsh Accels/Trip", "avg_num_harsh_accels"),
        ("Night Trip %", "night_trip_pct_overall"),
        ("Idling %", "idling_pct_overall"),
        ("Urban %", "urban_pct_overall"),
        ("Highway %", "highway_pct_overall"),
        ("Years Driving", "years_driving"),
        ("Claims", "num_claims"),
        ("Violations", "num_violations"),
        ("Vehicle Age", "vehicle_age"),
        ("Type", "vehicle_type"),
        ("Policy Years", "insurance_policy_length_years"),
        ("Weighted Claim Score", "claims_weighted_score")
    ]
    g1, g2 = st.columns(2)
    for i, (label, key) in enumerate(profile_grid):
        val = driver_info.get(key, 'N/A')
        val = safe_round(val) if isinstance(val, (int, float)) else val
        (g1 if i % 2 == 0 else g2).markdown(f"<div class='card'><span class='metric-label'>{label}:</span> {val}</div>", unsafe_allow_html=True)


    st.markdown("<div class='section-title'>📊 Select Data Visualization</div>", unsafe_allow_html=True)


    graph_options = [
        "Night Driving Fraction",
        "Harsh Braking Events Over Time",
        "Harsh Accelerating Events Over Time",
        "Speed Distribution",
        "Trip Duration Distribution",
    ]


    selected_graph = st.selectbox("Choose a graph to display", graph_options)


    if selected_graph == "Night Driving Fraction":
        night_pct = driver_info.get('night_trip_pct_overall', 0)
        fig, ax = plt.subplots(figsize=(6, 0.1))
        ax.barh([1], [1], height=0.4, color="#d0d0d0")
        ax.barh([1], [night_pct], height=0.4, color="#7a6de8")
        ax.set_xlim(0, 1)
        ax.axis('off') 
        st.pyplot(fig)
        st.markdown(f"<div style='text-align: center; font-size: 18px; color: #ff4dc2; margin-top: -12px;'>Night Driving: {safe_round(night_pct * 100)}%</div>", unsafe_allow_html=True)

    elif selected_graph == "Harsh Braking Events Over Time":
        if not driver_telemetry.empty and "timestamp" in driver_telemetry.columns:
            df = driver_telemetry.copy()
            df['harsh_brake'] = df['acceleration'] < -4
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            timeline = df.set_index('timestamp').resample('D')['harsh_brake'].sum()

            fig, ax = plt.subplots(figsize=(10, 4))
            timeline.plot(ax=ax, color="#17DAE8", linestyle='-', marker='o')
            ax.set_title("Harsh Braking Events Over Time", fontsize=14, color="#3f65b6")
            ax.set_ylabel("Count", fontsize=12)
            ax.grid(alpha=0.3)
            st.pyplot(fig)
        else:
            st.info("No telemetry data available for harsh braking over time.")

    elif selected_graph == "Harsh Accelerating Events Over Time":
        if not driver_telemetry.empty and "timestamp" in driver_telemetry.columns:
            df = driver_telemetry.copy()
            df['harsh_accel'] = df['acceleration'] > 4  
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            timeline = df.set_index('timestamp').resample('D')['harsh_accel'].sum()

            fig, ax = plt.subplots(figsize=(10, 4))
            timeline.plot(ax=ax, color="#e81717", linestyle='-', marker='o')
            ax.set_title("Harsh Accelerating Events Over Time", fontsize=14, color="#8b1a1a")
            ax.set_ylabel("Count", fontsize=12)
            ax.grid(alpha=0.3)
            st.pyplot(fig)
        else:
            st.info("No telemetry data available for harsh accelerating over time.")

    elif selected_graph == "Speed Distribution":
        if not driver_telemetry.empty and "speed" in driver_telemetry.columns:
            fig, ax = plt.subplots(figsize=(8, 4))
            sns.histplot(driver_telemetry['speed'], bins=30, kde=True, color='#17DAE8', ax=ax)
            ax.set_title("Speed Distribution", fontsize=14, color='#3f65b6')
            ax.set_xlabel("Speed", fontsize=12)
            st.pyplot(fig)
        else:
            st.info("No telemetry speed data available.")

    elif selected_graph == "Trip Duration Distribution":
        if not driver_trips.empty and "trip_duration_min" in driver_trips.columns:
            fig, ax = plt.subplots(figsize=(8, 4))
            sns.histplot(driver_trips['trip_duration_min'], bins=30, kde=True, color='#17DAE8', ax=ax)
            ax.set_title("Trip Duration Distribution (minutes)", fontsize=14, color='#3f65b6')
            ax.set_xlabel("Minutes", fontsize=12)
            st.pyplot(fig)
        else:
            st.info("No trip duration data available.")


    st.markdown("<div class='section-title'>🌐 All Customers Summary</div>", unsafe_allow_html=True)
    foot1, foot2, foot3, foot4 = st.columns(4)
    foot1.metric("Drivers", drivers_df.shape[0])
    foot2.metric("Mean Risk Score", round(drivers_risk_df["predicted_risk_score"].mean(), 2))
    foot3.metric("Avg Premium", f"${round(drivers_risk_df['premium_annual'].mean(), 2)}")
    foot4.metric("Total Miles", round(drivers_df["total_miles"].sum(), 2))

