# D85：魔力布法袍四槽消费与逐面UV补核

本批补D34已经看过的Botania魔力布套装，不把重看同套算新参考。开襟袍学习组已存在；新增独立设计信用0、1000已验适用总数和缺口仍未知，制作门槛未满足。未改游戏资源、身体模型、共享Jar、主清单或session。

## 适用范围和固定来源

布甲、锦缎、海蚕丝甲的未验缺口包括图标/穿戴材料一致性、长布区与接缝判断。魔力布只能提供布片分区和专用UV消费对照，不证明项目旧稿简陋，也不授权给其增加长袍/肩块。当前70priority未确认有ID同时属于未做过且简陋。保留全部已认可精致稿。

官方VazkiiMods/Botania固定提交0c06dcf7ae9555d52885f913ecd769ceb94fa823，复用D34固定commit/tree，逐份重新验证21份选择来源的Git blob与SHA256；新取得12份同提交源码/配方/声明，亦逐份验证。gradle.properties声明MC1.20.1/build457；Forge/build.gradle第47行声明1.20.1-47.1.3。完整源码归档只用于机器查找初始化调用者，1098 Java文件扫描不等于实际逐个阅读、更不等于1098参考。

## 实际看图与新发现

重新查看四张16方图标及64×128穿戴原图（共5PNG），最近邻原图页和102个原UV矩形两页全部看过。青色兜帽包住深色脸口，短宽胸配横带和中间扣列，裤图标表现为长下摆两片，靴为低亮暗青双靴。长衣料以少量竖亮折边、深下摆和简洁横带区分区域；图标窄碎亮格偏多，只借大区层次，不复制满图细纹。不能为统一普通甲比例误删本套长布结构；也不能将这套长布结构强加到Dynasty已认可普通甲。

准确逐面提取17个源方块、102个原UV矩形，均落在64×128内。4个2×2根方块（head、body、left_arm、right_arm）各六面全透明；它们是有几何声明但无可见像素的根，不应变成4个装饰件或新设计。6个空根无addBox，完全不计方块。兜帽正面留下透明脸窗，图标里的深脸口却是主体像素，二者不能混为背景删除。

胸部上下片分岛，胸前扣列与背部大色块有区别；袖中段为深青大面，肩片为较亮短块。左右两条裙片各5×13×6，分别绕Y ±10度、Z ±15度，父级依附对应腿，不能按普通裤图集剪掉长片。双靴自身5×4×5，仅占下腿末端，和上方短腿衬块分开。左右部分镜像、原点、局部姿态及左右袖/肩膨胀参数不完全一致，均按源码保留；没有为了强制对称修正外部作者源码。原始裁片不等于最终旋转、镜像顶点朝向、接缝或姿态验收。

## 模型与纹理消费证据

完整阅读ManaweaveRobeModel、ArmorModel、ArmorModels、ManaweaveArmorItem、ManaweaveHelmItem和Forge ItemManasteelArmorForgeMixin。Manaweave继承ManasteelArmorItem，getArmorTexture先看PhantomInk，非隐形时经getArmorTextureAfterInk选择默认或节日图；本批只看默认非节日无Ink状态，节日/隐形均不计新设计。四槽共享botania:textures/model/armor_manaweave.png，不是普通layer1/2两图。

BotaniaLayerDefinitions36–37将inside/outside分别建成64×128层；ArmorModels按LEGS选择inside，其余槽outside，并按物品实际equipmentSlot返回模型。ArmorModel.renderToBuffer设置该槽可见根后渲染；setupAnim含普通实体与盔甲架两条姿态路径，仅阅读，未运行。

本批找到此前未闭合的初始化调用者：ForgeClientInitializer注册层定义及实体渲染器，EntityRenderers.registerEntityRenderers注册DOPPLEGANGER的GaiaGuardianRenderer工厂；该渲染器构造器调用ArmorModels.init(ctx)，再逐槽bakeLayer。这里只阅读构造器及注册入口，不处理Boss身体或战斗。Forge客户端mixin声明列出ItemManasteelArmorForgeMixin，initializeClient回调返回ArmorModels.get；源码声明链已读通，Mixin实际应用、事件执行和已加载模型尚未运行验证。

## 原生物品和获取范围

BotaniaItems225–228四条及LibItemNames187–190确认原生四ID；四item JSON均引用对应默认PNG，只有holiday谓词分支，未当变体计数。四件标准合成配方使用botania:manaweave_cloth；cloth配方由4份botania:mana_string合成，配方已完整阅读。mana_string上游原生获取、真实合成支付回执和任务衔接未验证，不能称完整获取链完成。

## 去重与待验

实际阅读既有immersive_robe_open_front组全部五条存储观察，D34README和相关模型记录；未重新查看其余四项目全部旧PNG。本套历史botania:manaweave仍同一设计；只补专用17方块/102面与初始化来源证据，不能以模型根、裁片、两页、节日状态或新批次计数。

MC ModelPart UV算式使用既有同MC1.20.1的Forge47.4.10映射源码；精确Forge47.1.3官方源码归档已在D83校验，可复用客户端扩展hook定义，但不冒称47.1.3已加载Minecraft二进制。符号UP V、局部角度、镜像标记保留；最终世界正侧背45度、纯黑剪影、接缝、走动裙摆和真实穿戴未验。所有参考源均不复制进Dynasty。
