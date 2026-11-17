#!/usr/bin/env python3
"""Inspect previously unviewed size hits; no automatic purpose or credit."""
import importlib.util
from pathlib import Path

OUT = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.OUT = OUT
    return m


if __name__ == '__main__':
    m = load('renderer', OUT.parent / 'research-20261101-dungeons-017/inspect_batch.py')
    m.SELECTION = [
      ('ati_structures', '*ATi*jar', 'https://www.curseforge.com/minecraft/mc-mods/ati-structures', ['gnome_hut', 'gnome_hut1']),
      ('trek', '*远足*jar', 'https://modrinth.com/datapack/trek', ['overworld/medium/jungle_treehouse']),
      ('goetyawaken', '*goetyawaken*jar', None, ['rabbit_shed'])]
    m.main()
    details = load('details', OUT.parent / 'research-20261101-dungeons-002/inspect_details.py')
    details.SPECS = {'F01': (3, 14, 12, 10), 'F02': (3, 14, 12, 11),
                     'F03': (15, 25, 13, 9), 'F04': (3, 10, 16, 16)}
    details.main()
    load('audit', OUT.parent / 'research-20261101-dungeons-017/audit_sources.py').main()
    load('dedup', OUT.parent / 'research-20261101-dungeons-002/check_dedup.py').main()
