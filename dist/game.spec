# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['game.py'],
    pathex=[],
    binaries=[],
    datas=[('src/assets/fonts/*', 'src/assets/fonts'), ('src/assets/images/*.png', 'src/assets/images'), ('src/assets/sounds/*', 'src/assets/sounds')],
    hiddenimports=['dnspython'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Space Invaders',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='src/assets/images/icon.ico',
)
