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
        ('template.xml','.'),
        ('imgToxml.py','.'),
        ('new-xml.py','.'),
        ('pdfToxml.py','.'),
        ('settings.py','.')
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
        'pdfplumber',        import sys, os, traceback
        from tkinter import messagebox
        
        # after you define `script_dir` but before creating your CTk():
        def handle_exception(exc, val, tb):
            err = ''.join(traceback.format_exception(exc, val, tb))
            # show the error to the user
            messagebox.showerror("Unexpected Error", err)
            # also write to a log
            with open(os.path.join(script_dir, "error.log"), "w") as f:
                f.write(err)
        
        # hook all uncaught exceptions
        sys.excepthook = handle_exception
        
        # for Tkinter callbacks:
        import tkinter
        tkinter.Misc.report_callback_exception = handle_exception
        
        # … now build your `app = CTk()` and everything else …
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
    console=True,          # ← show console for errors
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