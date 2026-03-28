import os
import sys
import cv2
import torch
import numpy as np
import argparse

from yapilandirma import (
    GORUNTU_BOYUTU, CIHAZ, MODEL_KAYIT_YOLU, CIKTI_YOLU,
    EN_IYI_MODEL_ADI, GUVEN_ESIGI, NMS_ESIGI, SINIF_ISIMLERI,
    HAREKET_CERCEVE_SAYISI
)
from model import AsteroidAlgilayici
from araclar import non_max_suppression


def argumanlari_al():
    cozumleyici = argparse.ArgumentParser()
    cozumleyici.add_argument('--goruntu', type=str, required=True,
                             help='Goruntu dosyasi yolu')
    cozumleyici.add_argument('--model', type=str, default=None)
    cozumleyici.add_argument('--guven', type=float, default=GUVEN_ESIGI)
    cozumleyici.add_argument('--cikti', type=str, default=None)
    return cozumleyici.parse_args()


def tek_goruntu_tespit(goruntu_yolu, model, cihaz, guven_esigi):
    cerceve = cv2.imread(goruntu_yolu)
    if cerceve is None:
        print(f"HATA: Goruntu okunamadi: {goruntu_yolu}")
        return None, []

    orijinal_yukseklik, orijinal_genislik = cerceve.shape[:2]
    olcek_x = orijinal_genislik / GORUNTU_BOYUTU
    olcek_y = orijinal_yukseklik / GORUNTU_BOYUTU

    goruntu_rgb = cv2.cvtColor(cerceve, cv2.COLOR_BGR2RGB)
    goruntu_boyutlu = cv2.resize(goruntu_rgb, (GORUNTU_BOYUTU, GORUNTU_BOYUTU))
    tensor = torch.from_numpy(goruntu_boyutlu).permute(2, 0, 1).float() / 255.0
    tensor = tensor.unsqueeze(0).to(cihaz)

    cerceve_listesi = [tensor] * HAREKET_CERCEVE_SAYISI

    with torch.no_grad():
        ciktilar = model(cerceve_listesi)
        kutular, skorlar, sinif_idleri = model.tahmin_cikart(ciktilar, GORUNTU_BOYUTU)

    kutular_nms, skorlar_nms, siniflar_nms = non_max_suppression(
        kutular[0], skorlar[0], sinif_idleri[0],
        iou_esigi=NMS_ESIGI,
        guven_esigi=guven_esigi
    )

    tespitler = []
    sonuc = cerceve.copy()

    for i in range(len(kutular_nms)):
        x1 = int(kutular_nms[i][0].item() * olcek_x)
        y1 = int(kutular_nms[i][1].item() * olcek_y)
        x2 = int(kutular_nms[i][2].item() * olcek_x)
        y2 = int(kutular_nms[i][3].item() * olcek_y)
        skor = skorlar_nms[i].item()
        sinif_idx = int(siniflar_nms[i].item())
        sinif_adi = SINIF_ISIMLERI[sinif_idx] if sinif_idx < len(SINIF_ISIMLERI) else f"sinif_{sinif_idx}"

        merkez_x = (x1 + x2) // 2
        merkez_y = (y1 + y2) // 2

        tespitler.append({
            'sinif': sinif_adi,
            'guven': skor,
            'kutu': [x1, y1, x2, y2],
            'merkez': [merkez_x, merkez_y],
            'boyut': [x2 - x1, y2 - y1]
        })

        cv2.rectangle(sonuc, (x1, y1), (x2, y2), (0, 255, 128), 2)
        etiket = f"{sinif_adi}: {skor:.2f}"
        (yg, yy), _ = cv2.getTextSize(etiket, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        cv2.rectangle(sonuc, (x1, y1 - yy - 10), (x1 + yg, y1), (0, 180, 90), -1)
        cv2.putText(sonuc, etiket, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.circle(sonuc, (merkez_x, merkez_y), 4, (0, 0, 255), -1)
        konum = f"({merkez_x}, {merkez_y})"
        cv2.putText(sonuc, konum, (x2 + 5, merkez_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 128), 1)

    return sonuc, tespitler


def ana():
    argumanlar = argumanlari_al()

    cihaz = torch.device(CIHAZ if torch.cuda.is_available() else "cpu")

    if argumanlar.model:
        model_yolu = argumanlar.model
    else:
        model_yolu = os.path.join(MODEL_KAYIT_YOLU, EN_IYI_MODEL_ADI)

    if not os.path.exists(model_yolu):
        print(f"HATA: Model bulunamadi: {model_yolu}")
        sys.exit(1)

    model = AsteroidAlgilayici()
    kontrol = torch.load(model_yolu, map_location=cihaz, weights_only=False)
    model.load_state_dict(kontrol['model_durumu'])
    model.to(cihaz)
    model.eval()

    sonuc, tespitler = tek_goruntu_tespit(argumanlar.goruntu, model, cihaz, argumanlar.guven)

    if sonuc is not None:
        print(f"\nToplam tespit: {len(tespitler)}")
        for idx, tespit in enumerate(tespitler):
            print(f"  [{idx + 1}] {tespit['sinif']} - Guven: {tespit['guven']:.2f}")
            print(f"       Konum: {tespit['merkez']}")
            print(f"       Kutu: {tespit['kutu']}")
            print(f"       Boyut: {tespit['boyut']}")

        if argumanlar.cikti:
            cikti_yolu = argumanlar.cikti
        else:
            os.makedirs(CIKTI_YOLU, exist_ok=True)
            dosya_adi = os.path.basename(argumanlar.goruntu)
            cikti_yolu = os.path.join(CIKTI_YOLU, f"tespit_{dosya_adi}")

        cv2.imwrite(cikti_yolu, sonuc)
        print(f"\nSonuc kaydedildi: {cikti_yolu}")


if __name__ == "__main__":
    ana()
