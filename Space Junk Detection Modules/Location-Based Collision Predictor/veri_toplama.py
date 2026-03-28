import os
import json
import random
from datetime import datetime
import config

def uzay_copu_verisi_olustur(isimler, n_samples=1000):
    veriler = []
    for i in range(n_samples):
        miss_dist = random.uniform(0.1, 2000.0)
        vel = random.uniform(5.0, 20.0)
        
        # Carpma riski olan nesneler
        hazardous = 1 if (miss_dist < 50.0 and vel > 10.0) else 0
        impact_prob = random.uniform(0.0001, 0.05) if hazardous else random.uniform(0, 0.00001)
        
        veriler.append({
            "uzay_copu_id": f"DEB-{random.randint(10000,99999)}",
            "uzay_copu_adi": random.choice(isimler) + f" DEB {i}",
            "estimated_diameter_min_km": random.uniform(0.001, 0.1),
            "estimated_diameter_max_km": random.uniform(0.01, 0.5),
            "relative_velocity_km_s": vel,
            "miss_distance_km": miss_dist,
            "absolute_magnitude": random.uniform(15.0, 30.0),
            "orbit_eccentricity": random.uniform(0.0, 0.5),
            "orbit_semi_major_axis": random.uniform(6000, 40000),
            "orbit_inclination": random.uniform(0, 180),
            "is_hazardous": hazardous,
            "impact_probability": impact_prob
        })
    return veriler

def toplu_veri_topla(gun_sayisi=None, ilerleme_goster=True):
    isimler = ["FENGYUN 1C", "COSMOS 2251", "IRIDIUM 33", "ARIANE 4", "DELTA II", "TITAN IIIC", "SOYUZ"]
    
    if ilerleme_goster:
        print("[*] Uzay copu (Space Debris) veritabanı simüle ediliyor veya CSV'den çekiliyor...")
    
    simule_veriler = uzay_copu_verisi_olustur(isimler, 5000)
    
    toplanan_veri = {
        "uzay_copuler": simule_veriler
    }

    os.makedirs(config.VERI_KLASORU, exist_ok=True)
    kayit_yolu = os.path.join(config.VERI_KLASORU, "ham_veri.json")
    with open(kayit_yolu, "w", encoding="utf-8") as f:
        json.dump(toplanan_veri, f, ensure_ascii=False, indent=2)

    if ilerleme_goster:
        print(f"[+] Tum veriler kaydedildi: {kayit_yolu}")

    return toplanan_veri

def yorunge_verileri_zenginlestir(uzay_copu_listesi, ilerleme_goster=True):
    return uzay_copu_listesi
