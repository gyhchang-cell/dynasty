"""Building tools are local workshop dependencies, not release-pack content."""
from pathlib import Path

WORKSHOP_PREFIXES = ('worldedit-', 'prefab-')

def release_mod(filename):
    return not Path(filename).name.lower().startswith(WORKSHOP_PREFIXES)

def release_config(relative):
    name = str(relative).replace('\\', '/').lower()
    return not (name.startswith(('worldedit/', 'prefab/')) or name.startswith(('worldedit.', 'prefab-', 'prefab.')))
