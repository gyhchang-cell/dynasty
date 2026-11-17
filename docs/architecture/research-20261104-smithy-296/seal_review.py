"""Seal complete original residence study; semantic admission remains independent."""
import json,hashlib,sys,math
from pathlib import Path
from zipfile import ZipFile
P=Path(__file__).resolve().parent;R=P.parents[2]
assert not(P/'RECEIPT.json').exists()
sys.path.insert(0,str(R/'tools/architecture'))
from nbt_read import read
def ld(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
checks=[]
def ck(n,v):
 assert v,n
 checks.append(n)
b=ld(P/'source-binding.json');d=ld(P/'source-original.json');bridge=ld(P/'bridge-original.json');c=ld(P/'source-counts.json')
ck('fixed archive exact',bind(b['archive']['path'])==b['archive'])
with ZipFile(b['archive']['path'])as z:
 for row,src in [(b,d),(b['bridge'],bridge)]:
  raw=z.read(row['member']);ck('source exact '+row['member'],hashlib.sha256(raw).hexdigest()==row['raw_sha256']and read(raw)==src)
 for row in ld(P/'source-context.json')['resources']:
  raw=z.read(row['member']);ck('context exact '+row['member'],hashlib.sha256(raw).hexdigest()==row['sha256']and raw.decode()==row['text']and json.loads(raw)==row['json'])
ck('residence accounting',c['stored']==4930 and c['nonair']==3434 and c['air']==1496 and c['omitted']==6270 and c['stored']+c['omitted']==math.prod(d['size']))
ck('palette BE entities accounting',len(d['palette'])==200 and len(ld(P/'all-BE-original.json'))==55 and len(ld(P/'grouped-full-BE.json'))==12 and len(d['entities'])==4)
ck('source approach accounting',len(bridge['blocks'])==166 and len(bridge['palette'])==20 and not bridge['entities'])
ck('ten viewed image files',len(list(P.glob('*.png')))==10)
ck('133 saved actual source probes',ld(P/'actually-read-route-probes.json')['count']==133)
ck('36 bridge upper walk probes',ld(P/'bridge-upper-walk-probes.json')['count']==36)
ck('exact-name prior whole history no hits',not ld(P/'history-screen.json')['hits'])
old=R/'docs/architecture/research-20261104-smithy-095/manual-review.json';case=ld(old)['cases'][0]
put('complete-old-whole-comparison.json',dict(binding=bind(old),old_whole={k:case[k]for k in ['id','member','observations','whole_boundary','credit_proposal_maximum','status']},actual_current_reading='All seven own observations and whole boundary read in full; no old images reopened or added credit.',current_comparison='旧森林屋为宽L/T北横生活翼/东长分床翼，底use3、中use9、北阁床use13，内三宽长直阶，七床、六painting；本草原屋为厚高石台内低储藏、内单宽六阶、上方多门夹室与狭北翼、单列五梯达南阁，唯一个完整床对，西原接近台阶桥。比较完整占地/分房/使用标高/交通，不以浅深木、屋顶颜色、三孤床脚或bbox差异断新。两者同作者多层复合住宅族，Main仍可MERGE0；旧095对铁匠用途HOLD0持续，不因本次换用途自动给旧屋信用。'))
put('excluded-prior-whole-windmill.json',dict(binding=bind(R/'docs/architecture/research-20261104-smithy-157/active-checkpoint.json'),decision='旧157原两片illager风车早已整栋19PNG研究，尽管manual未直接含member，source/topology索引查出，当前未渲染、不加数。',old_checkpoint=ld(R/'docs/architecture/research-20261104-smithy-157/active-checkpoint.json')))
status='SEALED_ONE_ORIGINAL_RAISED_RESIDENCE_AND_APPROACH_STUDY_SPATIAL_AUXILIARY_PENDING_MAIN_MAX1'
review=dict(batch=296,status=status,source=b,source_counting_unit='One complete residence including optional original approach; bridge, rooms, floors, entity decorations and images never separate building references.',new_complete_source_whole_studies=1,new_qualifying_buildings_confirmed=0,reference_proposal_maximum=1,formal_credit_added=0,tasks_deleted=0,native_acceptance=False,
 actual_reading=dict(images_actually_viewed=10,images=[bind(p)for p in sorted(P.glob('*.png'))],house_plan_layers_actually_viewed=25,house_full_height_section_planes_actually_viewed=2,approach_plan_layers_actually_viewed=7,house_palette_states_actually_read=200,approach_palette_states_actually_read=20,unique_complete_BE_payloads_actually_read=12,house_BE_positions_actually_read=55,source_entity_profiles_actually_read=4,complete_context_JSON_actually_read=4,saved_house_probes_actually_read=133,saved_bridge_upper_walk_probes_actually_read=36,all4930_positions_individually_read=False,old095_F01_complete_seven_dimensions_read=True),
 seven_dimensions=dict(
 layout='单整栋高石台复合住宅：南主块石基内y2..4有低储藏小室/桶；y5地板上use6主厅接西门，北细长实体台上y7地板/use8窄厅与外环廊；内单宽南向长阶升到floor11/use12的分房居住层，南阁floor16/use17由西竖梯连接。北主长翼与南横向房块/东突出小间构非规则复合占地。原接桥是西侧三宽上台阶，不是另栋住宅。',
 proportion='原16×25×28/DV2586，4930stored=3434nonair1496air，6270省略unknown；200palette/55BE/4装饰实体。最高y23烟口、y24省略，25不是层数；厚石台、低储室、主生活标高、居住层和南阁分别描述，不能把高石台全当住楼。桥12×7×5/166存/254省略，不加一栋。',
 facade='下stone402/stonebrick440/andesite及basalt混石厚台，转折外廊悬挑；上strippedbirch260/strippedoak225浅木框加magenta_terracotta247墙。spruce/darkoak活板与栅形成细构件、栏边和窗饰，原无玻璃，不把类色灰全叫石瓦。21原墙牌Text1..4全空；3spruce门+6oak门各两半，合9扇非18。',
 roof='多段相交坡盖：北细翼较低长双坡，南主房高横脊及东凸翼低坡，木檐与阶/半砖/活板层层收边。原193sprucestairs、168darkoakslab与315sprucetrapdoor等同时用于屋盖/托檐/细饰；顶盖灰色仅分类，不能认瓦材。南烟口y23 lit营火，8其他campfire多为未燃陈设。未实测遮雨/烟路或消防。',
 materials='两箱与十二桶保留normal/potions/barrels原loot引用、无seed；本批三loot全文未读，普通potion不替原变体。两smoker分别(6,12,24)Slot1 charcoal4与(6,17,13)charcoal6，均unlit/CookBurnTotal0，无输入/生产回执。五redbed块只有(6,12,4head)/(6,12,5foot)north一完整床；另(4,12,19)south foot、(5,12,12)/(11,12,18)west foot的期望head分别为open活板/木柱，非有效床。4源实体三painting加cookie itemframe，不是住户或食物获得回执；两原skull仅纹理元数据不新做人模/贴图。',
 circulation='主长阶x9：y6,z16→y7,z17→y8,z18→y9,z19→y10,z20→y11,z21均south bottom darkoak，步上y+1/+2逐格有air；顶南x9,z22为木柱，向西转(8,11,21)plank上y12/13air可研究落脚。下前(9,5,15)andesite上6/7air，原西门(2,6/7,18)east closed、内x3,y6/7air。竖梯(3,y12..16,18)east，背x2为plank/wood，东落脚(4,16,18)plank上17/18air。门控、横穿厅室、薄件碰撞、阁层开箱和NPC路径未原生验；不概括所有房间均可达。',
 terrain='西house socket(0,0,18)west_up/namepart0/targetpart1，原bridge socket(11,0,2)east_up/namepart1/targetpart0，无旋转单步邻接得到bridge origin(-12,0,16)。三宽东升阶localx0y0至x5y5，x6..11 y5为顶步行台接house x0/1 floor5、门use6；台上原多省略，不能当air。bridge只有单接头、不捏造第二出口/无限串屋。root WORLD_SURFACE_WG/beardthin,start0,size2/max114；start池唯一房、main池房/桥各weight1 rigid/empty，候选匹配及游戏引擎未运行。plains/meadow/sunflowerplains tag已读；自然坡/世界下方/y-1未知，不凭厚石基保证落地。'),
 applicability=dict(target='COD2 DUN05 酆都鬼市沿街民宅/客栈与楼阁栈道的空间组织辅助研究，最多一处候选待Main独立判断。',useful='可应用多标高分房、窄长主翼接横房、外廊与单宽内阶/阁梯的容量关系；台阶桥接高入口时另核步行层而非只对socket。',unmet='源是西式浅木/紫陶住宅，无黑瓦白墙徽派立面、中文鬼市招牌、屋顶连续探索、衙门/渡口/任务链。不能直接充当DUN05完成资产，严格风格相关性或近族判断可HOLD0。NPC12茶馆/铁匠用途未证明，不混入其1000计数。'),
 prior_reading='旧272F03只有材料/BE与配置预筛，没有fullNBT spatial/PNG；当前补足首次整屋/桥空间查看。旧157风车有19整屋图，查出后排除未再渲染。293–295重复/近似营地信用继续0。',
 applied_principles=['把低储藏、主厅、上层隔房与阁层分别按实际使用标高算净空，烟口/高石台不算居住层。','上长阶末端若正前木柱，另查转侧落脚和双高净空；照片中看着通不等真实通。','地形接头标高可与步行入口标高不同，匹配接口后还要看步行台、门槛和省略格。','借用空间组织方法，不复制建筑/模型/贴图；主题立面和中文导航仍按原需求单独完成与验收。'],
 limits=['整处研究1、候选最多1且确认相关0/正式0；Main阅图/近族/用途独立审查前不入账，未满1000不制作不删任务。','10PNG为源类别色/全格薄件近似；原源属性未改，仅研究图平移，不是游戏生成/碰撞/实机截图或原创产物。','主4930原格和桥166原格已保存但不宣称全部逐格读。已实际看主25层/桥7层、主2整剖；全部200+20palette/12BE独特全文覆盖55位置及4实体全文实际读。','只写296目录，旧sealed/主清单/ownership/pending/session/专业资产/共享Jar不写；无Java/游戏/声音亮度/唤醒焦点/用户实例存档/网络/Git/自动化操作。'],NPC_cumulative=None,all_tasks_complete=False)
put('manual-review.json',review)
previous=ld(R/'docs/architecture/research-20261104-smithy-295/protected-current.json');protected=[]
for row in previous['files']:
 before=row['current'];after=bind(before['path']);protected.append(dict(previous295_observation=before,current=after,unchanged=before==after,this_chat_wrote_file=False))
put('protected-current.json',dict(files=protected,boundary='Read-only comparison with295 end; not a fabricated296-start measurement. Concurrent changes never overwritten.'))
ck('shared Jar unchanged since295',all(x['unchanged']for x in protected if x['current']['path'].endswith('.jar')))
cp=ld(P/'active-checkpoint.json');cp.update(status=status,images_generated=10,images_actually_viewed=10,new_complete_source_whole_studies=1,new_qualifying_buildings_confirmed=0,reference_proposal_maximum=1,formal_credit_added=0,next='Main可按风格/近族HOLD0；继续未研究的不同完整建筑，先查sources+旧ID台账，不将组件与截图算数。');put('active-checkpoint.json',cp)
put('verification.json',dict(passed=True,count=len(checks),checks=checks,java_run=False,game_run=False,independent_acceptance=False))
files=[bind(p)for p in sorted(P.iterdir())if p.is_file()and p.name!='RECEIPT.json']
put('RECEIPT.json',dict(batch=296,status=status,files=files,checks=len(checks),new_complete_source_whole_studies=1,reference_proposal_maximum=1,formal_credit_added=0,tasks_deleted=0,all_tasks_complete=False))
print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),manual=bind(P/'manual-review.json'),files=len(files),checks=len(checks),protected_unchanged=sum(x['unchanged']for x in protected)),ensure_ascii=False))
