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


def dataframe_olustur(uzay_copu_listesi):
    if not uzay_copu_listesi:
        return pd.DataFrame()
    return pd.DataFrame(uzay_copu_listesi)


def ozellik_muhendisligi(df):
    if df.empty:
        return df

    df = df.copy()

    ortalama_cap = (df["estimated_diameter_min_km"] + df["estimated_diameter_max_km"]) / 2
    df["diameter_velocity_ratio"] = np.where(
        df["relative_velocity_km_s"] > 0,
        ortalama_cap / df["relative_velocity_km_s"],
        0
    )

    # Kinetik enerji tahmini: m * v^2 / 2 (basitce)
    df["energy_estimate"] = 0.5 * (ortalama_cap ** 3) * (np.pi / 6) * 3000 * (df["relative_velocity_km_s"]) ** 2

    # Tehlike puani
    hiz_norm = df["relative_velocity_km_s"] / (df["relative_velocity_km_s"].max() + 1e-9)
    cap_norm = ortalama_cap / (ortalama_cap.max() + 1e-9)
    mesafe_norm = 1 - (df["miss_distance_km"] / (df["miss_distance_km"].max() + 1e-9))
    df["hazard_score"] = (hiz_norm * 0.3 + cap_norm * 0.3 + mesafe_norm * 0.3 + df["is_hazardous"] * 0.1)

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


def asiri_degerleri_kirp(df, sutunlar=None, alt_yuzde=0.01, ust_yuzde=0.99):
    if df.empty:
        return df

    df = df.copy()
    if sutunlar is None:
        sutunlar = df.select_dtypes(include=[np.number]).columns

    for sutun in sutunlar:
        if sutun in df.columns:
            alt_sinir = df[sutun].quantile(alt_yuzde)
            ust_sinir = df[sutun].quantile(ust_yuzde)
            df[sutun] = df[sutun].clip(alt_sinir, ust_sinir)

    return df


def tam_veri_isleme_hatti(ham_veri=None, sentetik_uret=False):
    if ham_veri is None:
        ham_veri = ham_veri_yukle()

    print("[*] DataFrame olusturuluyor...")
    df = dataframe_olustur(ham_veri.get("uzay_copuler", []))
    print(f"    -> {len(df)} kayit")

    if df.empty:
        print("[!] Veri bos, isleme durduruluyor")
        return df

    print("[*] Ozellik muhendisligi uygulaniyor...")
    df = ozellik_muhendisligi(df)

    print("[*] Eksik veriler dolduruluyor...")
    df = eksik_verileri_doldur(df)

    print("[*] Asiri degerler kirpiliyor...")
    df = asiri_degerleri_kirp(df)

    os.makedirs(config.VERI_KLASORU, exist_ok=True)
    kayit_yolu = os.path.join(config.VERI_KLASORU, "islenmis_veri.csv")
    df.to_csv(kayit_yolu, index=False)
    print(f"[+] Islenmis veri kaydedildi: {kayit_yolu}")
    print(f"[+] Toplam kayit sayisi: {len(df)}")
    print(f"[+] Ozellik sayisi: {len(df.columns)}")

    return df
