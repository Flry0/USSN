import os
import sys
import cv2
import random
import shutil
import argparse
import numpy as np
from tqdm import tqdm

from yapilandirma import (
    VERI_SETI_YOLU, EGITIM_YOLU, DOGRULAMA_YOLU, TEST_YOLU,
    GORUNTU_YOLU, ETIKET_YOLU, GORUNTU_BOYUTU
)


def argumanlari_al():
    cozumleyici = argparse.ArgumentParser()
    cozumleyici.add_argument('--kaynak', type=str, required=True,
                             help='Kaynak goruntu klasoru')
    cozumleyici.add_argument('--etiketler', type=str, default=None,
                             help='Etiket dosyalari klasoru (YOLO formati)')
    cozumleyici.add_argument('--egitim-orani', type=float, default=0.7)
    cozumleyici.add_argument('--dogrulama-orani', type=float, default=0.15)
    cozumleyici.add_argument('--test-orani', type=float, default=0.15)
    cozumleyici.add_argument('--tohum', type=int, default=42)
    cozumleyici.add_argument('--sentetik', action='store_true',
                             help='Sentetik asteroid verisi olustur')
    cozumleyici.add_argument('--sentetik-sayi', type=int, default=200,
                             help='Olusturulacak sentetik goruntu sayisi')
    return cozumleyici.parse_args()


def klasor_yapisini_olustur():
    for ana_klasor in [EGITIM_YOLU, DOGRULAMA_YOLU, TEST_YOLU]:
        os.makedirs(os.path.join(ana_klasor, GORUNTU_YOLU), exist_ok=True)
        os.makedirs(os.path.join(ana_klasor, ETIKET_YOLU), exist_ok=True)


def veriyi_bol(kaynak_klasor, etiket_klasor, egitim_orani, dogrulama_orani, test_orani, tohum):
    random.seed(tohum)
    np.random.seed(tohum)

    desteklenen = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif')
    tum_dosyalar = sorted([
        d for d in os.listdir(kaynak_klasor)
        if d.lower().endswith(desteklenen)
    ])

    if len(tum_dosyalar) == 0:
        print(f"HATA: {kaynak_klasor} klasorunde goruntu bulunamadi!")
        return

    random.shuffle(tum_dosyalar)
    toplam = len(tum_dosyalar)
    egitim_sinir = int(toplam * egitim_orani)
    dogrulama_sinir = egitim_sinir + int(toplam * dogrulama_orani)

    bolumler = {
        'egitim': (tum_dosyalar[:egitim_sinir], EGITIM_YOLU),
        'dogrulama': (tum_dosyalar[egitim_sinir:dogrulama_sinir], DOGRULAMA_YOLU),
        'test': (tum_dosyalar[dogrulama_sinir:], TEST_YOLU)
    }

    for bolum_adi, (dosyalar, hedef_yolu) in bolumler.items():
        goruntu_hedef = os.path.join(hedef_yolu, GORUNTU_YOLU)
        etiket_hedef = os.path.join(hedef_yolu, ETIKET_YOLU)

        for dosya in tqdm(dosyalar, desc=f"{bolum_adi} kopyalaniyor"):
            kaynak_yol = os.path.join(kaynak_klasor, dosya)
            shutil.copy2(kaynak_yol, os.path.join(goruntu_hedef, dosya))

            if etiket_klasor:
                etiket_adi = os.path.splitext(dosya)[0] + '.txt'
                etiket_yol = os.path.join(etiket_klasor, etiket_adi)
                if os.path.exists(etiket_yol):
                    shutil.copy2(etiket_yol, os.path.join(etiket_hedef, etiket_adi))

        print(f"  {bolum_adi}: {len(dosyalar)} goruntu")


def yildiz_alani_olustur(genislik, yukseklik):
    arkaplan = np.zeros((yukseklik, genislik, 3), dtype=np.uint8)
    arkaplan[:] = np.random.randint(3, 12, size=3)

    yildiz_sayisi = np.random.randint(50, 200)
    for _ in range(yildiz_sayisi):
        x = np.random.randint(0, genislik)
        y = np.random.randint(0, yukseklik)
        parlaklik = np.random.randint(100, 255)
        boyut = np.random.choice([1, 1, 1, 2, 2, 3])
        renk = (parlaklik, parlaklik, int(parlaklik * np.random.uniform(0.8, 1.0)))
        cv2.circle(arkaplan, (x, y), boyut, renk, -1)
        if boyut >= 2:
            cv2.GaussianBlur(
                arkaplan[max(0, y-5):y+5, max(0, x-5):x+5],
                (3, 3), 0.5,
                dst=arkaplan[max(0, y-5):y+5, max(0, x-5):x+5]
            )

    bulutsu_sayisi = np.random.randint(0, 3)
    for _ in range(bulutsu_sayisi):
        bx = np.random.randint(0, genislik)
        by = np.random.randint(0, yukseklik)
        br = np.random.randint(30, 100)
        renk = tuple(np.random.randint(5, 30, size=3).tolist())
        gecici = np.zeros_like(arkaplan)
        cv2.circle(gecici, (bx, by), br, renk, -1)
        gecici = cv2.GaussianBlur(gecici, (br * 2 + 1, br * 2 + 1), br // 2)
        arkaplan = cv2.add(arkaplan, gecici)

    return arkaplan


def asteroid_ekle(goruntu, kutu_listesi):
    yukseklik, genislik = goruntu.shape[:2]
    asteroid_sayisi = np.random.randint(1, 4)

    for _ in range(asteroid_sayisi):
        boyut = np.random.randint(5, 30)
        x = np.random.randint(boyut + 5, genislik - boyut - 5)
        y = np.random.randint(boyut + 5, yukseklik - boyut - 5)

        parlaklik = np.random.randint(120, 255)
        tur = np.random.choice(['yuvarlak', 'cizgi', 'nokta'])

        if tur == 'yuvarlak':
            renk = (parlaklik, int(parlaklik * 0.9), int(parlaklik * 0.85))
            cv2.circle(goruntu, (x, y), boyut // 2, renk, -1)
            cv2.GaussianBlur(
                goruntu[max(0, y - boyut):y + boyut, max(0, x - boyut):x + boyut],
                (5, 5), 1.5,
                dst=goruntu[max(0, y - boyut):y + boyut, max(0, x - boyut):x + boyut]
            )
        elif tur == 'cizgi':
            aci = np.random.uniform(0, np.pi)
            dx = int(np.cos(aci) * boyut)
            dy = int(np.sin(aci) * boyut)
            renk = (parlaklik, parlaklik, int(parlaklik * 0.9))
            cv2.line(goruntu, (x - dx, y - dy), (x + dx, y + dy), renk, max(1, boyut // 8))
            bolgesi = goruntu[max(0, y - boyut):y + boyut, max(0, x - boyut):x + boyut]
            if bolgesi.size > 0:
                cv2.GaussianBlur(bolgesi, (3, 3), 0.8, dst=bolgesi)
        else:
            renk = (parlaklik, parlaklik, parlaklik)
            cv2.circle(goruntu, (x, y), max(2, boyut // 4), renk, -1)

        kutu_g = boyut * 2.5 / genislik
        kutu_y = boyut * 2.5 / yukseklik
        kutu_x = x / genislik
        kutu_yy = y / yukseklik
        kutu_g = min(kutu_g, 1.0)
        kutu_y = min(kutu_y, 1.0)
        kutu_listesi.append((0, kutu_x, kutu_yy, kutu_g, kutu_y))

    return goruntu, kutu_listesi


def sentetik_veri_olustur(sayi, hedef_yolu):
    goruntu_klasoru = os.path.join(hedef_yolu, GORUNTU_YOLU)
    etiket_klasoru = os.path.join(hedef_yolu, ETIKET_YOLU)
    os.makedirs(goruntu_klasoru, exist_ok=True)
    os.makedirs(etiket_klasoru, exist_ok=True)

    for i in tqdm(range(sayi), desc="Sentetik veri olusturuluyor"):
        goruntu = yildiz_alani_olustur(GORUNTU_BOYUTU, GORUNTU_BOYUTU)
        kutu_listesi = []
        goruntu, kutu_listesi = asteroid_ekle(goruntu, kutu_listesi)

        dosya_adi = f"sentetik_{i:05d}"
        cv2.imwrite(os.path.join(goruntu_klasoru, f"{dosya_adi}.png"), goruntu)

        with open(os.path.join(etiket_klasoru, f"{dosya_adi}.txt"), 'w') as dosya:
            for kutu in kutu_listesi:
                dosya.write(f"{kutu[0]} {kutu[1]:.6f} {kutu[2]:.6f} {kutu[3]:.6f} {kutu[4]:.6f}\n")

    print(f"{sayi} sentetik goruntu olusturuldu: {hedef_yolu}")


def ana():
    argumanlar = argumanlari_al()
    klasor_yapisini_olustur()

    if argumanlar.sentetik:
        toplam = argumanlar.sentetik_sayi
        egitim_sayi = int(toplam * argumanlar.egitim_orani)
        dogrulama_sayi = int(toplam * argumanlar.dogrulama_orani)
        test_sayi = toplam - egitim_sayi - dogrulama_sayi

        print(f"Sentetik veri olusturuluyor...")
        print(f"  Egitim: {egitim_sayi}")
        print(f"  Dogrulama: {dogrulama_sayi}")
        print(f"  Test: {test_sayi}")

        sentetik_veri_olustur(egitim_sayi, EGITIM_YOLU)
        sentetik_veri_olustur(dogrulama_sayi, DOGRULAMA_YOLU)
        sentetik_veri_olustur(test_sayi, TEST_YOLU)

        print("\nSentetik veri seti hazir!")
    else:
        print("Gercek veri bolunuyor...")
        veriyi_bol(
            argumanlar.kaynak,
            argumanlar.etiketler,
            argumanlar.egitim_orani,
            argumanlar.dogrulama_orani,
            argumanlar.test_orani,
            argumanlar.tohum
        )
        print("\nVeri seti hazir!")


if __name__ == "__main__":
    ana()
