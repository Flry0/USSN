NASA_API_KEY = "DEMO_KEY"

# NOAA SWPC Real-Time Data APIs
NOAA_PLASMA_URL = "https://services.swpc.noaa.gov/products/solar-wind/plasma-1-day.json"
NOAA_MAG_URL = "https://services.swpc.noaa.gov/products/solar-wind/mag-1-day.json"
NOAA_XRAY_URL = "https://services.swpc.noaa.gov/json/goes/primary/xrays-1-day.json"
NOAA_KP_URL = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"

MODEL_KAYIT_YOLU = "trained_model"
VERI_KLASORU = "data"

OZELLIK_SUTUNLARI = [
    "xray_flux",
    "solar_wind_speed",
    "solar_wind_density",
    "solar_wind_temp",
    "bz_gsm",
    "bt_total",
    "kp_index",
    "energetic_protons"
]


HEDEF_SUTUN = "risk_derecesi" 

RANDOM_STATE = 42
TEST_ORANI = 0.2
VARSAYILAN_ORNEK_SAYISI = 10000
