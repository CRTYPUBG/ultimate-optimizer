import os
import sys
import logging
import json
import subprocess
import winreg
import ctypes
import psutil
import platform
import wmi
from datetime import datetime
from PySide6.QtCore import QThread, Signal

# We assume constants like DNA_FILE are passed or handled by paths
# For now, let's define a path helper or assume it's in config/

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
                    if not self.running: return
                    if proc.info['name'] in self.emulator_procs:
                        found_any = True
                        pid = proc.info['pid']
                        p = psutil.Process(pid)
                        
                        if pid not in self.active_pids:
                            p.nice(psutil.HIGH_PRIORITY_CLASS)
                            cores = list(range(psutil.cpu_count()))
                            if len(cores) > 2: p.cpu_affinity(cores[1:])
                            if hasattr(p, 'ionice'): p.ionice(psutil.IOPRIO_HIGH)
                            self.active_pids.add(pid)
                        
                        ctypes.windll.kernel32.SwitchToThread()
                        ctypes.windll.kernel32.SetPriorityClass(p.handle, 0x00000080)
                        self.msleep(10)

                if not found_any:
                    self.active_pids.clear()
                    for _ in range(10):
                        if not self.running: return
                        self.msleep(100)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied): continue
            except Exception as e:
                logging.error(f"ESE Worker Error: {e}")
                self.msleep(100)

    def restore_system(self):
        logging.info("ESE: Restoring system behavior...")
        self.running = False
        try:
            ntdll = ctypes.WinDLL('ntdll.dll')
            ntdll.NtSetTimerResolution(156250, 0, ctypes.byref(ctypes.c_ulong()))
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
        else:
            self.stop()

    def stop(self):
        if self.worker:
            self.worker.restore_system()
            self.worker.wait()
            self.worker = None

class ProOptimizerWorker(QThread):
    def __init__(self, settings_getter):
        super().__init__()
        self.get_settings = settings_getter
        self.running = True
        self.timer_active = False
        self.ntdll = ctypes.WinDLL('ntdll.dll')
        self.default_procs = ["csgo.exe", "valorant.exe", "r5apex.exe", "pubg.exe", "TslGame.exe", 
                             "aow_exe.exe", "AndroidProcess.exe", "FortniteClient-Win64-Shipping.exe",
                             "GTA5.exe", "League of Legends.exe", "Overwatch.exe"]

    def run(self):
        while self.running:
            try:
                settings = self.get_settings()
                game_procs = settings.get("TargetGameProcs", self.default_procs)
                is_gaming = False
                
                for proc in psutil.process_iter(['name', 'pid']):
                    try:
                        name = proc.info['name']
                        if name in game_procs:
                            is_gaming = True
                            p = psutil.Process(proc.info['pid'])
                            if settings.get("Core 0 Isolation", False):
                                cores = list(range(psutil.cpu_count()))
                                if len(cores) > 2:
                                    try:
                                        aff = p.cpu_affinity()
                                        if 0 in aff: p.cpu_affinity(cores[1:])
                                    except: pass
                            if settings.get("Disk I/O Burst Smoother", False):
                                if name in ["aow_exe.exe", "AndroidProcess.exe"]:
                                    try:
                                        if hasattr(p, 'ionice'): p.ionice(psutil.IOPRIO_HIGH)
                                    except: pass
                    except: continue

                if settings.get("Dynamic Timer Resolution", False):
                    if is_gaming and not self.timer_active:
                        self.ntdll.NtSetTimerResolution(5000, 1, ctypes.byref(ctypes.c_ulong()))
                        self.timer_active = True
                    elif not is_gaming and self.timer_active:
                        self.ntdll.NtSetTimerResolution(156250, 0, ctypes.byref(ctypes.c_ulong()))
                        self.timer_active = False

                if settings.get("Standby Memory Guard", False):
                    mem = psutil.virtual_memory()
                    if mem.percent > 85:
                        ctypes.windll.psapi.EmptyWorkingSet(ctypes.windll.kernel32.GetCurrentProcess())
                        subprocess.run("powershell -Command \"[System.GC]::Collect()\"", shell=True, capture_output=True)

                for _ in range(30):
                    if not self.running: return
                    self.msleep(100)
            except: self.msleep(1000)

    def stop(self):
        self.running = False
        if self.timer_active:
            self.ntdll.NtSetTimerResolution(156250, 0, ctypes.byref(ctypes.c_ulong()))
        self.wait()

class ProOptimizerEngine:
    def __init__(self, settings_getter):
        self.worker = None
        self.get_settings = settings_getter

    def start(self):
        if not self.worker:
            self.worker = ProOptimizerWorker(self.get_settings)
            self.worker.start()

    def stop(self):
        if self.worker:
            self.worker.stop()
            self.worker = None

class AdvancedCPUWorker(QThread):
    def __init__(self, settings_getter, dna_file_path):
        super().__init__()
        self.get_settings = settings_getter
        self.dna_file = dna_file_path
        self.running = True
        self.target_procs = ["csgo.exe", "valorant.exe", "r5apex.exe", "pubg.exe", "TslGame.exe", 
                            "aow_exe.exe", "AndroidProcess.exe", "FortniteClient-Win64-Shipping.exe",
                            "GTA5.exe", "League of Legends.exe", "Overwatch.exe"]
        self.topology = self._get_cpu_topology()
        self.dna_profiles = self._load_dna_profiles()
        self.active_analysis = {}
        self.applied_pids = set()

    def _get_cpu_topology(self):
        topo = {"P": [], "E": [], "Type": "Unknown"}
        try:
            count = psutil.cpu_count()
            p_count = int(count * 0.75) if count > 8 else count
            topo["P"] = list(range(p_count))
            topo["E"] = list(range(p_count, count)) if count > p_count else []
            if "INTEL" in platform.processor().upper(): topo["Type"] = "Intel"
            elif "AMD" in platform.processor().upper(): topo["Type"] = "AMD"
        except: topo["P"] = list(range(psutil.cpu_count()))
        return topo

    def _load_dna_profiles(self):
        if os.path.exists(self.dna_file):
            try:
                with open(self.dna_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: pass
        return {}

    def _save_dna_profiles(self):
        try:
            with open(self.dna_file, "w", encoding="utf-8") as f:
                json.dump(self.dna_profiles, f, indent=2, ensure_ascii=False)
        except: pass

    def run(self):
        ticker = 0
        while self.running:
            try:
                settings = self.get_settings()
                found_game = False
                current_time = datetime.now()
                active_pids = set()
                
                for proc in psutil.process_iter(['name', 'pid', 'cpu_percent']):
                    try:
                        name = proc.info['name']
                        if name in settings.get("TargetGameProcs", self.target_procs):
                            found_game = True
                            pid = proc.info['pid']
                            p = psutil.Process(pid)
                            active_pids.add(pid)
                            if settings.get("Adaptive Core Priority Masking (ACPM)", False):
                                if self.topology["E"]: p.cpu_affinity(self.topology["P"])
                                p.nice(psutil.HIGH_PRIORITY_CLASS)
                            if settings.get("Instruction Cache Locking (ICL-FPS)", False):
                                ctypes.windll.kernel32.SetPriorityClass(p.handle, 0x00000080)
                            if settings.get("FPS DNA MODE™", False):
                                if name in self.dna_profiles:
                                    if pid not in self.applied_pids:
                                        self._apply_dna_profile(p, self.dna_profiles[name])
                                        self.applied_pids.add(pid)
                                else: self._analyze_dna(p, name, current_time)
                    except: continue

                self.applied_pids &= active_pids
                items_to_del = [pid for pid in self.active_analysis if pid not in active_pids]
                for pid in items_to_del: del self.active_analysis[pid]

                if found_game and settings.get("Micro-Stutter Killer Loop", False):
                    for _ in range(20): ctypes.windll.kernel32.SwitchToThread()
                
                if settings.get("Clock Stabilization", False) and found_game and ticker % 10 == 0:
                    subprocess.run("powercfg -setacvalueindex scheme_current sub_processor processorsettingsmin 100", shell=True)
                    subprocess.run("powercfg -setactive scheme_current", shell=True)

                ticker += 1
                self.msleep(1000 if not found_game else 500)
            except: self.msleep(5000)

    def _analyze_dna(self, p, name, current_time):
        pid = p.pid
        if pid not in self.active_analysis:
            self.active_analysis[pid] = {'start_time': current_time, 'samples': [], 'migrations': 0, 'last_core': -1, 'threads': []}
        data = self.active_analysis[pid]
        try:
            curr = p.cpu_num()
            if data['last_core'] != -1 and curr != data['last_core']: data['migrations'] += 1
            data['last_core'] = curr
            data['samples'].append(p.cpu_percent())
            data['threads'].append(p.num_threads())
        except: return
        if (current_time - data['start_time']).total_seconds() > 180:
            profile = self._extract_dna(data, name)
            self.dna_profiles[name] = profile
            self._save_dna_profiles()
            del self.active_analysis[pid]

    def _extract_dna(self, data, name):
        avg_threads = sum(data['threads']) / len(data['threads'])
        mig_rate = data['migrations'] / len(data['samples'])
        max_s = max(data['samples'])
        if mig_rate < 0.2 and avg_threads < 16:
            return {"type": "STABLE_CORE", "priority": "HIGH", "core_lock": True, "preferred_cores": self.topology["P"][:4] if len(self.topology["P"]) > 4 else self.topology["P"]}
        elif max_s > 80 and mig_rate > 0.4:
            return {"type": "BURST", "priority": "ABOVE_NORMAL", "core_lock": False}
        else:
            return {"type": "LATENCY_SENSITIVE", "priority": "HIGH", "core_lock": True, "input_core": self.topology["P"][1] if len(self.topology["P"]) > 1 else 0}

    def _apply_dna_profile(self, p, profile):
        try:
            p.nice(psutil.HIGH_PRIORITY_CLASS if profile["priority"] == "HIGH" else psutil.ABOVE_NORMAL_PRIORITY_CLASS)
            if profile.get("core_lock", False) and "preferred_cores" in profile:
                p.cpu_affinity(profile["preferred_cores"])
            res = int(profile.get("timer_resolution", 0.5) * 10000)
            ctypes.WinDLL('ntdll.dll').NtSetTimerResolution(res, 1, ctypes.byref(ctypes.c_ulong()))
        except: pass

    def stop(self):
        self.running = False
        self.wait()

class AdvancedCPUEngine:
    def __init__(self, settings_getter, dna_file):
        self.worker = None
        self.get_settings = settings_getter
        self.dna_file = dna_file

    def start(self):
        if not self.worker:
            self.worker = AdvancedCPUWorker(self.get_settings, self.dna_file)
            self.worker.start()

    def stop(self):
        if self.worker:
            self.worker.stop()
            self.worker = None

class TweakEngine:
    def __init__(self, settings_getter=None, dna_file=None):
        self.settings_getter = settings_getter
        self.pro_engine = ProOptimizerEngine(settings_getter) if settings_getter else None
        self.adv_cpu_engine = AdvancedCPUEngine(settings_getter, dna_file) if settings_getter and dna_file else None

    def stop_all(self):
        if self.pro_engine: self.pro_engine.stop()
        if self.adv_cpu_engine: self.adv_cpu_engine.stop()
        if hasattr(self, 'ese_engine'): self.ese_engine.stop()

    @staticmethod
    def set_reg_value(root, path, name, value, vtype=winreg.REG_DWORD):
        try:
            key = winreg.CreateKeyEx(root, path, 0, winreg.KEY_ALL_ACCESS)
            winreg.SetValueEx(key, name, 0, vtype, value)
            winreg.CloseKey(key)
            return True
        except: return False

    @staticmethod
    def delete_reg_value(root, path, name):
        try:
            key = winreg.OpenKey(root, path, 0, winreg.KEY_ALL_ACCESS)
            winreg.DeleteValue(key, name)
            winreg.CloseKey(key)
            return True
        except: return False

    @staticmethod
    def run_cmd(cmd):
        try:
            subprocess.run(cmd, shell=True, check=False, capture_output=True)
            return True
        except: return False

    def apply_tweak(self, title, state):
        if title == "Telemetry Kapat":
            self.set_reg_value(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\DataCollection", "AllowTelemetry", 0 if state else 1)
            self.set_reg_value(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\DiagTrack", "Start", 4 if state else 2)
            if state: self.run_cmd("sc stop DiagTrack")
        elif title == "Hızlı Yanıt Süresi":
            self.set_reg_value(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", "AutoEndTasks", "1" if state else "0", winreg.REG_SZ)
        elif title == "Gecikme İyileştirme (MMCSS)":
            self.set_reg_value(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile", "SystemResponsiveness", 0 if state else 20)
        elif title == "Win32 Priority Separation":
            self.set_reg_value(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\PriorityControl", "Win32PrioritySeparation", 26 if state else 2)
        elif title == "Game Mode Aktif":
            self.set_reg_value(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\GameBar", "AllowAutoGameMode", 1 if state else 0)
        elif title == "FSO & Game Bar Kapat":
            self.set_reg_value(winreg.HKEY_CURRENT_USER, r"System\GameConfigStore", "GameDVR_Enabled", 0 if state else 1)
        elif title == "MPO Fix Uygula":
            self.set_reg_value(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\Dwm", "OverlayTestMode", 5 if state else 0)
        elif title == "HPET Kapat":
            self.run_cmd("bcdedit /set useplatformclock No" if state else "bcdedit /deletevalue useplatformclock")
        elif title == "Çekirdek Park Etmeyi Kapat":
            self.run_cmd("powercfg -setacvalueindex scheme_current sub_processor processorsettingsmin 100")
            self.run_cmd("powercfg -setactive scheme_current")
        elif title == "Emulator Stability Engine":
            if not hasattr(self, 'ese_engine'): self.ese_engine = EmulatorStabilityEngine()
            self.ese_engine.toggle(state)
        elif title == "Geri Alma Koruması (FREE)":
            if state: self.run_cmd("powershell -Command \"Checkpoint-Computer -Description 'Optimizer_Protect' -RestorePointType MODIFY_SETTINGS\"")
        elif title in ["Dynamic Timer Resolution", "Core 0 Isolation", "Disk I/O Burst Smoother", "Standby Memory Guard"]:
            if state and self.pro_engine: self.pro_engine.start()
        elif title == "GPU Interrupt Priority Lock": self.apply_gpu_interrupt_lock(state)
        elif title in ["Adaptive Core Priority Masking (ACPM)", "Instruction Cache Locking (ICL-FPS)", "FPS DNA MODE™", "Micro-Stutter Killer Loop", "Clock Stabilization"]:
            if state and self.adv_cpu_engine: self.adv_cpu_engine.start()

    def apply_gpu_interrupt_lock(self, state):
        try:
            c = wmi.WMI()
            gpu_pnp = None
            for gpu in c.Win32_VideoController():
                if gpu.PNPDeviceID and "PCI" in gpu.PNPDeviceID:
                    gpu_pnp = gpu.PNPDeviceID
                    break
            if not gpu_pnp: return
            base_path = fr"SYSTEM\CurrentControlSet\Enum\{gpu_pnp}\Device Parameters\Interrupt Management"
            if state:
                self.set_reg_value(winreg.HKEY_LOCAL_MACHINE, base_path + r"\MessageSignaledInterruptProperties", "MSISupported", 1)
                aff_path = base_path + r"\Affinity Policy"
                self.set_reg_value(winreg.HKEY_LOCAL_MACHINE, aff_path, "DevicePriority", 3)
                self.set_reg_value(winreg.HKEY_LOCAL_MACHINE, aff_path, "AssignmentPolicy", 4)
                cores = psutil.cpu_count()
                mask = 1 << (cores - 1)
                self.set_reg_value(winreg.HKEY_LOCAL_MACHINE, aff_path, "TargetProcessors", mask, winreg.REG_QWORD if cores > 32 else winreg.REG_DWORD)
            else:
                aff_path = base_path + r"\Affinity Policy"
                self.delete_reg_value(winreg.HKEY_LOCAL_MACHINE, aff_path, "DevicePriority")
                self.delete_reg_value(winreg.HKEY_LOCAL_MACHINE, aff_path, "AssignmentPolicy")
                self.delete_reg_value(winreg.HKEY_LOCAL_MACHINE, aff_path, "TargetProcessors")
        except: pass

    def get_system_score(self):
        try:
            ram = psutil.virtual_memory().percent
            cpu = psutil.cpu_percent(interval=0.5)
            disk = psutil.disk_usage('/').percent
            score = 100 - (ram * 0.3 + cpu * 0.4 + disk * 0.3)
            return max(10, min(100, int(score)))
        except: return 85

class SystemMonitorWorker(QThread):
    stats = Signal(dict)
    def __init__(self):
        super().__init__()
        self.running = True
        self._wmi_cached = None

    def run(self):
        try: 
            self._wmi_cached = wmi.WMI()
        except: pass

        while self.running:
            try:
                cpu = psutil.cpu_percent(interval=None)
                ram = psutil.virtual_memory().percent
                disk = psutil.disk_usage('C:').percent
                
                gpu = 0
                if self._wmi_cached:
                    try:
                        counters = self._wmi_cached.Win32_PerfFormattedData_GPUPerformanceCounters_GPUAdapterMemory()
                        if counters: gpu = int(float(counters[0].PercentMemoryUsage))
                    except: pass

                self.stats.emit({'cpu': cpu, 'ram': ram, 'disk': disk, 'gpu': gpu})
            except: pass
            
            for _ in range(10):
                if not self.running: return
                self.msleep(100)

    def stop(self):
        self.running = False
        self.wait()

class OptimizerApp:
    def __init__(self):
        from .security import is_admin, request_admin
        from .logger import setup_logger
        
        if not is_admin():
            request_admin()
            sys.exit(0)
            
        setup_logger()
        logging.info("OptimizerApp Initialized")

    def run(self):
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QTimer
        from ui.main_window import MainWindow, SplashScreen
        from .config import SETTINGS_FILE

        app = QApplication(sys.argv)
        
        splash = SplashScreen()
        splash.show()
        splash.set_status("Sistem Analiz Ediliyor")
        
        hw = self._detect_hardware()
        
        splash.set_status("Ayarlar Yükleniyor")
        settings = {}
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    settings = json.load(f)
            except: pass
            
        data = {"hw": hw, "settings": settings}
        window = MainWindow(data)
        
        QTimer.singleShot(2500, lambda: [splash.close(), window.show()])
        sys.exit(app.exec())

    def _detect_hardware(self):
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
        except Exception as e:
            logging.error(f"Hardware detection error: {e}")
        return hw
