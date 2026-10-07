# crear_ejecutable.spec
# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_all

# ============================================
# RECOLECCIÓN DE DEPENDENCIAS COMPLEJAS
# ============================================

datas = []
binaries = []
hiddenimports = []

# DeepFace
tmp_datas, tmp_binaries, tmp_hidden = collect_all('deepface')
datas += tmp_datas
binaries += tmp_binaries
hiddenimports += tmp_hidden

# TensorFlow
tmp_datas, tmp_binaries, tmp_hidden = collect_all('tensorflow')
datas += tmp_datas
binaries += tmp_binaries
hiddenimports += tmp_hidden

# OpenCV
tmp_datas, tmp_binaries, tmp_hidden = collect_all('cv2')
datas += tmp_datas
binaries += tmp_binaries
hiddenimports += tmp_hidden

# retinaface (parte de deepface)
try:
    tmp_datas, tmp_binaries, tmp_hidden = collect_all('retinaface')
    datas += tmp_datas
    binaries += tmp_binaries
    hiddenimports += tmp_hidden
except Exception:
    pass

# mtcnn (detector de rostros)
try:
    tmp_datas, tmp_binaries, tmp_hidden = collect_all('mtcnn')
    datas += tmp_datas
    binaries += tmp_binaries
    hiddenimports += tmp_hidden
except Exception:
    pass

# ============================================
# ARCHIVOS Y CARPETAS A INCLUIR
# ============================================

# Modelos de IA
datas.append(('.deepface', '.deepface'))

# Logo de la escuela
datas.append(('recursos', 'recursos'))

# ============================================
# MÓDULOS OCULTOS
# ============================================

hiddenimports += [
    'PIL._tkinter_finder',
    'tkinter',
    'tkinter.ttk',
    'tkinter.scrolledtext',
    'tkinter.messagebox',
]

# ============================================
# CONFIGURACIÓN DEL EJECUTABLE
# ============================================

block_cipher = None

a = Analysis(
    ['sistema_principal/gui_camara.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'IPython',
        'jupyter',
        'notebook',
    ],
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
    name='SistemaReconocimientoFacial',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)