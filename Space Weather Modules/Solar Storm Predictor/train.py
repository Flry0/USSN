import os
import sys
import time
import pandas as pd
from sklearn.model_selection import train_test_split
import config
from veri_toplama import toplu_veri_topla
from veri_isleme import tam_veri_isleme_hatti
from model import UzayYoluTahminModeli


def veri_hazirla_ve_kaydet():
    print("=" * 60)
    print("  UZAY HAVASI ERKEN UYARI SISTEMI - VERI TOPLAMA")
    print("=" * 60)

    ham_veri = toplu_veri_topla()

    print("\n" + "=" * 60)
    print("  VERI ISLEME")
    print("=" * 60)

    df = tam_veri_isleme_hatti(ham_veri=ham_veri)
    return df


def modeli_egit_ve_test_et(df, model_tipi="random_forest"):
    print(f"\n[*] {model_tipi.upper()} modeli egitiliyor...")

    tahmin_modeli = UzayYoluTahminModeli(model_tipi=model_tipi)
    X = tahmin_modeli.ozellikleri_hazirla(df)
    y = df[config.HEDEF_SUTUN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=config.TEST_ORANI,
        random_state=config.RANDOM_STATE,
    )

    print(f"    Egitim seti: {len(X_train)} ornek")
    print(f"    Test seti: {len(X_test)} ornek")

    egitim_sonuclari = tahmin_modeli.egit(X_train, y_train)
    print(f"\n    [Egitim Sonuclari]")
    print(f"    Dogruluk (Training Accuracy): {egitim_sonuclari['egitim_dogruluk']:.4f}")

    print(f"\n[*] Capraz dogrulama yapiliyor...")
    cv_sonuclari = tahmin_modeli.capraz_dogrula(X_train, y_train)
    print(f"    Ortalama CV Dogrulugu: {cv_sonuclari['ortalama_dogruluk']:.4f}")
    print(f"    CV Standart Sapmasi:   {cv_sonuclari['std_dogruluk']:.4f}")

    print(f"\n[*] Test seti degerlendirmesi...")
    test_raporu = tahmin_modeli.degerlendirme_raporu(X_test, y_test)
    print(f"    Test Dogrulugu: {test_raporu['dogruluk']:.4f}")
    print("\n    [Siniflandirma Raporu]")
    print(test_raporu['rapor_metin'])

    return tahmin_modeli

def modeli_kaydet(model):
    kayit_yolu = model.kaydet()
    print(f"\n[+] Model kaydedildi: {kayit_yolu}")
    return kayit_yolu

def main():
    baslangic_zamani = time.time()

    print("\n" + "=" * 60)
    print("  UZAY HAVASI (SOLAR STORM) RISK TAHMIN SISTEMI")
    print("  Egitim Modulu")
    print("=" * 60)

    islenmis_veri_yolu = os.path.join(config.VERI_KLASORU, "islenmis_veri.csv")
    if os.path.exists(islenmis_veri_yolu):
        print(f"\n[?] Mevcut islenmis veri bulundu: {islenmis_veri_yolu}")
        print("[?] Mevcut veriyi kullanmak icin 'e', yenisini uretmek icin 'h' girinebasin: ", end="")
        secim = input().strip().lower()
        if secim == "e":
            print("[*] Mevcut veri yukleniyor...")
            df = pd.read_csv(islenmis_veri_yolu)
        else:
            df = veri_hazirla_ve_kaydet()
    else:
        df = veri_hazirla_ve_kaydet()

    if df is None or df.empty:
        print("[!] Veri toplama basarisiz. Cikiliyor...")
        sys.exit(1)

    print(f"\n[*] Egitim verisi hazir: {len(df)} kayit, {len(df.columns)} ozellik")

    model = modeli_egit_ve_test_et(df, model_tipi="random_forest")
    modeli_kaydet(model)

    gecen_sure = time.time() - baslangic_zamani
    print(f"\n[+] Egitim {int(gecen_sure)} saniyede tamamlandi.")


if __name__ == "__main__":
    main()
