"""Read two authored mausoleum alternatives as one possible funerary family."""
import importlib.util
from pathlib import Path
OUT=Path(__file__).resolve().parent
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=OUT;return m
if __name__=='__main__':
    m=load('renderer017',OUT.parent/'research-20261101-dungeons-017/inspect_batch.py')
    m.SELECTION=[('goetyawaken','*goetyawaken*jar','https://github.com/k1sak1/goetyawaken/issues',['the_mausoleum1','the_mausoleum2'])]
    m.main()
    d=load('details002',OUT.parent/'research-20261101-dungeons-002/inspect_details.py')
    d.SPECS={'F01':(4,20,18,18),'F02':(4,20,18,18)};d.main()
    load('audit017',OUT.parent/'research-20261101-dungeons-017/audit_sources.py').main()
    load('dedup002',OUT.parent/'research-20261101-dungeons-002/check_dedup.py').main()
