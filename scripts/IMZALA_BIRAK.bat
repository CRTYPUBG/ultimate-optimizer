@echo off
title CRTY_GLOBAL Auto-Signer
set SIGNTOOL="C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe"
set PFX="C:\Users\LenovoPC\crty_global.pfx"
set PASS=ueo586_crty555

if "%~1"=="" (
    echo.
    echo [ HATALİ KULLANİM ]
    echo Lutfen imzalamak istediginiz dosyayi bu ikonun uzerine surukleyin.
    pause
    exit
)

echo.
echo === CRTY_GLOBAL IMZALAMA ISLEMI ===
echo Dosya: %~nx1
echo.

%SIGNTOOL% sign /f %PFX% /p %PASS% /tr http://timestamp.digicert.com /td sha256 /fd sha256 "%~1"

if %errorlevel% equ 0 (
    echo.
    echo [ BASARİLİ ] Dosya imzalandi ve zaman damgasi eklendi.
    timeout /t 3
) else (
    echo.
    echo [ HATA ] Imzalama basarisiz oldu!
    pause
)
