import numpy as np

def calculate_frame_delta(current_frame, last_frame_data, threshold_delta):
    fark_matrisi = np.abs(current_frame.astype(int) - last_frame_data.astype(int))
    degisim_maskesi = fark_matrisi > threshold_delta
    
    row_indices, col_indices = np.where(degisim_maskesi)
    piksel_degerleri = current_frame[degisim_maskesi]
    
    compressed_payload = {
        "r_idx": row_indices.tolist(),
        "c_idx": col_indices.tolist(),
        "vals": piksel_degerleri.tolist()
    }
    return compressed_payload

def reconstruct_frame(last_frame_data, compressed_payload):
    yeni_goruntu_frame = np.copy(last_frame_data)
    if len(compressed_payload["vals"]) > 0:
        rows = compressed_payload["r_idx"]
        cols = compressed_payload["c_idx"]
        yeni_goruntu_frame[rows, cols] = compressed_payload["vals"]
    return yeni_goruntu_frame
