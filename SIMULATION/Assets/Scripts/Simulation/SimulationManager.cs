using System;
using System.Collections.Generic;
using UnityEngine;

namespace USSN.Simulation
{
    [DefaultExecutionOrder(-100)]
    public class SimulationManager : MonoBehaviour
    {
        public static SimulationManager Aktif { get; private set; }

        private Dictionary<string, SpaceObject> _aktifNesneler = new Dictionary<string, SpaceObject>();

        public event Action<SpaceObject> NesneOlusturuldu;
        public event Action<string> NesneSilindi;
        public event Action<SpaceObject, Vector3> NesneTasindi;

        private void Awake()
        {
            if (Aktif == null)
            {
                Aktif = this;
            }
            else
            {
                Destroy(gameObject);
            }
        }

        public void Kaydet(SpaceObject nesne)
        {
            if (!_aktifNesneler.ContainsKey(nesne.Kimlik))
            {
                _aktifNesneler.Add(nesne.Kimlik, nesne);
                Debug.Log($"[Yonetici] Kaydedildi {nesne.NesneTipi}: {nesne.Kimlik}");
                NesneOlusturuldu?.Invoke(nesne);
            }
        }

        public void KaydiSil(string kimlik)
        {
            if (_aktifNesneler.ContainsKey(kimlik))
            {
                _aktifNesneler.Remove(kimlik);
                Debug.Log($"[Yonetici] Kayit silindi: {kimlik}");
                NesneSilindi?.Invoke(kimlik);
            }
        }

        public string Olustur(SpaceObjectType tip, Vector3 konum)
        {
            string prefabAdi = tip switch
            {
                SpaceObjectType.SolarWave => "solar_wave",
                _ => tip.ToString().ToLower()
            };

            GameObject prefab = Resources.Load<GameObject>($"Prefabs/{prefabAdi}");
            if (prefab == null)
            {
                Debug.LogError($"[Yonetici] Prefab yuklenemedi: Resources/Prefabs/{prefabAdi}");
                return null;
            }

            GameObject olusturulan = Instantiate(prefab, konum, Quaternion.identity);

            SpaceObject uzayNesnesi = olusturulan.GetComponent<SpaceObject>();
            if (uzayNesnesi == null)
            {
                uzayNesnesi = olusturulan.AddComponent<SpaceObject>();
            }
            uzayNesnesi.NesneTipi = tip;

            string yeniKimlik = Guid.NewGuid().ToString();
            uzayNesnesi.Kimlik = yeniKimlik;

            if (tip == SpaceObjectType.SolarWave)
            {
                SolarWaveController dalga = olusturulan.GetComponent<SolarWaveController>();
                if (dalga != null)
                {
                    Vector3 hedefYon = UnityEngine.Random.onUnitSphere;
                    GameObject dunya = GameObject.Find("Earth");
                    if (dunya != null)
                    {
                        hedefYon = (dunya.transform.position - konum).normalized;
                    }
                    else if (konum.sqrMagnitude > 0.01f)
                    {
                        hedefYon = konum.normalized;
                    }

                    dalga.PatlayisiBaslat(konum, hedefYon);
                }
            }

            return yeniKimlik;
        }

        public SpaceObject Getir(string kimlik)
        {
            if (_aktifNesneler.TryGetValue(kimlik, out SpaceObject nesne))
            {
                return nesne;
            }

            GameObject sahneNesnesi = GameObject.Find(kimlik);
            if (sahneNesnesi != null)
            {
                SpaceObject uzayNesnesi = sahneNesnesi.GetComponent<SpaceObject>();
                if (uzayNesnesi == null)
                {
                    uzayNesnesi = sahneNesnesi.AddComponent<SpaceObject>();
                    uzayNesnesi.Kimlik = kimlik;
                    uzayNesnesi.NesneTipi = SpaceObjectType.Asteroid;
                }

                if (sahneNesnesi.GetComponent<OrbitalMovement>() == null)
                    sahneNesnesi.AddComponent<OrbitalMovement>();

                if (sahneNesnesi.GetComponent<OrbitVisualizer>() == null)
                    sahneNesnesi.AddComponent<OrbitVisualizer>();

                return uzayNesnesi;
            }

            return null;
        }

        public void Tasi(string kimlik, Vector3 konum)
        {
            SpaceObject nesne = Getir(kimlik);
            if (nesne != null)
            {
                nesne.transform.position = konum;
                NesneTasindi?.Invoke(nesne, konum);
            }
            else
            {
                Debug.LogWarning($"[Yonetici] Tasinamadi, nesne bulunamadi: {kimlik}");
            }
        }

        public void Sil(string kimlik)
        {
            SpaceObject nesne = Getir(kimlik);
            if (nesne != null)
            {
                Destroy(nesne.gameObject);
            }
            else
            {
                Debug.LogWarning($"[Yonetici] Silinemedi, nesne bulunamadi: {kimlik}");
            }
        }

        public float CarpismaRiskiHesapla(string kimlikA, string kimlikB)
        {
            SpaceObject a = Getir(kimlikA);
            SpaceObject b = Getir(kimlikB);

            if (a == null || b == null) return 0f;

            float mesafe = Vector3.Distance(a.transform.position, b.transform.position);
            float risk = Mathf.Clamp01(1f - (mesafe / 100f)) * 100f;
            Debug.Log($"[Yonetici] {kimlikA} ile {kimlikB} arasi risk: %{risk}");
            return risk;
        }
    }
}
