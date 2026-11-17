import json,hashlib,math
from pathlib import Path
from zipfile import ZipFile
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
assert not (OUT/'RECEIPT.json').exists()
def put(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
sources=json.loads((OUT/'sources.json').read_text())['candidates'];raw=json.loads((OUT/'raw-source-audit.json').read_text())['candidates']
biomes=[]
with ZipFile(sources[0]['source_archive'])as z:
 for theme in ['mushrooms','hills']:
  m=f'data/repurposed_structures/tags/worldgen/biome/collections/{theme}.json';b=z.read(m);biomes.append({'member':m,'sha256':hashlib.sha256(b).hexdigest(),'json':json.loads(b)})
put('biome-collection-context.json',biomes);print('BIOMES',json.dumps(biomes,ensure_ascii=False))
functional=[]
for a in raw:
 d=a['nbt_decoded_original'];pal=d.get('palette')or d['palettes'][0];items=[]
 for b in d['blocks']:
  s=pal[b['state']]
  if b.get('nbt')or any(w in s['Name']for w in ['door','furnace','smithing','candle','stairs','wall','smooth_stone']):items.append({'pos':b['pos'],'state':s,'original_block_entity':b.get('nbt')})
 functional.append({'id':a['id'],'stored_records':len(d['blocks']),'declared_volume':math.prod(d['size']),'omitted_positions':math.prod(d['size'])-len(d['blocks']),'explicit_air':a['air'],'nonair':a['nonair'],'entities_original':d.get('entities',[]),'functional_states':items})
put('functional-evidence.json',{'candidates':functional,'sparse_omission_not_air':True,'native_function_not_verified':True})
obs=[
{'layout':'9×8横向小作坊，西双门进单室，北/东侧smooth_stone台呈折角，南中央blast_furnace(4,1,5)与后烟囱一体；无外部工作棚、储箱或卧室。','proportion':'9×8×8全576位置记录，228非空气/348air，屋脊与烟囱最高y7；室内单层，屋顶体积不算楼层。','facade':'mushroom_stem108作围墙/细部、红菇块71和棕菇块21；西双门x1/z3、4同east而hinge左右，4门状态是两扇门而非4入口。四玻璃板为采光。','roof':'整体逐级收进的矩形双坡原菇块盖，后部小烟囱伸出；通用分类图全灰不是石屋或精细菌盖纹理。没有梯床，不把烟囱/屋脊计塔层。','materials':'smooth_stone8沿北东作业台，砖3与brick_stairs1围南炉；炉north/lit=false且Items/Cook/Burn皆空。5处magenta_candle原每处candles4/lit=true，非已运行光照。','circulation':'由西双门进入中央长向空地，(4,1,4)显式air正对北向炉口，台占两侧。炉上brick_stairs朝south、后烟囱尚未证贯通排烟，不将装饰烟囱称完整排烟系统。','terrain':'地板/屋体边界完整记录，西入口empty/final red_mushroom_block，不需要后接房翼；菇林村地表投射不是山脚/本项目生态适配验收。'},
{'layout':'9×12一体L形窄室，西南双门入横向入口段后折向北长室；北端smithing_table(6,1,2)，南端墙/蜡烛陈设，原没有热棚、炉或箱室。','proportion':'9×6×12全部648位置存储，233非空气/415air；低单层，沿L形连续屋盖，不把两个臂各计建筑或两层。','facade':'西双桦门x2/z8、9均east、左右hinge，3玻璃板沿长室；mushroom_stem104为主要围护，不把通用灰图称石墙。','roof':'红菇块85/棕菇块30收成连续L形低屋盖，局部凸端不称塔；屋盖形态要联合室内转折组织比较，换菌材本身不支持信用。','materials':'一个真实smithing_table与2andesite_stairs、1andesite_wall，magenta/purple蜡烛各1均原4candles/littrue；没有grindstone/blastfurnace/anvil/lava或床。','circulation':'门内(3,1,8)/(4,1,8)显式air，折向(5,1,7)至(5,1,3)长室通路，再到北端工作台；这只是原格态连通依据，半块/门碰撞与交互净空未验。','terrain':'原菇材地板随L体连续，入口empty/final structure_void，双门外两andesite_stairs原状态留存；不是自然地面蘑菇，也不声称已接入本项目任务或生成。'},
{'layout':'10×7长条封闭单室，西单门、南墙中央并排双blast_furnace(4/5,1,4)，长轴空通道在北侧，东端一灰玻璃窗；不因两炉记两栋。','proportion':'10×7×7体积490，234记录=184非空气+50air，256位置省略；低长屋身配纵向大坡盖，屋脊y5和墙帽y6非第二层。','facade':'石砖61/stone10围室，西spruce_door(1,1,3)east/closed；东窗一灰玻璃板配两开活板和poppy2，门facing不直接等同西立面朝向。','roof':'spruce_log69逐级向脊收进，屋顶是原木而不是楼梯瓦；南炉上双石砖阶/墙帽形成烟囱意向，无梯床，未证烟道连续。','materials':'两高炉均north/litfalse，原Items空且Burn/Cook0；炉上(4/5,2,4)是stone_bricks，不能声称炉上有贯通烟气或正在冶炼。','circulation':'西门后(2/3/4/5,1,3)显式air通两north炉口；没有独立热棚、储室或回廊，工作流仍为单室侧炉，不以双炉位置改动记新家族。','terrain':'dirt25/grass3与石地小基裙，西empty入口final structure_void，无缺翼；山地村root size6/WORLD_SURFACE_WG只上下文，原生地形与功能未验。'}]
comparisons=[
'与059F02长封闭内炉主室+东侧开放砂轮棚不同，本例只有一室、西双门、北东连续台与南中央炉/后烟囱；与066F01北门双外磨工+后箱不同，本例磨工和外棚皆无。最多1完整单室甲匠作坊候选；菇材和门数本身不构成信用，需独立相关性/家族复核。',
'最近060F02为两个并置冷加工小室，本例连续L形单室、入口臂折到北端工作台；与067F02热台/外前场/侧长室/南箱的分隔流线不同，本例无热外棚。与056住居L也无卧室及外热角。原功能非常简，只提出最多1空间参考；L形或换菇材本身不增加有效数。',
'与本批F01同属封闭单室侧炉/烟囱意向，长短、双炉、原木代菇盖不自动构成独立家族；且066小冷室与原已研究单室群接近。虽无精确指纹重复，当前缺少足够独立空间语义，保守0，不强行凑数。']
bindings=[bind(next((ROOT/'docs/architecture').glob(f'research-*smithy-{n}/manual-review.json')))for n in ['056','059','060','066','067']]
cases=[]
for a,o,c,credit in zip(sources,obs,comparisons,[1,1,0]):
 cases.append({**a,'observations':o,'images_actually_viewed':[bind(p)for p in sorted(OUT.glob(a['id']+'-*.png'))],'whole_boundary':'原完整源体包含基础、室内、围护、屋盖与工作位；F01/F02全体积记录，F03稀疏不虚填air；empty入口未见必需外接房翼。原生碰撞/排烟/运行未验。','semantic_family_comparison':{'comparison':c,'saved_existing_judgments_reused_not_reaccepted':bindings,'proposal_maximum':credit},'credit_proposal_maximum':credit,'formal_credit_added':0,'status':'PENDING_INDEPENDENT_SCOPE_AND_FAMILY_ADMISSION'if credit else 'HELD_ZERO_FAMILY_INDEPENDENCE_UNPROVEN','native_acceptance':False})
put('manual-review.json',{'cases':cases,'source_bodies_studied':3,'whole_smithy_bodies_studied':3,'actual_current_images_viewed':20,'manual_observations':21,'pending_maximum':2,'held_zero':['F03'],'formal_credit_added':0,'no_independent_self_admission':True})
put('source-context-reading.json',{'metadata':'同一固定RepurposedStructures7.1.19+1.20.1-forge，TelepathicGrunt，LGPLv3声明，完整metadata/credits保留；不复制原建筑到产品。','house_entries':'三源各weight2/rigid/legacy single；菇林两源actual processor general_randomizer，山地源actual mossify。','roots':'菇林size8、山地size6，二者WORLD_SURFACE_WG/startheight0/beardthin；是原村参数，未运行地形/生成。','mushroom_processor':'general_randomizer先red_mushroom .33→brown/.33→air；紫/品红candle各3条.3规则输出3/2/1 candles且littrue，再force_place_mushroom_blocks自定义processor。不是逐栋随机屋形，不给额外信用；未检查其Java实现/运行。','mountain_processor':'mossify五规则沿用已读当前JSON：cobble/stone/stonebricks/mossywall的概率替换，非改变空间布局。','extra_context':'crop/path/weak_goldify是同村池其他条目上下文，不伪装当前房屋使用；未声称逐条阅读全部不相关规则。','connectors':'全为empty入口，无外接实体/房翼；原源entities0，无loot或NPC行为凭空补入。','biome_collections':biomes,'native_acceptance':False})
put('applicable-principles.json',{'principles':['室内台面和炉服务面的净空比装饰烟囱数量更重要；实炉记录不证明排烟或加工运行。','连续L冷加工长室与冷热/储藏分区的L铺按功能和路线比较，不能仅凭轮廓。','同一封闭单室只变长度、炉数或材料时保守不增加家族信用。','适用1000完整不同建筑参考与独立验收前不制作；学习比例与动线，不移植原建筑。'],'implemented_product':False})
put('task-scope-boundary.json',{'target':'COD3 NPC01 老陈 山脚铁匠铺空间研究','original_line':1122,'implemented':False,'outstanding':['适用1000完整不同建筑参考与独立复核','原创建筑','材料/前置/付款/获取回执','中文指南针','昼夜雨险/水锤世界状态','原生最终验收'],'COD4_ledger':{'accepted':153,'target':1000,'gap':847,'increment':0},'masterlist_deletions':0,'cod5_missing_not_invented':True})
put('session.json',{'batch':68,'status':'MANUAL_STUDY_COMPLETE_VERIFICATION_PENDING','source_bodies_studied':3,'actual_images_viewed':20,'pending_maximum':2,'held_zero':['F03'],'formal_credit_added':0,'cumulative_not_reset':True,'java_run':False,'product_files_written':False,'masterlists_edited':False,'native_acceptance':False,'all_tasks_complete':False,'next':'继续真正未研究且用途相近的完整smithy源；同体换材和职业家具替换保留0。'})
print('Saved21 observations/20 viewed PNG/2 pending/1 held0/formal0')
