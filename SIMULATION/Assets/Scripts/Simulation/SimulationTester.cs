using UnityEngine;
using System.Collections;
using USSN.Simulation;

public class SimulationTester : MonoBehaviour
{
    private void Start()
    {
        StartCoroutine(TestBaslat());
    }

    private IEnumerator TestBaslat()
    {
        yield return new WaitForSeconds(0.5f);

        Debug.Log("<color=green>--- API TESTI BASLIYOR ---</color>");

        GameObject dunya = GameObject.Find("Earth");
        Vector3 dunyaKonumu = dunya != null ? dunya.transform.position : new Vector3(24, 0, 98);

        string asteroidKimlik = SimulationManager.Aktif.Olustur(SpaceObjectType.Asteroid, new Vector3(33, 0, 100));
        Debug.Log($"<color=cyan>[Test]</color> Asteroit olusturuldu: (33, 0, 100)");

        yield return new WaitForSeconds(1.0f);

        Vector3 uyduKonumu = dunyaKonumu + new Vector3(10, 0, 10);
        string uyduKimlik = SimulationManager.Aktif.Olustur(SpaceObjectType.Satellite, uyduKonumu);
        Debug.Log($"<color=cyan>[Test]</color> Uydu olusturuldu: {uyduKonumu}");

        yield return new WaitForSeconds(1.0f);

        string dalgaKimlik = SimulationManager.Aktif.Olustur(SpaceObjectType.SolarWave, Vector3.zero);
        Debug.Log($"<color=orange>[Test]</color> Gunes dalgasi olusturuldu: (0,0,0)");

        yield return new WaitForSeconds(3.0f);

        SimulationAPI api = FindObjectOfType<SimulationAPI>();
        if (api != null)
        {
            string enkazKimlik = api.SpawnDebris(dunyaKonumu.x + 15, 0, dunyaKonumu.z + 15);
            Debug.Log($"<color=yellow>[Test]</color> Enkaz API ile olusturuldu: {enkazKimlik}");

            yield return new WaitForSeconds(1.5f);

            api.UpdateObject(
                enkazKimlik,
                x: -9999f, y: -9999f, z: -9999f,
                scale: 0.3f,
                orbitSpeed: 45f,
                orbitRadius: 20f,
                orbitTargetName: "Earth"
            );
            Debug.Log($"<color=yellow>[Test]</color> Enkaz parametreleri API ile guncellendi");
        }

        yield return new WaitForSeconds(1.0f);

        if (api != null)
        {
            api.UpdateObject(
                id: "Earth",
                x: -9999f, y: -9999f, z: -9999f,
                scale: -9999f,
                orbitSpeed: 5f,
                orbitRadius: 100f,
                orbitTargetName: "UnstableStar"
            );
            Debug.Log($"<color=yellow>[Test]</color> Dunya parametreleri API ile guncellendi");
        }

        Debug.Log("<color=green>--- API TESTI TAMAMLANDI ---</color>");
    }
}
