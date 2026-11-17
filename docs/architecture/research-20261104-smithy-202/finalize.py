import json,hashlib,zipfile
from pathlib import Path
P=Path(__file__).resolve().parent;PRE=P.parent/'research-20261104-smithy-201'
assert not(P/'RECEIPT.json').exists()
def read(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
checks=[]
def check(k,v):
 checks.append(dict(check=k,passed=bool(v)));assert v,k
raw=read(P/'raw-source-audit.json')['candidates'][0];d=raw['nbt_decoded_original'];pal=d['palette'];g={tuple(b['pos']):b['state'] for b in d['blocks']};be=[b for b in d['blocks'] if 'nbt'in b]
check('size DV',d['size']==[15,15,9] and d['DataVersion']==3105)
check('counts',len(pal)==71 and len(be)==15 and len(g)==2025 and raw['air']==1696 and raw['nonair']==329 and d['entities']==[])
check('original air20',pal[20]['Name']=='minecraft:air')
for l in read(P/'original-index-rle.json')['layers']:
 check('nine rows y'+str(l['y']),len(l['rows_z0_8'])==9)
 for z,row in enumerate(l['rows_z0_8']):
  vals=[]
  for s in row.split():
   t=s.split('x');vals += [int(t[0])]*(int(t[1]) if len(t)>1 else 1)
  check('full original row y%d z%d'%(l['y'],z),vals==[g[(x,l['y'],z)] for x in range(15)])
check('bed paired west',g[(2,2,3)]==66 and g[(3,2,3)]==68)
check('bed bases explicit air',g[(2,1,3)]==20 and g[(3,1,3)]==20)
check('furnaces actual loom support',g[(6,0,3)]==8 and g[(7,0,3)]==8)
check('top three fullair layers',all(v==20 for (x,y,z),v in g.items() if y>=12))
check('fixed archive',bind(raw['source_archive'])['sha256']==raw['source_archive_sha256'])
with zipfile.ZipFile(raw['source_archive']) as z:check('original member SHA',hashlib.sha256(z.read(raw['member'])).hexdigest()==raw['nbt_sha256'])
context=read(P/'source-context.json');check('no invented JSON',context['candidates'][0]['contexts']==[] and context['candidates'][0]['missing']==['data/minecraft/worldgen/template_pool/village/jungle/jungle_village_2.json'])
check('literal search0',read(P/'source-pool-literal-search.json')['JSON_mentions']==[])
put('manual-review.json',dict(batch=202,case='F06',source={k:v for k,v in raw.items() if k not in ['nbt_decoded_original','material_counts']},seven_dimensions={
'layout':'南侧8,0,7/8接头向中央工作带，北6/7,1,3高炉/烟炉、东10,y1/2,3两桶，西2/3,2,3床与2,2,4桶构较高端部生活角。全件为窄长两侧围护与收拢高屋盖的一体模板；设备与床不能拆为多屋。西生活角下保存空气，完整性保留HOLD。',
'proportion':'15×15×9/DV3105，2025全保存=329非air+1696显式air，零省略；71palette/15BE/entities[]。15层135RLE/2025格实际读；y12..14全air、y11只有竹顶，15高不等楼层。床y2与核心设备y1仅高差一格，不叫独立二层工作生活。',
'facade':'两侧z2/6混合绿陶土/绿混凝土粉/木框围护，活板与开栅栏装饰；没有标准上下半扇门。西床边三空白牌、east-facing床侧一牌是原空白数据，不编中文NPC标识。图像是全格材质类别近似，灰色不等石墙。',
'roof':'屋面从两侧z2/6高位材料朝z4收拢，中央y8/9梁/半砖、y10孤立半砖，原存在海绵/湿海绵/西瓜/玻化陶土/泥等混合保存状态；没有来源处理器证据时保留原名，不臆造最终茅草/石瓦。局部脊间空气和竹杆不构成可达阁楼，也未证明雨密。',
'materials':'高炉6,1,3south与烟炉7,1,3south均litfalse/timers0/Items[]；营火6,1,5east和4,2,5south均unlit/空，三桶空Items；绿色床foot3,2,3/head2,2,3west完整一对。底部looms作模板实体承托/造型，不按每个织布机计岗位或建筑。无砧、锻造台或切石机，不能叫完整锻造生产线。',
'circulation':'南8,0,7 south_up pool empty/finalair，邻8,0,8 north_up pool minecraft:village/jungle/jungle_village_2/finalair；经x8中部过道至炉前6/7,1,4（stone_button/air，不将按钮格叫完整air），东西通往两桶和西生活角。无梯；西5,0,4 east stair/4,0,4 bottom slab表达高差，但床下显式air，实际净空/邻居更新/上床/碰撞/NPC均未运行。',
'ground_support':'炉下6/7,0,3为north loom实际实体；西床两半下2/3,1,3均显式air，再下2,0,3竹、3,0,3蕨，不隐去该支撑缺口。模板y0以下世界地面未知，无water不称浮船/已自然落地；接头原minecraft池在当前Jar缺失且全Jar JSON字面搜0，未更改namespace或补造依赖。'},limits=[
'当前原源71palette/15BE/entities[]、15层135行2025格及8PNG均实际完整读/看；三metadata全文实际读；0完整上下文JSON，缺失选池不算已读。',
'原源整体静态研究完成不等生成后完整可用；床下支撑、接池闭环与地形仍未解决，作者HOLD0、新合格提议0，未冒充Main独立验收。',
'两床BE仅一对床，不算两床位；两个相邻jigsaw不是两入口或两建筑。炉未点燃、桶空，无原entities，不能推断村民、交易或产出。',
'选择器未找到literal的范围仅当前固定Jar全部JSON，未跨其它运行数据包搜索，不证明世界绝无该池。root/biome/structureset/processor实现未读，未修改作者资产。',
'全部材料状态原样保留，粉末/海绵/瓜和空白牌未转换；DV3105到当前运行版本的状态升级、重力、邻居更新与支撑未运行，不能把分类图视为最终实机。',
'完整195的七维/10限制本轮实际读以比较：195前炉后储物上床长平台也有接池/梯和外地基缺口。当前为狭长工作带西床角，没有独立可证的上层闭环；不因尺寸、材质、不同NBT就合格，也不据作者195HOLD当旧接受。旧PNG/NBT均不重开。',
'1030新机器线索=1200:2230，三段240加310；与1980:480和200480:1200相接。冻结2230表的机器检查范围至此覆盖，不等2230完整建筑或所有本地来源穷尽。设备共存、文件数/指纹不提供语义信用。',
'七个指纹候选只有F06本轮整项研究；F01/02/03/04/05/07未读完整palette/BE/原格/图/上下文，保持0提议0信用。宅邸房间/帐篷/职业组件不能直接算整栋，machine列表未逐个人工确认。',
'复用153指纹cache及153..201实际存在delta，旧原NBT未重开。没有exact或alias只是来源新鲜度线索，不是语义去重或1000门槛满足。',
'197first199仅一次+1、本批后续0；190first193后续0；157W01唯一活跃whole待审、182HOLD0和064未追认、174first177/186first187历史接受不变。COD4153/847、NPC05+0、NPC01累计未知。',
'本专岗不编辑主清单，不删除游戏内容；无Java/游戏/网络/制作/资产/Jar/Git/用户实例/声音亮度唤醒焦点改动，不声称全任务完成或主动工时。'],status='HOLD_UNRESOLVED_BED_SUPPORT_POOL_GROUND_ZERO',complete_original_spatial_study=True,new_reference_proposal=0,formal_credit_added=0,actual_reading=dict(palette=71,BE=15,entities=0,layers=15,RLE_rows=135,positions=2025,PNG_actual_viewed=8,full_metadata=3,full_context_JSON=0)))
old195=read(P.parent/'research-20261104-smithy-195/manual-review.json');put('saved-complete-comparison.json',dict(binding195=bind(P.parent/'research-20261104-smithy-195/manual-review.json'),full_saved195=old195,old_raw_or_PNG_reopened=False,comparison='Current west raised bed corner/central heat/east storage has no proven upper living route and unresolved explicit air under both bed halves. Do not infer completeness/novelty from different source. AuthorHOLD0.',credit=0))
for name in ['latest-independent-admissions.json','carried-forward-pending.json']:
 v=read(PRE/name)
 if name.startswith('latest'):
  v['previous_binding']=bind(PRE/name);v['current_batch_formal_credit_added']=0;v['all_prior_acceptances_carry_only_no_current_increment_202']=dict(increment=0,old_raw_or_PNG_reopened=False)
 else:
  v['previous_batch_receipt']=bind(PRE/'RECEIPT.json');v['current_batch_new_pending']=0;v['current_batch_pending_cases']=[];v['202_F06_full_study_HOLD_not_qualifying_proposal']=dict(new_pending=0,credit=0,reason='explicit air under both bed halves; missing native pool; outside ground unresolved');v['197first199_later_carry_increment_202']=0;v['190first193_later_carry_increment_202']=0
 put(name,v)
a=read(P/'latest-independent-admissions.json');c=read(P/'carried-forward-pending.json');orig=read('docs/cod4/audit-20261022/coordinator-smithy197-F04-ring-work-tower-whole-review-20261110.json')
check('197 exact full object in both carries',a['newly_notified_NPC01_admission_197_F04']['full_Main_judgment_preserved_exact']==orig and c['197F04_NPC01_resolved_accept1_first199']['full_Main_judgment_preserved_exact']==orig)
check('first199/later0 retained',a['newly_notified_NPC01_admission_197_F04']['first_author_carry_batch']==199 and a['newly_notified_NPC01_admission_197_F04']['all_later_carries_increment']==0)
check('157 sole active whole pending',len(c['carried_unresolved_whole_reference_proposals'])==1 and c['carried_unresolved_whole_reference_proposals'][0]['batch']==157)
protected=[]
for f in read(PRE/'protected-inputs-current.json')['files']:
 old=f['current201'];now=bind(old['path']);protected.append(dict(last201_checkpoint=old,current202=now,unchanged=old==now))
put('protected-inputs-current.json',dict(files=protected,baseline='201 checkpoint, not a new202 start snapshot',this_chat_product_writes=False,concurrent_changes_not_reverted=True))
check('eight protected inputs unchanged',len(protected)==8 and all(f['unchanged'] for f in protected))
scans=[read(P/n)['scanned'] for n in ['new-machine-work-candidates.json','new-machine-work-candidates-pass2.json','new-machine-work-candidates-pass3.json','new-machine-work-candidates-pass4.json']];pairs=[(x['source_archive'],x['member']) for rows in scans for x in rows]
check('1030 unique machine candidates',list(map(len,scans))==[240,240,240,310] and len(set(pairs))==1030)
for n in ['F06-whole.png','F06-cutaway.png','F06-y0.png','F06-y3.png','F06-y6.png','F06-y9.png','F06-y12.png','F06-vertical.png']:check(n+' exists actual seen',(P/n).stat().st_size>0)
put('verification.json',dict(status='PASS',check_count=len(checks),checks=checks,machine_checks_not_semantic_credit=True))
s=dict(batch=202,status='SOURCE_WHOLE_STUDY_HOLD_ZERO',formal_credit_added=0,new_qualifying_reference_proposals=0,actual_new_original_spatial_studies=1,current_PNG=8,PNG_actual_viewed=8,palette=71,BE=15,layers=15,RLE_rows=135,positions=2025,full_metadata=3,full_context_JSON=0,new_machine_candidates=1030,machine_new_semantic_credit=0,accepted197_first199_later_increment=0,accepted190_first193_later_increment=0,COD4_accepted_baseline=153,COD4_gap=847,COD4_increment=0,NPC05_increment=0,NPC01_cumulative_not_inferred=None,java_run=False,game_run=False,network_used=False,product_files_written=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,next='Continue previously unread complete related building. Frozen2230 machine list now scanned, but no full-study credit from machine coverage. F01 stone igloo/F02 work tower remain unstudied candidates, not proposals.')
put('session.json',s);put('active-checkpoint.json',s)
files=[bind(p) for p in sorted(P.iterdir()) if p.is_file() and p.name!='RECEIPT.json'];put('RECEIPT.json',dict(**s,files=files,verification_checks=len(checks)))
print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),files=len(files),checks=len(checks)),ensure_ascii=False))
