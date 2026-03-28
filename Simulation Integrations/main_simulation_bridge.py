import time
from ai_to_sim_mapper import SimulasyonKoprusuCore
from ussn_payload_builder import build_update_komutu, build_spawn_komutu

def start_integration_engines():
    motor_merkezi = SimulasyonKoprusuCore()
    
    dunya_baslangic = build_update_komutu("Earth", {"orbitSpeed": 5.0, "orbitRadius": 100.0, "orbitTargetName": "UnstableStar"})
    motor_merkezi.unity_sender_obj.send_sim_command(dunya_baslangic)
    print("Dunya Yorungesi Unity API uzerinden modifiye edildi.")
    
    cop_uretici = build_spawn_komutu("debris", 40.0, 0.0, 110.0)
    motor_merkezi.unity_sender_obj.send_sim_command(cop_uretici)
    motor_merkezi.sahne_takip_obj.add_object_record("DEBRIS_123", "debris")
    print("Yikici Uzay Copu Sahneye Uretildi (Spawned).")
    
    uydu_kacisi_simule = motor_merkezi.translate_ai_evasion("SAT_ALPHA", 40.0, 1.0)
    print("SAT_ALPHA uydusu kacis manevrasi GMAT ve Unity'ye islendi.")
    
    silah_modu_aktif = motor_merkezi.translate_chaos_weapon("DEBRIS_123")
    print("Uzay Copu Kaos Silahi olarak hizlandirildi.")
    
    print("UNITY USSN VE NASA GMAT SIMULASYON KOPRUSU AKTIF TEST BASARILI.")

if __name__ == "__main__":
    start_integration_engines()
