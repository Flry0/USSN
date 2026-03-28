using UnityEngine;

namespace USSN.Simulation
{
    [System.Serializable]
    public class SimCommand
    {
        public string action;
        public string type;
        public string id;
        public float x = -9999f;
        public float y = -9999f;
        public float z = -9999f;
        public float scale = -9999f;
        public float orbitSpeed = -9999f;
        public float orbitRadius = -9999f;
        public string orbitTargetName = "";
    }

    public class SimulationAPI : MonoBehaviour
    {
        public string SpawnAsteroid(float x, float y, float z)
        {
            Debug.Log($"[API] Asteroit olusturuluyor: {x}, {y}, {z}");
            return SimulationManager.Aktif.Olustur(SpaceObjectType.Asteroid, new Vector3(x, y, z));
        }

        public string SpawnSatellite(float x, float y, float z)
        {
            Debug.Log($"[API] Uydu olusturuluyor: {x}, {y}, {z}");
            return SimulationManager.Aktif.Olustur(SpaceObjectType.Satellite, new Vector3(x, y, z));
        }

        public string SpawnSolarWave(float x, float y, float z)
        {
            Debug.Log($"[API] Gunes dalgasi olusturuluyor: {x}, {y}, {z}");
            return SimulationManager.Aktif.Olustur(SpaceObjectType.SolarWave, new Vector3(x, y, z));
        }

        public string SpawnDebris(float x, float y, float z)
        {
            Debug.Log($"[API] Enkaz olusturuluyor: {x}, {y}, {z}");
            return SimulationManager.Aktif.Olustur(SpaceObjectType.Debris, new Vector3(x, y, z));
        }

        public void MoveObject(string id, float x, float y, float z)
        {
            SimulationManager.Aktif.Tasi(id, new Vector3(x, y, z));
        }

        public void UpdateObject(string id, float x, float y, float z, float scale, float orbitSpeed, float orbitRadius, string orbitTargetName)
        {
            SpaceObject nesne = SimulationManager.Aktif.Getir(id);
            if (nesne == null) return;

            if (x != -9999f && y != -9999f && z != -9999f)
            {
                SimulationManager.Aktif.Tasi(id, new Vector3(x, y, z));
            }

            if (scale != -9999f)
            {
                nesne.transform.localScale = new Vector3(scale, scale, scale);
            }

            OrbitalMovement yorunge = nesne.GetComponent<OrbitalMovement>();
            if (yorunge != null)
            {
                if (orbitSpeed != -9999f) yorunge.donusHizi = orbitSpeed;
                if (orbitRadius != -9999f) yorunge.YaricapiDegistir(orbitRadius);

                if (!string.IsNullOrEmpty(orbitTargetName))
                {
                    GameObject hedefObj = GameObject.Find(orbitTargetName);
                    if (hedefObj != null) yorunge.HedefiDegistir(hedefObj.transform);
                }
            }
            Debug.Log($"[API] Nesne guncellendi -> {id}");
        }

        public void DeleteObject(string id)
        {
            Debug.Log($"[API] Nesne siliniyor: {id}");
            SimulationManager.Aktif.Sil(id);
        }

        public void ExecuteCommand(string jsonCommand)
        {
            try
            {
                SimCommand komut = JsonUtility.FromJson<SimCommand>(jsonCommand);
                if (komut == null) return;

                switch (komut.action.ToLower())
                {
                    case "spawn":
                        SpaceObjectType nesneTipi = SpaceObjectType.Asteroid;
                        if (komut.type != null && komut.type.ToLower() == "satellite") nesneTipi = SpaceObjectType.Satellite;
                        if (komut.type != null && komut.type.ToLower() == "solar_wave") nesneTipi = SpaceObjectType.SolarWave;
                        if (komut.type != null && komut.type.ToLower() == "debris") nesneTipi = SpaceObjectType.Debris;

                        float baslangicX = komut.x != -9999f ? komut.x : 0f;
                        float baslangicY = komut.y != -9999f ? komut.y : 0f;
                        float baslangicZ = komut.z != -9999f ? komut.z : 0f;

                        string kimlik = SimulationManager.Aktif.Olustur(nesneTipi, new Vector3(baslangicX, baslangicY, baslangicZ));
                        Debug.Log($"[API] JSON komutuyla olusturuldu -> {kimlik}");
                        break;
                    case "move":
                        if (komut.x != -9999f && komut.y != -9999f && komut.z != -9999f)
                        {
                            MoveObject(komut.id, komut.x, komut.y, komut.z);
                        }
                        break;
                    case "update":
                        UpdateObject(komut.id, komut.x, komut.y, komut.z, komut.scale, komut.orbitSpeed, komut.orbitRadius, komut.orbitTargetName);
                        break;
                    case "delete":
                        DeleteObject(komut.id);
                        break;
                }
            }
            catch (System.Exception hata)
            {
                Debug.LogError($"[API] Komut isleme hatasi: {hata.Message}");
            }
        }
    }
}
