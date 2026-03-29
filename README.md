<div align="center">
  <img src="docs/banner.png" alt="USSN Banner" width="100%">
  <br><br>
  
  [![Website](https://img.shields.io/badge/Website-ussn.netlify.app-blue?style=for-the-badge&logo=vercel)](https://ussn.netlify.app)
  [![Hackathon](https://img.shields.io/badge/TUA_Astro_Hackathon-2026-red?style=for-the-badge&logo=hackaday)](#)
  [![Unity](https://img.shields.io/badge/Unity-6-black?style=for-the-badge&logo=unity)](https://unity.com)
  [![AI](https://img.shields.io/badge/AI-Object_Detection-orange?style=for-the-badge&logo=scikitlearn)](#)
</div>

<br>

> **Orbi-Tech** takımı tarafından **TUA Astro Hackathon** için 48 saatte yapılmıştır.  
> **Takım Üyeleri:** Yiğit Alp Göktaş, Yusuf Kaan Mutlu

---

## 🛑 Problem: Uzaydaki Büyüyen Tehdit

Dünya yörüngesi hızla kalabalıklaşıyor ve her yıl katlanarak artan yüksek hızlı uzay çöpleri yılda yüzlerce çarpışma riskine yol açıyor. Uydu ağı karmaşık ve merkezi kontrol eksik, solar patlamalar veri kaybı ve iletişim sorunları oluşturuyor. Mevcut sistemler çarpışmaları önlemek ve tehditleri öngörmek için yeterince otomatik ve güvenli değil, kritik uzay altyapıları risk altında.

## 💡 Çözüm: USSN - Uzayın Kolektif Zekası

USSN; uzaydaki tehditleri anlık olarak algılayan, riskleri otonom kararlara dönüştüren ve bu veriyi güvenli protokollerle tüm ağa yayan bütünleşik bir güvenlik ağıdır.

- 👁️ **Algılama (AI Tabanlı Tespit):** Uzay çöplerini, asteroidleri ve solar fırtınaları görsel/verisel olarak anında tanımlar.
- 🚀 **Aksiyon (Otonom Manevra):** Çarpışma risklerini hesaplar, uydulara yeni rotalar atar ve yörünge optimizasyonu sağlar.
- 📡 **Haberleşme (Güvenli Haberleşme):** Kuantum dayanıklı şifreleme ve düşük bant genişliğiyle veriyi manipüle edilemez kılar.

---

# ⚙️ Teknik Yaklaşım – Tam Sistem Detayları

## 1. Detection Layer (Algılama Katmanı)

### 🗑️ Uzay Çöpü Algılama

<div align="center">
  <img src="docs/debris_detection.png" alt="Uzay Çöpü Algılama" width="80%">
</div>

- **Veri Kaynağı:** Space-Track API
- **Yöntem:** Hough Transform + YOLOv8 object detection
- **Özellik:** Gerçek zamanlı görüntü işleme ile yörüngedeki tüm debris’leri tespit eder
- **Validation:** ESA ve NASA açık veri setleri ile doğrulandı
- **Not:** Multi-frame analiz ile hızlı ve doğru algılama sağlanır, hareketli ve durağan objeler ayrıştırılır

### ☄️ Asteroid Algılama

<div align="center">
  <img src="docs/asteroid_detection.png" alt="Asteroid Algılama" width="80%">
</div>

- **Veri Kaynağı:** NASA NeoWs API
- **Yöntem:** Blink Comparison + YOLO object detection
- **Özellik:** Çok kareli görüntü karşılaştırmasıyla hareketli objeler algılanır
- **Validation:** GMAT simülasyonu ile %99.97 uyum sağlandı
- **Not:** Çarpışma riski skorları hesaplanır ve Intelligence Layer’a iletilir

### ☀️ Solar Fırtına Algılama

<div align="center">
  <img src="docs/solar_flare_detection.png" alt="Solar Fırtına Algılama" width="80%">
</div>

- **Veri Kaynağı:** NASA DONKI Space Weather API
- **Yöntem:** Time-series analysis ile erken tahmin
- **Özellik:** Solar flares ve CME’leri tahmin ederek risk skoru üretir
- **Validation:** Tarihsel olaylarla test edildi, erken uyarı doğruluğu ≥ %95

---

## 2. Intelligence Layer (Karar ve Risk Skorlama)

- **Risk Skorlama:**
  - Çarpışma olasılığı (%), debris density (yüksek/orta/düşük), solar risk (yüksek/orta/düşük)
- **Tahmin Modülleri:**
  - LSTM ve Transformer tabanlı derin öğrenme modelleri
  - Her senaryo için 9 ayrı model, her biri ≥ %95 doğruluk
- **Otonom Karar Layer:**
  - AI, risk skorlarına göre önerilen yörünge değişikliklerini üretir
  - Swarm Intelligence ile merkezi sistem olmadan uydular birbirine bilgi aktarır

---

## 3. Control & Movement (Yörünge ve Çarpışma Yönetimi)

- **Uydu Yörüngesi Optimizasyonu:**
  - AI, çarpışma riski, debris density ve solar risk skorlarını değerlendirerek yörünge planlaması yapar
  - Delta-v hesaplamaları ile enerji verimli rota değişiklikleri
- **Çarpışma Önleme:**
  - Monte Carlo simülasyonları ile olası çarpışma senaryoları üretilir
  - Collision avoidance algoritmaları ile otonom manevra önerilir
- **Bant Genişliği Yönetimi:**
  - Intent-based communication (komut tabanlı veri transferi)
  - Delta sıkıştırma ve adaptive bitrate ile veri boyutu optimize edilir
  - Reed-Solomon error correction ile veri kayıpları giderilir
- **Otonom Eylem Katmanı:**
  - AI, risk skorlarına göre otonom yönlendirme yapar
  - Bandwidth optimizasyonu ve sistem kaynak yönetimi entegre edilmiştir

---

## 4. Simulation & Validation

- **Unity 6 + Rebound Physics Engine:**
  - Gerçek zamanlı yörünge, debris ve çarpışma simülasyonu
  - Uydu manevraları ve swarm intelligence test edildi
- **GMAT Doğrulaması:**
  - Tüm AI modelleri GMAT ile %99.97 doğrulukta eşleşti
- **Model Başarıları:**
  - 9 derin öğrenme modeli, her senaryoda ≥ %95 doğruluk
  - Farklı görevler ve simülasyon koşullarında performans doğrulandı

---

## 5. LLM Entegrasyonu (Qwen3-14b)

- Tüm kritik olaylar ve risk skorları **Qwen3-14b LLM** tarafından analiz edilir
- **Otomatik Rapor Üretimi:** PDF olarak detaylı olay ve öneriler
- Olayların yorumlanması, risk düzeylerinin açıklanması ve geleceğe yönelik öneriler

---

## 6. Network & Communication Layer

- **Bant Yönetimi:** Telemetri değil, akıllı iletişim
  - Delta sıkıştırma, intent-based communication, adaptive bitrate
- **Kayıp Giderme:** _“Veri kaybı olabilir, düzeltilir.”_
  - Reed-Solomon error correction, fragmentasyon, store-and-forward
- **Güvenlik:** _“Müdahale edilemez.”_
  - AES-256 uçtan uca şifreleme, QKD uyumlu anahtar değişimi, dijital imza doğrulama
- **Self-Healing Network:** Merkezi olmayan yapı ile single point of failure yok

---

## 7. Open Source & Reproducibility

- Tüm kodlar, modeller ve simülasyonlar GitHub ve Kaggle üzerinden erişilebilir
- Kullanılan veri setleri ve API’ler güvenilir, belgelenmiş ve açık kaynak
- Bilimsel doğrulama ve topluluk katkısı için tamamen şeffaf yapı

---

# 🔌 USSN Simulation API (Kullanım Özeti)

USSN projesi tamamen dışarıdan kontrol edilebilir açık bir **JSON API mimarisi** üzerine kurulmuştur. Herhangi bir AI Karar Motoru (Python, Node.js vb.), Unity simülasyonuna anlık müdahale edebilir.

**Örnek JSON Talebi:**

```json
{
  "action": "update",
  "id": "satellite_001",
  "orbitSpeed": 45,
  "orbitRadius": 50,
  "orbitTargetName": "Earth"
}
```

### Temel API Yetenekleri:

- **`spawn`**: İstenilen koordinatlarda dinamik olarak uzay çöpü, asteroit, uydu veya solar wave oluşturur.
- **`move`**: Objeleri anında yeni koordinatlara ışınlar (Manuel rotasyon ve müdahale için).
- **`update`**: Risk tespit edildiğinde; objenin ölçeğini, dönüş hızını ve yörünge yarıçapını otonom olarak yeniler. Çarpışma engelleme manevraları bu sayede simüle edilir.
- **`delete`**: Objeleri simülasyondan temizler.

_Tam API sözlüğü ve tüm opsiyonlar için **SIMULATION** klasörü içerisindeki [`USSN_API_GUIDE.md`](SIMULATION/USSN_API_GUIDE.md) dosyasına göz atabilirsiniz._
