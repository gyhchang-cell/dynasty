import json,hashlib,zipfile
from pathlib import Path
P=Path(__file__).resolve().parent;PRE=P.parent/'research-20261104-smithy-218';assert not(P/'RECEIPT.json').exists()
def read(p):return json.loads(Path(p).read_text())
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
checks=[]
def ck(k,v):checks.append(dict(check=k,passed=bool(v)));assert v,k
screen=read(P/'pre-render-history-screen.json');rows=read(P/'raw-source-audit.json')['candidates'];r=rows[0];d=r['nbt_decoded_original'];pal=d['palette'];names={a['Name']for a in pal};ctx=read(P/'source-context.json')['candidates'][0]['contexts']
ck('four fresh exact-screen leads not four references',len(screen['rows'])==4 and all(a['eligible_for_new_source_study']for a in screen['rows']))
ck('only first candidate bounded actual read',len(rows)==1 and r['id']=='F01')
ck('size DV palette',d['size']==[14,12,13] and d['DataVersion']==3578 and len(pal)==77)
ck('complete stored coverage but not full manual spatial reading',len(d['blocks'])==2184 and r['air']==1504 and r['nonair']==680)
ck('two original BE',sum('nbt'in b for b in d['blocks'])==2)
ck('no alchemy or heat devices in full palette',not(names&{'minecraft:brewing_stand','minecraft:furnace','minecraft:smoker','minecraft:blast_furnace','minecraft:campfire','minecraft:soul_campfire'}))
entities=d['entities'];alive=[e for e in entities if e['nbt']['id']!='minecraft:item' and e['nbt']['Health']>0];dead=[e for e in entities if e['nbt']['id']!='minecraft:item' and e['nbt']['Health']==0]
ck('ten entity records six zero health two alive two dropped items',len(entities)==10 and len(alive)==2 and len(dead)==6 and sum(e['nbt']['id']=='minecraft:item'for e in entities)==2)
ck('no PNG or layer-RLE generated means zero whole review',not list(P.glob('*.png'))and not list(P.glob('*rle*')))
with zipfile.ZipFile(r['source_archive'])as z:
 ck('fixed archive',bind(r['source_archive'])['sha256']==r['source_archive_sha256']);ck('fixed source',hashlib.sha256(z.read(r['member'])).hexdigest()==r['nbt_sha256'])
 ck('three direct contexts fixed',len(ctx)==3 and all(hashlib.sha256(z.read(a['member'])).hexdigest()==a['sha256']for a in ctx))
put('manual-review.json',dict(batch=219,status='BOUNDED_FULL_PALETTE_BE_ENTITY_CONTEXT_READING_PURPOSE_HOLD_ZERO',complete_original_spatial_study=False,formal_credit_added=0,new_reference_proposal=0,actual_reading=dict(candidates=1,palette_entries=77,full_BE=2,full_entities=10,full_context_JSON=3,full_metadata=0,full_layers=0,PNG_viewed=0),observations=['F01 Terralith mage/house DV3578 14×12×13，2184stored=1504air+680非air，无省略，但只是机器完整保存，不等全栋空间已人工读。', '实际完整读77palette状态、2BE、10entities、三JSON。craftingtable(10,1,8)、满水cauldron(5,2,4)level3、up barrel(3,1,8)原loot mage/extras；无酿造台及炉/烟熏炉/高炉/营火palette，不能由法师命名推炼药生产。', '10实体为4witch/4pillager/2items，8生物中6个Health0/HurtTime10，另witch26和pillager24；item glassbottle2/stick1，源历史导出状态原样保留，不修资产、不当10NPC。', '原house池house/house2/house3/barracks各weight1、rigid/ground processor，后三完整房屋尚未研究不算新增；name原mage_hice。', 'ground processor只把location calcite条件下grassblock换calcite；extras 13基础物品候选含amethyst/warpedplanks/leather/crossbow/bone/coal/paper等，非炼药配方或已领取回执。', '这轮仅用途筛查，无整栋图、全层人工读、路线/支撑/根生成证明，完整整栋数0；不补写七维完整结论或提议。', '其他F02 fortifiedshepherd/F03 piglinstorage/F04 mushroomcauldron只完成固定来源及历史精确指纹筛查，0实际空间信用，保留后续候选；不声称冻结本地来源耗尽。', '继承218及已采纳157first206/203first209，当前增量0、COD4153/847，NPC01/05/06总数未知。', '无Java/游戏/联网/生产资产/主清单/共享Jar/原档/声亮焦点/Git修改。不删未验任务、不声称1000/全部完成/主动10小时。']))
for name in ['latest-independent-admissions.json','carried-forward-pending.json']:
 a=read(PRE/name);a['previous218_binding']=bind(PRE/name);a['203first209_current219_increment']=0;a['157first206_current219_increment']=0
 if name.startswith('latest'):a['current_batch_formal_credit_added']=0
 else:a['current_batch_new_pending']=0;a['current_batch_pending_cases']=[]
 put(name,a)
protected=[]
for f in read(PRE/'protected-inputs-current.json')['files']:
 old=f['current218'];now=bind(old['path']);protected.append(dict(last218_checkpoint=old,current219=now,unchanged=old==now))
put('protected-inputs-current.json',dict(files=protected,baseline='saved218 checkpoint',this_chat_product_writes=False,concurrent_changes_not_reverted=True));put('verification.json',dict(status='PASS',check_count=len(checks),checks=checks,machine_checks_not_reference_credit=True))
s=dict(batch=219,status='COMPLETE_BOUNDED_MAGE_HOUSE_PURPOSE_SCREEN_ZERO',formal_credit_added=0,accepted203_first209_current_increment=0,accepted157_first206_current_increment=0,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,NPC06_total=None,new_complete_whole_studies=0,new_qualifying_proposals=0,active_pending=[],java_run=False,game_run=False,network_used=False,production=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,protected_input_concurrent_changes=sum(not a['unchanged']for a in protected),next='Inspect frozen219 F02 fortified shepherd complete layout and dye/wash purpose if relevant; or other frozen complete processing source, no machine leads/parts/recolor credit. Reuse exact history, no passed view reopening.')
put('session.json',s);put('active-checkpoint.json',s);files=[bind(f)for f in sorted(P.iterdir())if f.is_file()and f.name!='RECEIPT.json'];put('RECEIPT.json',dict(**s,files=files,verification_checks=len(checks)));print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),files=len(files),checks=len(checks),protected_unchanged=sum(a['unchanged']for a in protected)),ensure_ascii=False))
