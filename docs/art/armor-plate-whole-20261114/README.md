# D79：板甲铁／皮革完整配置的有界研究

本批实际研究匠魂板甲四槽的铁甲片＋皮革内衬配置，用于未改旧金属甲的轮廓、材质分区与穿戴UV学习。没有制作或覆盖Dynasty资源。与旅行者共用渲染实现不代表是新实现，换材质也不另计设计。

## 固定来源与配置身份

官方 [SlimeKnights/TinkersConstruct](https://github.com/SlimeKnights/TinkersConstruct/tree/16bbeb883a933986321867ef3b93bd441f0fa894)，提交 `16bbeb883a933986321867ef3b93bd441f0fa894`；复用D78固定Git树及上下文哈希，新增25个来源文件逐个校验Git blob和SHA256。相同源码声明MC1.20.1、Forge47.4.0、Mantle1.11.126，不代表当前Dynasty加载了这套二进制。

TinkerTools240的plateArmor由registerEnum("plate", ArmorItem.Type.values(), type -> new MultilayerArmorItem(ArmorDefinitions.PLATE, type, ...))注册，ArmorDefinitions.PLATE指向tconstruct:plate。四份原生plate_helmet/chestplate/leggings/boots物品模型和工具定义都存在。本批继续保留Mantle枚举后缀辅助内部未读的限制，不凭材料另造注册ID。

四份工具定义的default_materials并非固定铁／皮革，而是两个tier1–2随机材料选择器。因此这里的铁／皮革是明确选定的研究配置，不能称默认生成套装。铁stats包含四种plating槽，皮革stats包含maille，支持本配置的两个角色；本批没有构造真实NBT、验证随机材料选择器、配方或游戏获取。源码材料资格不等于实际获取验收。

四个模型均loader=tconstruct:tool，plating索引0、maille索引1，破损模型仅为同物件状态，不计参考。plate.json穿戴层顺序是plating material(index0)、maille first_present、trim。maille先判断金属fallback并使用染色金属图，再尝试染色布图，最后使用材料图；皮革fallback为cloth，无dyed修改器时按最后的材料路径研究。本批未读取下层MaterialModel精确sprite解析，也没有声称把诊断合成当原生渲染结果。

复用D78已读的MultilayerArmorItem → ArmorModelDispatcher → MultilayerArmorModel → 传入HumanoidModel；LEGS用leggings，其余槽用armor，路径在textures/tinker_armor/plate。穿戴材质逐层armorCutoutNoCull，图标则使用ToolModel动态材料。复用消费者清单与哈希见reused-consumer-context.json，不重复授予实现信用。

## 实际查看与观察

实际查看12张新原生PNG：8张16×16图标组件、4张64×32穿戴层。native-icon-parts、native-worn-layers为原生像素最近邻放大；source-over-diagnostic仅拼合所选配置；prior-whole-comparison重开D78诊断页作整套比较。四页均非游戏截图，后两页不能代替物品加载器、穿戴五视图或GPU材质验收。

- 头件金属48像素、皮革30像素。金属为低拱帽顶和窄面缘，深色皮革下沿形成护耳与面口，区别旅行者的两块镜片及单条头带；不能因为头部留白就补成实心头盔。
- 胸件铁片120像素、皮革36像素。上肩与领口的白亮块连成少数阶梯面，灰主体保持短宽，底缘皮革横腰和袖端小皮块明确收束。主亮面占比大、肩口近原版，适合旧金属甲的清晰体积参考；不应照搬白亮面形状作为原创。
- 腿件铁片80像素，形成腰和上腿；皮革32像素集中在两侧下腿，裤裆保持透明。不能用高饱和花纹替代上下材料关系。靴铁片88像素，两条直筒与方形外伸鞋头，中部皮革带16像素；本参考靴偏高，不能无条件用于用户已认可的短靴比例。
- 穿戴ARMOR铁片608像素、皮革164；LEGGINGS铁片248像素、皮革48。铁片头、躯干、手臂与脚部区域呈连续大亮面和较深边缘；皮革层集中于边带、腰线等。LEGGINGS皮革仅原始矩形[0,27,16,30]，不能把其他空区当缺图后填满。
- 12张原图alpha仅0/255；白色是铁甲主体高光，不是应删的背景。并不因此量化用户原稿，或将这个案例的二值alpha当成通用规则。
- 与D78的原生金属组件比较，四槽alpha均不同；这只是像素事实，不能单独证明语义独立。诊断整套中，旅行者以皮面与小金属扣为主，板甲以大铁片和少量皮带为主；其差异比单纯材质换色明确，但仍须与已有金属甲家族一起去重。

## 去重、应用与未验范围

已读D59Wanderer、D76防化服、D77养蜂服和D78旅行者的冻结观察，对照布料主面／面罩网罩／皮面小扣／铁片内衬四类分工。前三批旧原生图本轮没有重开，不能虚报重新看过。D59罩帽金边、D76胸接口、D77网罩衣襟不能因同有四槽和64×32图集就等同板甲。另一方面，已有hard_leather_metal_shoulders、knight_metal_color_family及knightly_metal_waist均有甲片＋衣料语言，不能因本批新命名空间就给独立信用。保存观察比较见prior-family-comparison.json。

可供旧金属甲借鉴：金属用连续亮面、皮革用于真实连接位置，图标与穿戴材料分工保持对应。布／皮甲只学接口区组织，不改成重板甲。竹、织锦、朱砂、鸿蒙等已认可原稿继续保护，不按本参考统一重画。

本批至多1个待审完整配置，新增正式信用0；四槽、12PNG、组件、破损、染色及换材质均不拆算。全局有效总数和准确缺口仍未知，gate=false。保留完整D54确认对象及全部旧ledger。

仍未闭合：Mantle注册辅助内部、精确sprite解析及修改器组合、真实NBT制作和原生获取、精确游戏消费者与五视穿戴／接缝。本批没有修改身体模型或做实机验收，不删除提示词，不启动Java/游戏，不碰共享Jar、存档、声音、亮度、焦点或主清单。
