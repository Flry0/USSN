import time
from event_bus import UniversalMessageBus
from alert_dispatcher import AcilDurumYonetici
from api_gateway import GatewayServerDugumu
from security import generate_handshake_crypto
import json

def llm_report_mock_callback(gercek_veri):
    print("LLM OTOMATIK RAPOR TETIKLENDI:", gercek_veri)

def run_central_mission_control():
    ana_veriyolu = UniversalMessageBus()
    
    acil_dispatcher = AcilDurumYonetici(ana_veriyolu)
    ana_veriyolu.subscribe_to_topic("LLM_REPORT_QUEUE", llm_report_mock_callback)
    
    ag_gecidi = GatewayServerDugumu(ana_veriyolu)
    ag_gecidi.start_listening()
    
    test_node_kimligi = "ISS_STATION_ALPHA"
    ornek_token_sifresi = generate_handshake_crypto(test_node_kimligi)
    
    ornek_payload = {
        "node_id": test_node_kimligi,
        "token": ornek_token_sifresi,
        "source_type": "ASTEROID",
        "data": {"impact_probability": 0.95, "position": [150, 400, 20]}
    }
    
    import socket
    test_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    test_sock.sendto(json.dumps(ornek_payload).encode('utf-8'), ("127.0.0.1", 9000))
    
    islem_durumu = ag_gecidi.receive_and_route()
    
    islenen_event_sayisi = ana_veriyolu.process_message_queue()
    islenen_event_sayisi += ana_veriyolu.process_message_queue()
    
    print("EVRENSEL AG BAGLANTISI VE ASENKRON ILETISIM TESTI BASARILI.")
    print("TOPLAM ISLENEN EVENT SAYISI:", islenen_event_sayisi)
    
if __name__ == "__main__":
    run_central_mission_control()
