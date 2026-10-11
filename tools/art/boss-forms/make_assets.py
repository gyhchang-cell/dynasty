"""Default art export preserves approved bodies/rigs/timelines; no Java launched.

Geometry redesign is a separate explicitly requested operation (build.py +
ground.py). Texture work must never silently rebuild the approved geometry.
"""
import runpy
from pathlib import Path
from retexture import run
from build import IDS
run(IDS)
runpy.run_path(str(Path(__file__).with_name('export_bbmodel.py')),run_name='__main__')
from texture_validate import run as validate
validate()
