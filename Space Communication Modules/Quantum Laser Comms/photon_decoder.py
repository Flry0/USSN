import random

def measure_photons(ulasan_foton_tuple_list, alici_basis_listesi):
    olcum_uydusu_verileri = []
    for f_idx, foton_obj in ulasan_foton_tuple_list:
        alici_basis = alici_basis_listesi[f_idx]
        if foton_obj["basis"] == alici_basis:
            olculen_bit_degeri = foton_obj["bit"]
        else:
            olculen_bit_degeri = random.choice([0, 1])
            
        kayit = {"f_idx": f_idx, "bit": olculen_bit_degeri, "basis": alici_basis}
        olcum_uydusu_verileri.append(kayit)
        
    return olcum_uydusu_verileri

def sift_quantum_keys(gonderici_basis_list, alici_olcum_listesi):
    ortak_anahtar = []
    for olcum in alici_olcum_listesi:
        idx_val = olcum["f_idx"]
        g_basis = gonderici_basis_list[idx_val]
        a_basis = olcum["basis"]
        
        if g_basis == a_basis:
            ortak_anahtar.append(olcum["bit"])
            
    return ortak_anahtar
