import os
import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime
import config
from veri_toplama import (
    nasa_neows_veri_cek,
    sentry_risk_verisi_cek,
    sentry_nesne_detay_cek,
    yakin_gecis_verisi_cek,
    sbdb_yorunge_verisi_cek,
    esa_risk_listesi_cek,
)
from veri_isleme import ozellik_muhendisligi, eksik_verileri_doldur
from model import CarpismaTahminModeli, CokluModelToplulugu


def modeli_yukle(topluluk_mu=False):
    if topluluk_mu:
        topluluk_yolu = os.path.join(config.MODEL_KAYIT_YOLU, "topluluk")
        if os.path.exists(topluluk_yolu):
            return CokluModelToplulugu.yukle()
    return CarpismaTahminModeli.yukle()


def tek_asteroid_tahmin(asteroid_bilgisi, model):
    df = pd.DataFrame([asteroid_bilgisi])

    for sutun in ["orbit_eccentricity", "orbit_semi_major_axis", "orbit_inclination", "orbit_period"]:
        if sutun not in df.columns:
            df[sutun] = 0.0

    df["is_hazardous"] = df.get("is_hazardous", pd.Series([0]))
    df = ozellik_muhendisligi(df)
    df = eksik_verileri_doldur(df)

    if isinstance(model, CokluModelToplulugu):
        ozellikler = [s for s in config.OZELLIK_SUTUNLARI if s in df.columns]
        X = df[ozellikler]
        tahmin = model.toplu_tahmin(X)
    else:
        X = model.ozellikleri_hazirla(df)
        tahmin = model.tahmin_et(X)

    return float(tahmin[0])


def uydu_carpma_analizi(asteroid_bilgisi, model, uydu_yukseklik_km=400):
    dunya_yaricap_km = 6371
    uydu_yorunge_yaricap = dunya_yaricap_km + uydu_yukseklik_km

    temel_olasilik = tek_asteroid_tahmin(asteroid_bilgisi, model)

    kacirma_km = asteroid_bilgisi.get("miss_distance_km", 1e9)
    cap_km = (
        asteroid_bilgisi.get("estimated_diameter_min_km", 0)
        + asteroid_bilgisi.get("estimated_diameter_max_km", 0)
    ) / 2

    uydu_bolgesi_km = uydu_yorunge_yaricap * 2 * np.pi
    uydu_kesit_orani = uydu_yukseklik_km / uydu_bolgesi_km

    if kacirma_km < uydu_yorunge_yaricap + cap_km:
        uydu_carpma_olasiligi = temel_olasilik * uydu_kesit_orani * 100
    elif kacirma_km < uydu_yorunge_yaricap * 2:
        yakinlik_faktoru = 1 - (kacirma_km - uydu_yorunge_yaricap) / uydu_yorunge_yaricap
        uydu_carpma_olasiligi = temel_olasilik * uydu_kesit_orani * yakinlik_faktoru * 50
    else:
        mesafe_orani = uydu_yorunge_yaricap / kacirma_km
        uydu_carpma_olasiligi = temel_olasilik * (mesafe_orani ** 2) * uydu_kesit_orani

    return {
        "temel_carpma_olasiligi": temel_olasilik,
        "uydu_carpma_olasiligi": min(uydu_carpma_olasiligi, 1.0),
        "uydu_yukseklik_km": uydu_yukseklik_km,
        "kacirma_mesafesi_km": kacirma_km,
        "asteroid_cap_km": cap_km,
        "risk_seviyesi": _risk_seviyesi_belirle(uydu_carpma_olasiligi),
    }


def _risk_seviyesi_belirle(olasilik):
    if olasilik >= 0.01:
        return "KRITIK"
    elif olasilik >= 0.001:
        return "YUKSEK"
    elif olasilik >= 1e-5:
        return "ORTA"
    elif olasilik >= 1e-8:
        return "DUSUK"
    else:
        return "IHMAL EDILEBILIR"


def canli_tarama_yap(model, gun_araligi=7):
    bugun = datetime.now()
    baslangic = bugun.strftime("%Y-%m-%d")
    from datetime import timedelta
    bitis = (bugun + timedelta(days=gun_araligi)).strftime("%Y-%m-%d")

    print(f"\n[*] Canli tarama yapiliyor ({baslangic} - {bitis})...")
    asteroidler = nasa_neows_veri_cek(baslangic, bitis)

    if not asteroidler:
        print("[!] Hicbir asteroid bulunamadi")
        return []

    sonuclar = []
    print(f"[*] {len(asteroidler)} asteroid analiz ediliyor...")

    for asteroid in asteroidler:
        try:
            tahmin = tek_asteroid_tahmin(asteroid, model)
            uydu_analiz = uydu_carpma_analizi(asteroid, model)

            sonuc = {
                "asteroid_adi": asteroid.get("asteroid_adi", "Bilinmiyor"),
                "asteroid_id": asteroid.get("asteroid_id", ""),
                "tarih": asteroid.get("tarih", ""),
                "impact_probability": tahmin,
                "satellite_impact_probability": uydu_analiz["uydu_carpma_olasiligi"],
                "risk_seviyesi": uydu_analiz["risk_seviyesi"],
                "diameter_km": (asteroid.get("estimated_diameter_min_km", 0) + asteroid.get("estimated_diameter_max_km", 0)) / 2,
                "velocity_km_s": asteroid.get("relative_velocity_km_s", 0),
                "miss_distance_km": asteroid.get("miss_distance_km", 0),
                "is_hazardous": asteroid.get("is_hazardous", 0),
            }
            sonuclar.append(sonuc)
        except Exception:
            pass

    sonuclar.sort(key=lambda x: x["impact_probability"], reverse=True)
    return sonuclar


def sentry_analizi_yap(model):
    print("\n[*] Sentry risk verileri analiz ediliyor...")
    tehditler = sentry_risk_verisi_cek()

    if not tehditler:
        print("[!] Sentry verisi bulunamadi")
        return []

    analiz_sonuclari = []
    for tehdit in tehditler:
        sentry_ip = tehdit.get("impact_probability", 0)
        palermo = tehdit.get("palermo_scale", -10)
        torino = tehdit.get("torino_scale", 0)
        cap = tehdit.get("estimated_diameter_km", 0)
        hiz = tehdit.get("approach_velocity_km_s", 0)

        if cap > 0 and hiz > 0:
            enerji_mt = 0.5 * (cap ** 3) * (np.pi / 6) * 3000 * (hiz * 1000) ** 2 / 4.184e15
        else:
            enerji_mt = 0

        analiz = {
            "asteroid_adi": tehdit.get("asteroid_adi", ""),
            "sentry_impact_probability": sentry_ip,
            "palermo_scale": palermo,
            "torino_scale": torino,
            "diameter_km": cap,
            "velocity_km_s": hiz,
            "estimated_energy_mt": enerji_mt,
            "impact_count": tehdit.get("impact_count", 0),
            "risk_range": tehdit.get("risk_range", ""),
            "risk_seviyesi": _risk_seviyesi_belirle(sentry_ip),
        }
        analiz_sonuclari.append(analiz)

    analiz_sonuclari.sort(key=lambda x: x["sentry_impact_probability"], reverse=True)
    return analiz_sonuclari


def sonuclari_yazdir(sonuclar, baslik="ANALIZ SONUCLARI"):
    print(f"\n{'=' * 80}")
    print(f"  {baslik}")
    print(f"{'=' * 80}")

    if not sonuclar:
        print("  Sonuc bulunamadi.")
        return

    for i, sonuc in enumerate(sonuclar[:20], 1):
        isim = sonuc.get("asteroid_adi", "Bilinmiyor")
        print(f"\n  [{i}] {isim}")
        print(f"  {'─' * 40}")

        for anahtar, deger in sonuc.items():
            if anahtar == "asteroid_adi":
                continue
            if isinstance(deger, float):
                if abs(deger) < 0.001 and deger != 0:
                    deger_str = f"{deger:.2e}"
                else:
                    deger_str = f"{deger:.6f}"
            else:
                deger_str = str(deger)

            gosterim_adi = anahtar.replace("_", " ").title()
            print(f"    {gosterim_adi:30s}: {deger_str}")

    print(f"\n  Toplam: {len(sonuclar)} sonuc (ilk 20 gosterildi)")
    print(f"{'=' * 80}")


def sonuclari_kaydet(sonuclar, dosya_adi="analiz_sonuclari.json"):
    os.makedirs(config.VERI_KLASORU, exist_ok=True)
    kayit_yolu = os.path.join(config.VERI_KLASORU, dosya_adi)

    for sonuc in sonuclar:
        for anahtar, deger in sonuc.items():
            if isinstance(deger, (np.integer,)):
                sonuc[anahtar] = int(deger)
            elif isinstance(deger, (np.floating,)):
                sonuc[anahtar] = float(deger)

    with open(kayit_yolu, "w", encoding="utf-8") as f:
        json.dump(sonuclar, f, ensure_ascii=False, indent=2)

    print(f"\n[+] Sonuclar kaydedildi: {kayit_yolu}")
    return kayit_yolu


def interaktif_menu(model):
    while True:
        print(f"\n{'=' * 60}")
        print("  ASTEROID CARPMA OLASILIGI TAHMIN SISTEMI")
        print("  Ana Menu")
        print(f"{'=' * 60}")
        print("  [1] Canli asteroid taramasi (NeoWs)")
        print("  [2] Sentry risk analizi")
        print("  [3] Tek asteroid sorgulama")
        print("  [4] Uydu carpma analizi")
        print("  [5] ESA risk listesi")
        print("  [0] Cikis")
        print(f"{'=' * 60}")

        secim = input("\n  Seciminiz: ").strip()

        if secim == "1":
            gun = input("  Kac gunluk tarama? (varsayilan 7): ").strip()
            gun = int(gun) if gun.isdigit() else 7
            sonuclar = canli_tarama_yap(model, gun_araligi=gun)
            sonuclari_yazdir(sonuclar, "CANLI TARAMA SONUCLARI")
            if sonuclar:
                kaydet = input("\n  Sonuclari kaydetmek ister misiniz? (e/h): ").strip().lower()
                if kaydet == "e":
                    sonuclari_kaydet(sonuclar, "canli_tarama.json")

        elif secim == "2":
            sonuclar = sentry_analizi_yap(model)
            sonuclari_yazdir(sonuclar, "SENTRY RISK ANALIZI")
            if sonuclar:
                kaydet = input("\n  Sonuclari kaydetmek ister misiniz? (e/h): ").strip().lower()
                if kaydet == "e":
                    sonuclari_kaydet(sonuclar, "sentry_analiz.json")

        elif secim == "3":
            print("\n  Asteroid bilgilerini girin:")
            try:
                asteroid = {
                    "absolute_magnitude": float(input("    Mutlak parlaklik (H): ")),
                    "estimated_diameter_min_km": float(input("    Min cap (km): ")),
                    "estimated_diameter_max_km": float(input("    Max cap (km): ")),
                    "relative_velocity_km_s": float(input("    Hiz (km/s): ")),
                    "miss_distance_au": float(input("    Mesafe (AU): ")),
                    "miss_distance_km": float(input("    Mesafe (km): ")),
                    "miss_distance_lunar": float(input("    Mesafe (Lunar): ")),
                    "is_hazardous": int(input("    Tehlikeli mi? (0/1): ")),
                }
            except ValueError:
                print("  [!] Gecersiz deger girdiniz")
                continue

            tahmin = tek_asteroid_tahmin(asteroid, model)
            risk = _risk_seviyesi_belirle(tahmin)
            print(f"\n  {'=' * 40}")
            print(f"  Carpma Olasiligi: {tahmin:.2e}")
            print(f"  Risk Seviyesi:    {risk}")
            print(f"  {'=' * 40}")

        elif secim == "4":
            print("\n  Uydu bilgilerini girin:")
            try:
                uydu_yukseklik = float(input("    Uydu yuksekligi (km, varsayilan 400): ") or "400")
                asteroid = {
                    "absolute_magnitude": float(input("    Asteroid mutlak parlaklik (H): ")),
                    "estimated_diameter_min_km": float(input("    Asteroid min cap (km): ")),
                    "estimated_diameter_max_km": float(input("    Asteroid max cap (km): ")),
                    "relative_velocity_km_s": float(input("    Asteroid hiz (km/s): ")),
                    "miss_distance_au": float(input("    Mesafe (AU): ")),
                    "miss_distance_km": float(input("    Mesafe (km): ")),
                    "miss_distance_lunar": float(input("    Mesafe (Lunar): ")),
                    "is_hazardous": int(input("    Tehlikeli mi? (0/1): ")),
                }
            except ValueError:
                print("  [!] Gecersiz deger girdiniz")
                continue

            analiz = uydu_carpma_analizi(asteroid, model, uydu_yukseklik_km=uydu_yukseklik)
            print(f"\n  {'=' * 50}")
            print(f"  UYDU CARPMA ANALIZI")
            print(f"  {'─' * 50}")
            print(f"  Temel Carpma Olasiligi:  {analiz['temel_carpma_olasiligi']:.2e}")
            print(f"  Uydu Carpma Olasiligi:   {analiz['uydu_carpma_olasiligi']:.2e}")
            print(f"  Risk Seviyesi:           {analiz['risk_seviyesi']}")
            print(f"  Uydu Yuksekligi:         {analiz['uydu_yukseklik_km']} km")
            print(f"  Kacirma Mesafesi:        {analiz['kacirma_mesafesi_km']:.2f} km")
            print(f"  Asteroid Capi:           {analiz['asteroid_cap_km']:.4f} km")
            print(f"  {'=' * 50}")

        elif secim == "5":
            print("\n[*] ESA risk listesi cekiliyor...")
            esa_riskleri = esa_risk_listesi_cek()
            if esa_riskleri:
                sonuclari_yazdir(esa_riskleri, "ESA NEOCC RISK LISTESI")
            else:
                print("  [!] ESA verileri alinamadi")

        elif secim == "0":
            print("\n  Cikis yapiliyor...")
            break

        else:
            print("  [!] Gecersiz secim")


def programatik_kullanim(asteroid_verileri, model_yolu=None, topluluk_mu=False):
    if model_yolu:
        if topluluk_mu:
            model = CokluModelToplulugu.yukle(model_yolu)
        else:
            model = CarpismaTahminModeli.yukle(model_yolu)
    else:
        model = modeli_yukle(topluluk_mu=topluluk_mu)

    if isinstance(asteroid_verileri, dict):
        return tek_asteroid_tahmin(asteroid_verileri, model)
    elif isinstance(asteroid_verileri, list):
        return [tek_asteroid_tahmin(a, model) for a in asteroid_verileri]
    else:
        raise ValueError("asteroid_verileri dict ya da list olmali")


def main():
    print("\n" + "=" * 60)
    print("  ASTEROID CARPMA OLASILIGI TAHMIN SISTEMI")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    topluluk_mu = "--topluluk" in sys.argv

    topluluk_yolu = os.path.join(config.MODEL_KAYIT_YOLU, "topluluk")
    tekil_yolu = config.MODEL_KAYIT_YOLU

    if topluluk_mu and os.path.exists(topluluk_yolu):
        print("\n[*] Topluluk modeli yukleniyor...")
        model = CokluModelToplulugu.yukle()
        print("[+] Topluluk modeli yuklendi")
    elif os.path.exists(os.path.join(tekil_yolu, "carpma_modeli.joblib")):
        print("\n[*] Model yukleniyor...")
        model = CarpismaTahminModeli.yukle()
        print("[+] Model yuklendi")
    else:
        print("\n[!] Egitilmis model bulunamadi!")
        print("[!] Lutfen once train.py'yi calistirin:")
        print("    python train.py")
        sys.exit(1)

    if "--tarama" in sys.argv:
        gun = 7
        for i, arg in enumerate(sys.argv):
            if arg == "--gun" and i + 1 < len(sys.argv):
                gun = int(sys.argv[i + 1])
        sonuclar = canli_tarama_yap(model, gun_araligi=gun)
        sonuclari_yazdir(sonuclar, "CANLI TARAMA")
        sonuclari_kaydet(sonuclar)
    elif "--sentry" in sys.argv:
        sonuclar = sentry_analizi_yap(model)
        sonuclari_yazdir(sonuclar, "SENTRY ANALIZI")
        sonuclari_kaydet(sonuclar, "sentry_sonuclari.json")
    else:
        interaktif_menu(model)


if __name__ == "__main__":
    main()
