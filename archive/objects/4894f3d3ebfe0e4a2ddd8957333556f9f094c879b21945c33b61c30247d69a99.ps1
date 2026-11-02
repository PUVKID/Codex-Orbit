$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot '중지.ps1')
$startup = Join-Path ([Environment]::GetFolderPath('Startup')) 'Codex 모델 변경 알림.lnk'
Remove-Item -LiteralPath $startup -Force -ErrorAction SilentlyContinue
& (Join-Path $PSScriptRoot 'src\toast.ps1') -Action Uninstall
Write-Output '자동 시작 및 전용 시작 메뉴 항목 제거 완료. 소스와 로컬 이력은 보존했습니다.'
