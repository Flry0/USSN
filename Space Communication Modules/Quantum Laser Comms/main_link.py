from laser_tracker import OptikHedefTakipleyici
from quantum_key_dist import QKDProtokolYonetici
from laser_transmitter import LaserVericiDugumu
from laser_receiver import LaserAliciDugumu
import config

def start_laser_communication():
    takip_motoru = OptikHedefTakipleyici()
    hedef_yildiz_koordinatlari = {'x': config.HEDEF_X, 'y': config.HEDEF_Y, 'z': config.HEDEF_Z}
    
    hizalanma_durumu = takip_motoru.takip_dongusunu_calistir(hedef_yildiz_koordinatlari)
    print("LAZER HIZALANMA KONTROLU:", hizalanma_durumu)
    
    if hizalanma_durumu:
        qkd_yonetici = QKDProtokolYonetici(128)
        retrieved_quantum_key = qkd_yonetici.execute_bb84_protocol()
        print("KUANTUM ANAHTAR URETIMI UZUNLUK:", len(retrieved_quantum_key))
        
        verici_lazer = LaserVericiDugumu(retrieved_quantum_key)
        alici_lazer = LaserAliciDugumu(retrieved_quantum_key)
        
        gizli_mesaj = "YORUNGE_MERKEZI_VERI_AKISI_BASLADI"
        print("ORIJINAL MESAJ:", gizli_mesaj)
        
        modulasyonlu_isik_akisi = verici_lazer.encrypt_and_modulate(gizli_mesaj)
        print("LAZER MODULASYONU (HEX):", modulasyonlu_isik_akisi)
        
        cozulen_komut_gelen = alici_lazer.demodulate_and_decrypt(modulasyonlu_isik_akisi)
        print("ALINAN DECRYPT MESAJ:", cozulen_komut_gelen)
        
        if cozulen_komut_gelen == gizli_mesaj:
            print("KUANTUM LAZER ILETISIM TESTI BASARILI.")
        else:
            print("KUANTUM LAZER ILETISIM TESTI BASARISIZ.")
            
if __name__ == "__main__":
    start_laser_communication()
