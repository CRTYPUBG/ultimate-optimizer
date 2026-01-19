# 📖 Ultimate Optimizer Wiki

Welcome to the official Wiki for **Ultimate Optimizer**. This document provides detailed information about the tool's features, technical architecture, and troubleshooting steps.

---

## 🌍 Language / Dil
- [English](#-english)
- [Türkçe](#-türkçe)

---

## 🇺🇸 English

### 🚀 Introduction
**Ultimate Optimizer** is a high-performance Windows optimization utility developed in Python using the PySide6 framework. It is designed to reduce system latency, improve gaming performance, and provide a cleaner Windows experience through hardware-aware tweaks.

### 🛠 Key Features
- **Hardware-Aware Tweaks**: Automatically detects your CPU (Intel/AMD) and GPU (NVIDIA/AMD) to apply only compatible optimizations.
- **Emulator Stability Engine (ESE)**: Specialized hooks for popular Android emulators like GameLoop, BlueStacks, LDPlayer, and MEmu to ensure smoother gameplay.
- **Pro Optimizer Engine**: Dynamic priority adjustments for major titles including Fortnite, GTA V, League of Legends, and Overwatch.
- **Modern UI**: A premium, borderless interface featuring glassmorphism effects and smooth animations.
- **Privacy & Debloat**: Removes intrusive Windows telemetry and disables unnecessary background services.

### 📥 Installation
1.  Navigate to the [Releases](https://github.com/CRTYPUBG/ultimate-optimizer/releases) page.
2.  Download the latest `UltimateOptimizer.exe`.
3.  Right-click and select **Run as Administrator** (Required for registry and service modifications).

### 💻 Technology Stack
- **Languages**: Python 3.x
- **UI Framework**: PySide6 (Qt 6)
- **APIs**: Windows Registry (winreg), WMI, Windows Native APIs (ctypes)
- **Graphics**: SVG-based scalable assets

### 🔍 Troubleshooting
- **App doesn't start**: Ensure you have granted Administrator privileges.
- **Antivirus triggers**: Since the tool modifies system settings and registry keys, some AVs might flag it. This is a false positive; you can safely add it to exclusions.
- **Version Mismatch**: Ensure `Version.json` exists in the application directory for update checks.

### 🛠 Development & Build
- **Setup Environment**: `pip install PySide6 wmi psutil`
- **Signing**: The project includes a robust signing system using `sign.py` and PowerShell scripts (`create_and_sign.ps1`).
- **Building**: Use `build.py` or `build_exe.bat` to generate the standalone executable.

---

## 🇹🇷 Türkçe

### 🚀 Giriş
**Ultimate Optimizer**, PySide6 framework'ü kullanılarak Python ile geliştirilmiş yüksek performanslı bir Windows optimizasyon aracıdır. Donanım duyarlı ince ayarlar aracılığıyla sistem gecikmesini azaltmak, oyun performansını artırmak ve daha temiz bir Windows deneyimi sunmak için tasarlanmıştır.

### 🛠 Temel Özellikler
- **Donanım Duyarlı Ayarlar**: Yalnızca uyumlu optimizasyonları uygulamak için CPU (Intel/AMD) ve GPU (NVIDIA/AMD) donanımınızı otomatik olarak algılar.
- **Emulator Stability Engine (ESE)**: Daha akıcı bir oyun deneyimi sağlamak için GameLoop, BlueStacks, LDPlayer ve MEmu gibi popüler Android emülatörlerine özel geliştirmeler.
- **Pro Optimizer Engine**: Fortnite, GTA V, League of Legends ve Overwatch dahil olmak üzere popüler oyunlar için dinamik öncelik ayarlamaları.
- **Modern Arayüz**: Glassmorphism efektleri ve pürüzsüz animasyonlar içeren premium, kenarlıksız bir arayüz.
- **Gizlilik ve Hafifleştirme**: Müdahaleci Windows telemetrisini kaldırır ve gereksiz arka plan hizmetlerini devre dışı bırakır.

### 📥 Kurulum
1.  [Releases](https://github.com/CRTYPUBG/ultimate-optimizer/releases) (Sürümler) sayfasına gidin.
2.  En güncel `UltimateOptimizer.exe` dosyasını indirin.
3.  Sağ tıklayın ve **Yönetici Olarak Çalıştır** seçeneğini seçin (Kayıt defteri ve hizmet değişiklikleri için gereklidir).

### 💻 Teknoloji Yığını
- **Diller**: Python 3.x
- **Arayüz Framework**: PySide6 (Qt 6)
- **API'ler**: Windows Kayıt Defteri (winreg), WMI, Windows Native API'leri (ctypes)
- **Grafikler**: SVG tabanlı ölçeklenebilir varlıklar.

### 🔍 Sorun Giderme
- **Uygulama başlamıyor**: Yönetici ayrıcalıkları verdiğinizden emin olun.
- **Antivirüs uyarısı**: Araç sistem ayarlarını ve kayıt defteri anahtarlarını değiştirdiği için bazı antivirüsler uyarı verebilir. Bu bir hatalı tespittir (false positive); güvenle istisnalara ekleyebilirsiniz.
- **Sürüm Hatası**: Güncelleme kontrolleri için uygulama dizininde `Version.json` dosyasının bulunduğundan emin olun.

### 🛠 Geliştirme ve Derleme
- **Ortam Kurulumu**: `pip install PySide6 wmi psutil`
- **İmzalama**: Proje, `sign.py` ve PowerShell betiklerini (`create_and_sign.ps1`) kullanan sağlam bir imzalama sistemi içerir.
- **Derleme**: Bağımsız yürütülebilir dosyayı oluşturmak için `build.py` veya `build_exe.bat` kullanın.
