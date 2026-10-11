"""Compatibility entrypoint for the original Cuboid/16px NPC workflow.

The former generic rig/noise generator has been replaced. Existing catalog
scripts now regenerate the current original NPC artwork.
"""
import runpy
from pathlib import Path

if __name__ == '__main__':
    runpy.run_path(str(Path(__file__).resolve().parents[1] / 'art/cod3/rebuild_npcs.py'), run_name='__main__')
