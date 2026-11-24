# 빌드 대상 두 패키지의 자료·바이너리·하위 모듈·메타를 명시적으로 수집합니다.
import os
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules, copy_metadata
root=Path(SPECPATH).parent
runtime=Path(os.environ['ORBIT_RUNTIME_ASSETS'])
datas=[(str(runtime),'assets')];binaries=[];hiddenimports=[]
for name in ('moderngl','glcontext'):
    datas+=collect_data_files(name,include_py_files=True)
    binaries+=collect_dynamic_libs(name)
    hiddenimports+=collect_submodules(name)
    # 모든 설치 패키지의 파일 존재 여부를 조사하지 않고 실제 대상 메타를 보존합니다.
    datas+=copy_metadata(name)
a=Analysis([str(root/'src/orbit_entry.py')],pathex=[str(root/'src')],binaries=binaries,datas=datas,hiddenimports=hiddenimports,hookspath=[],hooksconfig={},runtime_hooks=[],excludes=[],noarchive=False,optimize=0)
pyz=PYZ(a.pure)
exe=EXE(pyz,a.scripts,a.binaries,a.datas,[],name='CodexOrbit',debug=False,bootloader_ignore_signals=False,strip=False,upx=True,upx_exclude=[],runtime_tmpdir=None,console=False,disable_windowed_traceback=False,argv_emulation=False,target_arch=None,codesign_identity=None,entitlements_file=None,icon=[str(root/'assets/Orbit.ico')])
