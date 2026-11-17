# D60 山羊毛甲完整四槽研究

官方 Momo-Softworks/Cold-Sweat，1.20.1-FG 固定 e529039f96365812ade00923dd23be73d292b5d2。gradle.properties实读MC1.20.1/mod2.4.5；mods.toml声明Forge[47,)，不把最低范围说成精确加载版本。

cold_sweat:goat_fur_helmet/chestplate/leggings/boots 是4个真实注册；ItemInit16/48–55创建ITEMS与四GoatArmorItem；ColdSweat37–58的MOD_ID=cold_sweat及构造器ITEMS.register(MOD_BUS)闭合原生声明。四个完整item JSON均item/generated→layer0同ID图。不是羊毛原料goat_fur单件，也不将另Hoglin系列加分。

实际查看原生四16x16图标+两64x128穿戴图，以及两张7组UV网格近看页。棕皮宽边包浅米白毛，毛帽留大暗脸孔和耳边短垂片；短宽胸毛口、棕中线与横腰，裤两腿分开、膝前浅毛大块；长直靴筒棕边白口，两脚明确。白色是毛主体，不可删成透明。图标靴筒偏长，本项目普通甲不直接照其比例。图集下半才是定制区域，不能按64x32普通甲取它上半空白。

Goat四Model、GoatArmorItem、RegisterModels、ModArmorMaterials均完整实读。每模型调用HumanoidModel.createMesh(0,1F)，保留7个标准基础盒；新加10盒：帽1，胸/大毛领/双袖4，腰/双腿3，双靴2；共7种不同UV/尺寸网格、60原始面矩形，未将其当独立设计。LayerDefinition均64x128。头UV16,80尺寸8³；胸0,64尺寸8x12x4；毛领24,64尺寸10x6x10；袖0,80；裤腰16,112、双腿0,112；靴48,80。镜像builder在左袖/左腿/左靴addBox之前调用mirror，右边不镜像。最终面朝向仍需实际烘焙验证。

10盒原点、局部pivot、膨胀量(.8或裤.6；袖Y1.2)和父根已逐一记入source-uv-correspondence.json。头帽局部Z3不是最终世界位移；身体胸盒Y-24加子pivot24，实际仍受body父姿态影响。毛领body子fluff是唯一动态调整处：viewXRot夹0..60°后弧度/2，并令fluff.x=fluff.zRot*2；不误读为yaw追踪，不证明无穿模。

RegisterModels MOD/CLIENT订阅的registerLayers注册四LayerDefinition；GoatArmorItem initializeClient扩展回调先checkForInitModels，再按HEAD/CHEST/LEGS/FEET返回专用缓存。懒初始化以HOGLIN_HELMET_MODEL非null作guard，顺序先Hoglin后Goat；本批不运行，不把这个guard静态观察说成已复现故障。材质getName为cold_sweat:goat_fur，GoatItem没有覆盖getArmorTexture。

已复用并实际读保存Forge1.20.1上下文：HumanoidArmorLayer完整；ForgeHooksClient325–343；IClientItemExtensions98–139；HumanoidModel36–80。消费链：原层先copyProperties与setPartVisibility，再hook→IClientItemExtensions.getGenericArmorModel→当前Goat四模型→copyModelProperties，复制标准根可见性；CHEST只body双臂，LEGS body双腿，FEET双腿，HEAD head/hat，子毛领随body过滤。非染色ArmorItem选材质L1/L2；LEGS为2，其余1。这个上下文闭合有界静态对应，不证明玩家实际加载二进制、第三方mixin、资源包、裁切/左右/五视接缝或动画通过。

对照既有完整保存的 arctic_fur_leather、wastefur_torn_hem_coat、yeti_pale_blue_fur、cryomancer_fur_collar文字观察：白毛棕皮/毛领不是新机制保证；此套环状大毛领与下半图集分区提供来源学习，但独立适用语义仍待Main核收，最多1候选，信用0；不以新namespace、10盒、7网格、4部位计数。对于leather/cloth仅借“皮边连帽口/袖口/靴口且毛为粗块”的材质组织；大立体毛领不移植给普通Dynasty体型。

本批无新美术/模型/UV修改、无Java/游戏、无主清单修改。289保护资产以哈希另记。D54本地已验1族只继承前账本，重复carry加0；全局总数/缺口null，gate false，未称全部完成或实际穿戴验收。
