"""Human source/visual review record; no pixels or live game state changed."""
from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent; R=D.parents[2]
P=R/'docs/art/armor-historic-compact-reference-20261104'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    pages=['icons-01.png','worn-01.png','worn-02.png','worn-03.png']
    review={
      'scope':'D23既有三套的完整静态对应关系加深，不新增名称或设计信用',
      'pages_actually_reopened':[{'path':str((P/p).relative_to(R)),'sha256':sha(P/p)} for p in pages],
      'observations':[
        {'family':'holy_armor','source_material':'HOLY','slots':4,'grid':[128,128],
         'visual':'四件图标用暖金主带、银白板片和深灰内衬保持同套辨识；盔翼、胸肩金线与靴侧白翼是大轮廓识别点，而不是满幅细纹。图集也使用这三类主材，白金不是孤立图标配色。',
         'binding':'本套4槽，胸甲有普通/细臂两种layer supplier；其余3槽固定普通图集。5个几何方法对应128×128图集，不能套64×32标准甲UV。',
         'uv_geometry':'头6、胸普通32/细臂32、腿7、脚10个原始addBox调用；胸有chestCore、chestBack、胸前效果片、肘甲和翅片，靴也有翼片。共享template只有空节点，所以这些片来自专用槽模型。调用数不是最终可见体块数。',
         'application':'Dynasty神圣感优先保留原版比例，用金色主带与白色甲面的大分区；不能因16px图标紧凑便照搬专用模型大量悬浮效果。hongmeng图标已认可，先做穿戴材质与图标对应，不能重画图标或复制本甲纹样。',
         'independent_credit_delta':0},
        {'family':'japanese_light_armor','source_material':'JAPANESE_LIGHT','slots':4,'grid':[64,32],
         'visual':'图标以米色绑带、暗褐皮革与浅褐甲片组成，胸甲横向条带、头带后结、腿部护片、靴长筒分别有用途轮廓；不是四件同形换色。普通/细臂图集均保留相同主材，不构成两套独立设计。',
         'binding':'胸甲才选择细臂图集；头、腿、靴普通图集。64×32只是图集尺寸，头带、结和0.01厚飘带、外侧腿片均是自定义UV。',
         'uv_geometry':'普通胸主体8×12×4，双臂4×12×4；细臂3×12×4并加独立breast。护臂有2×5×5的独立覆盖块，腿片2×5×4，脚模型主体4×12×4，不能由boots文件名推定只画最下面几行。镜像与旋转仍需实际模型验收。',
         'application':'bamboo/cloth/leather/sea_silk/brocade袖口按目标长短袖和真实甲UV决定，不能把空终端一律补满或将外部图集当透明遮罩。米色带、褐甲大条带是可借鉴的材质组织方法；不复制纹样。',
         'independent_credit_delta':0},
        {'family':'centurion_armor','source_material':'CENTURION','slots':4,'grid':[128,64],
         'visual':'红冠羽、金色盔面与腿裙、深褐胸身、斜金带组合成职业剪影；胸甲不是大块金属正面填满。图集中大红褐片与金带同图标一致。',
         'binding':'四槽绑定材料CENTURION及centurion模型；本地源中文却为食神头盔/铠甲/护腿/护靴。作为译名与原名不一致的反例，不据中文虚构厨师玩法或再算一个主题设计。',
         'uv_geometry':'普通胸有body三组调用、独立chestBelt与左右肩件；细臂15调用而普通12，仍是同一套适配。头部jow使用0×3×6平面，在uv=[75,-4]的帽面出现零宽负v矩形，不能当真实缺图。',
         'application':'Dynasty同名材料以图标和实际功能识别，先固定主材、腰带方向与四件一致的亮部；衣服甲片边界要能读作甲片，不用亮线填满。盔甲显示名称不足以证明材料/模型绑定。',
         'independent_credit_delta':0}
      ],
      'source_chain_findings':[
        'ItemRegistry构造器40条注册传入实际材料枚举与HELMET/CHESTPLATE/LEGGINGS/BOOTS；Forge工厂用type.getSlot().getName拼head/chest/legs/feet，并由捕获supplier实例化ForgeHumanoidArmorItem。',
        'HumanoidArmorItem以相同键查ModelProviderRegistry；registry的具体bootstrap直接指向构造器与normal/slim layer方法，不能由目录名猜。exalted_aurum_armor的模型目录实际为exalted_aurum。',
        'provider的正常纹理模板是textures/models/armor/{name}.png；Mixed才有{name}_slim.png。create4参数与create5参数对应不同provider，不能看到两图就假设所有槽切换。',
        'isSlim优先本地偏好配置，再按未忽略的同步映射选择，最后才回退皮肤模型。CommonClass加载配置并用同步处理更新映射，不改用户当前偏好。',
        '客户端registerLayerDefinitions对普通provider注册普通layer，对Mixed另注册细臂layer；静态源码证明声明路径，不证明当前运行实例无其他mod覆盖。',
        'ArmorModel.templateLayerDefinition只有head/hat/body/arms/legs空节点与pose，没有可隐含套用的原版实体方块。',
        'CubeDefinition使用原始dims与UV，inflate改变顶点而非UV；ModelPart的六面公式用于本批范围分析。小数和零厚几何不能用整数包围框直接判可见面积。',
        'HOLY/JAPANESE_LIGHT/CENTURION材料读AOTAConfig的耐久、防御等字段；本批未读取当前游戏配置/获取配方，不依据艺术主题推断实际强度阶段。'
      ],
      'raw_uv_flags':{
        'count':6,'confirmed_live_defects':0,
        'degenerate_zero_width_caps':{'count':4,'family':'centurion_armor','offsets':[204,228],'faces':['DOWN','UP'],'rect':[81,-4,81,2],'finding':'零宽面原始范围为负v；正面积侧面起于v=2。不据此报缺图，不改外部作者资产。'},
        'fractional_thin_ribbon':{'count':2,'family':'japanese_light_armor','offset':168,'uv':[60,0],'dimensions':[2,9,0.01],'finding':'原始UP/SOUTH右边界约64.01/64.02；是需区别处理的小数薄片边缘。包围框越界不等于已证可见采样问题，实际材质采样/可见性未验。'}},
      'dedup_decision':{'new_names':0,'new_learning_groups':0,'new_independent_design_credit':0,'normal_slim_split_credit':0,'slot_or_call_count_credit':0,'prior_ledger_unchanged':True},
      'remaining':['其余7套仅静态绑定路径读到，几何UV未在本批逐套读完','三套实际穿戴、多角度、接缝、遮挡和动画验收仍未做','1000个适用完整独立设计仍未达；不得提前制作','Dynasty五套袖口、五套旧L2、三套材质问题继续待制作；保护认可图标'],
      'new_artwork':0,'production_changes':0,'game_starts':0,'checklist_deletions':0,'reference_gate_met':False
    }
    (D/'manual-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
    print('Saved three complete-set correspondence reviews; zero additional design credit.')
if __name__=='__main__':main()
