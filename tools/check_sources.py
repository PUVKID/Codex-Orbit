"""배포 소스의 엄격 UTF-8과 Python 문법을 검사합니다."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
count = 0
for directory in ('src', 'tests', 'assets', 'tools', 'docs', 'installer'):
    base = ROOT / directory
    if not base.exists():
        continue
    for path in base.rglob('*'):
        if not path.is_file() or path.suffix.lower() not in ('.py', '.md', '.txt', '.iss'):
            continue
        text = path.read_bytes().decode('utf-8-sig')
        if '\ufffd' in text:
            raise ValueError(f'대체 문자 발견: {path}')
        if path.suffix == '.py':
            ast.parse(text, filename=str(path))
        count += 1
print(f'엄격 UTF-8 및 Python 구문: {count}개 파일 통과. 의미상 완전 무오류 보증은 아닙니다.')
