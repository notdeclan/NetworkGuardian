# -*- mode: python ; coding: utf-8 -*-
import sys

block_cipher = None

a = Analysis(['entry_point.py'],
             pathex=['./'],
             binaries=[],
             datas=[('networkguardian/gui/static', 'static'), ('networkguardian/gui/templates/', 'templates')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

if sys.platform == 'darwin':
    print("Mac OS X")
    exe = EXE(pyz,
            a.scripts,
            a.binaries,
            a.zipfiles,
            a.datas,
            name='Network Guardian',
            debug=False,
            strip=False,
            upx=True,
            runtime_tmpdir=None,
            console=True,
            icon='assets/icon.icns')

# Package the executable file into .app if on OS X
if sys.platform == 'darwin':
    app = BUNDLE(exe,
        name='Network Guardian',
        info_plist = {
        'NSHighResolutionCapable': 'True'
        },
        icon='assets/icon.icns'
    )

if sys.platform == 'win32' or sys.platform == 'win64' or sys.platform == 'linux':
    print("Windows / Linux")
    exe = EXE(pyz,
              a.scripts,
              a.binaries,
              a.zipfiles,
              a.datas,
              [],
              name='NetworkGuardian',
              debug=False,
              bootloader_ignore_signals=False,
              strip=False,
              upx=True,
              upx_exclude=[],
              runtime_tmpdir=None,
              console=True, icon='resources/icon.ico')