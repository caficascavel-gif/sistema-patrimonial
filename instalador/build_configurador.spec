# -*- mode: python ; coding: utf-8 -*-
# Gera o ConfigurarTudo.exe — roda em Windows, com: pyinstaller build_configurador.spec
from pathlib import Path

PASTA = Path(SPECPATH)
SCHEMA = PASTA.parent / "database" / "schema.sql"

block_cipher = None

a = Analysis(
    [str(PASTA / 'configurar_tudo.py')],
    pathex=[str(PASTA)],
    binaries=[],
    datas=[(str(SCHEMA), '.')],  # embute o schema.sql dentro do próprio .exe
    hiddenimports=['pymysql', 'bcrypt'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [],
    name='ConfigurarTudo',
    debug=False, bootloader_ignore_signals=False, strip=False, upx=True,
    upx_exclude=[], runtime_tmpdir=None,
    console=True,  # precisa ser visível: é onde a pessoa responde as perguntas
    disable_windowed_traceback=False, argv_emulation=False,
    target_arch=None, codesign_identity=None, entitlements_file=None, icon=None,
)
