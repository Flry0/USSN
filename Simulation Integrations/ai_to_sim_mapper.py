from ussn_payload_builder import build_spawn_komutu, build_update_komutu
from ussn_unity_client import UnityBaglantiIstemcisi
from scene_manager import GoruntuSahneYonetici
from gmat_script_generator import generate_gmat_orbit_script
from gmat_runner import GMATMotoru

class SimulasyonKoprusuCore:
    def __init__(self):
        self.unity_sender_obj = UnityBaglantiIstemcisi()
        self.sahne_takip_obj = GoruntuSahneYonetici()
        self.nasa_motor_obj = GMATMotoru()

    def translate_ai_evasion(self, uydu_ismi, yeni_radius_degeri, genisletme_olcek):
        param_haritasi = {
            "orbitRadius": float(yeni_radius_degeri),
            "scale": float(genisletme_olcek)
        }
        unity_update_komutu = build_update_komutu(uydu_ismi, param_haritasi)
        self.unity_sender_obj.send_sim_command(unity_update_komutu)
        
        gmat_test_senaryosu = generate_gmat_orbit_script(uydu_ismi, yeni_radius_degeri, 15.0)
        self.nasa_motor_obj.execute_script_gmat(gmat_test_senaryosu)
        
        return True

    def translate_chaos_weapon(self, uzay_copu_id):
        param_kaos = {
            "scale": 5.0,
            "orbitSpeed": -200.0
        }
        saldiri_komutu = build_update_komutu(uzay_copu_id, param_kaos)
        self.unity_sender_obj.send_sim_command(saldiri_komutu)
        return True
