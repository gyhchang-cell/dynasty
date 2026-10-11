"""Default art export preserves approved bodies/rigs/timelines; no Java launched.

Geometry redesign is a separate explicitly requested operation (build.py +
ground.py). Texture work must never silently rebuild the approved geometry.
"""
from materials import export,validate
export()
validate()
