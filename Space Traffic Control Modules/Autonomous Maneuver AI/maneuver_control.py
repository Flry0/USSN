import math

class ManevraYonetici:
    def __init__(self, yakit):
        self.kalan_yakit = yakit

    def thrust_hesapla(self, delta_v):
        sarfiyat = delta_v * 0.12
        if self.kalan_yakit >= sarfiyat:
            self.kalan_yakit -= sarfiyat
            return True, sarfiyat
        return False, 0

def kacinma_manevrasi(mevcut_pos, engel_pos):
    dx = engel_pos[0] - mevcut_pos[0]
    dy = engel_pos[1] - mevcut_pos[1]
    mesafe = math.sqrt(dx**2 + dy**2)
    return [mevcut_pos[0] - dx/mesafe, mevcut_pos[1] - dy/mesafe]

if __name__ == "__main__":
    m = ManevraYonetici(100)
    yeni_rota = kacinma_manevrasi([0,0], [10,10])
    print(f"Kacinma Rota Koordinati: {yeni_rota}")
