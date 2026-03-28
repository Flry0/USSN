using UnityEngine;
using UnityEngine.UI;
using USSN.Simulation;

namespace USSN.Simulation
{
    public class ObjectDetectorUI : MonoBehaviour
    {
        public Color kutuRengi = new Color(0.83f, 0.84f, 0f, 1f);
        public float tabanBosluk = 0.5f;

        private RectTransform tuvalAlani;
        private Image cerceveCizimi;
        private Image baslikCubugu;
        private Text etiketYazisi;

        private float sonrakiGuncellemeZamani = 0f;
        private float guncelGuvenilirlik = 0.83f;

        void Start()
        {
            ArayuzKur();
        }

        void ArayuzKur()
        {
            GameObject tuvalObj = new GameObject("AI_Detector_Canvas");
            tuvalObj.transform.SetParent(transform);
            tuvalObj.transform.localPosition = new Vector3(0, 0, -0.2f);
            tuvalObj.layer = 0;

            Canvas tuval = tuvalObj.AddComponent<Canvas>();
            tuval.renderMode = RenderMode.WorldSpace;
            tuval.worldCamera = Camera.main;

            tuvalAlani = tuvalObj.GetComponent<RectTransform>();
            tuvalAlani.sizeDelta = new Vector2(1000, 1000);

            Color temaRengi = NesneRenginiAl();

            GameObject arkaplanObj = new GameObject("HUD_BG");
            arkaplanObj.transform.SetParent(tuvalObj.transform, false);
            arkaplanObj.layer = 0;
            Image arkaplanImg = arkaplanObj.AddComponent<Image>();
            arkaplanImg.color = new Color(0, 0, 0, 0.15f);
            arkaplanImg.rectTransform.anchorMin = Vector2.zero;
            arkaplanImg.rectTransform.anchorMax = Vector2.one;
            arkaplanImg.rectTransform.sizeDelta = Vector2.zero;
            arkaplanImg.rectTransform.anchoredPosition = Vector2.zero;

            float kalinlik = 30f;
            CerceveOlustur("Sol", tuvalObj.transform, new Vector2(0, 0), new Vector2(0, 1), new Vector2(kalinlik, 0), temaRengi);
            CerceveOlustur("Sag", tuvalObj.transform, new Vector2(1, 0), new Vector2(1, 1), new Vector2(kalinlik, 0), temaRengi);
            CerceveOlustur("Ust", tuvalObj.transform, new Vector2(0, 1), new Vector2(1, 1), new Vector2(0, kalinlik), temaRengi);
            CerceveOlustur("Alt", tuvalObj.transform, new Vector2(0, 0), new Vector2(1, 0), new Vector2(0, kalinlik), temaRengi);

            GameObject baslikObj = new GameObject("BaslikBar");
            baslikObj.transform.SetParent(tuvalObj.transform, false);
            baslikObj.layer = 0;
            baslikCubugu = baslikObj.AddComponent<Image>();
            baslikCubugu.color = temaRengi;

            RectTransform baslikRect = baslikObj.GetComponent<RectTransform>();
            baslikRect.anchorMin = new Vector2(0, 1);
            baslikRect.anchorMax = new Vector2(1, 1);
            baslikRect.pivot = new Vector2(0.5f, 0);
            baslikRect.anchoredPosition = new Vector2(0, kalinlik);
            baslikRect.sizeDelta = new Vector2(0, 300f);

            GameObject yaziObj = new GameObject("BaslikYazi");
            yaziObj.transform.SetParent(baslikObj.transform, false);
            yaziObj.layer = 0;

            etiketYazisi = yaziObj.AddComponent<Text>();

            Font yazi = null;
            try { yazi = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf"); } catch { }

            if (yazi == null)
            {
                Font[] tumYazilar = Resources.FindObjectsOfTypeAll<Font>();
                if (tumYazilar.Length > 0) yazi = tumYazilar[0];
            }
            if (yazi != null) etiketYazisi.font = yazi;

            etiketYazisi.fontSize = 140;
            etiketYazisi.resizeTextForBestFit = false;
            etiketYazisi.fontStyle = FontStyle.Bold;
            etiketYazisi.color = Color.white;
            etiketYazisi.alignment = TextAnchor.MiddleCenter;
            etiketYazisi.horizontalOverflow = HorizontalWrapMode.Overflow;
            etiketYazisi.verticalOverflow = VerticalWrapMode.Overflow;

            RectTransform yaziRect = yaziObj.GetComponent<RectTransform>();
            yaziRect.anchorMin = Vector2.zero;
            yaziRect.anchorMax = Vector2.one;
            yaziRect.sizeDelta = Vector2.zero;
            yaziRect.anchoredPosition = Vector2.zero;

            YaziGuncelle();
        }

        void CerceveOlustur(string isim, Transform ebeveyn, Vector2 minAnchor, Vector2 maxAnchor, Vector2 boyut, Color renk)
        {
            GameObject cizgiObj = new GameObject(isim);
            cizgiObj.transform.SetParent(ebeveyn, false);
            cizgiObj.layer = 0;
            Image gorsel = cizgiObj.AddComponent<Image>();
            gorsel.color = renk;
            RectTransform rt = cizgiObj.GetComponent<RectTransform>();
            rt.anchorMin = minAnchor;
            rt.anchorMax = maxAnchor;
            rt.sizeDelta = boyut;
            rt.anchoredPosition = Vector2.zero;
        }

        Color NesneRenginiAl()
        {
            SpaceObject uzayNesnesi = GetComponent<SpaceObject>();
            if (uzayNesnesi != null)
            {
                if (uzayNesnesi.NesneTipi == SpaceObjectType.Asteroid) return new Color(1f, 0.2f, 0.2f, 1f);
                if (uzayNesnesi.NesneTipi == SpaceObjectType.Satellite) return new Color(0.2f, 0.7f, 1f, 1f);
                if (uzayNesnesi.NesneTipi == SpaceObjectType.SolarWave) return new Color(1f, 0.6f, 0f, 1f);
                if (uzayNesnesi.NesneTipi == SpaceObjectType.Debris) return new Color(0.7f, 0.7f, 0.7f, 1f);
            }
            return kutuRengi;
        }

        void Update()
        {
            if (Camera.main != null && tuvalAlani != null)
            {
                tuvalAlani.LookAt(tuvalAlani.position + Camera.main.transform.rotation * Vector3.forward,
                                  Camera.main.transform.rotation * Vector3.up);
            }

            ArayuzBoyutGuncelle();

            if (Time.time > sonrakiGuncellemeZamani)
            {
                guncelGuvenilirlik = Mathf.Clamp(guncelGuvenilirlik + Random.Range(-0.05f, 0.05f), 0.80f, 0.99f);
                YaziGuncelle();
                sonrakiGuncellemeZamani = Time.time + 0.1f;
            }
        }

        void ArayuzBoyutGuncelle()
        {
            float enBuyukBoyut = 5f;
            MeshRenderer mr = GetComponentInChildren<MeshRenderer>();
            if (mr != null)
            {
                Vector3 boyut = mr.bounds.size;
                enBuyukBoyut = Mathf.Max(boyut.x, Mathf.Max(boyut.y, boyut.z)) * 1.5f + tabanBosluk;
            }
            else
            {
                enBuyukBoyut = 8f;
            }

            Vector3 ebeveynOlcek = transform.lossyScale;
            float hedefDunyaOlcegi = enBuyukBoyut / 1000f;

            float sx = ebeveynOlcek.x != 0 ? hedefDunyaOlcegi / ebeveynOlcek.x : hedefDunyaOlcegi;
            float sy = ebeveynOlcek.y != 0 ? hedefDunyaOlcegi / ebeveynOlcek.y : hedefDunyaOlcegi;
            float sz = ebeveynOlcek.z != 0 ? hedefDunyaOlcegi / ebeveynOlcek.z : hedefDunyaOlcegi;

            tuvalAlani.localScale = new Vector3(sx, sy, sz);
        }

        void YaziGuncelle()
        {
            SpaceObject uzayNesnesi = GetComponent<SpaceObject>();
            string tipAdi = uzayNesnesi != null ? uzayNesnesi.NesneTipi.ToString().ToLower() : "bilinmeyen";
            etiketYazisi.text = $" {tipAdi} {guncelGuvenilirlik:F2}";
        }
    }
}
