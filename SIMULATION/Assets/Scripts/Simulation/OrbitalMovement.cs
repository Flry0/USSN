using UnityEngine;

namespace USSN.Simulation
{
    public class OrbitalMovement : MonoBehaviour
    {
        public Transform yorungeHedefi;
        public float donusHizi = 10f;
        public float kendiDonusHizi = 15f;

        public float yaricap;
        private float mevcutAci;
        private bool uyduMu = false;
        private Vector3 hedefMerkez => yorungeHedefi != null ? yorungeHedefi.position : Vector3.zero;

        void Start()
        {
            SpaceObject uzayNesnesi = GetComponent<SpaceObject>();

            if (uzayNesnesi != null && uzayNesnesi.NesneTipi == SpaceObjectType.Satellite)
            {
                donusHizi = -15f;
                uyduMu = true;
            }

            if (yorungeHedefi == null)
            {
                if (uzayNesnesi != null && uzayNesnesi.NesneTipi == SpaceObjectType.Satellite)
                {
                    GameObject dunya = GameObject.Find("Earth");
                    if (dunya != null) yorungeHedefi = dunya.transform;
                }
                else
                {
                    GameObject gunes = GameObject.Find("UnstableStar");
                    if (gunes != null) yorungeHedefi = gunes.transform;
                }
            }

            if (yaricap <= 0f)
            {
                if (yorungeHedefi != null)
                {
                    yaricap = Vector3.Distance(transform.position, yorungeHedefi.position);
                    Vector3 fark = transform.position - yorungeHedefi.position;
                    mevcutAci = Mathf.Atan2(fark.x, fark.z) * Mathf.Rad2Deg;
                }
                else
                {
                    yaricap = Vector3.Distance(transform.position, Vector3.zero);
                    Vector3 fark = transform.position - Vector3.zero;
                    mevcutAci = Mathf.Atan2(fark.x, fark.z) * Mathf.Rad2Deg;
                }
            }
        }

        public void YaricapiDegistir(float yeniYaricap)
        {
            yaricap = yeniYaricap;
        }

        public void HedefiDegistir(Transform yeniHedef)
        {
            yorungeHedefi = yeniHedef;
            OrbitVisualizer gorsellestirici = GetComponent<OrbitVisualizer>();
            if (gorsellestirici != null) gorsellestirici.merkezHedef = yeniHedef;
        }

        void Update()
        {
            if (yaricap <= 0.001f) return;

            mevcutAci += donusHizi * Time.deltaTime;
            if (mevcutAci > 360f) mevcutAci -= 360f;

            float x = Mathf.Sin(mevcutAci * Mathf.Deg2Rad) * yaricap;
            float z = Mathf.Cos(mevcutAci * Mathf.Deg2Rad) * yaricap;

            transform.position = hedefMerkez + new Vector3(x, 0, z);

            if (uyduMu && yorungeHedefi != null)
            {
                transform.LookAt(yorungeHedefi);
            }
            else
            {
                Vector3 mevcutRotasyon = transform.localEulerAngles;
                mevcutRotasyon.y += kendiDonusHizi * Time.deltaTime;
                transform.localEulerAngles = mevcutRotasyon;
            }
        }
    }
}
