# Ultimate Optimizer - Proje Konuları ve Özellikler 📋

Bu dosya, Ultimate Optimizer projesinde geliştirilen tüm özellikleri ve teknik konuları özetler.

---

## 🎯 Ana Modüller

### 1. Windows Genel Optimizasyon
- Telemetri Kapatma
- Hızlı Yanıt Süresi
- Hızlı Başlatma Kontrolü
- FSO & Game Bar Devre Dışı
- OneDrive Kaldırma

### 2. Oyun & Düşük Gecikme
- MMCSS Gecikme İyileştirme
- Win32 Priority Separation
- TCP No Delay (Nagle Algoritması)
- Game Mode Optimizasyonu
- HPET Zamanlayıcı Kontrolü

### 3. Emulator Stability Engine (ESE)
- VM Tick Desynchronizer
- Cache Pulse (Kaynak Yönetimi)
- GPU Submit Gate
- Dinamik CPU Affinity
- IO Öncelik Yönetimi

### 4. Sağlık & Onarım Modülü
- Onarım Modu (FREE)
- FPS Drop Analizi (FREE)
- Oturum Sağlık Skoru (FREE)
- RAM & Bellek Dengeleme (VIP)
- Disk Gecikme Azaltma (VIP)
- Oyun Profili Sistemi (VIP)
- Donanım-Windows Uyum Analizi (VIP)
- Geri Alma Koruması (FREE)
- Sessiz Tüketici Algısı (VIP)

### 5. Gizlilik & Debloat
- Mağaza Otomatik Güncelleme Kontrolü
- Hata Raporlama Devre Dışı
- Reklam Kimliği Engelleme

### 6. GPU Tweaks
- **NVIDIA:** MPO Fix, Ansel Kapatma, Düşük Gecikme Modu
- **AMD:** ULPS Kapatma, Shader Cache Reset

### 7. CPU Tweaks
- Power Throttling Kontrolü
- Çekirdek Park Etme Yönetimi

---

## ⚙️ Teknik Altyapı

### Güncelleme Sistemi
- GitHub API Entegrasyonu
- Self-Patching (Kendi Kendini Güncelleme)
- Sayısal Sürüm Karşılaştırma (`version_to_tuple`)
- Anlık Bellek Tazeleme

### Veri Yönetimi
- `%LOCALAPPDATA%\UltimateOptimizer` Dizini
- `Settings.json` - Kullanıcı Tercihleri
- `Version.json` - Sürüm Metadata
- `log-data.log` - İşlem Kayıtları

### UI/UX Tasarım
- PySide6 (Qt6) Framework
- Glassmorphism Tema
- 45px Border Radius
- Animasyonlu Toggle Butonları
- Premium Splash Screen
- Karanlık Tema Dialog Pencereleri

---

## 🌐 Web Sitesi

### Dosyalar
- `index.html` - Ana sayfa
- `style.css` - Tailwind + Custom CSS
- `script.js` - jQuery, AOS, Particles.js, SweetAlert2

### Özellikler
- Preloader Animasyonu
- Particles.js Arka Plan
- AOS Scroll Animasyonları
- Hardware Profiler Seçici
- Responsive Tasarım

---

## 📦 Dağıtım

### Depolar
- **Uygulama:** `CRTYPUBG/ultimate-optimizer`
- **Web Sitesi:** `CRTYPUBG/crtyweb`

### Build Araçları
- PyInstaller (`build_exe.bat`)
- Inno Setup (`setup.iss`)

---

## 📅 Sürüm Geçmişi

| Sürüm | Durum | Açıklama |
|-------|-------|----------|
| v1.0.0 | ✅ | İlk resmi sürüm |
| v1.0.6 | ✅ | ESE Motoru, Ayar Kalıcılığı |
| v1.0.9 | ✅ | Sağlık Modülü, UI Polish |
| v1.1.0 | ✅ | Güncelleme Sistemi, Stabilite Düzeltmeleri |

---

**Son Güncelleme:** 04.01.2026
