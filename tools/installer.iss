[Setup]
AppId=CodexOrbit.Desktop
AppName=Codex Orbit
AppVersion=2.11.0
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
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"

[LangOptions]
DialogFontName=SUIT
WelcomeFontName=SUIT

[CustomMessages]
korean.DesktopShortcut=바탕화면 바로가기 만들기
english.DesktopShortcut=Create a desktop shortcut
korean.UserGuide=사용법
english.UserGuide=User guide
korean.GuideFile=사용법.md
english.GuideFile=Usage.en.md
korean.LaunchApp=Codex Orbit 실행
english.LaunchApp=Launch Codex Orbit
korean.FontError=내장 글꼴을 읽을 수 없습니다. 설치 파일을 다시 확인해 주세요.
english.FontError=Could not load the bundled font. Please check the installer.

[Tasks]
Name: "desktopicon"; Description: "{cm:DesktopShortcut}"; Flags: unchecked

[Files]
Source: "..\배포\Usage.en.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\assets\SUIT-SemiBold.ttf"; DestDir: "{app}\assets"; Flags: ignoreversion
Source: "..\assets\SUIT-Medium.ttf"; DestDir: "{app}\assets"; Flags: ignoreversion
Source: "..\assets\SUIT-Regular.ttf"; DestDir: "{app}\assets"; Flags: ignoreversion
Source: "..\assets\NanumGothic-Bold.ttf"; DestDir: "{app}\assets"; Flags: ignoreversion
Source: "..\배포\CodexOrbit.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\배포\사용법.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\배포\기본_지침.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\배포\연도별_월_테마.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\배포\연도별_월_테마.csv"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\배포\연도별_월별_테마_전체.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\배포\연도별_월별_테마_전체.csv"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\배포\배포안내.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\배포\라이선스\*"; DestDir: "{app}\라이선스"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\Codex Orbit"; Filename: "{app}\CodexOrbit.exe"
Name: "{group}\{cm:UserGuide}"; Filename: "{app}\{cm:GuideFile}"
Name: "{autodesktop}\Codex Orbit"; Filename: "{app}\CodexOrbit.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\CodexOrbit.exe"; Description: "{cm:LaunchApp}"; Flags: nowait postinstall skipifsilent

[Code]
var
  PrivateFontPath: String;

function AddFontResourceExW(FileName: String; Flags: Cardinal; Reserved: Integer): Integer;
  external 'AddFontResourceExW@gdi32.dll stdcall';
function RemoveFontResourceExW(FileName: String; Flags: Cardinal; Reserved: Integer): Boolean;
  external 'RemoveFontResourceExW@gdi32.dll stdcall';

function InitializeSetup(): Boolean;
begin
  ExtractTemporaryFile('SUIT-SemiBold.ttf');
  PrivateFontPath := ExpandConstant('{tmp}\SUIT-SemiBold.ttf');
  Result := AddFontResourceExW(PrivateFontPath, $10, 0) > 0;
  if not Result then
    MsgBox(ExpandConstant('{cm:FontError}'), mbError, MB_OK);
end;

procedure InitializeWizard();
begin
  WizardForm.Font.Name := 'SUIT';
  WizardForm.Font.Style := [fsBold];
end;

procedure DeinitializeSetup();
begin
  if PrivateFontPath <> '' then
    RemoveFontResourceExW(PrivateFontPath, $10, 0);
end;
