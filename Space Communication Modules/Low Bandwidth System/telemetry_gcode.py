def telemetri_olustur_gcode(x_pos, y_pos, z_pos, hiz, aku_durumu):
    gcode_metni = f"G0 X{x_pos:.3f} Y{y_pos:.3f} Z{z_pos:.3f} F{hiz:.1f} E{aku_durumu:.1f}"
    return gcode_metni.encode('utf-8')

def gcode_cozumle(gcode_bytes):
    gelen_str = gcode_bytes.decode('utf-8')
    split_data = gelen_str.split(' ')
    parsed_sonuc = {}
    for element in split_data:
        if len(element) > 1:
            key_val = element[0]
            if key_val in ['X', 'Y', 'Z', 'F', 'E']:
                parsed_sonuc[key_val] = float(element[1:])
    return parsed_sonuc
