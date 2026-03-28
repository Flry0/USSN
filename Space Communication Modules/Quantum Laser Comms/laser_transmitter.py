class LaserVericiDugumu:
    def __init__(self, qkd_key_listesi):
        self.encryption_sequence = qkd_key_listesi
        
    def encrypt_and_modulate(self, mesaj_str):
        mesaj_byte_array = bytearray(mesaj_str.encode('utf-8'))
        sifrelenmis_payload = bytearray()
        
        for m_idx in range(len(mesaj_byte_array)):
            key_bit_val = self.encryption_sequence[m_idx % len(self.encryption_sequence)]
            xor_sonucu = mesaj_byte_array[m_idx] ^ (key_bit_val * 255)
            sifrelenmis_payload.append(xor_sonucu)
            
        optik_modulasyon_verisi = sifrelenmis_payload.hex()
        return optik_modulasyon_verisi
