import random
import config

class UyduAgentNode:
    def __init__(self, node_id, is_iss=False):
        self.node_id = node_id
        self.is_iss = is_iss
        self.pos_x = random.uniform(0, config.MAX_YORUNGE_X)
        self.pos_y = random.uniform(0, config.MAX_YORUNGE_Y)
        self.pos_z = random.uniform(0, config.MAX_YORUNGE_Z)
        self.vx = random.uniform(-1.0, 1.0)
        self.vy = random.uniform(-1.0, 1.0)
        self.vz = random.uniform(-1.0, 1.0)
        self.kalan_yakit = config.MAX_YAKIT_KAPASITESI

    def get_state_vector(self):
        durum_listesi = [self.pos_x, self.pos_y, self.pos_z, self.vx, self.vy, self.vz, self.kalan_yakit]
        return durum_listesi

    def apply_thrust_action(self, ax, ay, az):
        harcanan_enerji = abs(ax) + abs(ay) + abs(az)
        if self.kalan_yakit >= harcanan_enerji:
            self.vx += ax
            self.vy += ay
            self.vz += az
            self.kalan_yakit -= harcanan_enerji
            return True
        return False

    def update_position(self):
        self.pos_x += self.vx
        self.pos_y += self.vy
        self.pos_z += self.vz
