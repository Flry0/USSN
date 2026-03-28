def optimize_burn_route(mevcut_yakit, required_thrust_list):
    optimize_edilen_hareket = []
    kalan_capasite = mevcut_yakit
    
    for thrust_val in required_thrust_list:
        if abs(thrust_val) > kalan_capasite:
            yakilan_deger = (thrust_val / abs(thrust_val)) * kalan_capasite if thrust_val != 0 else 0
        else:
            yakilan_deger = thrust_val
            
        optimize_edilen_hareket.append(yakilan_deger)
        kalan_capasite -= abs(yakilan_deger)
        
    return optimize_edilen_hareket

def calculate_fleet_efficiency(uydu_obj_listesi):
    total_harcanan = 0.0
    for s_obj in uydu_obj_listesi:
        total_harcanan += (100.0 - s_obj.kalan_yakit)
    return total_harcanan
