import os
import sys
import time
import torch
import torch.optim as optim
from torch.utils.data import DataLoader
from tqdm import tqdm

from yapilandirma import (
    EGITIM_YOLU, DOGRULAMA_YOLU, MODEL_KAYIT_YOLU, CIKTI_YOLU,
    OGRENME_ORANI, PARTI_BOYUTU, EPOK_SAYISI, AGIRLIK_AZALMASI,
    CIHAZ, ISCI_SAYISI, PIN_BELLEK, GORUNTU_BOYUTU,
    EN_IYI_MODEL_ADI, SON_MODEL_ADI, GUVEN_ESIGI
)
from model import AsteroidAlgilayici
from veri_seti import AsteroidVeriSeti, egitim_donusumu_olustur, dogrulama_donusumu_olustur
from kayip import AsteroidKayipFonksiyonu
from araclar import metrik_hesapla, non_max_suppression


def klasorleri_olustur():
    os.makedirs(MODEL_KAYIT_YOLU, exist_ok=True)
    os.makedirs(CIKTI_YOLU, exist_ok=True)


def veri_yukleyici_olustur(veri_yolu, donusum, karistir=True):
    veri_seti = AsteroidVeriSeti(veri_yolu, donusum=donusum)
    def harmanlama_fonksiyonu(ornekler):
        cerceve_listeleri = []
        hedef_listeleri = []
        for cerceveler, hedefler in ornekler:
            cerceve_listeleri.append(cerceveler)
            hedef_listeleri.append(hedefler)

        parti_cerceveler = []
        cerceve_sayisi = len(cerceve_listeleri[0])
        for cerceve_idx in range(cerceve_sayisi):
            cerceve_partisi = torch.stack([
                cerceve_listeleri[ornek_idx][cerceve_idx]
                for ornek_idx in range(len(cerceve_listeleri))
            ])
            parti_cerceveler.append(cerceve_partisi)

        parti_hedefler = []
        olcek_sayisi = len(hedef_listeleri[0])
        for olcek_idx in range(olcek_sayisi):
            olcek_partisi = torch.stack([
                hedef_listeleri[ornek_idx][olcek_idx]
                for ornek_idx in range(len(hedef_listeleri))
            ])
            parti_hedefler.append(olcek_partisi)

        return parti_cerceveler, parti_hedefler

    yukleyici = DataLoader(
        veri_seti,
        batch_size=PARTI_BOYUTU,
        shuffle=karistir,
        num_workers=ISCI_SAYISI,
        pin_memory=PIN_BELLEK,
        collate_fn=harmanlama_fonksiyonu,
        drop_last=True
    )
    return yukleyici


def bir_epok_egit(model, yukleyici, kayip_fonksiyonu, optimizer, cihaz, epok):
    model.train()
    toplam_kayip = 0.0
    toplam_konum = 0.0
    toplam_nesne = 0.0
    toplam_sinif = 0.0
    parti_sayaci = 0

    ilerleme = tqdm(yukleyici, desc=f"Epok {epok + 1}", leave=True)

    for cerceveler, hedefler in ilerleme:
        cerceveler = [c.to(cihaz) for c in cerceveler]
        hedefler = [h.to(cihaz) for h in hedefler]

        optimizer.zero_grad()
        tahminler = model(cerceveler)
        kayip, konum_k, nesne_k, sinif_k = kayip_fonksiyonu(tahminler, hedefler)

        if torch.isnan(kayip) or torch.isinf(kayip):
            continue

        kayip.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=10.0)
        optimizer.step()

        toplam_kayip += kayip.item()
        toplam_konum += konum_k.item() if isinstance(konum_k, torch.Tensor) else konum_k
        toplam_nesne += nesne_k.item() if isinstance(nesne_k, torch.Tensor) else nesne_k
        toplam_sinif += sinif_k.item() if isinstance(sinif_k, torch.Tensor) else sinif_k
        parti_sayaci += 1

        ilerleme.set_postfix({
            'kayip': f'{kayip.item():.4f}',
            'konum': f'{konum_k.item() if isinstance(konum_k, torch.Tensor) else konum_k:.4f}',
            'nesne': f'{nesne_k.item() if isinstance(nesne_k, torch.Tensor) else nesne_k:.4f}'
        })

    ort_kayip = toplam_kayip / max(parti_sayaci, 1)
    ort_konum = toplam_konum / max(parti_sayaci, 1)
    ort_nesne = toplam_nesne / max(parti_sayaci, 1)
    ort_sinif = toplam_sinif / max(parti_sayaci, 1)

    return ort_kayip, ort_konum, ort_nesne, ort_sinif


@torch.no_grad()
def dogrulama_yap(model, yukleyici, kayip_fonksiyonu, cihaz):
    model.eval()
    toplam_kayip = 0.0
    parti_sayaci = 0

    for cerceveler, hedefler in yukleyici:
        cerceveler = [c.to(cihaz) for c in cerceveler]
        hedefler = [h.to(cihaz) for h in hedefler]

        tahminler = model(cerceveler)
        kayip, _, _, _ = kayip_fonksiyonu(tahminler, hedefler)

        if not (torch.isnan(kayip) or torch.isinf(kayip)):
            toplam_kayip += kayip.item()
            parti_sayaci += 1

    ort_kayip = toplam_kayip / max(parti_sayaci, 1)
    return ort_kayip


def modeli_kaydet(model, optimizer, epok, kayip, dosya_yolu):
    torch.save({
        'epok': epok,
        'model_durumu': model.state_dict(),
        'optimizer_durumu': optimizer.state_dict(),
        'kayip': kayip,
    }, dosya_yolu)


def egitimi_baslat():
    klasorleri_olustur()

    cihaz = torch.device(CIHAZ if torch.cuda.is_available() else "cpu")
    print(f"Kullanilan cihaz: {cihaz}")

    model = AsteroidAlgilayici().to(cihaz)
    toplam_parametre = sum(p.numel() for p in model.parameters())
    egitilen_parametre = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Toplam parametre: {toplam_parametre:,}")
    print(f"Egitilen parametre: {egitilen_parametre:,}")

    kayip_fonksiyonu = AsteroidKayipFonksiyonu().to(cihaz)
    optimizer = optim.AdamW(
        model.parameters(),
        lr=OGRENME_ORANI,
        weight_decay=AGIRLIK_AZALMASI
    )
    zamanlayici = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOK_SAYISI, eta_min=1e-6)

    egitim_donusumu = egitim_donusumu_olustur()
    dogrulama_donusumu = dogrulama_donusumu_olustur()

    egitim_yukleyici = veri_yukleyici_olustur(EGITIM_YOLU, egitim_donusumu, karistir=True)
    dogrulama_yukleyici = veri_yukleyici_olustur(DOGRULAMA_YOLU, dogrulama_donusumu, karistir=False)

    print(f"Egitim veri sayisi: {len(egitim_yukleyici.dataset)}")
    print(f"Dogrulama veri sayisi: {len(dogrulama_yukleyici.dataset)}")

    if len(egitim_yukleyici.dataset) == 0:
        print("HATA: Egitim verisi bulunamadi!")
        print(f"Lutfen {EGITIM_YOLU} klasorune goruntuler ve etiketler ekleyin.")
        print(f"Goruntuler: {EGITIM_YOLU}/goruntuler/")
        print(f"Etiketler: {EGITIM_YOLU}/etiketler/")
        sys.exit(1)

    en_iyi_kayip = float('inf')
    kayip_gecmisi = {
        'egitim_kaybi': [],
        'dogrulama_kaybi': [],
        'ogrenme_orani': []
    }

    print(f"\nEgitim basliyor - {EPOK_SAYISI} epok")
    print("=" * 60)

    for epok in range(EPOK_SAYISI):
        baslangic = time.time()

        ort_kayip, ort_konum, ort_nesne, ort_sinif = bir_epok_egit(
            model, egitim_yukleyici, kayip_fonksiyonu, optimizer, cihaz, epok
        )

        dogrulama_kaybi = 0.0
        if len(dogrulama_yukleyici.dataset) > 0:
            dogrulama_kaybi = dogrulama_yap(
                model, dogrulama_yukleyici, kayip_fonksiyonu, cihaz
            )

        zamanlayici.step()
        mevcut_lr = optimizer.param_groups[0]['lr']

        kayip_gecmisi['egitim_kaybi'].append(ort_kayip)
        kayip_gecmisi['dogrulama_kaybi'].append(dogrulama_kaybi)
        kayip_gecmisi['ogrenme_orani'].append(mevcut_lr)

        sure = time.time() - baslangic

        print(f"\nEpok [{epok + 1}/{EPOK_SAYISI}] - Sure: {sure:.1f}s")
        print(f"  Egitim Kaybi: {ort_kayip:.4f} (Konum: {ort_konum:.4f}, Nesne: {ort_nesne:.4f}, Sinif: {ort_sinif:.4f})")
        print(f"  Dogrulama Kaybi: {dogrulama_kaybi:.4f}")
        print(f"  Ogrenme Orani: {mevcut_lr:.6f}")

        modeli_kaydet(
            model, optimizer, epok, ort_kayip,
            os.path.join(MODEL_KAYIT_YOLU, SON_MODEL_ADI)
        )

        if dogrulama_kaybi < en_iyi_kayip and dogrulama_kaybi > 0:
            en_iyi_kayip = dogrulama_kaybi
            modeli_kaydet(
                model, optimizer, epok, dogrulama_kaybi,
                os.path.join(MODEL_KAYIT_YOLU, EN_IYI_MODEL_ADI)
            )
            print(f"  >>> En iyi model kaydedildi! (Kayip: {en_iyi_kayip:.4f})")

    print("\n" + "=" * 60)
    print("Egitim tamamlandi!")
    print(f"En iyi dogrulama kaybi: {en_iyi_kayip:.4f}")

    grafik_ciz(kayip_gecmisi)


def grafik_ciz(kayip_gecmisi):
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        sekil, eksenler = plt.subplots(1, 2, figsize=(14, 5))

        eksenler[0].plot(kayip_gecmisi['egitim_kaybi'], label='Egitim', color='#FF6B6B', linewidth=2)
        eksenler[0].plot(kayip_gecmisi['dogrulama_kaybi'], label='Dogrulama', color='#4ECDC4', linewidth=2)
        eksenler[0].set_title('Kayip Grafigi', fontsize=14)
        eksenler[0].set_xlabel('Epok')
        eksenler[0].set_ylabel('Kayip')
        eksenler[0].legend()
        eksenler[0].grid(True, alpha=0.3)

        eksenler[1].plot(kayip_gecmisi['ogrenme_orani'], color='#FFD93D', linewidth=2)
        eksenler[1].set_title('Ogrenme Orani', fontsize=14)
        eksenler[1].set_xlabel('Epok')
        eksenler[1].set_ylabel('LR')
        eksenler[1].grid(True, alpha=0.3)

        plt.tight_layout()
        grafik_yolu = os.path.join(CIKTI_YOLU, 'egitim_grafigi.png')
        plt.savefig(grafik_yolu, dpi=150)
        plt.close()
        print(f"Egitim grafigi kaydedildi: {grafik_yolu}")
    except Exception as hata:
        print(f"Grafik cizilemedi: {hata}")


if __name__ == "__main__":
    egitimi_baslat()
