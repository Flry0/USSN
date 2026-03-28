import time
from pid_controller import HassasPIDKontrolcu
import config

class OptikHedefTakipleyici:
    def __init__(self):
        self.pid_x = HassasPIDKontrolcu(config.PID_P, config.PID_I, config.PID_D)
        self.pid_y = HassasPIDKontrolcu(config.PID_P, config.PID_I, config.PID_D)
        self.pid_z = HassasPIDKontrolcu(config.PID_P, config.PID_I, config.PID_D)
        self.guncel_x = 0.0
        self.guncel_y = 0.0
        self.guncel_z = 0.0
        self.hizalanma_basarili = False

    def takip_dongusunu_calistir(self, target_coord_dict):
        dt_val = 0.1
        fark_x = abs(target_coord_dict['x'] - self.guncel_x)
        fark_y = abs(target_coord_dict['y'] - self.guncel_y)
        fark_z = abs(target_coord_dict['z'] - self.guncel_z)
        
        for adim in range(5000):
            duzeltme_x = self.pid_x.calculate_duzeltme(target_coord_dict['x'], self.guncel_x, dt_val)
            duzeltme_y = self.pid_y.calculate_duzeltme(target_coord_dict['y'], self.guncel_y, dt_val)
            duzeltme_z = self.pid_z.calculate_duzeltme(target_coord_dict['z'], self.guncel_z, dt_val)
            
            self.guncel_x += duzeltme_x
            self.guncel_y += duzeltme_y
            self.guncel_z += duzeltme_z
            
        fark_toplam = abs(target_coord_dict['x'] - self.guncel_x) + abs(target_coord_dict['y'] - self.guncel_y) + abs(target_coord_dict['z'] - self.guncel_z)
        if fark_toplam < 5.0:
            self.hizalanma_basarili = True
        else:
            self.hizalanma_basarili = False
            
        return self.hizalanma_basarili
