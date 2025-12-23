import sys
import platform
import wmi
import os
import json
import subprocess
import winreg
import urllib.request
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QStackedWidget, 
                               QFrame, QScrollArea, QGraphicsDropShadowEffect,
                               QSizePolicy, QMessageBox)
from PySide6.QtCore import Qt, QSize, QPoint, QPropertyAnimation, QEasingCurve, Property, QTimer, QThread, Signal
from PySide6.QtGui import QIcon, QPixmap, QCursor, QColor, QPainter, QLinearGradient

# --- CONSTANTS ---
GITHUB_API_URL = "https://api.github.com/repos/CDB1646/multi-optimizer"
VERSION_FILE = "Version.json"
UI_DIR = os.path.join(os.path.dirname(__file__), "UI")

def get_ui_path(filename):
    return os.path.join(UI_DIR, filename)

# --- TWEAK ENGINE ---
class TweakEngine:
    @staticmethod
    def set_reg_value(root, path, name, value, vtype=winreg.REG_DWORD):
        try:
            key = winreg.CreateKeyEx(root, path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, name, 0, vtype, value)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Registry Error: {e}")
            return False

    @staticmethod
    def run_cmd(cmd):
        try:
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
            return True
        except Exception as e:
            print(f"Command Error: {e}")
            return False

    def apply_tweak(self, title, state):
        print(f"Applying Tweak: {title} -> {state}")
        val = 1 if state else 0
        
        # Windows Genel
        if title == "Telemetry Kapat":
            self.set_reg_value(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\DataCollection", "AllowTelemetry", 0 if state else 1)
        elif title == "Game Bar Kapat":
            self.set_reg_value(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\GameDVR", "AppCaptureEnabled", 0 if state else 1)
        elif title == "Ultimate Performance":
            if state: self.run_cmd("powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61")
        
        # GPU / CPU Specific
        elif title == "MPO Fix Uygula":
            self.set_reg_value(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\Dwm", "OverlayTestMode", 0x00000005 if state else 0)
        elif title == "HPET Kapat":
            self.run_cmd("bcdedit /set useplatformclock No" if state else "bcdedit /deletevalue useplatformclock")

# --- UPDATE WORKER ---
class UpdateWorker(QThread):
    finished = Signal(dict)
    
    def run(self):
        try:
            req = urllib.request.Request(GITHUB_API_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                self.finished.emit(data)
        except Exception as e:
            print(f"Update Check Failed: {e}")
            self.finished.emit({})

# --- DONANIM ALGILAMA SINIFI ---
class HardwareManager:
    def __init__(self):
        try: self.c = wmi.WMI()
        except: self.c = None
        self.cpu_type = "Unknown"
        self.gpu_type = "Unknown"
        self.detect_hardware()

    def detect_hardware(self):
        proc_info = platform.processor()
        if "Intel" in proc_info: self.cpu_type = "INTEL"
        elif "AMD" in proc_info: self.cpu_type = "AMD"
        
        try:
            if self.c:
                for gpu in self.c.Win32_VideoController():
                    name = gpu.Name.upper()
                    if "NVIDIA" in name: self.gpu_type = "NVIDIA"; break
                    elif "AMD" in name or "RADEON" in name: self.gpu_type = "AMD"; break
        except: pass 
        print(f"Sistem Algılandı: CPU={self.cpu_type}, GPU={self.gpu_type}")

# --- ÖZEL TOGGLE BUTONU ---
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
        painter.drawEllipse(self._circle_pos, 3, 20, 20)

# --- AYAR SATIRI WIDGET'I ---
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

# --- ANA PENCERE ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.hw = HardwareManager()
        self.engine = TweakEngine()
        
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(1000, 650)
        
        self.main_widget = QWidget()
        self.main_widget.setObjectName("MainWidget")
        self.setCentralWidget(self.main_widget)
        self.main_layout = QHBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. SIDEBAR
        self.sidebar = QWidget(); self.sidebar.setObjectName("Sidebar"); self.sidebar.setFixedWidth(260)
        self.sidebar_layout = QVBoxLayout(self.sidebar); self.sidebar_layout.setContentsMargins(20, 40, 20, 40); self.sidebar_layout.setSpacing(10)
        
        lbl_logo = QLabel("ULTIMATE\nOPTIMIZER"); lbl_logo.setAlignment(Qt.AlignCenter); lbl_logo.setObjectName("LogoLabel")
        self.sidebar_layout.addWidget(lbl_logo); self.sidebar_layout.addSpacing(30)

        self.btn_genel = self.create_nav_btn("Windows Genel", None)
        self.sidebar_layout.addWidget(self.btn_genel)

        self.btn_gpu = None
        if self.hw.gpu_type == "NVIDIA":
            self.btn_gpu = self.create_nav_btn("NVIDIA Ayarları", "nvdia_button.svg")
            self.sidebar_layout.addWidget(self.btn_gpu)
        elif self.hw.gpu_type == "AMD":
            self.btn_gpu = self.create_nav_btn("AMD GPU Ayarları", "amd_button.svg")
            self.sidebar_layout.addWidget(self.btn_gpu)

        self.btn_cpu = None
        if self.hw.cpu_type == "INTEL":
            self.btn_cpu = self.create_nav_btn("Intel CPU", "intel_button.svg")
            self.sidebar_layout.addWidget(self.btn_cpu)
        elif self.hw.cpu_type == "AMD":
            self.btn_cpu = self.create_nav_btn("AMD Ryzen CPU", "amd_button.svg")
            self.sidebar_layout.addWidget(self.btn_cpu)

        self.sidebar_layout.addStretch()
        
        self.update_frame = QFrame(); self.update_layout = QHBoxLayout(self.update_frame); self.update_layout.setContentsMargins(0, 0, 0, 0)
        self.btn_update = QPushButton(" GÜNCELLEMELERİ DENETLE"); self.btn_update.setObjectName("UpdateBtn")
        self.btn_update.setIcon(QIcon(get_ui_path("update_strat_button.svg"))); self.btn_update.clicked.connect(self.check_for_updates)
        self.update_layout.addWidget(self.btn_update)
        
        self.loading_label = QLabel(); self.loading_label.setFixedSize(20, 20); self.loading_label.setScaledContents(True)
        self.loading_label.setPixmap(QPixmap(get_ui_path("update_loading_icon.svg"))); self.loading_label.hide()
        self.update_layout.addWidget(self.loading_label)
        self.sidebar_layout.addWidget(self.update_frame)
        
        btn_exit = QPushButton("SİSTEMDEN ÇIK"); btn_exit.setObjectName("ExitBtn"); btn_exit.clicked.connect(self.close)
        self.sidebar_layout.addWidget(btn_exit)

        # 2. CONTENT
        self.content_container = QWidget(); self.content_container.setObjectName("ContentContainer")
        self.content_layout = QVBoxLayout(self.content_container); self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.title_bar = QFrame(); self.title_bar.setFixedHeight(40); self.title_bar.setObjectName("TitleBar"); self.content_layout.addWidget(self.title_bar)
        self.content_area = QStackedWidget(); self.content_area.setObjectName("ContentArea"); self.content_layout.addWidget(self.content_area)
        
        # PAGES
        self.page_genel = self.create_page("Genel Windows Optimizasyonu", [
            ("Telemetry Kapat", "Windows veri takibini ve arka plan veri gönderimini durdurur."),
            ("Game Bar Kapat", "Xbox Game Bar etkileşimini ve FPS düşüşlerini engeller."),
            ("Ultimate Performance", "Windows Güç Planını 'Nihai Performans' moduna alır."),
            ("Hibernation Kapat", "Hızlı başlatmayı kapatarak kernel temizliğini sağlar."),
            ("FSO Devre Dışı", "Fullscreen Optimization'ı tüm oyunlar için optimize eder.")
        ])
        self.content_area.addWidget(self.page_genel)
        
        if self.btn_gpu:
            if self.hw.gpu_type == "NVIDIA":
                self.page_gpu = self.create_page("NVIDIA Gizli Ayarlar", [
                    ("Re-Size BAR Zorla", "rBAR desteği olmayan DX11/DX12 oyunlarda açar."),
                    ("Düşük Gecikme Modu", "Input lag'ı 'Ultra' seviyeye düşürür."),
                    ("Ansel Kapat", "Arka planda çalışan Ansel kamera servisini durdurur."),
                    ("HD Audio Devre Dışı", "Monitor hoparlörü kullanmıyorsanız DPC gecikmesini azaltır.")
                ])
            else:
                 self.page_gpu = self.create_page("AMD Radeon Ayarları", [
                    ("MPO Fix Uygula", "Multi-Plane Overlay kaynaklı ekran titremelerini yüzer."),
                    ("Shader Cache Reset", "Oyunlardaki anlık takılmaları (stutter) temizler."),
                    ("ULPS Kapat", "Düşük güç modunu kapatarak Crossfire/Single GPU kararlılığı artırır.")
                ])
            self.content_area.addWidget(self.page_gpu)

        if self.btn_cpu:
            cpu_title = "Intel İşlemci Ayarları" if self.hw.cpu_type == "INTEL" else "AMD Ryzen Ayarları"
            self.page_cpu = self.create_page(cpu_title, [
                ("Power Throttling Kapat", "İşlemcinin ağır yük altında frekans düşürmesini engeller."),
                ("Çekirdek Park Etmeyi Kapat", "Tüm CPU çekirdeklerini her zaman %100 uyanık tutar."),
                ("HPET Kapat", "High Precision Event Timer gecikmesini minimize eder.")
            ])
            self.content_area.addWidget(self.page_cpu)

        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_container, 1)
        self.old_pos = None; self.btn_genel.setChecked(True)

    def create_nav_btn(self, text, icon_name):
        btn = QPushButton(f"  {text}"); btn.setCheckable(True); btn.setObjectName("NavBtn")
        if icon_name:
            icon_path = get_ui_path(icon_name)
            if os.path.exists(icon_path): btn.setIcon(QIcon(icon_path)); btn.setIconSize(QSize(20, 20))
        btn.clicked.connect(lambda: self.switch_page(text))
        return btn

    def create_page(self, title_text, settings_list):
        page = QWidget(); layout = QVBoxLayout(page); layout.setContentsMargins(40, 20, 40, 40); layout.setSpacing(20)
        lbl = QLabel(title_text); lbl.setObjectName("PageTitle"); layout.addWidget(lbl)
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setStyleSheet("background: transparent; border: none;")
        scroll_content = QWidget(); scroll_content.setObjectName("ScrollContent")
        scroll_layout = QVBoxLayout(scroll_content); scroll_layout.setContentsMargins(0, 0, 10, 0); scroll_layout.setSpacing(10)
        for title, desc in settings_list:
            row = SettingRow(title, desc, self.engine)
            scroll_layout.addWidget(row)
        scroll_layout.addStretch(); scroll.setWidget(scroll_content); layout.addWidget(scroll)
        return page

    def switch_page(self, text):
        buttons = self.sidebar.findChildren(QPushButton, "NavBtn")
        for b in buttons: b.setChecked(False)
        sender = self.sender()
        if sender: sender.setChecked(True)
        if "Genel" in text: target_idx = 0
        elif "NVIDIA" in text or "AMD GPU" in text: target_idx = 1
        elif "CPU" in text or "Ryzen" in text: target_idx = 2 if self.btn_gpu else 1
        else: return
        self.content_area.setCurrentIndex(target_idx)

    def check_for_updates(self):
        self.btn_update.setEnabled(False); self.btn_update.setText(" DENETLENİYOR..."); self.loading_label.show()
        self.update_thread = UpdateWorker(); self.update_thread.finished.connect(self.on_update_result); self.update_thread.start()

    def on_update_result(self, data):
        self.btn_update.setEnabled(True); self.btn_update.setText(" GÜNCELLEMELERİ DENETLE"); self.loading_label.hide()
        if not data: return
        
        # Load local version
        try:
            with open(VERSION_FILE, "r") as f: local_data = json.load(f)
            if data["pushed_at"] != local_data["pushed_at"]:
                QMessageBox.information(self, "Güncelleme Mevcut", f"Yeni bir sürüm bulundu!\nSon Güncelleme: {data['pushed_at']}")
            else:
                QMessageBox.information(self, "Güncel", "Sisteminiz zaten en güncel sürümde.")
        except: pass

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.old_pos = event.globalPosition().toPoint()
    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()
    def mouseReleaseEvent(self, event): self.old_pos = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    qss_path = os.path.join(os.path.dirname(__file__), "style.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f: app.setStyleSheet(f.read())
    window = MainWindow(); window.show(); sys.exit(app.exec())
