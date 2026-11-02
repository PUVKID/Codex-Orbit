param([string]$PythonPath = 'USER_HOME\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\pythonw.exe')
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
# 현재 사용자 전용 시작 메뉴 항목과 로그인 자동 시작만 등록합니다.
& (Join-Path $root 'src\toast.ps1') -Action Install -PythonPath $PythonPath -RootPath $root
$startup = Join-Path ([Environment]::GetFolderPath('Startup')) 'Codex 모델 변경 알림.lnk'
$shell = New-Object -ComObject WScript.Shell
$link = $shell.CreateShortcut($startup)
$link.TargetPath = $PythonPath
$link.Arguments = '-B -X utf8 "' + (Join-Path $root 'src\notifier.py') + '" watch'
$link.WorkingDirectory = $root
$link.WindowStyle = 7
$link.Description = '현재 사용자 Codex 모델 변경 감시'
$link.Save()
Write-Output '설치 완료. 아직 감시기를 시작하지 않았습니다. 시작.ps1을 실행하세요.'
