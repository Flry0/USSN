# USSN (Universal Satellite Safety Network) Simulation API Guide

Bu doküman, USSN Simülasyon projesinde bulunan uzay objelerini (Dünya, Uydular, Asteroitler, Uzay Çöpleri ve Güneş Patlamaları) dış bir yapay zeka, backend sunucusu veya script üzerinden **JSON** veri yapılarıyla dinamik olarak kontrol etmek için hazırlanmıştır.

## API İletişim Noktası (Endpoint)

Unity içerisindeki tüm API istekleri `SimulationAPI.cs` script'indeki `ExecuteCommand(string jsonCommand)` fonksiyonu üzerinden işlenir.

Yapay zeka sistemleri veya dış C# betikleri, basit bir JSON dizgisini (string) bu fonksiyona yollayarak sahnedeki hiçbir koda dokunmadan simülasyonu yönetebilir.

---

## 🏗️ JSON Komut Yapısı (SimCommand)

Tüm komutlar aşağıdaki ana yapı üzerinden çalışır. (Kullanmadığınız özellikleri JSON'a eklemenize gerek yoktur, sistem varsayılanları otomatik ayarlar.)

```json
{
  "action": "KOMUT TİPİ (spawn, move, update, delete)",
  "type": "OBJE TİPİ (asteroid, satellite, solar_wave, debris)",
  "id": "Manipüle edilecek objenin ID'si veya Sahne Adı (Örn: 'Earth')",

  "x": 0.0,
  "y": 0.0,
  "z": 100.0,

  "scale": 1.0,
  "orbitSpeed": 15.0,
  "orbitRadius": 50.0,
  "orbitTargetName": "Earth"
}
```

---

## 🛠️ Temel API Aksiyonları ve Örnekler

### 1. Yeni Obje Oluşturma (action: "spawn")

Simülasyona uzay taşı, çöp, uydu veya güneş fırtınası fırlatır. Obje yaratılırken otomatik bir `GUID` atanır ve bu ID log olarak döndürülür.

**Desteklenen Tipler (`type`):**

- `asteroid`: Kızıl/Turuncu renkte bir asteroit. Güneşi baz alır.
- `satellite`: Mavi renkli bir uydu. Dünyayı baz alır.
- `solar_wave`: Görsel güneş patlaması (Otomatik olarak dünyaya fırlar).
- `debris`: Gri renkli, kontrolsüz uzay çöpü.

**Örnek: Bir "Uzay Çöpü" Spawn Etmek**

```json
{
  "action": "spawn",
  "type": "debris",
  "x": 40.0,
  "y": 0.0,
  "z": 110.0
}
```

### 2. Sadece Konum Taşıma (action: "move")

Sahnede bulunan bir objeyi **anında** belirtilen x, y, z koordinatına ışınlar.

**Örnek: Asteroidi Işınlamak**

```json
{
  "action": "move",
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "x": -100.0,
  "y": 0.0,
  "z": 50.0
}
```

### 3. Obje Parametrelerini Güncelleme (action: "update")

Sahnede hali hazırda dönen veya duran _HERHANGİ_ bir objenin `Boyut (Scale)`, `Hız (orbitSpeed)`, `Mesafe (orbitRadius)` veya `Hedef (orbitTargetName)` bilgilerini manipüle eder.

🚀 **ÖNEMLİ:** `id` değeri olarak karmaşık GUID vermek zorunda değilsiniz. Doğrudan sahnedeki obje isimlerini verebilirsiniz! (Örneğin `"Earth"` veya `"UnstableStar"`)

**Örnek A: Dünyanın Yörüngesini Yapay Zeka ile Oluşturmak:**

```json
{
  "action": "update",
  "id": "Earth",
  "orbitSpeed": 5.0,
  "orbitRadius": 100.0,
  "orbitTargetName": "UnstableStar"
}
```

**Örnek B: Varolan Bir Uydunun Çarpışmayı Önlemek İçin Dünyadan Uzaklaştırılması:**

```json
{
  "action": "update",
  "id": "UYDUNUN_ID_SI",
  "orbitRadius": 30.0,
  "scale": 0.2
}
```

**Örnek C: Bir Uzay Çöpünü Silah Olarak Kullanmak (Kaotik AI):**

```json
{
  "action": "update",
  "id": "COPUN_ID_SI",
  "scale": 5.0,
  "orbitSpeed": -200.0
}
```

### 4. Obje Yok Etme (action: "delete")

```json
{
  "action": "delete",
  "id": "UYDUNUN_ID_SI"
}
```

---

## C# Tarafındaki Fonksiyonlar

| Fonksiyon                     | Açıklama                    |
| ----------------------------- | --------------------------- |
| `SpawnAsteroid(x, y, z)`      | Asteroit yaratır            |
| `SpawnSatellite(x, y, z)`     | Uydu yaratır                |
| `SpawnSolarWave(x, y, z)`     | Güneş dalgası yaratır       |
| `SpawnDebris(x, y, z)`        | Uzay çöpü yaratır           |
| `MoveObject(id, x, y, z)`     | Nesneyi ışınlar             |
| `UpdateObject(id, ...)`       | Tüm parametreleri günceller |
| `DeleteObject(id)`            | Nesneyi yok eder            |
| `ExecuteCommand(jsonCommand)` | JSON ile toplu kontrol      |

---

## 💡 Yapay Zeka Karar Algoritması İçin İpuçları

- Yapay zeka bir asteroitin uyduya çarpacağını öngördüğünde, `UpdateObject` kullanarak Uydunun `orbitRadius` parametresine artış yaparak onu çarpışma vektöründen dışarı alabilir.
- Hız ayarlamaları için `orbitSpeed` alanını manipüle etmelidir. Negatif değer yönü tersine çevirir.
- Dünyanın Güneş etrafında ne kadar açık veya kapalı döneceğini `ExecuteCommand` ile `{"action": "update", "id": "Earth"...}` JSON'u göndererek karar verebilir.
- Kullanılmayan parametreleri JSON'a eklemenize gerek yoktur, sistem varsayılanları otomatik kullanır.
