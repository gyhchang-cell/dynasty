"""Inspect one locally present citadel, preserving unresolved chain dependencies."""
import importlib.util
from pathlib import Path

OUT=Path(__file__).resolve().parent
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.OUT=OUT
    return m

if __name__=='__main__':
    renderer=load('renderer',OUT.parent/'research-20261101-dungeons-017/inspect_batch.py')
    renderer.SELECTION=[('friendsandfoes','*friendsandfoes*jar','https://github.com/Faboslav/friends-and-foes',
        ['citadel/citadel'])]
    renderer.main()
    details=load('details',OUT.parent/'research-20261101-dungeons-002/inspect_details.py')
    details.SPECS={'F01':(4,16,15,15)};details.main()
    load('audit',OUT.parent/'research-20261101-dungeons-017/audit_sources.py').main()
    load('dedup',OUT.parent/'research-20261101-dungeons-002/check_dedup.py').main()
