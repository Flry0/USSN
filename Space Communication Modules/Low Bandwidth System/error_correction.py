def generate_fec_parity_block(veri_parcalari):
    if not veri_parcalari:
        return b""
    parity_buffer = bytearray(len(veri_parcalari[0]))
    for parca_chunk in veri_parcalari:
        for index in range(len(parca_chunk)):
            parity_buffer[index] ^= parca_chunk[index]
    return bytes(parity_buffer)

def recover_data_chunk(veri_parcalari, kayip_index, parity_buffer):
    recovered_sonuc = bytearray(len(parity_buffer))
    for index in range(len(parity_buffer)):
        temp_val = parity_buffer[index]
        for idx_j, parca_chunk in enumerate(veri_parcalari):
            if idx_j != kayip_index and parca_chunk:
                temp_val ^= parca_chunk[index]
        recovered_sonuc[index] = temp_val
    return bytes(recovered_sonuc)
