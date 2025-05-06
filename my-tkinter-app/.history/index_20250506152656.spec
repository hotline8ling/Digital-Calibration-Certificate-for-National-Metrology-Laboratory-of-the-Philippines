# -*- mode: python -*-
block_cipher = None

a = Analysis(
    ['index.py'],
    pathex=[r'C:\Users\ADMIN\Documents\GitHub\Digital-Calibration-Certificate-for-National-Metrology-Laboratory-of-the-Philippines\my-tkinter-app'],
    binaries=[],
    datas=[
        ('static_info.json', '.'),
        ('itdi-logo.png', '.'),
        ('nml-logo1.png', '.'),
    ],
    hiddenimports=[
        'customtkinter',
        'tkinter',
        'PIL',
        'cv2',
        'numpy',
        'pytesseract',
        'reportlab.pdfgen.canvas',
        'lxml.etree',
        'pdfplumber',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,          # <-- use zipped_data, not zipped
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='my_tkinter_app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='my_tkinter_app'
)