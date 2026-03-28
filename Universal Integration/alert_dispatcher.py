import time

class AcilDurumYonetici:
    def __init__(self, evrensel_bus_obj):
        self.bus_sistemi = evrensel_bus_obj
        self.bus_sistemi.subscribe_to_topic("CRITICAL_THREAT", self.handle_critical_alert)
        self.son_uyarilar = []

    def handle_critical_alert(self, danger_payload):
        zaman_id = int(time.time())
        raporlanacak_veri = {
            "tam_zaman": zaman_id,
            "tehlike_seviyesi": danger_payload.get("danger_score", 100),
            "kaynak_modul": danger_payload.get("source", "UNKNOWN")
        }
        self.son_uyarilar.append(raporlanacak_veri)
        
        yapay_zeka_istegi = {"action": "TRIGGER_LLM_PDF", "details": raporlanacak_veri}
        self.bus_sistemi.publish_event("LLM_REPORT_QUEUE", yapay_zeka_istegi)
        
        return True
