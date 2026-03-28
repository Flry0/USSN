from orbit_env import SpaceTrafficEnv
from fleet_manager import SwarmFleetManager
from iss_telemetry import fetch_iss_live_status
from energy_optimizer import calculate_fleet_efficiency

def start_ai_fleet_simulation():
    komuta_merkezi = SwarmFleetManager()
    
    episode_sayisi = 1
    
    while episode_sayisi <= 3:
        print("EPISODE START DIR:", episode_sayisi)
        iss_baslangic = fetch_iss_live_status()
        print("ISS DURUMU:", iss_baslangic)
        
        ortam_cevresi = SpaceTrafficEnv(num_satellites=5)
        dongu_bitti = False
        toplam_kazanc = 0.0
        
        while not dongu_bitti:
            ajanlarin_kararlari = komuta_merkezi.generate_fleet_actions(ortam_cevresi.uydu_filosu)
            yeni_durum_vektoru, adim_odulu, dongu_bitti = ortam_cevresi.step_simulation(ajanlarin_kararlari)
            komuta_merkezi.ai_engine.update_policy_weights(adim_odulu)
            toplam_kazanc += adim_odulu
            
            if ortam_cevresi.adim_sayaci % 100 == 0:
                print("SIMULASYON ADIMI:", ortam_cevresi.adim_sayaci, "ODUL:", adim_odulu)
                
        yakit_harcamasi = calculate_fleet_efficiency(ortam_cevresi.uydu_filosu)
        print("EPISODE SONU TOPLAM ODUL:", toplam_kazanc)
        print("FILO TOPLAM YAKIT TUKETIMI:", yakit_harcamasi)
        print("-" * 50)
        episode_sayisi += 1
        
    print("AI SATELLITE FLEET KONTROL SISTEMI TAMAMLANDI")
    
if __name__ == "__main__":
    start_ai_fleet_simulation()
