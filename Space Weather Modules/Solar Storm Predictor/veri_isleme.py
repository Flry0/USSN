import pandas as pd
import numpy as np
import json
import os
import config

def ham_veri_yukle(dosya_yolu=None):
    if dosya_yolu is None:
        dosya_yolu = os.path.join(config.VERI_KLASORU, "ham_veri.json")

    with open(dosya_yolu, "r", encoding="utf-8") as f:
        return json.load(f)

def dataframe_olustur(uzay_havasi_listesi):
    if not uzay_havasi_listesi:
        return pd.DataFrame()
    return pd.DataFrame(uzay_havasi_listesi)

def ozellik_muhendisligi(df):
    if df.empty:
        return df

    df = df.copy()

    df["log_xray_flux"] = np.log10(np.clip(df["xray_flux"], 1e-10, 1e-2))
    df["dynamic_pressure_npa"] = (1.6726e-6) * df["solar_wind_density"] * (df["solar_wind_speed"] ** 2)

    # v * Bs
    bs = np.where(df["bz_gsm"] < 0, np.abs(df["bz_gsm"]), 0)
    df["reconnection_rate"] = df["solar_wind_speed"] * bs

    # A < 1e-7, B >= 1e-7, C >= 1e-6, M >= 1e-5, X >= 1e-4
    conditions = [
        (df["xray_flux"] >= 1e-4),
        (df["xray_flux"] >= 1e-5) & (df["xray_flux"] < 1e-4),
        (df["xray_flux"] >= 1e-6) & (df["xray_flux"] < 1e-5),
        (df["xray_flux"] >= 1e-7) & (df["xray_flux"] < 1e-6),
        (df["xray_flux"] < 1e-7)
    ]
    choices = [4, 3, 2, 1, 0] # X, M, C, B, A
    df["flare_class_code"] = np.select(conditions, choices, default=0)

    sayisal_sutunlar = ["solar_wind_speed", "solar_wind_density", "kp_index", "energetic_protons"]
    for sutun in sayisal_sutunlar:
        max_val = df[sutun].max() if df[sutun].max() > 0 else 1
        df[f"{sutun}_norm"] = df[sutun] / max_val

    return df

def eksik_verileri_doldur(df):
    if df.empty:
        return df

    df = df.copy()
    sayisal_sutunlar = df.select_dtypes(include=[np.number]).columns
    for sutun in sayisal_sutunlar:
        if df[sutun].isnull().any():
            medyan = df[sutun].median()
            df[sutun] = df[sutun].fillna(medyan)
    return df

def tam_veri_isleme_hatti(ham_veri=None):
    if ham_veri is None:
        ham_veri = ham_veri_yukle()

    print("[*] DataFrame olusturuluyor...")
    df = dataframe_olustur(ham_veri.get("uzay_havasi", []))
    print(f"    -> {len(df)} kayit (Solar Storm Samples)")

    if df.empty:
        print("[!] Veri bos, isleme durduruluyor")
        return df

    print("[*] Uzay havasi fiziksel arayuzu hesabi uygulaniyor...")
    df = ozellik_muhendisligi(df)

    print("[*] Eksik veriler dolduruluyor...")
    df = eksik_verileri_doldur(df)

    os.makedirs(config.VERI_KLASORU, exist_ok=True)
    kayit_yolu = os.path.join(config.VERI_KLASORU, "islenmis_veri.csv")
    df.to_csv(kayit_yolu, index=False)
    print(f"[+] Islenmis uzay hava durumu verisi kaydedildi: {kayit_yolu}")
    print(f"[+] Toplam kayit sayisi: {len(df)}")
    return df
