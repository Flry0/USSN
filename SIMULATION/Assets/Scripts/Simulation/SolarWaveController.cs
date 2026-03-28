using UnityEngine;
using System.Collections.Generic;

namespace USSN.Simulation
{
    [RequireComponent(typeof(LineRenderer))]
    public class SolarWaveController : MonoBehaviour
    {
        public float patlamaSuresi = 4.0f;
        public float maksimumGenislik = 25.0f;
        public int noktaSayisi = 30;
        public float kemerYuksekligi = 15.0f;

        private LineRenderer cizgiCizici;
        private Vector3 baslangicNoktasi;
        private Vector3 hedefNoktasi;
        private float baslangicZamani;
        private bool baslatildiMi = false;

        void Awake()
        {
            cizgiCizici = GetComponent<LineRenderer>();
            CizgiAyarla();
        }

        void CizgiAyarla()
        {
            cizgiCizici.positionCount = noktaSayisi;
            cizgiCizici.widthMultiplier = 0f;
            cizgiCizici.useWorldSpace = true;

            Shader parlakShader = Shader.Find("USSN/SolarFlare");
            if (parlakShader == null) parlakShader = Shader.Find("Legacy Shaders/Particles/Additive");
            if (parlakShader == null) parlakShader = Shader.Find("Sprites/Default");

            cizgiCizici.material = new Material(parlakShader);
            cizgiCizici.material.color = new Color(1f, 0.5f, 0.1f, 1f);

            Gradient renk = new Gradient();
            renk.SetKeys(
                new GradientColorKey[] { new GradientColorKey(Color.white, 0f), new GradientColorKey(new Color(1f, 0.4f, 0f), 0.3f), new GradientColorKey(Color.red, 0.7f), new GradientColorKey(new Color(0.1f, 0.8f, 1f), 1f) },
                new GradientAlphaKey[] { new GradientAlphaKey(0.4f, 0f), new GradientAlphaKey(1f, 0.2f), new GradientAlphaKey(1f, 0.8f), new GradientAlphaKey(0.4f, 1f) }
            );
            cizgiCizici.colorGradient = renk;
        }

        public void PatlayisiBaslat(Vector3 kaynak, Vector3 yon)
        {
            baslangicNoktasi = kaynak;
            hedefNoktasi = kaynak + yon * 50f + Random.insideUnitSphere * 15f;

            baslangicZamani = Time.time;
            baslatildiMi = true;

            YolOlustur();
            Destroy(gameObject, patlamaSuresi);
        }

        void YolOlustur()
        {
            Vector3 ortaNokta = (baslangicNoktasi + hedefNoktasi) * 0.5f + (Random.onUnitSphere * kemerYuksekligi);

            for (int i = 0; i < noktaSayisi; i++)
            {
                float t = i / (float)(noktaSayisi - 1);
                Vector3 m1 = Vector3.Lerp(baslangicNoktasi, ortaNokta, t);
                Vector3 m2 = Vector3.Lerp(ortaNokta, hedefNoktasi, t);
                cizgiCizici.SetPosition(i, Vector3.Lerp(m1, m2, t));
            }
        }

        void Update()
        {
            if (!baslatildiMi) return;

            float gecenSure = Time.time - baslangicZamani;
            float ilerleme = gecenSure / patlamaSuresi;

            float genislik = Mathf.Sin(ilerleme * Mathf.PI) * maksimumGenislik;
            cizgiCizici.widthMultiplier = genislik;
        }
    }
}
