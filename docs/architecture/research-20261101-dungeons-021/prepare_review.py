#!/usr/bin/env python3
"""Re-open fixed original buildings, never relabel old templates as new sources."""
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from zipfile import ZipFile
OUT=Path(__file__).resolve().parent
BASE=OUT.parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read
from whole_building_candidates import AIR
SELECTION=[('T01',13,'F03',(11,20,9,12)),('T02',16,'F05',(11,20,9,6)),
 ('C01',11,'F01',(12,20,10,10)),('C02',16,'F02',(9,17,8,7)),('C03',15,'F01',(6,21,9,9))]
def sha(b):return hashlib.sha256(b).hexdigest()
def ev(p):return dict(path=str(p),sha256=sha(p.read_bytes()))
def exact(v,k):
 if isinstance(v,str):return v==k
 if isinstance(v,dict):return any(exact(x,k)for x in v.values())
 if isinstance(v,list):return any(exact(x,k)for x in v)
 return False
def dump(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 entries=[];archives={};specs={};planes=[]
 for ident,batch,oldid,cuts in SELECTION:
  if batch=='WHOLE':
   p=BASE/'continuation-20261022/references/whole-candidates/candidates.json'
   old=next(c for c in json.loads(p.read_text())['candidates']if c['id']==oldid)
   jar=Path(old['source_jar']);member=old['member'];prior_id=oldid
   old_folder=p.parent;image_path=old_folder/f'{oldid}-whole.png'
   # The historical index provides the exact PNG paths, if its naming differs.
   if not image_path.is_file()and old.get('image'):
    image_path=old_folder/old['image']
   if not image_path.is_file():
    paths=[Path(v)if str(v).startswith('/')else old_folder/v for v in old.get('images',[]) if isinstance(v,str)]
    image_path=next(v for v in paths if v.name.endswith('-whole.png'))
   url=old.get('source_url','provenance stored in original index')
  else:
   old_folder=BASE/f'research-20261101-dungeons-{batch:03d}';p=old_folder/'sources.json'
   old=next(c for c in json.loads(p.read_text())['candidates']if c['id']==oldid)
   jar=Path(old['source_archive']);member=old['member'];prior_id=f'{batch:03d}-{oldid}'
   image_path=old_folder/(oldid+'-whole.png');url=old['publisher_url']
  assert image_path.is_file()
  if str(jar)not in archives:archives[str(jar)]=dict(path=str(jar),sha256=sha(jar.read_bytes()),publisher_url=url,url_access='Provenance only, no network request')
  with ZipFile(jar)as z:
   raw=z.read(member);assert sha(raw)==old['nbt_sha256'];d=read(raw);pal=d.get('palette')or d['palettes'][0]
   states={tuple(b['pos']):pal[b['state']]for b in d['blocks']};cells={p:s for p,s in states.items()if s['Name']not in AIR}
   prefix,tail=member.split('/structures/');resource=prefix.split('/')[-1]+':'+tail[:-4];refs=[]
   for name in z.namelist():
    if '/worldgen/template_pool/' in name and name.endswith('.json'):
     b=z.read(name);data=json.loads(b)
     if exact(data,resource):refs.append(dict(member=name,data=data))
  doors=[dict(position=list(p),state=s)for p,s in states.items()if s['Name'].endswith('_door')and s.get('Properties',{}).get('half')=='lower']
  sockets=[dict(position=b['pos'],state=pal[b['state']],data=b.get('nbt',{}))for b in d['blocks']if pal[b['state']]['Name']=='minecraft:jigsaw']
  opening=[dict(position=list(p),state=s)for p,s in states.items()if any(k in s['Name']for k in ['stairs','ladder','door','gate','jigsaw'])]
  entries.append(dict(id=ident,prior_identity=prior_id,original_index=ev(p),original_whole_image=ev(image_path),
   source_archive=str(jar),source_archive_sha256=archives[str(jar)]['sha256'],publisher_url=url,member=member,
   nbt_sha256=sha(raw),size=d['size'],nonair=len(cells),materials=dict(Counter(s['Name']for s in cells.values())),
   doors=doors,sockets=sockets,opening_and_vertical_states=opening,pool_references=refs,
   source_is_previously_studied=True,new_source_template_credit=0,source_dedup_identity=resource))
  specs[ident]=cuts
  selected=[]
  for y in cuts[:2]:
   plane=[dict(position=list(p),state=s)for p,s in states.items()if p[1]==y]
   selected.append(dict(y=y,stored_positions=len(plane),possible_positions=d['size'][0]*d['size'][2],
    explicit_air_positions=sum(s['state']['Name']in AIR for s in plane),
    nonair_positions=sum(s['state']['Name']not in AIR for s in plane),original_states=plane))
  planes.append(dict(id=ident,prior_identity=prior_id,selected_horizontal_planes=selected,
   limits='Original stored states. Missing cells and explicit air remain distinguishable in JSON; no walking/collision solver or room topology certification.'))
 dump('sources.json',dict(source_archives=list(archives.values()),candidates=entries,new_source_templates=0,automatic_credit=0,
  scope='Targeted fresh section review of previous held and accepted complete building sources; IDs retain prior identities, not newly discovered designs.'))
 dump('room-layer-original-states.json',dict(entries=planes,building_credit_added=0))
 detail=module('details',BASE/'research-20261101-dungeons-002/inspect_details.py');detail.OUT=OUT;detail.SPECS=specs;detail.main()
 print('Prior identities:',[e['prior_identity']for e in entries],'; new templates: 0')
if __name__=='__main__':main()
