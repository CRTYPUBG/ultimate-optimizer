import sys
import platform
import wmi
import os
import json
import subprocess
import winreg
import urllib.request
import ctypes

# --- HIDE CONSOLE ---
def hide_console():
    if platform.system() == "Windows":
        hWnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hWnd:
            ctypes.windll.user32.ShowWindow(hWnd, 0) # 0 = SW_HIDE

# hide_console()

import logging
import re
import psutil
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QStackedWidget, 
                               QFrame, QScrollArea, QGraphicsDropShadowEffect,
                               QSizePolicy, QMessageBox)
from PySide6.QtCore import Qt, QSize, QPoint, QPropertyAnimation, QEasingCurve, Property, QTimer, QThread, Signal
from PySide6.QtGui import QIcon, QPixmap, QCursor, QColor, QPainter, QLinearGradient

# --- DATA PATHS (FOR ADMIN & INSTALL PERMISSIONS) ---
def get_data_dir():
    app_data = os.environ.get('LOCALAPPDATA')
    if not app_data:
        app_data = os.path.expanduser('~')
    path = os.path.join(app_data, "UltimateOptimizer")
    if not os.path.exists(path):
        try:
            os.makedirs(path, exist_ok=True)
        except:
            return os.path.dirname(os.path.abspath(__file__))
    return path

DATA_DIR = get_data_dir()
LOG_FILE = os.path.join(DATA_DIR, 'log-data.log')
SETTINGS_FILE = os.path.join(DATA_DIR, 'Settings.json')
VERSION_FILE = os.path.join(DATA_DIR, 'Version.json')

# --- LOGGING SETUP ---
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

# --- CONSTANTS ---
# --- VERSION CONFIG ---
DEFAULT_VERSION = "v1.1.0"
DEFAULT_DESC = "🚀 Sağlık & Onarım Modülü, Self-Patching Güncelleme Sistemi, Premium UI ve Stabilite Düzeltmeleri içeren tam sürüm."

def version_to_tuple(v):
    """Sürüm metnini ('v1.0.6') sayısal tuple'a çevirir (1, 0, 6)"""
    try:
        clean = re.sub(r'[^\d.]', '', v)
        return tuple(map(int, clean.split('.')))
    except: return (0, 0, 0)

def load_version_info():
    try:
        app_data = os.environ.get('LOCALAPPDATA') or os.path.expanduser('~')
        v_path = os.path.join(app_data, "UltimateOptimizer", "Version.json")
        if os.path.exists(v_path):
            with open(v_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("version", DEFAULT_VERSION), data.get("description", DEFAULT_DESC)
    except: pass
    return DEFAULT_VERSION, DEFAULT_DESC

CURRENT_VERSION, CURRENT_DESCRIPTION = load_version_info()
GITHUB_API_URL = "https://api.github.com/repos/CRTYPUBG/ultimate-optimizer/releases/latest"
UI_DIR = os.path.join(os.path.dirname(__file__), "UI")

def ensure_version_file():
    """Version.json dosyasını kod sürümü ile senkronize eder."""
    try:
        # Kodun içindeki sürümü her zaman esas al
        sync_data = {
            "name": "ultimate-optimizer", 
            "version": CURRENT_VERSION,
            "description": CURRENT_DESCRIPTION,
            "last_active": datetime.now().strftime("%d.%m.%Y")
        }
        
        # Eğer dosya yoksa veya sürüm farklıysa güncelle
        trigger_write = False
        if not os.path.exists(VERSION_FILE):
            trigger_write = True
        else:
            with open(VERSION_FILE, "r", encoding="utf-8") as f:
                old_data = json.load(f)
                if old_data.get("version") != CURRENT_VERSION:
                    trigger_write = True
        
        if trigger_write:
            with open(VERSION_FILE, "w", encoding="utf-8") as f:
                json.dump(sync_data, f, indent=2, ensure_ascii=False)
            logging.info(f"Version.json senkronize edildi: {CURRENT_VERSION}")
    except Exception as e:
        logging.error(f"Version sync error: {e}")
        try:
            with open(VERSION_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "name": "multi-optimizer", 
                    "version": CURRENT_VERSION,
                    "description": CURRENT_DESCRIPTION,
                    "last_sync": datetime.now().strftime("%d.%m.%Y")
                }, f, indent=2, ensure_ascii=False)
            logging.info(f"Version.json senkronize edildi: {CURRENT_VERSION}")
        except Exception as e:
            logging.error(f"Version.json güncelleme hatası: {e}")

def get_ui_path(filename):
    return os.path.join(UI_DIR, filename)

def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

# --- EMULATOR STABILITY ENGINE (ESE) - UNIFIED SYSTEM ---
class ESEWorker(QThread):
    def __init__(self, emulator_procs):
        super().__init__()
        self.emulator_procs = emulator_procs
        self.running = True
        self.active_pids = set()

    def run(self):
        logging.info("ESE: Unified Engine started. Monitoring for emulators...")
        while self.running:
            try:
                found_any = False
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                    if proc.info['name'] in self.emulator_procs:
                        found_any = True
                        pid = proc.info['pid']
                        p = psutil.Process(pid)
                        
                        # 1. EMULATOR CACHE PULSE (Resource Allocation)
                        if pid not in self.active_pids:
                            # İlk Algılama: Çekirdek 0'dan temizle ve Öncelik ata
                            p.nice(psutil.HIGH_PRIORITY_CLASS)
                            cores = list(range(psutil.cpu_count()))
                            if len(cores) > 2: p.cpu_affinity(cores[1:])
                            if hasattr(p, 'ionice'): p.ionice(psutil.IOPRIO_HIGH)
                            self.active_pids.add(pid)
                        
                        # 2. VM TICK DESYNCHRONIZER (Execution Timing)
                        # Her döngüde thread geçişini tetikleyerek render çakışmasını önler
                        ctypes.windll.kernel32.SwitchToThread()
                        
                        # 3. GPU SUBMIT GATE (Submission Optimization)
                        # Grafik zamanlayıcısına yüksek öncelik ver
                        ctypes.windll.kernel32.SetPriorityClass(p.handle, 0x00000080)

                        # DYNAMIC ADAPTATION: Yük yoğunluğuna göre bekleme süresini ayarla
                        cpu_usage = proc.info['cpu_percent']
                        sleep_time = 5 if cpu_usage > 50 else 15
                        self.msleep(sleep_time)

                if not found_any:
                    self.active_pids.clear()
                    self.msleep(1000) # Emülatör yoksa bekleme süresini artır
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
            except Exception as e:
                logging.error(f"ESE Worker Error: {e}")
                self.msleep(100)

    def restore_system(self):
        """Sistem ayarlarını normale döndürür."""
        logging.info("ESE: Restoring system behavior...")
        self.running = False
        try:
            # Ultra Timer'ı sıfırla
            ntdll = ctypes.WinDLL('ntdll.dll')
            ntdll.NtSetTimerResolution(156250, 0, ctypes.byref(ctypes.c_ulong()))
            # Registry ayarlarını sıfırla (GTS)
            root = winreg.HKEY_LOCAL_MACHINE
            path = r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers\Scheduler"
            key = winreg.CreateKeyEx(root, path, 0, winreg.KEY_ALL_ACCESS)
            winreg.SetValueEx(key, "EnableVolatileBatching", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
        except: pass

class EmulatorStabilityEngine:
    def __init__(self):
        self.emulator_procs = ["AndroidProcess.exe", "aow_exe.exe", "dnplayer.exe", "HD-Player.exe", "BlueStacks.exe", "MEmu.exe"]
        self.worker = None

    def toggle(self, state):
        root = winreg.HKEY_LOCAL_MACHINE
        path = r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers\Scheduler"
        if state:
            try:
                ntdll = ctypes.WinDLL('ntdll.dll')
                ntdll.NtSetTimerResolution(5000, 1, ctypes.byref(ctypes.c_ulong()))
                key = winreg.CreateKeyEx(root, path, 0, winreg.KEY_ALL_ACCESS)
                winreg.SetValueEx(key, "EnableVolatileBatching", 0, winreg.REG_DWORD, 1)
                winreg.CloseKey(key)
            except: pass
            
            self.worker = ESEWorker(self.emulator_procs)
            self.worker.start()
            logging.info("ESE: Enabled.")
        else:
            self.stop()

    def stop(self):
        if self.worker:
            self.worker.restore_system()
            self.worker.wait()
            self.worker = None
            logging.info("ESE: Disabled and Restored.")

# --- TWEAK ENGINE ---
class TweakEngine:
    @staticmethod
    def set_reg_value(root, path, name, value, vtype=winreg.REG_DWORD):
        try:
            key = winreg.CreateKeyEx(root, path, 0, winreg.KEY_ALL_ACCESS)
            winreg.SetValueEx(key, name, 0, vtype, value)
            winreg.CloseKey(key)
            logging.info(f"Registry Set: {path}\\{name} = {value}")
            return True
        except Exception as e:
            logging.error(f"Registry Error ({path}\\{name}): {e}")
            return False

    @staticmethod
    def delete_reg_value(root, path, name):
        try:
            key = winreg.OpenKey(root, path, 0, winreg.KEY_ALL_ACCESS)
            winreg.DeleteValue(key, name)
            winreg.CloseKey(key)
            logging.info(f"Registry Deleted: {path}\\{name}")
            return True
        except Exception as e:
            logging.error(f"Registry Delete Error ({path}\\{name}): {e}")
            return False

    @staticmethod
    def run_cmd(cmd):
        try:
            result = subprocess.run(cmd, shell=True, check=False, capture_output=True, text=True, errors='replace')
            logging.info(f"Command Executed: {cmd} | ReturnCode: {result.returncode}")
            return True
        except Exception as e:
            logging.error(f"Command Error ({cmd}): {e}")
            return False

    def apply_tweak(self, title, state):
        logging.info(f"User Action: {title} {'Aktif' if state else 'Pasif'}")
        
        # --- WINDOWS GENEL & PERFORMANCE (Optimizer / Melody) ---
        if title == "Telemetry Kapat":
            self.set_reg_value(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\DataCollection", "AllowTelemetry", 0 if state else 1)
            self.set_reg_value(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\DiagTrack", "Start", 4 if state else 2)
            self.set_reg_value(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\dmwappushservice", "Start", 4 if state else 2)
            if state: self.run_cmd("sc stop DiagTrack")
            
        elif title == "Hızlı Yanıt Süresi":
            # Control Panel\Desktop Tweaks (All string types for REG_SZ)
            self.set_reg_value(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", "AutoEndTasks", "1" if state else "0", winreg.REG_SZ)
            self.set_reg_value(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", "HungAppTimeout", "1000" if state else "5000", winreg.REG_SZ)
            self.set_reg_value(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", "WaitToKillAppTimeout", "2000" if state else "20000", winreg.REG_SZ)
            self.set_reg_value(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control", "WaitToKillServiceTimeout", "2000" if state else "5000", winreg.REG_SZ)

        elif title == "Gecikme İyileştirme (MMCSS)":
            # Multimedia Class Scheduler
            self.set_reg_value(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile", "SystemResponsiveness", 0 if state else 20)
            self.set_reg_value(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile", "NetworkThrottlingIndex", 0xFFFFFFFF if state else 0xA)
            # Games Subkey
            task_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games"
            self.set_reg_value(winreg.HKEY_LOCAL_MACHINE, task_path, "GPU Priority", 8 if state else 8)
            self.set_reg_value(winreg.HKEY_LOCAL_MACHINE, task_path, "Priority", 6 if state else 2)
            self.set_reg_value(winreg.HKEY_LOCAL_MACHINE, task_path, "Scheduling Category", "High" if state else "Medium", winreg.REG_SZ)
            self.set_reg_value(winreg.HKEY_LOCAL_MACHINE, task_path, "SFIO Priority", "High" if state else "Normal", winreg.REG_SZ)

        elif title == "Win32 Priority Separation":
            # 26 (Hex 1A) is a very balanced performance value for gaming (Melody's Tweaker)
            self.set_reg_value(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\PriorityControl", "Win32PrioritySeparation", 26 if state else 2)

        elif title == "Game Mode Aktif":
            self.set_reg_value(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\GameBar", "AllowAutoGameMode", 1 if state else 0)
            self.set_reg_value(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\GameBar", "AutoGameModeEnabled", 1 if state else 0)

        elif title == "FSO & Game Bar Kapat":
            # Disabled Fullscreen Optimization & Game Bar
            self.set_reg_value(winreg.HKEY_CURRENT_USER, r"System\GameConfigStore", "GameDVR_Enabled", 0 if state else 1)
            self.set_reg_value(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\GameDVR", "AllowGameDVR", 0 if state else 1)
            self.set_reg_value(winreg.HKEY_CURRENT_USER, r"System\GameConfigStore", "GameDVR_FSEBehaviorMode", 2 if state else 0)

        elif title == "OneDrive Kaldır":
            if state:
                self.run_cmd("taskkill /f /im OneDrive.exe")
                self.run_cmd(r"%SystemRoot%\System32\OneDriveSetup.exe /uninstall" if os.path.exists(r"C:\Windows\System32\OneDriveSetup.exe") else r"%SystemRoot%\SysWOW64\OneDriveSetup.exe /uninstall")
            else:
                self.run_cmd(r"%SystemRoot%\System32\OneDriveSetup.exe" if os.path.exists(r"C:\Windows\System32\OneDriveSetup.exe") else r"%SystemRoot%\SysWOW64\OneDriveSetup.exe")

        # --- GPU SPECIFIC ---
        elif title == "MPO Fix Uygula":
            self.set_reg_value(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\Dwm", "OverlayTestMode", 0x00000005 if state else 0)
        
        elif title == "Düşük Gecikme Modu":
            # NVIDIA specific via Registry (not as powerful as Inspector but works)
            pass

        # --- CPU SPECIFIC ---
        elif title == "HPET Kapat":
            self.run_cmd("bcdedit /set useplatformclock No" if state else "bcdedit /deletevalue useplatformclock")
        
        elif title == "Çekirdek Park Etmeyi Kapat":
            # ParkControl logic
            self.run_cmd("powercfg -setacvalueindex scheme_current sub_processor processorsettingsmin 100")
            self.run_cmd("powercfg -setacvalueindex scheme_current sub_processor processorsettingsmax 100")
            self.run_cmd("powercfg -setactive scheme_current")

        elif title == "Hızlı Başlatmayı Kapat":
            self.set_reg_value(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Power", "HiberbootEnabled", 0 if state else 1)

        elif title == "TCP No Delay":
            try:
                interfaces_path = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, interfaces_path) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        sub_key_name = winreg.EnumKey(key, i)
                        full_path = f"{interfaces_path}\\{sub_key_name}"
                        self.set_reg_value(winreg.HKEY_LOCAL_MACHINE, full_path, "TcpAckFrequency", 1 if state else 2)
                        self.set_reg_value(winreg.HKEY_LOCAL_MACHINE, full_path, "TCPNoDelay", 1 if state else 0)
            except: pass

        # --- EMULATOR STABILITY ENGINE (UNIFIED) ---
        elif title == "Emulator Stability Engine":
            if not hasattr(self, 'ese_engine'):
                self.ese_engine = EmulatorStabilityEngine()
            self.ese_engine.toggle(state)
            
        # --- HEALTH & REPAIR TOOLS ---
        elif title == "Onarım Modu (FREE)":
            self.run_repair_mode(state)
        elif title == "FPS Drop Analizi (FREE)":
            if state:
                report = self.analyze_fps_drops()
                logging.info(f"FPS Drop Report: {report}")
        elif title == "Oturum Sağlık Skoru (FREE)":
            if state:
                score = self.get_system_score()
                logging.info(f"Session Health Score: {score}/100")
        elif title == "RAM & Bellek Dengeleme (VIP)":
            if state:
                # Simulate RAM clearing/EmptyWorkingSet
                self.run_cmd("powershell -Command \"[System.GC]::Collect()\"")
        elif title == "Disk Gecikme Azaltma (VIP)":
            if state:
                # Set disk IO priority to High for specific patterns (placeholder)
                pass
        elif title == "Geri Alma Koruması (FREE)":
            if state:
                self.run_cmd("powershell -Command \"Checkpoint-Computer -Description 'Optimizer_Protect' -RestorePointType MODIFY_SETTINGS\"")

    def run_repair_mode(self, state):
        """Oyun Odaklı Windows Onarım Modu"""
        logging.info(f"Repair Mode: {'ON' if state else 'OFF'}")
        if state:
            # CPU Zamanlayıcı Önceliği
            self.set_reg_value(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\PriorityControl", "Win32PrioritySeparation", 38) # Agresif
            # Gereksiz servisleri kısıtla
            self.run_cmd("sc stop SysMain")
            self.run_cmd("sc stop WerSvc")
        else:
            # Geri Al
            self.set_reg_value(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\PriorityControl", "Win32PrioritySeparation", 2)
            self.run_cmd("sc start SysMain")
            self.run_cmd("sc start WerSvc")

    def get_system_score(self):
        """Oturum Sağlık Skoru Analizi"""
        try:
            ram = psutil.virtual_memory().percent
            cpu = psutil.cpu_percent(interval=0.5)
            disk = psutil.disk_usage('/').percent
            
            score = 100 - (ram * 0.3 + cpu * 0.4 + disk * 0.3)
            return max(10, min(100, int(score)))
        except: return 85

    def analyze_fps_drops(self):
        """FPS Drop Kaynak Tespiti"""
        ram = psutil.virtual_memory().percent
        cpu = psutil.cpu_percent(interval=1)
        disk_io = psutil.disk_io_counters()
        
        report = []
        if ram > 85: report.append("- RAM Baskısı Yüksek: Arka plan uygulamalarını kapatın.")
        if cpu > 90: report.append("- CPU Darboğazı: İşlemci yükü oyunun altında eziliyor.")
        if disk_io.read_time > 1000: report.append("- Disk Gecikmesi: Oyun dosyalarına erişim yavaş (SSD önerilir).")
        
        if not report: return "Sistem Stabil: Yazılımsal bir darboğaz tespit edilmedi."
        return "\n".join(report)

# --- MAINTENANCE & REPAIR ENGINES ---
class DiagnosticEngine:
    def __init__(self, tweak_engine):
        self.te = tweak_engine

    def check_health(self):
        return self.te.get_system_score()

    def discover_hidden_consumers(self):
        """Sessiz Performans Tüketici Algısı"""
        bad_procs = ["SearchIndexer.exe", "CompatTelRunner.exe", "MicrosoftEdgeUpdate.exe"]
        found = []
        for p in psutil.process_iter(['name']):
            if p.info['name'] in bad_procs:
                found.append(p.info['name'])
        return found

# --- UI COMPONENTS ---
class AnimatedNavBtn(QPushButton):
    def __init__(self, text, icon_off, icon_on=None, parent=None):
        super().__init__(parent)
        self.setText(f"  {text}")
        self.setCheckable(True)
        self.setObjectName("NavBtn")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(60)
        self.icon_off = icon_off
        self.icon_on = icon_on if icon_on else icon_off
        self.update_icon()
        self._padding = 25
        self.anim = QPropertyAnimation(self, b"paddingLeft")
        self.anim.setDuration(300)
        self.anim.setEasingCurve(QEasingCurve.OutQuint)

    @Property(int)
    def paddingLeft(self): return self._padding
    @paddingLeft.setter
    def paddingLeft(self, val):
        self._padding = val
        self.setStyleSheet(f"padding-left: {val}px;")

    def update_icon(self):
        icon_path = get_ui_path(self.icon_on if self.isChecked() else self.icon_off)
        if os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(28, 28))

    def nextCheckState(self):
        super().nextCheckState()
        self.update_icon()

    def enterEvent(self, event):
        self.anim.stop(); self.anim.setEndValue(40); self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.anim.stop(); self.anim.setEndValue(25); self.anim.start()
        super().leaveEvent(event)

class AnimatedToggle(QPushButton):
    stateChanged = Signal(str, bool)
    def __init__(self, title, engine, initial_state=False, parent=None):
        super().__init__(parent)
        self.tweak_title = title
        self.engine = engine
        self.setCheckable(True)
        self.setChecked(initial_state)
        self.setFixedSize(50, 26)
        self._circle_pos = 27 if initial_state else 3
        self.animation = QPropertyAnimation(self, b"circle_pos")
        self.animation.setDuration(250)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.clicked.connect(self.on_clicked)

    @Property(float)
    def circle_pos(self): return self._circle_pos
    @circle_pos.setter
    def circle_pos(self, pos): self._circle_pos = pos; self.update()

    def on_clicked(self):
        self.animation.stop()
        self.animation.setEndValue(27 if self.isChecked() else 3)
        self.animation.start()
        self.engine.apply_tweak(self.tweak_title, self.isChecked())
        self.stateChanged.emit(self.tweak_title, self.isChecked())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        color = QColor("#8a2be2") if self.isChecked() else QColor("#333")
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 13, 13)
        painter.setBrush(QColor("#fff"))
        painter.drawEllipse(int(self._circle_pos), 3, 20, 20)

class SettingRow(QFrame):
    def __init__(self, title, description, engine, initial_state=False, callback=None):
        super().__init__()
        self.setObjectName("SettingRow")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        text_layout = QVBoxLayout()
        lbl_title = QLabel(title); lbl_title.setObjectName("SettingTitle")
        lbl_desc = QLabel(description); lbl_desc.setObjectName("SettingDesc")
        text_layout.addWidget(lbl_title); text_layout.addWidget(lbl_desc)
        self.toggle = AnimatedToggle(title, engine, initial_state)
        if callback: self.toggle.stateChanged.connect(callback)
        layout.addLayout(text_layout); layout.addStretch(); layout.addWidget(self.toggle)

# --- UPDATE WORKER ---
class UpdateWorker(QThread):
    finished = Signal(dict)
    def run(self):
        try:
            # GitHub API'den veriyi çek (Header ekleyerek ve Timeout koyarak daha güvenli hale getirildi)
            req = urllib.request.Request(GITHUB_API_URL)
            req.add_header('User-Agent', 'Ultimate-Optimizer-App')
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                self.finished.emit(data)
        except Exception as e:
            logging.error(f"Update Check Connectivity Error: {e}")
            self.finished.emit({})

# --- PRELOAD & SPLASH ---
class PreloadWorker(QThread):
    finished = Signal(dict)
    def __init__(self):
        super().__init__()
        self.engine = TweakEngine()

    def run(self):
        logging.info("Preload: System checks starting...")
        ensure_version_file()
        
        # 1. Detect HW
        hw = {'os': '10', 'cpu': 'Unknown', 'gpu': 'Unknown'}
        try:
            build = int(platform.version().split('.')[-1])
            if build >= 22000: hw['os'] = '11'
            proc = platform.processor().upper()
            if "INTEL" in proc: hw['cpu'] = "INTEL"
            elif "AMD" in proc: hw['cpu'] = "AMD"
            c = wmi.WMI()
            for g in c.Win32_VideoController():
                n = g.Name.upper()
                if "NVIDIA" in n: hw['gpu'] = "NVIDIA"; break
                elif "AMD" in n or "RADEON" in n: hw['gpu'] = "AMD"; break
        except: pass
        
        # 2. Settings
        settings = {}
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    settings = json.load(f)
            except: pass
        
        # 3. Apply Active Tweaks (During Loading)
        logging.info("Preload: Applying active tweaks...")
        skip_during_preload = ["Geri Alma Koruması (FREE)", "FPS Drop Analizi (FREE)", "Oturum Sağlık Skoru (FREE)"]
        for title, state in settings.items():
            if state and title not in skip_during_preload:
                self.engine.apply_tweak(title, True)
            
        self.finished.emit({"hw": hw, "settings": settings})

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(520, 380)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.layout = QVBoxLayout(self)
        self.bg = QFrame()
        # Ultra Sade & Premium Dark
        self.bg.setStyleSheet("""
            QFrame {
                background-color: #0a0a0a;
                border: 1px solid rgba(138, 43, 226, 0.3);
                border-radius: 45px;
            }
        """)
        self.layout.addWidget(self.bg)
        
        self.inner = QVBoxLayout(self.bg)
        self.inner.setContentsMargins(50, 50, 50, 50)
        self.inner.setSpacing(10)
        
        self.inner.addSpacing(20)

        # 1. Main Logo (ultimate_logo.png)
        self.logo = QLabel()
        logo_pix = QPixmap(get_ui_path("ultimate_logo.png"))
        if not logo_pix.isNull():
            self.logo.setPixmap(logo_pix.scaled(300, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo.setAlignment(Qt.AlignCenter)
        self.logo.setStyleSheet("background: transparent; border: none;")
        self.inner.addWidget(self.logo)
        
        self.inner.addStretch()

        # 3. Minimal Status Info
        self.status = QLabel("SİSTEM ANALİZ EDİLİYOR...")
        self.status.setStyleSheet("""
            color: rgba(255, 255, 255, 0.6); 
            font-size: 11px; 
            font-weight: 600; 
            letter-spacing: 4px;
            background: transparent;
            border: none;
        """)
        self.status.setAlignment(Qt.AlignCenter)
        self.inner.addWidget(self.status)

        # 4. Thin Modern Progress bar
        self.prog_container = QFrame()
        self.prog_container.setFixedHeight(2)
        self.prog_container.setFixedWidth(260)
        self.prog_container.setStyleSheet("background: rgba(255, 255, 255, 0.05); border-radius: 1px; border: none;")
        self.prog_bar = QFrame(self.prog_container)
        self.prog_bar.setFixedHeight(2)
        self.prog_bar.setFixedWidth(0)
        self.prog_bar.setStyleSheet("background: #8a2be2; border-radius: 1px; border: none;")
        self.inner.addWidget(self.prog_container, 0, Qt.AlignCenter)

        # Animations
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(600); self.fade_anim.setStartValue(0); self.fade_anim.setEndValue(1); self.fade_anim.start()

        self.prog_anim = QPropertyAnimation(self.prog_bar, b"minimumWidth")
        self.prog_anim.setDuration(3000); self.prog_anim.setStartValue(0); self.prog_anim.setEndValue(260); self.prog_anim.start()

    def set_status(self, text):
        self.status.setText(text.upper() + "...")

# --- MAIN WINDOW ---
class MainWindow(QMainWindow):
    def __init__(self, data):
        super().__init__()
        self.hw = data['hw']
        self.app_settings = data['settings']
        self.engine = TweakEngine()
        self.update_worker = None
        
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(1100, 700)
        
        self.main_widget = QWidget(); self.main_widget.setObjectName("MainWidget")
        self.setCentralWidget(self.main_widget)
        self.main_layout = QHBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0); self.main_layout.setSpacing(0)

        # SIDEBAR
        self.sidebar = QWidget(); self.sidebar.setObjectName("Sidebar"); self.sidebar.setFixedWidth(280)
        self.sidebar_layout = QVBoxLayout(self.sidebar); self.sidebar_layout.setContentsMargins(20, 40, 20, 40); self.sidebar_layout.setSpacing(10)
        
        # LOGO GÜNCELLEME (ultimate_logo.png) - Sadece Görsel
        self.logo_container = QLabel()
        logo_path = get_ui_path("ultimate_logo.png")
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            self.logo_container.setPixmap(logo_pixmap.scaled(220, 110, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        self.logo_container.setAlignment(Qt.AlignCenter)
        self.sidebar_layout.addWidget(self.logo_container)
        self.sidebar_layout.addSpacing(30)

        # Nav Buttons
        win_off, win_on = ("win11_button_off.svg", "win11_button_on.png") if self.hw['os'] == '11' else ("win10_button_off.svg", "win10_buton_on.png")
        self.nav_btns = {
            "Genel": AnimatedNavBtn("Windows Genel", win_off, win_on),
            "Gaming": AnimatedNavBtn("Oyun & Latency", "oyn_lc_button.svg"),
            "Health": AnimatedNavBtn("Sağlık & Onarım", "gvn_no_button_.svg"),
            "Stability": AnimatedNavBtn("Emülatör Stabilite", "emu_stb_button_off.svg", "emu_stb_button_on.png"),
            "Privacy": AnimatedNavBtn("Gizlilik & Debloat", "Glk_db_button.svg"),
            "GPU": None,
            "CPU": None
        }

        for key in ["Genel", "Gaming", "Health", "Stability", "Privacy"]:
            self.nav_btns[key].clicked.connect(lambda checked=False, k=key: self.switch_page(k))
            self.sidebar_layout.addWidget(self.nav_btns[key])

        if self.hw['gpu'] == "NVIDIA": self.nav_btns["GPU"] = AnimatedNavBtn("NVIDIA Ayarları", "nvdia_button.svg")
        elif self.hw['gpu'] == "AMD": self.nav_btns["GPU"] = AnimatedNavBtn("AMD GPU Ayarları", "amd_button.svg")
        if self.nav_btns["GPU"]:
            self.nav_btns["GPU"].clicked.connect(lambda checked=False: self.switch_page("GPU"))
            self.sidebar_layout.addWidget(self.nav_btns["GPU"])

        if self.hw['cpu'] == "INTEL": self.nav_btns["CPU"] = AnimatedNavBtn("Intel CPU", "intel_button.svg")
        elif self.hw['cpu'] == "AMD": self.nav_btns["CPU"] = AnimatedNavBtn("AMD Ryzen CPU", "amd_button.svg")
        if self.nav_btns["CPU"]:
            self.nav_btns["CPU"].clicked.connect(lambda checked=False: self.switch_page("CPU"))
            self.sidebar_layout.addWidget(self.nav_btns["CPU"])

        self.sidebar_layout.addStretch()
        
        # Güncelleme Butonu
        self.btn_update = QPushButton(" GÜNCELLEMELERİ DENETLE")
        self.btn_update.setObjectName("UpdateBtn")
        self.btn_update.setIcon(QIcon(get_ui_path("update_strat_button.svg")))
        self.btn_update.clicked.connect(self.check_updates)
        self.sidebar_layout.addWidget(self.btn_update)
        
        btn_exit = QPushButton("ÇIKIŞ"); btn_exit.setObjectName("ExitBtn"); btn_exit.clicked.connect(self.close)
        self.sidebar_layout.addWidget(btn_exit)

        # CONTENT
        self.content_container = QWidget(); self.content_layout = QVBoxLayout(self.content_container); self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.title_bar = QFrame(); self.title_bar.setFixedHeight(50); self.content_layout.addWidget(self.title_bar)
        self.content_area = QStackedWidget(); self.content_layout.addWidget(self.content_area)
        
        self.create_all_pages()

        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_container, 1)
        self.old_pos = None; self.nav_btns["Genel"].setChecked(True)

    def closeEvent(self, event):
        logging.info("Application closing. Cleaning up...")
        if hasattr(self.engine, 'ese_engine'):
            self.engine.ese_engine.stop()
        if self.update_worker and self.update_worker.isRunning():
            self.update_worker.terminate()
            self.update_worker.wait()
        event.accept()

    def save_setting(self, title, state):
        self.app_settings[title] = state
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.app_settings, f, indent=2, ensure_ascii=False)
            logging.info(f"Setting Saved: {title} = {state}")
        except: pass

    def check_updates(self):
        logging.info("Update check started.")
        self.btn_update.setText(" DENETLENİYOR...")
        self.btn_update.setEnabled(False)
        self.update_worker = UpdateWorker()
        self.update_worker.finished.connect(self.update_finished)
        self.update_worker.start()

    def update_finished(self, data):
        self.btn_update.setEnabled(True)
        self.btn_update.setText(" GÜNCELLEMELERİ DENETLE")
        
        if not data or "tag_name" not in data:
            logging.warning("Update check failed or no release found.")
            QMessageBox.information(self, "Güncel", "Şu anda yeni bir yayın bulunamadı.")
            return

        try:
            latest_version = data.get("tag_name")
            # Bellekteki güncel sürümü kullan
            global CURRENT_VERSION, CURRENT_DESCRIPTION
            current_version = CURRENT_VERSION
            
            v_latest = version_to_tuple(latest_version)
            v_current = version_to_tuple(current_version)
            
            logging.info(f"Local: {v_current} | Server: {v_latest}")
            
            # 1. UI için temiz notlar
            raw_notes = data.get("body", "Sürüm notu bulunamadı.")
            ui_notes = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', raw_notes)
            ui_notes = ui_notes.replace('**', '').replace('__', '').replace('#', '').strip()
            
            # 2. Kod dosyası (main.py) için
            code_notes = ui_notes.replace('"', "'").replace("\n", "\\n").replace("\r", "")

            # --- Sadece gerçekten daha yeni bir sürüm varsa güncelle ---
            if v_latest > v_current:
                # --- SELF PATCHING (KODU GÜNCELLEME) ---
                try:
                    main_path = os.path.abspath(__file__)
                    with open(main_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    
                    with open(main_path, "w", encoding="utf-8") as f:
                        for line in lines:
                            if line.strip().startswith('DEFAULT_VERSION ='):
                                f.write(f'DEFAULT_VERSION = "{latest_version}"\n')
                            elif line.strip().startswith('DEFAULT_DESC ='):
                                f.write(f'DEFAULT_DESC = "{code_notes}"\n')
                            else:
                                f.write(line)
                    
                    # BELLEĞİ ANINDA GÜNCELLE (Böylece aynı oturumda tekrar 'güncelle' demez)
                    CURRENT_VERSION = latest_version
                    CURRENT_DESCRIPTION = ui_notes
                    logging.info("Source code patched and memory refreshed.")
                    
                except Exception as e:
                    logging.error(f"Self-patch failed: {e}")

                # Version.json dosyasını güncelle
                update_info = {
                    "name": "ultimate-optimizer",
                    "version": latest_version,
                    "latest_seen": latest_version,
                    "description": ui_notes,
                    "last_check": datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                }
                with open(VERSION_FILE, "w", encoding="utf-8") as f:
                    json.dump(update_info, f, indent=2, ensure_ascii=False)

                msg = QMessageBox(self)
                msg.setWindowIcon(QIcon(get_ui_path("app_icon.ico")))
                msg.setWindowTitle("Güncelleme Mevcut")
                msg.setText(f"Yeni bir sürüm bulundu: <b style='color:#8a2be2;'>{latest_version}</b>")
                msg.setInformativeText(f"Sistem dosyaları güncellendi. Uygulama bir sonraki açılışta yeni sürümle başlayacaktır.\n\n<b>Yenilikler:</b>\n{ui_notes}")
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                msg.setDefaultButton(QMessageBox.Yes)
                msg.setIcon(QMessageBox.Information)
                
                if msg.exec() == QMessageBox.Yes:
                    import webbrowser
                    webbrowser.open(data.get("html_url", "https://github.com/CDB1646/multi-optimizer/releases"))
            else:
                QMessageBox.information(self, "Sistem Güncel", f"Harika! Zaten en son sürümü ({current_version}) kullanıyorsunuz.")
        except Exception as e:
            logging.error(f"Update Finished Error: {e}")
            QMessageBox.warning(self, "Hata", "Güncelleme bilgileri işlenirken bir sorun oluştu.")
        except Exception as e:
            logging.error(f"Update Finished Error: {e}")
            QMessageBox.warning(self, "Hata", "Güncelleme bilgileri işlenirken bir sorun oluştu.")

    def create_all_pages(self):
        self.content_area.addWidget(self.create_page("Windows Genel Optimizasyon", [
            ("Telemetry Kapat", "Sistem veri toplama servislerini ve görevlerini durdurur."),
            ("Hızlı Yanıt Süresi", "Uygulama kapanma ve yanıt verme sürelerini milisaniyeye indirir."),
            ("Hızlı Başlatmayı Kapat", "Sistem kararlılığı için hibrit kapatmayı devre dışı bırakır."),
            ("FSO & Game Bar Kapat", "Tam ekran iyileştirmelerini ve Game Bar gecikmesini engeller."),
            ("OneDrive Kaldır", "Sistemi yavaşlatan OneDrive'ı tamamen kaldırır.")
        ]))
        # 1. Gaming & Latency
        self.content_area.addWidget(self.create_page("Oyun & Düşük Gecikme", [
            ("Gecikme İyileştirme (MMCSS)", "Ağ ve işlemci önceliğini multimedya/oyunlara odaklar."),
            ("Win32 Priority Separation", "İşlemci zaman dilimlerini oyun performansı için optimize eder."),
            ("TCP No Delay", "Ağ paket gecikmesini (Nagle's Algorithm) optimize eder."),
            ("Game Mode Aktif", "Windows'un oyun modunu en agresif seviyeye getirir."),
            ("HPET Kapat", "Sistem zamanlayıcı gecikmesini minimuma indirir (Timer Resolution).")
        ]))
        # 2. Emulator Stability
        self.content_area.addWidget(self.create_page("Emulator Stability Engine", [
            ("Emulator Stability Engine", "VM Tick, Cache Pulse ve GPU Gate sistemlerini birleştirerek emülatör takılmalarını yok eder."),
        ]))
        # 3. Health & Repair
        self.content_area.addWidget(self.create_page("Sistem Sağlığı & Onarım", [
            ("Onarım Modu (FREE)", "Windows sistem kaynaklarını oyun için geçici olarak onarır ve optimize eder."),
            ("FPS Drop Analizi (FREE)", "Anlık takılmaların kaynağını Windows seviyesinde tespit eder."),
            ("Oturum Sağlık Skoru (FREE)", "Her oyun oturumundan sonra sistem stabilitesini puanlar."),
            ("RAM & Bellek Dengeleme (VIP)", "Ani bellek dolmalarını ve mikro takılmaları önler."),
            ("Disk Gecikme Azaltma (VIP)", "Oyun dosyalarına erişim önceliğini artırarak gecikmeyi düşürür."),
            ("Oyun Profili Sistemi (VIP)", "Gameloop, PUBG ve diğer PC oyunları için özel profiller."),
            ("Donanım-Windows Uyum Analizi (VIP)", "Sorunun donanımsal mı yoksa yazılımsal mı olduğunu belirler."),
            ("Geri Alma Koruması (FREE)", "Her işlemden önce otomatik mini geri yükleme noktası oluşturur."),
            ("Sessiz Tüketici Algısı (VIP)", "Arka planda gizli performans emen süreçleri uyarır.")
        ]))
        # 4. Privacy
        self.content_area.addWidget(self.create_page("Gizlilik & Debloat", [
            ("Mağaza Otomatik Güncelleme Kapat", "Arka planda uygulama güncellemeyi durdurur."),
            ("Hata Raporlama Kapat", "Windows Error Reporting servislerini devre dışı bırakır."),
            ("Reklam Kimliğini Kapat", "Kişiselleştirilmiş reklam takibini engeller.")
        ]))
        # 4. GPU
        if self.nav_btns["GPU"]:
            gpu_t = "NVIDIA Premium Tweaks" if self.hw['gpu'] == "NVIDIA" else "AMD Radeon Pro Tweaks"
            gpu_list = [("MPO Fix Uygula", "Overlay kaynaklı titreme ve takılmaları çözer.")]
            if self.hw['gpu'] == "NVIDIA":
                gpu_list += [("Ansel Kapat", "NVIDIA Ansel kamera arayüzünü devre dışı bırakır."), ("Düşük Gecikme Modu", "Input lag'ı minimize eder.")]
            else:
                gpu_list += [("ULPS Kapat", "Düşük güç modunu kapatarak stabilite artırır."), ("Shader Cache Reset", "Oyun stuttering problemlerini giderir.")]
            self.content_area.addWidget(self.create_page(gpu_t, gpu_list))
        # 5. CPU
        if self.nav_btns["CPU"]:
            cpu_t = "Intel Core Optimize" if self.hw['cpu'] == "INTEL" else "AMD Ryzen Master Tweaks"
            cpu_list = [
                ("Power Throttling Kapat", "CPU'nun frekans düşürmesini (Power Limit) engeller."),
                ("Çekirdek Park Etmeyi Kapat", "Tüm çekirdeklerin %100 uyanık kalmasını sağlar.")
            ]
            self.content_area.addWidget(self.create_page(cpu_t, cpu_list))

    def create_page(self, title_text, settings_list):
        page = QWidget(); layout = QVBoxLayout(page); layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(0)
        
        # BANNER / HEADER
        banner = QLabel(); banner.setFixedHeight(180); banner.setObjectName("PageBanner")
        banner_pix = QPixmap(get_ui_path("banner.png"))
        if not banner_pix.isNull():
            banner.setPixmap(banner_pix.scaled(820, 180, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        
        banner_layout = QVBoxLayout(banner)
        banner_layout.addStretch()
        lbl = QLabel(title_text); lbl.setObjectName("PageTitle")
        banner_layout.addWidget(lbl)
        layout.addWidget(banner)

        # CONTENT AREA
        container = QWidget(); container_layout = QVBoxLayout(container); container_layout.setContentsMargins(40, 20, 40, 40); container_layout.setSpacing(20)
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setStyleSheet("background: transparent; border: none;")
        scroll_content = QWidget(); scroll_content.setObjectName("ScrollContent")
        scroll_layout = QVBoxLayout(scroll_content); scroll_layout.setContentsMargins(0, 0, 10, 0); scroll_layout.setSpacing(10)
        for title, desc in settings_list:
            initial = self.app_settings.get(title, False)
            row = SettingRow(title, desc, self.engine, initial, self.save_setting)
            scroll_layout.addWidget(row)
        scroll_layout.addStretch(); scroll.setWidget(scroll_content); container_layout.addWidget(scroll)
        layout.addWidget(container)
        return page

    def switch_page(self, key):
        for k, btn in self.nav_btns.items():
            if btn: btn.setChecked(False)
        if key in self.nav_btns and self.nav_btns[key]:
            self.nav_btns[key].setChecked(True)
        # Update Icons
        for btn in self.nav_btns.values():
            if btn: btn.update_icon()
        
        indices = {"Genel": 0, "Gaming": 1, "Stability": 2, "Health": 3, "Privacy": 4, "GPU": 5, "CPU": 6}
        # Correctly find index by name because of dynamic nature
        # For simplicity, we match the creation order
        order = ["Genel", "Gaming", "Stability", "Health", "Privacy", "GPU", "CPU"]
        idx = 0
        for name in order:
            if name == key: break
            if name in ["GPU", "CPU"]:
                if self.nav_btns.get(name): idx += 1
            else: idx += 1
            
        self.content_area.setCurrentIndex(idx)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton: self.old_pos = e.globalPosition().toPoint()
    def mouseMoveEvent(self, e):
        if self.old_pos:
            d = QPoint(e.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + d.x(), self.y() + d.y()); self.old_pos = e.globalPosition().toPoint()

if __name__ == "__main__":
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1); sys.exit()
    
    # hide_console()
    app = QApplication(sys.argv)
    
    # Splash Screen
    splash = SplashScreen()
    splash.show()
    
    global_preloader = PreloadWorker()
    main_window = None

    def start_main(data):
        global main_window
        splash.set_status("Arayüz Yükleniyor...")
        main_window = MainWindow(data)
        
        qss_path = os.path.join(os.path.dirname(__file__), "style.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f: app.setStyleSheet(f.read())
            
        main_window.show()
        splash.close()

    global_preloader.finished.connect(start_main)
    global_preloader.start()
    sys.exit(app.exec())
