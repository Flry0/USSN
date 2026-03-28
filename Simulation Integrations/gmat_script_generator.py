import os
import config_sim

def generate_gmat_orbit_script(uydu_id_ismi, radius_mesafesi, speed_hizi):
    script_icerigi = f"""
Create Spacecraft {uydu_id_ismi};
GMAT {uydu_id_ismi}.DateFormat = UTCGregorian;
GMAT {uydu_id_ismi}.Epoch = '01 Jan 2026 12:00:00.000';
GMAT {uydu_id_ismi}.SMA = {radius_mesafesi + 6371.0};
GMAT {uydu_id_ismi}.ECC = 0.0001;
GMAT {uydu_id_ismi}.INC = 98.0;

Create ForceModel KusursuzDunyaGucu;
GMAT KusursuzDunyaGucu.CentralBody = Earth;
GMAT KusursuzDunyaGucu.PrimaryBodies = {{Earth}};

Create Propagator DefaultProp;
GMAT DefaultProp.FM = KusursuzDunyaGucu;
GMAT DefaultProp.Type = RungeKutta89;

BeginMissionSequence;
Propagate DefaultProp({uydu_id_ismi}) {{12000.0}};
"""
    hedef_klasor = config_sim.GMAT_OUTPUT_DIR
    if not os.path.exists(hedef_klasor):
        os.makedirs(hedef_klasor, exist_ok=True)
        
    dosya_dizini = os.path.join(hedef_klasor, f"Yorunge_{uydu_id_ismi}.script")
    with open(dosya_dizini, "w", encoding="utf-8") as dosya_nesnesi:
        dosya_nesnesi.write(script_icerigi.strip())
        
    return dosya_dizini
