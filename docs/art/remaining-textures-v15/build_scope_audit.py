from pathlib import Path
from PIL import Image
import json, re, hashlib, collections
R=Path('/Users/a15356015027/Desktop/dynasty');D=R/'docs/art';O=D/'remaining-textures-v15';A=R/'src/main/resources/assets/dynasty'
items=json.loads((O/'all-current-items.json').read_text());ids={x['id'] for x in items}; ev=collections.defaultdict(list)
def add(id,path,kind,note=''):
 if id in ids:
  v={'path':str(path),'kind':kind,'note':note}
  if v not in ev[id]:ev[id].append(v)
for d in sorted(D.iterdir()):
 if not d.is_dir() or any(s in d.name for s in ['native16','references','accessory-detail','armor-sample','remaining-textures']):continue
 for p in d.rglob('*.json'):
  if any(s in p.relative_to(d).parts for s in ['before','source','sources','runtime','qa']):continue
  if not any(s in p.name for s in ['assets','manifest','weapons','prompts','remasters']):continue
  try:j=json.loads(p.read_text())
  except:continue
  def scan(v):
   if isinstance(v,dict):
    for k,x in v.items():
     if k=='id' and isinstance(x,str) and x in ids:add(x,p.relative_to(R),'art_record','Dedicated remaster/sample record; source/before pixels alone are not used as completion evidence.')
     if k in ids:add(k,p.relative_to(R),'art_record','Dedicated artwork prompt accompanied by this art batch delivery README/export script.')
     scan(x)
   elif isinstance(v,list):
    for x in v:scan(x)
  scan(j)
 for p in d.rglob('*.png'):
  rel=p.relative_to(d)
  if p.stem in ids and any(s in rel.parts for s in ['after','item','armor','samples']) and not any(s in rel.parts for s in ['before','source','sources','runtime','qa','mesh-qa']):
   add(p.stem,p.relative_to(R),'finished_png','Actual after/item/armor/sample PNG; not source or before.')
manual={
 'tools/art/export_guanyu_weapons.sh':['tianzi_sword','qinglong_dao'],
 'tools/art/export_houyi_bow_v2.sh':['houyi_bow','houyi_bow_pulling_0','houyi_bow_pulling_1','houyi_bow_pulling_2'],
 'tools/art/export_readable_batch_01.sh':['alchemy_furnace_charm','jade_ruyi','wine_gourd'],
 'tools/art/export_readable_batch_02.sh':['phoenix_hairpin','bagua_mirror','tiger_tally'],
 'tools/art/export_weapon_batch_01.sh':['longyuan_sword','leiting_hammer'],
 'tools/art/gen_tab_icon.py':['dynasty_emblem']}
for p,names in manual.items():
 for id in names:add(id,p,'dedicated_art_export','Existing authored art mechanical packaging; dynasty_emblem script explicitly packages the completed dragon-and-jade-seal artwork, not a procedural placeholder.')
thread={'bronze_mirror':'docs/art/accessory-detail-v13-sample/manifest.json','jade_pendant':'docs/art/native16-rework-v11/candidate-manifest.json','storm_charm':'docs/art/native16-rework-v11/candidate-manifest.json','dark_iron_chestplate':'docs/art/armor-sample-v14/manifest.json'}
for id,p in thread.items():add(id,p,'this_thread_candidate','Candidate already drawn in this task; not yet installed. Bronze mirror v13 approved; dark iron v14 may receive explicitly authorized refinement only.')
# These generators are original legacy art/template scripts, not later fine-art completion records.
gen_files=[p for p in (R/'tools/art').glob('gen*.py') if any(s in p.stem for s in ['gen_items','gen_food','gen_trinkets','gen_armor','gen_gear','gen_weapons','gen_dynasty3','gen_relic_materials','gen_trinket_box','gen_dragon_palace']) and not p.stem.endswith('_json')]
texts={p:p.read_text() for p in gen_files}
for row in items:
 id=row['id'];p=R/row['path'];im=Image.open(p).convert('RGBA');e=ev[id]
 legacy=[]
 for f,s in texts.items():
  pat=r'[\"\x27]'+re.escape(id)+r'[\"\x27]'
  m=re.search(pat,s)
  if m:legacy.append({'path':str(f.relative_to(R))+':'+str(s.count('\n',0,m.start())+1),'kind':'legacy_generator','note':'Old procedural/template/copy artwork generator reference; NOT counted as a fine-art completion.'})
 if id.endswith(('_helmet','_chestplate','_leggings','_boots')):
  prefix=id.rsplit('_',1)[0]
  for f,s in texts.items():
   if 'armor' not in f.stem and f.stem!='gen_dynasty3':continue
   m=re.search(r'[\"\x27]'+re.escape(prefix)+r'[\"\x27]',s)
   if m:legacy.append({'path':str(f.relative_to(R))+':'+str(s.count('\n',0,m.start())+1),'kind':'legacy_set_generator','note':'Armor set template/copy/tint generator; not bespoke art completion.'})
 row['resource_type']='item_texture';row['namespace_id']='dynasty:'+id
 row['item_model']='src/main/resources/assets/dynasty/models/item/'+id+'.json'
 mp=R/row['item_model'];row['item_model_definition']=json.loads(mp.read_text()) if mp.exists() else None
 row['opaque_color_count']=len({v for v in im.get_flattened_data() if v[3]});row['alpha_values']=sorted(set(im.getchannel('A').get_flattened_data()))
 row['is_armor_icon']=id.endswith(('_helmet','_chestplate','_leggings','_boots'))
 row['legacy_evidence']=legacy
 if any(v in id for v in ['ritual','zhenyuan']):cl='uncertain_preserve';why='Parallel ritual/zhenyuan ownership; do not touch regardless of completion.'
 elif id in thread:cl='completed_this_thread';why='Existing v11/v13/v14 candidate already created; preserve even if uninstalled.'
 elif e:cl='completed_elsewhere';why='Dedicated previous art batch/artifact/export evidence exists; preserve even if not installed or not independently user-approved.'
 elif legacy and row['size']==[32,32]:cl='legacy_pending';why='Native current 32px legacy artwork with old procedural/copy generator evidence; no later dedicated art completion record found.'
 else:cl='uncertain_preserve';why='No sufficiently specific art provenance; preserve rather than infer unfinished from resolution or absence of a record.'
 row['classification']=cl;row['classification_reason']=why;row['evidence']=e
 row['protected']=cl!='legacy_pending'
 row['current_source_hash_matches_initial']=hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
# All 34 production dedicated block PNGs are protected v9 work, even those this thread sampled later.
v9={x['id']:x for x in json.loads((D/'vanilla-v9/manifest.json').read_text())}
blocktex=[]
for p in sorted((A/'textures/block').glob('*.png')):
 im=Image.open(p);id=p.stem;blocktex.append({'id':id,'namespace_resource':'dynasty:block/'+id,'resource_type':'block_texture','path':str(p.relative_to(R)),'size':list(im.size),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'classification':'completed_elsewhere' if id in v9 else 'uncertain_preserve','protected':True,'evidence':[{'path':'docs/art/vanilla-v9/manifest.json','kind':'dedicated_finished_block','note':'User explicitly forbids redrawing the 34 completed v9 block textures.'}] if id in v9 else [{'path':str(p.relative_to(R)),'kind':'parallel_or_unknown','note':'Unknown/new production block asset; preserve.'}]})
def models_for(v):
 out=[]
 if isinstance(v,dict):
  if isinstance(v.get('model'),str):out.append(v['model'])
  for x in v.values():out+=models_for(x)
 elif isinstance(v,list):
  for x in v:out+=models_for(x)
 return out
def model_textures(mid,seen=None):
 seen=seen or set()
 if mid in seen:return set()
 seen.add(mid)
 if not mid.startswith('dynasty:'):return set()
 p=A/'models'/(mid.split(':',1)[1]+'.json')
 if not p.exists():return set()
 j=json.loads(p.read_text());out={v for v in j.get('textures',{}).values() if isinstance(v,str) and not v.startswith('#')}
 if isinstance(j.get('parent'),str):out|=model_textures(j['parent'],seen)
 return out
blocks=[]
workshops={'marrow_vat','essence_condenser','jade_mending_forge','vitality_shrine','hide_stretcher','herbal_basin','lapidary_bench','ember_brazier'}
for p in sorted((A/'blockstates').glob('*.json')):
 id=p.stem;mods=sorted(set(models_for(json.loads(p.read_text()))));tex=sorted(set().union(*(model_textures(m) for m in mods))) if mods else []
 own=any('ritual' in x or 'zhenyuan' in x for x in [id,*mods])
 direct=id in v9 or id=='crimson_pillar' or id in workshops
 cl='completed_elsewhere' if direct and not own else 'uncertain_preserve'
 e=[{'path':'docs/art/vanilla-v9/release-notes.md' if direct else str(p.relative_to(R)),'kind':'finished_block_or_workshop' if direct else 'existing_model','note':'Explicit v9 completed block/workshop; existing textures protected.' if direct else 'Uses existing models and vanilla/shared art; do not infer missing art.'}]
 if own:e.append({'path':'current-user-scope','kind':'parallel_owner','note':'ritual/zhenyuan parallel task resources are protected; not an unfinished texture assignment.'})
 if id=='bounty_board':e.append({'path':'docs/content/bounty-board-v1.md:178','kind':'temporary_vanilla_reference','note':'Document calls bookshelf texture temporary; preserve as uncertain, not count as bespoke finished texture nor auto-authorize modifying another task model.'})
 if id in {'star_dial','clue_tablet','echo_bell','element_lamp','ruin_controller','ruin_gate'}:e.append({'path':'docs/content/ruin-puzzles-v1.md','kind':'other_task_mechanism','note':'Existing puzzle resource references; preserve during texture work.'})
 blocks.append({'id':id,'namespace_id':'dynasty:'+id,'resource_type':'block_id','blockstate':str(p.relative_to(R)),'models':mods,'textures':tex,'classification':cl,'protected':True,'evidence':e})
counts=dict(collections.Counter(x['classification'] for x in items))
res={'schema':1,'scope':'476 existing item texture files (bow stages are resource IDs), plus 34 dedicated block PNGs and 46 current blockstate IDs. Armor wear atlases are not item icons.','rules':['Source/before images alone never establish completion.','Old procedural/copy/tint/register generators do not establish bespoke art completion.','Explicit previous artwork remains protected even uninstalled.','All 34 v9 block textures protected per newest user instruction.','Parallel ritual/zhenyuan resources always protected.','Dark iron chestplate v14 can only receive user-authorized refinement of its existing candidate.'],'counts':{'items':counts,'item_total':len(items),'block_texture_total':len(blocktex),'block_id_total':len(blocks)},'pending_non_armor_ids':sorted(x['id'] for x in items if x['classification']=='legacy_pending' and not x['is_armor_icon']),'pending_armor_ids':sorted(x['id'] for x in items if x['classification']=='legacy_pending' and x['is_armor_icon']),'items':sorted(items,key=lambda x:x['id']),'block_textures':blocktex,'blocks':blocks}
(O/'audit-items.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
for filename,want in [('PROTECTED.md',True),('TODO.md',False)]:
 selected=[x for x in sorted(items,key=lambda x:x['id']) if x['protected']==want]
 lines=['# '+('已完成/不确定保护清单' if want else '有旧生成器证据的待做清单'),'','审计以当前476张物品贴图、实际美术产物/记录和专用导出脚本为准。before/source本身不计完成；未找到记录也不会单凭尺寸判为待做。','',f'本表 {len(selected)} 张物品贴图。全部34张专属方块贴图保护；46个方块ID均不进入本次自动重绘。完整模型引用见 audit-items.json。','', '| ID | 类别 | 证据 |','|---|---|---|']
 for x in selected:
  proof=x['evidence'] if want else x['legacy_evidence'];paths='；'.join('`'+p['path']+'`' for p in proof[:3]) or x['classification_reason']
  lines.append(f'| `{x["id"]}` | {x["classification"]} | {paths} |')
 if want:
  lines+=['','## 额外保护','','- v6 的 general/jade/sky 四部位共12件、v7 的 bronze/xuantian 四部位共8件图标已有完成记录。','- v13 铜镜已认可；v11 玉佩/雷纹护符及 v14 玄铁胸甲已画候选，未安装也不当成没做。玄铁胸甲仅允许用户明确要求的小幅精修。','- v9 全部34张专属方块图 + 八工坊共有/原版材质；不能为批量数量重复做。','- ritual / zhenyuan 及其模型、UV、注册、建筑资源属于并行任务。','- bounty_board 文档明确是临时复用书架材质；此处标 uncertain_preserve，不伪称专属贴图完成，也不擅改其模型。','- 图标清单不能授权改盔甲共享穿戴层；穿戴层需要单独核对每套UV和完成记录。']
 else:
  lines+=['','## 可机器读取的分组','',f'- 非盔甲 {len(res["pending_non_armor_ids"])} 张：audit-items.json → pending_non_armor_ids。',f'- 盔甲图标 {len(res["pending_armor_ids"])} 张：audit-items.json → pending_armor_ids。','- 没有待自动重绘的专属方块图；本轮不要重画 v9 材质。','- legacy_pending 表示旧模板资源有证据且无后续精修记录，不代表物品功能未实现。']
 (O/filename).write_text('\n'.join(lines)+'\n')
print(json.dumps({'counts':res['counts'],'pending_non_armor':len(res['pending_non_armor_ids']),'pending_armor':len(res['pending_armor_ids']),'uncertain':[x['id'] for x in items if x['classification']=='uncertain_preserve']},ensure_ascii=False,indent=2))
