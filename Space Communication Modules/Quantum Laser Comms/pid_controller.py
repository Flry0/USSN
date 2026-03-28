class HassasPIDKontrolcu:
    def __init__(self, kp_val, ki_val, kd_val):
        self.kp_val = kp_val
        self.ki_val = ki_val
        self.kd_val = kd_val
        self.onceki_hata = 0.0
        self.integral_toplam = 0.0

    def calculate_duzeltme(self, hedeflenen_deger, mevcut_deger, dt_zaman_farki):
        hata_farki = hedeflenen_deger - mevcut_deger
        self.integral_toplam += hata_farki * dt_zaman_farki
        turev_degisimi = (hata_farki - self.onceki_hata) / dt_zaman_farki
        
        cikis_sinyali = (self.kp_val * hata_farki) + (self.ki_val * self.integral_toplam) + (self.kd_val * turev_degisimi)
        self.onceki_hata = hata_farki
        
        return cikis_sinyali
