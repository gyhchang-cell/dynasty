import json,hashlib,zipfile
from pathlib import Path
P=Path(__file__).resolve().parent;PRE=P.parent/'research-20261104-smithy-204';assert not(P/'RECEIPT.json').exists()
def read(p):return json.loads(Path(p).read_text())
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
checks=[]
def check(k,v):
 checks.append(dict(check=k,passed=bool(v)));assert v,k
r=read(P/'raw-source-audit.json')['candidates'][0];n=r['nbt_decoded_original'];pal=n['palette'];g={tuple(b['pos']):b['state'] for b in n['blocks']}
check('sizeDV',n['size']==[7,15,7] and n['DataVersion']==3105)
check('counts',len(pal)==45 and sum('nbt'in b for b in n['blocks'])==7 and len(g)==735 and r['air']==522 and r['nonair']==213 and n['entities']==[])
check('air12',pal[12]['Name']=='minecraft:air')
for l in read(P/'original-index-rle.json')['layers']:
 check('seven rows y'+str(l['y']),len(l['rows_z0_6'])==7)
 for z,row in enumerate(l['rows_z0_6']):
  vals=[]
  for s in row.split():
   t=s.split('x');vals += [int(t[0])]*(int(t[1]) if len(t)>1 else 1)
  check('original row y%d z%d'%(l['y'],z),vals==[g[(x,l['y'],z)] for x in range(7)])
check('two unsupported ladder backs',g[(2,5,3)]==12 and g[(2,6,3)]==12 and g[(2,7,3)]==16)
check('raised furnace supports',g[(2,4,2)]==0 and g[(4,4,2)]==0)
check('bed support thin closed top trapdoors',g[(3,7,2)]==16 and g[(4,7,2)]==16)
check('whole last layer air',all(g[(x,14,z)]==12 for x in range(7) for z in range(7)))
check('fixed archive',bind(r['source_archive'])['sha256']==r['source_archive_sha256'])
with zipfile.ZipFile(r['source_archive']) as z:check('original member hash',hashlib.sha256(z.read(r['member'])).hexdigest()==r['nbt_sha256'])
check('literal pool search0',read(P/'source-pool-literal-search.json')['JSON_mentions']==[])
old195=read(P.parent/'research-20261104-smithy-195/manual-review.json');old203=read(P.parent/'research-20261104-smithy-203/manual-review.json')['cases'][1]
put('saved-complete-family-comparison.json',dict(binding195=bind(P.parent/'research-20261104-smithy-195/manual-review.json'),full195=old195,binding203=bind(P.parent/'research-20261104-smithy-203/manual-review.json'),full203F02=old203,current_comparison='Current stilt y4 work platform/y7 bed platform is not the rotated202/204 long room and does not have203 continuous supported ladder/back or explicit ground entrance. Compared with195 whole ladder/back/pool limitations, retain authorHOLD0.203 is only pending, not accepted or runtime proof.',old_NBT_PNG_reopened=False,credit=0))
put('manual-review.json',dict(batch=205,case='F04',source={k:v for k,v in r.items() if k not in ['nbt_decoded_original','material_counts']},seven_dimensions={
'layout':'紧凑高脚双高差整体：八个泥砖墙柱支起floor4/use5工作面，北高炉/烟炉、东工作台，内短梯通floor7/use8床/桶层，收拢屋盖。与202/204单层长室不同，源完整研究一件，不拆柱/工作层/卧层；梯背、地面入口及缺池未解故HOLD0。',
'proportion':'7×15×7/DV3105，735全保存=213非air+522显式air，无省略；45palette/7BE/entities[]。15层105原行735位全读；实际floor4和floor7，高到y13开门栅/末饰，y14全air，不把15高算15经营层。',
'facade':'stripped spruce及mangrove wood框、绿混凝土粉/陶土/苔/瓜/海绵保存状态，四侧木栅半砖/活板装饰，floor4四侧阶檐；没有标准入户门。无处理器证据不把保存的混合材料解释成最终茅草纹理。',
'roof':'y8外圈bottom slab裙檐、y9..11逐层混合方块收拢，y12中心east底阶/y13中心west open in_wall栅门顶饰。上床层有开放缝/悬灯，不证明密闭防雨屋盖。类色图灰不等石屋面。',
'materials':'高炉2,5,2east/烟炉4,5,2south均未燃空Items/CookBurnTotal0，craft4,5,4；上桶2,8,2south/Items[]，绿床3,8,2foot与4,8,2headeast一对。没有砧、水、熔岩，不称实际完整锻造工艺或材料供应链。',
'circulation':'south 3,0,5/6两个接头均finalair，后者字面minecraft:jungle_village_13选池；近地只有y1闭top活板环与y3顶半砖环，模板无从地面连续升至floor4的梯/阶链。内梯2,y5..7,4south，背2,y5/6,3为显式air，y7背才closed top trapdoor；顶2,8,4air。上床下closed top活板是薄件，不推完整净空/梯存留/邻居更新/床可达已验。',
'ground_support':'八泥砖墙柱自y0至y3：x2/4,z1/5及x1/5,z2/4，细柱不是满铺实心基。高炉下2,4,2和烟炉下4,4,2确stripped spruce log；床下3/4,7,2为closed top spruce trapdoor。y-1地面及柱脚自然衔接未知，没water不称水上浮屋；原minecraft选池在当前Jar缺失。'},limits=[
'45palette/7BE/entities[]、15层105RLE/735格、8PNG及3metadata全部实际读/看，0完整contextJSON；没有把不存在的池当已读或造namespace替换。',
'全Jar JSON字面jungle_village_13搜索0，只证明当前固定来源包未找到；其它运行数据包未查，root/biome/structureset/processor/被引外部池均未读。',
'地面到floor4连续登临未证、内梯两背air/上背薄活板，运行邻居更新/碰撞/操作路径未测；不声称原作者源永远不可用，只保留本研究完整性HOLD。',
'一对床完整方向配合不等卧层功能验收；床下top活板、周围薄栏/半砖净高和安全边界未运行。',
'完整195七维/10限制与203F02七维/13限制实际读于前批，当前通过绑定完整保存对象复用，旧PNG/NBT不重开。195虽长平台不同，但同有梯背/池/地形未解；203有连续实体梯背，不能把其支持情况移植到当前。',
'203F02仍仅作者新whole待审上限1/正式0，不冒充Main新独立验收；本205无新合格提议。',
'原45palette材料状态与DV3105保留，不自动量化/替换/补模型或贴图，不把屋面不同高度/颜色/设备数量作建筑信用。',
'197first199和190first193仅历史各一次接受后续0，174/186历史接受原样；157W01及203F02活跃待审保持；182HOLD0/064不追认。COD4153/847、NPC05+0、NPC01总数未知。',
'无Java/游戏/网络/声音亮度唤醒/实例/原档/专业资产/共享Jar/Git/主清单写入，无清单删除或主动工时/全部完成声明。'],complete_original_spatial_study=True,status='HOLD_UNRESOLVED_GROUND_ENTRANCE_LADDER_BACKING_POOL_ZERO',actual_reading=dict(palette=45,BE=7,entities=0,layers=15,RLE_rows=105,positions=735,PNG_actual_viewed=8,full_metadata=3,full_context_JSON=0),new_reference_proposal=0,formal_credit_added=0))
for name in ['latest-independent-admissions.json','carried-forward-pending.json']:
 d=read(PRE/name)
 if name.startswith('latest'):
  d['previous_binding']=bind(PRE/name);d['current_batch_formal_credit_added']=0;d['all_prior_acceptances_carry_only_no_current_increment_205']=dict(increment=0,old_raw_or_PNG_reopened=False)
 else:
  d['previous_batch_receipt']=bind(PRE/'RECEIPT.json');d['current_batch_new_pending']=0;d['current_batch_pending_cases']=[];d['205_F04_complete_source_HOLD_not_qualifying_proposal']=dict(credit=0,new_pending=0,reason='ladder backing / ground entrance / missing pool')
 put(name,d)
orig=read('docs/cod4/audit-20261022/coordinator-smithy197-F04-ring-work-tower-whole-review-20261110.json')
check('197 full unchanged',read(P/'latest-independent-admissions.json')['newly_notified_NPC01_admission_197_F04']['full_Main_judgment_preserved_exact']==orig and read(P/'carried-forward-pending.json')['197F04_NPC01_resolved_accept1_first199']['full_Main_judgment_preserved_exact']==orig)
check('157 plus203 pending unchanged',[(x['batch'],x['id']) for x in read(P/'carried-forward-pending.json')['carried_unresolved_whole_reference_proposals']]==[(157,'W01'),(203,'F02')])
protected=[]
for f in read(PRE/'protected-inputs-current.json')['files']:
 old=f['current204'];now=bind(old['path']);protected.append(dict(last204_checkpoint=old,current205=now,unchanged=old==now))
check('eight protected same',len(protected)==8 and all(f['unchanged'] for f in protected));put('protected-inputs-current.json',dict(files=protected,baseline='204 checkpoint not fresh205 start snapshot',this_chat_product_writes=False,concurrent_changes_not_reverted=True))
check('8 PNG exists all seen',len(list(P.glob('*.png')))==8)
put('verification.json',dict(status='PASS',check_count=len(checks),checks=checks,machine_checks_not_semantic_credit=True))
s=dict(batch=205,status='WHOLE_SOURCE_STUDY_HOLD_ZERO',formal_credit_added=0,new_qualifying_reference_proposals=0,actual_new_original_spatial_studies=1,palette=45,BE=7,layers=15,RLE_rows=105,positions=735,PNG_actual_viewed=8,full_metadata=3,full_context_JSON=0,accepted197_first199_later_increment=0,accepted190_first193_later_increment=0,COD4_accepted_baseline=153,COD4_gap=847,COD4_increment=0,NPC05_increment=0,NPC01_cumulative=None,java_run=False,game_run=False,network_used=False,product_files_written=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,next='Continue new complete related sources beyond studied footprint families; screen rotations/components first. No repetition of203 pending or old accepted raw views.')
put('session.json',s);put('active-checkpoint.json',s);files=[bind(f) for f in sorted(P.iterdir()) if f.is_file() and f.name!='RECEIPT.json'];put('RECEIPT.json',dict(**s,files=files,verification_checks=len(checks)));print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),files=len(files),checks=len(checks)),ensure_ascii=False))
