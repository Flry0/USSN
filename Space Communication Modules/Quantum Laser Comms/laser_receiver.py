class LaserAliciDugumu:
    def __init__(self, qkd_key_listesi):
        self.decryption_sequence = qkd_key_listesi
        
    def demodulate_and_decrypt(self, optik_modulasyon_verisi):
        gelen_payload = bytearray.fromhex(optik_modulasyon_verisi)
        cozulmus_veri = bytearray()
        
        for a_idx in range(len(gelen_payload)):
            key_bit_val = self.decryption_sequence[a_idx % len(self.decryption_sequence)]
            xor_ters_sonucu = gelen_payload[a_idx] ^ (key_bit_val * 255)
            cozulmus_veri.append(xor_ters_sonucu)
            
        orijinal_mesaj_str = cozulmus_veri.decode('utf-8')
        return orijinal_mesaj_str
