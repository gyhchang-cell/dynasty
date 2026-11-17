# D78：旅行者护甲完整默认配置的有界参考

本批实际查看匠魂旅行者护甲默认玫瑰金＋皮革组合的原生组件，研究图标及穿戴材质分工。没有制作、覆盖 Dynasty 美术，也没有启动 Java 或游戏。参考门槛仍未满足，不能据本批删除待办。

## 固定来源及实际查看范围

官方仓库 [SlimeKnights/TinkersConstruct](https://github.com/SlimeKnights/TinkersConstruct/tree/16bbeb883a933986321867ef3b93bd441f0fa894)，固定提交 `16bbeb883a933986321867ef3b93bd441f0fa894`。提交、未截断 Git 树及逐文件 Git blob/SHA256 见 provenance.json。gradle.properties 声明 MC 1.20.1、Forge 47.4.0、Mantle 1.11.126；这不是 Dynasty 当前已加载依赖的证明。

实际查看14张原生PNG：9张16×16图标组件和5张64×32穿戴层。对应三页为 native-icon-parts.png、native-worn-layers.png、source-over-diagnostic.png。最后一页仅用源像素作 source-over 合成方便阅读，不模拟物品加载器、修改器、染色、深度或GPU，不是游戏图或最终图标验收。其余下载的铁材、灰度底、染色底等未逐张看图，不计入14张。上游文件原样保存，不接入 Dynasty。

## 注册、配置和消费者

- TinkerTools.java 238–247：travelersGear 使用 `registerEnum("travelers", ArmorItem.Type.values(), ...)` 创建 MultilayerArmorItem；本批没有读取 Mantle 的 registerEnum 内部，因此枚举后缀拼接的底层实现未闭合。四个 travelers_helmet/chestplate/leggings/boots 原生模型和工具定义均存在，不能另外编造材料变体注册ID。
- 四个原生 tool_definitions 的 default_materials 都是索引0 `tconstruct:rose_gold`、索引1 `tconstruct:leather`。最初选择铁材只是一项研究假设，查到定义后改查默认玫瑰金；铁材下载不另计设计。未构造或加载真实NBT物品。
- 四个物品模型 loader 为 `tconstruct:tool`，cuirass索引1、metal索引0；护目镜额外有无材料索引的base。ToolModel.java 396–436、610–642、752–778显示按材料列表索引选sprite，运行时从MaterialIdNBT读取材料。本批未闭合 MaterialModel/Mantle 的实际sprite解析与全部修改器，所以合成页只作诊断。
- MultilayerArmorItem.getArmorTexture 返回 dummy；initializeClient 交给 ArmorModelDispatcher。Dispatcher.getGenericArmorModel → MultilayerArmorModel.setup，使用传入的原生 HumanoidModel，不在本批创建专用身体几何。
- ArmorModelManager 从 `tinkering/armor_models` 读取配置；travelers.json 顺序为固定base、first_present cuirass、material metal、trim。皮革材质的渲染信息fallback为cloth，不是wool；无dyed修改器的条件下，前两个染色分支不供图，随后按索引1选皮革材质。是否解析到指定原生sprite仍有下层读取待核。
- TextureType.fromSlot 只有LEGS走LEGGINGS，其余槽走ARMOR；文件路径在 `textures/tinker_armor/travelers`，不是标准 `textures/models/armor/*_layer_1/2`。base_leggings不在固定树中，不应补造一张。材质getter处理材料专用纹理及fallback；多层逐次render。TintedArmorTexture使用armorCutoutNoCull和原生模型，不等于普通图像alpha合成。

## 实际像素观察与可借鉴点

1. 护目镜不是整盔：两块浅灰蓝镜片只有4个不透明原生像素，棕绑带24像素，玫瑰金边框与顶部扣16像素。靠透明空区和横向双镜片识别，不靠画满头像。可学“材料各司其职”，不能把 Dynasty 普通盔甲强改成护目镜。
2. 背心为短宽棕皮外轮廓、阶梯V领，中央浅粉竖扣片和深色扣缝；皮面138像素、金属38像素。亮边在肩上及左侧形成几块连续平面，没有细碎雕花。适用于旧皮甲的材质对比参考，不授权重画已认可胸甲。
3. 长裤以腰部连接两条直腿，裤裆透明；膝部少量横向金属块与皮色分离。靴子两侧直筒、下端方形外伸鞋底，中间保持明确透明间隔。旅行者靴偏高筒；不能直接照搬到用户要求的原版短靴比例。
4. ARMOR皮革层原生430个不透明像素，金属43；LEGGINGS皮革280、金属108。皮革用连续深浅棕色块建立皮面与接缝，金属留给护目镜、扣片及局部护片。腿部层腰带的金属横条比ARMOR层更集中，不能因同属一套就共用两张图。
5. 14张查看图的alpha都只含0/255；这些白亮部、粉亮部、灰蓝镜片是主体，不是应删除的背景。不把这一案例的二值alpha推广为所有原稿都必须量化。

## 去重及适用限制

已有ledger中 complete_hard_leather_metal_shoulders、complete_thief_hood_leather_panel、explorer_straps_iron_variant、jerote_brown_hunter_leather_variants 均存在棕皮、绑带及金属扣语言，本批读取其保存观察作对照，未重新查看旧图。护目镜和中央短扣片有具体差异，但不足以单凭名称、来源或文件哈希授予独立设计信用。见 prior-family-comparison.json。

只提交最多1个待审完整配置；9张图标组件、5张穿戴层、4槽、玫瑰金/铁材以及损坏/染色/翅膀变体都不拆分计数。新增正式信用0；全局独立适用总数与准确缺口仍未知，gate=false。D54独立确认对象与全部旧ledger原样继承。

当前可服务旧皮甲、布甲的材料分区研究；不把上游原图复制为原创。尚未闭合Mantle注册辅助、MaterialModel精确sprite解析、默认NBT实际生成/获取及真实穿戴五视图、接缝、修改器叠层；本批没有给出这些验收结论。受保护289项与优先70项只作批前/批后字节核对，不假称重新审过全部美术。
