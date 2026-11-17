import json,hashlib,zipfile
from pathlib import Path
P=Path(__file__).resolve().parent;PRE=P.parent/'research-20261104-smithy-211';assert not(P/'RECEIPT.json').exists()
def read(p):return json.loads(Path(p).read_text())
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
checks=[]
def check(k,v):
 checks.append(dict(check=k,passed=bool(v)));assert v,k
r=read(P/'raw-source-audit.json')['candidates'][0];n=r['nbt_decoded_original'];pal=n['palette']
check('sizeDV',n['size']==[13,25,19] and n['DataVersion']==3953)
check('palette count139',len(pal)==139)
check('stored counts machine only',len(n['blocks'])==2195 and r['nonair']==1559 and r['air']==636 and sum('nbt'in b for b in n['blocks'])==57)
check('no alchemy heat palettes',not any(s['Name'] in ['minecraft:brewing_stand','minecraft:cauldron','minecraft:water_cauldron','minecraft:lava_cauldron','minecraft:furnace','minecraft:smoker','minecraft:blast_furnace','minecraft:campfire','minecraft:soul_campfire'] for s in pal))
functional=[dict(pos=b['pos'],state=pal[b['state']]) for b in n['blocks'] if pal[b['state']]['Name']=='minecraft:crafting_table'];put('bounded-functional-markers.json',dict(crafting_tables=functional,no_alchemy_heat_palette=True,whole_room_organization_not_inferred=True,credit=0))
check('no PNG generated or viewed',len(list(P.glob('*.png')))==0)
check('fixed archive',bind(r['source_archive'])['sha256']==r['source_archive_sha256'])
with zipfile.ZipFile(r['source_archive']) as z:check('source member hash',hashlib.sha256(z.read(r['member'])).hexdigest()==r['nbt_sha256'])
correction=read(P/'211-wording-correction.json');check('211 exact prior binding',bind(correction['prior_binding']['path'])['sha256']==correction['prior_binding']['sha256'])
# Query only the one already read saved-source cell for the specific text correction, no old NBT/image replay.
oldn=read(PRE/'raw-source-audit.json')['candidates'][0]['nbt_decoded_original'];pot=next(b for b in oldn['blocks'] if b['pos']==[1,4,3]);check('one saved pot state actual correction',oldn['palette'][pot['state']]['Name']=='minecraft:potted_mangrove_propagule')
put('manual-review.json',dict(batch=212,case='F03',source={k:v for k,v in r.items() if k not in ['nbt_decoded_original','material_counts']},status='BOUNDED_FUNCTIONAL_APPLICABILITY_SCREEN_ZERO_NOT_COMPLETE_WHOLE_STUDY',observations=[
'13×25×19/DV3953 big_house源，139palette全文实际读；不因文件名big或25高称完整多层炼药楼。',
'完整palette没有brewingstand/cauldron或各water/lava锅、炉/烟炉/高炉/营火，只见craftingtable及床/箱/墙饰/脚手架等，NPC06熬药用途未证。当前到此保留有界0，不因沼泽住宅或大体量强行补成药楼。',
'机器解码2195stored=1559非air636air/57BE/entities[]仅原保存数量；本批未读全部57BE、25全层索引、任何PNG、完整空间分区或近族七维，不能声称一项完整建筑研究。',
'当前脚本records-only，0PNG/0实际新完整context/metadata全文阅读；保存的JSON不是已读的依据。不复开候选F01temple/F02church旧图/NBT，原screen有界排除，不抹消原研究。',
'211facade残留文字2?已在本212独立勘误，实际盆栽(1,4,3)为potted_mangrove_propagule；只核保存原解码该格、不重开原NBT/图，不修改已封211。无新信用。',
'无Java/游戏/网络/声音亮度唤醒/用户实例原档/专业资产/共享Jar/Git/主清单写入，未1000不生产或删任务。'],actual_reading=dict(palette=139,full_BE_read=False,whole_layers_read=False,PNG_actual_viewed=0,PNG_generated=0,full_context_JSON=0,full_metadata=0,complete_whole_spatial_study=False,one_prior_saved_cell_for_wording_correction=True),formal_credit_added=0,new_reference_proposal=0))
for name in ['latest-independent-admissions.json','carried-forward-pending.json']:
 d=read(PRE/name);d['previous211_binding']=bind(PRE/name);d['203first209_current212_increment']=0;d['157first206_current212_increment']=0
 if name.startswith('latest'):d['current_batch_formal_credit_added']=0
 else:d['current_batch_new_pending']=0;d['current_batch_pending_cases']=[];d['212F03_bounded_workflow_unproven0']=dict(increment=0,new_pending=0)
 put(name,d)
protected=[]
for f in read(PRE/'protected-inputs-current.json')['files']:
 oldbind=f['current211'];now=bind(oldbind['path']);protected.append(dict(last211_checkpoint=oldbind,current212=now,unchanged=oldbind==now))
put('protected-inputs-current.json',dict(files=protected,baseline='saved211 checkpoint',this_chat_product_writes=False,concurrent_changes_not_reverted=True))
put('verification.json',dict(status='PASS',check_count=len(checks),checks=checks,machine_checks_not_reference_credit=True))
s=dict(batch=212,status='BOUNDED_BIG_SWAMP_HOUSE_FUNCTION_SCREEN_ZERO',formal_credit_added=0,accepted203_first209_current_increment=0,accepted157_first206_current_increment=0,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,NPC06_total=None,new_complete_whole_studies=0,bounded_original_sources=1,new_qualifying_proposals=0,active_pending=[],palette=139,full_BE_read=False,PNG_actual_viewed=0,PNG_generated=0,java_run=False,game_run=False,network_used=False,production=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,protected_input_concurrent_changes=sum(not a['unchanged'] for a in protected),next='Find materially applicable complete work/processing buildings beyond studied sleeping dwellings and palette variants; reference suitability before expensive full diagrams. Preserve scoped valid references.')
put('session.json',s);put('active-checkpoint.json',s);files=[bind(f) for f in sorted(P.iterdir()) if f.is_file() and f.name!='RECEIPT.json'];put('RECEIPT.json',dict(**s,files=files,verification_checks=len(checks)));print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),files=len(files),checks=len(checks),functional=functional),ensure_ascii=False))
