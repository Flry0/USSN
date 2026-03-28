import struct
import time

def build_packet_header(packet_id, data_tipi, payload_icerik):
    zaman_damgasi = int(time.time() * 1000)
    header_kismi = struct.pack('!I B Q', packet_id, data_tipi, zaman_damgasi)
    tam_paket = header_kismi + payload_icerik
    return tam_paket

def parse_packet_header(tam_paket):
    header_boyutu = struct.calcsize('!I B Q')
    header_kismi = tam_paket[:header_boyutu]
    payload_icerik = tam_paket[header_boyutu:]
    
    packet_id, data_tipi, zaman_damgasi = struct.unpack('!I B Q', header_kismi)
    return packet_id, data_tipi, zaman_damgasi, payload_icerik

def chunk_data_split(tam_veri, chunk_boyutu):
    parca_listesi = []
    for idx_i in range(0, len(tam_veri), chunk_boyutu):
        veri_dilimi = tam_veri[idx_i:idx_i + chunk_boyutu]
        if len(veri_dilimi) < chunk_boyutu:
            veri_dilimi = veri_dilimi + b'\x00' * (chunk_boyutu - len(veri_dilimi))
        parca_listesi.append(veri_dilimi)
    return parca_listesi
