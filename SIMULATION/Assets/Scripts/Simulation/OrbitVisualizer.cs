using UnityEngine;
using USSN.Simulation;

[RequireComponent(typeof(LineRenderer))]
public class OrbitVisualizer : MonoBehaviour
{
    public int segmentSayisi = 128;
    public float cizgiKalinligi = 0.05f;
    public Transform merkezHedef;
    private Color yorungeRengi = new Color(1f, 1f, 1f, 0.4f);

    private LineRenderer cizgi;

    void Start()
    {
        cizgi = GetComponent<LineRenderer>();
        cizgi.positionCount = segmentSayisi + 1;
        cizgi.useWorldSpace = true;
        cizgi.startWidth = 0.02f;
        cizgi.endWidth = 0.02f;

        Material cizgiMateryali = new Material(Shader.Find("Sprites/Default"));
        cizgi.material = cizgiMateryali;

        OrbitalMovement hareket = GetComponent<OrbitalMovement>();
        if (hareket != null && hareket.yorungeHedefi != null)
        {
            merkezHedef = hareket.yorungeHedefi;
        }
        else
        {
            SpaceObject uzayNesnesi = GetComponent<SpaceObject>();
            if (uzayNesnesi != null)
            {
                if (uzayNesnesi.NesneTipi == SpaceObjectType.Satellite)
                {
                    yorungeRengi = new Color(0.1f, 0.7f, 1f, 0.5f);
                    GameObject dunya = GameObject.Find("Earth");
                    if (dunya != null) merkezHedef = dunya.transform;
                }
                else if (uzayNesnesi.NesneTipi == SpaceObjectType.Asteroid)
                {
                    yorungeRengi = new Color(1f, 0.3f, 0.1f, 0.6f);
                    GameObject gunes = GameObject.Find("UnstableStar");
                    if (gunes != null) merkezHedef = gunes.transform;
                }
                else if (uzayNesnesi.NesneTipi == SpaceObjectType.Debris)
                {
                    yorungeRengi = new Color(0.6f, 0.6f, 0.6f, 0.4f);
                    GameObject dunya = GameObject.Find("Earth");
                    if (dunya != null) merkezHedef = dunya.transform;
                }
                else if (uzayNesnesi.NesneTipi == SpaceObjectType.SolarWave)
                {
                    cizgi.enabled = false;
                }

                if (gameObject.name == "Earth")
                {
                    yorungeRengi = new Color(0.2f, 0.6f, 1f, 0.6f);
                }
            }
        }

        if (merkezHedef == null) merkezHedef = null;

        cizgi.startColor = yorungeRengi;
        cizgi.endColor = yorungeRengi;
    }

    void Update()
    {
        YorungeCiz();
    }

    void YorungeCiz()
    {
        Vector3 merkez = merkezHedef != null ? merkezHedef.position : Vector3.zero;
        float yaricap = Vector3.Distance(transform.position, merkez);

        if (yaricap < 0.1f) return;

        float aci = 0f;
        for (int i = 0; i < (segmentSayisi + 1); i++)
        {
            float x = Mathf.Sin(Mathf.Deg2Rad * aci) * yaricap;
            float z = Mathf.Cos(Mathf.Deg2Rad * aci) * yaricap;

            cizgi.SetPosition(i, merkez + new Vector3(x, 0, z));

            aci += (360f / segmentSayisi);
        }
    }
}
