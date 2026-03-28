import math
import config

def calculate_distance_3d(node_a_pos, node_b_pos):
    fark_x = node_a_pos[0] - node_b_pos[0]
    fark_y = node_a_pos[1] - node_b_pos[1]
    fark_z = node_a_pos[2] - node_b_pos[2]
    mesafe_val = math.sqrt(fark_x**2 + fark_y**2 + fark_z**2)
    return mesafe_val

def find_potential_collisions(uydu_listesi):
    risk_listesi = []
    for num_i in range(len(uydu_listesi)):
        for num_j in range(num_i + 1, len(uydu_listesi)):
            pos_1 = [uydu_listesi[num_i].pos_x, uydu_listesi[num_i].pos_y, uydu_listesi[num_i].pos_z]
            pos_2 = [uydu_listesi[num_j].pos_x, uydu_listesi[num_j].pos_y, uydu_listesi[num_j].pos_z]
            aradaki_uzaklik = calculate_distance_3d(pos_1, pos_2)
            if aradaki_uzaklik < config.GUVENLI_MESAFE:
                tehlike_kaydi = (uydu_listesi[num_i].node_id, uydu_listesi[num_j].node_id, aradaki_uzaklik)
                risk_listesi.append(tehlike_kaydi)
    return risk_listesi
