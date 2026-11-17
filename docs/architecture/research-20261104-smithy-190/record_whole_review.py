import json, hashlib, zipfile
from pathlib import Path
P=Path(__file__).resolve().parent; OLD=P.parent/'research-20261104-smithy-189'
def read(p):return json.loads(p.read_text())
def save(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=p.resolve();b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
assert not (P/'RECEIPT.json').exists()
a=read(P/'raw-source-audit.json')['candidates'][0];r=a['nbt_decoded_original'];s=read(P/'sources.json')['candidates'][0]
observations={
'layout':'北横体x1..17/z2..10与南纵翼x5..13/z15..23经x5..13/z11..14桥廊连接，非四面围合院。使用层y4；南翼室内石切工位(9,4,19)north，北横体中公共厅/壁炉，东侧独立炊事区，西侧楼梯；上层y11北横体分隔小房及东侧储物，南翼卧室。工作区位于南翼下、睡眠区位于其正上方，是垂直叠置的工居组织。',
'proportion':'19×20×25声明范围，4279保存位置=3033非空气+1246显式air，另5221省略不得当空气。工作楼板y3至上楼板y10跨度7格，北横屋脊y16、南纵屋脊y16；y17..19为烟囱端部，不等于额外楼层。桥廊使两翼在地面轮廓收窄，而非一整矩形厅或组件计数。',
'facade':'去皮云杉柱/深色梁分格，浅灰羊毛填墙，青色玻璃窗；工作厅下部石基、二层卧室凸出的窗墙、木檐和两翼交叉坡屋顶整体相接。原图是颜色分类的整格近似，不表现楼梯/栏杆/玻璃真实形状，不能作为原材质实机截图。',
'roof':'北屋脊沿x轴(0..18,16,6)，南屋脊沿z轴(9,16,7..24)，dark_prismarine坡面在y10..15逐层收分，spruce_log封边。南翼还在(3..15,15,17)横向木构；不是另一个独立建筑。烟囱在北侧x9/z1及南侧x8/z22，营火原状态lit=true只读，未运行。',
'materials':'stone436/stone_bricks322作连续台基及南作业厅底板，spruce_planks246、stripped_spruce_wood275、stripped_dark_oak_wood151与light_gray_wool215构成框架，dark_prismarine308屋面。石切机只有1个；北东(14,4,4)furnace、(14,4,5)crafting_table、(14,4,6)smoker不能冒称锻造流水线。8活塞为上朝未伸长原状态，未见红石驱动，不能说可运行锯木机器。',
'circulation':'西侧三格宽外阶x2..4从z17/y0→z16/y1→z15/y2→z14/y3北升，接桥廊楼面y3，再由(11,4,10)south门进入北公共厅；桥廊向南通入作业厅。北室西侧(4,4,6)south门分出楼梯间，x2自z8/y4逐级至z4/y8，利用北端平台折返至(4,9,5)和(4,10,6)，从(5,11,7)west门到上层主厅。上层(13,11,7)east门进东储物间，(10,11,10)south门接南翼睡眠区。上述为原始状态空间读法，NPC寻路/碰撞未运行。',
'terrain':'y0..3北横体与南翼下方均有实际保存石质台基，西梯最低踏面y0，桥廊脚下y1..3有横向石连接；不以省略格补地。南作业厅y3下存在y0..2地基，区别182作业层0且脚下缺失。只证明模板自身承托关系；未读取root structure/biome链，不保证世界实际埋深、树木清除或自然坡地贴合。'}
limits=[
'三组south床在x8..10/y11/z19foot,z20head完整；z18另3块north foot朝z17没有相配head，不称6床，不据此认定可睡6人。原资产仅研究未修复。',
'5实体=2画、2盔甲架、1甜浆果物品展示框；不是真NPC；立方图不渲染原实体。',
'42方块实体完整阅读；唱片机保存ward唱片、营火lit、钟只读，无Java/游戏/声音。',
'4完整JSON为单元素pool及3loot；原生minecraft嵌套3职业loot、fishes tag、root structure/biome/运行时转换未追读。药水名称与效果不一致处按原JSON保留，不能凭名字声称用途。',
'DataVersion2586旧cauldron[level3]及原状态保留，未验证1.20.1转换。5221省略格与air39严格区别。',
'原始类色全格图不证明原版碰撞、烟道防火、楼梯全部净空或床边可交互。',
'参考提议最多1，仅COD3NPC01；不能自增正式接受数，不影响COD4已接受153/缺847，NPC01累计未推断。']
comparison={'064_prior_complete_case':read(OLD/'complete-saved-semantic-boundaries.json')['064F01_complete_saved_case_preserved'],'prior_binding':bind(OLD/'complete-saved-semantic-boundaries.json'),'actual_reuse':'完整旧064七项观察及家族/限制已在189读取，本批再次完整读保存记录，不重开旧NBT/PNG，不增旧例信用。','current_disposition':'PENDING_INDEPENDENT_WHOLE_FAMILY_REVIEW','proposal_maximum':1,'reason':'064为北部独立长热厅、南东木构住宅、东内折阶及顶下储藏；190为南纵翼上下同位切割/睡眠、北横厅西折阶与东独立炊事/储物，桥廊连接两翼。差异在生产-居住垂直关系和公共交通组织，不以蓝屋面、职业名称、设备数或体量计数。064同作者上下工居框架仍须独立判断，不能自行排除家族重复。'}
images=[bind(P/n) for n in ['F01-whole.png','F01-cutaway.png','F01-y0.png','F01-y3.png','F01-y4.png','F01-y10.png','F01-vertical.png']]
case={'id':'F01','source':s,'observations':observations,'limitations':limits,'images_actually_viewed':images,'family_review':comparison,'formal_credit_added':0,'native_acceptance':False}
save('manual-review.json',{'cases':[case],'new_whole_reference_studies':1,'formal_credit_added':0,'independent_review_required':True})
save('actual-reading-boundary.json',{'original_index_RLE':{'layers':list(range(20)),'positions':9500,'rows':500,'representation':'original palette indices, x-count RLE, ?omitted vs39air','all_actual_read':True},'palette':{'entries':173,'actual_read_chunks':['0..85','86..172'],'initial_combined_clipped_not_counted_as_full':True},'BE_full_actual_read':42,'entities_full_actual_read':5,'context_full_JSON_actual_read':4,'metadata_full_actual_read':2,'context_initial_pretty_output_clipped_repaired':'entire4JSON+2metadata subsequently compactly output untruncated','PNG_generated':7,'PNG_actual_viewed':images,'old064_saved_record_reuse_only':True,'root_and_external_loot_unread':True,'semantic_credit_added':0})
prev=bind(OLD/'RECEIPT.json')
for n in ['latest-independent-admissions.json','carried-forward-pending.json']:
 d=read(OLD/n)
 if n.startswith('carried'):
  d['previous_batch_receipt']=prev;d['current_batch_new_pending']=[{'batch':190,'id':'F01','scope':'COD3NPC01','status':'PENDING_INDEPENDENT_WHOLE_FAMILY_REVIEW','proposal_maximum':1,'formal_credit_added':0,'manual_review':str(P/'manual-review.json')}]
  d['current_batch_pending_cases']=['190F01']
 save(n,d)
session={'batch':190,'status':'ONE_COMPLETE_WOODWORK_LIVING_SOURCE_STUDIED_PENDING_INDEPENDENT_REVIEW','formal_credit_added':0,'prior_admissions_current_increment':0,'186first187_later_carry_increment':0,'actual_new_original_semantic_source_studies':1,'complete_new_whole_reference_studies':1,'current_PNG':7,'PNG_actual_viewed':7,'COD4_accepted_baseline':153,'COD4_gap':847,'COD4_increment':0,'NPC05_increment':0,'NPC01_cumulative_not_inferred':True,'java_run':False,'game_run':False,'product_files_written':False,'masterlists_edited':False,'all_tasks_complete':False,'actual_active_work_hours':None,'next':'交Main独立整例及家族复审190F01；157W01仍待审，不重交旧HOLD；未满1000继续真实相近整例研究，不制作建筑。'}
save('session.json',session)
checks=[]
def check(n,b):checks.append({'name':n,'passed':bool(b)})
g={tuple(b['pos']):b['state'] for b in r['blocks']};out={}
for l in read(P/'original-index-rle.json')['layers']:
 for z,row in enumerate(l['rows_z0_24']):
  x=0
  for run in row.split():
   v,_,count=run.partition('x');count=int(count) if count else 1
   for _ in range(count):
    if v!='?':out[(x,l['y'],z)]=int(v)
    x+=1
  check('RLE_y%s_z%s_width19'%(l['y'],z),x==19)
check('all_4279_saved_indices_exact',out==g)
check('counts',len(g)==4279 and sum(r['palette'][v]['Name']=='minecraft:air' for v in g.values())==1246)
check('all_palette_BE_entities',len(r['palette'])==173 and sum('nbt'in b for b in r['blocks'])==42 and len(r['entities'])==5)
check('source_archive_hash',bind(Path(s['source_archive']))['sha256']==s['source_archive_sha256'])
with zipfile.ZipFile(s['source_archive']) as z:check('original_NBT_hash',hashlib.sha256(z.read(s['member'])).hexdigest()==s['nbt_sha256'])
for f in read(P/'protected-inputs.json')['files']:check('protected_unchanged:'+f['path'],bind(Path(f['path']))==f)
check('old186_admission_carry_exact',read(P/'latest-independent-admissions.json')['newly_notified_NPC01_admission_186_F04']==read(OLD/'latest-independent-admissions.json')['newly_notified_NPC01_admission_186_F04'])
check('old182_HOLD_carry_exact',read(P/'carried-forward-pending.json')['182F01_NPC01_resolved_initial_review_HOLD0_first184']==read(OLD/'carried-forward-pending.json')['182F01_NPC01_resolved_initial_review_HOLD0_first184'])
check('all7PNG_exist',len(list(P.glob('F01-*.png')))==7)
check('one_proposal_not_admission',session['formal_credit_added']==0)
v={'status':'PASS' if all(c['passed'] for c in checks) else 'FAIL','checks':checks,'check_count':len(checks),'machine_assertions_not_credit':True};save('verification.json',v)
save('active-checkpoint.json',{**session,'verification':v['status']})
(P/'HANDOFF.md').write_text('第190批：Simply Houses taiga_woodcutter完整源空间研究1例，待Main独立整例/家族复审，正式新增0。完整读20层9500位置原索引RLE、173palette、42BE、5entities、4JSON+2metadata，实际看7PNG。南翼下切割上卧室、北横厅西折阶东炊事/储物、桥廊连接，与064热厅复合住宅比较全文保存。三块孤立north床尾、旧状态与原生/地形/碰撞限制保留。只改190研究目录，不运行Java/游戏、不改清单/产品、不制作新建筑。157W01继续待审；182HOLD、174/186已接受首次记录均承接且本批0。\n')
if v['status']!='PASS':print(json.dumps([c for c in checks if not c['passed']],ensure_ascii=False));raise SystemExit('NOT SEALED')
files=[bind(p) for p in sorted(P.iterdir()) if p.is_file() and p.name!='RECEIPT.json'];save('RECEIPT.json',{**session,'files':files})
print(json.dumps({'receipt':bind(P/'RECEIPT.json'),'files':len(files),'checks':len(checks)},ensure_ascii=False))
