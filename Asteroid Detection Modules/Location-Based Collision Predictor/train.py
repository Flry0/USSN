import os
import sys
import time
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import config
from veri_toplama import toplu_veri_topla, yorunge_verileri_zenginlestir
from veri_isleme import tam_veri_isleme_hatti, ham_veri_yukle
from model import CarpismaTahminModeli, CokluModelToplulugu


def veri_topla_ve_isle(gun_sayisi=None, yorunge_zenginlestir=False):
    if gun_sayisi is None:
        gun_sayisi = config.VARSAYILAN_GUN_ARALIGI

    print("=" * 60)
    print("  ASTEROID CARPMA TAHMINI - VERI TOPLAMA")
    print("=" * 60)

    ham_veri = toplu_veri_topla(gun_sayisi=gun_sayisi)

    if yorunge_zenginlestir and ham_veri.get("neows_asteroidler"):
        print("\n[*] Yorunge verileri zenginlestiriliyor...")
        ham_veri["neows_asteroidler"] = yorunge_verileri_zenginlestir(
            ham_veri["neows_asteroidler"]
        )

    print("\n" + "=" * 60)
    print("  VERI ISLEME")
    print("=" * 60)

    df = tam_veri_isleme_hatti(ham_veri=ham_veri, sentetik_uret=True)
    return df


def tek_model_egit(df, model_tipi="gradient_boosting"):
    print(f"\n[*] {model_tipi.upper()} modeli egitiliyor...")

    tahmin_modeli = CarpismaTahminModeli(model_tipi=model_tipi)
    X = tahmin_modeli.ozellikleri_hazirla(df)
    y = df[config.HEDEF_SUTUN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=config.TEST_ORANI,
        random_state=config.RANDOM_STATE,
    )

    print(f"    Egitim seti: {len(X_train)} kayit")
    print(f"    Test seti: {len(X_test)} kayit")

    egitim_sonuclari = tahmin_modeli.egit(X_train, y_train)
    print(f"\n    [Egitim Sonuclari]")
    print(f"    MSE:  {egitim_sonuclari['egitim_mse']:.6f}")
    print(f"    RMSE: {egitim_sonuclari['egitim_rmse']:.6f}")
    print(f"    R2:   {egitim_sonuclari['egitim_r2']:.6f}")

    print(f"\n[*] Capraz dogrulama yapiliyor...")
    cv_sonuclari = tahmin_modeli.capraz_dogrula(X_train, y_train)
    print(f"    Ortalama RMSE: {cv_sonuclari['ortalama_rmse']:.6f}")
    print(f"    Std MSE:       {cv_sonuclari['std_mse']:.6f}")

    print(f"\n[*] Test seti degerlendirmesi...")
    test_raporu = tahmin_modeli.degerlendirme_raporu(X_test, y_test)
    print(f"    MSE:           {test_raporu['mse']:.10f}")
    print(f"    RMSE:          {test_raporu['rmse']:.10f}")
    print(f"    MAE:           {test_raporu['mae']:.10f}")
    print(f"    R2 (log):      {test_raporu['r2_log_scale']:.6f}")
    print(f"    Ort. Tahmin:   {test_raporu['ortalama_tahmin']:.2e}")
    print(f"    Max Tahmin:    {test_raporu['max_tahmin']:.2e}")

    onem_df = tahmin_modeli.onem_siralamasini_al()
    if onem_df is not None:
        print(f"\n    [Ozellik Onemleri - Top 10]")
        for _, satir in onem_df.head(10).iterrows():
            bar = "█" * int(satir["onem_degeri"] * 50)
            print(f"    {satir['ozellik']:30s} {satir['onem_degeri']:.4f} {bar}")

    return tahmin_modeli, test_raporu


def topluluk_modeli_egit(df):
    print("\n" + "=" * 60)
    print("  TOPLULUK MODELI EGITIMI")
    print("=" * 60)

    topluluk = CokluModelToplulugu()

    gb_model, gb_rapor = tek_model_egit(df, "gradient_boosting")
    rf_model, rf_rapor = tek_model_egit(df, "random_forest")

    gb_agirlik = max(0.1, gb_rapor.get("r2_log_scale", 0.5))
    rf_agirlik = max(0.1, rf_rapor.get("r2_log_scale", 0.5))

    topluluk.model_ekle("gradient_boosting", gb_model, agirlik=gb_agirlik)
    topluluk.model_ekle("random_forest", rf_model, agirlik=rf_agirlik)

    return topluluk


def modeli_kaydet(model, topluluk_mu=False):
    if topluluk_mu:
        kayit_yolu = model.kaydet()
        print(f"\n[+] Topluluk modeli kaydedildi: {kayit_yolu}")
    else:
        kayit_yolu = model.kaydet()
        print(f"\n[+] Model kaydedildi: {kayit_yolu}")

    return kayit_yolu


def egitim_ozetini_yazdir(baslangic_zamani):
    gecen_sure = time.time() - baslangic_zamani
    dakika = int(gecen_sure // 60)
    saniye = int(gecen_sure % 60)
    print(f"\n{'=' * 60}")
    print(f"  EGITIM TAMAMLANDI")
    print(f"  Gecen sure: {dakika} dakika {saniye} saniye")
    print(f"{'=' * 60}")


def main():
    baslangic_zamani = time.time()

    print("\n" + "=" * 60)
    print("  ASTEROID CARPMA OLASILIGI TAHMIN SISTEMI")
    print("  Egitim Modulu")
    print("=" * 60)

    gun_sayisi = config.VARSAYILAN_GUN_ARALIGI
    yorunge_verisi = False
    topluluk = False
    model_tipi = "gradient_boosting"

    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "--gun" and i + 1 < len(args):
            gun_sayisi = int(args[i + 1])
        elif arg == "--yorunge":
            yorunge_verisi = True
        elif arg == "--topluluk":
            topluluk = True
        elif arg == "--model" and i + 1 < len(args):
            model_tipi = args[i + 1]

    islenmis_veri_yolu = os.path.join(config.VERI_KLASORU, "islenmis_veri.csv")
    if os.path.exists(islenmis_veri_yolu):
        print(f"\n[?] Mevcut islenmis veri bulundu: {islenmis_veri_yolu}")
        print("[?] Mevcut veriyi kullanmak icin 'e', yeni veri toplamak icin 'h' girin: ", end="")
        secim = input().strip().lower()
        if secim == "e":
            print("[*] Mevcut veri yukleniyor...")
            df = pd.read_csv(islenmis_veri_yolu)
        else:
            df = veri_topla_ve_isle(gun_sayisi=gun_sayisi, yorunge_zenginlestir=yorunge_verisi)
    else:
        df = veri_topla_ve_isle(gun_sayisi=gun_sayisi, yorunge_zenginlestir=yorunge_verisi)

    if df is None or df.empty:
        print("[!] Veri toplama basarisiz. Cikiliyor...")
        sys.exit(1)

    print(f"\n[*] Egitim verisi hazir: {len(df)} kayit, {len(df.columns)} ozellik")

    if topluluk:
        model = topluluk_modeli_egit(df)
        modeli_kaydet(model, topluluk_mu=True)
    else:
        model, rapor = tek_model_egit(df, model_tipi)
        modeli_kaydet(model)

    egitim_ozetini_yazdir(baslangic_zamani)


if __name__ == "__main__":
    main()
