import json,hashlib,zipfile
from pathlib import Path
P=Path(__file__).resolve().parent; PRE=P.parent/'research-20261104-smithy-205'
assert not(P/'RECEIPT.json').exists()
def read(p):return json.loads(Path(p).read_text())
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
checks=[]
def check(k,v):
 checks.append(dict(check=k,passed=bool(v)));assert v,k
r=read(P/'raw-source-audit.json')['candidates'][0];n=r['nbt_decoded_original'];pal=n['palette'];g={tuple(b['pos']):b['state'] for b in n['blocks']}
check('size and DV',n['size']==[14,17,11] and n['DataVersion']==3465)
check('source counts',len(pal)==105 and len(g)==2273 and r['nonair']==882 and r['air']==1391 and 2618-len(g)==345 and sum('nbt'in b for b in n['blocks'])==2 and len(n['entities'])==2)
check('entities are dropped carpets not NPC',all(e['nbt']['id']=='minecraft:item' and e['nbt']['Item']['id']=='minecraft:moss_carpet' for e in n['entities']))
check('air25',pal[25]['Name']=='minecraft:air')
for l in read(P/'original-index-rle.json')['layers']:
 check('11rows y'+str(l['y']),len(l['rows_z0_10'])==11)
 for z,row in enumerate(l['rows_z0_10']):
  vals=[]
  for s in row.split():
   t=s.split('x');vals += [int(t[0])]*(int(t[1]) if len(t)>1 else 1)
  check('raw row y%d z%d'%(l['y'],z),vals==[g.get((x,l['y'],z),-1) for x in range(14)])
for row in read(P/'critical-original-states.json'):
 c=tuple(row['pos']);check('critical '+str(c),row['state']==pal[g[c]])
check('doors on EAST boundary face west',[(g[(7,y,z)]) for y,z in [(3,2),(4,2),(3,3),(4,3)]]==[50,59,51,60])
check('two cauldrons and crafting',g[(11,6,5)]==72 and g[(11,6,7)]==72 and g[(7,6,3)]==11)
check('no ladder bed brewingstand furnace palette',not any(s['Name'] in ['minecraft:ladder','minecraft:brewing_stand','minecraft:furnace','minecraft:blast_furnace','minecraft:smoker'] or s['Name'].endswith('_bed') for s in pal))
check('fixed archive',bind(r['source_archive'])['sha256']==r['source_archive_sha256'])
with zipfile.ZipFile(r['source_archive']) as z:
 check('original member',hashlib.sha256(z.read(r['member'])).hexdigest()==r['nbt_sha256'])
 ctx=read(P/'source-context.json')
 for a in ctx['metadata']:
  b=z.read(a['member']);check('metadata '+a['member'],hashlib.sha256(b).hexdigest()==a['sha256'] and b.decode()==a['original_text'])
 for a in ctx['candidates'][0]['contexts']+read(P/'exact-root-context.json')['records']:
  b=z.read(a['member']);check('context '+a['member'],hashlib.sha256(b).hexdigest()==a['sha256'] and json.loads(b)==a['json'])
mainpath=Path('docs/cod4/audit-20261022/coordinator-architecture157-actual-author-ACK-final-acceptance-20261111.json');main=read(mainpath);ack=read(P/'157-preack-author-ack.json')
check('final acceptance exact expected SHA',bind(mainpath)['sha256']=='57892ea1b1f20b3b11c81b113a38da91aa2e2d78f637f11e923f3bd59d2374fa')
check('ACK unchanged approved bytes',bind(P/'157-preack-author-ack.json')==main['actual_author_ack'])
check('full response equality',main['actual_author_responses']=={k:ack[k] for k in ['Main_finding_responses','Main_limit_responses','actual_exact_slab_records','manifest_count_response']})
check('all8 plus8 preserved',len(ack['Main_finding_responses'])==8 and len(ack['Main_limit_responses'])==8)
check('full Main preACK preserved',ack['full_Main_judgment_preserved_exact']==read(main['Main_complete_independent_review']['path']))
check('full clarification preserved',ack['full_manifest_clarification_preserved_exact']==read(main['Main_manifest_count_clarification']['path']))
check('38 original manifest files',len(read(P.parent/'research-20261104-smithy-157/RECEIPT.json')['files'])==38)
check('two exact slab corrections',all(x['state']=={'Properties':{'waterlogged':'false','type':'bottom'},'Name':'minecraft:andesite_slab'} for x in ack['actual_exact_slab_records']))
check('accept one only no production',main['accepted_whole_reference_increment']==1 and main['production_authorized']==False and main['applicable1000_gate_met']==False)
carry=dict(Main_final_acceptance_binding=bind(mainpath),full_Main_final_acceptance_preserved_exact=main,complete_author_ACK_and_original_Main_judgments=ack,first_author_carry_batch=206,current_increment=1,all_later_increment=0,scope='COD3 NPC05 阿吉 废村磨坊，一座两段接合48×64×34建筑的空间研究',NPC05_total=None,COD4_increment=0,NPC01_increment=0,not_production_or_todo_completion=True)
put('157-final-acceptance-first-carry.json',carry)
old=read(PRE/'manual-review.json')
put('saved-complete-family-comparison.json',dict(binding205=bind(PRE/'manual-review.json'),full205=old,whole_comparison='205是7×15×7柱脚/高工作面/更高床层/短内梯；当前14×17×11为低层双门储物室、东侧抬高双锅工作区、大体积交接木屋盖，没有床和梯。共同高脚木构不能直接等同同一建筑；仍不能以题材不同自动计新信用，当前东工作区登临未解，保留HOLD0。205旧梯背/缺池限制原样，不重开旧PNG/NBT。',current_new_proposal=0,old_source_reopened=False))
put('manual-review.json',dict(batch=206,case='F01',source={k:v for k,v in r.items() if k not in ['nbt_decoded_original','material_counts']},seven_dimensions={
'layout':'完整单体低层双门储物室+东侧更高双锅/桶工作区，被宽大交接屋盖统合。低层主要floor2/use3，东工作面floor5/use6；上方y7..16主要檐、屋架和收坡，不算第三经营层。原源一件，不拆双锅/双桶/门/屋坡。',
'proportion':'14×17×11 DV3465；2618范围内2273保存=882非air+1391显式air，345省略非air。105palette/2BE/2掉落物实体。17层187RLE行2618坐标全读，9PNG全看。高屋盖与较低使用层的比例明显，不能拿17高度当可用楼层数。',
'facade':'spruce原木/去皮木立架、横木、east边双west朝向门，绿色/棕色玻璃小窗；苔、藤和活板/半砖檐丰富边缘。类色方块图不显示真实透明窗或薄门碰撞，不把灰色类色直接叫石结构。',
'roof':'y7以上多个x向横木坡面随z收拢，前部z向短屋脊与主屋盖交接；上端y16仍有x向长横木与z向短段，苔/藤不规则覆面。大片屋顶投影不等满层楼板或密闭防雨；薄阶/活板用全方格示意有形状误差。',
'materials':'低桶3,3,7与东桶10,6,4均up/closed/terralith:witch_hut loot，各原seed保留。craft7,6,3；空cauldron11,6,5与11,6,7，前者下11,5,5top spruce slab，后者下11,5,7top/south spruce stair；桶下10,5,4top/north stair。无brewingstand/furnace/bed/ladder，不称已熬药或熔炼。',
'circulation':'东边界x7,z2/3有成对门，朝west；z2右铰已开，z3左铰关闭，上下3/4配合。东外侧x8,y2,z2/3为west底阶接低地储物层。东工作面比低室高3格，x8,use6,z4..7有木栅阻隔、craft7,6,3旁6,6,3air而7,7,3是east底阶；全源无梯。未证从低室到双锅平台连续可行路线，不把散落阶/装饰称安全楼梯，也不判源永久不可用。',
'ground_support':'低室由去皮木梁/局部原木脚支持，保存y0的2,0,1/2,0,7/7,0,4/7,0,7/11,0,4/11,0,7等是y向柱，7/11,0,0为去皮全木；不是满铺实心基。y0还有东侧薄top活板平台。y-1地形/水位未读，不能推实际涉水、洪水高度、柱基稳定与水上安全入口。'},limits=[
'完整105palette、2BE、2实体及17层187RLE/2618位实际读；9PNG实际看，3metadata与6完整contextJSON实际读。初次合并大输出发生截断，截断本身不记新阅读；最终接受非responses部分已独立完整重读，responses与实际读过ACK全部精确相等。',
'两个实体为minecraft:item/moss_carpet，含源Age/绝对NBT.Pos/相对pos保留，不是女巫/黑婆或可靠原生存货。',
'pool有一个rigid原单体，empty processor/fallback，内name bad_luck原样；loot仅毒药/金苹果/虚弱喷溅/蝌蚪桶及杂项概率，不等玩家获得/付款/任务回执。',
'精确start_pool检索得两个root：surface root对orchid_swamp/ice_marsh/swamp，并piece范围cat1和witch1..2；underground路径root用empty none标签且spawn_overrides空。只读这两root和两直接tag，不宣结构集、overlay、运行数据包闭环，也不把空tag断定永不生成。',
'与205完整七维/全部9限制比较并保留其原文，旧PNG/NBT不重读。205非本NPC06累计信用，当前不得将NPC01/05旧接受挪给NPC06。',
'东工作层登临未证，门/阶/栅/半砖的真实净空、碰撞、邻居更新、女巫生成及NPC使用均未运行；当前完整研究HOLD0，不提新合格待审。',
'157W01在本206首次按Main最终收据接受NPC05空间参考+1；保留完整原作者/Main8发现8限制/真实ACK/两底半砖及38文件补正。原ACK的历史pending/formal0不回改，后续carry0，NPC05总数未知。',
'203F02仍待Main独立审；204/205HOLD0不升级。197first199、190first193及174/186旧接受后续0；182HOLD0/064不追认；COD4153/847不变，所有适用1000门槛均未声明达到。',
'无Java/游戏/网络/声音亮度唤醒/用户实例原档/生产专业资产/共享Jar/Git/主清单写入，无任务删除/工时达标/全部完成声明。'],status='WHOLE_STUDY_HOLD_UNRESOLVED_WORK_PLATFORM_ACCESS_ZERO',actual_reading=dict(palette=105,BE=2,entities=2,layers=17,RLE_rows=187,positions=2618,PNG_actual_viewed=9,full_metadata=3,full_context_JSON=6),complete_original_spatial_study=True,new_reference_proposal=0,formal_credit_added=0))
for filename in ['latest-independent-admissions.json','carried-forward-pending.json']:
 d=read(PRE/filename);d['previous_205_binding']=bind(PRE/filename);d['157W01_NPC05_resolved_accept1_first206']=carry
 if filename.startswith('latest'):
  d['current_batch_formal_credit_added']=1;d['current_batch_increment_scope']='157W01 NPC05 only; all old admissions increment0'
 else:
  previous=d['carried_unresolved_whole_reference_proposals'];check('previous pending157203',[(a['batch'],a['id']) for a in previous]==[(157,'W01'),(203,'F02')]);d['carried_unresolved_whole_reference_proposals']=[a for a in previous if a['batch']!=157];d['current_batch_new_pending']=0;d['current_batch_pending_cases']=[];d['206_F01_NPC06_HOLD0']=dict(increment=0,new_pending=0,unresolved='work platform access')
 put(filename,d)
protected=[]
for f in read(PRE/'protected-inputs-current.json')['files']:
 oldbind=f['current205'];now=bind(oldbind['path']);protected.append(dict(last205_checkpoint=oldbind,current206=now,unchanged=oldbind==now))
put('protected-inputs-current.json',dict(files=protected,baseline='saved205 checkpoint; concurrent changes never reverted',this_chat_product_writes=False))
check('9 PNG viewed',len(list(P.glob('*.png')))==9)
check('active pending203 only',[(a['batch'],a['id']) for a in read(P/'carried-forward-pending.json')['carried_unresolved_whole_reference_proposals']]==[(203,'F02')])
put('verification.json',dict(status='PASS',check_count=len(checks),checks=checks,machine_checks_not_reference_credit=True))
s=dict(batch=206,status='ONE_OLD_MILL_ACCEPTANCE_FIRST_CARRY_AND_NEW_SWAMP_WHOLE_HOLD',formal_credit_added=1,NPC05_increment=1,accepted_case='157W01',first_carry_batch=206,NPC05_cumulative=None,NPC06_increment=0,NPC06_cumulative=None,COD4_accepted=153,COD4_gap=847,COD4_increment=0,NPC01_increment=0,NPC01_cumulative=None,new_whole_studies=1,new_qualifying_proposals=0,active_pending=['203F02'],palette=105,BE=2,entities=2,RLE_rows=187,layers=17,positions=2618,PNG_actual_viewed=9,metadata_full=3,context_JSON_full=6,java_run=False,game_run=False,production=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,protected_input_concurrent_changes=sum(not a['unchanged'] for a in protected),next='Continue new whole relevant building sources with saved history dedup; no oldPNG/NBT replay, no production before applicable1000. 157accepted first206 all later0;203 stillpending;206NPC06HOLD0.')
put('session.json',s);put('active-checkpoint.json',s)
files=[bind(f) for f in sorted(P.iterdir()) if f.is_file() and f.name!='RECEIPT.json'];put('RECEIPT.json',dict(**s,files=files,verification_checks=len(checks)))
print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),files=len(files),checks=len(checks),protected_input_concurrent_changes=s['protected_input_concurrent_changes']),ensure_ascii=False))
