import os
import sys
import pandas as pd
import numpy as np
import time
import getpass
from colorama import init, Fore, Style
from model import UzayYoluTahminModeli
from veri_toplama import gercek_noaa_verisi_cek
from veri_isleme import ozellik_muhendisligi

init(autoreset=True)

def ekran_temizle():
    os.system('cls' if os.name == 'nt' else 'clear')

def asistan_mesaji(risk_seviyesi):
    if risk_seviyesi == 0:
        return f"{Fore.GREEN}GÜVENLİ:{Style.RESET_ALL} Uzay havası durağan. LEO, MEO ve GEO uydu operasyonları sorunsuz çalışabilir. Herhangi bir manyetik fırtına (Geomagnetic Storm) tespit edilmedi."
    elif risk_seviyesi == 1:
        return f"{Fore.YELLOW}UYARI (Minör Fırtına):{Style.RESET_ALL} LEO yörüngesindeki uydularda erken yalpalanma veya atmosferik sürüklenme (drag) artışı beklenebilir. G1-G2 seviye manyetik hareket tespit edildi."
    elif risk_seviyesi == 2:
        return f"{Fore.MAGENTA}TEHLİKE (Orta Şiddet):{Style.RESET_ALL} MEO yörüngesinde bulunan GPS ve Galileo uydularında sinyal/navigasyon kesintileri ve yüzeysel şarj (Surface Charging) riski mevcuttur. M-Class güneş patlaması / G3 fırtına olasılığı."
    elif risk_seviyesi == 3:
        return f"{Fore.RED}KRİTİK (Şiddetli Fırtına):{Style.RESET_ALL} X-Class Solar Flare veya G4/G5 fırtına! GEO ve MEO uydularında tam haberleşme kopuşu, kalıcı hasar veya astronotlar için tehlikeli radyasyon dozajı riski. Uydularınızı hemen Güvenli Mod'a alın."
    else:
        return f"{Fore.CYAN}Bilinmeyen Risk Seviyesi.{Style.RESET_ALL}"

def asistan_uydular(risk_seviyesi):
    if risk_seviyesi == 0:
        return "-"
    elif risk_seviyesi == 1:
        return "ISS, Starlink, Hubble, KüpUydular (LEO)"
    elif risk_seviyesi == 2:
        return "ISS, Starlink, GPS Uyduları, Galileo (LEO, MEO)"
    elif risk_seviyesi == 3:
        return "Tüm Yörüngeler: Türksat, GPS, Starlink, ISS, James Webb, Deep Space (LEO, MEO, GEO)"

def yuzdesel_olasilik_getir(olasilik_listesi):
    fmt = []
    for i, p in enumerate(olasilik_listesi):
        fmt.append(f"Seviye {i}: %{p*100:.2f}")
    return " | ".join(fmt)

def canli_tahmin_yap(model):
    print(f"\n{Fore.CYAN}[*] NOAA SWPC Canlı Verileri İzleniyor... (Gerçek Zamanlı API){Style.RESET_ALL}")
    time.sleep(1)
    
    veri = gercek_noaa_verisi_cek()
    if veri is None:
        print(f"{Fore.RED}[!] Veri anlık olarak okunamadı.{Style.RESET_ALL}")
        return

    print("\n   [CANLI UZAY HAVASI DEĞERLERİ]")
    print(f"   X-Ray Flux:           {veri['xray_flux']:.2e} Watts/m2")
    print(f"   Solar Rüzgar Hızı:    {veri['solar_wind_speed']} km/s")
    print(f"   Solar Plazma Yoğun.:  {veri['solar_wind_density']} p/cc")
    print(f"   Manyetik Yönelim (Bz):{veri['bz_gsm']} nT")
    print(f"   Kp İndeksi:           {veri['kp_index']}/9.0")
    
    df = pd.DataFrame([veri])
    df_islenmis = ozellik_muhendisligi(df)
    
    #tahmin
    try:
        tahmin_sinifi, tahmin_olasiligi = model.tahmin_et(df_islenmis)
        risk = int(tahmin_sinifi[0])
        olasiliklar = tahmin_olasiligi[0]
        
        print("\n" + "=" * 60)
        print(f"   ERKEN UYARI TAHMİN RAPORU")
        print("=" * 60)
        print(f"   Yapay Zeka Olasılık Dağılımı: {yuzdesel_olasilik_getir(olasiliklar)}")
        print(f"   Hesaplanan Risk Seviyesi: [{risk}/3]")
        print("\n   [YAPAY ZEKA ASİSTANI YORUMU]")
        print("   " + asistan_mesaji(risk))
        print("\n   [BİRİNCİL ETKİLENECEK YÖRÜNGELER / UYDULAR]")
        print("   " + asistan_uydular(risk))
        print("=" * 60)
        
    except Exception as e:
        print(f"{Fore.RED}[!] Tahmin motoru hata verdi: {e}{Style.RESET_ALL}")

def manuel_tahmin_yap(model):
    print(f"\n{Fore.CYAN}[*] Manuel Uzay Havasi Degerleri Girisi (Tehlike Similasyonu) {Style.RESET_ALL}")
    
    try:
        xray_flux = float(input("   X-Ray Radyasyon Akısı (Örn: 1e-4 veya 0.0001): "))
        speed = float(input("   Solar Rüzgar Hızı (km/s) (Örn: 400.0, 900.0): "))
        density = float(input("   Solar Rüzgar Yoğunluğu (p/cc) (Örn: 5.0, 40.0): "))
        bz = float(input("   Gezegenler Arası Manyetik Alan Bz (nT) (Örn: -15.0, 5.0): "))
        bt = float(input("   Toplam Manyetik Alan Bt (nT) (Örn: 5.0, 25.0): "))
        kp = float(input("   Geomanyetik Kp İndeksi (0 - 9) (Örn: 2, 8): "))
        
        veri = {
            "xray_flux": xray_flux,
            "solar_wind_speed": speed,
            "solar_wind_density": density,
            "bz_gsm": bz,
            "bt_total": bt,
            "kp_index": kp,
            "solar_wind_temp": 150000.0,
            "energetic_protons": 0.5
        }
        
        df = pd.DataFrame([veri])
        df_islenmis = ozellik_muhendisligi(df)
        
        tahmin_sinifi, tahmin_olasiligi = model.tahmin_et(df_islenmis)
        risk = int(tahmin_sinifi[0])
        olasiliklar = tahmin_olasiligi[0]
        
        print("\n" + "=" * 60)
        print(f"   ERKEN UYARI TAHMİN RAPORU (SİMULASYON)")
        print("=" * 60)
        print(f"   Yapay Zeka Olasılık Dağılımı: {yuzdesel_olasilik_getir(olasiliklar)}")
        print(f"   Hesaplanan Risk Seviyesi: [{risk}/3]")
        print("\n   [YAPAY ZEKA ASİSTANI YORUMU]")
        print("   " + asistan_mesaji(risk))
        print("\n   [BİRİNCİL ETKİLENECEK YÖRÜNGELER / UYDULAR]")
        print("   " + asistan_uydular(risk))
        print("=" * 60)
        
    except ValueError:
        print(f"{Fore.RED}[!] Lutfen gecerli bir sayisal veri girin.{Style.RESET_ALL}")

def main():
    ekran_temizle()
    try:
        print(f"{Fore.YELLOW}[*] Uzay Havasi (Space Weather) Erken Uyarı Modeli yükleniyor...{Style.RESET_ALL}")
        model = UzayYoluTahminModeli.yukle()
    except Exception as e:
        print(f"{Fore.RED}[!] Model yüklenemedi. Lütfen önce modeli eğitin: `python train.py`\nHata: {e}{Style.RESET_ALL}")
        sys.exit(1)

    while True:
        print(f"{Fore.BLUE}\n" + "=" * 60)
        print("  NOAA SWPC SOLAR STORM ERKEN UYARI YAPAY ZEKASI")
        print("=" * 60 + Style.RESET_ALL)
        print("  [1] Canlı Veri ile Taran (Gerçek Zamanlı Olarak Risk Belirle)")
        print("  [2] Manuel Veri Girerek Risk Simüle Et")
        print("  [0] Çıkış\n")
        
        secim = input("  Seçiminiz: ").strip()
        
        if secim == "1":
            canli_tahmin_yap(model)
        elif secim == "2":
            manuel_tahmin_yap(model)
        elif secim == "0":
            print("  Çıkış yapılıyor...")
            break
        else:
            print(f"  {Fore.RED}Gerçersiz seçim!{Style.RESET_ALL}")
            
if __name__ == "__main__":
    main()
