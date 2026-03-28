using System;
using UnityEngine;

namespace USSN.Simulation
{
    public enum SpaceObjectType
    {
        Asteroid,
        Satellite,
        SolarWave,
        Debris
    }

    public class SpaceObject : MonoBehaviour
    {
        public string Kimlik;
        public SpaceObjectType NesneTipi;

        private void Awake()
        {
            if (string.IsNullOrEmpty(Kimlik))
            {
                Kimlik = Guid.NewGuid().ToString();
            }
        }

        private void Start()
        {
            if (SimulationManager.Aktif != null)
            {
                SimulationManager.Aktif.Kaydet(this);
            }
            else
            {
                Debug.LogWarning($"SpaceObject {Kimlik} kayit olamadi: SimulationManager bulunamadi!");
            }
        }

        private void OnDestroy()
        {
            if (SimulationManager.Aktif != null && !string.IsNullOrEmpty(Kimlik))
            {
                SimulationManager.Aktif.KaydiSil(Kimlik);
            }
        }
    }
}
