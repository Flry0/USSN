import random

def fetch_iss_live_status():
    iss_data_dict = {
        "velocity": random.uniform(7.66, 7.67),
        "altitude_km": random.uniform(415.0, 420.0),
        "crew_count": 7,
        "solar_panel_efficiency": random.uniform(0.9, 1.0)
    }
    return iss_data_dict

def set_iss_evasion_maneuver(is_critical_threat):
    if is_critical_threat:
        boost_thrust = 5.0
        return boost_thrust
    return 0.0
