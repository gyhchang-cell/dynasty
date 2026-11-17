"""Keep workshop tools and retired HUD integrations out of release packs."""
from pathlib import Path

WORKSHOP_PREFIXES = ('worldedit-', 'prefab-', 'dynasty-playtest-helper', 'dynasty-audit-', 'dynasty-quest-qa')
# Old branch checkouts can restore this retired jar. Keep the local file, but
# never ship it alongside Dynasty's replacement HUD or the locked mod inventory.
RETIRED_PREFIXES = ('overflowingbars-',)

def release_mod(filename):
    return not Path(filename).name.lower().startswith(WORKSHOP_PREFIXES + RETIRED_PREFIXES)

def release_config(relative):
    name = str(relative).replace('\\', '/').lower()
    return not (name.startswith(('worldedit/', 'prefab/')) or name.startswith(('worldedit.', 'prefab-', 'prefab.')))
