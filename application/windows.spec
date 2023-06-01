# app.spec for Windows

# Specify the main script file
entry_point = 'app.py'

# Configure the PyInstaller options
block_cipher = None

a = Analysis([entry_point],
             pathex=[],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=None,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
          cipher=None)

exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='LIMS',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='dist')

# Define any additional configurations or options as needed

# Return the Analysis object
