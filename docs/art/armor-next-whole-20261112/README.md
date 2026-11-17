# D51：下一完整参考——Frostiful 毛皮甲

本轮转向此前池中没有的 Frostiful，未再包装 D49。官方来源 https://github.com/TheDeathlyCow/frostiful ，固定1.20.1分支提交 f017b15a2b23a6474d03d8e4b4e9e244247ffa24；项目属性为Frostiful1.0.11、Minecraft1.20.1、Fabric0.15.7。只下载并阅读原始资源和源码，未构建或执行外部项目。归档SHA、逐条SHA和原始LICENSE/CREDITS已保存。

## 已有资源与筛选

原有28套/112图标/56穿戴PNG的历史制作依据仍有效，不能把有旧版本的资源随意称作从未修改。当前已确证未改套装仍为0；D2袖口/材质/旧L2问题保持待验。289保护路径当前哈希全部与固定基线相符，已认可与精致稿不动。

本地本轮5514条jar路径按文件名+大小筛查3561桶（不是内容去重），得到331个四部位文件名候选；这只是机器候选，包含重复版本、原版与空槽位，不计参考信用。已筛出的非原版候选仍多为已有命名别名，所以改用官方新来源，不据此声称本地所有设计已穷尽。candidate-screen.json保留原样，不能拿331当已看设计。

## 完整毛皮甲与同系列对照

实际看过 native-icons.png、native-wear.png，以及两页 uv-context-*.png；都是作者原图或原图矩形的整数放大，非Dynasty新画、非游戏截图。主研究是fur四件完整毛皮甲，fur_padded_chainmail四件仅同族升级对照，暂保守按一个完整学习候选，不把部位、材质或镶饰拆信用。两张额外图是fur_padding和fur_upgrade_template，不是盔甲设计，排除计数。

毛皮图标用紧凑帽壳和倒U开口、短宽肩胸、两条直腿、分开的短靴保持原版身份。棕色皮面、浅赭毛边和深棕结构缝以大簇分区，毛边集中在肩、腰、裤脚与靴口，未用遍布全身的金线。毛皮锁甲对照在胸/腿/靴露出灰色网格，保留棕色垫边；只能学习材料分工，不把网格复制成布甲噪点，也不把同升级系拆成多个全新设计。

四部位图标与穿戴并非同一张贴图：fur图标模型layer0为frostiful:item/fur_*；穿戴材质getName是 **frostiful_fur**，原图位于 **assets/minecraft/textures/models/armor/**。锁甲物品名是fur_padded_chainmail_*，穿戴材质却是 **frostiful_fur_lined_chainmail**。这个明确不一致说明不能按物品ID前缀猜穿戴文件名或强行改名。

## 模型、UV与四槽消费者

Frostiful.MODID明示frostiful，主初始化调用FItems.registerItems；四个FUR_*用普通new ArmorItem(FUR_ARMOR, Type.HELMET/CHESTPLATE/LEGGINGS/BOOTS)，并注册原生fur_*ID。同系列四件对应FUR_LINED_CHAIN。没有把冰鞋或其自有模型当毛皮靴模型。

原生模型JSON均是minecraft:item/generated，四件各有10个trim_type覆盖，当前只研究无镶饰基础图，不把镶饰当参考。FrostifulClient的模型插件只额外加载霜杖库存模型；ArmorFeatureRendererMixin改构造后的自定义镶饰图集及renderTrim，不据此声称修改基础毛皮几何。机械token筛查的唯一相关model-data命中还包括IceSkateModel，仅作范围警示，不是额外语义阅读信用。

材质名、64×32原图与普通ArmorItem声明符合1.20.1标准盔甲布局。复用已固定的本地 **Forge生成MC1.20.1源码上下文**，保存头/帽、胸/双臂、裤身/双腿、靴双腿共60原图矩形/套，两套120矩形。Yarn与Mojmap不是同一源码凭证；没有把Forge上下文伪装成精确Fabric消费者源码，也没有声称已实测Fabric调用。标准对应是头胸靴L1、裤L2，完整记录见slot-and-uv-study.json。

实际矩形观察：fur帽外层区域透明，主头前面留开口及浅毛边；胸前浅边围成V，背面上沿成片毛边；手臂肩和腕有毛边，中段留空；裤腰与下腿、靴筒各使用不同图层区。锁甲对照的帽外层有棕色/深灰边，胸和腿有网格。不能将透明袖中段一律补满，也不能从原始矩形裁图推断镜像后的世界朝向、实际缝隙或穿模。120矩形不是120参考。

## 验证与尚未接受的边界

review.py通过：固定官方提交归档/源条目哈希、8个原生槽位声明、模型引用、4张64×32图集、120个有界UV上下文矩形及289受保护路径。未启动游戏、未改生产、未删除任务。Python首次联网遇到本地证书链错误，改用正常验证证书的curl取得官方固定归档，未禁用TLS验证。

本轮提供一个新完整毛皮甲候选及同族锁甲对照，尚待独立语义去重/适用性审查，不增加已验独立设计信用。现有654名称族/640盔甲名称族/215保守组不等于1000个已验独立设计。精确Fabric默认渲染器源码及实际穿戴五视角、逐面接缝、镶饰画面尚未验收，继续保留要求。制作门槛未满足，未提前重画。
