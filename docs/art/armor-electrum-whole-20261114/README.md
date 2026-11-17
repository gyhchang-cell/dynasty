# D80 Electrum：完整四槽、专用64×64穿戴图研究

本批是盔甲贴图／UV来源研究，不是新美术制作或游戏验收。实际查看4张原生16×16图标、1张直接引用的64×64实体护甲图，另看3张旧默认路径图作为非活动上下文。不把8PNG、13体块、四槽或trim变体拆算设计。

核心交付入口：`coordinator-delivery.json`；五张直接引用原图和三张上下文原图的绝对路径、SHA256、分辨率见 `original-image-paths.json`，简短路径表见 `original-image-paths.txt`。`native-icons.png`、`active-native-atlas.png`、`inactive-default-path-context.png`是原像素最近邻放大，非游戏图。

## 固定来源与实际绑定

官方 [TeamGalena/oreganized](https://github.com/TeamGalena/oreganized/tree/51cc3d88878e23cda7c4993a860e32cb1df3a5a4)，分支main/1.20.x、固定提交 `51cc3d88878e23cda7c4993a860e32cb1df3a5a4`。API提交与未截断Git树、全部下载文件的Git blob/SHA256在provenance.json。gradle.properties为MC1.20.1、Forge47.3.10，mods.toml要求Blueprint≥7.1.0；未执行上游代码，也未宣称与当前Dynasty解析二进制相同。

OItems90–97四个HELPER.createItem将electrum_helmet/chestplate/leggings/boots分别构造为ElectrumArmorItem的四种ArmorItem.Type。HELPER取Oreganized.REGISTRY_HELPER.getItemSubHelper，主构造器先OItems.register触发类初始化，再REGISTRY_HELPER.register(modBus)。Blueprint内部helper未读，不把这段源码链扩大为完整依赖运行闭合。

ElectrumArmorItem全文读取：材质OArmorMaterials.ELECTRUM；getArmorTexture所有槽都返回 `oreganized:textures/entity/electrum_armor.png`。initializeClient创建ElectrumArmorModel(createBodyLayer().bakeRoot(), armorSlot)。因此当前直接覆盖路径是一张64×64图，不能仅按材料名把electrum_layer_1/2/3认作当前实际穿戴图。3张默认路径图虽存在、已看，只留非活动上下文，不计额外设计或当前渲染绑定。

四个库存模型为minecraft:item/generated，layer0指向各自electrum图标，存在10种trim_type override。只研究无trim基础图标，未逐一解析或目视trim变体。四个smithing_transform配方均为对应钻石装备＋electrum_ingot＋electrum_upgrade_smithing_template→对应Electrum装备；这是配方来源，不是实际制作、付款或获取验收。

## 专用模型与UV边界

ElectrumArmorModel全文读取。图集64×64，共13个addBox声明：头1、头侧翼片2、躯干2、双臂2、双腿2、双靴2、靴侧翼片2。四个翼片名义宽度0，deformation0.01，含独立y轴旋转，不能从二维图推断它们完整的侧面轮廓。

头纹理偏移(0,48)，头翼(32,41)；身体主件(40,21)、下摆(40,14)；右／左臂(48,37)/(32,37)；右／左腿(0,0)/(16,0)；右／左靴(0,16)/(0,24)，靴翼(16,12)/(16,18)。数值及名义尺寸抽取见declared-uv-boxes.json。它是声明记录，不是消费者六面方向、镜像、形变厚度或接缝验收，不套用标准64×32矩形裁图。

renderToBuffer按装备槽分开渲染：HEAD拷贝head姿态到Head，CHEST渲染Body及双臂，LEGS只渲染双腿，FEET将靴姿态拷贝自双腿并渲染靴。young分支另有缩放／位置处理，未实测。没有修改Dynasty身体几何、骨骼或挂点。

HumanoidArmorLayerMixin及Accessor全文读取，mixins.json列出两者：对Electrum护甲取getArmorModelHook渲染专用模型；trim另取原版铁甲模型；glint使用专用模型后取消原分支。这里只证明声明意图，不证明Mixin实际启动或对精确Forge消费者注入成功。renderToBuffer局部调用未转发输入的RGBA参数，不据此假称染色／glint表现正确或错误。

## 实际像素观察与适用性

1. 头图两侧有高起窄金片，中央盔顶与面孔开口仍明确；靴侧也有相呼应的金片。这个身份不是单纯金色换皮，但与已有翼冠／翼靴族有语义重叠，不能凭新命名空间增加信用。
2. 胸图为短宽金属胸片、两侧抬高方肩、中央亮区及下腹弧阶梯；腿图为连腰双直腿，保留裤裆透明。没有细碎纹样，主要靠浅黄、暗黄褐和少量近白大簇组织金属。
3. 靴图左右分开、鞋头为方阶梯，亮面在前侧，侧翼明显超出普通靴主体。可学亮暗簇的连续分工，不能把侧翼或肩片直接加到用户认可的普通短靴／胸甲上。
4. 64×64直接引用图中，腿、靴、躯干、头及翼片使用不同UV岛；亮黄大块与暗褐边分工连续。原默认layer_3只有零散翼片，不能把它当缺失身体贴图，也不能因为文件存在就加作第三次独立设计。
5. 对当前未改金属甲，只限定借鉴离散高光、少数大材料面和四件身份对应；不直接迁移专用UV或翼冠几何。它并非前期布皮甲的整体比例范本，更不授权重画已认可鸿蒙等高阶甲。

与D59流浪者、D76防化服、D77养蜂服、D78旅行者及D79板甲的冻结观察对比：本案的金属翼冠／翼靴和独立64×64模型区别于布罩帽、功能面罩、皮革小扣与普通甲片；这些旧原图本轮未重开。既有aether_valkyrie_white_gold_crown、divine_ornate_gold、shadowlands_small_wing_cap记录已经包含翼冠／金色分区语义，实际独立性仍未闭合，不声称找到一个已证明在旧族之外的新族。详见prior-family-comparison.json。

## 限制与断点

最多1个待审完整族，正式新增信用0，全局有效总数及准确缺口仍未知，gate=false。没有把组件、配方、图集、体块或换色算成设计。完整旧ledger与D54确认对象保留。

本批收到并读取Main对D79的有限支持收据，SHA256 `3a9074b0703301b6ce0c5d4f3e4b110ce9546a9de3f6fa81d8ccce993bfce490`：leather tier0不保证落在默认tier1–2随机范围，BASE validator也必须先成立。仅在新批保存限制，不重写D79。该支持不构成全局设计信用。

未闭合Blueprint注册helper、确切Forge消费者／Mixin启动、trim映射与全部修改器、原生获取及真实穿戴五视图和接缝。289保护／70优先资源批前批后核对，不开Java／游戏，不动共享Jar、主清单、提示词或用户实例、存档、声音亮度。
