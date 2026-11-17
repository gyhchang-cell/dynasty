"""Bound the explicitly authorized deeper study of sealed141 F01 without editing141."""
from pathlib import Path
from zipfile import ZipFile
import json,hashlib,sys,math
O=Path(__file__).resolve().parent;R=O.parents[2];P=O.with_name('research-20261104-smithy-141');assert not(O/'RECEIPT.json').exists()
sys.path.insert(0,str(R/'tools/architecture'))
from nbt_read import read

def get(p):return json.loads(p.read_text())
def put(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def restore(v):
 if isinstance(v,dict):
  if set(v)=={'__original_nbt_byte_array_hex__'}:return bytes.fromhex(v['__original_nbt_byte_array_hex__'])
  return {k:restore(w)for k,w in v.items()}
 if isinstance(v,list):return [restore(w)for w in v]
 return v
checks=[]
def ck(n,v):
 assert v,n;checks.append(n)
def bindings(v):
 if isinstance(v,dict):
  if {'path','sha256','bytes'}<=v.keys():ck(v['path'],bind(v['path'])=={k:v[k]for k in ['path','sha256','bytes']})
  else:
   for w in v.values():bindings(w)
 elif isinstance(v,list):
  for w in v:bindings(w)
for f in get(P/'RECEIPT.json')['files']:bindings(f)
bindings(get(O/'continuation-inputs.json'))
s=get(P/'sources.json')['candidates'][0];r=get(P/'raw-source-audit.json')['candidates'][0];d=restore(r['nbt_decoded_original']);pal=d['palette'];mp={tuple(b['pos']):b['state']for b in d['blocks']}
with ZipFile(s['source_archive'])as z:
 b=z.read(s['member']);ck('fixed archive',bind(s['source_archive'])['sha256']==s['source_archive_sha256']);ck('original NBT full equality existing decoder',hashlib.sha256(b).hexdigest()==s['nbt_sha256']and read(b)==d)
 for t in get(P/'source-context.json')['candidates'][0]['contexts']:ck('context bytes '+t['member'],hashlib.sha256(z.read(t['member'])).hexdigest()==t['sha256']and json.loads(z.read(t['member']))==t['json'])
ck('original palette all135',get(O/'original-palette.json')==pal and len(pal)==135)
y=None;grid={};rows=0
for line in (O/'original-layer-index-runs.txt').read_text().splitlines():
 if line.startswith('Y='):y=int(line.split(';')[0][2:]);continue
 zi,raw=line.split(':',1);zz=int(zi);arr=[]
 for run in raw.split(','):
  kv=run.split(':');val=None if kv[0]=='-'else int(kv[0]);n=int(kv[1])if len(kv)>1 else 1;arr.extend([val]*n)
 ck('layer row '+str((y,zz)),len(arr)==17)
 for x,st in enumerate(arr):grid[(x,y,zz)]=st
 rows+=1
ck('all40 index planes lossless including absence',rows==40*17 and len(grid)==11560 and all(grid[q]==mp.get(q)for q in grid))
ck('exact source dimensions storage and no implicit air',d['size']==[17,40,17]and len(mp)==4263 and r['nonair']==1944 and r['air']==2319 and 11560-len(mp)==7297)
ck('upper17to39 entirely omitted',all(y<=16 for x,y,z in mp))
for vals in get(O/'route-state-evidence.json').values():
 for v in vals:
  q=tuple(v['pos']);ck('route original '+str(q),v['state']==(pal[mp[q]]if q in mp else None)and v['omitted']==(q not in mp))
new_names=['y2','y4','y6','y8','y10','y12','y14','y16','vertical'];new_views=[bind(P/f'F01-{v}.png')for v in new_names];old_views=get(P/'visual-reading-boundary.json')['viewed'];ck('previous three actually viewed',len(old_views)==3);all_views=old_views+new_views;seen={v['path']for v in all_views};unviewed=[bind(p)for p in sorted(P.glob('*.png'))if str(p)not in seen];ck('23existing images 12 cumulative 9 new 11 unread',len(all_views)==12 and len(new_views)==9 and len(unviewed)==11)
obs=dict(
 layout='完整餐饮/储物民用屋：东侧突出入口翼由北/南两门进入，横向接中央大餐厅；北备餐室由台面/柱与主厅分界、南端有附属座席凹厅；西墙内窄折返阶上至同十字交叉屋盖下的中央上厅，上厅北/南各开双宽口进储箱凹室，东侧有两工作台。只把这一整组设计最多提1，非分拆9箱/上下层/两个门/多个厅。源是butcher且tavern loot，相关性仅公众接待—受控备餐—内升冷储/支向空间组织，不是锻造流程完成。',
 proportion='17×40×17/DV3578，4263存储=1944非air2319显式air，7297省略。全部135palette/40原层索引（0..16含原状态、17..39全省略）/14BE/entities[]已实读。floor1/use2下层，floor7/use8上层，y12/13交叉高盖已封顶，y14..16仅局部烟构/周围显式air或省略，不编第三完整使用层。保留141三图，当前新增看9图，累计12/原生成23，11张高处全省略区的类色PNG未看；不是23图全看。',
 facade='木框架/低石基/绿色薄玻璃，东入口翼两门均open原状态；东正中15,3,8是green pane，不当从东窗直穿的门。北门13,2/3,5与南门13,2/3,11分别接13,1,4south和13,1,12north底石阶。入口道路jigsaw在16,1,14，并不与正中玻璃形成直线路径；外绕路和门碰撞未实机验证。',
 roof='主南北高脊与东西横脊相交，brick/granite stairs和slabs并用、wood檐托及墙端封闭上下厅。y12大片完整砖/双半块、y13脊底半块，不能将屋盖底阶当上楼阶。顶烟柱x2,z4延至y16；无通往烟柱或屋脊的楼梯，不算高塔或第三经营层。',
 materials='两smoker3,3,3east与4,3,4north都unlit、Cook/Burn0、Items[]、RecipesUsed{}；无运行中的热作/锻炉/砧/熔岩淬水证明。底箱7,1,5north tavern_downstairs，上方7,2,5 TOP/south oakstairs为台面，非air，箱开盖未验。上八箱在x4和9、z3/4及12/13，原left/right/方向/八独立seed保留为四双箱组合，不能当8已取奖励。三个craftingtable和两个villager sockets仅静态状态/池接口，entities[]不称已生NPC。141真正red_candle的原三烛状态与138的orange_candle勘误分开，不混用来源。',
 circulation='主厅5,2/3,7→4,2/3,7→3,2/3,7→3,2/3,8均显式air，到3,2,9south BOTTOM阶；其上3,3,9是east/open/bottom spruce trapdoor，不写air且保留通行/净空未验。南转角3,2,10和2,2,10整木（上use3air），西支2,3,9→2,4,8→2,5,7 north BOTTOM连续三阶，接2,5,6整木与3,5,6 TOP/west转角；回东支3,6,7→3,7,8 south BOTTOM，再3,7,9 TOP/north落脚→4,7,9/5,7,9整木上use8air至上厅。TOP承托与open活板门不是新增踏步/空气。上南北口x6/7,z5和11在y8/9原air且floor7spruceplanks；无内门证明也不写独立全封闭多房。任何阶/薄门/头顶/玩家或NPC通行均未原生验收。',
 terrain_and_dedup='源内低草土地基+窄石边与木地板一体，source仅固定模板，非山脚自然落地或雨险验收。root fortified_village size6/max80/start0/WORLD_SURFACE_WG/beardthin/expansiontrue；house weight2 single rigid empty。复用141实际读过8context的准确范围：starts empty1/castle3，castleNBT未读；roads只name/fallback/count12/straight2样本，余11条目及roadNBT未读；双tavern loot是候选，不是存货回执。当前完整关系与070F02热作低凹口+外阶高双床、087F02两个不通底店+外阶上南卧、115F01西热翼/东动物院/中央直阶冷储、134F02内折阶上北工区西敞台均不同，但公众厅+内折返阶+上冷储本身不是新颖性保证。承认相关性和家族近似，交Main可判0，不因材质/职业或箱数保证接受。')
comparisons=[]
for n,case in [(70,'F02'),(87,'F02'),(115,'F01'),(134,'F02')]:comparisons.append(dict(binding=bind(P.with_name(f'research-20261104-smithy-{n:03d}')/'manual-review.json'),case=case,actual_saved_observations_read=True,old_images_or_original_replayed=False,credit=0))
review=dict(source=s,source_batch=141,source_case='F01',study_batch=142,explicit_deepening_not_new_source=True,complete_source_spatial_study=True,observations=obs,comparisons=comparisons,credit_proposal_maximum=1,formal_credit_added=0,native_acceptance=False,old141_bounded_study_not_retroactively_changed=True)
put('complete-study-review.json',review)
put('visual-reading-boundary.json',dict(new_current_views=new_views,old_actual_three_reused=old_views,cumulative_actual_views=all_views,not_viewed_generated=unviewed,new_images_generated=0,current_new_actual_count=9,cumulative_actual_count=12,total_existing_generated=23,all_generated_images_viewed=False,upper_unviewed_png_not_source_air_proof=True,class_colors_not_textures_or_collision=True))
put('full-study-reading-boundary.json',dict(source_batch=141,palette_entries_actually_read=135,original_index_planes_actually_read=list(range(40)),index_runs=bind(O/'original-layer-index-runs.txt'),all_14_original_BE_actually_read=True,original_entities=[],new_PNG_actually_viewed=9,prior_three_reused=True,all_generated_PNG_viewed=False,original_source_full_equality_verified_with_existing_decoder=True,context_reading='Reuse141 prior actual8context semantic scope; current rehash/JSON equality is integrity not new semantic credit; no metadata rereading credit.',no_native_navigation_verification=True))
a=get(P/'latest-independent-admissions.json');a['previous_binding']=bind(P/'latest-independent-admissions.json');a['138F02_first141_carry_only_no_current_increment_142']=True;put('latest-independent-admissions.json',a)
carry=get(P/'carried-forward-pending.json');ck('no previous unresolved',carry['current_batch_pending_cases']==[]and carry['carried_unresolved_whole_reference_proposals']==[]);carry['previous_batch_receipt']=bind(P/'RECEIPT.json');carry['current_batch_new_pending']=1;carry['current_batch_pending_cases']=[dict(batch=142,id='F01',source_batch=141,source_case='F01',maximum=1,independent_admission=False)];put('carried-forward-pending.json',carry)
for n,first in [(128,131),(134,136),(136,137),(138,141)]:ck('complete admission and resolved equal '+str(n),a[f'newly_notified_admission_{n}_F02']==carry[f'{n}F02_resolved_accept1_first{first}'])
bindings(a);bindings(carry);bindings(comparisons)
put('task-scope-boundary.json',get(P/'task-scope-boundary.json'))
session=dict(batch=142,status='141_F01_DEEPENING_COMPLETE_SPATIAL_STUDY_PENDING_MAX1',new_source_count=0,source_batch=141,new_actual_PNG=9,old_actual_PNG_reused=3,cumulative_actual_PNG=12,total_existing_generated=23,unviewed_generated=11,palette_entries_read=135,index_planes_read=40,complete_whole_reference_studies=1,pending_maximum=1,formal_credit_added=0,prior_admissions_current_increment=0,product_files_written=False,masterlists_edited=False,java_run=False,game_run=False,native_acceptance=False,all_tasks_complete=False,next='Continue other fixed-local related complete designs; Main may judge this whole0 or1. Never repeat141/142 as two buildings; do not self-admit.')
put('session.json',session);put('active-checkpoint.json',{**session,'previous_receipt':bind(P/'RECEIPT.json')})
(O/'HANDOFF.md').write_text('142按明确交办深化141F01 fortified butcher固定原源；135palette/40原层索引/14BE实读，新增9PNG+141旧3合12/23，11高层全省略区域图未看。下双侧入口翼→中央餐厅/北备餐/南座席、西内折返阶→上厅南北储箱凹室整体最多1pending，正式0；首阶上open trapdoor与所有半格/头顶/箱开盖/实际地形和NPC未验，7297省略不补air。原141及已认可138不重写不重计；完整旧接受138first141等carry0。没有新制作/Java/游戏/主清单更动。\n')
put('verification.json',dict(status='PASS_SOURCE_AND_READING_BOUNDARIES_NOT_INDEPENDENT_ACCEPTANCE',checks_passed=len(checks),checks=checks,semantic_credit_from_hashing=0,source_archive_and_all_original_NBT_equal=True,existing_decoder=bind(R/'tools/architecture/nbt_read.py'),all_tasks_complete=False))
put('RECEIPT.json',{**session,'checks_passed':len(checks),'files':[bind(p)for p in sorted(O.iterdir())if p.is_file()and p.name!='RECEIPT.json']});print(json.dumps(dict(receipt=bind(O/'RECEIPT.json'),checks=len(checks),files=len(get(O/'RECEIPT.json')['files'])),ensure_ascii=False))
