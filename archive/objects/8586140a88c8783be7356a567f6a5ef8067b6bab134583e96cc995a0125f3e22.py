"""UTF-8, Python 구문, PowerShell 구문을 직접 검사합니다."""
import ast
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
files = []
for folder in ['src', 'tests', 'tools']:
    files.extend((ROOT / folder).rglob('*.py'))
    files.extend((ROOT / folder).rglob('*.ps1'))
files.extend(ROOT.glob('*.ps1'))
files.append(ROOT / 'README.md')
for path in files:
    text = path.read_bytes().decode('utf-8-sig', errors='strict')
    if '\ufffd' in text:
        raise ValueError(f'대체 문자: {path}')
    if path.suffix == '.py':
        ast.parse(text, filename=str(path))
exe = Path(os.environ.get('SystemRoot', r'C:\Windows')) / 'System32/WindowsPowerShell/v1.0/powershell.exe'
script = "$ErrorActionPreference='Stop'; $bad=$false; Get-ChildItem -LiteralPath $args[0] -Filter '*.ps1' -Recurse | ForEach-Object { $tokens=$null; $errors=$null; [System.Management.Automation.Language.Parser]::ParseFile($_.FullName,[ref]$tokens,[ref]$errors) | Out-Null; if($errors.Count){$errors | Out-String | Write-Output; $bad=$true} }; if($bad){exit 1}"
# 경로는 환경 변수로 전달하여 명령 문자열 인용에 섞지 않습니다.
env = dict(os.environ, NOTIFIER_CHECK_ROOT=str(ROOT))
script = script.replace('$args[0]', '$env:NOTIFIER_CHECK_ROOT')
result = subprocess.run([str(exe), '-NoProfile', '-NonInteractive', '-Command', script], env=env,
                        capture_output=True, timeout=8, shell=False,
                        creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
if result.returncode:
    raise RuntimeError(result.stdout.decode('utf-8', errors='replace') + result.stderr.decode('utf-8', errors='replace'))
print(f'엄격 UTF-8 및 구문 검사 성공: {len(files)}개 파일. 타입/전용 린터 설정은 없습니다.')
