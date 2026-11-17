# D83：Sanguine四槽甲原图、分槽消费者与面UV研究

本轮为来源研究，不制作或覆盖Dynasty资源，不运行Java/游戏、不改共享Jar/实例/主清单/session。正式新增设计信用0，最多一个未独立验收的整体来源候选；不是31源码、6图片、4槽或84面独立设计。

## 当前目标资格与用途

复核D72/D73的七家族28个ID、70优先文件和289保护基线。目前没有证据能把其中某个ID同时判定为“未改过且简陋”。布、皮、海蚕丝的旧版本不等于未制作；其余已重做图标也不得因穿戴待验而重新设计。target-qualification保存原状态文件及SHA，确认本轮没有指定可重画ID。

本参考对朱砂甲的红色材质主次、图标与穿戴分区一致性有局部用途；对鸿蒙高级甲仅用于研究“原版盔甲主壳加独立少量特征”的结构边界。不是布/皮/海蚕丝专项证据，不给其材料设计信用；不把Sanguine有机材料/角饰复制进这些已认可资产。

## 固定来源和依赖

官方仓库 https://github.com/team-abnormals/caverns-and-chasms ，1.20.x分支固定提交 `f4cafc50ccac49f50e281ecdaa1bef9c1765dfbb`。1.20.1分支查询404，实际API分支名是1.20.x。commit-api的root tree `23e60805a0e64bf4517cc47931391e7dd294e248` 与固定commit树条目一致。31份选取源码/资源按Git blob与SHA256验证；数量不是美术语义信用。

gradle.properties声明MC1.20.1、Forge47.1.3、Blueprint7.1.3、mod2.1.3。精确版本Forge sources.jar来自官方Maven，服务端SHA1核对；Blueprint精确版本sources.jar来自官方Maven HTTPS并保存本地SHA256，但其.sha1请求403，不能声称已独立核对上游摘要。归档、提取项和限制在consumer-provenance。

复用D73同MC1.20.1/Forge47.4.10映射源码的HumanoidModel、HumanoidArmorModel、ModelPart、LayerDefinitions及HumanoidArmorLayer作为几何/面UV上下文，保存旧路径与哈希。Forge47.1.3补丁独立读取并追踪关键钩子；这并不等于加载过精确二进制或验证版本运行兼容。

## 实际查看的6张原PNG

四张图标16×16，两张穿戴图64×32。original-image-paths记录原路径、尺寸、RGBA透明度和SHA256；原图未缩改。native-icons/native-worn-layers是原像素整数最近邻研究页，非游戏、非Dynasty成稿。另下载的trim sanguine_leggings.PNG没有作为默认甲图研究或计数。

- 暗红/酒红主体，较亮的灰粉红在大面中心，深红沿边与凹口，使用离散像素面而不是柔光渐变。图标中胸甲短宽、两条裤腿平直，靴向外阶梯并保留腿间透明间隔。
- 头图标额中间向下的小折面、两侧向上角和两侧暗眼区建立身份；头部并不是普通倒U露面头盔，面区的暗实体像素不能当背景删掉。
- 胸上缘的两尖角甚至触及图标顶边，不能照搬为Dynasty普通甲的边距/肩宽规范；盔角高、肩角上挑也是比例反例。仅借鉴角饰与原版主体分开、主面红块和暗连接的层次。
- L1头面有分叉眉和暗凹口、胸前中心竖区与胸背不同的大暗红分面，侧袖以几条横带分材质。L2只有腰胯和腿部区域，图集上方为空并不表示缺头：该层用于腿槽。
- 原图较多小红灰块会在暗处挤成一团，不能把细密层次照搬成普通布甲；遵守用户大像素簇标准，只学大面和关节暗区关系。

## 真正穿戴消费链

CCItems201–204四工厂明确SANGUINE材质及四个ArmorItem.Type；CCItems200同时注册living_flesh基础材料。CavernsAndChasms.REGISTRY_HELPER以本MOD_ID创建；Blueprint ItemSubRegistryHelper构造器为parent.getModId建立DeferredRegister，createItem(name,supplier)调用其register；RegistryHelper.register遍历子helper，AbstractSubRegistryHelper.register接入eventBus。这是静态方法链，事件加载/原生物品实际注册仍未运行。

CCTiers材料用BlueprintArmorMaterial(location("sanguine"))；精确版本helper的getName返回ResourceLocation.toString，得到caverns_and_chasms:sanguine。SanguineArmorItem没有getArmorTexture覆盖；Forge47.1.3 HumanoidArmorLayer补丁按material.getName拆namespace，再按usesInnerModel选层号，物品回调无覆盖时使用默认路径。因此默认未纹饰栈：HEAD/CHEST/FEET选sanguine_layer_1，LEGS选sanguine_layer_2。

SanguineArmorItem.initializeClient返回扩展，getHumanoidArmorModel仅HEAD/CHEST返回SanguineArmorModel.INSTANCE；LEGS/FEET返回传入properties。INSTANCE由createLayerDefinition(OUTER_ARMOR_DEFORMATION).bakeRoot直接构造，没有在CCModelLayers中猜一个不存在的Sanguine注册层。模型从HumanoidArmorModel标准mesh继承主体，再向head加左右两角、两arm各加一肩角；全部为cuboid，不是新身体模型。

精确Forge47.1.3扩展getGenericArmorModel在replacement!=original时调用ForgeHooksClient.copyModelProperties，转移根姿态和可见性。默认slot显隐上下文为HEAD:head/hat；CHEST:body/arms；LEGS:body/legs；FEET:legs。模型共享单例在最终动作和渲染顺序中的表现尚未实测。

HumanoidArmorLayerMixin明确包含Sanguine trim追加分支，也处理Cowl/Mime/药水等其他情况；本轮只读其1–164的相关段落及声明，不宣称全部Mixin已阅读或注入成功。四图标各10个trim predicate引用已读，trim实际像素与渲染未研究，不计40个设计。默认未纹饰范围与trim验收分开。

四张原生配方都用living_flesh标准盔/胸/裤/靴网格，输出准确四ID。配方声明已看；材料原生来源、合成加载和实际获取仍待验，不以别的基础物品代替。

## 面UV具体结果

slot-face-uv逐槽保存原点、标称尺寸、膨胀、parent offset、mirror与带符号UP面UV。四新增方块：头角2×5×2，UV(0,0)/(24,0)；肩角2×3×2，UV(32,0)/(56,0)。头角膨胀(.25,.625,.25)、肩角(.5,.25,.5)，由外层deformation1代入源码比例。主壳、帽壳及腿沿用MC源上下文；标称尺寸控制UV，膨胀不增加UV面积。

按四槽分工共有14个cube实例、84个原始面矩形，全部处于64×32内：HEAD24面、CHEST30面、LEGS18面、FEET12面。它们包含复用左右臂腿及完全透明帽壳，绝不是84个新设计。帽壳六面全透明；四角使用原布局未使用的窄图区，不能因为同属图集上方就判断贴到帽面。L1头DOWN/y_min盖面有红主材，UP/y_max区域中间透明；源方向标签保留，不颠倒成世界“头顶/下巴”结论。

raw-slot-face-crops已经逐行查看：头正面分叉中心、两侧横带、背面横深带；胸前的竖亮区与背中大暗片不同，袖口横带，L2腰带与腿前明暗相接，靴只在下段有实体像素。裁片保留原矩形方向，未模拟UP顶点绕序、镜像UV与最终pose，不能据此宣称镜像/接缝正确。无软件穿戴图替代游戏五视角。

## 旧whole去重和保留

全部旧30个pending whole键与1个模块整体对照已保存；215历史学习组名、640case注册继续复用。最接近的旧肉肋甲、有机骨肉甲、暗红肋胸、角面罩、龙鳞和红甲套件观察完整保存于historical-group-comparison。它们已有V胸、分叉眉、两角和暗红主材；本套独立角块与默认原版主体的具体实现差异，不能直接证明独立语义。

仅追加最多一个未独立验收的完整来源候选，正式0，旧分组/case/D54已验整体完整保留，1000总数/精确缺口仍未知且gate=false。

## 待验和保护

- 独立适用性和完整旧whole/学习族语义验收；目标仍旧简陋未获认可的资格未成立。
- Blueprint归档上游checksum403、实际加载二进制/事件/Mixin；trim和native stack、材料来源与获取。
- 精确47.1.3加载模型、最终面方向/镜像/接缝、动作、正面/45度/侧/背/灰模和黑剪影实机。

289保护/70优先哈希未变；原图未改，要求全文及哈希另存本轮。未删任何未验提示词。
