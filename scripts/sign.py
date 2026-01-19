import sys
import os
import subprocess
import ctypes
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                               QLabel, QFileDialog, QMessageBox, QTextEdit)
from PySide6.QtCore import Qt

# --- CONFIGURATION ---
PFX_FILE = r"C:\Users\LenovoPC\cert.pfx"
PFX_PASS = "ueo586_crty555"
TIMESTAMP_URL = "http://timestamp.digicert.com"

# --- YÖNETİCİ KONTROLÜ ---
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Eğer yönetici değilse kendini yönetici olarak yeniden başlat
if not is_admin():
    print("Yönetici izni alınıyor...")
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

class SignToolApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CRTYPUBG Ultimate Signer (ADMIN MODE)")
        self.resize(550, 450)
        self.selected_file = None
        
        self.setStyleSheet("""
            QWidget { background-color: #1e1e1e; color: #ffffff; font-family: 'Segoe UI', sans-serif; }
            QPushButton { background-color: #8a2be2; border: none; padding: 12px; border-radius: 6px; font-weight: bold; font-size: 13px; }
            QPushButton:hover { background-color: #9b4dca; }
            QPushButton:disabled { background-color: #444; color: #888; }
            QTextEdit { background-color: #252526; border: 1px solid #333; border-radius: 5px; padding: 5px; font-family: Consolas; }
            QLabel { font-size: 14px; font-weight: 500; }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        self.lbl_info = QLabel(" 🛡️ YÖNETİCİ MODU AKTİF")
        self.lbl_info.setStyleSheet("color: #00ff7f; font-weight: bold;")
        self.lbl_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_info)

        # GÜVEN TUŞU (KESİN ÇÖZÜM)
        self.btn_trust = QPushButton("� ROOT YETKİSİNİ ZORLA (FIX TRUST)")
        self.btn_trust.setStyleSheet("background-color: #dc143c; color: white;")
        self.btn_trust.setCursor(Qt.PointingHandCursor)
        self.btn_trust.clicked.connect(self.fix_trust_force)
        layout.addWidget(self.btn_trust)

        layout.addSpacing(10)

        # Dosya Seçimi
        self.btn_select = QPushButton("📂 İmzalanacak Dosyayı Seç (.exe)")
        self.btn_select.setCursor(Qt.PointingHandCursor)
        self.btn_select.setStyleSheet("background-color: #444;")
        self.btn_select.clicked.connect(self.select_file)
        layout.addWidget(self.btn_select)

        self.lbl_path = QLabel("Dosya bekleniyor...")
        self.lbl_path.setStyleSheet("color: #888; font-size: 11px;")
        self.lbl_path.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_path)

        # İmzalama Tuşu
        self.btn_sign = QPushButton("✍️ İMZALA VE DOĞRULA")
        self.btn_sign.setCursor(Qt.PointingHandCursor)
        self.btn_sign.setEnabled(False)
        self.btn_sign.clicked.connect(self.start_signing)
        layout.addWidget(self.btn_sign)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

    def log(self, msg):
        self.log_area.append(msg)
        self.log_area.verticalScrollBar().setValue(self.log_area.verticalScrollBar().maximum())

    def fix_trust_force(self):
        cer_path = r"C:\Users\LenovoPC\cert.cer"
        if not os.path.exists(cer_path):
            QMessageBox.critical(self, "Hata", "cert.cer masaüstünde/ana dizinde bulunamadı!")
            return

        self.log("\n--- KÖK YETKİSİ ZORLANIYOR (BATCH MODU) ---")
        
        # Geçici Batch Dosyası Oluştur (Görünür olması için)
        bat_path = os.path.join(os.getcwd(), "fix_trust.bat")
        bat_content = f"""
@echo off
color 1f
title CRTYPUBG Sertifika Yukleyici
echo.
echo ===================================================
echo   CRTYPUBG SERTIFIKA GUVENLIK KURULUMU EKRANI
echo ===================================================
echo.
echo Islem Yonetici Olarak Yapiliyor...
echo.

echo [1/4] KOK SERTIFIKA (Root) ZORLANIYOR...
certutil -f -addstore "Root" "{cer_path}"
if %errorlevel% neq 0 ( color 4f & echo HATA! & pause & exit )

echo.
echo [2/4] YETKILI KOK (AuthRoot) ZORLANIYOR...
certutil -f -addstore "AuthRoot" "{cer_path}"

echo.
echo [3/4] GUVENILIR YAYINCI (TrustedPublisher) ZORLANIYOR...
certutil -f -addstore "TrustedPublisher" "{cer_path}"

echo.
echo [4/4] ARA SERTIFIKA (CA) ZORLANIYOR...
certutil -f -addstore "CA" "{cer_path}"

echo.
echo ===================================================
echo   ISLEM TAMAMLANDI! ARTIK GUVENLISINIZ.
echo ===================================================
echo.
pause
del "%~f0"
"""
        try:
            with open(bat_path, "w") as f:
                f.write(bat_content)
            
            # Batch dosyasını YÖNETİCİ olarak çalıştır ve GÖSTER (SW_SHOW = 5)
            # Bu sayede kullanıcı CMD ekranını görebilir.
            ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", bat_path, None, None, 1)
            
            if ret > 32: # Success
                 self.log("✅ Kurulum penceresi açıldı. Lütfen oradaki 'Başarılı' mesajını bekleyin.")
                 QMessageBox.information(self, "Bilgi", "Siyah CMD penceresi açıldı.\nLütfen o pencerenin işlemini bitirmesini bekleyin.")
            else:
                 self.log("❌ Yönetici izni reddedildi veya hata oluştu.")
                 
        except Exception as e:
            self.log(f"Kritik Hata: {e}")

    def find_signtool(self):
        base_paths = [r"C:\Program Files (x86)\Windows Kits\10\bin", r"C:\Program Files\Windows Kits\10\bin"]
        for base in base_paths:
            if not os.path.exists(base): continue
            for root, dirs, files in os.walk(base):
                if "signtool.exe" in files and "x64" in root: return os.path.join(root, "signtool.exe")
        return None

    def select_file(self):
        f, _ = QFileDialog.getOpenFileName(self, "Seç", "", "Executable (*.exe)")
        if f:
            self.selected_file = f
            self.lbl_path.setText(f)
            self.btn_sign.setEnabled(True)
            self.log(f"Dosya: {os.path.basename(f)}")

    def start_signing(self):
        if not self.selected_file: return
        signtool = self.find_signtool()
        if not signtool: return self.log("❌ Signtool bulunamadı!")

        self.log("\n--- İMZALANIYOR ---")
        cmd = [
            signtool, "sign", "/f", PFX_FILE, "/p", PFX_PASS, 
            "/tr", TIMESTAMP_URL, "/td", "sha256", "/fd", "sha256", 
            self.selected_file
        ]
        
        proc = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        if proc.returncode == 0:
            self.log("✅ İMZA ATILDI.")
            
            # Doğrulama
            self.log("--- DOĞRULANIYOR ---")
            v_cmd = [signtool, "verify", "/pa", "/v", self.selected_file]
            v_proc = subprocess.run(v_cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            if "Error" not in v_proc.stdout and "fail" not in v_proc.stdout:
                self.log("✅ DOĞRULAMA: GEÇERLİ (TRUSTED)")
                QMessageBox.information(self, "Mükemmel", "İmza atıldı ve sistem tarafından DOĞRULANDI.")
            else:
                self.log("⚠️ İmza var ama hala 'Kök' uyarısı veriyor.")
                self.log(v_proc.stdout)
        else:
            self.log(f"❌ İmza Hatası: {proc.stderr}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SignToolApp()
    window.show()
    sys.exit(app.exec())
