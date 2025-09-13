import pandas as pd
import numpy as np

def aggregate_driver_features(trip_df):
    driver_features = []
    np.random.seed(42)  
    
    driver_ids = trip_df['driver_id'].unique()
    num_drivers = len(driver_ids)

    years_driving = np.random.randint(1, 30, num_drivers)
    num_claims = np.random.poisson(0.3, num_drivers)
    num_violations = np.random.poisson(0.5, num_drivers)
    vehicle_age = np.random.randint(0, 15, num_drivers)
    vehicle_types = ['Sedan', 'SUV', 'Sports Car', 'Truck', 'Electric']
    vehicle_type_choices = np.random.choice(vehicle_types, num_drivers, p=[0.5, 0.25, 0.1, 0.1, 0.05])
    insurance_policy_length_years = np.random.randint(1, 10, num_drivers)
    
    for i, driver_id in enumerate(driver_ids):
        trips = trip_df[trip_df['driver_id'] == driver_id]
        num_trips = len(trips)
        total_miles = trips['total_miles'].sum()
        total_drive_time_min = trips['trip_duration_min'].sum()
        avg_trip_duration_min = trips['trip_duration_min'].mean()
        avg_trip_miles = trips['total_miles'].mean()
        avg_speed_overall = trips['avg_speed'].mean()
        max_speed_overall = trips['max_speed'].max()
        total_harsh_brakes = trips['num_harsh_brakes'].sum()
        total_harsh_accels = trips['num_harsh_accels'].sum()
        avg_num_harsh_brakes = trips['num_harsh_brakes'].mean()
        avg_num_harsh_accels = trips['num_harsh_accels'].mean()
        
        night_trip_pct_overall = (trips['night_trip_pct'] * trips['trip_duration_min']).sum() / total_drive_time_min if total_drive_time_min > 0 else 0
        idling_pct_overall = (trips['idling_pct'] * trips['trip_duration_min']).sum() / total_drive_time_min if total_drive_time_min > 0 else 0
        urban_pct_overall = (trips['urban_pct'] * trips['trip_duration_min']).sum() / total_drive_time_min if total_drive_time_min > 0 else 0
        highway_pct_overall = (trips['highway_pct'] * trips['trip_duration_min']).sum() / total_drive_time_min if total_drive_time_min > 0 else 0

        years_exp = years_driving[i]
        claims = num_claims[i]
        violations = num_violations[i]
        veh_age = vehicle_age[i]
        veh_type = vehicle_type_choices[i]
        policy_length = insurance_policy_length_years[i]

        claims_weighted_score = claims * 25 + violations * 15
        
        driver_features.append({
            'driver_id': driver_id,
            'num_trips': num_trips,
            'total_miles': total_miles,
            'total_drive_time_min': total_drive_time_min,
            'avg_trip_duration_min': avg_trip_duration_min,
            'avg_trip_miles': avg_trip_miles,
            'avg_speed_overall': avg_speed_overall,
            'max_speed_overall': max_speed_overall,
            'total_harsh_brakes': total_harsh_brakes,
            'total_harsh_accels': total_harsh_accels,
            'avg_num_harsh_brakes': avg_num_harsh_brakes,
            'avg_num_harsh_accels': avg_num_harsh_accels,
            'night_trip_pct_overall': night_trip_pct_overall,
            'idling_pct_overall': idling_pct_overall,
            'urban_pct_overall': urban_pct_overall,
            'highway_pct_overall': highway_pct_overall,
            'years_driving': years_exp,
            'num_claims': claims,
            'num_violations': violations,
            'vehicle_age': veh_age,
            'vehicle_type': veh_type,
            'insurance_policy_length_years': policy_length,
            'claims_weighted_score': claims_weighted_score
        })
    
    return pd.DataFrame(driver_features)

if __name__ == "__main__":
    trip_df = pd.read_csv('trip_data.csv')
    driver_df = aggregate_driver_features(trip_df)
    driver_df.to_csv('driver_data.csv', index=False)
    print("Driver-level features with simulated history and vehicle info saved to driver_data.csv")
