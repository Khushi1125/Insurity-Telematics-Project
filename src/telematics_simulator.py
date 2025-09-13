import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def get_road_type_segments(trip_duration_sec, sample_interval_sec):
    total_samples = trip_duration_sec // sample_interval_sec
    fractions = {'highway': 0.3, 'city': 0.5, 'residential': 0.2}
    types = list(fractions)
    counts = [int(fractions[t] * total_samples) for t in types]
    for i in range(total_samples - sum(counts)):
        counts[i % len(counts)] += 1
    segments = []
    for t, c in zip(types, counts):
        segments += [t] * c
    return segments  

def simulate_telemetry_df(num_drivers=30, trips_per_driver=10, min_trip_min=1, max_trip_hr=1, sample_interval_sec=5):
    records = []
    HARSH_BRAKE_PROB = {'city': 0.02, 'highway': 0.005, 'residential': 0.01}
    HARSH_ACCEL_PROB = {'city': 0.02, 'highway': 0.05, 'residential': 0.01}
    engine_on = 1

    MIN_LAT, MAX_LAT = 36.5, 45.0
    MIN_LON, MAX_LON = -94.0, -81.0

    for driver in range(1, num_drivers + 1):
        driver_id = f'driver_{driver}'
        for trip in range(1, trips_per_driver + 1):
            trip_id = f'{driver_id}_trip_{trip}'
            trip_duration_sec = random.randint(min_trip_min * 60, max_trip_hr * 3600)
            samples_per_trip = max(1, trip_duration_sec // sample_interval_sec)

            night_prob = 0.3
            if random.random() < night_prob:
                start_hour = random.choice(list(range(22,24))+list(range(0,6)))
            else:
                start_hour = random.randint(6, 21)
            start_minute = random.randint(0, 59)
            start_time = datetime.now().replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
            start_time -= timedelta(days=random.randint(0, 10))
            prev_speed = random.uniform(20, 50)

            def get_road_type_segments(trip_duration_sec, sample_interval_sec):
                total_samples = trip_duration_sec // sample_interval_sec
                fractions = {'residential': 0.4, 'city': 0.4, 'highway': 0.2}
                types = list(fractions)
                counts = [int(fractions[t] * total_samples) for t in types]
                for i in range(total_samples - sum(counts)):
                    counts[i % len(counts)] += 1
                segments = []
                for t, c in zip(types, counts):
                    segments += [t] * c
                return segments

            road_types = get_road_type_segments(trip_duration_sec, sample_interval_sec)

            for sample in range(samples_per_trip):
                timestamp = start_time + timedelta(seconds=sample * sample_interval_sec)
                road_type = road_types[sample]
                road_speed_limits = {'highway': (65, 90), 'city': (20, 50), 'residential': (10, 30)}
                mean_speed, max_speed = road_speed_limits[road_type]
                speed = max(0, min(np.random.normal(mean_speed, 8), max_speed))

                acceleration = (speed - prev_speed) / sample_interval_sec
                if random.random() < HARSH_BRAKE_PROB[road_type]:
                    acceleration = random.uniform(-7, -4)
                if random.random() < HARSH_ACCEL_PROB[road_type]:
                    acceleration = random.uniform(4, 7)

                lat = random.uniform(MIN_LAT, MAX_LAT)
                lon = random.uniform(MIN_LON, MAX_LON)

                records.append({
                    'timestamp': timestamp,
                    'trip_id': trip_id,
                    'driver_id': driver_id,
                    'lat': lat,
                    'lon': lon,
                    'speed': speed,
                    'acceleration': acceleration,
                    'road_type': road_type,
                    'engine_on': engine_on
                })
                prev_speed = speed

    telemetry_df = pd.DataFrame(records)
    telemetry_df['timestamp'] = pd.to_datetime(telemetry_df['timestamp'])
    telemetry_df['road_type'] = telemetry_df['road_type'].astype('category')
    return telemetry_df

if __name__ == "__main__":
    df = simulate_telemetry_df()
    df.to_csv('telemetry_data.csv', index=False)
    print("Simulated telemetry data (Midwest only) saved to telemetry_data.csv")
