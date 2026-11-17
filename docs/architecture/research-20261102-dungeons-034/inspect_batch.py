"""Check four size hits from one custom underground structure, without Java."""
import importlib.util
from pathlib import Path

OUT = Path(__file__).resolve().parent

def load(name, path):
    spec = importlib.util.spec_from_file_location(name,path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.OUT = OUT
    return m

if __name__ == '__main__':
    renderer = load('renderer',OUT.parent/'research-20261101-dungeons-017/inspect_batch.py')
    renderer.SELECTION = [('eeeabsmobs','*eeeabsmobs*jar',
        'https://www.curseforge.com/minecraft/mc-mods/eeeabs-mobs',
        ['guling_1','guling_2','guling_3','guling_4'])]
    renderer.main()
    details = load('details',OUT.parent/'research-20261101-dungeons-002/inspect_details.py')
    details.SPECS = {f'F{i:02d}':(10,25,13,13) for i in range(1,5)}
    details.main()
    load('audit',OUT.parent/'research-20261101-dungeons-017/audit_sources.py').main()
    load('dedup',OUT.parent/'research-20261101-dungeons-002/check_dedup.py').main()
