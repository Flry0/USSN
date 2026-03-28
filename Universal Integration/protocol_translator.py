def normalize_to_universal_format(gelen_veri_dict, kaynak_protokol):
    evrensel_payload = {"source": kaynak_protokol, "priority": "LOW", "danger_score": 0.0, "coordinates": []}
    
    if kaynak_protokol == "WEATHER":
        evrensel_payload["danger_score"] = float(gelen_veri_dict.get("kp_index", 0.0)) * 10.0
        evrensel_payload["priority"] = "HIGH" if evrensel_payload["danger_score"] > 70 else "LOW"
        
    elif kaynak_protokol == "ASTEROID":
        evrensel_payload["danger_score"] = float(gelen_veri_dict.get("impact_probability", 0.0)) * 100.0
        evrensel_payload["coordinates"] = gelen_veri_dict.get("position", [0,0,0])
        evrensel_payload["priority"] = "CRITICAL" if evrensel_payload["danger_score"] > 85 else "MEDIUM"
        
    elif kaynak_protokol == "GCODE_TELEMETRY":
        evrensel_payload["coordinates"] = [gelen_veri_dict.get("X", 0), gelen_veri_dict.get("Y", 0), gelen_veri_dict.get("Z", 0)]
        
    return evrensel_payload
