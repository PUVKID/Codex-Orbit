$ErrorActionPreference = 'Stop'
$work = Join-Path $PSScriptRoot 'work'
[System.IO.Directory]::CreateDirectory($work) | Out-Null
[System.IO.File]::WriteAllText((Join-Path $work 'stop.request'), (Get-Date -Format o), (New-Object System.Text.UTF8Encoding($false)))
Write-Output '중지 요청 저장 완료. 감시 중인 명령이 반환한 다음 종료합니다. heartbeat.json의 중지됨을 확인하세요.'
