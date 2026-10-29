"""외부 통신 없는 로컬 자료 읽기와 명시적 지침 적용."""
import hashlib
import json
import os
from pathlib import Path
import stat
import uuid

MAX_TEXT_BYTES = 2 * 1024 * 1024
BEGIN = b'<!-- CODEX-ORBIT:BEGIN -->'
END = b'<!-- CODEX-ORBIT:END -->'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read_jsonl_tail(path, max_bytes=MAX_TEXT_BYTES, max_records=500):
    """물리적 LF만 나누며 잘린 앞/뒤 조각은 레코드로 해석하지 않습니다."""
    path = Path(path)
    if not path.exists():
        return [], []
    with path.open('rb') as handle:
        size = handle.seek(0, os.SEEK_END)
        start = max(0, size - max_bytes)
        handle.seek(start)
        raw = handle.read(max_bytes)
    problems = []
    if start:
        problems.append(f'앞부분 생략: 전체 {size}바이트, 최대 {max_bytes}바이트 읽음')
        raw = raw.partition(b'\n')[2]
    pieces = raw.split(b'\n')
    pieces.pop()  # 마지막 LF 뒤 조각 또는 미완성 레코드는 기다립니다.
    rows = []
    for number, piece in enumerate(pieces):
        if not piece:
            continue
        try:
            row = json.loads(piece.decode('utf-8'))
            if not isinstance(row, dict):
                raise ValueError('JSON 객체가 아닙니다.')
            rows.append(row)
        except (UnicodeError, ValueError) as error:
            problems.append(f'읽은 범위의 레코드 {number + 1}: {error}')
    return rows[-max_records:], problems[:50]


def session_titles(path):
    rows, _ = read_jsonl_tail(path, max_records=10000)
    return {r['id']: r['thread_name'][:500] for r in rows
            if isinstance(r.get('id'), str) and isinstance(r.get('thread_name'), str)
            and r['thread_name'].strip()}


def clamp_position(position, screens, size=140):
    for x, y, width, height in screens:
        if x <= position[0] and y <= position[1] and position[0] + size <= x + width and position[1] + size <= y + height:
            return tuple(position)
    if not screens:
        return (24, 24)
    x, y, _, _ = screens[0]
    return (x + 24, y + 24)


def safe_path(path):
    """적용 파일과 모든 기존 조상 경로의 링크/재분석 지점을 거부합니다."""
    path = Path(os.path.abspath(path))
    for part in [path, *path.parents]:
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise ValueError('링크 또는 재분석 경로에는 적용할 수 없습니다: ' + str(part))
    return path


def read_text_strict(path):
    path = Path(path)
    if path.stat().st_size > MAX_TEXT_BYTES:
        raise ValueError('문서가 2 MiB 상한을 초과했습니다.')
    return path.read_bytes().decode('utf-8-sig')


class InstructionStore:
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)

    def _target(self, target):
        target = safe_path(target)
        if target.name.lower() != 'agents.md':
            raise ValueError('적용 대상은 AGENTS.md 파일이어야 합니다.')
        if not target.parent.is_dir():
            raise ValueError('대상 폴더가 존재하지 않습니다.')
        if target.exists() and (not target.is_file() or target.stat().st_size > MAX_TEXT_BYTES):
            raise ValueError('대상은 2 MiB 이하의 일반 파일이어야 합니다.')
        return target

    def preview(self, target, content):
        target = self._target(target)
        added = content.encode('utf-8')
        if not content.strip() or len(added) > MAX_TEXT_BYTES:
            raise ValueError('빈 지침 또는 2 MiB 초과 지침은 적용할 수 없습니다.')
        if BEGIN in added or END in added:
            raise ValueError('지침 내용에 앱 관리구역 표식을 넣을 수 없습니다.')
        existed = target.exists()
        original = target.read_bytes() if existed else b''
        original.decode('utf-8-sig')
        block = BEGIN + b'\n' + added.rstrip(b'\r\n') + b'\n' + END
        if BEGIN in original or END in original:
            if original.count(BEGIN) != 1 or original.count(END) != 1 or original.index(BEGIN) >= original.index(END):
                raise ValueError('기존 관리구역 표식이 손상되었거나 중복되었습니다.')
            start = original.index(BEGIN)
            finish = original.index(END) + len(END)
            result = original[:start] + block + original[finish:]
        else:
            result = original + (b'\n' if original and not original.endswith(b'\n') else b'') + block + b'\n'
        if len(result) > MAX_TEXT_BYTES:
            raise ValueError('적용 결과가 2 MiB 상한을 초과합니다.')
        return {'target': str(target), 'before_hash': digest(original), 'existed': existed,
                'original': original, 'applied_bytes': result, 'after_hash': digest(result)}

    def _unchanged(self, target, existed, expected):
        target = self._target(target)
        if target.exists() != existed or digest(target.read_bytes() if existed else b'') != expected:
            raise ValueError('대상 파일이 미리보기/적용 이후 변경되었습니다. 새 미리보기가 필요합니다.')
        return target

    def _replace(self, target, raw, existed, expected):
        temp = target.parent / ('.codex-orbit-' + uuid.uuid4().hex + '.tmp')
        try:
            with temp.open('xb') as handle:
                handle.write(raw)
                handle.flush()
                os.fsync(handle.fileno())
            self._unchanged(target, existed, expected)
            if existed:
                os.chmod(temp, stat.S_IMODE(target.stat().st_mode))
            os.replace(temp, target)
        finally:
            temp.unlink(missing_ok=True)

    def apply(self, plan):
        target = self._unchanged(plan['target'], plan['existed'], plan['before_hash'])
        if digest(plan['original']) != plan['before_hash'] or digest(plan['applied_bytes']) != plan['after_hash']:
            raise ValueError('미리보기 데이터가 변경되었습니다.')
        backup_dir = safe_path(self.data_dir / 'backups')
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup = backup_dir / (uuid.uuid4().hex + '.bin')
        with backup.open('xb') as handle:
            handle.write(plan['original'])
            handle.flush()
            os.fsync(handle.fileno())
        receipt = {key: value for key, value in plan.items() if key != 'original'}
        receipt['backup'] = str(backup)
        # 쓰기 실패 시에도 원문 백업은 남기며 적용 성공이라고 기록하지 않습니다.
        self._replace(target, plan['applied_bytes'], plan['existed'], plan['before_hash'])
        manifest = {key: value for key, value in receipt.items() if key != 'applied_bytes'}
        (backup.with_suffix('.json')).write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        return receipt

    def restore(self, receipt):
        target = self._unchanged(receipt['target'], True, receipt['after_hash'])
        backup = safe_path(receipt['backup'])
        if backup.parent != safe_path(self.data_dir / 'backups') or not backup.is_file() or backup.stat().st_size > MAX_TEXT_BYTES:
            raise ValueError('유효한 앱 원문 백업이 아닙니다.')
        raw = backup.read_bytes()
        if digest(raw) != receipt['before_hash']:
            raise ValueError('백업 해시가 일치하지 않습니다.')
        if receipt['existed']:
            self._replace(target, raw, True, receipt['after_hash'])
        else:
            self._unchanged(target, True, receipt['after_hash'])
            target.unlink()

    def receipts(self):
        directory = self.data_dir / 'backups'
        if not directory.is_dir():
            return []
        result = []
        for path in sorted(directory.glob('*.json'), key=lambda p: p.stat().st_mtime, reverse=True)[:100]:
            if path.stat().st_size <= 10000:
                result.append(json.loads(path.read_text(encoding='utf-8')))
        return result
