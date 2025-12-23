@echo off
echo Ultimate Optimizer EXE Olusturuluyor...
pip install pyinstaller
pyinstaller --noconsole --onefile ^
    --icon="UI/app_icon.ico" ^
    --add-data "UI;UI" ^
    --add-data "style.qss;." ^
    --add-data "Version.json;." ^
    --name "UltimateOptimizer" ^
    main.py
echo Islem tamamlandi! "dist" klasorune bakiniz.
pause
