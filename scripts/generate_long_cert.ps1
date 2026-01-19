# Yönetici izni kontrolü (Self-Elevation)
if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "Yönetici izni gerekiyor. Script yeniden başlatılıyor..." -ForegroundColor Yellow
    Start-Process powershell.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

# Sertifika Bilgileri
$certName = "CRTYPUBG"
$pfxPath = "C:\Users\LenovoPC\cert.pfx"
$cerPath = "C:\Users\LenovoPC\cert.cer"
$password = "ueo586_crty555"
$notAfter = Get-Date -Year 2030 -Month 6 -Day 1

Write-Host "Yeni uzun ömürlü sertifika oluşturuluyor (Bitiş: $notAfter)..." -ForegroundColor Cyan

# Eski sertifikaları yedekle (varsa)
if (Test-Path $pfxPath) { Rename-Item $pfxPath "$pfxPath.bak" -Force }
if (Test-Path $cerPath) { Rename-Item $cerPath "$cerPath.bak" -Force }

# Yeni Sertifikayı Oluştur
$newCert = New-SelfSignedCertificate -Type Custom -Subject "CN=$certName" -KeyUsage DigitalSignature -FriendlyName "$certName Certificate" -CertStoreLocation "Cert:\LocalMachine\My" -NotAfter $notAfter -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3")

# PFX Olarak Dışa Aktar
$securePassword = ConvertTo-SecureString -String $password -Force -AsPlainText
Export-PfxCertificate -Cert $newCert -FilePath $pfxPath -Password $securePassword

# CER Olarak Dışa Aktar (Genel anahtar)
Export-Certificate -Cert $newCert -FilePath $cerPath

Write-Host "✅ Yeni sertifika başarıyla oluşturuldu!" -ForegroundColor Green
Write-Host "PFX: $pfxPath"
Write-Host "CER: $cerPath"
Write-Host "Geçerlilik Bitiş: 01.06.2030" -ForegroundColor Yellow

# Sertifikayı sisteme güvenilir olarak ekle
Write-Host "Sertifika sisteme güvenilir kök olarak tanıtılıyor..." -ForegroundColor Cyan
Import-Certificate -FilePath $cerPath -CertStoreLocation "Cert:\LocalMachine\Root"
Import-Certificate -FilePath $cerPath -CertStoreLocation "Cert:\LocalMachine\AuthRoot"
Import-Certificate -FilePath $cerPath -CertStoreLocation "Cert:\LocalMachine\TrustedPublisher"

Write-Host "🚀 İşlem TAMAMLANDI. Artık uygulamalarını imzalayabilirsin." -ForegroundColor Green
