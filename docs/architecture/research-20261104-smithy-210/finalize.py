import json,hashlib,zipfile
from pathlib import Path
P=Path(__file__).resolve().parent;PRE=P.parent/'research-20261104-smithy-209';assert not(P/'RECEIPT.json').exists()
def read(p):return json.loads(Path(p).read_text())
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
checks=[]
def check(k,v):
 checks.append(dict(check=k,passed=bool(v)));assert v,k
r=read(P/'raw-source-audit.json')['candidates'][0];n=r['nbt_decoded_original'];pal=n['palette'];g={tuple(b['pos']):b for b in n['blocks']}
check('size DV',n['size']==[15,17,14] and n['DataVersion']==3953)
check('96pal32BE entitiesempty',len(pal)==96 and sum('nbt'in b for b in n['blocks'])==32 and n['entities']==[])
check('counts',len(g)==1415 and r['air']==352 and r['nonair']==1063 and 3570-len(g)==2155)
for l in read(P/'original-index-rle.json')['layers']:
 check('14rows y'+str(l['y']),len(l['rows_z0_13'])==14)
 for z,row in enumerate(l['rows_z0_13']):
  vals=[]
  for s in row.split():
   t=s.split('x');vals += [int(t[0])]*(int(t[1]) if len(t)>1 else 1)
  check('RLE y%d z%d'%(l['y'],z),vals==[g[(x,l['y'],z)]['state'] if (x,l['y'],z)in g else -1 for x in range(15)])
for row in read(P/'critical-original-states.json'):
 c=tuple(row['pos']);expected=pal[g[c]['state']] if c in g else 'OMITTED_NOT_AIR';check('critical '+str(c),expected==row['state'])
ls=read(P/'all-ladder-and-backing.json');check('nine ladder split3plus6',[(a['pos'][1],a['pos'][2]) for a in ls]==[(y,3 if y<=3 else 4) for y in range(1,10)])
for a in ls:
 c=tuple(a['pos']);b=tuple(a['back_pos']);check('ladder/back '+str(c),a['state']==pal[g[c]['state']] and a['back_state']==pal[g[b]['state']])
check('fixed archive',bind(r['source_archive'])['sha256']==r['source_archive_sha256'])
with zipfile.ZipFile(r['source_archive']) as z:
 check('original NBT hash',hashlib.sha256(z.read(r['member'])).hexdigest()==r['nbt_sha256'])
 ctx=read(P/'source-context.json');oldctx=read(PRE/'source-context.json')
 check('full metadata previous exact',ctx['metadata']==oldctx['metadata']);check('2fullcontext exactreuse',ctx['candidates'][0]['contexts']==oldctx['candidates'][0]['contexts'])
 for a in ctx['metadata']:
  b=z.read(a['member']);check('metadata '+a['member'],b.decode()==a['original_text'] and hashlib.sha256(b).hexdigest()==a['sha256'])
 for a in ctx['candidates'][0]['contexts']:
  b=z.read(a['member']);check('context '+a['member'],json.loads(b)==a['json'] and hashlib.sha256(b).hexdigest()==a['sha256'])
check('9PNG actually viewed',len(list(P.glob('*.png')))==9)
put('saved-complete-family-comparison.json',dict(comparisons=[dict(binding=bind(P.parent/f'research-20261104-smithy-{batch}/manual-review.json'),full_judgment=read(P.parent/f'research-20261104-smithy-{batch}/manual-review.json')) for batch in [208,209]],current_comparison='208为同floor3双卧房加弯折外廊，209是低单床箱室；210下部L形长室/双床、southwest外折阶上独立双床室，另east分段错列梯接屋檐，是整体不同组合。但本源仍无熬药区/缺柱池/当前选屋与root未闭合，不因多层/床数/外梯就提NPC06合格参考。',old_NBT_PNG_reopened=False,current_credit=0))
put('manual-review.json',dict(batch=210,case='F01',source={k:v for k,v in r.items() if k not in ['nbt_decoded_original','material_counts']},seven_dimensions={
'layout':'下部L形长室：north横厅与east/south双床箱室同floor3/use4，通过室内空带相接；west低门及south门各接外廊。southwest绕阶另上floor8/use9独立双床高屋、west入户门；east墙有另一路分段梯，不等内梯串两层。整组一个原源，不拆四床/三门/外梯/阁屋计数。',
'proportion':'15×17×14 DV3953；3570声明=1415保存(1063非air352air)+2155省略。96palette/32BE/entities[]，17层238RLE3570位/9PNG全读看。实际use4与use9两层，较高y13..15屋盖、y16全省略；不把17高当17层。',
'facade':'oakplank/stripped oak与原oak log骨架，窗pane/藤/lantern、薄门活板/木栅饰面。west低门3,4/5,3west/left/closed、south低门11,4/5,11north/right/closed、上门7,9/10,8west/right/closed三扇实际门，门朝向不等外立面命名。灰类色梯/半砖不叫灰石楼。',
'roof':'north横厅y8梁与y9长木檐盖，在y10收坡，east/south高卧房y12梁、y13主盖、y14偏脊阶/半砖与y15薄边，y16全省略；上下不同木盖一组。高箱8,7,10与9,7,2只是薄活板附近陈设，不证明独立第三储层；无完整防雨/通烟验收。',
'materials':'低床heads8,4,z7/9与feet9,4,z7/9朝west；上床feet11,9,z8/10与heads12,9,z8/10朝east。低床下TOP圆石slab，上床下TOPspruce slab；4原loot箱及seed完整保留。32BE=8床/4箱/20接头，不当32建筑。没有cauldron/brewingstand/furnace或熬药瓶罐区，不能按NPC06职业完成。',
'circulation':'外折阶9,4,12west底oak→8,5,12west底oak→7,6,12west底oak转6,7,11north底oak→6,8,10north底oak接6,8,9TOP/south阶与6,8,8TOPoakslab，上6,9,8air邻上门7,9,8。east九梯非同一直线：x14,z3,y1..3三段，继x14,z4,y4..9六段，低两背13,y1/2,z3为open/bottom/west薄活板，非实体木柱；14,y4..8,z3省略、14,9,3是TOPspruce slab，不能写九段连续安全同轴梯。所有转角/梯侧移/头顶/门操作与NPC路径未运行。',
'ground_support':'低楼floor3多TOP圆石/苔圆石slab，柱foot20接头中15向下oak_log池/finalstructure_void、3居民up接头finalslab、2入口finalair。原地面y0仅west粗土条、其余大片省略；缺下延oak_log模板池，不能补想落水底柱。下床8/9,3,7与上床11/12,8,8均有保存slab仅静态支承；自然水位/柱基/地形衔接未知。'},limits=[
'96palette/32BE/entities[]、17层238RLE3570位及9PNG实际读看。metadata3与居民池/loot2全文由208/209刚读范围精确对象和原包hash验证复用，不当新增案例。',
'缺trek:feature/block_column/oak_log原池，当前整屋选择池/root/biome/structure_set及居民三NBT未读；entities[]不证明游戏无居民，3居民socket不是黑婆或任务NPC。',
'静态上下两层/外绕阶有清楚分区，east梯实际错列且低两背薄开活板，不能叫已验连续直梯。选中的阶/落脚局部原状态不证明完整碰撞、开门、安全转角或NPC上下。',
'高处4箱含两薄活板承托陈设位，不推实用仓层或已领物。源loot原概率/seed保留，未付款、制作、原生拾取、奖励或任务回执。',
'与208/209完整七维与全部9限制原样比较保存，既有用途门槛不混用：当前没有熬药/药材处理区且柱池未解，NPC06用途HOLD0。仅多层床/楼梯差异不等新合格相关参考，不因造型不同凑数。',
'原DV3953不自动视为当前1.20.1兼容；泛色全格图不是原材质/半块碰撞/UV/灯光/性能验收；没有资源复制/替换。',
'203first209与157first206均只历史一次接受，本210各0；完整Main/作者对象在连续ledger保留，NPC01/05/06累计未知，COD4153/847不变，未达适用1000不制作。',
'没有改变主清单、任务进度、共享Jar、角色模型、物品贴图或建筑资产；无Java/游戏/声音亮度唤醒/用户实例原档/Git/网络操作，不宣全部完成或工时。'],actual_reading=dict(palette=96,BE=32,entities=0,layers=17,RLE_rows=238,positions=3570,PNG_actual_viewed=9,full_metadata_verified_reused=3,full_context_JSON_verified_reused=2,all_ladder_backing_rows=9),complete_original_spatial_study=True,status='WHOLE_SOURCE_NPC06_APPLICABILITY_MISSING_PILLAR_POOL_HOLD_ZERO',new_reference_proposal=0,formal_credit_added=0))
for name in ['latest-independent-admissions.json','carried-forward-pending.json']:
 d=read(PRE/name);d['previous209_binding']=bind(PRE/name);d['203first209_current210_increment']=0;d['157first206_current210_increment']=0
 if name.startswith('latest'):d['current_batch_formal_credit_added']=0
 else:d['current_batch_new_pending']=0;d['current_batch_pending_cases']=[];d['210F01_NPC06_HOLD0']=dict(increment=0,new_pending=0)
 put(name,d)
protected=[]
for f in read(PRE/'protected-inputs-current.json')['files']:
 oldbind=f['current209'];now=bind(oldbind['path']);protected.append(dict(last209_checkpoint=oldbind,current210=now,unchanged=oldbind==now))
put('protected-inputs-current.json',dict(files=protected,baseline='saved209 checkpoint',this_chat_product_writes=False,concurrent_changes_not_reverted=True))
put('verification.json',dict(status='PASS',check_count=len(checks),checks=checks,machine_checks_not_reference_credit=True))
s=dict(batch=210,status='COMPLETE_SWAMP_MEDIUM2_HOLD_ZERO',formal_credit_added=0,accepted203_first209_current_increment=0,accepted157_first206_current_increment=0,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,NPC06_total=None,new_complete_whole_studies=1,new_qualifying_proposals=0,active_pending=[],palette=96,BE=32,entities=0,layers=17,RLE_rows=238,positions=3570,PNG_actual_viewed=9,full_metadata_verified_reused=3,full_context_JSON_verified_reused=2,java_run=False,game_run=False,network_used=False,production=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,protected_input_concurrent_changes=sum(not a['unchanged'] for a in protected),next='Target closer witch_hut/alchemist whole originals, screen all fixed history before render; missing pillars/selection/actual alchemy retain0. No old-source replay or production.')
put('session.json',s);put('active-checkpoint.json',s);files=[bind(f) for f in sorted(P.iterdir()) if f.is_file() and f.name!='RECEIPT.json'];put('RECEIPT.json',dict(**s,files=files,verification_checks=len(checks)));print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),files=len(files),checks=len(checks)),ensure_ascii=False))
