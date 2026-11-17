"""D26 observed whole designs, native atlases, conservative semantic exclusions."""
from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 pages=[f'icons-{i:02}.png' for i in range(1,7)]+[f'worn-{i:02}.png' for i in range(1,4)]+[f'jinghui-{f}-assembly.png' for f in 'blk fxt hlp lb qn yangjian'.split()]
 rows=[
 ('organic_aquatic_horned_plate',['blk'],'白龙甲以白/青鳞面、红小嵌件、淡金腰边作主次，角盔、三层外伸肩、分片裙在正背和黑剪影均清楚；侧面肩甲和帽角远超躯干，不能作为原版甲比例。腿图不是普通裤轮廓，靴图包含红宝石和青白护片。227体块、512图集对256网格。','可借鉴大白面与小红焦点、背面与正面一致的材质；不照搬巨肩、角冠或细格鳞纹。已有水生角甲族覆盖，名称、红色变化或体块数都不加独立信用。'),
 ('divine_ornate_gold',['fxt'],'凤兮火袍的金红展开冠、白羽肩穗、交领上衣、红分裙、长弧背饰与细长尾带构成同套礼服；正背红裙呼应，侧面弧背饰突出，头胸间空白是全套静态组装不含人体。原图高分辨率渲染，不能视为粗像素图标范本。141体块、512对256网格。','只学习金框/红布/浅羽三大材料区和交领连续，不搬细穗、弧饰或大冠；现有神圣金装饰组追加，不把凤凰题材、火光或四槽当新组。'),
 ('samurai_plate_variants_conservative',['hlp','lb'],'黑龙袍用暗黑交领、龙形肩、红腰带与双前绶条；背面几乎纯黑，侧面有长黑尾样突出，暗部容易糊在一起。无双用红黑层叠肩/裙、青绿胸腰嵌件、金腰和极长红双翎，正背黑剪影都明显超宽；不能因冠翎/肩饰/裙片拆成多套。两者163/237体块，图集512/256、网格256/128均2倍密度。','可取黑红面积比和腰部小块金色支撑识别，保留深衬而非全黑；避免原版甲套用巨大双翎、肩宽和细碎面。与既有中式片甲族保守合并，不因黑龙/无双名称另计。'),
 ('ninja_cloth_cowl',['qn'],'潜匿为低黑斗笠与青绿挂绳、深蓝分片上衣、亮青绿腰结、黑长裤靴；侧面可见多把鞘/挂刃，背面V形蓝甲和红腰带。胸图内的侧挂武器不是额外护甲设计。205体块，512对256网格。','只借深布底与局部蓝绿边识别轻装；黑裤黑靴大矩形和高饱和小线属于反例，不直接照抄。斗笠/刀鞘并不让已有隐匿布装变成多套独立设计。'),
 ('priest_white_gold_cloth',['yangjian'],'清源妙道为细金高冠、白开襟袍、灰锁甲内层、铜袖口、绿色小胸坠和金纹靴；背面白短披片覆灰甲裙，与正面开襟形成层次。171体块、256对128网格。金冠细杈和密链纹过细，不适合原版甲直接沿用。','可取白袍/灰内甲/铜袖口三大块材质分离，腰下衣摆须按目标用途保留；不能统一清掉旧L2。与已有白金祭司布装族合并，不以神名或绿色点缀新增信用。')]
 observations=[{'semantic_group':g,'prior_group':g,'cases':['jinghui:'+x for x in cases],'credit':'APPEND_TO_PRIOR_GROUP_ZERO_NEW_DESIGNS','observation':obs,'application':app} for g,cases,obs,app in rows]
 out={'scope':'六套此前未读礼装/战甲原图、几何和四槽声明的只读研究；不是资产制作或实机验收',
 'pages_actually_viewed':[{'path':p,'sha256':sha(D/p)} for p in pages],'observations':observations,
 'native_bindings':{'names':6,'item_models':24,'item_icons':24,'native_atlases':6,'geo_models':6,'animations':6,'native_classes':31,'reused_geckolib_classes':2,'four_slot_chains':24,'geometry_cubes_read':1144,'software_assembly_sheets':6},
 'root_followup':'原统计取最近的armor前缀名称，不能代替渲染器的八个指定根。按真实parent链重算：凤兮armorBody2→armorBody、armorRightLeg2→armorLeftLeg、armorLeftBoo→armorLeftBoot、armorLeftBoo2→armorRightBoot；无双armorRightArm2→armorLeftArm；潜匿armorRightLeg2→armorRightLeg。24槽都存在预期根及其后代体块，未改外部模型，也不称游戏bug。详见binding-study每槽后代数。',
 'dedup_limits':['六套名称、24槽、1144体块、五视角和图集2倍密度不算独立设计','全部追加既有五类，新增学习组0；已验完整独立总数仍未知，不能以629名称冒充629个有效设计','无双与黑龙细节不同但保守合并片甲族，不重复算材质/装饰变化'],
 'runtime_limits':['软件全套组装不包含玩家，不证明实际每槽可见性、动画、行走、采样或接缝','固定GeckoLib4.8.4类仅解读上下文，未假定外部整合包实际版本','D2袖口、旧L2和材质对应仍待门槛及制作验收'],
 'new_names':6,'new_learning_groups':0,'new_validated_independent_design_credit':0,'new_artwork':0,'production_changes':0,'game_starts':0,'checklist_deletions':0,'reference_gate_met':False}
 (D/'semantic-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 print('D26: six whole-source cases reviewed, conservative append only; no production or runtime acceptance.')
if __name__=='__main__':main()
