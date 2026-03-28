from path_predictor import UzayAraci, rota_tahmin_et
from maneuver_control import kacinma_manevrasi, ManevraYonetici

def execute_autonomous_flight(sat_id, s_pos, obstacle_pos):
    sat = UzayAraci(s_pos[0], s_pos[1], s_pos[2])
    prediction = rota_tahmin_et(sat, 5)
    
    if abs(s_pos[0]-obstacle_pos[0]) < 5:
        escape_vect = kacinma_manevrasi(s_pos, obstacle_pos)
        print(f"AUTO_MANEUVER_{sat_id}: ESCAPE_TO_{escape_vect}")
        return escape_vect
    
    print(f"FLIGHT_PATH_{sat_id}: OK")
    return prediction

if __name__ == "__main__":
    execute_autonomous_flight("SAT-X", [0,0,500], [2,2,500])
