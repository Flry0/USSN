import random

def apply_scintillation_noise(foton_listesi, bulut_yogunlugu):
    etkilenmis_fotonlar = []
    for foton in foton_listesi:
        r_val = random.random()
        if r_val < bulut_yogunlugu:
            etkilenen_foton = {"bit": foton["bit"], "basis": random.choice([0, 1])}
            etkilenmis_fotonlar.append(etkilenen_foton)
        else:
            etkilenmis_fotonlar.append(foton)
    return etkilenmis_fotonlar

def foton_kaybi_simule_et(foton_listesi, atmosferik_zayiflama_orani):
    ulasan_fotonlar = []
    for f_idx, foton in enumerate(foton_listesi):
        s_val = random.random()
        if s_val >= atmosferik_zayiflama_orani:
            ulasan_fotonlar.append((f_idx, foton))
    return ulasan_fotonlar
