"""Reconstruct an unprocessed original reference from statically read placement, not game content."""
import json,hashlib,sys,math
from pathlib import Path
from zipfile import ZipFile
from collections import Counter
P=Path(__file__).resolve().parent;R=P.parents[2];assert not(P/'RECEIPT.json').exists()
sys.path.insert(0,str(R/'tools/architecture'))
from nbt_read import read
def ld(p):return json.loads(Path(p).read_text())
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def put(n,v,compact=False):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=None if compact else 2,separators=(',',':')if compact else None)+'\n')
root=ld(P/'StructureGuling-static.json');piece=ld(P/'StructureGuling$Piece-static.json');arc=root['source']['archive']
assert bind(arc['path'])==arc
mapping_dir=Path('/Users/a15356015027/.gradle/caches/forge_gradle/minecraft_repo/versions/1.20.1')
mp=mapping_dir/'mcp_mappings.tsrg';official=mapping_dir/'client_mappings.txt';mlines=mp.read_text().splitlines();olines=official.read_text().splitlines()
def block(lines,header):
 i=next(i for i,s in enumerate(lines)if s.startswith(header));j=i+1
 while j<len(lines)and(lines[j].startswith((' ','\t'))or not lines[j]):j+=1
 return [dict(line_number=k+1,text=lines[k])for k in range(i,j)]
targets=[('net.minecraft.core.BlockPos','gu', ['m_7918_','m_121955_','m_7954_'], [' offset(', ' rotate(']),('net.minecraft.core.Vec3i','hz',['m_123341_','m_123342_','m_123343_'],['getX()','getY()','getZ()']),('net.minecraft.world.level.ChunkPos','clt',['m_45604_','m_45605_'],['getMinBlockX','getMinBlockZ']),('net.minecraft.world.level.levelgen.structure.templatesystem.BlockIgnoreProcessor','duv',['f_74046_'],['STRUCTURE_BLOCK -> b']),('net.minecraft.world.level.levelgen.structure.templatesystem.StructurePlaceSettings','dvp',['m_163782_'],['setKeepLiquids']),('net.minecraft.tags.BlockTags','anq',['f_144287_'],['FEATURES_CANNOT_REPLACE'])]
cross=[]
for name,obf,srgkeys,named in targets:
 ob=block(olines,name+' ->');actual=ob[0]['text'].split(' -> ')[1].rstrip(':');tb=block(mlines,actual+' ')
 sr=[v for v in tb if any(k in v['text']for k in srgkeys)];nr=[v for v in ob if any(k in v['text']for k in named)];assert sr and nr
 cross.append(dict(class_name=name,obfuscated_class=actual,SRG_lines=sr,official_lines=nr))
put('mapping-crosswalk.json',dict(SRG=bind(mp),official=bind(official),crosswalk=cross,meaning='BlockPos m_7918_ and m_121955_ are additive offset, not subtract; inherited m_123341/2/3 are X/Y/Z. f74046 is STRUCTURE_BLOCK, not AIR. m163782 is setKeepLiquids, not ignoreEntities.',limits='Local1.20.1 mapping chain for reading fixedmod class references; not runtime compatibility or source execution.'))
origins={1:[27,2,27],2:[1,2,27],3:[1,2,1],4:[27,2,1]}
expected_sizes={1:[27,45,27],2:[26,45,27],3:[26,45,26],4:[27,45,26]}
palette=[];pmap={};merged={};sources=[];contexts=[]
meta=R/'docs/architecture/research-20261101-dungeons-026/all-structure-metadata.json';metadata=ld(meta)
with ZipFile(arc['path'])as z:
 for i in range(1,5):
  member=f'data/eeeabsmobs/structures/guling_{i}.nbt';raw=z.read(member);d=read(raw);e=next(x for x in metadata['entries']if x['member']==member);assert hashlib.sha256(raw).hexdigest()==e['nbt_sha256'];assert d['size']==expected_sizes[i]
  put(f'original-part{i}.json',d,True);localpal=d['palette'];remap={}
  for j,s in enumerate(localpal):
   key=json.dumps(s,sort_keys=True,separators=(',',':'))
   if key not in pmap:pmap[key]=len(palette);palette.append(s)
   remap[j]=pmap[key]
  offset=[origins[i][0]-1,0,origins[i][2]-1]
  for b in d['blocks']:
   q=tuple(b['pos'][k]+offset[k]for k in range(3));assert q not in merged
   merged[q]=dict(pos=list(q),state=remap[b['state']],**({'nbt':b['nbt']}if'nbt'in b else{}))
  sources.append(dict(part=i,member=member,raw_sha256=e['nbt_sha256'],original=bind(P/f'original-part{i}.json'),size=d['size'],DataVersion=d['DataVersion'],stored=len(d['blocks']),unknown=math.prod(d['size'])-len(d['blocks']),palette=len(localpal),BE=sum('nbt'in b for b in d['blocks']),entities=d.get('entities',[]),relative_to_generation_base=origins[i],normalized_origin=offset))
 for member in ['data/eeeabsmobs/worldgen/structure/guling.json','data/eeeabsmobs/worldgen/structure_set/guling.json','data/eeeabsmobs/tags/worldgen/biome/has_structure/guling.json','data/eeeabsmobs/tags/worldgen/structure/eye_of_guling.json']:
  raw=z.read(member);contexts.append(dict(member=member,sha256=hashlib.sha256(raw).hexdigest(),json=json.loads(raw)))
 for member in ['assets/eeeabsmobs/lang/zh_cn.json','assets/eeeabsmobs/lang/en_us.json']:
  if member in z.namelist():
   raw=z.read(member);lang=json.loads(raw);put(Path(member).stem+'-selected-localization.json',dict(member=member,sha256=hashlib.sha256(raw).hexdigest(),selected={k:v for k,v in lang.items()if'guling'in k},limits='Selected original keys only; not full lang JSON reading or Chinese architectural qualification.'))
put('source-context.json',dict(archive=arc,resources=contexts))
entities=[]
for v in sources:
 for e in v['entities']:
  off=v['normalized_origin'];entities.append(dict(part=v['part'],entity=e,normalized_pos=[e['pos'][i]+off[i]for i in range(3)],normalized_blockPos=[e['blockPos'][i]+off[i]for i in range(3)],boundary='Keep raw entity including historical nested nbt.Pos/Tile coords untouched; normalized anchors use template outer pos/blockPos only. No entity spawned or NBT runtime transformation claimed.'))
put('merged-source-entities.json',entities)
put('merged-original-reference.json',dict(size=[53,45,53],palette=palette,blocks=list(merged.values()),entities=entities,reference_only=True,unprocessed=True,translation_basis='Normalize minX/Z=1 to0 and y start1+OFFSET1 to0; sourceworldY=-30..14, not actual generated terrain.'),True)
layers=[]
for y in range(45):
 rows=[]
 for zz in range(53):
  vals=[merged[x,y,zz]['state']if(x,y,zz)in merged else None for x in range(53)];runs=[]
  for value in vals:
   if runs and runs[-1][0]==value:runs[-1][1]+=1
   else:runs.append([value,1])
  rows.append(runs)
 layers.append(dict(y=y,rows_z=rows))
put('merged-full-layers-RLE.json',dict(legend='Rows z0..52, each [global_palette_index,count] increases x0..52; null is omitted unknown, not air. All original source states retained; structure blocks NOT processed away in this reference.',layers=layers),True)
be=[dict(pos=b['pos'],state=palette[b['state']],nbt=b['nbt'])for b in merged.values()if'nbt'in b];put('merged-all-BE.json',be)
stats=dict(size=[53,45,53],declared=53*45*53,stored=len(merged),nonair=sum(palette[b['state']]['Name']!='minecraft:air'for b in merged.values()),air=sum(palette[b['state']]['Name']=='minecraft:air'for b in merged.values()),unknown=53*45*53-len(merged),palette=len(palette),BE=len(be),entities=len(entities),entity_counts_by_part={str(v['part']):len(v['entities'])for v in sources},layers=45,rows=45*53,materials=dict(Counter(palette[b['state']]['Name']for b in merged.values())))
put('source-binding.json',dict(archive=arc,metadata=bind(meta),parts=sources,merged_original_reference=bind(P/'merged-original-reference.json'),counts=stats,source_context=bind(P/'source-context.json'),class_root=bind(P/'StructureGuling-static.json'),class_piece=bind(P/'StructureGuling$Piece-static.json'),mapping=bind(P/'mapping-crosswalk.json'),boundary='Offline raw reference reconstructed by manually read source placement chain; world processors/marker spawning/liquids/native placement not run. Not yet full architectural study.'))
print(json.dumps(dict(parts=[{k:v[k]for k in ['part','size','DataVersion','stored','unknown','palette','BE','normalized_origin']}for v in sources],counts={k:v for k,v in stats.items()if k!='materials'}),ensure_ascii=False))
