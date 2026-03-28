import torch
import torch.nn as nn
import torch.nn.functional as F
from yapilandirma import (
    OMURGA_KANAL_LISTESI, ALGILAMA_KAFASI_KANAL, SINIF_SAYISI,
    ANCHOR_SAYISI, HAREKET_CERCEVE_SAYISI, KANAL_SAYISI
)


class KonvBlogu(nn.Module):
    def __init__(self, giris_kanal, cikis_kanal, cekirdek=3, adim=1, dolgu=1):
        super().__init__()
        self.konv = nn.Conv2d(giris_kanal, cikis_kanal, cekirdek, adim, dolgu, bias=False)
        self.norm = nn.BatchNorm2d(cikis_kanal)
        self.aktivasyon = nn.SiLU(inplace=True)

    def forward(self, x):
        return self.aktivasyon(self.norm(self.konv(x)))


class ArtikBlok(nn.Module):
    def __init__(self, kanal_sayisi, tekrar=1):
        super().__init__()
        self.katmanlar = nn.ModuleList()
        for _ in range(tekrar):
            self.katmanlar.append(nn.Sequential(
                KonvBlogu(kanal_sayisi, kanal_sayisi // 2, cekirdek=1, dolgu=0),
                KonvBlogu(kanal_sayisi // 2, kanal_sayisi, cekirdek=3, dolgu=1)
            ))

    def forward(self, x):
        for katman in self.katmanlar:
            x = x + katman(x)
        return x


class HareketModulu(nn.Module):
    def __init__(self, cerceve_sayisi, giris_kanal):
        super().__init__()
        self.cerceve_sayisi = cerceve_sayisi
        fark_kanal = giris_kanal * (cerceve_sayisi - 1)
        self.fark_konv = nn.Sequential(
            KonvBlogu(fark_kanal, giris_kanal * 2, cekirdek=3, dolgu=1),
            KonvBlogu(giris_kanal * 2, giris_kanal, cekirdek=1, dolgu=0)
        )
        self.dikkat = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(giris_kanal, giris_kanal // 4),
            nn.SiLU(inplace=True),
            nn.Linear(giris_kanal // 4, giris_kanal),
            nn.Sigmoid()
        )

    def forward(self, cerceveler):
        farklar = []
        for i in range(len(cerceveler) - 1):
            farklar.append(cerceveler[i + 1] - cerceveler[i])
        fark_birlesik = torch.cat(farklar, dim=1)
        hareket_ozelligi = self.fark_konv(fark_birlesik)
        dikkat_agirligi = self.dikkat(hareket_ozelligi).unsqueeze(-1).unsqueeze(-1)
        return hareket_ozelligi * dikkat_agirligi


class ParlaklikModulu(nn.Module):
    def __init__(self, giris_kanal):
        super().__init__()
        self.parlaklik_konv = nn.Sequential(
            KonvBlogu(giris_kanal, giris_kanal, cekirdek=3, dolgu=1),
            KonvBlogu(giris_kanal, giris_kanal, cekirdek=1, dolgu=0)
        )
        self.esik_agirligi = nn.Parameter(torch.tensor(0.5))

    def forward(self, x):
        ortalama = x.mean(dim=1, keepdim=True)
        parlak_bolge = torch.sigmoid((ortalama - self.esik_agirligi) * 10)
        ozellik = self.parlaklik_konv(x)
        return ozellik * parlak_bolge


class OmurgaAgi(nn.Module):
    def __init__(self):
        super().__init__()
        katmanlar = []
        onceki_kanal = KANAL_SAYISI
        for kanal in OMURGA_KANAL_LISTESI:
            katmanlar.append(nn.Sequential(
                KonvBlogu(onceki_kanal, kanal, cekirdek=3, adim=2, dolgu=1),
                ArtikBlok(kanal, tekrar=2)
            ))
            onceki_kanal = kanal
        self.katmanlar = nn.ModuleList(katmanlar)

    def forward(self, x):
        ozellikler = []
        for katman in self.katmanlar:
            x = katman(x)
            ozellikler.append(x)
        return ozellikler[-3], ozellikler[-2], ozellikler[-1]


class BoynAgi(nn.Module):
    def __init__(self):
        super().__init__()
        self.yukari1 = nn.Sequential(
            KonvBlogu(OMURGA_KANAL_LISTESI[-1], OMURGA_KANAL_LISTESI[-2], cekirdek=1, dolgu=0),
            nn.Upsample(scale_factor=2, mode='nearest')
        )
        self.birlestir1 = nn.Sequential(
            KonvBlogu(OMURGA_KANAL_LISTESI[-2] * 2, OMURGA_KANAL_LISTESI[-2], cekirdek=1, dolgu=0),
            KonvBlogu(OMURGA_KANAL_LISTESI[-2], OMURGA_KANAL_LISTESI[-2], cekirdek=3, dolgu=1)
        )
        self.yukari2 = nn.Sequential(
            KonvBlogu(OMURGA_KANAL_LISTESI[-2], OMURGA_KANAL_LISTESI[-3], cekirdek=1, dolgu=0),
            nn.Upsample(scale_factor=2, mode='nearest')
        )
        self.birlestir2 = nn.Sequential(
            KonvBlogu(OMURGA_KANAL_LISTESI[-3] * 2, OMURGA_KANAL_LISTESI[-3], cekirdek=1, dolgu=0),
            KonvBlogu(OMURGA_KANAL_LISTESI[-3], OMURGA_KANAL_LISTESI[-3], cekirdek=3, dolgu=1)
        )

    def forward(self, kucuk, orta, buyuk):
        yukari = self.yukari1(buyuk)
        orta = self.birlestir1(torch.cat([yukari, orta], dim=1))
        yukari = self.yukari2(orta)
        kucuk = self.birlestir2(torch.cat([yukari, kucuk], dim=1))
        return kucuk, orta, buyuk


class AlgilamaKafasi(nn.Module):
    def __init__(self, giris_kanal):
        super().__init__()
        cikis_kanal = ANCHOR_SAYISI * (5 + SINIF_SAYISI)
        self.konv_katmanlari = nn.Sequential(
            KonvBlogu(giris_kanal, ALGILAMA_KAFASI_KANAL, cekirdek=3, dolgu=1),
            KonvBlogu(ALGILAMA_KAFASI_KANAL, ALGILAMA_KAFASI_KANAL, cekirdek=3, dolgu=1),
            nn.Conv2d(ALGILAMA_KAFASI_KANAL, cikis_kanal, kernel_size=1)
        )

    def forward(self, x):
        return self.konv_katmanlari(x)


class UzayCopuAlgilayici(nn.Module):
    def __init__(self, cerceve_sayisi=HAREKET_CERCEVE_SAYISI):
        super().__init__()
        self.cerceve_sayisi = cerceve_sayisi
        self.omurga = OmurgaAgi()
        self.hareket = HareketModulu(cerceve_sayisi, OMURGA_KANAL_LISTESI[-3])
        self.parlaklik = ParlaklikModulu(OMURGA_KANAL_LISTESI[-3])
        self.boyun = BoynAgi()
        self.birlestirme = nn.Sequential(
            KonvBlogu(OMURGA_KANAL_LISTESI[-3] * 3, OMURGA_KANAL_LISTESI[-3], cekirdek=1, dolgu=0),
            KonvBlogu(OMURGA_KANAL_LISTESI[-3], OMURGA_KANAL_LISTESI[-3], cekirdek=3, dolgu=1)
        )
        self.kafa_kucuk = AlgilamaKafasi(OMURGA_KANAL_LISTESI[-3])
        self.kafa_orta = AlgilamaKafasi(OMURGA_KANAL_LISTESI[-2])
        self.kafa_buyuk = AlgilamaKafasi(OMURGA_KANAL_LISTESI[-1])

    def forward(self, cerceve_listesi):
        if isinstance(cerceve_listesi, torch.Tensor) and cerceve_listesi.dim() == 4:
            cerceve_listesi = [cerceve_listesi] * self.cerceve_sayisi

        omurga_ciktilari = []
        for cerceve in cerceve_listesi:
            omurga_ciktilari.append(self.omurga(cerceve))

        kucuk_ozellikler = [c[0] for c in omurga_ciktilari]
        hareket_ozelligi = self.hareket(kucuk_ozellikler)
        parlaklik_ozelligi = self.parlaklik(kucuk_ozellikler[-1])
        birlesik = torch.cat([kucuk_ozellikler[-1], hareket_ozelligi, parlaklik_ozelligi], dim=1)
        birlesik = self.birlestirme(birlesik)

        orta_ozellik = omurga_ciktilari[-1][1]
        buyuk_ozellik = omurga_ciktilari[-1][2]

        kucuk, orta, buyuk = self.boyun(birlesik, orta_ozellik, buyuk_ozellik)

        cikti_kucuk = self.kafa_kucuk(kucuk)
        cikti_orta = self.kafa_orta(orta)
        cikti_buyuk = self.kafa_buyuk(buyuk)

        return [cikti_kucuk, cikti_orta, cikti_buyuk]

    def tahmin_cikart(self, ciktilar, goruntu_boyutu):
        tum_kutular = []
        tum_skorlar = []
        tum_siniflar = []

        from yapilandirma import ANCHOR_BOYUTLARI

        for olcek_idx, cikti in enumerate(ciktilar):
            parti, _, yukseklik, genislik = cikti.shape
            cikti = cikti.view(parti, ANCHOR_SAYISI, 5 + SINIF_SAYISI, yukseklik, genislik)
            cikti = cikti.permute(0, 1, 3, 4, 2).contiguous()

            grid_y, grid_x = torch.meshgrid(
                torch.arange(yukseklik, device=cikti.device, dtype=torch.float32),
                torch.arange(genislik, device=cikti.device, dtype=torch.float32),
                indexing='ij'
            )

            anchor_listesi = ANCHOR_BOYUTLARI[olcek_idx]
            anchor_tensor = torch.tensor(anchor_listesi, device=cikti.device, dtype=torch.float32)

            tx = torch.sigmoid(cikti[..., 0])
            ty = torch.sigmoid(cikti[..., 1])
            tw = cikti[..., 2]
            th = cikti[..., 3]
            nesne_skoru = torch.sigmoid(cikti[..., 4])
            sinif_skoru = torch.sigmoid(cikti[..., 5:])

            adim = goruntu_boyutu / yukseklik

            bx = (tx + grid_x.unsqueeze(0).unsqueeze(0)) * adim
            by = (ty + grid_y.unsqueeze(0).unsqueeze(0)) * adim
            bw = torch.exp(tw) * anchor_tensor[:, 0].view(1, -1, 1, 1)
            bh = torch.exp(th) * anchor_tensor[:, 1].view(1, -1, 1, 1)

            x1 = bx - bw / 2
            y1 = by - bh / 2
            x2 = bx + bw / 2
            y2 = by + bh / 2

            kutular = torch.stack([x1, y1, x2, y2], dim=-1).view(parti, -1, 4)
            skorlar = (nesne_skoru.unsqueeze(-1) * sinif_skoru).view(parti, -1, SINIF_SAYISI)
            en_iyi_skor, en_iyi_sinif = skorlar.max(dim=-1)

            tum_kutular.append(kutular)
            tum_skorlar.append(en_iyi_skor)
            tum_siniflar.append(en_iyi_sinif)

        return torch.cat(tum_kutular, dim=1), torch.cat(tum_skorlar, dim=1), torch.cat(tum_siniflar, dim=1)
