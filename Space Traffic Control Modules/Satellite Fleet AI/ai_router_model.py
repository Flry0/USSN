import random

class AIYorungeModeli:
    def __init__(self, action_limit_val=0.5):
        self.action_limit = action_limit_val
        self.knowledge_weights = [random.uniform(-0.1, 0.1) for _ in range(50)]

    def predict_optimal_action(self, agent_state_list, riskli_durum):
        if riskli_durum:
            ax = random.uniform(-self.action_limit, self.action_limit) * 2.0
            ay = random.uniform(-self.action_limit, self.action_limit) * 2.0
            az = random.uniform(-self.action_limit, self.action_limit) * 2.0
        else:
            ax = random.uniform(-self.action_limit/10, self.action_limit/10)
            ay = random.uniform(-self.action_limit/10, self.action_limit/10)
            az = random.uniform(-self.action_limit/10, self.action_limit/10)
            
        return [ax, ay, az]

    def update_policy_weights(self, reward_skoru):
        for w_idx in range(len(self.knowledge_weights)):
            self.knowledge_weights[w_idx] += reward_skoru * 0.001
