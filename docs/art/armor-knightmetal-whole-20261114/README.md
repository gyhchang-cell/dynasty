# D106 twilightforest:knightmetal 整套参考补证

骑士金属甲同一旧knightly_metal_waist家族：四图标与两穿戴原图均查看。图标灰绿金属、暗面孔T口和棕金腰带形成身份；穿戴图knightly命名不同于knightmetal注册ID，实际返回路径已读，不能按名字拼错。

TFItems bootstrap100–103→factory81–84创建KnightmetalArmorItem、ARMOR_KNIGHTLY及四对应Type。LEGS返回knightly_2，其他knightly_1。initializeClient扩展选择KNIGHTMETAL_ARMOR_INNER/OUTER，实用TFArmorModel；TFLayerDefinitions bootstrap6/7→lambda4/5→KnightmetalArmorModel.setup并创建64×32层定义。

setup完整320指令已实读：基于HumanoidModel，头8³；左右角各两节5×3×3和3×2×2，UV24,0与54,16；臂UV40,16、腿UV0,16。另有肩/靴2³小尖块，非球体曲面。左右镜像/旋转与inflate.25保存为待最终面向核验，不把方块网矩形当有符号面。

实际查看角根、角尖和尖块UV矩形：粗大浅绿金属块与灰边，腰带只在LEGS图集躯干区。四配方forge:ingots/knightmetal标准形状、无附加NBT输出；图标各10trim覆盖属于同设计变体。

固定本地Jar、原始文件与Python解析哈希均保存。原图及原始UV矩形已实际查看；矩形裁片不等于最终有符号面/穿戴接缝验收。既有整套家族比较见historic-family-dedup.json，同套新增部位、附加层不计新设计，新增验收信用0。保留既有适用认可证据，总数与缺口仍未核定，1000门槛未成立。

待验：独立适用性验收、全局1000不同设计总数与缺口未核定，制作门槛未成立；真实加载、染色/trim及最终有符号UV面、左右镜像接缝和穿戴五视图未验；当前28目标均未证明同时从未重画且简陋，不能借研究重画受保护原稿。

289已认可与70优先资源哈希不变；未覆盖贴图、共享Jar或主清单；未运行Java或游戏，未操作用户实例、声音、屏幕和亮度。
