import os
import sys
import cv2
import time
import torch
import numpy as np
import argparse
from collections import deque

from yapilandirma import (
    GORUNTU_BOYUTU, CIHAZ, MODEL_KAYIT_YOLU, CIKTI_YOLU,
    EN_IYI_MODEL_ADI, GUVEN_ESIGI, NMS_ESIGI, SINIF_ISIMLERI,
    HAREKET_CERCEVE_SAYISI, PARLAKLIK_ESIGI, FARK_ESIGI
)
from model import AsteroidAlgilayici
from araclar import non_max_suppression


KUTU_RENGI = (0, 255, 128)
YAZI_RENGI = (255, 255, 255)
ARKA_PLAN_RENGI = (0, 180, 90)
HAREKET_RENGI = (0, 200, 255)
PARLAKLIK_RENGI = (255, 255, 0)


def argumanlari_al():
    cozumleyici = argparse.ArgumentParser()
    cozumleyici.add_argument('--kaynak', type=str, required=True,
                             help='Video dosyasi yolu veya goruntu klasoru')
    cozumleyici.add_argument('--model', type=str, default=None,
                             help='Model dosyasi yolu')
    cozumleyici.add_argument('--guven', type=float, default=GUVEN_ESIGI,
                             help='Guven esigi')
    cozumleyici.add_argument('--nms', type=float, default=NMS_ESIGI,
                             help='NMS esigi')
    cozumleyici.add_argument('--cikti', type=str, default=None,
                             help='Cikti video dosyasi yolu')
    cozumleyici.add_argument('--goster', action='store_true',
                             help='Sonuclari ekranda goster')
    cozumleyici.add_argument('--hareket', action='store_true',
                             help='Hareket haritasini goster')
    cozumleyici.add_argument('--parlaklik', action='store_true',
                             help='Parlaklik haritasini goster')
    return cozumleyici.parse_args()


def modeli_yukle(model_yolu, cihaz):
    model = AsteroidAlgilayici()
    kontrol_noktasi = torch.load(model_yolu, map_location=cihaz, weights_only=False)
    model.load_state_dict(kontrol_noktasi['model_durumu'])
    model.to(cihaz)
    model.eval()
    return model


def cerceve_hazirla(cerceve, cihaz):
    goruntu = cv2.cvtColor(cerceve, cv2.COLOR_BGR2RGB)
    goruntu = cv2.resize(goruntu, (GORUNTU_BOYUTU, GORUNTU_BOYUTU))
    tensor = torch.from_numpy(goruntu).permute(2, 0, 1).float() / 255.0
    return tensor.unsqueeze(0).to(cihaz)


def hareket_haritasi_olustur(onceki_cerceve, simdiki_cerceve):
    if onceki_cerceve is None:
        return np.zeros_like(simdiki_cerceve)
    gri_onceki = cv2.cvtColor(onceki_cerceve, cv2.COLOR_BGR2GRAY)
    gri_simdiki = cv2.cvtColor(simdiki_cerceve, cv2.COLOR_BGR2GRAY)
    fark = cv2.absdiff(gri_onceki, gri_simdiki)
    _, esiklenmis = cv2.threshold(fark, FARK_ESIGI, 255, cv2.THRESH_BINARY)
    esiklenmis = cv2.GaussianBlur(esiklenmis, (5, 5), 0)
    renkli_harita = cv2.applyColorMap(esiklenmis, cv2.COLORMAP_HOT)
    return renkli_harita


def parlaklik_haritasi_olustur(cerceve):
    gri = cv2.cvtColor(cerceve, cv2.COLOR_BGR2GRAY)
    _, parlak = cv2.threshold(gri, PARLAKLIK_ESIGI, 255, cv2.THRESH_BINARY)
    parlak = cv2.GaussianBlur(parlak, (3, 3), 0)
    renkli_harita = cv2.applyColorMap(parlak, cv2.COLORMAP_JET)
    return renkli_harita


def kutu_ciz(cerceve, kutular, skorlar, siniflar, olcek_x, olcek_y):
    tespit_sayisi = 0
    for i in range(len(kutular)):
        x1 = int(kutular[i][0].item() * olcek_x)
        y1 = int(kutular[i][1].item() * olcek_y)
        x2 = int(kutular[i][2].item() * olcek_x)
        y2 = int(kutular[i][3].item() * olcek_y)
        skor = skorlar[i].item()
        sinif_idx = int(siniflar[i].item())
        sinif_adi = SINIF_ISIMLERI[sinif_idx] if sinif_idx < len(SINIF_ISIMLERI) else f"sinif_{sinif_idx}"

        cv2.rectangle(cerceve, (x1, y1), (x2, y2), KUTU_RENGI, 2)

        etiket = f"{sinif_adi}: {skor:.2f}"
        (yazi_g, yazi_y), taban = cv2.getTextSize(etiket, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        cv2.rectangle(cerceve, (x1, y1 - yazi_y - 10), (x1 + yazi_g, y1), ARKA_PLAN_RENGI, -1)
        cv2.putText(cerceve, etiket, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, YAZI_RENGI, 1)

        merkez_x = (x1 + x2) // 2
        merkez_y = (y1 + y2) // 2
        cv2.circle(cerceve, (merkez_x, merkez_y), 4, (0, 0, 255), -1)
        cv2.circle(cerceve, (merkez_x, merkez_y), 8, (0, 0, 255), 1)

        konum_metni = f"({merkez_x}, {merkez_y})"
        cv2.putText(cerceve, konum_metni, (x2 + 5, y2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, KUTU_RENGI, 1)

        tespit_sayisi += 1

    return cerceve, tespit_sayisi


def bilgi_paneli_ciz(cerceve, tespit_sayisi, fps, cerceve_no):
    panel_yukseklik = 80
    panel = np.zeros((panel_yukseklik, cerceve.shape[1], 3), dtype=np.uint8)
    panel[:] = (30, 30, 30)

    cv2.putText(panel, f"Asteroid Tespit Sistemi", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 128), 2)
    cv2.putText(panel, f"Tespit: {tespit_sayisi}", (10, 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.putText(panel, f"FPS: {fps:.1f}", (200, 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.putText(panel, f"Cerceve: {cerceve_no}", (380, 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    return np.vstack([panel, cerceve])


def videoyu_isle(argumanlar):
    cihaz = torch.device(CIHAZ if torch.cuda.is_available() else "cpu")
    print(f"Kullanilan cihaz: {cihaz}")

    if argumanlar.model:
        model_yolu = argumanlar.model
    else:
        model_yolu = os.path.join(MODEL_KAYIT_YOLU, EN_IYI_MODEL_ADI)

    if not os.path.exists(model_yolu):
        print(f"HATA: Model dosyasi bulunamadi: {model_yolu}")
        sys.exit(1)

    print(f"Model yukleniyor: {model_yolu}")
    model = modeli_yukle(model_yolu, cihaz)
    print("Model basariyla yuklendi!")

    kaynak = argumanlar.kaynak

    if os.path.isdir(kaynak):
        goruntu_dosyalari = sorted([
            os.path.join(kaynak, d) for d in os.listdir(kaynak)
            if d.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'))
        ])
        if len(goruntu_dosyalari) == 0:
            print("HATA: Klasorde goruntu bulunamadi!")
            sys.exit(1)
        goruntulerden_isle(model, goruntu_dosyalari, argumanlar, cihaz)
    else:
        video_yakalayici = cv2.VideoCapture(kaynak)
        if not video_yakalayici.isOpened():
            print(f"HATA: Video acilamadi: {kaynak}")
            sys.exit(1)
        videodan_isle(model, video_yakalayici, argumanlar, cihaz)


def videodan_isle(model, yakalayici, argumanlar, cihaz):
    genislik = int(yakalayici.get(cv2.CAP_PROP_FRAME_WIDTH))
    yukseklik = int(yakalayici.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = yakalayici.get(cv2.CAP_PROP_FPS)
    toplam_cerceve = int(yakalayici.get(cv2.CAP_PROP_FRAME_COUNT))

    olcek_x = genislik / GORUNTU_BOYUTU
    olcek_y = yukseklik / GORUNTU_BOYUTU

    print(f"Video: {genislik}x{yukseklik}, FPS: {fps:.1f}, Toplam cerceve: {toplam_cerceve}")

    yazici = None
    if argumanlar.cikti:
        os.makedirs(os.path.dirname(os.path.abspath(argumanlar.cikti)), exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        cikti_yukseklik = yukseklik + 80
        yazici = cv2.VideoWriter(argumanlar.cikti, fourcc, fps, (genislik, cikti_yukseklik))

    cerceve_tamponu = deque(maxlen=HAREKET_CERCEVE_SAYISI)
    onceki_cerceve = None
    cerceve_no = 0
    fps_sayaci = 0
    fps_zamani = time.time()
    gercek_fps = 0.0

    toplam_tespit = 0

    while True:
        basarili, cerceve = yakalayici.read()
        if not basarili:
            break

        cerceve_no += 1
        fps_sayaci += 1

        if time.time() - fps_zamani >= 1.0:
            gercek_fps = fps_sayaci
            fps_sayaci = 0
            fps_zamani = time.time()

        tensor = cerceve_hazirla(cerceve, cihaz)
        cerceve_tamponu.append(tensor)

        if len(cerceve_tamponu) < HAREKET_CERCEVE_SAYISI:
            while len(cerceve_tamponu) < HAREKET_CERCEVE_SAYISI:
                cerceve_tamponu.appendleft(tensor.clone())

        tampon_listesi = list(cerceve_tamponu)

        with torch.no_grad():
            ciktilar = model(tampon_listesi)
            kutular, skorlar, sinif_idleri = model.tahmin_cikart(ciktilar, GORUNTU_BOYUTU)

        kutular_nms, skorlar_nms, siniflar_nms = non_max_suppression(
            kutular[0], skorlar[0], sinif_idleri[0],
            iou_esigi=argumanlar.nms,
            guven_esigi=argumanlar.guven
        )

        sonuc_cerceve = cerceve.copy()
        sonuc_cerceve, tespit_sayisi = kutu_ciz(
            sonuc_cerceve, kutular_nms, skorlar_nms, siniflar_nms, olcek_x, olcek_y
        )
        toplam_tespit += tespit_sayisi

        if argumanlar.hareket:
            hareket_h = hareket_haritasi_olustur(onceki_cerceve, cerceve)
            hareket_kucuk = cv2.resize(hareket_h, (genislik // 4, yukseklik // 4))
            sonuc_cerceve[10:10 + yukseklik // 4, genislik - genislik // 4 - 10:genislik - 10] = hareket_kucuk

        if argumanlar.parlaklik:
            parlaklik_h = parlaklik_haritasi_olustur(cerceve)
            parlaklik_kucuk = cv2.resize(parlaklik_h, (genislik // 4, yukseklik // 4))
            y_baslangic = 10 + (yukseklik // 4 + 10 if argumanlar.hareket else 0)
            sonuc_cerceve[y_baslangic:y_baslangic + yukseklik // 4,
                         genislik - genislik // 4 - 10:genislik - 10] = parlaklik_kucuk

        sonuc_cerceve = bilgi_paneli_ciz(sonuc_cerceve, tespit_sayisi, gercek_fps, cerceve_no)

        if yazici:
            yazici.write(sonuc_cerceve)

        if argumanlar.goster:
            cv2.imshow("Asteroid Tespit", sonuc_cerceve)
            tus = cv2.waitKey(1) & 0xFF
            if tus == ord('q') or tus == 27:
                break

        onceki_cerceve = cerceve.copy()

        if cerceve_no % 100 == 0:
            print(f"Cerceve {cerceve_no}/{toplam_cerceve} - Tespit: {tespit_sayisi}")

    yakalayici.release()
    if yazici:
        yazici.release()
    if argumanlar.goster:
        cv2.destroyAllWindows()

    print(f"\nIslem tamamlandi!")
    print(f"Toplam cerceve: {cerceve_no}")
    print(f"Toplam tespit: {toplam_tespit}")
    if argumanlar.cikti:
        print(f"Cikti kaydedildi: {argumanlar.cikti}")


def goruntulerden_isle(model, goruntu_dosyalari, argumanlar, cihaz):
    print(f"Toplam goruntu: {len(goruntu_dosyalari)}")

    cikti_klasoru = argumanlar.cikti if argumanlar.cikti else os.path.join(CIKTI_YOLU, "tespitler")
    os.makedirs(cikti_klasoru, exist_ok=True)

    cerceve_tamponu = deque(maxlen=HAREKET_CERCEVE_SAYISI)
    onceki_cerceve = None
    toplam_tespit = 0

    for idx, dosya_yolu in enumerate(goruntu_dosyalari):
        cerceve = cv2.imread(dosya_yolu)
        if cerceve is None:
            continue

        yukseklik, genislik = cerceve.shape[:2]
        olcek_x = genislik / GORUNTU_BOYUTU
        olcek_y = yukseklik / GORUNTU_BOYUTU

        tensor = cerceve_hazirla(cerceve, cihaz)
        cerceve_tamponu.append(tensor)

        if len(cerceve_tamponu) < HAREKET_CERCEVE_SAYISI:
            while len(cerceve_tamponu) < HAREKET_CERCEVE_SAYISI:
                cerceve_tamponu.appendleft(tensor.clone())

        tampon_listesi = list(cerceve_tamponu)

        with torch.no_grad():
            ciktilar = model(tampon_listesi)
            kutular, skorlar, sinif_idleri = model.tahmin_cikart(ciktilar, GORUNTU_BOYUTU)

        kutular_nms, skorlar_nms, siniflar_nms = non_max_suppression(
            kutular[0], skorlar[0], sinif_idleri[0],
            iou_esigi=argumanlar.nms,
            guven_esigi=argumanlar.guven
        )

        sonuc_cerceve = cerceve.copy()
        sonuc_cerceve, tespit_sayisi = kutu_ciz(
            sonuc_cerceve, kutular_nms, skorlar_nms, siniflar_nms, olcek_x, olcek_y
        )
        toplam_tespit += tespit_sayisi

        if argumanlar.hareket and onceki_cerceve is not None:
            hareket_h = hareket_haritasi_olustur(onceki_cerceve, cerceve)
            hareket_kucuk = cv2.resize(hareket_h, (genislik // 4, yukseklik // 4))
            sonuc_cerceve[10:10 + yukseklik // 4, genislik - genislik // 4 - 10:genislik - 10] = hareket_kucuk

        sonuc_cerceve = bilgi_paneli_ciz(sonuc_cerceve, tespit_sayisi, 0, idx + 1)

        dosya_adi = os.path.basename(dosya_yolu)
        cikti_yolu = os.path.join(cikti_klasoru, f"tespit_{dosya_adi}")
        cv2.imwrite(cikti_yolu, sonuc_cerceve)

        if argumanlar.goster:
            cv2.imshow("Asteroid Tespit", sonuc_cerceve)
            tus = cv2.waitKey(0) & 0xFF
            if tus == ord('q') or tus == 27:
                break

        onceki_cerceve = cerceve.copy()
        print(f"[{idx + 1}/{len(goruntu_dosyalari)}] {dosya_adi} - Tespit: {tespit_sayisi}")

    if argumanlar.goster:
        cv2.destroyAllWindows()

    print(f"\nIslem tamamlandi!")
    print(f"Toplam goruntu: {len(goruntu_dosyalari)}")
    print(f"Toplam tespit: {toplam_tespit}")
    print(f"Sonuclar kaydedildi: {cikti_klasoru}")


if __name__ == "__main__":
    argumanlar = argumanlari_al()
    videoyu_isle(argumanlar)
