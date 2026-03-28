import hmac
import hashlib

def create_hmac_hash(payload_data, secret_hash_key):
    return hmac.new(secret_hash_key, payload_data, hashlib.sha256).digest()

def verify_hmac_hash(payload_data, incoming_hash, secret_hash_key):
    beklenen_hash_degeri = hmac.new(secret_hash_key, payload_data, hashlib.sha256).digest()
    return hmac.compare_digest(beklenen_hash_degeri, incoming_hash)

def custom_rc4_cipher(payload_data, sifreleme_key):
    S_box = list(range(256))
    j_idx = 0
    sifrelenmis_sonuc = bytearray()
    
    for i in range(256):
        j_idx = (j_idx + S_box[i] + sifreleme_key[i % len(sifreleme_key)]) % 256
        S_box[i], S_box[j_idx] = S_box[j_idx], S_box[i]
        
    i = j_idx = 0
    for data_byte in payload_data:
        i = (i + 1) % 256
        j_idx = (j_idx + S_box[i]) % 256
        S_box[i], S_box[j_idx] = S_box[j_idx], S_box[i]
        k_val = S_box[(S_box[i] + S_box[j_idx]) % 256]
        sifrelenmis_sonuc.append(data_byte ^ k_val)
        
    return bytes(sifrelenmis_sonuc)
