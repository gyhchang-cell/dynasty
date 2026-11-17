import json, hashlib, re, zipfile
from pathlib import Path
P=Path(__file__).resolve().parent
assert not (P/'RECEIPT.json').exists(), 'sealed batch is immutable'
PRE=P.parent/'research-20261104-smithy-199'
def read(p):return json.loads(Path(p).read_text())
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
checks=[]
def check(n,v):
 checks.append(dict(check=n,passed=bool(v)))
 assert v,n
raw=read(P/'raw-source-audit.json')['candidates'][0];nbt=raw['nbt_decoded_original'];pal=nbt['palette'];blocks=nbt['blocks']
check('original size and DV',nbt['size']==[8,8,9] and nbt['DataVersion']==3465)
check('counts',len(pal)==37 and len(blocks)==343 and raw['air']==71 and raw['nonair']==272 and nbt['entities']==[])
check('air13',pal[13]['Name']=='minecraft:air')
grid={tuple(b['pos']):b['state'] for b in blocks};rle=read(P/'original-index-rle.json')
check('eight actual layers',len(rle['layers'])==8)
for layer in rle['layers']:
 check('nine rows y'+str(layer['y']),len(layer['rows_z0_8'])==9)
 for z,row in enumerate(layer['rows_z0_8']):
  vals=[]
  for s in row.split():
   t=s.split('x');vals += [int(t[0])]*(int(t[1]) if len(t)>1 else 1)
  check('original RLE exact y%d z%d'%(layer['y'],z),len(vals)==8 and vals==[grid.get((x,layer['y'],z),-1) for x in range(8)])
be=[b for b in blocks if 'nbt' in b];check('one fullBE',len(be)==1)
with zipfile.ZipFile(raw['source_archive']) as z:check('selected source member hash',hashlib.sha256(z.read(raw['member'])).hexdigest()==raw['nbt_sha256'])
check('fixed archive binding',bind(raw['source_archive'])['sha256']==raw['source_archive_sha256'])
ctx=read(P/'source-context.json')['candidates'][0]['contexts']
seven={
'layout':'西门2,2/3,3进入同一工作室，西侧窄围栏前廊仅附属于该入口；北灰/紫陶土堆与南石切机共用中央空隙。无独立生活翼或上下层工序。对比198完整桦木单室与085完整共同加工室，保持同一空间组织，作者family0。',
'proportion':'8×8×9/DV3465；576声明格=343保存(272非air+71显式air)+233省略。37palette/1BE/entities[]，8层72行576格已逐层研究。较198增加底层标记与高度，不据高度另计房屋。',
'facade':'黑陶土围护、绯红木框/围栏/单扇东向left闭门及橙色玻璃窗格。红石火把在西0,3,4和0,3,7，薄件分类整格图并非真实碰撞或材质贴图。',
'roof':'y4外檐绯红阶梯，y5梁和中央菌光体4,5,4/活板通风装饰，4,4,4闭合top活板；y6收口与孤立黑石墙、y7绯红木脊。无梯/第二层地板，空腔和装饰不是可用阁楼。',
'materials':'原源有黑石、黑/灰/紫陶土及绯红木，4,2,6north石切机；无实际clay、炉、砧、床、箱、水、熔岩。六个power0红石粉与两个lit火把不证明自动化或加工产出。无付款/获取回执。',
'circulation':'唯一西门完整上下半，经窄前廊进入共同室。石切机北前4,2,5是redstone_wire薄件，不是整格air，不能据分类图断NPC寻路通过。唯一0,1,3西向jigsaw指crimson/streets，最终黑石东向底阶；围栏/门/阶梯净空未经运行。',
'ground_support':'工作y2下y1黑石板；y0黑色玻璃42与橙色玻璃3是原模板标记，正常randomizer完整读到DOWN pillar分别替换黑石/绯红木板，不能把原图玻璃当生成后透明基座，也不能把读到配置当实机落地。y-1地形、柱生成终止与道路落点仍未验。'}
limits=[
'当前7PNG均逐张实际查看；此前多图文本返回被截断，已排除该次阅读信用并逐项补看。分类整格图只校验结构，不是游戏截图/真实贴图/碰撞。',
'全部37palette、1BE、entities[]及8层72原索引RLE/576格已实际读，程序逐格与保存原解码复核；文件数和散列不提供语义信用。',
'仅完整读取normal randomizer、path_randomizer、path_pillar_randomizer三JSON；normal与zombie houses只实际读目标masons_house_1条目和fallback。均weight2/legacy rigid，同一源分别randomizer与zombify；不算两栋。',
'正常randomizer随机黑石与绯红木替换、DOWN原基质和标记柱配置已读；道路处理遇熔岩与地面随机、五格下柱及柱材随机已读。处理器实现、柱实际延伸/碰撞/重力/原生生成未执行。',
'完整zombie houses、normal houses、streets、zombify仅保存未全文研究；root/biome/terminators/道路NBT和实现均未读。missing[]只对采集子集，不代表依赖闭环。META-INF/mods.toml与pack.mcmeta两篇全文已读。',
'完整198七维/11限制和保存085完整七维再用于比较；旧NBT/图片未重开。198曾待197的历史描述只保留其时点，不覆盖199已接受197。',
'新源原始NBT不同，但底座/绯红材质/红石/通风装饰不引入独立工作翼、公共穿行或上下生活工序；作者family0、新合格提议0，未声称Main独立研究当前案例。',
'机器三段各240、共720是198冻结尺寸表480:1200候选线索，与1980:480分离；未穷尽2230。F02 jungle仅指纹与199竹屋重复，F03 mountain/F04 rustic只指纹待研究，均无当前完整原格/图阅读信用。',
'197原Main整项接受仅first199一次+1，本200及后续0，完整对象照旧；新收到Main first199完整性审查不新增语义信用、不算新197/199图或NBT阅读。',
'157W01仍唯一活跃whole提议；182HOLD0、064未追认、174first177/186first187/190first193后续0原样。NPC01累计未知，COD4153/847与NPC05+0不变。',
'无Java/游戏/网络/制作/清单删项/共享Jar/专业资产/Git/亮度声音唤醒焦点/用户实例改动。未满适用1000不提前制作，不称全任务完成，不计墙钟或并行等待为主动工时。']
put('manual-review.json',dict(cases=[dict(id='F01',source={k:v for k,v in raw.items() if k not in ['nbt_decoded_original','material_counts']},seven_dimensions=seven,limits=limits,complete_original_spatial_study=True,status='AUTHOR_EXISTING_SINGLE_SHARED_WORKROOM_FAMILY_ZERO',new_reference_proposal_maximum=0,formal_credit_added=0)]))
comp=read(P.parent/'research-20261104-smithy-198/saved-complete-family-comparison.json')
put('saved-complete-family-comparison.json',dict(binding198=bind(P.parent/'research-20261104-smithy-198/manual-review.json'),full198_case=read(P.parent/'research-20261104-smithy-198/manual-review.json')['cases'][0],complete085=comp['085_complete_saved_case_actually_read'],current_comparison=seven['layout'],old_NBT_or_PNG_reopened=False,formal_credit_added=0))
main=Path('docs/cod4/audit-20261022/coordinator-smithy197-first199-carry-integrity-review-20261110.json');mb=bind(main)
check('Main first199 integrity binding',mb['sha256']=='c46a1654e5df3aab0a4c221e63d8f2ecbe1b41ca8f76ff9928de8675ebb7682b' and mb['bytes']==3624)
integrity=dict(binding=mb,full_Main_judgment_preserved_exact=read(main),current_semantic_increment=0,current_old_NBT_or_PNG_reading=0)
orig=read('docs/cod4/audit-20261022/coordinator-smithy197-F04-ring-work-tower-whole-review-20261110.json')
a=read(PRE/'latest-independent-admissions.json');carry=read(PRE/'carried-forward-pending.json');first=read(PRE/'first-carry-197-independent-admission.json')
for label,ob in [('first',first),('admissions',a['newly_notified_NPC01_admission_197_F04']),('pending',carry['197F04_NPC01_resolved_accept1_first199'])]:
 check(label+' full197 exact',ob['full_Main_judgment_preserved_exact']==orig)
 check(label+' first199 later0',ob['first_author_carry_batch']==199 and ob['increment_once']==1 and ob['all_later_carries_increment']==0)
a['previous_binding']=bind(PRE/'latest-independent-admissions.json');a['current_batch_formal_credit_added']=0;a['197first199_Main_carry_integrity_only']=integrity;a['all_prior_acceptances_carry_only_no_current_increment_200']=dict(increment=0,old_raw_or_PNG_reopened=False)
put('latest-independent-admissions.json',a)
carry['previous_batch_receipt']=bind(PRE/'RECEIPT.json');carry['current_batch_new_pending']=0;carry['current_batch_pending_cases']=[]
carry['200_complete_crimson_workroom_author_family0']=dict(new_proposal=0,author_family_credit=0,Main_independent_review=False)
carry['197first199_later_carry_increment_200']=0;carry['190first193_later_carry_increment_200']=0;carry['197first199_Main_carry_integrity_only']=integrity
check('157 sole active whole pending',len(carry['carried_unresolved_whole_reference_proposals'])==1 and carry['carried_unresolved_whole_reference_proposals'][0]['batch']==157)
put('carried-forward-pending.json',carry)
cache=read(P/'history-cache-reuse.json');known={x['path'] for x in cache['delta_bindings']}
for i in range(195,200):
 p=P.parent/('research-20261104-smithy-%03d'%i)/'pre-render-history-screen.json';b=bind(p)
 if b['path'] not in known:cache['delta_bindings'].append(b)
put('history-cache-reuse.json',cache)
protected=[]
for f in read(PRE/'protected-inputs-current.json')['files']:
 old=f['current199'];now=bind(old['path']);protected.append(dict(last199_checkpoint=old,current200=now,unchanged=old==now))
put('protected-inputs-current.json',dict(files=protected,baseline='199 checkpoint, not a new200 start snapshot',this_chat_product_writes=False,concurrent_changes_not_reverted=True))
check('protected8 unchanged vs199',len(protected)==8 and all(x['unchanged'] for x in protected))
for n in ['F01-whole.png','F01-cutaway.png','F01-y0.png','F01-y1.png','F01-y3.png','F01-y6.png','F01-vertical.png']:check('view exists '+n,(P/n).stat().st_size>0)
scans=[read(P/n)['scanned'] for n in ['new-machine-work-candidates.json','new-machine-work-candidates-pass2.json','new-machine-work-candidates-pass3.json']]
pairs=[(x['source_archive'],x['member']) for rows in scans for x in rows]
check('three240 disjoint720',all(len(x)==240 for x in scans) and len(set(pairs))==720)
check('threefullprocessors selected',all('processors' in ctx[i]['json'] for i in [3,5,6]))
put('actual-reading-scope.json',dict(palette=37,BE=1,entities=[],layers=8,RLE_rows=72,declared_positions=576,actual_PNG_viewed=7,full_processor_members=[ctx[i]['member'] for i in [3,5,6]],pool_selected_entry_and_fallback_only=[ctx[i]['member'] for i in [0,1]],full_metadata=2,saved_only_not_fully_read=[ctx[i]['member'] for i in [0,1,2,4]],clipped_previous_output_excluded=True,repaired_with_individual_views_and_bounded_text=True,machine_candidates=720,machine_semantic_credit=0))
session=dict(batch=200,status='SEALED_RESEARCH_AUTHOR_FAMILY_ZERO',formal_credit_added=0,accepted197_first199_later_increment=0,accepted190_first193_later_increment=0,actual_new_original_semantic_source_studies=1,current_new_original_formal_credit=0,new_qualifying_reference_proposals=0,current_PNG=7,PNG_actual_viewed=7,old197_PNG_reopened=False,COD4_accepted_baseline=153,COD4_gap=847,COD4_increment=0,NPC05_increment=0,NPC01_cumulative_not_inferred=None,java_run=False,game_run=False,network_used=False,product_files_written=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,next='Continue one previously unread complete related local work building; F03/F04 remain fingerprint-only candidates, not credits. Never restart old accepted source reads.')
put('session.json',session);put('active-checkpoint.json',session)
put('verification.json',dict(status='PASS',check_count=len(checks),checks=checks,machine_checks_not_semantic_credit=True))
files=[bind(p) for p in sorted(P.iterdir()) if p.is_file() and p.name!='RECEIPT.json']
put('RECEIPT.json',dict(**session,files=files,verification_checks=len(checks)))
print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),files=len(files),checks=len(checks),protected8_unchanged=True),ensure_ascii=False))
