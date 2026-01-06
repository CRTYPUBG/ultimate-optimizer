@echo off
setlocal

:: 1. Sertifika ve İmzalama İşlemi (Ana EXE)
echo [1/3] Sertifika kontrol ediliyor ve dosyalar imzalanıyor...
powershell -ExecutionPolicy Bypass -File create_and_sign.ps1

:: 2. Inno Setup Derleyici Bul
echo [2/3] Inno Setup Derleyici aranıyor...
set "iscc="

:: Manuel check (En yaygın yollar)
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "iscc=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not defined iscc if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set "iscc=C:\Program Files\Inno Setup 6\ISCC.exe"

:: Kayıt defterinden kontrol (Daha sağlam)
if not defined iscc (
    for /f "tokens=2*" %%a in ('reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Inno Setup 6_is1" /v "InstallLocation" 2^>nul') do (
        if exist "%%b\ISCC.exe" set "iscc=%%b\ISCC.exe"
    )
)

if not defined iscc (
    echo [HATA] Inno Setup ISCC.exe bulunamadi.
    echo Lutfen Inno Setup 6 yuklu oldugundan emin olun.
    pause
    exit /b 1
)

echo Bulundu: "%iscc%"

echo [3/3] Installer derleniyor...
"%iscc%" setup.iss

echo.
echo [BONUS] Installer EXE imzalanıyor...
powershell -ExecutionPolicy Bypass -Command "$setup = Get-ChildItem -Path 'installer' -Filter 'UltimateOptimizer_Setup_v*.exe' | Sort-Object LastWriteTime -Descending | Select-Object -First 1; if ($setup) { $signtool = (Get-ChildItem -Path 'C:\Program Files (x86)\Windows Kits\10\bin' -Filter 'signtool.exe' -Recurse | Where-Object { $_.FullName -like '*x64*' } | Select-Object -First 1).FullName; if ($signtool) { Write-Host 'Imzalanan Dosya: ' $setup.FullName; & $signtool sign /f 'C:\Users\LenovoPC\cert.pfx' /p 'ueo586_crty555' /tr http://timestamp.digicert.com /td sha256 /fd sha256 $setup.FullName } }"

echo.
echo Islem tamamlandi. 'installer' klasörüne bakiniz.
pause
