import json,hashlib,zipfile
from pathlib import Path
P=Path(__file__).resolve().parent;PRE=P.parent/'research-20261104-smithy-210';assert not(P/'RECEIPT.json').exists()
def read(p):return json.loads(Path(p).read_text())
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
checks=[]
def check(k,v):
 checks.append(dict(check=k,passed=bool(v)));assert v,k
r=read(P/'raw-source-audit.json')['candidates'][0];n=r['nbt_decoded_original'];pal=n['palette'];g={tuple(b['pos']):b for b in n['blocks']}
check('sizeDV',n['size']==[7,8,9] and n['DataVersion']==3465)
check('counts',len(pal)==17 and not any('nbt'in b for b in n['blocks']) and len(g)==164 and r['air']==27 and r['nonair']==137 and 504-len(g)==340)
check('two original persistent cat witch',len(n['entities'])==2 and {e['nbt']['id'] for e in n['entities']}=={'minecraft:cat','minecraft:witch'} and all(e['nbt']['PersistenceRequired']==1 for e in n['entities']))
for l in read(P/'original-index-rle.json')['layers']:
 check('nine rows y'+str(l['y']),len(l['rows_z0_8'])==9)
 for z,row in enumerate(l['rows_z0_8']):
  vals=[]
  for s in row.split():
   t=s.split('x');vals += [int(t[0])]*(int(t[1]) if len(t)>1 else 1)
  check('RLE y%d z%d'%(l['y'],z),vals==[g[(x,l['y'],z)]['state'] if (x,l['y'],z)in g else -1 for x in range(7)])
check('water2 cauldron and crafting',pal[g[(4,3,2)]['state']]=={'Properties':{'level':'2'},'Name':'minecraft:water_cauldron'} and pal[g[(3,3,2)]['state']]['Name']=='minecraft:crafting_table')
check('four red glass triggers',[(b['pos']) for b in n['blocks'] if pal[b['state']]['Name']=='minecraft:red_stained_glass']==[[1,0,1],[1,0,6],[5,0,1],[5,0,6]])
check('no bed no ladder no brewing no furnace',not any(s['Name'].endswith('_bed') or s['Name'] in ['minecraft:ladder','minecraft:brewing_stand','minecraft:furnace','minecraft:blast_furnace','minecraft:smoker'] for s in pal))
check('fixed archive',bind(r['source_archive'])['sha256']==r['source_archive_sha256'])
with zipfile.ZipFile(r['source_archive']) as z:
 check('original NBT hash',hashlib.sha256(z.read(r['member'])).hexdigest()==r['nbt_sha256'])
 ctx=read(P/'source-context.json')
 for a in ctx['metadata']:
  b=z.read(a['member']);check('metadata '+a['member'],b.decode()==a['original_text'] and hashlib.sha256(b).hexdigest()==a['sha256'])
 for a in ctx['candidates'][0]['contexts']+read(P/'exact-root-context.json')['records']:
  b=z.read(a['member']);check('context '+a['member'],json.loads(b)==a['json'] and hashlib.sha256(b).hexdigest()==a['sha256'])
check('6PNG actuallyviewed',len(list(P.glob('*.png')))==6)
sc=read(P/'pre-render-history-screen.json')['rows'];check('darkforest same batch role occupancy only',not sc[1]['known_history'] and not sc[1]['historical_exact_matches'] and sc[1]['within_batch_exact_matches']==[{'source':r['member'],'exact_keys':['role_sha256','occupancy_sha256']}])
old192=read(P.parent/'research-20261104-smithy-192/manual-review.json')['cases'][2]
put('saved-complete-family-comparison.json',dict(comparisons=[dict(binding=bind(P.parent/f'research-20261104-smithy-{b}/manual-review.json'),full_judgment=read(P.parent/f'research-20261104-smithy-{b}/manual-review.json')) for b in [206,209]],binding192=bind(P.parent/'research-20261104-smithy-192/manual-review.json'),full192F03=old192,actual_reading='完整192F03七观察/5限制及元数据实际读；206/209完整自有已读判断复用；旧图/NBT不重开。192其它两有界记录文字偶同输出读到，但不升级完整性或信用。',current_comparison='206为低室+高双锅台及高交接屋盖，192F03为浮岛公共酿造柱亭且NPC01相关性HOLD0；209为单床箱室。当前低单室水锅/工作台+南前廊/4柱，与209紧凑单室替换陈设仍不能确认新的整体动线家族；不把水锅、木种、已有女巫实体、单平盖当新整体信用。原用途/旧状态不改，不将192旧NPC01HOLD追授NPC06。',current_credit=0))
put('manual-review.json',dict(batch=211,case='F01',source={k:v for k,v in r.items() if k not in ['nbt_decoded_original','material_counts']},seven_dimensions={
'layout':'紧凑四柱抬高单室，floor2/use3：北内工作台3,3,2与水锅4,3,2并列，南偏东x4,z6开口接南平台z7/8；无卧室/上下工作区/独立药料间或内部交通系统。整间+前廊+柱脚一个原源，不拆四柱/台锅/居民或六木种。',
'proportion':'7×8×9 DV3465；504声明=164保存(137非air27air)+340省略。17palette/0BE/2实体、8层72RLE504位/6PNG实际读看。最高构造y5盖、y6/7全省略不等air；floor2为唯一使用层，8高不等8层。',
'facade':'stripped mangrove四角柱与mangroveplanks低墙，mangrove fence窗格与前廊两栏；西盆胎生苗2?实际1,4,3，窗南北大开口。源无门/玻璃窗，泛色蓝柱foot对应red_stained_glass处理触发标记，不能说成最终玻璃基础或石结构。',
'roof':'y5内部x1..5,z1..6木板平盖，外圈bottom mangrove stairs各方向含转角收边形成浅盖檐；不是高坡阁楼。north/south/east/west灰类色是木阶未保原纹理，y6/7全省略不能宣全屋顶上air净空。',
'materials':'craft3,3,2与water_cauldron4,3,2 level2是真实保存状态，无brewingstand/燃炉/床/储箱/梯。盆栽1,4,3为mangrove_propagule；水锅不推实际熬药/毒药产出/交易。两原实体完整NBT为all_black cat与witch，PersistenceRequired1，各相对坐标/旧绝对NBT.Pos/UUID保留，非黑婆模型/NPC任务。',
'circulation':'南开口4,3/4,6显式air、内4,3/4,5air，通floor2同层外前廊z7的x1..5与z8的x2..4。前廊头部多省略而非显式air；没有门也没有模板内地面升floor2的阶/梯链。用前廊/开口关系作研究，不称原生安全入口/NPC寻路已验。',
'ground_support':'四y0 red_stained_glass触发在x1/5,z1/6，y1/2 strippedmangrove柱。所读processor为自定义pillar_processor/DOWN，把redglass换stripped_mangrove_log[y]，直接替换及延柱意图明确；处理器实现、终止深度、地形/水位实际支承没读/没运行，不能依据四标记宣生成柱已落地。'},limits=[
'17palette/0BE/2实体完整原NBT与8层72RLE504位/6PNG实际读看。2metadata与pool/processor/root/directbiometag4完整JSON实际读，missing[]仅该子集，不等运行全闭环。',
'pool单候选权1 single rigid emptyfallback；root generic_jigsaw size1/start0/WORLD_SURFACE_WG/terrainnone，piece范围cat1/witch1。directbiometag引collections/mangroves未读，structure_set/customprocessor实现未读；不推自然生成概率或所有依赖齐全。',
'原实体cat/witch既有PersistenceRequired和旧绝对Pos，不是新人物制作/黑婆AI；不能照搬敌对原实体或据此生成中文NPC/任务ID。',
'水锅level2与craft陈设符合湿作角题材，仍无热作/熬药过程证据；没有独立药料存取/多区组织，职业与家具替换不足以新整体家族通过，作者HOLD0不提新待审。',
'完整206/209与192F03七观察/全部限制保存比较；192原NPC01相关性HOLD0不追授NPC06，206HOLD0不升级，所有既有适用有效参考保留不清零。',
'F02dark_forest是本批F01 role+occupancy相同，未重新渲染/原语义研究，不是历史已读。F03sky alchemist命中192，F04witch_tower命中dungeons001，旧图/NBT不重开；四候选/六木种不凑参考。',
'门口headroom省略/地面到高平台路线未证；薄窗栏/楼阶碰撞、实体行为、延柱生存更新、火雨/性能均未验。类色全格图不是贴图/模型/实机验收。',
'203first209与157first206本211各0；NPC01/05/06累计未知，COD4153/847不变，未达1000不制作或删任务。无Java/游戏/网络/声音亮度唤醒/用户实例原档/专业资产/共享Jar/Git/主清单写入，不宣全部完成或工时。'],actual_reading=dict(palette=17,BE=0,entities=2,layers=8,RLE_rows=72,positions=504,PNG_actual_viewed=6,full_metadata=2,full_context_JSON=4),complete_original_spatial_study=True,status='WHOLE_SOURCE_SINGLE_CELL_FAMILY_AND_NPC06_WORKFLOW_HOLD_ZERO',new_reference_proposal=0,formal_credit_added=0))
for name in ['latest-independent-admissions.json','carried-forward-pending.json']:
 d=read(PRE/name);d['previous210_binding']=bind(PRE/name);d['203first209_current211_increment']=0;d['157first206_current211_increment']=0
 if name.startswith('latest'):d['current_batch_formal_credit_added']=0
 else:d['current_batch_new_pending']=0;d['current_batch_pending_cases']=[];d['211F01_mangrove_witchhut_HOLD0']=dict(increment=0,new_pending=0)
 put(name,d)
protected=[]
for f in read(PRE/'protected-inputs-current.json')['files']:
 oldbind=f['current210'];now=bind(oldbind['path']);protected.append(dict(last210_checkpoint=oldbind,current211=now,unchanged=oldbind==now))
put('protected-inputs-current.json',dict(files=protected,baseline='saved210 checkpoint',this_chat_product_writes=False,concurrent_changes_not_reverted=True))
put('verification.json',dict(status='PASS',check_count=len(checks),checks=checks,machine_checks_not_reference_credit=True,commentary_classification_corrected='Initially said all3 excluded sources were historical; actual F02 exact role+occupancy matches within current batch only, F03/F04 historical. Corrected before sealing; no semantic reading or credit claimed for excluded sources.'))
s=dict(batch=211,status='COMPLETE_MANGROVE_WITCHHUT_FAMILY_WORKFLOW_HOLD_ZERO',formal_credit_added=0,accepted203_first209_current_increment=0,accepted157_first206_current_increment=0,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,NPC06_total=None,new_complete_whole_studies=1,new_qualifying_proposals=0,active_pending=[],palette=17,BE=0,entities=2,layers=8,RLE_rows=72,positions=504,PNG_actual_viewed=6,full_metadata=2,full_context_JSON=4,java_run=False,game_run=False,network_used=False,production=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,protected_input_concurrent_changes=sum(not a['unchanged'] for a in protected),next='Continue whole relevant source beyond studied small-hut/material-swap families; preserve valid previous evidence and purposes. No old-source replay or production.')
put('session.json',s);put('active-checkpoint.json',s);files=[bind(f) for f in sorted(P.iterdir()) if f.is_file() and f.name!='RECEIPT.json'];put('RECEIPT.json',dict(**s,files=files,verification_checks=len(checks)));print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),files=len(files),checks=len(checks)),ensure_ascii=False))
