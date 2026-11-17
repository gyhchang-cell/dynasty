import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;PRE=P.parent/'research-20261104-smithy-200'
assert not (P/'RECEIPT.json').exists()
def read(p):return json.loads(Path(p).read_text())
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
raw=read(P/'raw-source-audit.json')['candidates'][0];n=raw['nbt_decoded_original'];checks=[]
def check(k,v):
 checks.append(dict(check=k,passed=bool(v)));assert v,k
check('sizeDV',n['size']==[5,12,5] and n['DataVersion']==3105)
check('original counts',len(n['palette'])==24 and len(n['blocks'])==300 and raw['air']==225 and raw['nonair']==75 and n['entities']==[])
check('air6',n['palette'][6]['Name']=='minecraft:air')
g={tuple(b['pos']):b['state'] for b in n['blocks']}
for layer in read(P/'original-index-grid.json')['layers']:
 for z,row in enumerate(layer['rows_z0_4']):check('grid y%d z%d'%(layer['y'],z),row==[g[(x,layer['y'],z)] for x in range(5)])
check('all y9..11 air',all(v==6 for (x,y,z),v in g.items() if y>=9))
be=[b for b in n['blocks'] if 'nbt' in b];check('two BE',len(be)==2)
check('single socket bottom',be[0]['pos']==[2,0,2] and be[0]['nbt']['pool']=='minecraft:empty' and be[0]['nbt']['final_state']=='minecraft:dark_oak_planks')
ctx=read(P/'source-context.json');pool=ctx['candidates'][0]['contexts'][0]['json'];check('12 profession components pool',len(pool['elements'])==12 and pool['fallback']==pool['name'])
put('manual-review.json',dict(cases=[dict(id='F01',source={k:v for k,v in raw.items() if k not in ['nbt_decoded_original','material_counts']},status='ORIGINAL_GRID_COMPONENT_EXCLUSION_ZERO_NOT_COMPLETE_BUILDING',complete_original_spatial_study=False,full_original_grid_screening_complete=True,seven_dimensions={
'layout':'5×5职业内装：整块y0深橡木底板、低层设备及零星铜块，四周与主要中段全air，无独立建筑墙/门。只凭profession文件名不能认完整铺子。',
'proportion':'5×12×5/DV3105，300保存=75非air+225显式air，零省略；24palette/2BE/entities[]，12层60行300格全读。y9..11全air，高度12不等12层或塔屋。',
'facade':'没有连续外墙、门窗或立柱围护，铜块为局部设备背景/基座，不编成封闭建筑立面。',
'roof':'y7两条砖/花岗阶与顶半砖板、y8中部砖与双花岗板/两边底半板，属于局部屋盖片段；y4灯笼接y5/6链，无撑到地面完整外围。',
'materials':'y1(2,1,3)smithing_table；(3,1,1)polished_deepslate上(3,2,1)lava_cauldron；(4,3,4)west chipped_anvil下两层铜，箱(0,1,4)west。实际smithing_table不是炉，不把lava_cauldron叫熔炉或完整热锻链。',
'circulation':'仅(2,1,1)west ladder一格，y2同位air，不能说完整上楼梯或可达阁楼；设备散布同一未围护面，无法独立证明门、外围接入、楼层路线。',
'ground_support':'y0全5×5木板，中(2,0,2)jigsaw down_west/rollable，name与target bottom，pool empty/final深橡木。仅此片段无法确认所附建筑/世界地面及各设备人体操作高度；不因底板完整等同完整房屋。'},limits=[
'全部24palette/2BE/entities[]和12层60行300原格已实际完整读；0PNG，采用原格组件筛除，不称全视觉研究或完整建筑样本。',
'唯一profession_misc选池完整JSON已读，12等权职业片段、legacy rigid/empty processor/fallback自身；其余11源未读，不计12栋。',
'底部empty socket不证明无宿主；JSON精确字面搜索未发现其它rustic pool引用，仅是有限JSON检索，没有搜索宿主NBT接口或证明绝无宿主。未来若研究宿主，应整体计数而非组件各计。',
'工具匠loot vanilla路径不在当前Jar，记录missing；原箱没有Seed，不编造内容/生成/取货回执。META-INF/mods.toml、fabric.mod.json、pack.mcmeta三篇全文实际读；fabric原转义串不擅自改写。',
'各设备方块和高度只表明该组件内容；无床/原实体/独立外壳；不通过设备数、屋面、高度或指纹取得建筑信用。',
'当前正式0/新提议0；197first199/190first193仅历史一次接受本批后续0，157W01唯一活跃whole提议、182HOLD0、064未追认；COD4153/847,NPC05+0,NPC01未知。',
'无Java/游戏/网络/声音亮度唤醒/用户实例/共享Jar/生产资产/Git/主清单改动，无删除任务，无主动工时或全部完成声明。'],formal_credit_added=0,new_reference_proposal_maximum=0)]))
for name in ['latest-independent-admissions.json','carried-forward-pending.json']:
 d=read(PRE/name)
 if name.startswith('latest'):
  d['previous_binding']=bind(PRE/name);d['current_batch_formal_credit_added']=0;d['all_prior_acceptances_carry_only_no_current_increment_201']=dict(increment=0,old_NBT_or_PNG_reopened=False)
 else:
  d['previous_batch_receipt']=bind(PRE/'RECEIPT.json');d['current_batch_new_pending']=0;d['current_batch_pending_cases']=[];d['201_rustic_toolsmith_component_excluded']=dict(complete_building=False,new_pending=0,credit=0);d['197first199_later_carry_increment_201']=0;d['190first193_later_carry_increment_201']=0
 put(name,d)
orig=read('docs/cod4/audit-20261022/coordinator-smithy197-F04-ring-work-tower-whole-review-20261110.json')
check('197 original object exact carry',read(P/'latest-independent-admissions.json')['newly_notified_NPC01_admission_197_F04']['full_Main_judgment_preserved_exact']==orig and read(P/'carried-forward-pending.json')['197F04_NPC01_resolved_accept1_first199']['full_Main_judgment_preserved_exact']==orig)
check('157 sole active',len(read(P/'carried-forward-pending.json')['carried_unresolved_whole_reference_proposals'])==1 and read(P/'carried-forward-pending.json')['carried_unresolved_whole_reference_proposals'][0]['batch']==157)
protected=[]
for f in read(PRE/'protected-inputs-current.json')['files']:
 old=f['current200'];now=bind(old['path']);protected.append(dict(last200_checkpoint=old,current201=now,unchanged=old==now))
check('protected8 same vs200',len(protected)==8 and all(x['unchanged'] for x in protected))
put('protected-inputs-current.json',dict(files=protected,baseline='200 checkpoint not fresh start201 snapshot',this_chat_product_writes=False,concurrent_changes_not_reverted=True))
put('verification.json',dict(status='PASS',check_count=len(checks),checks=checks,machine_checks_not_semantic_credit=True))
session=dict(batch=201,status='COMPONENT_EXCLUDED_SOURCE_GRID_SCREEN_ONLY',formal_credit_added=0,new_qualifying_reference_proposals=0,new_complete_building_studies=0,actual_original_component_grid_studies=1,original_grid_layers=12,original_grid_rows=60,original_grid_positions=300,palette=24,BE=2,PNG_actual_viewed=0,full_context_JSON=1,full_metadata=3,accepted197_first199_later_increment=0,accepted190_first193_later_increment=0,COD4_accepted_baseline=153,COD4_gap=847,COD4_increment=0,NPC05_increment=0,NPC01_cumulative=None,java_run=False,game_run=False,network_used=False,product_files_written=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,next='Continue new complete related building sources; exclude remaining rustic profession inserts from whole-building counts. F03 mountain mason remains only fingerprint screened, no full reading credit.')
put('session.json',session);put('active-checkpoint.json',session)
files=[bind(p) for p in sorted(P.iterdir()) if p.is_file() and p.name!='RECEIPT.json'];put('RECEIPT.json',dict(**session,files=files,verification_checks=len(checks)))
print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),files=len(files),checks=len(checks)),ensure_ascii=False))
