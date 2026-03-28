import random
import config

def generate_random_bits(uzunluk_miktari):
    return [random.choice([0, 1]) for _ in range(uzunluk_miktari)]

def generate_random_bases(uzunluk_miktari):
    return [random.choice([config.BASIS_RECTILINEAR, config.BASIS_DIAGONAL]) for _ in range(uzunluk_miktari)]

def create_photon_stream(bit_dizisi, basis_dizisi):
    foton_akisi = []
    for b_val, bas_val in zip(bit_dizisi, basis_dizisi):
        foton = {"bit": b_val, "basis": bas_val}
        foton_akisi.append(foton)
    return foton_akisi
