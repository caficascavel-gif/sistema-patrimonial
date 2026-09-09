# -*- mode: python ; coding: utf-8 -*-
# Gera o .exe da API. Rodar em uma máquina Windows (o PyInstaller empacota
# para o sistema operacional onde ele é executado).
#
# Uso (dentro da pasta backend/, com o venv ativado):
#   pyinstaller build/api.spec

from pathlib import Path

BACKEND_DIR = Path(SPECPATH).parent

block_cipher = None

a = Analysis(
    [str(BACKEND_DIR / 'run_server.py')],
    pathex=[str(BACKEND_DIR)],
    binaries=[],
    datas=[],
    # O FastAPI/uvicorn/SQLAlchemy fazem vários imports "dinâmicos" que o
    # PyInstaller sozinho não descobre analisando o código só de olho —
    # por isso listamos manualmente aqui. Se faltar algum, o sintoma é um
    # ModuleNotFoundError ao abrir o .exe; a mensagem de erro sempre diz
    # qual módulo falta, daí é só adicionar nesta lista.
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'pymysql',
        'bcrypt',
        'jose.backends.cryptography_backend',
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
    name='SistemaPatrimonialAPI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,   # janela de console visível de propósito — se algo der
                    # errado (ex: não conseguiu conectar no MySQL), a
                    # mensagem de erro aparece na tela em vez de sumir.
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
