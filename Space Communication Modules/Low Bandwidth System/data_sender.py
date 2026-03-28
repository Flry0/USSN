import socket
from security_utils import custom_rc4_cipher, create_hmac_hash
from error_correction import generate_fec_parity_block
from network_packets import build_packet_header, chunk_data_split
import config

class SatelliteSenderNode:
    def __init__(self, target_ip_address, target_port_number):
        self.ip_address = target_ip_address
        self.port_number = target_port_number
        self.socket_tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.packet_counter_id = 1000

    def transmit_secure_data(self, ham_veri_bytes, veri_tipi_id):
        encrypted_veri = custom_rc4_cipher(ham_veri_bytes, config.SECRET_KEY)
        hash_imzasi = create_hmac_hash(encrypted_veri, config.HMAC_KEY)
        
        birlesik_payload = hash_imzasi + encrypted_veri
        chunklanmis_liste = chunk_data_split(birlesik_payload, config.MAX_PACKET_SIZE)
        
        fec_parity_verisi = generate_fec_parity_block(chunklanmis_liste)
        chunklanmis_liste.append(fec_parity_verisi)
        
        for kucuk_paket in chunklanmis_liste:
            gonderilecek_udp = build_packet_header(self.packet_counter_id, veri_tipi_id, kucuk_paket)
            self.socket_tx.sendto(gonderilecek_udp, (self.ip_address, self.port_number))
            self.packet_counter_id += 1
