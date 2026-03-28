import threading
import time
import json
import numpy as np
from data_sender import SatelliteSenderNode
from data_receiver import EarthReceiverNode
from telemetry_gcode import telemetri_olustur_gcode, gcode_cozumle
from video_compressor import calculate_frame_delta, reconstruct_frame
from error_correction import recover_data_chunk
import config

def baslat_earth_receiver():
    rx_node = EarthReceiverNode(config.HOST_IP, config.PORT_RX)
    while True:
        rx_sonuc = rx_node.receive_and_decode(2)
        if rx_sonuc and rx_sonuc != b"HASH_ERROR":
            try:
                parsed_gcode_sonuc = gcode_cozumle(rx_sonuc)
                print("GELEN TELEMETRI:", parsed_gcode_sonuc)
            except:
                pass

def main_execution():
    threading.Thread(target=baslat_earth_receiver, daemon=True).start()
    time.sleep(1)
    
    tx_node = SatelliteSenderNode(config.HOST_IP, config.PORT_RX)
    
    olusturulan_gcode_verisi = telemetri_olustur_gcode(100.5, 200.75, -50.2, 7500.0, 98.5)
    tx_node.transmit_secure_data(olusturulan_gcode_verisi, 1)
    
    eski_goruntu_frame = np.ones((10, 10), dtype=np.uint8) * 50
    yeni_goruntu_frame = np.ones((10, 10), dtype=np.uint8) * 50
    yeni_goruntu_frame[4:6, 4:6] = 255
    
    compress_edilmis_delta = calculate_frame_delta(yeni_goruntu_frame, eski_goruntu_frame, config.DELTA_THRESHOLD)
    json_delta_encode = json.dumps(compress_edilmis_delta).encode('utf-8')
    
    tx_node.transmit_secure_data(json_delta_encode, 2)
    
    recovered_orijinal = reconstruct_frame(eski_goruntu_frame, compress_edilmis_delta)
    print("VIDEO DELTA COMPRESSION TAMAMLANDI.")
    
    kayip_test_veriler = [b"PART1___", None, b"PART3___"]
    parity_test = b"PARITY__"
    kurtarilan_test = recover_data_chunk(kayip_test_veriler, 1, parity_test)
    print("FORWARD ERROR CORRECTION (FEC / QR-Style) KURTARMA TAMAMLANDI.")
    
    print("LOW BANDWIDTH COMMUNICATION SYSTEM TEST BITTI.")

if __name__ == "__main__":
    main_execution()
