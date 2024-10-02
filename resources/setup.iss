#define MyAppName "WoW Token Price Checker"
#define MyAppDescription "WoW Token Price Checker"
#define MyAppVersion "1.0.0.0"
#define MyAppPublisher "Caprine Logic"
#define MyAppExeName "wtpc.exe"
#define MyAppCopyright "Copyright (C) 2024 Caprine Logic"

[Setup]
AppId={{7051B4F3-365B-4A5A-9108-F795A59562A2}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL=https://github.com/depthbomb/wtpc
AppSupportURL=https://github.com/depthbomb/wtpc
AppUpdatesURL=https://github.com/depthbomb/wtpc
AppCopyright={#MyAppCopyright}
VersionInfoVersion={#MyAppVersion}
DefaultDirName={autopf}\{#MyAppPublisher}\{#MyAppName}
DisableDirPage=yes
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
AllowNoIcons=yes
LicenseFile=..\LICENSE
OutputDir=.\..\build
OutputBaseFilename=wtpc_setup
SetupIconFile=.\icons\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
WizardResizable=no
;WizardImageFile=.\images\Image_*.bmp
;WizardSmallImageFile=.\images\SmallImage_*.bmp
ArchitecturesAllowed=x64
UninstallDisplayIcon={app}\wtpc.exe
UninstallDisplayName={#MyAppName} - {#MyAppDescription}
ShowTasksTreeLines=True
AlwaysShowDirOnReadyPage=True
VersionInfoCompany={#MyAppPublisher}
VersionInfoCopyright={#MyAppCopyright}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}
VersionInfoProductTextVersion={#MyAppVersion}
VersionInfoDescription={#MyAppDescription}

[Code]
function FromUpdate: Boolean;
begin
	Result := ExpandConstant('{param:update|no}') = 'yes'
end;

function FromNormal: Boolean;
begin
	Result := FromUpdate = False
end;

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}";

[Files]
Source: "..\build\wtpc.dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent; Check: FromUpdate
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent unchecked; Check: FromNormal

[UninstallDelete]
Type: filesandordirs; Name: "{app}\*"
Type: dirifempty; Name: "{app}"
