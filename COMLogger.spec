# -*- mode: python ; coding: utf-8 -*-

import sys
import os
tree = []
if os.name == "nt":
    from kivy_deps import sdl2, glew
    tree = [Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)]
path = os.path.abspath(".")


a = Analysis(
    ['main.py'],
    pathex=[path],
    binaries=[],

    datas=[('comloggerapp.kv', '.')],
    hiddenimports=["libs.utils"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pygement","requests","urllib3","kivy.garden"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='COMLogger',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    *tree,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='COMLogger',
)
