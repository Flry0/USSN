import os
import cv2
import torch
import numpy as np
from torch.utils.data import Dataset
from PIL import Image
import albumentations as A
from albumentations.pytorch import ToTensorV2
from yapilandirma import (
    GORUNTU_BOYUTU, GORUNTU_YOLU, ETIKET_YOLU,
    HAREKET_CERCEVE_SAYISI, ANCHOR_BOYUTLARI, ANCHOR_SAYISI,
    SINIF_SAYISI, GRID_OLCEKLERI
)


def egitim_donusumu_olustur():
    return A.Compose([
        A.Resize(GORUNTU_BOYUTU, GORUNTU_BOYUTU),
        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.3),
        A.RandomBrightnessContrast(brightness_limit=0.3, contrast_limit=0.3, p=0.5),
        A.GaussNoise(p=0.3),
        A.Normalize(mean=[0.0, 0.0, 0.0], std=[1.0, 1.0, 1.0]),
        ToTensorV2()
    ], bbox_params=A.BboxParams(format='yolo', label_fields=['sinif_etiketleri']))


def dogrulama_donusumu_olustur():
    return A.Compose([
        A.Resize(GORUNTU_BOYUTU, GORUNTU_BOYUTU),
        A.Normalize(mean=[0.0, 0.0, 0.0], std=[1.0, 1.0, 1.0]),
        ToTensorV2()
    ], bbox_params=A.BboxParams(format='yolo', label_fields=['sinif_etiketleri']))


def etiket_dosyasi_oku(dosya_yolu):
    kutular = []
    siniflar = []
    if not os.path.exists(dosya_yolu):
        return kutular, siniflar
    with open(dosya_yolu, 'r') as dosya:
        for satir in dosya.readlines():
            parcalar = satir.strip().split()
            if len(parcalar) >= 5:
                sinif_no = int(parcalar[0])
                x_merkez = float(parcalar[1])
                y_merkez = float(parcalar[2])
                genislik = float(parcalar[3])
                yukseklik = float(parcalar[4])
                kutular.append([x_merkez, y_merkez, genislik, yukseklik])
                siniflar.append(sinif_no)
    return kutular, siniflar


def hedef_tensoru_olustur(kutular, siniflar):
    hedefler = []
    for olcek_idx, grid_boyutu in enumerate(GRID_OLCEKLERI):
        hedef = torch.zeros(ANCHOR_SAYISI, grid_boyutu, grid_boyutu, 6)
        for kutu_idx, kutu in enumerate(kutular):
            x_merkez, y_merkez, genislik, yukseklik = kutu
            sinif = siniflar[kutu_idx]

            grid_x = int(x_merkez * grid_boyutu)
            grid_y = int(y_merkez * grid_boyutu)
            grid_x = min(grid_x, grid_boyutu - 1)
            grid_y = min(grid_y, grid_boyutu - 1)

            en_iyi_iou = 0
            en_iyi_anchor = 0
            for anchor_idx, anchor in enumerate(ANCHOR_BOYUTLARI[olcek_idx]):
                anchor_g = anchor[0] / GORUNTU_BOYUTU
                anchor_y = anchor[1] / GORUNTU_BOYUTU
                kesisim_g = min(genislik, anchor_g)
                kesisim_y = min(yukseklik, anchor_y)
                kesisim_alan = kesisim_g * kesisim_y
                birlesim_alan = genislik * yukseklik + anchor_g * anchor_y - kesisim_alan
                iou = kesisim_alan / (birlesim_alan + 1e-6)
                if iou > en_iyi_iou:
                    en_iyi_iou = iou
                    en_iyi_anchor = anchor_idx

            if hedef[en_iyi_anchor, grid_y, grid_x, 4] == 0:
                hedef[en_iyi_anchor, grid_y, grid_x, 0] = x_merkez * grid_boyutu - grid_x
                hedef[en_iyi_anchor, grid_y, grid_x, 1] = y_merkez * grid_boyutu - grid_y
                hedef[en_iyi_anchor, grid_y, grid_x, 2] = genislik
                hedef[en_iyi_anchor, grid_y, grid_x, 3] = yukseklik
                hedef[en_iyi_anchor, grid_y, grid_x, 4] = 1.0
                hedef[en_iyi_anchor, grid_y, grid_x, 5] = sinif

        hedefler.append(hedef)
    return hedefler


class AsteroidVeriSeti(Dataset):
    def __init__(self, veri_yolu, donusum=None, cerceve_sayisi=HAREKET_CERCEVE_SAYISI):
        self.veri_yolu = veri_yolu
        self.donusum = donusum
        self.cerceve_sayisi = cerceve_sayisi
        self.goruntu_klasoru = os.path.join(veri_yolu, GORUNTU_YOLU)
        self.etiket_klasoru = os.path.join(veri_yolu, ETIKET_YOLU)

        desteklenen_uzantilar = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.fits')
        self.goruntu_listesi = []
        if os.path.exists(self.goruntu_klasoru):
            self.goruntu_listesi = sorted([
                dosya for dosya in os.listdir(self.goruntu_klasoru)
                if dosya.lower().endswith(desteklenen_uzantilar)
            ])

    def __len__(self):
        return len(self.goruntu_listesi)

    def goruntu_yukle(self, goruntu_adi):
        goruntu_yolu = os.path.join(self.goruntu_klasoru, goruntu_adi)
        if goruntu_adi.lower().endswith(('.fits', '.fit')):
            try:
                from astropy.io import fits
                with fits.open(goruntu_yolu) as hdul:
                    veri = hdul[0].data.astype(np.float32)
                    veri = (veri - veri.min()) / (veri.max() - veri.min() + 1e-8) * 255
                    veri = veri.astype(np.uint8)
                    if veri.ndim == 2:
                        veri = cv2.cvtColor(veri, cv2.COLOR_GRAY2RGB)
                    return veri
            except ImportError:
                return None
        goruntu = cv2.imread(goruntu_yolu)
        if goruntu is not None:
            goruntu = cv2.cvtColor(goruntu, cv2.COLOR_BGR2RGB)
        return goruntu

    def komsulari_bul(self, indeks):
        toplam = len(self.goruntu_listesi)
        indeksler = []
        for i in range(self.cerceve_sayisi):
            komsu = indeks - (self.cerceve_sayisi - 1) + i
            komsu = max(0, min(komsu, toplam - 1))
            indeksler.append(komsu)
        return indeksler

    def __getitem__(self, indeks):
        komsu_indeksler = self.komsulari_bul(indeks)
        ana_goruntu_adi = self.goruntu_listesi[indeks]
        etiket_adi = os.path.splitext(ana_goruntu_adi)[0] + '.txt'
        etiket_yolu = os.path.join(self.etiket_klasoru, etiket_adi)
        kutular, siniflar = etiket_dosyasi_oku(etiket_yolu)

        cerceve_tensorleri = []
        for komsu_idx in komsu_indeksler:
            goruntu_adi = self.goruntu_listesi[komsu_idx]
            goruntu = self.goruntu_yukle(goruntu_adi)
            if goruntu is None:
                goruntu = np.zeros((GORUNTU_BOYUTU, GORUNTU_BOYUTU, 3), dtype=np.uint8)

            if self.donusum and komsu_idx == indeks:
                gecerli_kutular = [k for k in kutular if all(0 <= v <= 1 for v in k)]
                gecerli_siniflar = siniflar[:len(gecerli_kutular)]
                donusmus = self.donusum(
                    image=goruntu,
                    bboxes=gecerli_kutular,
                    sinif_etiketleri=gecerli_siniflar
                )
                cerceve_tensorleri.append(donusmus['image'].float())
                kutular = [[b[0], b[1], b[2], b[3]] for b in donusmus['bboxes']]
                siniflar = donusmus['sinif_etiketleri']
            elif self.donusum:
                donusmus = self.donusum(
                    image=goruntu,
                    bboxes=[],
                    sinif_etiketleri=[]
                )
                cerceve_tensorleri.append(donusmus['image'].float())
            else:
                goruntu = cv2.resize(goruntu, (GORUNTU_BOYUTU, GORUNTU_BOYUTU))
                tensor = torch.from_numpy(goruntu).permute(2, 0, 1).float() / 255.0
                cerceve_tensorleri.append(tensor)

        hedefler = hedef_tensoru_olustur(kutular, siniflar)
        return cerceve_tensorleri, hedefler
