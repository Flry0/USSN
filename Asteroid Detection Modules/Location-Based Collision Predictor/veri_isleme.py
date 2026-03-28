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


def neows_dataframe_olustur(asteroid_listesi):
    if not asteroid_listesi:
        return pd.DataFrame()
    return pd.DataFrame(asteroid_listesi)


def sentry_dataframe_olustur(tehdit_listesi):
    if not tehdit_listesi:
        return pd.DataFrame()
    return pd.DataFrame(tehdit_listesi)


def birlestir_ve_eslestir(neows_df, sentry_df):
    if neows_df.empty and sentry_df.empty:
        return pd.DataFrame()

    if sentry_df.empty:
        neows_df["impact_probability"] = 0.0
        neows_df["palermo_scale"] = -10.0
        neows_df["torino_scale"] = 0
        return neows_df

    if neows_df.empty:
        return sentry_df

    sentry_eslestirme = sentry_df[["asteroid_id", "impact_probability", "palermo_scale", "torino_scale"]].copy()
    sentry_eslestirme = sentry_eslestirme.rename(columns={"asteroid_id": "asteroid_adi_sentry"})

    merged = neows_df.copy()
    merged["impact_probability"] = 0.0
    merged["palermo_scale"] = -10.0
    merged["torino_scale"] = 0

    sentry_isimleri = set(sentry_df["asteroid_adi"].str.strip().str.lower())
    sentry_dict = {}
    for _, row in sentry_df.iterrows():
        temiz_isim = row["asteroid_adi"].strip().lower()
        sentry_dict[temiz_isim] = {
            "impact_probability": row["impact_probability"],
            "palermo_scale": row["palermo_scale"],
            "torino_scale": row["torino_scale"],
        }

    for idx, row in merged.iterrows():
        neo_isim = row["asteroid_adi"].strip().lower()
        for sentry_isim, degerler in sentry_dict.items():
            if sentry_isim in neo_isim or neo_isim in sentry_isim:
                merged.at[idx, "impact_probability"] = degerler["impact_probability"]
                merged.at[idx, "palermo_scale"] = degerler["palermo_scale"]
                merged.at[idx, "torino_scale"] = degerler["torino_scale"]
                break

    return merged


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

    df["energy_estimate"] = 0.5 * (ortalama_cap ** 3) * (np.pi / 6) * 3000 * (df["relative_velocity_km_s"] * 1000) ** 2
    df["energy_estimate"] = df["energy_estimate"] / 4.184e15

    df["momentum_estimate"] = (ortalama_cap ** 3) * (np.pi / 6) * 3000 * df["relative_velocity_km_s"]

    hiz_norm = df["relative_velocity_km_s"] / df["relative_velocity_km_s"].max() if df["relative_velocity_km_s"].max() > 0 else 0
    cap_norm = ortalama_cap / ortalama_cap.max() if ortalama_cap.max() > 0 else 0
    mesafe_norm = 1 - (df["miss_distance_au"] / df["miss_distance_au"].max()) if df["miss_distance_au"].max() > 0 else 0
    df["hazard_score"] = (hiz_norm * 0.3 + cap_norm * 0.3 + mesafe_norm * 0.3 + df["is_hazardous"] * 0.1)

    df["distance_diameter_ratio"] = np.where(
        ortalama_cap > 0,
        df["miss_distance_km"] / ortalama_cap,
        0
    )

    df["velocity_distance_ratio"] = np.where(
        df["miss_distance_au"] > 0,
        df["relative_velocity_km_s"] / df["miss_distance_au"],
        0
    )

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


def hedef_degisken_olustur(df):
    if df.empty:
        return df

    df = df.copy()

    if "impact_probability" not in df.columns:
        df["impact_probability"] = 0.0

    return df


def sentetik_tehdit_verisi_uret(mevcut_df, tehdit_sayisi=500):
    if mevcut_df.empty:
        return mevcut_df

    tehlikeli = mevcut_df[mevcut_df["is_hazardous"] == 1]
    if tehlikeli.empty:
        tehlikeli = mevcut_df

    sentetik_kayitlar = []
    for _ in range(tehdit_sayisi):
        rastgele_idx = np.random.choice(tehlikeli.index)
        base_record = tehlikeli.loc[rastgele_idx].copy()

        base_record["miss_distance_au"] *= np.random.uniform(0.001, 0.1)
        base_record["miss_distance_km"] *= np.random.uniform(0.001, 0.1)
        base_record["miss_distance_lunar"] *= np.random.uniform(0.001, 0.1)
        base_record["relative_velocity_km_s"] *= np.random.uniform(0.8, 2.0)
        base_record["estimated_diameter_min_km"] *= np.random.uniform(1.0, 5.0)
        base_record["estimated_diameter_max_km"] *= np.random.uniform(1.0, 5.0)
        base_record["is_hazardous"] = 1

        mesafe_faktor = max(0.001, base_record["miss_distance_au"])
        cap_faktor = (base_record["estimated_diameter_min_km"] + base_record["estimated_diameter_max_km"]) / 2
        hiz_faktor = base_record["relative_velocity_km_s"]

        base_olasilik = (1 / (mesafe_faktor * 1000)) * (cap_faktor * 10) * (hiz_faktor / 30)
        base_record["impact_probability"] = min(max(base_olasilik * np.random.uniform(0.5, 2.0), 1e-10), 0.1)

        sentetik_kayitlar.append(base_record)

    sentetik_df = pd.DataFrame(sentetik_kayitlar)
    birlesik = pd.concat([mevcut_df, sentetik_df], ignore_index=True)

    return birlesik


def tam_veri_isleme_hatti(ham_veri=None, sentetik_uret=True):
    if ham_veri is None:
        ham_veri = ham_veri_yukle()

    print("[*] NeoWs DataFrame olusturuluyor...")
    neows_df = neows_dataframe_olustur(ham_veri.get("neows_asteroidler", []))
    print(f"    -> {len(neows_df)} kayit")

    print("[*] Sentry DataFrame olusturuluyor...")
    sentry_df = sentry_dataframe_olustur(ham_veri.get("sentry_tehditler", []))
    print(f"    -> {len(sentry_df)} kayit")

    print("[*] Veriler birlestiriliyor...")
    df = birlestir_ve_eslestir(neows_df, sentry_df)
    print(f"    -> {len(df)} kayit birlestirildi")

    if df.empty:
        print("[!] Birlestirme sonrasi veri bos, isleme durduruluyor")
        return df

    for sutun in ["orbit_eccentricity", "orbit_semi_major_axis", "orbit_inclination", "orbit_period"]:
        if sutun not in df.columns:
            df[sutun] = 0.0

    print("[*] Hedef degisken olusturuluyor...")
    df = hedef_degisken_olustur(df)

    if sentetik_uret:
        print("[*] Sentetik tehdit verisi uretiliyor...")
        onceki_boyut = len(df)
        df = sentetik_tehdit_verisi_uret(df)
        print(f"    -> {len(df) - onceki_boyut} sentetik kayit eklendi")

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
