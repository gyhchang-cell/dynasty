"""Inspect fixed local tower and ground templates; never count components."""
import importlib.util
from pathlib import Path
OUT=Path(__file__).resolve().parent
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=OUT;return m

if __name__=='__main__':
    m=load('renderer017',OUT.parent/'research-20261101-dungeons-017/inspect_batch.py')
    m.SELECTION=[('lost_aether_content','*lost_aether_content*jar','https://moddinglegacy.com/',
        ['platinum_dungeon/tower','platinum_dungeon/ground'])]
    m.main()
    d=load('details002',OUT.parent/'research-20261101-dungeons-002/inspect_details.py')
    d.SPECS={'F01':(3,17,14,14),'F02':(0,12,23,23)};d.main()
    load('audit017',OUT.parent/'research-20261101-dungeons-017/audit_sources.py').main()
    load('dedup002',OUT.parent/'research-20261101-dungeons-002/check_dedup.py').main()
