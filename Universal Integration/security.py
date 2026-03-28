import hashlib
import time
import config

def verify_node_token(gelen_token, node_id):
    zaman_damgasi_haritasi = str(int(time.time() / 60))
    birlestirilmis_metin = node_id + config.HUB_SECRET_KEY + zaman_damgasi_haritasi
    
    beklenen_hash_sonucu = hashlib.sha256(birlestirilmis_metin.encode('utf-8')).hexdigest()
    
    if gelen_token == beklenen_hash_sonucu:
        return True
    return False

def generate_handshake_crypto(node_id):
    zaman_kodu = str(int(time.time() / 60))
    ham_metin = node_id + config.HUB_SECRET_KEY + zaman_kodu
    return hashlib.sha256(ham_metin.encode('utf-8')).hexdigest()
