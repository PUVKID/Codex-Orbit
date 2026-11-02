[Setup]
AppId=CodexOrbit.Desktop
AppName=Codex Orbit
AppVersion=2.3.0
AppPublisher=Codex Orbit
DefaultDirName={localappdata}\Programs\CodexOrbit
DefaultGroupName=Codex Orbit
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
WizardStyle=modern dark includetitlebar
SetupIconFile=..\assets\Orbit.ico
WizardImageFile=..\assets\SetupBanner.bmp
WizardSmallImageFile=..\assets\SetupSmall.bmp
DisableProgramGroupPage=yes
DisableDirPage=no
OutputDir=..\배포
OutputBaseFilename=CodexOrbit-Setup
Compression=lzma2
SolidCompression=yes
UninstallDisplayIcon={app}\CodexOrbit.exe
CloseApplications=yes
SetupLogging=yes

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"

[LangOptions]
DialogFontName=NanumGothic
WelcomeFontName=NanumGothic

[Tasks]
Name: "desktopicon"; Description: "바탕화면 바로가기 만들기"; Flags: unchecked

[Files]
Source: "..\assets\NanumGothic-Bold.ttf"; DestDir: "{app}\assets"; Flags: ignoreversion
Source: "..\배포\CodexOrbit.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\배포\사용법.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\배포\기본_지침.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\배포\배포안내.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\배포\라이선스\*"; DestDir: "{app}\라이선스"; Flags: ignoreversion recursesubdirs
Source: "..\배포\소스와_재빌드.zip"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Codex Orbit"; Filename: "{app}\CodexOrbit.exe"
Name: "{group}\사용법"; Filename: "{app}\사용법.md"
Name: "{autodesktop}\Codex Orbit"; Filename: "{app}\CodexOrbit.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\CodexOrbit.exe"; Description: "Codex Orbit 실행"; Flags: nowait postinstall skipifsilent

[Code]
var
  PrivateFontPath: String;

function AddFontResourceExW(FileName: String; Flags: Cardinal; Reserved: Integer): Integer;
  external 'AddFontResourceExW@gdi32.dll stdcall';
function RemoveFontResourceExW(FileName: String; Flags: Cardinal; Reserved: Integer): Boolean;
  external 'RemoveFontResourceExW@gdi32.dll stdcall';

function InitializeSetup(): Boolean;
begin
  ExtractTemporaryFile('NanumGothic-Bold.ttf');
  PrivateFontPath := ExpandConstant('{tmp}\NanumGothic-Bold.ttf');
  Result := AddFontResourceExW(PrivateFontPath, $10, 0) > 0;
  if not Result then
    MsgBox('내장 글꼴을 읽을 수 없습니다. 설치 파일을 다시 확인해 주세요.', mbError, MB_OK);
end;

procedure InitializeWizard();
begin
  WizardForm.Font.Name := 'NanumGothic';
  WizardForm.Font.Style := [fsBold];
end;

procedure DeinitializeSetup();
begin
  if PrivateFontPath <> '' then
    RemoveFontResourceExW(PrivateFontPath, $10, 0);
end;
