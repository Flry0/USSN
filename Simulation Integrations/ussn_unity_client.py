import socket
import json
import config_sim

class UnityBaglantiIstemcisi:
    def __init__(self):
        self.sunucu_adresi = config_sim.UNITY_HOST_IP
        self.sunucu_portu = config_sim.UNITY_API_PORT
        self.udp_soketi = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_sim_command(self, hazir_payload_dict):
        json_metni = json.dumps(hazir_payload_dict)
        byte_encode_mesaj = json_metni.encode('utf-8')
        
        try:
            self.udp_soketi.sendto(byte_encode_mesaj, (self.sunucu_adresi, self.sunucu_portu))
            return True
        except Exception:
            return False
