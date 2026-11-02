param(
    [ValidateSet('Send','Install','Uninstall')][string]$Action = 'Send',
    [string]$XmlPath,
    [string]$Tag = 'codexmodel',
    [string]$PythonPath,
    [string]$RootPath
)
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$appId = 'Yunseok.Codex.ModelChangeNotifier'
$registryPath = 'HKCU:\Software\Classes\AppUserModelId\' + $appId
$shortcutPath = Join-Path ([Environment]::GetFolderPath('Programs')) 'Codex 모델 변경 알림.lnk'
if ($Action -eq 'Uninstall') {
    Remove-Item -LiteralPath $shortcutPath -Force -ErrorAction SilentlyContinue
    if (Test-Path -LiteralPath $registryPath) { Remove-Item -LiteralPath $registryPath -Force }
    Write-Output '전용 시작 메뉴 바로가기와 현재 사용자 전용 앱 ID 표시 정보를 제거했습니다.'
    exit 0
}
if ($Action -eq 'Install') {
    if (-not (Test-Path -LiteralPath $PythonPath -PathType Leaf)) { throw 'Python 실행 파일이 없습니다.' }
    if (-not (Test-Path -LiteralPath (Join-Path $RootPath 'src\notifier.py') -PathType Leaf)) { throw '감시기 소스가 없습니다.' }
    # 전용 바로가기에 Microsoft 문서의 PKEY_AppUserModel_ID를 지정합니다.
    Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
using System.Text;
using System.Runtime.InteropServices.ComTypes;
public static class NotifierShortcut {
 [ComImport, Guid("00021401-0000-0000-C000-000000000046")] class ShellLink {}
 [ComImport, InterfaceType(ComInterfaceType.InterfaceIsIUnknown), Guid("000214F9-0000-0000-C000-000000000046")]
 interface IShellLinkW {
  void GetPath([Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder p,int n,IntPtr d,uint f);
  void GetIDList(out IntPtr p); void SetIDList(IntPtr p);
  void GetDescription([Out,MarshalAs(UnmanagedType.LPWStr)] StringBuilder p,int n);
  void SetDescription([MarshalAs(UnmanagedType.LPWStr)] string p);
  void GetWorkingDirectory([Out,MarshalAs(UnmanagedType.LPWStr)] StringBuilder p,int n);
  void SetWorkingDirectory([MarshalAs(UnmanagedType.LPWStr)] string p);
  void GetArguments([Out,MarshalAs(UnmanagedType.LPWStr)] StringBuilder p,int n);
  void SetArguments([MarshalAs(UnmanagedType.LPWStr)] string p);
  void GetHotkey(out short p); void SetHotkey(short p); void GetShowCmd(out int p); void SetShowCmd(int p);
  void GetIconLocation([Out,MarshalAs(UnmanagedType.LPWStr)] StringBuilder p,int n,out int i);
  void SetIconLocation([MarshalAs(UnmanagedType.LPWStr)] string p,int i);
  void SetRelativePath([MarshalAs(UnmanagedType.LPWStr)] string p,uint r);
  void Resolve(IntPtr w,uint f); void SetPath([MarshalAs(UnmanagedType.LPWStr)] string p);
 }
 [StructLayout(LayoutKind.Sequential, Pack=4)] struct PROPERTYKEY { public Guid fmtid; public uint pid; }
 [StructLayout(LayoutKind.Explicit, Size=24)] struct PROPVARIANT {
  [FieldOffset(0)] public ushort vt; [FieldOffset(8)] public IntPtr pointer;
 }
 [ComImport, Guid("886D8EEB-8CF2-4446-8D02-CDBA1DBDCF99"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
 interface IPropertyStore {
  void GetCount(out uint c); void GetAt(uint i,out PROPERTYKEY k);
  void GetValue(ref PROPERTYKEY k,out PROPVARIANT v);
  void SetValue(ref PROPERTYKEY k,ref PROPVARIANT v); void Commit();
 }
 public static void Create(string path,string exe,string arguments,string cwd,string appId) {
  object raw = new ShellLink();
  try {
   var link=(IShellLinkW)raw; link.SetPath(exe); link.SetArguments(arguments);
   link.SetWorkingDirectory(cwd); link.SetDescription("Codex 모델 변경 알림"); link.SetShowCmd(7);
   var store=(IPropertyStore)raw;
   var key=new PROPERTYKEY {fmtid=new Guid("9F4C2855-9F79-4B39-A8D0-E1D42DE1D5F3"),pid=5};
   var value=new PROPVARIANT {vt=31,pointer=Marshal.StringToCoTaskMemUni(appId)};
   try {store.SetValue(ref key,ref value); store.Commit();}
   finally {Marshal.FreeCoTaskMem(value.pointer);}
   ((IPersistFile)raw).Save(path,true);
  } finally {Marshal.FinalReleaseComObject(raw);}
 }
}
'@
    $source = Join-Path $RootPath 'src\notifier.py'
    [NotifierShortcut]::Create($shortcutPath, $PythonPath, ('-B -X utf8 "' + $source + '" watch'), $RootPath, $appId)
    # 공식 Toolkit의 현재 사용자 AppUserModelId 등록과 같은 표시 정보만 지정합니다.
    # 클릭 활성화 COM 서버를 구현하지 않으므로 다른 앱 CLSID나 가짜 활성기를 등록하지 않습니다.
    New-Item -Path $registryPath -Force | Out-Null
    New-ItemProperty -LiteralPath $registryPath -Name 'DisplayName' -Value 'Codex 모델 변경 알림' -PropertyType ExpandString -Force | Out-Null
    New-ItemProperty -LiteralPath $registryPath -Name 'IconBackgroundColor' -Value 'FF245A81' -PropertyType String -Force | Out-Null
    Write-Output ('전용 AppUserModelID 등록: ' + $shortcutPath)
    exit 0
}
if (-not (Test-Path -LiteralPath $shortcutPath -PathType Leaf)) { throw '먼저 설치.ps1로 전용 알림 ID를 등록해야 합니다.' }
[xml]$xml = [System.IO.File]::ReadAllText($XmlPath, [System.Text.Encoding]::UTF8)
$texts = @($xml.SelectNodes('/toast/visual/binding/text') | ForEach-Object { $_.InnerText })
if ($texts.Count -ne 3) { throw '알림 제목·변경 전후·이유의 세 항목이 필요합니다.' }
$title = [string]$texts[0]
$body = $texts[1] + "`n" + $texts[2]
if ($title.Length -gt 63 -or $body.Length -gt 255) { throw 'Windows 알림의 제목 63·본문 255 UTF-16 길이 제한을 초과했습니다.' }
# 현대 토스트의 등록 실패를 성공으로 숨기지 않고 명시적인 Windows Forms 전송을 사용합니다.
# 표시 이벤트를 기다리며 집중 모드·전역 알림 정책을 변경하지 않습니다.
Add-Type -ReferencedAssemblies System.Windows.Forms,System.Drawing -TypeDefinition @'
using System;
using System.Diagnostics;
using System.Drawing;
using System.Runtime.InteropServices;
using System.Threading;
using System.Windows.Forms;
public static class ModelChangeBalloon {
 [DllImport("shell32.dll", CharSet=CharSet.Unicode)]
 private static extern int SetCurrentProcessExplicitAppUserModelID(string appId);
 public static string Show(string title, string body, string appId) {
  Marshal.ThrowExceptionForHR(SetCurrentProcessExplicitAppUserModelID(appId));
  bool shown = false;
  bool finished = false;
  using (var icon = new NotifyIcon()) {
   icon.Icon = SystemIcons.Information;
   icon.Text = "Codex 모델 변경 알림";
   icon.BalloonTipShown += delegate { shown = true; };
   icon.BalloonTipClosed += delegate { finished = true; };
   icon.BalloonTipClicked += delegate { finished = true; };
   icon.Visible = true;
   icon.ShowBalloonTip(8000, title, body, ToolTipIcon.Info);
   var clock = Stopwatch.StartNew();
   while (clock.ElapsedMilliseconds < 8000 && !finished) {
    Application.DoEvents();
    Thread.Sleep(40);
   }
  }
  if (!shown) {
   throw new InvalidOperationException("8초 안에 Windows BalloonTipShown 이벤트가 오지 않았습니다. 알림 차단 또는 표시 지연을 확인해야 합니다.");
  }
  return "Windows NotifyIcon.ShowBalloonTip 반환 및 BalloonTipShown 이벤트 확인; 화면 수신과 알림 센터 저장은 미확인";
 }
}
'@
Write-Output ([ModelChangeBalloon]::Show($title, $body, $appId))
