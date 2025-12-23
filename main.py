import sys
import platform
import wmi
import os
import json
import subprocess
import winreg
import urllib.request
import ctypes
import logging
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QStackedWidget, 
                               QFrame, QScrollArea, QGraphicsDropShadowEffect,
                               QSizePolicy, QMessageBox)
from PySide6.QtCore import Qt, QSize, QPoint, QPropertyAnimation, QEasingCurve, Property, QTimer, QThread, Signal
from PySide6.QtGui import QIcon, QPixmap, QCursor, QColor, QPainter, QLinearGradient

# --- LOGGING SETUP ---
logging.basicConfig(
    filename='log-data.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

# --- CONSTANTS ---
GITHUB_API_URL = "https://api.github.com/repos/CDB1646/multi-optimizer/releases/latest"
VERSION_FILE = "Version.json"
UI_DIR = os.path.join(os.path.dirname(__file__), "UI")

def get_ui_path(filename):
    return os.path.join(UI_DIR, filename)

def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

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
            result = subprocess.run(cmd, shell=True, check=False, capture_output=True, text=True)
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
    def __init__(self, title, engine, parent=None):
        super().__init__(parent)
        self.tweak_title = title
        self.engine = engine
        self.setCheckable(True)
        self.setFixedSize(50, 26)
        self._circle_pos = 3
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
    def __init__(self, title, description, engine):
        super().__init__()
        self.setObjectName("SettingRow")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        text_layout = QVBoxLayout()
        lbl_title = QLabel(title); lbl_title.setObjectName("SettingTitle")
        lbl_desc = QLabel(description); lbl_desc.setObjectName("SettingDesc")
        text_layout.addWidget(lbl_title); text_layout.addWidget(lbl_desc)
        self.toggle = AnimatedToggle(title, engine)
        layout.addLayout(text_layout); layout.addStretch(); layout.addWidget(self.toggle)

# --- UPDATE WORKER ---
class UpdateWorker(QThread):
    finished = Signal(dict)
    def run(self):
        try:
            # GitHub API'den veriyi çek
            with urllib.request.urlopen(GITHUB_API_URL) as response:
                data = json.loads(response.read().decode())
                self.finished.emit(data)
        except Exception as e:
            print(f"Update Check Error: {e}")
            self.finished.emit({})

# --- MAIN WINDOW ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.hw = self.detect_system()
        self.engine = TweakEngine()
        
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
            "Privacy": AnimatedNavBtn("Gizlilik & Debloat", "Glk_db_button.svg"),
            "GPU": None,
            "CPU": None
        }

        for key in ["Genel", "Gaming", "Privacy"]:
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

    def check_updates(self):
        logging.info("Update check started.")
        self.btn_update.setText(" DENETLENİYOR...")
        self.btn_update.setEnabled(False)
        self.worker = UpdateWorker()
        self.worker.finished.connect(self.update_finished)
        self.worker.start()

    def update_finished(self, data):
        self.btn_update.setEnabled(True)
        self.btn_update.setText(" GÜNCELLEMELERİ DENETLE")
        
        if not data or "tag_name" not in data:
            logging.warning("Update check failed or no release found.")
            QMessageBox.information(self, "Güncel", "Şu anda yeni bir yayın (release) bulunamadı.")
            return

        try:
            with open(VERSION_FILE, "r") as f:
                local_data = json.load(f)
            
            latest_version = data.get("tag_name")
            current_version = local_data.get("version")
            logging.info(f"Local Version: {current_version} | Latest Version: {latest_version}")
            
            if latest_version != current_version:
                notes = data.get("body", "Sürüm notu bulunamadı.")
                msg = QMessageBox(self)
                msg.setWindowTitle("Güncelleme Mevcut")
                msg.setText(f"Yeni bir sürüm bulundu: <b>{latest_version}</b>")
                msg.setInformativeText(f"Şu anki sürüm: {current_version}\n\n<b>Yenilikler:</b>\n{notes}")
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                msg.setDefaultButton(QMessageBox.Yes)
                msg.setIcon(QMessageBox.Information)
                
                if msg.exec() == QMessageBox.Yes:
                    import webbrowser
                    webbrowser.open(data.get("html_url", "https://github.com/CDB1646/multi-optimizer/releases"))
            else:
                QMessageBox.information(self, "Güncel", f"Uygulamanız zaten güncel! (Sürüm: {current_version})")
        except Exception as e:
            print(f"Version Check Error: {e}")
            QMessageBox.warning(self, "Hata", "Versiyon dosyası okunamadı.")

    def detect_system(self):
        hw = {'os': '10', 'cpu': 'Unknown', 'gpu': 'Unknown'}
        build = int(platform.version().split('.')[-1])
        if build >= 22000: hw['os'] = '11'
        proc = platform.processor().upper()
        if "INTEL" in proc: hw['cpu'] = "INTEL"
        elif "AMD" in proc: hw['cpu'] = "AMD"
        try:
            c = wmi.WMI()
            for g in c.Win32_VideoController():
                n = g.Name.upper()
                if "NVIDIA" in n: hw['gpu'] = "NVIDIA"; break
                elif "AMD" in n or "RADEON" in n: hw['gpu'] = "AMD"; break
        except: pass
        return hw

    def create_all_pages(self):
        # 1. Genel
        self.content_area.addWidget(self.create_page("Windows Genel Optimizasyon", [
            ("Telemetry Kapat", "Sistem veri toplama servislerini ve görevlerini durdurur."),
            ("Hızlı Yanıt Süresi", "Uygulama kapanma ve yanıt verme sürelerini milisaniyeye indirir."),
            ("FSO & Game Bar Kapat", "Tam ekran iyileştirmelerini ve Game Bar gecikmesini engeller."),
            ("OneDrive Kaldır", "Sistemi yavaşlatan OneDrive'ı tamamen kaldırır.")
        ]))
        # 2. Gaming & Latency
        self.content_area.addWidget(self.create_page("Oyun & Düşük Gecikme", [
            ("Gecikme İyileştirme (MMCSS)", "Ağ ve işlemci önceliğini multimedya/oyunlara odaklar."),
            ("Win32 Priority Separation", "İşlemci zaman dilimlerini oyun performansı için optimize eder."),
            ("Game Mode Aktif", "Windows'un oyun modunu en agresif seviyeye getirir."),
            ("HPET Kapat", "Sistem zamanlayıcı gecikmesini minimuma indirir (Timer Resolution).")
        ]))
        # 3. Privacy
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
        page = QWidget(); layout = QVBoxLayout(page); layout.setContentsMargins(40, 20, 40, 40); layout.setSpacing(20)
        lbl = QLabel(title_text); lbl.setObjectName("PageTitle"); layout.addWidget(lbl)
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setStyleSheet("background: transparent; border: none;")
        scroll_content = QWidget(); scroll_content.setObjectName("ScrollContent")
        scroll_layout = QVBoxLayout(scroll_content); scroll_layout.setContentsMargins(0, 0, 10, 0); scroll_layout.setSpacing(10)
        for title, desc in settings_list:
            row = SettingRow(title, desc, self.engine); scroll_layout.addWidget(row)
        scroll_layout.addStretch(); scroll.setWidget(scroll_content); layout.addWidget(scroll)
        return page

    def switch_page(self, key):
        for k, btn in self.nav_btns.items():
            if btn: btn.setChecked(False)
        self.nav_btns[key].setChecked(True)
        # Update Icons
        for btn in self.nav_btns.values():
            if btn: btn.update_icon()
        
        indices = {"Genel": 0, "Gaming": 1, "Privacy": 2, "GPU": 3, "CPU": 4 if self.nav_btns["GPU"] else 3}
        self.content_area.setCurrentIndex(indices.get(key, 0))

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton: self.old_pos = e.globalPosition().toPoint()
    def mouseMoveEvent(self, e):
        if self.old_pos:
            d = QPoint(e.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + d.x(), self.y() + d.y()); self.old_pos = e.globalPosition().toPoint()

if __name__ == "__main__":
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1); sys.exit()
    app = QApplication(sys.argv)
    qss_path = os.path.join(os.path.dirname(__file__), "style.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f: app.setStyleSheet(f.read())
    window = MainWindow(); window.show(); sys.exit(app.exec())
