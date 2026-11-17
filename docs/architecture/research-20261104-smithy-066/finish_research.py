"""Current unsealed batch only. Research evidence, never product or acceptance writes."""
import json,hashlib,math,sys
from pathlib import Path
from zipfile import ZipFile
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
assert not (OUT/'RECEIPT.json').exists()
def put(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
sources=json.loads((OUT/'sources.json').read_text())['candidates'];raw=json.loads((OUT/'raw-source-audit.json').read_text())['candidates']
context=json.loads((OUT/'source-context.json').read_text())
# Follow the exact local biome collections; no inferred world-generation result.
with ZipFile(sources[0]['source_archive']) as z:
 closure=[]
 for m in ['data/repurposed_structures/tags/worldgen/biome/collections/hills.json','data/repurposed_structures/tags/worldgen/biome/collections/deep_oceans.json']:
  if m in z.namelist():
   b=z.read(m);closure.append({'member':m,'sha256':hashlib.sha256(b).hexdigest(),'json':json.loads(b)})
  else:closure.append({'member':m,'missing':True})
put('biome-collection-context.json',closure)
functional=[]
for a in raw:
 d=a['nbt_decoded_original'];pal=d.get('palette')or d['palettes'][0];items=[]
 for b in d['blocks']:
  state=pal[b['state']]
  if b.get('nbt') or any(w in state['Name']for w in ['door','grindstone','furnace','magma','bubble','stairs']):items.append({'pos':b['pos'],'state':state,'original_block_entity':b.get('nbt')})
 functional.append({'id':a['id'],'stored_records':len(d['blocks']),'declared_volume':math.prod(d['size']),'omitted_positions':math.prod(d['size'])-len(d['blocks']),'explicit_air':a['air'],'nonair_including_fluids':a['nonair'],'entities_original':d.get('entities',[]),'functional_states':items})
put('functional-evidence.json',{'candidates':functional,'sparse_NBT_omission_not_explicit_air':True,'water_not_solid':True,'native_function_not_verified':True})
obs=[
{'layout':'7×7占地内后封闭单冷作业室接北面双砂轮；一扇门居中，箱在后室西侧。没有前后热棚或独立住居翼。','proportion':'原7×9×7，238记录=204非空气+34显式air，另203位置未存；窄房高屋盖，不把y8屋脊当楼层。','facade':'石/石砖小室配灰玻璃和云杉活板装饰；门下半(3,1,2)状态south，两砂轮(2/4,1,1)均south。门朝向不直接等同北外立面。','roof':'云杉原木42形成后室逐级坡盖；前低檐y4草皮/蕨带不同于完整草皮屋盖。无梯/床，不能声称阁楼可住。','materials':'stone39、stone_bricks38与spruce_log42；没有炉/铁砧/岩浆。箱(2,1,3)east保留weaponsmith loot及种子；两块云杉楼梯(4,1,3/4)east是低处陈设，不是上楼梯。','circulation':'北街socket(3,1,0)→双砂轮之间→中门→后室箱；两砂轮没有形成独立两栋作坊。实际门和砂轮碰撞/交互净空未验。','terrain':'原草土/路径小基裙，入口empty池final structure_void，未发现待接室翼；山地村WORLD_SURFACE_WG投射不等于本项目山脚落地验收。'},
{'layout':'6×7原单坡棚体，砂轮在(2,1,3)，石砖墙柱支承屋盖；未见封闭储室、独立生活区或热工区。','proportion':'原6×5×7，121记录=82非空气+39air，89未存；低矮棚并非仅因小就排除，当前独立完整匠铺语义证据不足，保留0。','facade':'开敞前作业口及两墙柱/火把，南后侧屋面降至低处；没有门窗和箱，不把开口称缺失封墙。','roof':'20云杉原木构成单坡，向南z6下降；屋顶和柱是一体遮棚，不以坡向旋转再计一栋。','materials':'stone_brick_wall13、grass_block19、dirt_path11、grindstone1；无炉/岩浆/床。蕨/大蕨为植被，不能替代功能设施。','circulation':'北入口empty socket到棚下砂轮；(5,0,2)up_north连mountains/decor，final grass_block，是外饰接口，不编造后室。','terrain':'装饰池含向下支柱processor，原样保存；下探支柱/世界地形未运行，屋体遮棚边界和完整职业建筑边界分开，当前0。'},
{'layout':'9×11石作业前棚接木围后储室，双熔炉上下叠、箱在后室；与已研究经典前棚后室组织近似，保持家族独立信用0。','proportion':'9×9×11，558原记录全为非空气，其中water84+bubble2；333位置未存，不能称558实体建筑块或把省略格全判air。','facade':'石前棚开口、木后室玻璃，西入口jigsaw在(0,1,3)west_up，final为east bottom waterlogged cobble stair，不把非空街道池当缺房翼。','roof':'后室坡盖连接低平石棚，原橡木楼梯64及尖滴水石27；与057统一平石盖不同，但屋盖/水下材质变化目前不足独立空间家族信用。','materials':'cobble152、oak_planks68、stripped_oak_log38；magma2+bubble2非熔岩或已验淬火槽。双炉(4,3/4,3)west lit=false Items空，箱(6,2,4)south waterlogged。','circulation':'前棚砂轮(2,2,1)east与后室储箱相接，实际84水遮蔽室内。另2图仅隐藏water/bubble用于观察，没有修改原始水状态，也未证水下NPC作业。','terrain':'根OCEAN_FLOOR_WG、max_y52；向下dirt pillar引用dirt处理列表，noise换coarse_dirt/sand已保存。真实海底承托/街道相接/含水碰撞未验，不转作山脚已完成设计。'}]
comparisons=[
'与061F03抬高后冷室+南长栏台/侧外阶不同，本例地面北双砂轮正门直入小室，无栏台/折入外阶；与063F01双侧外阶上双床不同，无上下经营层；与060F03三侧热冷工作位和双门不同，无热台/侧门。仅提出最多1，最终完整性和家族判定交独立复核。',
'完整遮棚源已研究，但只能确定单砂轮遮棚，尚未证独立完整相关匠铺。不是凭文件名houses或metadata记信用；无补翼并不自动满足完整建筑要求。',
'057F01前石热棚/后木储室双炉西向及后箱；当前相同前后功能顺序，炉和箱偏移与水/坡盖变化不自动独立。不是精确hash重复，但保守保持0，不将海洋temple几何近邻误判为匠铺同家族证明。']
cases=[]
for a,o,comparison,credit in zip(sources,obs,comparisons,[1,0,0]):
 images=[bind(p)for p in sorted(OUT.glob(a['id']+'-*.png'))]
 cases.append({**a,'observations':o,'images_actually_viewed':images,'whole_boundary':'原稀疏NBT、整体现图、截层和纵剖已研究；未存位置与显式air分开。F02完整遮棚体不等于已证完整职业建筑；世界装配未验。','semantic_family_comparison':comparison,'comparison_documents':[bind(ROOT/'docs/architecture/research-20261104-smithy-057/manual-review.json'),bind(ROOT/'docs/architecture/research-20261104-smithy-060/manual-review.json'),bind(ROOT/'docs/architecture/research-20261104-smithy-061/manual-review.json'),bind(ROOT/'docs/architecture/research-20261104-smithy-063/manual-review.json')],'credit_proposal_maximum':credit,'status':'PENDING_INDEPENDENT_SCOPE_AND_FAMILY_ADMISSION'if credit else 'HELD_ZERO','native_acceptance':False})
put('manual-review.json',{'cases':cases,'source_bodies_studied':3,'whole_smithy_bodies_studied':2,'shelter_body_whole_smithy_boundary_unproven':1,'actual_current_images_viewed':24,'manual_observations':21,'pending_maximum':1,'formal_credit_added':0,'no_independent_self_admission':True})
put('source-context-reading.json',{'metadata':'原mod metadata已读：RepurposedStructures7.1.19+1.20.1-forge，TelepathicGrunt，声明LGPLv3；保留原完整credits，不访问外站，不移植原资产。','F01':'houses和zombie houses均weight2/rigid，常规mossify、僵尸zombify分开；root size6/world surface；mossify逐条规则为cobble.1、stone.1、stonebricks.4mossy/.1cracked、wall.1，不当统一磨损比例。','F02':'houses weight2 rigid/mossify；decor附接原池与pillar_1保存，非后室。towncenter/path处理只是上下文，不增加建筑数量。','F03':'houses weight2 rigid/ocean randomize；streets为外部连接；root size6/ocean floor/height cap52。randomize包含noise、规则、向下pillar及structure_void；其dirt子列表threshold.4→coarse_dirt/.5→sand，不等于本项目实测分布。','missing':'F01/F03引用原版weaponsmith loot不在当前mod Jar；不宣称缺主房，亦不声称运行奖励已接入。','scope_limit':'已读与当前源绑定的房池/根/入口/支柱/地形关键字段；其余完整JSON保留供审查，没有声称逐条读完所有村中心无关processor规则。'})
put('applicable-principles.json',{'principles':['小型冷加工铺可用室外成对磨工位与室内储藏分区，但交互净空须后续原生验收。','屋盖高低和正门次序服务用途；不把屋脊空腔、遮棚和挂接装饰重复计建筑。','有水、含水楼梯、支柱与海底投射须按真实场景验收，不能直接挪用成山脚工坊。','研究功能布置与比例，不复制作者NBT、贴图或模型；完整参考和独立性未达1000前不制作。'],'implemented_product':False})
put('task-scope-boundary.json',{'target':'COD3 NPC01 老陈 山脚铁匠铺空间研究','original_line':1122,'implemented':False,'outstanding':['1000个适用完整不同建筑及独立验收','原创建筑制作','材料与任务前置/付款/获取回执接入','中文指南针','昼夜雨险/水锤世界状态','原生最终验收'],'COD4_ledger':{'accepted':153,'target':1000,'gap':847,'increment':0},'cod5_missing_not_invented':True,'masterlist_deletions':0})
put('session.json',{'batch':66,'status':'MANUAL_STUDY_COMPLETE_VERIFICATION_PENDING','source_bodies_studied':3,'actual_images_viewed':24,'pending_maximum':1,'formal_credit_added':0,'cumulative_history_not_reset':True,'java_run':False,'product_files_written':False,'masterlists_edited':False,'runtime_acceptance':False,'all_tasks_complete':False,'next':'下一批新输入bamboo weaponsmith，仍需先完整来源与语义研究；不得因等待主审停下研究。'})
print('Saved manual21 observations /24 viewed PNG /1 pending /2 held0. Biome collections:',json.dumps(closure,ensure_ascii=False))
