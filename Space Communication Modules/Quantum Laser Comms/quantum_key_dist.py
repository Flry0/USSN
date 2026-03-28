from photon_encoder import generate_random_bits, generate_random_bases, create_photon_stream
from photon_decoder import measure_photons, sift_quantum_keys
from atmospheric_noise import apply_scintillation_noise, foton_kaybi_simule_et
import config

class QKDProtokolYonetici:
    def __init__(self, key_uzunlugu):
        self.key_uzunlugu = key_uzunlugu
        self.alice_bits = []
        self.alice_bases = []
        self.bob_bases = []

    def execute_bb84_protocol(self):
        self.alice_bits = generate_random_bits(self.key_uzunlugu * 4)
        self.alice_bases = generate_random_bases(self.key_uzunlugu * 4)
        
        foton_yayilimi = create_photon_stream(self.alice_bits, self.alice_bases)
        gurultulu_fotonlar = apply_scintillation_noise(foton_yayilimi, 0.05)
        kalan_fotonlar = foton_kaybi_simule_et(gurultulu_fotonlar, config.MAX_PHOTON_KAYBI)
        
        self.bob_bases = generate_random_bases(self.key_uzunlugu * 4)
        bob_olcumleri = measure_photons(kalan_fotonlar, self.bob_bases)
        
        final_shared_key = sift_quantum_keys(self.alice_bases, bob_olcumleri)
        
        if len(final_shared_key) > self.key_uzunlugu:
            final_shared_key = final_shared_key[:self.key_uzunlugu]
            
        return final_shared_key
