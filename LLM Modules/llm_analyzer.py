import llm_config
import json
import urllib.request

class SpaceLLMAnalyzer:
    def __init__(self):
        self.ollama_url = llm_config.OLLAMA_API_URL
        self.ai_model_name = llm_config.MODEL_ISMI

    def generate_report_text(self, event_data_dict):
        request_prompt = f"{llm_config.SYSTEM_PROMPT_METNI}\n\nOLAY VERISI:\n{json.dumps(event_data_dict)}"
        
        try:
            istem_bileseni = {
                "model": self.ai_model_name,
                "prompt": request_prompt,
                "stream": False
            }
            encode_edilmis_veri = json.dumps(istem_bileseni).encode('utf-8')
            http_request_objesi = urllib.request.Request(self.ollama_url, data=encode_edilmis_veri, headers={'Content-Type': 'application/json'})
            
            with urllib.request.urlopen(http_request_objesi) as baglanti_sonucu:
                gelen_ham_cevap = baglanti_sonucu.read().decode('utf-8')
                json_cevap_parsed = json.loads(gelen_ham_cevap)
                gercek_llm_metni = json_cevap_parsed.get("response", "")
                return gercek_llm_metni
        except Exception as e_hata:
            return "ollamada hata var"