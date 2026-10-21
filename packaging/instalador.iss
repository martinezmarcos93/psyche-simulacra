; Inno Setup 6 — instalador de PSYCHE SIMULACRA para Windows.
; Requiere haber corrido antes: pyinstaller packaging\psyche.spec --noconfirm
; Compilar con: "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" packaging\instalador.iss

#define AppName "Psyche Simulacra"
#define AppVersion "0.8.0"

[Setup]
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=Marcos Martinez
DefaultDirName={autopf}\PsycheSimulacra
DefaultGroupName={#AppName}
OutputDir=..\dist\instalador
OutputBaseFilename=PsycheSimulacra-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
; Instalación por usuario: no pide permisos de administrador
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear un acceso directo en el escritorio"; GroupDescription: "Accesos directos:"

[Files]
Source: "..\dist\PsycheSimulacra\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\PsycheSimulacra.exe"
Name: "{group}\Carpeta de corridas"; Filename: "{userdocs}\PsycheSimulacra"
Name: "{group}\Desinstalar {#AppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\PsycheSimulacra.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\PsycheSimulacra.exe"; Description: "Abrir {#AppName}"; Flags: nowait postinstall skipifsilent

; Las corridas viven en Documentos\PsycheSimulacra y NO se borran al desinstalar.
