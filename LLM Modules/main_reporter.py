from llm_analyzer import SpaceLLMAnalyzer
from pdf_creator import create_event_pdf

def trigger_emergency_event(event_tur_ismi, event_raw_dict):
    llm_yapay_zeka = SpaceLLMAnalyzer()
    
    uretilen_text_raporu = llm_yapay_zeka.generate_report_text(event_raw_dict)
    
    kaydedilen_pdf_yolu = create_event_pdf(uretilen_text_raporu, event_tur_ismi)
    
    print(f"[{event_tur_ismi}] OLAYI TESPIT EDILDI.")
    print("AI LLM RAPOR OLUSTURMA BASARILI OLMUSTUR.")
    print("GIZLI PDF RAPORU URETILDI:", kaydedilen_pdf_yolu)
    
if __name__ == "__main__":
    test_uydu_verisi = {
        "sensor_id": "SAT-99_RADAR",
        "anomaly_type": "Kritik Yakinlasma (Close Approach)",
        "distance_km": 1.2,
        "object_detected": "Uzay Copu (DEB-291)",
        "time_to_impact_sec": 450
    }
    trigger_emergency_event("CATISMA_RISKI", test_uydu_verisi)
