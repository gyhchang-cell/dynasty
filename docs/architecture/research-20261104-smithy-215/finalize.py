import json,hashlib,zipfile
from pathlib import Path
P=Path(__file__).resolve().parent;PRE=P.parent/'research-20261104-smithy-214';assert not(P/'RECEIPT.json').exists()
def read(p):return json.loads(Path(p).read_text())
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
checks=[]
def check(k,v):checks.append(dict(check=k,passed=bool(v)));assert v,k
rows=read(P/'raw-source-audit.json')['candidates'];check('four bounded source records',len(rows)==4);check('no diagrams',len(list(P.glob('*.png')))==0)
reports=[]
notes=[
'7×4×7营地标记：烟炉(3,1,5)含Slot1 charcoal1但Burn/Cook0、床一对、damaged anvil仅设备线索。未读完整状态/全层和图，无封闭工房/炉料流证明，不因一烟炉一砧直接叫完整相关铁匠铺。',
'12×5×11旧掠夺者营地线索：四mobs接头含1iron_golem、3pillager、箱引用minecraft pillager_outpost loot。已读5BE全文；机器有grindstone/stonecutter不证明锻造房、民用避难水磨或炼药楼，未读全层/图不得推完整空间。',
'13×6×10商人营地线索：3带trek wandering_traders loot桶、一对红床、空Items营火。完整六BE全文已读；仅原名/成员类型，不凭文件名断言整车完整行进结构；未读全部状态/全层/图和loot内容，不转为铁匠/水磨/炼药参考。',
'13×6×9另一商人来源：同3商人loot桶、一对红床、空Items营火；六BE全文读。不同木种/旋转/局部宽度即便指纹不等，也不是新空间族，本批无完整语义研究不能数第二栋。']
for r,note in zip(rows,notes):
 n=r['nbt_decoded_original'];pal=n['palette'];names=sorted(set(s['Name'] for s in pal));be=[b for b in n['blocks'] if 'nbt'in b]
 with zipfile.ZipFile(r['source_archive']) as z:check(r['id']+' original member SHA',hashlib.sha256(z.read(r['member'])).hexdigest()==r['nbt_sha256'])
 check(r['id']+' fixed archive SHA',bind(r['source_archive'])['sha256']==r['source_archive_sha256'])
 reports.append(dict(id=r['id'],source={k:v for k,v in r.items() if k not in ['nbt_decoded_original','material_counts']},bounded_observation=note,unique_material_names_actual_read=names,BE_full_actual_read=len(be),full_palette_states_read=False,full_layers_read=False,PNG_viewed=0,complete_spatial_study=False,source_contexts_saved_not_actual_full_read=True,formal_credit_added=0,new_pending=0))
put('manual-review.json',dict(batch=215,status='BOUNDED_FOUR_ORIGINAL_SOURCES_PURPOSE_UNPROVEN_ZERO',cases=reports,limits=['Only unique material names and all22BE actual read; 21/30/42/41 palette sizes are machine counts, not full property reading.','Four current sources not classified as four complete relevant buildings. No full RLE, PNG, context, root, biome, structureset or processor implementation study.','Saved context objects are evidence available for future reading only; no loot/production/quest/NPC inference from names.','No historical raw NBT/PNG reopened, no source editing. New candidate original decode once each for prefilter fingerprint and once records extraction is not two references.','Accepted source credit preserved:157first206 and203first209 current0, COD4153/847, NPC totals unknown, no1000 complete.','No Java/game/network/assets/sharedJar/master lists/user instance/save/audio/brightness/wake/focus/Git writes; no task delete/production/allcomplete/hour claim.'],complete_original_spatial_studies=0,new_reference_proposals=0,formal_credit_added=0))
for name in ['latest-independent-admissions.json','carried-forward-pending.json']:
 d=read(PRE/name);d['previous214_binding']=bind(PRE/name);d['203first209_current215_increment']=0;d['157first206_current215_increment']=0
 if name.startswith('latest'):d['current_batch_formal_credit_added']=0
 else:d['current_batch_new_pending']=0;d['current_batch_pending_cases']=[];d['215bounded4purpose0']=dict(increment=0,new_pending=0)
 put(name,d)
protected=[]
for f in read(PRE/'protected-inputs-current.json')['files']:
 old=f['current214'];now=bind(old['path']);protected.append(dict(last214_checkpoint=old,current215=now,unchanged=old==now))
put('protected-inputs-current.json',dict(files=protected,baseline='saved214 checkpoint',this_chat_product_writes=False,concurrent_changes_not_reverted=True))
put('verification.json',dict(status='PASS',check_count=len(checks),checks=checks,machine_checks_not_reference_credit=True))
s=dict(batch=215,status='BOUNDED_FOUR_SOURCE_APPLICABILITY_SCREEN_ZERO',formal_credit_added=0,accepted203_first209_current_increment=0,accepted157_first206_current_increment=0,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,NPC06_total=None,new_complete_whole_studies=0,bounded_original_sources=4,new_qualifying_proposals=0,active_pending=[],java_run=False,game_run=False,network_used=False,production=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,protected_input_concurrent_changes=sum(not a['unchanged'] for a in protected),next='Expand frozen local metadata discovery toward complete materially applicable work/processing buildings; do not inflate camp furniture or mansion rooms into whole buildings. Existing2230 dimension machine scan not semantic credit or local source exhaustion.')
put('session.json',s);put('active-checkpoint.json',s);files=[bind(f) for f in sorted(P.iterdir()) if f.is_file() and f.name!='RECEIPT.json'];put('RECEIPT.json',dict(**s,files=files,verification_checks=len(checks)));print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),files=len(files),checks=len(checks)),ensure_ascii=False))
