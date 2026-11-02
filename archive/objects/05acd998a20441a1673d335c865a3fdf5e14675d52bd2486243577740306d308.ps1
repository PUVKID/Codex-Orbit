param([string]$PythonPath = 'USER_HOME\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\pythonw.exe')
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $PythonPath -PathType Leaf)) { throw 'Python 실행 파일이 없습니다.' }
$source = Join-Path $PSScriptRoot 'src\notifier.py'
Start-Process -FilePath $PythonPath -ArgumentList ('-B -X utf8 "' + $source + '" watch') -WorkingDirectory $PSScriptRoot -WindowStyle Hidden
Write-Output '숨김 시작을 요청했습니다. work\heartbeat.json에서 실제 상태를 확인하세요.'
