import os
import sys
import torch
import numpy as np
from tqdm import tqdm

from yapilandirma import (
    TEST_YOLU, MODEL_KAYIT_YOLU, CIKTI_YOLU,
    EN_IYI_MODEL_ADI, CIHAZ, GORUNTU_BOYUTU,
    GUVEN_ESIGI, NMS_ESIGI, IOU_ESIGI
)
from model import AsteroidAlgilayici
from veri_seti import AsteroidVeriSeti, dogrulama_donusumu_olustur
from araclar import non_max_suppression, metrik_hesapla, iou_hesapla


def modeli_yukle(model_yolu, cihaz):
    model = AsteroidAlgilayici()
    kontrol_noktasi = torch.load(model_yolu, map_location=cihaz, weights_only=False)
    model.load_state_dict(kontrol_noktasi['model_durumu'])
    model.to(cihaz)
    model.eval()
    return model


def degerlendirmeyi_baslat():
    cihaz = torch.device(CIHAZ if torch.cuda.is_available() else "cpu")

    model_yolu = os.path.join(MODEL_KAYIT_YOLU, EN_IYI_MODEL_ADI)
    if not os.path.exists(model_yolu):
        print(f"HATA: Model bulunamadi: {model_yolu}")
        sys.exit(1)

    model = modeli_yukle(model_yolu, cihaz)

    donusum = dogrulama_donusumu_olustur()
    test_seti = AsteroidVeriSeti(TEST_YOLU, donusum=donusum)

    if len(test_seti) == 0:
        print(f"HATA: Test verisi bulunamadi: {TEST_YOLU}")
        sys.exit(1)

    print(f"Test veri sayisi: {len(test_seti)}")

    tum_hassasiyet = []
    tum_duyarlilik = []
    tum_f1 = []
    tum_iou = []

    for idx in tqdm(range(len(test_seti)), desc="Degerlendirme"):
        cerceveler, hedefler = test_seti[idx]

        cerceve_tensorleri = [c.unsqueeze(0).to(cihaz) for c in cerceveler]

        with torch.no_grad():
            ciktilar = model(cerceve_tensorleri)
            kutular, skorlar, sinif_idleri = model.tahmin_cikart(ciktilar, GORUNTU_BOYUTU)

        kutular_nms, skorlar_nms, siniflar_nms = non_max_suppression(
            kutular[0], skorlar[0], sinif_idleri[0],
            iou_esigi=NMS_ESIGI,
            guven_esigi=GUVEN_ESIGI
        )

        gercek_kutular = []
        for olcek_hedef in hedefler:
            nesne_maskesi = olcek_hedef[..., 4] == 1
            if nesne_maskesi.sum() > 0:
                gercek_veriler = olcek_hedef[nesne_maskesi]
                for gercek in gercek_veriler:
                    x, y, w, h = gercek[:4]
                    x1 = (x - w / 2) * GORUNTU_BOYUTU
                    y1 = (y - h / 2) * GORUNTU_BOYUTU
                    x2 = (x + w / 2) * GORUNTU_BOYUTU
                    y2 = (y + h / 2) * GORUNTU_BOYUTU
                    gercek_kutular.append(torch.tensor([x1, y1, x2, y2]))

        hassasiyet, duyarlilik, f1 = metrik_hesapla(
            kutular_nms if len(kutular_nms) > 0 else [],
            gercek_kutular if len(gercek_kutular) > 0 else [],
            iou_esigi=IOU_ESIGI
        )

        tum_hassasiyet.append(hassasiyet)
        tum_duyarlilik.append(duyarlilik)
        tum_f1.append(f1)

    ort_hassasiyet = np.mean(tum_hassasiyet)
    ort_duyarlilik = np.mean(tum_duyarlilik)
    ort_f1 = np.mean(tum_f1)

    print("\n" + "=" * 50)
    print("DEGERLENDIRME SONUCLARI")
    print("=" * 50)
    print(f"Ortalama Hassasiyet (Precision): {ort_hassasiyet:.4f}")
    print(f"Ortalama Duyarlilik (Recall):    {ort_duyarlilik:.4f}")
    print(f"Ortalama F1 Skoru:               {ort_f1:.4f}")
    print("=" * 50)

    sonuc_dosyasi = os.path.join(CIKTI_YOLU, "degerlendirme_sonuclari.txt")
    os.makedirs(CIKTI_YOLU, exist_ok=True)
    with open(sonuc_dosyasi, 'w') as dosya:
        dosya.write(f"Hassasiyet: {ort_hassasiyet:.4f}\n")
        dosya.write(f"Duyarlilik: {ort_duyarlilik:.4f}\n")
        dosya.write(f"F1 Skoru: {ort_f1:.4f}\n")
    print(f"Sonuclar kaydedildi: {sonuc_dosyasi}")


if __name__ == "__main__":
    degerlendirmeyi_baslat()
