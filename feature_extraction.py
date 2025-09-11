import pandas as pd
import numpy as np

def aggregate_trip_features(telemetry_df):
    trip_features = []
    telemetry_df = telemetry_df.sort_values(['trip_id', 'timestamp'])
    telemetry_df['time_diff'] = telemetry_df.groupby('trip_id')['timestamp'].diff().dt.total_seconds().fillna(5)
    
    for trip_id, trip in telemetry_df.groupby('trip_id'):
        driver_id = trip['driver_id'].iloc[0]
        trip_duration_min = trip['time_diff'].sum() / 60
        total_miles = (trip['speed'] * trip['time_diff'] / 3600).sum()
        
        avg_speed = trip['speed'].mean()
        max_speed = trip['speed'].max()
        
        # Convert m/s^2 thresholds to mph/s for harsh event detection (1 m/s² = 2.23694 mph/s)
        num_harsh_brakes = (trip['acceleration'] < -3 * 2.23694).sum()
        num_harsh_accels = (trip['acceleration'] > 3 * 2.23694).sum()
        
        idling_time = trip[(trip['speed'] < 5) & (trip['engine_on'] == 1)]['time_diff'].sum()
        idling_pct = idling_time / trip['time_diff'].sum()
        
        night_trip_pct = ((trip['timestamp'].dt.hour >= 22) | (trip['timestamp'].dt.hour < 5)).mean()
        urban_pct = (trip['road_type'] == 'city').mean()
        highway_pct = (trip['road_type'] == 'highway').mean()
        
        
        trip_features.append({
            'trip_id': trip_id,
            'driver_id': driver_id,
            'trip_duration_min': trip_duration_min,
            'total_miles': total_miles,
            'avg_speed': avg_speed,
            'max_speed': max_speed,
            'num_harsh_brakes': num_harsh_brakes,
            'num_harsh_accels': num_harsh_accels,
            'idling_pct': idling_pct,
            'night_trip_pct': night_trip_pct,
            'urban_pct': urban_pct,
            'highway_pct': highway_pct,
        })
    return pd.DataFrame(trip_features)

if __name__ == "__main__":
    telemetry_df = pd.read_csv('telemetry_data.csv', parse_dates=['timestamp'])
    trip_df = aggregate_trip_features(telemetry_df)
    trip_df.to_csv('trip_data.csv', index=False)
    print("Trip-level features saved to trip_data.csv")
