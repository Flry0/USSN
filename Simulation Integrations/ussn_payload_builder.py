import config_sim

def build_spawn_komutu(obje_tipi, x_pos, y_pos, z_pos):
    json_taslagi = {
        "action": config_sim.ACTION_SPAWN,
        "type": obje_tipi,
        "x": float(x_pos),
        "y": float(y_pos),
        "z": float(z_pos)
    }
    return json_taslagi

def build_update_komutu(hedef_id, degisen_parametreler_dict):
    json_taslagi = {
        "action": config_sim.ACTION_UPDATE,
        "id": hedef_id
    }
    for anahtar_kelime, deger_value in degisen_parametreler_dict.items():
        json_taslagi[anahtar_kelime] = deger_value
    return json_taslagi

def build_delete_komutu(silinecek_isim):
    json_taslagi = {
        "action": config_sim.ACTION_DELETE,
        "id": silinecek_isim
    }
    return json_taslagi
