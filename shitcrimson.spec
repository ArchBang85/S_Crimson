# -*- mode: python -*-
a = Analysis(['shitcrimson.py'],
             pathex=['C:\\Users\\Autio\\PycharmProjects\\ShitCrimson'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='shitcrimson.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True )
