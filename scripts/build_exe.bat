@echo off
:: Change directory to script location to avoid System32 error
cd /d "%~dp0"
echo Ultimate Optimizer EXE Olusturuluyor...

:: PyInstaller calistiriliyor
pyinstaller --noconsole --onefile --clean ^
    --icon="../assets/icons/app_icon.ico" ^
    --add-data "../assets/icons;assets/icons" ^
    --add-data "../src/ui/style.qss;src/ui" ^
    --add-data "../config/Version.json;config" ^
    --name "UltimateOptimizer" ^
    "../src/main.py"

echo.
echo Islem tamamlandi! "dist" klasorune bakiniz.
pause
