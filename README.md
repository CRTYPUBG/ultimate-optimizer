


https://github.com/user-attachments/assets/915bd74a-a1d0-43f9-9c46-fbce3c11f3ca


<img width="45" height="45" alt="banner" src="https://github.com/user-attachments/assets/05564a87-fae1-45ee-802c-84f7dfc68fb6" /> # Ultimate Optimizer

Ultimate Optimizer is a premium Windows optimization tool that combines various tweaks from industry-standard tools into a modern, hardware-aware UI.

<img width="45" height="45" alt="banner" src="https://cdn-icons-png.freepik.com/512/17794/17794099.png" /> ## Features

- **Hardware Aware:** Automatically detects CPU (Intel/AMD) and GPU (NVIDIA/AMD) to show relevant tweaks.
- **Premium UI:** Modern, borderless window with glassmorphism, smooth animations, and SVG assets.
- **Tweak Engine:** Comprehensive system optimizations including:
  - Telemetry & Debloat
  - Gaming & Latency (Win32 Priority Separation, MMCSS)
  - Privacy Enhancements
  - GPU Specific fixes (MPO Fix, NVIDIA Ansel, AMD ULPS)
  - CPU Power Management
- **Update System:** Integrated update checker connected to GitHub Releases with changelog display.
- **Logging:** All system changes are logged to `log-data.log` for transparency.

<img width="45" height="45" alt="banner" src="https://cdn-icons-png.flaticon.com/512/18510/18510301.png" /> ## Technology Stack

- **Backend:** Python 3.x
- **UI Framework:** PySide6 (Qt6)
- **APIs:** WMI, WinReg, Windows API (ctypes)
- **Assets:** SVG icons and PNG logos.

<img width="45" height="45" alt="banner" src="https://cdn-icons-png.freepik.com/256/13754/13754717.png?semt=ais_white_label" /> ## Installation

1. Run the `UltimateOptimizer.exe` from the Releases page.
2. Run with Administrator privileges (the app will prompt you).

<img width="45" height="45" alt="banner" src="https://cdn-icons-png.flaticon.com/512/3263/3263182.png" /> ## Development

To run from source:
```bash
pip install PySide6 wmi
python main.py
```

To build the EXE:
```bash
build_exe.bat
```
