import requests
import json
import os
import random
from datetime import datetime, timedelta
import config


def gercek_noaa_verisi_cek():
    veri = {}
    try:
        # X-Ray Flux
        res_xray = requests.get(config.NOAA_XRAY_URL, timeout=10)
        res_xray.raise_for_status()
        xray_liste = res_xray.json()
        if xray_liste:
            son_xray = xray_liste[-1]
            veri["xray_flux"] = float(son_xray.get("flux", 1e-8))
        else:
            veri["xray_flux"] = 1e-8
            
        #Hiz Yogunluk Sicaklik
        res_plasma = requests.get(config.NOAA_PLASMA_URL, timeout=10)
        res_plasma.raise_for_status()
        plasma_liste = res_plasma.json()
        if len(plasma_liste) > 1:
            son_plasma = plasma_liste[-1]
            veri["solar_wind_density"] = float(son_plasma[1] if son_plasma[1] else 5.0)
            veri["solar_wind_speed"] = float(son_plasma[2] if son_plasma[2] else 400.0)
            veri["solar_wind_temp"] = float(son_plasma[3] if son_plasma[3] else 100000.0)
        else:
            veri["solar_wind_density"] = 5.0
            veri["solar_wind_speed"] = 400.0
            veri["solar_wind_temp"] = 100000.0
        res_mag = requests.get(config.NOAA_MAG_URL, timeout=10)
        res_mag.raise_for_status()
        mag_liste = res_mag.json()
        if len(mag_liste) > 1:
            son_mag = mag_liste[-1]
            veri["bz_gsm"] = float(son_mag[3] if son_mag[3] else 0.0)
            veri["bt_total"] = float(son_mag[6] if son_mag[6] else 5.0)
        else:
            veri["bz_gsm"] = 0.0
            veri["bt_total"] = 5.0

        #Kp
        res_kp = requests.get(config.NOAA_KP_URL, timeout=10)
        res_kp.raise_for_status()
        kp_liste = res_kp.json()
        if len(kp_liste) > 1:
            son_kp = kp_liste[-1]
            veri["kp_index"] = float(son_kp[1] if son_kp[1] else 1.0)
        else:
            veri["kp_index"] = 1.0

        veri["energetic_protons"] = 0.1
    except Exception as e:
        print(f"[!] NOAA'dan gercek zamanli veri cekilemedi: {e}")
        return None

    return veri


def hava_durumu_verisi_olustur(n_samples=1000):
    veriler = []
    
    for _ in range(n_samples):
        
        SANS = random.random()
        if SANS > 0.95:
            xray = random.uniform(1e-4, 5e-3)
            speed = random.uniform(800.0, 1500.0)
            density = random.uniform(20.0, 100.0)
            bz = random.uniform(-50.0, -10.0)
            bt = random.uniform(20.0, 60.0)
            kp = random.uniform(7.0, 9.0)
            protons = random.uniform(10.0, 500.0) # pfu
        elif SANS > 0.80:
            xray = random.uniform(1e-5, 1e-4)
            speed = random.uniform(500.0, 800.0)
            density = random.uniform(10.0, 30.0)
            bz = random.uniform(-15.0, 0.0)
            bt = random.uniform(10.0, 25.0)
            kp = random.uniform(4.0, 6.9)
            protons = random.uniform(1.0, 10.0)
        else:
            xray = random.uniform(1e-8, 1e-6)
            speed = random.uniform(250.0, 500.0)
            density = random.uniform(1.0, 10.0)
            bz = random.uniform(-5.0, 10.0)
            bt = random.uniform(1.0, 10.0)
            kp = random.uniform(0.0, 3.9)
            protons = random.uniform(0.01, 1.0)
            
        temp = random.uniform(50000.0, 500000.0)

        risk = 0
        if kp >= 4.0 or density > 15.0 or xray >= 1e-5:
            risk = 1
        if kp >= 6.0 or (speed > 600.0 and bz < -5.0) or xray >= 5e-5:
            risk = 2
        if kp >= 8.0 or speed > 900.0 or xray >= 1e-4 or protons > 100.0:
            risk = 3

        veriler.append({
            "xray_flux": xray,
            "solar_wind_speed": speed,
            "solar_wind_density": density,
            "solar_wind_temp": temp,
            "bz_gsm": bz,
            "bt_total": bt,
            "kp_index": kp,
            "energetic_protons": protons,
            "risk_derecesi": risk,
            "tarih": (datetime.now() - timedelta(minutes=random.randint(1, 100000))).strftime("%Y-%m-%d %H:%M:%S")
        })

    return veriler


def toplu_veri_topla(ilerleme_goster=True):
    if ilerleme_goster:
        print("[*] Uzay Havasi (Space Weather) istatistiksel veritabani simule ediliyor...")
    
    simule_veriler = hava_durumu_verisi_olustur(config.VARSAYILAN_ORNEK_SAYISI)
    
    toplanan_veri = {
        "uzay_havasi": simule_veriler
    }

    os.makedirs(config.VERI_KLASORU, exist_ok=True)
    kayit_yolu = os.path.join(config.VERI_KLASORU, "ham_veri.json")
    with open(kayit_yolu, "w", encoding="utf-8") as f:
        json.dump(toplanan_veri, f, ensure_ascii=False, indent=2)

    if ilerleme_goster:
        print(f"[+] Tum egitim verileri kaydedildi: {kayit_yolu}")

    return toplanan_veri
