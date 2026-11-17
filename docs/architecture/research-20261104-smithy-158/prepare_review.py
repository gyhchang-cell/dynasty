"""Save actual whole-house reading; no production assets or masterlist edits."""
import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent; R=P.parents[2]; prev=P.parent/'research-20261104-smithy-157'
assert not (P/'RECEIPT.json').exists()
def get(p):return json.loads(p.read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 b=p.read_bytes();return {'path':str(p.resolve()),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
d=get(P/'raw-source-audit.json')['candidates'][0]; nb=d['nbt_decoded_original']; c=get(P/'source-context.json')['candidates'][0]
pool=next(x for x in c['contexts']if x['member'].endswith('/houses/regular.json')); root=c['contexts'][0]['json']
obs={
'layout':'一栋10×10×5窄长工住屋：西侧x0..4、z0..4封闭两层体，底内3×3储备/备料小室，上方同占地单床住屋；东侧x5..9为露天分级工作服务台、街边低位熏炉。唯一普通门在上层，内梯向下进入低室；不是底商双门加上宅的常规分铺。完整46palette、10原状态层、8BE、entities[]及8PNG实际读看，一整屋最多1仅COD3 NPC01用途相关研究待Main，不作为实际铁匠炉铺或NPC05风车。',
'proportion':'DV3578，完整500位置=296非air+204显式air，零省略。西体外5×5、内3×3，floor0/use1低室与floor4/use5住室；东台高差延展至x9，尺寸10宽不等于室内10宽。上檐y8、单脊y9，10高不是10层。底层低室净空主要y1..3，局部挂链/墙炬/家具侵入；未认证全室NPC碰撞。',
'facade':'主墙quartz_bricks171；分类图把含brick的白石英画作红褐色，这是通用分类错误，不是原作红砖墙。实际红砖14/brickslab27主要屋顶，cyanpane8分布两层窗。唯一普通门4,5/6,1为east/left/closed，上门外5,5/6,1显式air；低墙4,1,2是poweredtrue/openBOTTOM铁活板门，非普通首层出入口。其外5,1,2cobweb、6,1,2air、7,1,2quartz，不宣称低层完全无法进入或有安全通路。',
'roof':'西窄住屋y8砖屋面、两侧BOTTOM半砖挑檐，y9只z2长脊；覆盖西主体并向x5挑出，上门外5,7,1挂灯。东侧大部分y4以上显式air，只有低台花叶及细墙柱，不能当另一完整房屋/上层露台或把相邻工作台拆成第二建筑。屋面与挑檐的完整原状态已逐层核对，不以普通双坡红屋顶单独取得新信用。',
'materials':'低室blueice3,1,1、strippedmangrovelog1,1,3、redglazed1,2,1与铁/木活板门形成冷藏备料陈设线索，未证实制冷/加工机制。外箱5,3,1 east/single/dry，原butcher loot/seed-279175316891865267，非已发奖励。外低熏炉8,1,4east/unlit，BurnTime/CookTime/CookTimeTotal0、Items[]/RecipesUsed{}；东前9,1,4air、脚下9,0,4doubleandesiteslab，上8,2,4andesitewall，不写燃烧排烟已验。上层一张灰床1,5,2foot与1,5,3headsouth，两个空白双面birch墙牌1/3,5,1；不虚构中文招牌、第二床或NPC原实体。',
'circulation':'内梯3,y1..4,z3 west/dry贯穿上楼板角孔，梯上3,5/6,3air；上卧室侧邻原木地面，支持住屋下到低储室的关系研究，未运行碰撞/寻路。东外街阶9,1,3→9,2,2 BOTTOMnorth birch及9,2,1 TOPsouth落脚，内段5,3,3→5,4,2 BOTTOMnorth→5,4,1 TOPsouth临上门；两段之间有箱5,3,1、open trapdoor7,3,1、closedTOP铁板6,2,2及异向石英阶，不能描述为连续直梯或已验全程通行。上房2,5,1 birch stair为低家具，不是再上一层的楼梯。街socket9,1,2最终为TOPsouth birch stair，NPCsocket9,3,1最终air；仅原始装配意图，未放置村民/交易或验中文版指南针。',
'terrain_and_dedup':'固定T&T mediterranean regular池精确选中med_butcher_1权1legacy/rigid、street_mediterranean处理器，root size3/max116/start0/WORLD_SURFACE_WG/beardthin/expansiontrue。五完整JSON实际读：root、19项regular池、单项single中心池、10optional biome、processor；19房名/10biome不是19/10建筑参考。处理器三个顺序randomblockmatch andesite_slab .25→cobble/crackedstonebricks/stonebricks，不凭其推定实机各25%或原double半砖运行后地形。单Jar缺butcherloot/savannavillager池非全环境缺。旧070F02、071F01、087F02、095F02完整七观察及原比较实际读，原历史状态不变/旧图未重看。当前整屋差异是上唯一普通入口—内梯向下冷备室—外分级作业台与低街热端的整体关系，职业/色彩/单个冰块不单独计数；同为工下住上家族，Main可判重复0。'
}
comparisons=get(P/'pre-render-spatial-comparison.json')['cases']
texts=[
'070F02旧savanna armorer为北地面热工/南抬起双床住屋、西外折阶与通屋顶活板内梯；当前同一窄西体上卧下冷备且唯一普通门在上层，东外分级服务台和低街熏炉，不把内梯等同屋顶梯。',
'071F01旧cherry armorer两个西首层门通下工厅，东内直四阶上三床层；当前无下层普通门，上门进入单床后用角内梯下冷室，主要外工作端分离在低东台。',
'087F02同地域白石英红顶不可当差异。旧fletcher/toolsmith南北下层两独立铺、两下门、东单直四阶上南双床宅；当前单西体上门下内梯到低冷室，东分级开放台与低街热端，非原双铺换职业。',
'095F02旧forest stonemason西低地石作火棚、低封闭卧室内长梯上西砧厅再向东独立酿造室/南卧室；当前小型上卧下冷备单体与露天高差台，不是低宅上砧厅或相同多室工作路。'
]
for old,t in zip(comparisons,texts):old['current_complete_comparison']=t
rv={'id':'F01','source_stats':[3578,500,500,296,204,46,0],'expected_counts':d['material_counts'],'expected_states':get(P/'queried-original-states.json')['states'],'expected_block_entities':[{'pos':b['pos'],'nbt':b['nbt']}for b in nb['blocks']if 'nbt'in b],'selected_pool_member':pool['member'],'selected':[e for e in pool['json']['elements']if e['element'].get('location')==c['location']],'root_fields':root,'viewed':['whole','cutaway','vertical','y0','y2','y4','y6','y8'],'observations':obs,'written_comparisons':comparisons,'full_study':True,'credit_proposal_maximum':1,'target':'COD3 NPC01 老陈 山脚铁匠铺相关工住空间','context_reading':'五完整JSON实际读；regular池而非houses.json，处理器已读未运行；0原实体，8BE全文读，缺项仅单Jar语境。'}
status='ONE_COMPLETE_UPPER_ENTRY_DOWN_LADDER_COLD_ROOM_WHOLE_STUDY_PENDING_MAIN'
put('review-config.json',{'batch':158,'history_pairs':get(P/'pre-render-history-screen.json')['history_unique_archive_member_pairs'],'status':status,'scope':'COD3 NPC01 related workshop/living whole spatial study only; not NPC05/COD4','cases':[rv],'image_counts':[8,8,0],'pre_render_spatial_comparison':bind(P/'pre-render-spatial-comparison.json'),'limits':'原图为全方块近似分类色，非贴图/碰撞；白石英错误分类红褐，原状态为准。全部500位置原层读、46palette/8BE/0entities、8PNG；无游戏/Java/生产/主清单。当前max1待独立判定，156/157 NPC05提案沿用待审不重送，153已first156接受仅carry0，COD4维持153差847。','next':'从固定本地源继续相关整栋原始研究与语义去重；1000不足不制作，不重放旧收据。','handoff':'158 T&T med_butcher_1整屋研究：西窄上单床住屋唯一普通上门→角内梯向下低冷备室；东外分级工作服务台/街边低熏炉。500位置296非air204air、46palette/10原层/8BE/0entities/8PNG均实际读看，四旧完整七观察及原比较保留。最多1仅COD3 NPC01待Main，非NPC05或COD4增量；路线/炉/processor/native未运行。153 first156接受只carry0，156/157mill pending不重复提交；无Java、生产、主清单删除。'})
put('latest-independent-admissions.json',get(prev/'latest-independent-admissions.json'))
put('task-scope-boundary.json',get(R/'docs/architecture/research-20261104-smithy-155/task-scope-boundary.json'))
print('Prepared158 actual full house reading: 8 viewed, 1 pending NPC01, no formal credit')
