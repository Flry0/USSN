from satellite_node import UyduAgentNode
from collision_detector import find_potential_collisions
import config

class SpaceTrafficEnv:
    def __init__(self, num_satellites):
        self.uydu_filosu = []
        for s_idx in range(num_satellites):
            is_iss_flag = (s_idx == 0)
            yeni_uydu = UyduAgentNode(f"SAT_{s_idx}", is_iss=is_iss_flag)
            self.uydu_filosu.append(yeni_uydu)
        self.adim_sayaci = 0

    def get_global_state(self):
        tum_durumlar = []
        for uydu_obj in self.uydu_filosu:
            tum_durumlar.extend(uydu_obj.get_state_vector())
        return tum_durumlar

    def step_simulation(self, actions_dict):
        odul_toplami = 0.0
        
        for uydu_obj in self.uydu_filosu:
            if uydu_obj.node_id in actions_dict:
                a_x, a_y, a_z = actions_dict[uydu_obj.node_id]
                hedef_uygulandi = uydu_obj.apply_thrust_action(a_x, a_y, a_z)
                if not hedef_uygulandi:
                    odul_toplami -= 5.0
            
            uydu_obj.update_position()
            
            if uydu_obj.pos_x < 0 or uydu_obj.pos_x > config.MAX_YORUNGE_X or \
               uydu_obj.pos_y < 0 or uydu_obj.pos_y > config.MAX_YORUNGE_Y or \
               uydu_obj.pos_z < 0 or uydu_obj.pos_z > config.MAX_YORUNGE_Z:
                odul_toplami -= 10.0
                
        carpismalar_listesi = find_potential_collisions(self.uydu_filosu)
        
        for risk in carpismalar_listesi:
            mesafe_val = risk[2]
            if mesafe_val < config.CARPISMA_MESAFESI:
                odul_toplami -= 100.0
            else:
                odul_toplami -= 10.0
                
        odul_toplami += 1.0
        self.adim_sayaci += 1
        
        is_done = (self.adim_sayaci >= config.MAX_EPISODE_ADIMI)
        return self.get_global_state(), odul_toplami, is_done
