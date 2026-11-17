"""Publish approved original PNGs with the current runtime loader (never downsample)."""
from pathlib import Path
import runpy

def publish(ids=None):
    # Republish the complete canonical set so model/atlas bindings stay consistent.
    runpy.run_path(str(Path(__file__).with_name('publish_originals.py')))['publish']()

if __name__=='__main__':publish()
