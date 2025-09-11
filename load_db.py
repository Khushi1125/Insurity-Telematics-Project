# src/load_and_encrypt.py
import sqlite3
import pandas as pd
import pygeohash as pgh
from cryptography.fernet import Fernet
import os

# ---------- CONFIG ----------
SCHEMA_FILE = "schema.sql"
DB_FILE = "telematics.db"

DRIVER_CSV = "driver_data.csv"
TRIP_CSV = "trip_data.csv"
TELEMETRY_CSV = "telemetry_data.csv"

KEY_FILE = "secret.key"
GEOHASH_PRECISION = 5  # ~5 → ~5km cell
# -----------------------------

def load_key(key_file):
    if not os.path.exists(key_file):
        raise FileNotFoundError(f"Key file {key_file} not found. Generate with gen_key.py")
    with open(key_file, "rb") as f:
        return f.read()

def create_db(schema_file=SCHEMA_FILE, db_file=DB_FILE):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    with open(schema_file, "r") as f:
        cur.executescript(f.read())
    conn.commit()
    conn.close()
    print("✅ Database created with schema:", db_file)

def insert_drivers(csv_path=DRIVER_CSV, db_file=DB_FILE):
    df = pd.read_csv(csv_path)
    if "driver_id" not in df.columns:
        raise ValueError("driver_data.csv must have 'driver_id'")
    conn = sqlite3.connect(db_file)
    df.to_sql("drivers", conn, if_exists="append", index=False)
    conn.commit()
    conn.close()
    print(f"✅ Inserted {len(df)} rows into 'drivers'")

def insert_trips(csv_path=TRIP_CSV, db_file=DB_FILE):
    df = pd.read_csv(csv_path)
    if "trip_id" not in df.columns:
        raise ValueError("trip_data.csv must have 'trip_id'")
    conn = sqlite3.connect(db_file)
    df.to_sql("trips", conn, if_exists="append", index=False)
    conn.commit()
    conn.close()
    print(f"✅ Inserted {len(df)} rows into 'trips'")

def encrypt_and_insert_telemetry(csv_path=TELEMETRY_CSV, db_file=DB_FILE, key_file=KEY_FILE):
    key = load_key(key_file)
    f = Fernet(key)

    df = pd.read_csv(csv_path, parse_dates=["timestamp"])
    required = {"timestamp","trip_id","driver_id","lat","lon","speed","acceleration","road_type","engine_on"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError("Telemetry CSV missing columns: " + ", ".join(missing))

    # Coarse geohash
    df["geohash"] = df.apply(lambda r: pgh.encode(float(r["lat"]), float(r["lon"]), precision=GEOHASH_PRECISION), axis=1)

    # Encrypt lat/lon
    def enc_val(x):
        if pd.isna(x):
            return None
        return f.encrypt(str(x).encode()).decode()

    df["lat_enc"] = df["lat"].apply(enc_val)
    df["lon_enc"] = df["lon"].apply(enc_val)

    # Build insert DataFrame
    insert_df = df[[
        "timestamp","trip_id","driver_id","lat_enc","lon_enc",
        "speed","acceleration","road_type","engine_on","geohash"
    ]].copy()

    insert_df = insert_df.rename(columns={"lat_enc":"lat","lon_enc":"lon"})

    conn = sqlite3.connect(db_file)
    cur = conn.cursor()

    # If telemetry_secure table doesn’t exist, create it
    cur.execute("""
        CREATE TABLE IF NOT EXISTS telemetry_secure (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP,
            trip_id TEXT,
            driver_id TEXT,
            lat TEXT,
            lon TEXT,
            speed REAL,
            acceleration REAL,
            road_type TEXT,
            engine_on INTEGER,
            geohash TEXT
        );
    """)
    conn.commit()

    insert_df.to_sql("telemetry_secure", conn, if_exists="append", index=False)
    conn.commit()
    conn.close()
    print(f"✅ Inserted {len(insert_df)} rows into 'telemetry_secure'")

def main():
    # 1. Create schema
    create_db()

    # 2. Insert drivers
    if os.path.exists(DRIVER_CSV):
        insert_drivers()
    else:
        print("⚠️ driver_data.csv not found")

    # 3. Insert trips
    if os.path.exists(TRIP_CSV):
        insert_trips()
    else:
        print("⚠️ trip_data.csv not found")

    # 4. Insert telemetry with encryption
    if os.path.exists(TELEMETRY_CSV):
        encrypt_and_insert_telemetry()
    else:
        print("⚠️ telemetry.csv not found")

if __name__ == "__main__":
    main()
