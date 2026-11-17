import json,hashlib,sys
from pathlib import Path
from zipfile import ZipFile
from collections import Counter
P=Path(__file__).resolve().parent;R=P.parents[2];assert not(P/'RECEIPT.json').exists()
sys.path.insert(0,str(R/'tools/architecture'));from nbt_read import read
from whole_building_candidates import AIR
from reference_components import geometry_hash,role

def ld(p):return json.loads(Path(p).read_text())
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
m=R/'docs/architecture/research-20261101-dungeons-026/all-structure-metadata.json';mm=ld(m);n='data/repurposed_structures/structures/villages/bamboo/houses/medium_house_1.nbt';e=next(v for v in mm['entries']if v['member']==n);a=bind(e['source_archive']);inv=ld(mm['fixed_archive_inventory']['path']);assert a['sha256']==next(v['sha256']for v in inv['archives']if v['path']==a['path'])
with ZipFile(a['path'])as z:raw=z.read(n);d=read(raw)
assert hashlib.sha256(raw).hexdigest()==e['nbt_sha256'];pal=d['palette'];c=Counter(pal[b['state']]['Name']for b in d['blocks']);BE=[dict(pos=b['pos'],state=pal[b['state']],nbt=b['nbt'])for b in d['blocks']if'nbt'in b];cells={tuple(b['pos']):pal[b['state']]['Name']for b in d['blocks']if pal[b['state']]['Name']not in AIR};fp=dict(nbt_sha256=e['nbt_sha256'],role_sha256=geometry_hash({p:role(v)for p,v in cells.items()},d['size']),occupancy_sha256=geometry_hash({p:1 for p in cells},d['size']));cache=R/'docs/architecture/research-20261104-smithy-153/history-fingerprints.json';matches=[v for v in ld(cache)['entries']if any(v['fingerprints'].get(k)==h for k,h in fp.items())]
hits=[]
for pat in ['research-*/manual-review.json','research-*/sources.json']:
 for p in (R/'docs/architecture').glob(pat):
  if n in p.read_text():hits.append(bind(p))
put('header-precheck.json',dict(batch=305,source=dict(archive=a,member=n,raw_sha256=e['nbt_sha256'],metadata=bind(m)),size=d['size'],materials=dict(c),BE=BE,entities=d.get('entities'),old_member_hits=hits,fingerprints=fp,fingerprint_cache=bind(cache),fingerprint_matches=matches,actual_reading='尺寸/全部材料频次/全部9BE先读；未读全palette Properties/全源空间/PNG，尚非完整研究。',purpose_candidate='cod3 NPC03竹林居住空间的候选；实物确有68bamboo planks/88bamboo stair/60mud bricks、两床两处，但竹材/namespace不能证明中国茅屋或独立整栋。先查双端床区/多门/耕地的整体旧家族。',status='PARTIAL_ONLY_NEEDS_WHOLE_FAMILY_AND_THEME_QUALIFICATION',new_complete_whole_studies=0,formal_credit_added=0,tasks_deleted=0,limits=['无exact-member或几何hash命中不代表语义新例。','4个jigsaw里装饰/入口/两村民口不拆4建筑；两床不拆2房屋。','竹阶屋面不当茅草盖；任务饮茶观棋/NPC夜回屋未验，不能当完成。']))
put('active-checkpoint.json',dict(batch=305,status='NEXT_DISTINCT_TOPIC_SOURCE_STARTED_HEADER_ONLY',last_complete304=bind(R/'docs/architecture/research-20261104-smithy-304/RECEIPT.json'),source=n,next='先查原家族与真正东亚竹林民居资格，再决定全源/PNG；尚未作资格或独立信用结论。不中断清零原参考，不重做304/301。',new_complete_whole_studies=0,formal_credit_added=0,tasks_deleted=0))
print(json.dumps(dict(header=bind(P/'header-precheck.json'),fingerprint_matches=len(matches),old_member_hits=len(hits),BE=len(BE),new_complete_whole_studies=0),ensure_ascii=False))
