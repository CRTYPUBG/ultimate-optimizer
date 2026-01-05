https://github.com/user-attachments/assets/915bd74a-a1d0-43f9-9c46-fbce3c11f3ca
<img width="1408" height="736" alt="ult_opt_banner_github" src="https://github.com/user-attachments/assets/980b213a-cd67-4fb1-95fb-d7cc9e7a1b46" />
<img width="1408" height="736" alt="ult_opt_banner_github" src="https://github.com/user-attachments/assets/980b213a-cd67-4fb1-95fb-d7cc9e7a1b46" />

# Ultimate Optimizer

<p align="center">
  <img
    src="https://github.com/user-attachments/assets/980b213a-cd67-4fb1-95fb-d7cc9e7a1b46"
    style="
      max-width: 100%;
      border-radius: 14px;
      transition: transform 0.35s ease, box-shadow 0.35s ease;
    "
    onmouseover="this.style.transform='scale(1.02)'; this.style.boxShadow='0 20px 40px rgba(0,0,0,0.35)';"
    onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='none';"
  />
</p>

**Ultimate Optimizer** is a premium Windows optimization tool that combines proven tweaks from industry-standard utilities into a modern, hardware-aware application with a clean and responsive UI.

---

<h2 style="display:flex;align-items:center;gap:10px;">
  <img
    src="https://cdn-icons-png.freepik.com/512/17794/17794099.png"
    width="42"
    height="42"
    style="transition:transform 0.3s ease, filter 0.3s ease;"
    onmouseover="this.style.transform='scale(1.15)'; this.style.filter='drop-shadow(0 0 6px rgba(0,180,255,0.6))';"
    onmouseout="this.style.transform='scale(1)'; this.style.filter='none';"
  />
  Features
</h2>

<table>
<tr>
<td style="padding:18px;transition:transform 0.25s ease;"
onmouseover="this.style.transform='translateY(-6px)'"
onmouseout="this.style.transform='translateY(0)'">

### ⚙️ Hardware Aware
Automatically detects **CPU (Intel / AMD)** and **GPU (NVIDIA / AMD)** and only exposes relevant optimizations.

</td>

<td style="padding:18px;transition:transform 0.25s ease;"
onmouseover="this.style.transform='translateY(-6px)'"
onmouseout="this.style.transform='translateY(0)'">

### 🎨 Premium UI
Borderless modern window, glassmorphism design, smooth animations, and scalable SVG assets.

</td>
</tr>

<tr>
<td style="padding:18px;transition:transform 0.25s ease;"
onmouseover="this.style.transform='translateY(-6px)'"
onmouseout="this.style.transform='translateY(0)'">

### 🎮 Gaming & Latency
Win32 Priority Separation, MMCSS tuning, scheduler tweaks, and input latency optimizations.

</td>

<td style="padding:18px;transition:transform 0.25s ease;"
onmouseover="this.style.transform='translateY(-6px)'"
onmouseout="this.style.transform='translateY(0)'">

### 🛡 Privacy & Debloat
Telemetry removal, background service cleanup, and privacy-focused system adjustments.

</td>
</tr>

<tr>
<td style="padding:18px;transition:transform 0.25s ease;"
onmouseover="this.style.transform='translateY(-6px)'"
onmouseout="this.style.transform='translateY(0)'">

### 🖥 GPU-Specific Fixes
MPO disable, NVIDIA Ansel toggle, AMD ULPS control, and driver-level optimizations.

</td>

<td style="padding:18px;transition:transform 0.25s ease;"
onmouseover="this.style.transform='translateY(-6px)'"
onmouseout="this.style.transform='translateY(0)'">

### 🔄 Update System
Integrated GitHub Releases checker with changelog display inside the app.

</td>
</tr>
</table>

---

<h2 style="display:flex;align-items:center;gap:10px;">
  <img
    src="https://cdn-icons-png.flaticon.com/512/18510/18510301.png"
    width="42"
    height="42"
    style="transition:transform 0.3s ease, filter 0.3s ease;"
    onmouseover="this.style.transform='scale(1.15)'; this.style.filter='drop-shadow(0 0 6px rgba(0,180,255,0.6))';"
    onmouseout="this.style.transform='scale(1)'; this.style.filter='none';"
  />
  Technology Stack
</h2>

| Component | Technology |
|--------|------------|
| Backend | Python 3.x |
| UI Framework | PySide6 (Qt 6) |
| System APIs | WMI, WinReg, Windows API (ctypes) |
| Assets | SVG Icons, PNG Logos |

---

<h2 style="display:flex;align-items:center;gap:10px;">
  <img
    src="https://cdn-icons-png.flaticon.com/512/3263/3263182.png"
    width="42"
    height="42"
    style="transition:transform 0.3s ease, filter 0.3s ease;"
    onmouseover="this.style.transform='scale(1.15)'; this.style.filter='drop-shadow(0 0 6px rgba(0,180,255,0.6))';"
    onmouseout="this.style.transform='scale(1)'; this.style.filter='none';"
  />
  Installation
</h2>

1. Download **UltimateOptimizer.exe** from the **Releases** page  
2. Launch the application  
3. Grant **Administrator privileges** when prompted

---

<h2 style="display:flex;align-items:center;gap:10px;">
  <img
    src="https://cdn-icons-png.freepik.com/256/13754/13754717.png"
    width="42"
    height="42"
    style="transition:transform 0.3s ease, filter 0.3s ease;"
    onmouseover="this.style.transform='scale(1.15)'; this.style.filter='drop-shadow(0 0 6px rgba(0,180,255,0.6))';"
    onmouseout="this.style.transform='scale(1)'; this.style.filter='none';"
  />
  Development
</h2>

### Run from Source
```bash
pip install PySide6 wmi
python main.py
