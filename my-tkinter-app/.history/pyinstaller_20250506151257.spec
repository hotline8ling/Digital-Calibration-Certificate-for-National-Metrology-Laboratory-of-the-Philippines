# -*- mode: python -*-
block_cipher = None

a = Analysis(['index.py'],
             pathex=['/my-tkinter-app/my-tkinter-app'],
             binaries=[],
             datas=[('static_info.json', '.'), ('itdi-logo.png', '.'), ('nml-logo1.png', '.')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped, cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='my_tkinter_app',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
                a.binaries,
                a.zipfiles,
                a.datas,
                strip=False,
                upx=True,
                upx_exclude=[],
                name='my_tkinter_app')