import requests
import json
import os
import time
from datetime import datetime, timedelta
from tqdm import tqdm
import config


def nasa_neows_veri_cek(baslangic_tarihi, bitis_tarihi):
    tum_asteroidler = []
    baslangic = datetime.strptime(baslangic_tarihi, "%Y-%m-%d")
    bitis = datetime.strptime(bitis_tarihi, "%Y-%m-%d")

    current = baslangic
    while current < bitis:
        chunk_end = min(current + timedelta(days=7), bitis)
        params = {
            "start_date": current.strftime("%Y-%m-%d"),
            "end_date": chunk_end.strftime("%Y-%m-%d"),
            "api_key": config.NASA_API_KEY,
        }
        try:
            response = requests.get(f"{config.NASA_NEOWS_URL}/feed", params=params, timeout=30)
            response.raise_for_status()
            veri = response.json()

            for tarih, asteroid_listesi in veri.get("near_earth_objects", {}).items():
                for asteroid in asteroid_listesi:
                    islenmis = _neows_asteroid_isle(asteroid, tarih)
                    if islenmis:
                        tum_asteroidler.append(islenmis)
        except requests.exceptions.RequestException:
            pass

        current = chunk_end
        time.sleep(0.5)

    return tum_asteroidler


def _neows_asteroid_isle(asteroid, tarih):
    try:
        yakin_gecis = asteroid.get("close_approach_data", [{}])[0]
        sonuc = {
            "asteroid_id": asteroid.get("id", ""),
            "asteroid_adi": asteroid.get("name", ""),
            "tarih": tarih,
            "absolute_magnitude": float(asteroid.get("absolute_magnitude_h", 0)),
            "estimated_diameter_min_km": float(
                asteroid.get("estimated_diameter", {})
                .get("kilometers", {})
                .get("estimated_diameter_min", 0)
            ),
            "estimated_diameter_max_km": float(
                asteroid.get("estimated_diameter", {})
                .get("kilometers", {})
                .get("estimated_diameter_max", 0)
            ),
            "relative_velocity_km_s": float(
                yakin_gecis.get("relative_velocity", {}).get("kilometers_per_second", 0)
            ),
            "miss_distance_au": float(
                yakin_gecis.get("miss_distance", {}).get("astronomical", 0)
            ),
            "miss_distance_km": float(
                yakin_gecis.get("miss_distance", {}).get("kilometers", 0)
            ),
            "miss_distance_lunar": float(
                yakin_gecis.get("miss_distance", {}).get("lunar", 0)
            ),
            "is_hazardous": 1 if asteroid.get("is_potentially_hazardous_asteroid", False) else 0,
            "orbiting_body": yakin_gecis.get("orbiting_body", "Earth"),
        }
        return sonuc
    except (ValueError, IndexError, KeyError):
        return None


def sentry_risk_verisi_cek():
    tehdit_listesi = []
    try:
        response = requests.get(config.NASA_SENTRY_URL, timeout=30)
        response.raise_for_status()
        veri = response.json()

        for nesne in veri.get("data", []):
            islenmis = {
                "asteroid_id": nesne.get("des", ""),
                "asteroid_adi": nesne.get("fullname", ""),
                "impact_probability": float(nesne.get("ip", 0)),
                "palermo_scale": float(nesne.get("ps_cum", -10)),
                "torino_scale": int(nesne.get("ts_max", 0)),
                "absolute_magnitude": float(nesne.get("h", 0)),
                "estimated_diameter_km": float(nesne.get("diameter", 0)),
                "approach_velocity_km_s": float(nesne.get("v_inf", 0)),
                "impact_count": int(nesne.get("n_imp", 0)),
                "risk_range": nesne.get("range", ""),
                "last_observation": nesne.get("last_obs", ""),
            }
            tehdit_listesi.append(islenmis)
    except requests.exceptions.RequestException:
        pass

    return tehdit_listesi


def sentry_nesne_detay_cek(designation):
    try:
        params = {"des": designation}
        response = requests.get(config.NASA_SENTRY_URL, params=params, timeout=30)
        response.raise_for_status()
        veri = response.json()

        ozet = veri.get("summary", {})
        vi_listesi = []

        for vi in veri.get("data", []):
            vi_bilgi = {
                "tarih": vi.get("date", ""),
                "impact_probability": float(vi.get("ip", 0)),
                "energy_mt": float(vi.get("energy", 0)),
                "palermo_scale": float(vi.get("ps", -10)),
                "sigma_vi": float(vi.get("sigma_vi", 0)),
            }
            vi_listesi.append(vi_bilgi)

        return {"ozet": ozet, "sanal_carpisanlar": vi_listesi}
    except requests.exceptions.RequestException:
        return None


def yakin_gecis_verisi_cek(mesafe_limit_au=None, tarih_min=None, tarih_max=None):
    if mesafe_limit_au is None:
        mesafe_limit_au = config.YAKIN_GECIS_MESAFE_LIMIT_AU
    if tarih_min is None:
        tarih_min = "1900-01-01"
    if tarih_max is None:
        tarih_max = "2200-01-01"

    yakin_gecisler = []
    try:
        params = {
            "dist-max": str(mesafe_limit_au),
            "date-min": tarih_min,
            "date-max": tarih_max,
            "sort": "dist",
        }
        response = requests.get(config.NASA_CAD_URL, params=params, timeout=60)
        response.raise_for_status()
        veri = response.json()

        alanlar = veri.get("fields", [])
        for satir in veri.get("data", []):
            kayit = dict(zip(alanlar, satir))
            yakin_gecisler.append(kayit)
    except requests.exceptions.RequestException:
        pass

    return yakin_gecisler


def sbdb_yorunge_verisi_cek(asteroid_adi):
    try:
        params = {"sstr": asteroid_adi}
        response = requests.get(config.NASA_SBDB_URL, params=params, timeout=30)
        response.raise_for_status()
        veri = response.json()

        yorunge = veri.get("orbit", {}).get("elements", [])
        yorunge_dict = {}
        for eleman in yorunge:
            yorunge_dict[eleman.get("name", "")] = eleman.get("value", "")

        return {
            "eccentricity": float(yorunge_dict.get("e", 0)),
            "semi_major_axis": float(yorunge_dict.get("a", 0)),
            "inclination": float(yorunge_dict.get("i", 0)),
            "period": float(yorunge_dict.get("per", 0)) if yorunge_dict.get("per") else 0,
            "yukselme_dugumu": float(yorunge_dict.get("om", 0)),
            "perihelion_arg": float(yorunge_dict.get("w", 0)),
        }
    except (requests.exceptions.RequestException, ValueError):
        return None


def esa_risk_listesi_cek():
    esa_veriler = []
    try:
        response = requests.get(
            f"{config.ESA_NEOCC_URL}/PSDB/risklist/json",
            timeout=30,
            headers={"Accept": "application/json"}
        )
        response.raise_for_status()
        veri = response.json()

        for nesne in veri if isinstance(veri, list) else veri.get("data", []):
            esa_kayit = {
                "asteroid_adi": nesne.get("name", nesne.get("objectName", "")),
                "impact_probability": float(nesne.get("ip", nesne.get("impactProbability", 0))),
                "palermo_scale": float(nesne.get("ps", nesne.get("palermoScale", -10))),
                "torino_scale": int(nesne.get("ts", nesne.get("torinoScale", 0))),
                "source": "ESA",
            }
            esa_veriler.append(esa_kayit)
    except requests.exceptions.RequestException:
        pass

    return esa_veriler


def toplu_veri_topla(gun_sayisi=None, ilerleme_goster=True):
    if gun_sayisi is None:
        gun_sayisi = config.VARSAYILAN_GUN_ARALIGI

    bugun = datetime.now()
    baslangic = (bugun - timedelta(days=gun_sayisi)).strftime("%Y-%m-%d")
    bitis = bugun.strftime("%Y-%m-%d")

    toplanan_veri = {
        "neows_asteroidler": [],
        "sentry_tehditler": [],
        "yakin_gecisler": [],
        "esa_riskler": [],
    }

    if ilerleme_goster:
        print(f"[*] NASA NeoWs verileri cekiliyor ({baslangic} - {bitis})...")
    toplanan_veri["neows_asteroidler"] = nasa_neows_veri_cek(baslangic, bitis)
    if ilerleme_goster:
        print(f"    -> {len(toplanan_veri['neows_asteroidler'])} asteroid bulundu")

    if ilerleme_goster:
        print("[*] NASA Sentry risk verileri cekiliyor...")
    toplanan_veri["sentry_tehditler"] = sentry_risk_verisi_cek()
    if ilerleme_goster:
        print(f"    -> {len(toplanan_veri['sentry_tehditler'])} tehdit bulundu")

    if ilerleme_goster:
        print("[*] Yakin gecis verileri cekiliyor...")
    toplanan_veri["yakin_gecisler"] = yakin_gecis_verisi_cek()
    if ilerleme_goster:
        print(f"    -> {len(toplanan_veri['yakin_gecisler'])} yakin gecis bulundu")

    if ilerleme_goster:
        print("[*] ESA NEOCC risk listesi cekiliyor...")
    toplanan_veri["esa_riskler"] = esa_risk_listesi_cek()
    if ilerleme_goster:
        print(f"    -> {len(toplanan_veri['esa_riskler'])} ESA riski bulundu")

    os.makedirs(config.VERI_KLASORU, exist_ok=True)
    kayit_yolu = os.path.join(config.VERI_KLASORU, "ham_veri.json")
    with open(kayit_yolu, "w", encoding="utf-8") as f:
        json.dump(toplanan_veri, f, ensure_ascii=False, indent=2)

    if ilerleme_goster:
        print(f"[+] Tum veriler kaydedildi: {kayit_yolu}")

    return toplanan_veri


def yorunge_verileri_zenginlestir(asteroid_listesi, ilerleme_goster=True):
    zenginlestirilmis = []
    iterator = tqdm(asteroid_listesi, desc="Yorunge verileri") if ilerleme_goster else asteroid_listesi

    for asteroid in iterator:
        asteroid_id = asteroid.get("asteroid_adi", asteroid.get("asteroid_id", ""))
        yorunge = sbdb_yorunge_verisi_cek(asteroid_id)

        if yorunge:
            asteroid["orbit_eccentricity"] = yorunge.get("eccentricity", 0)
            asteroid["orbit_semi_major_axis"] = yorunge.get("semi_major_axis", 0)
            asteroid["orbit_inclination"] = yorunge.get("inclination", 0)
            asteroid["orbit_period"] = yorunge.get("period", 0)
        else:
            asteroid["orbit_eccentricity"] = 0
            asteroid["orbit_semi_major_axis"] = 0
            asteroid["orbit_inclination"] = 0
            asteroid["orbit_period"] = 0

        zenginlestirilmis.append(asteroid)
        time.sleep(0.3)

    return zenginlestirilmis
