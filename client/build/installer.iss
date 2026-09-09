; Script do Inno Setup — gera o instalador Windows (.exe) a partir do build do PyInstaller.
; Rodar no Windows, com o Inno Setup instalado: abra este arquivo no Inno Setup Compiler e compile,
; ou via linha de comando: iscc installer.iss
; Pré-requisito: já ter rodado "pyinstaller build/patrimonio.spec" antes (a pasta dist/SistemaPatrimonial deve existir).

#define MyAppName "Sistema de Controle Patrimonial"
#define MyAppVersion "1.0"
#define MyAppExeName "SistemaPatrimonial.exe"

[Setup]
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\SistemaPatrimonial
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=output
OutputBaseFilename=SistemaPatrimonial_Instalador
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar um ícone na área de trabalho"; GroupDescription: "Ícones adicionais:"

[Files]
; Pega TUDO que o PyInstaller gerou em dist/SistemaPatrimonial (exe + dlls + libs)
Source: "..\dist\SistemaPatrimonial\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Executar o sistema agora"; Flags: nowait postinstall skipifsilent
