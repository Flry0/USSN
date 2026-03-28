import torch
import torch.nn as nn
from yapilandirma import ANCHOR_BOYUTLARI, ANCHOR_SAYISI, SINIF_SAYISI, GORUNTU_BOYUTU, GRID_OLCEKLERI


class AsteroidKayipFonksiyonu(nn.Module):
    def __init__(self):
        super().__init__()
        self.mse = nn.MSELoss(reduction='sum')
        self.bce = nn.BCEWithLogitsLoss(reduction='sum')
        self.ce = nn.CrossEntropyLoss(reduction='sum')

        self.konum_agirligi = 5.0
        self.nesne_agirligi = 1.0
        self.nesne_yok_agirligi = 0.5
        self.sinif_agirligi = 1.0

    def forward(self, tahminler, hedefler):
        toplam_kayip = 0.0
        konum_kaybi = 0.0
        nesne_kaybi = 0.0
        sinif_kaybi = 0.0

        for olcek_idx, tahmin in enumerate(tahminler):
            parti, _, yukseklik, genislik = tahmin.shape
            hedef = hedefler[olcek_idx]

            tahmin = tahmin.view(parti, ANCHOR_SAYISI, 5 + SINIF_SAYISI, yukseklik, genislik)
            tahmin = tahmin.permute(0, 1, 3, 4, 2).contiguous()

            nesne_maskesi = hedef[..., 4] == 1
            nesne_yok_maskesi = hedef[..., 4] == 0

            if nesne_maskesi.sum() > 0:
                tahmin_nesne = tahmin[nesne_maskesi]
                hedef_nesne = hedef[nesne_maskesi]

                konum_tahmin = tahmin_nesne[..., :4]
                konum_hedef = hedef_nesne[..., :4]

                xy_kaybi = self.mse(
                    torch.sigmoid(konum_tahmin[..., :2]),
                    konum_hedef[..., :2]
                )
                wh_kaybi = self.mse(
                    konum_tahmin[..., 2:4],
                    torch.log(konum_hedef[..., 2:4] + 1e-16)
                )
                konum_kaybi += self.konum_agirligi * (xy_kaybi + wh_kaybi)

                nesne_skor_kaybi = self.bce(
                    tahmin_nesne[..., 4],
                    hedef_nesne[..., 4]
                )
                nesne_kaybi += self.nesne_agirligi * nesne_skor_kaybi

                if SINIF_SAYISI > 1:
                    sinif_tahmin = tahmin_nesne[..., 5:]
                    sinif_hedef = hedef_nesne[..., 5].long()
                    sinif_kaybi += self.sinif_agirligi * self.ce(sinif_tahmin, sinif_hedef)

            nesne_yok_tahmin = tahmin[nesne_yok_maskesi]
            if nesne_yok_tahmin.numel() > 0:
                nesne_yok_kaybi = self.bce(
                    nesne_yok_tahmin[..., 4],
                    torch.zeros_like(nesne_yok_tahmin[..., 4])
                )
                nesne_kaybi += self.nesne_yok_agirligi * nesne_yok_kaybi

        toplam_kayip = konum_kaybi + nesne_kaybi + sinif_kaybi
        return toplam_kayip, konum_kaybi, nesne_kaybi, sinif_kaybi
