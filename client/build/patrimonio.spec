# -*- mode: python ; coding: utf-8 -*-
# Gera o executável do cliente. Rodar em uma máquina Windows (o PyInstaller
# empacota para o sistema operacional onde ele é executado — não dá para
# gerar um .exe Windows a partir de Linux/Mac).
#
# Uso (dentro da pasta client/, com o venv ativado):
#   pyinstaller build/patrimonio.spec

import sys
from pathlib import Path

# Caminho da pasta client/ (onde fica o pacote app/)
CLIENT_DIR = Path(SPECPATH).parent

block_cipher = None

a = Analysis(
    [str(CLIENT_DIR / 'app' / 'main.py')],
    pathex=[str(CLIENT_DIR)],
    binaries=[],
    datas=[],
    # PySide6 costuma precisar desses hidden imports em builds congelados
    hiddenimports=[
        'PySide6.QtPrintSupport',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SistemaPatrimonial',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # sem janela de terminal atrás da aplicação
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,               # troque por 'icone.ico' se quiser um ícone próprio
)
