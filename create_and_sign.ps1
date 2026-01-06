# Ultimate Optimizer Sertifika İmzalama & Root Güvenlik Scripti
$pfxFile = "C:\Users\LenovoPC\cert.pfx"
$cerFile = "C:\Users\LenovoPC\cert.cer"
$password = "ueo586_crty555"

# 1. Root Sertifikayı Güvenilir Yap (Sertifika Hatasını Giderir)
if (Test-Path $cerFile) {
    Write-Host "Sertifika Root (Güvenilir Kök Yetkilileri) klasörüne ekleniyor..." -ForegroundColor Cyan
    Import-Certificate -FilePath $cerFile -CertStoreLocation "Cert:\LocalMachine\Root" -ErrorAction SilentlyContinue
    Write-Host "Sertifika sisteme Root olarak tanıtıldı." -ForegroundColor Green
} else {
    Write-Host "UYARI: Root (.cer) dosyası bulunamadı, sadece imzalama yapılacak." -ForegroundColor Yellow
}

if (-not (Test-Path $pfxFile)) {
    Write-Host "HATA: Sertifika bulunamadı: $pfxFile" -ForegroundColor Red
    exit 1
}

# Signtool yolunu bul
$signtool = (Get-ChildItem -Path "C:\Program Files (x86)\Windows Kits\10\bin" -Filter "signtool.exe" -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.FullName -like "*x64*" } | Select-Object -First 1).FullName

if ($signtool) {
    Write-Host "Dosyalar imzalanıyor..." -ForegroundColor Cyan
    
    # Ana EXE'yi imzala
    if (Test-Path "dist\UltimateOptimizer.exe") {
        & $signtool sign /f $pfxFile /p $password /tr http://timestamp.digicert.com /td sha256 /fd sha256 "dist\UltimateOptimizer.exe"
        Write-Host "UltimateOptimizer.exe imzalandı." -ForegroundColor Green
    }

    # Eğer Inno Setup yüklüyse (Opsiyonel)
    # ISCC.exe ile derleme yaparken imzalama tetiklenebilir.
} else {
    Write-Host "signtool.exe bulunamadı. Lütfen Windows SDK yüklü olduğundan emin olun." -ForegroundColor Red
}
