import os

PROJE_KOKU = os.path.dirname(os.path.abspath(__file__))

VERI_SETI_YOLU = os.path.join(PROJE_KOKU, "veri_seti")
EGITIM_YOLU = os.path.join(VERI_SETI_YOLU, "egitim")
DOGRULAMA_YOLU = os.path.join(VERI_SETI_YOLU, "dogrulama")
TEST_YOLU = os.path.join(VERI_SETI_YOLU, "test")

GORUNTU_YOLU = "goruntuler"
ETIKET_YOLU = "etiketler"

MODEL_KAYIT_YOLU = os.path.join(PROJE_KOKU, "modeller")
CIKTI_YOLU = os.path.join(PROJE_KOKU, "ciktilar")

GORUNTU_BOYUTU = 416
KANAL_SAYISI = 3
SINIF_SAYISI = 1
SINIF_ISIMLERI = ["asteroid"]

OGRENME_ORANI = 1e-4
PARTI_BOYUTU = 8
EPOK_SAYISI = 100
AGIRLIK_AZALMASI = 1e-5

GUVEN_ESIGI = 0.5
NMS_ESIGI = 0.4
IOU_ESIGI = 0.5

OMURGA_KANAL_LISTESI = [32, 64, 128, 256, 512]
ALGILAMA_KAFASI_KANAL = 256
ANCHOR_BOYUTLARI = [
    [(10, 13), (16, 30), (33, 23)],
    [(30, 61), (62, 45), (59, 119)],
    [(116, 90), (156, 198), (373, 326)]
]
ANCHOR_SAYISI = 3
GRID_OLCEKLERI = [GORUNTU_BOYUTU // 32, GORUNTU_BOYUTU // 16, GORUNTU_BOYUTU // 8]

HAREKET_CERCEVE_SAYISI = 3
PARLAKLIK_ESIGI = 30
FARK_ESIGI = 25

CIHAZ = "cuda"
ISCI_SAYISI = 4
PIN_BELLEK = True

EN_IYI_MODEL_ADI = "en_iyi_model.pth"
SON_MODEL_ADI = "son_model.pth"
