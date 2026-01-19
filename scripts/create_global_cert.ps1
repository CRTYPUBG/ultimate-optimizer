# Yönetici izni kontrolü
if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process powershell.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

# Dosya yolları
$desktop = "$env:USERPROFILE\Desktop"
$crtyPfx = Join-Path $desktop "crty_global.pfx"
$crtyCer = Join-Path $desktop "crty_global.cer"
$gameLoopPfx = Join-Path $desktop "gameloophub.pfx"
$gameLoopCer = Join-Path $desktop "gameloophub.cer"

$notAfter = Get-Date -Year 2035 -Month 1 -Day 1

# PFX şifresi güvenli şekilde soruluyor
$securePassword = Read-Host "PFX için şifre girin" -AsSecureString

Write-Host "✅ Sertifikalar Oluşturuluyor..." -ForegroundColor Cyan

try {
    # 1️⃣ CRYTIssuer Sertifikası (CRTY)
    $crtyCert = New-SelfSignedCertificate `
        -Type Custom `
        -Subject "CN=CRTY" `
        -CertStoreLocation "Cert:\LocalMachine\My" `
        -KeyExportPolicy Exportable `
        -KeyUsage DigitalSignature `
        -FriendlyName "CRTY Certificate"

    # CRYTIssuer dışa aktar
    Export-PfxCertificate -Cert $crtyCert -FilePath $crtyPfx -Password $securePassword
    Export-Certificate -Cert $crtyCert -FilePath $crtyCer

    # 2️⃣ GameLoopHUB Sertifikası (Verilen)
    $gameLoopCert = New-SelfSignedCertificate `
        -Type Custom `
        -Subject "CN=GameLoopHUB, E=help@gameloophub.com" `
        -CertStoreLocation "Cert:\LocalMachine\My" `
        -Signer $crtyCert `
        -NotAfter $notAfter `
        -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3") `
        -FriendlyName "GameLoopHUB Certificate"

    # GameLoopHUB dışa aktar
    Export-PfxCertificate -Cert $gameLoopCert -FilePath $gameLoopPfx -Password $securePassword
    Export-Certificate -Cert $gameLoopCert -FilePath $gameLoopCer

    # 3️⃣ Sisteme güvenilir olarak ekle (GameLoopHUB)
    Import-Certificate -FilePath $gameLoopCer -CertStoreLocation "Cert:\LocalMachine\Root"
    Import-Certificate -FilePath $gameLoopCer -CertStoreLocation "Cert:\LocalMachine\AuthRoot"
    Import-Certificate -FilePath $gameLoopCer -CertStoreLocation "Cert:\LocalMachine\TrustedPublisher"

    Write-Host "✅ İşlem Tamam!" -ForegroundColor Green
    Write-Host "📄 CRYTIssuer PFX: $crtyPfx" -ForegroundColor Yellow
    Write-Host "📄 CRYTIssuer CER: $crtyCer" -ForegroundColor Yellow
    Write-Host "📄 GameLoopHUB PFX: $gameLoopPfx" -ForegroundColor Yellow
    Write-Host "📄 GameLoopHUB CER: $gameLoopCer" -ForegroundColor Yellow

} catch {
    Write-Host "❌ Hata oluştu: $_" -ForegroundColor Red
}
