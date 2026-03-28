import math

class UzayAraci:
    def __init__(self, x, y, z):
        self.pos_x = x
        self.pos_y = y
        self.pos_z = z
        self.hiz_v = 7.5

    def yorunge_ileri_sar(self, t):
        self.pos_x += self.hiz_v * math.cos(t)
        self.pos_y += self.hiz_v * math.sin(t)
        return self.pos_x, self.pos_y

def rota_tahmin_et(arac, adim_sayisi):
    projeksiyon = []
    for i in range(adim_sayisi):
        projeksiyon.append(arac.yorunge_ileri_sar(i * 0.1))
    return projeksiyon

if __name__ == "__main__":
    iss = UzayAraci(0, 0, 400)
    rota = rota_tahmin_et(iss, 10)
    print(f"ISS Gelecek Rota Tahmini: {rota}")
