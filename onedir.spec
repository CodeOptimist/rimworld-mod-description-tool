# -*- mode: python -*-
a = Analysis(
    ['main.py'],
    datas=[
        ('example_*.yaml', '.'),
    ],
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, exclude_binaries=True, name='generate', upx=True)
dir = COLLECT(exe, a.binaries, a.datas, name='rimworld-mod-description-tool')
