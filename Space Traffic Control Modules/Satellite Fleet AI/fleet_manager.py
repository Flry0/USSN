from ai_router_model import AIYorungeModeli
from energy_optimizer import optimize_burn_route
from collision_detector import find_potential_collisions

class SwarmFleetManager:
    def __init__(self):
        self.ai_engine = AIYorungeModeli()

    def generate_fleet_actions(self, uydu_filosu_obj):
        riskli_ciftler = find_potential_collisions(uydu_filosu_obj)
        tehlikedeki_id_set = set()
        
        for risk in riskli_ciftler:
            tehlikedeki_id_set.add(risk[0])
            tehlikedeki_id_set.add(risk[1])
            
        action_kararlari = {}
        for s_obj in uydu_filosu_obj:
            is_in_danger = (s_obj.node_id in tehlikedeki_id_set)
            
            istenen_hareket = self.ai_engine.predict_optimal_action(s_obj.get_state_vector(), is_in_danger)
            
            guvenli_hareket = optimize_burn_route(s_obj.kalan_yakit, istenen_hareket)
            action_kararlari[s_obj.node_id] = guvenli_hareket
            
        return action_kararlari
