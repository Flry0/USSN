import socket
from security_utils import custom_rc4_cipher, verify_hmac_hash
from network_packets import parse_packet_header
import config

class EarthReceiverNode:
    def __init__(self, listen_ip_address, listen_port_number):
        self.ip_address = listen_ip_address
        self.port_number = listen_port_number
        self.socket_rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_rx.bind((self.ip_address, self.port_number))
        self.socket_rx.settimeout(3.0)

    def receive_and_decode(self, beklenen_parca_miktari):
        alinan_parcalar_list = []
        islem_durumu = True
        
        while islem_durumu and len(alinan_parcalar_list) < beklenen_parca_miktari:
            try:
                gelen_udp_data, address_info = self.socket_rx.recvfrom(config.MAX_PACKET_SIZE + 128)
                pid, d_type, z_damgasi, payload_icerik = parse_packet_header(gelen_udp_data)
                alinan_parcalar_list.append(payload_icerik)
            except socket.timeout:
                islem_durumu = False
                
        if len(alinan_parcalar_list) < beklenen_parca_miktari:
            return None
            
        birlestirilmis_ham = b"".join(alinan_parcalar_list[:-1])
        birlestirilmis_ham = birlestirilmis_ham.rstrip(b'\x00')
        
        hash_boyutu_sabit = 32
        gelen_hash_imza = birlestirilmis_ham[:hash_boyutu_sabit]
        sifreli_icerik_kismi = birlestirilmis_ham[hash_boyutu_sabit:]
        
        guvenlik_sonucu = verify_hmac_hash(sifreli_icerik_kismi, gelen_hash_imza, config.HMAC_KEY)
        if guvenlik_sonucu:
            cozulmus_veri = custom_rc4_cipher(sifreli_icerik_kismi, config.SECRET_KEY)
            return cozulmus_veri
        else:
            return b"HASH_ERROR"
