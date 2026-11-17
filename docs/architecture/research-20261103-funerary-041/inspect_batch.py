"""Read new fixed local small ritual enclosures, never credit by filename."""
import importlib.util
from pathlib import Path
OUT=Path(__file__).resolve().parent
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=OUT;return m
if __name__=='__main__':
    m=load('renderer017',OUT.parent/'research-20261101-dungeons-017/inspect_batch.py')
    m.SELECTION=[('legendary_monsters','*legendarymonsters*jar',None,
        ['mossy_temple','frostbitten_temple','frostbitten_temple2'])]
    m.main()
    d=load('details002',OUT.parent/'research-20261101-dungeons-002/inspect_details.py')
    d.SPECS={'F01':(2,5,11,10),'F02':(3,7,10,10),'F03':(3,7,10,10)};d.main()
    load('audit017',OUT.parent/'research-20261101-dungeons-017/audit_sources.py').main()
    load('dedup002',OUT.parent/'research-20261101-dungeons-002/check_dedup.py').main()
