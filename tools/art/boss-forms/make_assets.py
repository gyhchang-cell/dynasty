"""Rebuild all eight resources and editable sources; never launches Java or Gradle."""
import runpy
from pathlib import Path
folder=Path(__file__).parent
for script in ['build.py','ground.py','projectile.py','export_bbmodel.py','validate.py']:
 runpy.run_path(str(folder/script),run_name='__main__')
