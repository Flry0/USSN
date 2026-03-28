import torch
from yapilandirma import IOU_ESIGI, NMS_ESIGI, GUVEN_ESIGI


def iou_hesapla(kutu1, kutu2):
    x1 = torch.max(kutu1[..., 0], kutu2[..., 0])
    y1 = torch.max(kutu1[..., 1], kutu2[..., 1])
    x2 = torch.min(kutu1[..., 2], kutu2[..., 2])
    y2 = torch.min(kutu1[..., 3], kutu2[..., 3])

    kesisim = torch.clamp(x2 - x1, min=0) * torch.clamp(y2 - y1, min=0)
    alan1 = (kutu1[..., 2] - kutu1[..., 0]) * (kutu1[..., 3] - kutu1[..., 1])
    alan2 = (kutu2[..., 2] - kutu2[..., 0]) * (kutu2[..., 3] - kutu2[..., 1])
    birlesim = alan1 + alan2 - kesisim + 1e-6

    return kesisim / birlesim


def non_max_suppression(kutular, skorlar, siniflar, iou_esigi=NMS_ESIGI, guven_esigi=GUVEN_ESIGI):
    maske = skorlar > guven_esigi
    kutular = kutular[maske]
    skorlar = skorlar[maske]
    siniflar = siniflar[maske]

    if kutular.shape[0] == 0:
        return kutular, skorlar, siniflar

    siralama = torch.argsort(skorlar, descending=True)
    kutular = kutular[siralama]
    skorlar = skorlar[siralama]
    siniflar = siniflar[siralama]

    secilen = []
    while kutular.shape[0] > 0:
        secilen.append(0)
        if kutular.shape[0] == 1:
            break
        mevcut_kutu = kutular[0].unsqueeze(0)
        diger_kutular = kutular[1:]
        iou_degerleri = iou_hesapla(mevcut_kutu, diger_kutular)
        kalan_maske = iou_degerleri < iou_esigi
        korunan_indeksler = torch.where(kalan_maske)[0]
        kutular = kutular[1:][korunan_indeksler]
        skorlar = skorlar[1:][korunan_indeksler]
        siniflar = siniflar[1:][korunan_indeksler]

    toplam_kutular = torch.stack([kutular[0] if i == 0 else kutular[i] for i in range(len(kutular))])
    return kutular, skorlar, siniflar


def metrik_hesapla(tahmin_kutulari, gercek_kutulari, iou_esigi=IOU_ESIGI):
    if len(tahmin_kutulari) == 0 and len(gercek_kutulari) == 0:
        return 1.0, 1.0, 1.0

    if len(tahmin_kutulari) == 0:
        return 0.0, 0.0, 0.0

    if len(gercek_kutulari) == 0:
        return 0.0, 0.0, 0.0

    dogru_pozitif = 0
    eslesmis = set()

    for tahmin in tahmin_kutulari:
        en_iyi_iou = 0
        en_iyi_idx = -1
        for idx, gercek in enumerate(gercek_kutulari):
            if idx in eslesmis:
                continue
            iou = iou_hesapla(
                tahmin.unsqueeze(0) if tahmin.dim() == 1 else tahmin,
                gercek.unsqueeze(0) if gercek.dim() == 1 else gercek
            ).item()
            if iou > en_iyi_iou:
                en_iyi_iou = iou
                en_iyi_idx = idx
        if en_iyi_iou >= iou_esigi and en_iyi_idx >= 0:
            dogru_pozitif += 1
            eslesmis.add(en_iyi_idx)

    hassasiyet = dogru_pozitif / len(tahmin_kutulari) if len(tahmin_kutulari) > 0 else 0.0
    duyarlilik = dogru_pozitif / len(gercek_kutulari) if len(gercek_kutulari) > 0 else 0.0
    f1_skor = 2 * hassasiyet * duyarlilik / (hassasiyet + duyarlilik + 1e-6)

    return hassasiyet, duyarlilik, f1_skor


def xywh_to_xyxy(kutular):
    x_merkez = kutular[..., 0]
    y_merkez = kutular[..., 1]
    genislik = kutular[..., 2]
    yukseklik = kutular[..., 3]
    x1 = x_merkez - genislik / 2
    y1 = y_merkez - yukseklik / 2
    x2 = x_merkez + genislik / 2
    y2 = y_merkez + yukseklik / 2
    return torch.stack([x1, y1, x2, y2], dim=-1)


def xyxy_to_xywh(kutular):
    x1 = kutular[..., 0]
    y1 = kutular[..., 1]
    x2 = kutular[..., 2]
    y2 = kutular[..., 3]
    x_merkez = (x1 + x2) / 2
    y_merkez = (y1 + y2) / 2
    genislik = x2 - x1
    yukseklik = y2 - y1
    return torch.stack([x_merkez, y_merkez, genislik, yukseklik], dim=-1)
