@echo off
:: Change directory to script location to avoid System32 error
cd /d "%~dp0"
echo Ultimate Optimizer EXE Olusturuluyor...

:: PyInstaller calistiriliyor (Security Pack: AES-256 Equivalent Encryption)
pyinstaller --noconsole --onefile --clean ^
    --key "CRTY_SEC_PACK_256" ^
    --icon="../assets/icons/app_icon.ico" ^
    --add-data "../assets/icons;assets/icons" ^
    --add-data "../src/ui/style.qss;src/ui" ^
    --add-data "../config/Version.json;config" ^
    --name "UltimateOptimizer" ^
    "../src/main.py"

echo.
echo Islem tamamlandi! "dist" klasorune bakiniz.
pause
