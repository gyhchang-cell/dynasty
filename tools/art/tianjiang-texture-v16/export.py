"""Texture-only export onto the approved per-face UVs. Never writes JSON assets."""
import sys,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(R/'tools/art/tianjiang-steve-v15'))
from create import build,paint,PAL,TARGETS,hashes,D as PREV
from PIL import Image
D=R/'docs/art/tianjiang-texture-v16';ID='nine_heaven_general'
def export():
 # V17 owns the accepted helmet; legacy commands must not restore the flat face.
 import runpy
 runpy.run_path(str(R/'tools/art/tianjiang-helmet-v17/export.py'),run_name='__main__')
if __name__=='__main__':export()
