import numpy as np
import pandas as pd
import joblib
import os
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score, classification_report
import config


class UzayYoluTahminModeli:

    def __init__(self, model_tipi="random_forest", **ekstra_parametreler):
        self.model_tipi = model_tipi
        self.scaler = StandardScaler()
        self.ozellik_isimleri = None
        self.egitildi_mi = False

        varsayilan_gb_params = {
            "n_estimators": 200,
            "max_depth": 5,
            "learning_rate": 0.1,
            "random_state": config.RANDOM_STATE
        }

        varsayilan_rf_params = {
            "n_estimators": 200,
            "max_depth": 10,
            "min_samples_split": 5,
            "min_samples_leaf": 2,
            "random_state": config.RANDOM_STATE,
            "n_jobs": -1,
        }

        if model_tipi == "gradient_boosting":
            kullanilacak_params = {**varsayilan_gb_params, **ekstra_parametreler}
            self.model = GradientBoostingClassifier(**kullanilacak_params)
        elif model_tipi == "random_forest":
            kullanilacak_params = {**varsayilan_rf_params, **ekstra_parametreler}
            self.model = RandomForestClassifier(**kullanilacak_params)
        else:
            raise ValueError(f"Bilinmeyen model tipi: {model_tipi}")

    def ozellikleri_hazirla(self, df):
        mevcut_ozellikler = [s for s in config.OZELLIK_SUTUNLARI if s in df.columns]

        if "log_xray_flux" in df.columns and "log_xray_flux" not in mevcut_ozellikler:
            mevcut_ozellikler.append("log_xray_flux")
        if "flare_class_code" in df.columns and "flare_class_code" not in mevcut_ozellikler:
            mevcut_ozellikler.append("flare_class_code")
        if "dynamic_pressure_npa" in df.columns and "dynamic_pressure_npa" not in mevcut_ozellikler:
            mevcut_ozellikler.append("dynamic_pressure_npa")
        if "reconnection_rate" in df.columns and "reconnection_rate" not in mevcut_ozellikler:
            mevcut_ozellikler.append("reconnection_rate")

        if not mevcut_ozellikler:
            raise ValueError("Hicbir ozellik sutunu bulunamadi")

        X = df[mevcut_ozellikler].copy()
        X = X.replace([np.inf, -np.inf], np.nan)
        X = X.fillna(0)

        self.ozellik_isimleri = mevcut_ozellikler
        return X

    def egit(self, X, y):
        X_olcekli = self.scaler.fit_transform(X)

        self.model.fit(X_olcekli, y)
        self.egitildi_mi = True

        tahminler = self.model.predict(X_olcekli)
        dogruluk = accuracy_score(y, tahminler)

        return {
            "egitim_dogruluk": dogruluk
        }

    def capraz_dogrula(self, X, y, katlanma_sayisi=5):
        X_olcekli = self.scaler.fit_transform(X)

        skorlar = cross_val_score(
            self.model, X_olcekli, y,
            cv=katlanma_sayisi,
            scoring="accuracy"
        )

        return {
            "ortalama_dogruluk": skorlar.mean(),
            "std_dogruluk": skorlar.std()
        }

    def tahmin_et(self, X):
        if not self.egitildi_mi:
            raise RuntimeError("Model henuz egitilmedi")

        X_olcekli = self.scaler.transform(X)
        tahmin_sinifi = self.model.predict(X_olcekli)
        tahmin_olasiliklari = self.model.predict_proba(X_olcekli)

        return tahmin_sinifi, tahmin_olasiliklari

    def degerlendirme_raporu(self, X_test, y_test):
        tahminler, _ = self.tahmin_et(X_test)
        acc = accuracy_score(y_test, tahminler)
        rapor_str = classification_report(y_test, tahminler)

        rapor = {
            "dogruluk": acc,
            "rapor_metin": rapor_str
        }

        return rapor

    def kaydet(self, klasor_yolu=None):
        if klasor_yolu is None:
            klasor_yolu = config.MODEL_KAYIT_YOLU

        os.makedirs(klasor_yolu, exist_ok=True)

        model_dosyasi = os.path.join(klasor_yolu, "storm_class_model.joblib")
        scaler_dosyasi = os.path.join(klasor_yolu, "scaler.joblib")
        meta_dosyasi = os.path.join(klasor_yolu, "model_meta.joblib")

        joblib.dump(self.model, model_dosyasi)
        joblib.dump(self.scaler, scaler_dosyasi)
        joblib.dump({
            "model_tipi": self.model_tipi,
            "ozellik_isimleri": self.ozellik_isimleri,
            "egitildi_mi": self.egitildi_mi,
        }, meta_dosyasi)

        return klasor_yolu

    @classmethod
    def yukle(cls, klasor_yolu=None):
        if klasor_yolu is None:
            klasor_yolu = config.MODEL_KAYIT_YOLU

        model_dosyasi = os.path.join(klasor_yolu, "storm_class_model.joblib")
        scaler_dosyasi = os.path.join(klasor_yolu, "scaler.joblib")
        meta_dosyasi = os.path.join(klasor_yolu, "model_meta.joblib")

        meta = joblib.load(meta_dosyasi)

        instance = cls.__new__(cls)
        instance.model = joblib.load(model_dosyasi)
        instance.scaler = joblib.load(scaler_dosyasi)
        instance.model_tipi = meta["model_tipi"]
        instance.ozellik_isimleri = meta["ozellik_isimleri"]
        instance.egitildi_mi = meta["egitildi_mi"]

        return instance
