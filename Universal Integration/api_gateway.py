import socket
import json
from protocol_translator import normalize_to_universal_format
from security import verify_node_token
from module_registry import NodeKayitSistemi
import config

class GatewayServerDugumu:
    def __init__(self, message_bus_obj):
        self.ip_address = config.HUB_LISTEN_IP
        self.port_number = config.HUB_PORT_NUMBER
        self.sock_obj = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.kayit_motoru = NodeKayitSistemi()
        self.m_bus = message_bus_obj

    def start_listening(self):
        self.sock_obj.bind((self.ip_address, self.port_number))
        self.sock_obj.settimeout(2.0)

    def receive_and_route(self):
        try:
            gelen_udp_bytes, address_info = self.sock_obj.recvfrom(2048)
            decoded_str = gelen_udp_bytes.decode('utf-8')
            json_parsed = json.loads(decoded_str)
            
            node_kodu = json_parsed.get("node_id", "")
            guvenlik_token = json_parsed.get("token", "")
            
            if verify_node_token(guvenlik_token, node_kodu):
                self.kayit_motoru.register_new_node(node_kodu, "SATELLITE", address_info[0])
                ham_data = json_parsed.get("data", {})
                kaynak_tipi = json_parsed.get("source_type", "GCODE_TELEMETRY")
                
                evrensel_model = normalize_to_universal_format(ham_data, kaynak_tipi)
                
                if evrensel_model["priority"] == "CRITICAL":
                    self.m_bus.publish_event("CRITICAL_THREAT", evrensel_model)
                else:
                    self.m_bus.publish_event("NORMAL_TELEMETRY", evrensel_model)
                    
                return True
            return False
        except socket.timeout:
            return None
        except Exception:
            return False
