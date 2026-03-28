import numpy as np
import pandas as pd
import joblib
import os
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import config


class CarpismaTahminModeli:

    def __init__(self, model_tipi="gradient_boosting", **ekstra_parametreler):
        self.model_tipi = model_tipi
        self.scaler = RobustScaler()
        self.ozellik_isimleri = None
        self.egitildi_mi = False

        varsayilan_gb_params = {
            "n_estimators": 500,
            "max_depth": 6,
            "learning_rate": 0.05,
            "subsample": 0.8,
            "min_samples_split": 10,
            "min_samples_leaf": 5,
            "random_state": config.RANDOM_STATE,
            "loss": "huber",
        }

        varsayilan_rf_params = {
            "n_estimators": 300,
            "max_depth": 12,
            "min_samples_split": 5,
            "min_samples_leaf": 3,
            "random_state": config.RANDOM_STATE,
            "n_jobs": -1,
        }

        if model_tipi == "gradient_boosting":
            kullanilacak_params = {**varsayilan_gb_params, **ekstra_parametreler}
            self.model = GradientBoostingRegressor(**kullanilacak_params)
        elif model_tipi == "random_forest":
            kullanilacak_params = {**varsayilan_rf_params, **ekstra_parametreler}
            self.model = RandomForestRegressor(**kullanilacak_params)
        else:
            raise ValueError(f"Bilinmeyen model tipi: {model_tipi}")

    def ozellikleri_hazirla(self, df):
        mevcut_ozellikler = [s for s in config.OZELLIK_SUTUNLARI if s in df.columns]

        if not mevcut_ozellikler:
            raise ValueError("Hicbir ozellik sutunu bulunamadi")

        X = df[mevcut_ozellikler].copy()
        X = X.replace([np.inf, -np.inf], np.nan)
        X = X.fillna(0)

        self.ozellik_isimleri = mevcut_ozellikler
        return X

    def egit(self, X, y):
        X_olcekli = self.scaler.fit_transform(X)
        y_log = np.log1p(np.abs(y))

        self.model.fit(X_olcekli, y_log)
        self.egitildi_mi = True

        tahminler = self.model.predict(X_olcekli)
        egitim_mse = mean_squared_error(y_log, tahminler)
        egitim_r2 = r2_score(y_log, tahminler)

        return {
            "egitim_mse": egitim_mse,
            "egitim_rmse": np.sqrt(egitim_mse),
            "egitim_r2": egitim_r2,
        }

    def capraz_dogrula(self, X, y, katlanma_sayisi=5):
        X_olcekli = self.scaler.fit_transform(X)
        y_log = np.log1p(np.abs(y))

        skorlar = cross_val_score(
            self.model, X_olcekli, y_log,
            cv=katlanma_sayisi,
            scoring="neg_mean_squared_error"
        )

        return {
            "ortalama_mse": -skorlar.mean(),
            "std_mse": skorlar.std(),
            "ortalama_rmse": np.sqrt(-skorlar.mean()),
            "tum_skorlar": -skorlar,
        }

    def tahmin_et(self, X):
        if not self.egitildi_mi:
            raise RuntimeError("Model henuz egitilmedi")

        X_olcekli = self.scaler.transform(X)
        log_tahmin = self.model.predict(X_olcekli)
        gercek_tahmin = np.expm1(log_tahmin)

        return np.clip(gercek_tahmin, 0, 1)

    def onem_siralamasini_al(self):
        if not self.egitildi_mi:
            raise RuntimeError("Model henuz egitilmedi")

        if hasattr(self.model, "feature_importances_"):
            onemler = self.model.feature_importances_
            onem_df = pd.DataFrame({
                "ozellik": self.ozellik_isimleri,
                "onem_degeri": onemler,
            })
            onem_df = onem_df.sort_values("onem_degeri", ascending=False)
            return onem_df

        return None

    def degerlendirme_raporu(self, X_test, y_test):
        tahminler = self.tahmin_et(X_test)
        y_gercek = np.array(y_test)

        mse = mean_squared_error(y_gercek, tahminler)
        mae = mean_absolute_error(y_gercek, tahminler)
        rmse = np.sqrt(mse)

        y_log_gercek = np.log1p(np.abs(y_gercek))
        y_log_tahmin = np.log1p(np.abs(tahminler))
        r2 = r2_score(y_log_gercek, y_log_tahmin)

        rapor = {
            "mse": mse,
            "rmse": rmse,
            "mae": mae,
            "r2_log_scale": r2,
            "tahmin_sayisi": len(tahminler),
            "ortalama_tahmin": float(np.mean(tahminler)),
            "max_tahmin": float(np.max(tahminler)),
            "min_tahmin": float(np.min(tahminler)),
        }

        return rapor

    def kaydet(self, klasor_yolu=None):
        if klasor_yolu is None:
            klasor_yolu = config.MODEL_KAYIT_YOLU

        os.makedirs(klasor_yolu, exist_ok=True)

        model_dosyasi = os.path.join(klasor_yolu, "carpma_modeli.joblib")
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

        model_dosyasi = os.path.join(klasor_yolu, "carpma_modeli.joblib")
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


class CokluModelToplulugu:

    def __init__(self):
        self.modeller = {}
        self.agirliklar = {}

    def model_ekle(self, isim, model, agirlik=1.0):
        self.modeller[isim] = model
        self.agirliklar[isim] = agirlik

    def toplu_tahmin(self, X):
        tum_tahminler = []
        toplam_agirlik = sum(self.agirliklar.values())

        for isim, model in self.modeller.items():
            tahmin = model.tahmin_et(X)
            agirlik = self.agirliklar[isim] / toplam_agirlik
            tum_tahminler.append(tahmin * agirlik)

        birlesik_tahmin = np.sum(tum_tahminler, axis=0)
        return np.clip(birlesik_tahmin, 0, 1)

    def kaydet(self, klasor_yolu=None):
        if klasor_yolu is None:
            klasor_yolu = os.path.join(config.MODEL_KAYIT_YOLU, "topluluk")

        os.makedirs(klasor_yolu, exist_ok=True)

        for isim, model in self.modeller.items():
            model_klasoru = os.path.join(klasor_yolu, isim)
            model.kaydet(model_klasoru)

        joblib.dump(self.agirliklar, os.path.join(klasor_yolu, "agirliklar.joblib"))

    @classmethod
    def yukle(cls, klasor_yolu=None):
        if klasor_yolu is None:
            klasor_yolu = os.path.join(config.MODEL_KAYIT_YOLU, "topluluk")

        instance = cls()
        instance.agirliklar = joblib.load(os.path.join(klasor_yolu, "agirliklar.joblib"))

        for isim in instance.agirliklar:
            model_klasoru = os.path.join(klasor_yolu, isim)
            instance.modeller[isim] = CarpismaTahminModeli.yukle(model_klasoru)

        return instance
