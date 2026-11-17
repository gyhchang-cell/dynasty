# D47：铱金属甲四部位完整参考与原生UV分区

固定本地Terramity 0.9.8 Forge 1.20.1 JAR；17条原始文件和7份只读反汇编来源哈希见provenance.json。实际查看6张PNG：16×16四件库存图、64×32的iridium__layer_1/2。whole-native-source.png是原图整数放大排版，不是游戏截图或Dynasty制作稿。原图未缩小、减色或写进生产资源。

四槽请求iridium_armor_helmet/chestplate/leggings/boots经bootstrap340–343→lambda$static$338–341→对应IridiumArmorItem四个子类→ArmorItem.Type。库存JSON使用iridium_helmet等较短资源名，不能靠注册名猜贴图文件。头胸靴getArmorTexture返回带双下划线的iridium__layer_1，裤返回layer_2；所选四子类及父类未声明initializeClient/getHumanoidArmorModel。原版上下文是本地固定Forge生成源，非上游提交来源证明，也不等于实际运行无其他hook。

结合固定1.20.1 HumanoidModel.createMesh、HumanoidArmorLayer槽可见性与ModelPart.Cube声明，列出四槽10个部位实例的60块原生UV矩形，见whole-reference-study.json与native-uv-regions.png；已实际查看分区页。上下方向保留源构造器命名及UP倒置V端点，左侧镜像明确记录；图片只裁原图矩形，未把镜像后朝向、接缝或穿戴遮挡冒充验收。HEAD的hat全部透明；胸只剩短肩臂片。L1臂端盖[48,16,52,20)为0/16，四个侧面末行各0/4：相比D2五套端盖16/16而四侧末行空的记录，可借“短肩片不凭空补腕盖”的材质边界原则。此核对不证明D2游戏中悬空已复现。

材质与比例：倒U盔口、短宽胸、直腿与分开的短靴保持原版身份；米白亮簇→粉色主面→暗紫侧边和外沿，有清楚的离散层次。胸图标从左肩向胸上部连接亮块，未成为人台；但穿戴胸背的亮块较碎，不适合照搬进布皮甲。对鸿蒙/朱砂/织锦只学习主面与侧边的组织，不擅自改获选配色、纹样；对朴素袖口只借材质结束方式，不复制粉金属。

整体去重：terramity:iridium_armor已在既有池，基础形状仍属vanilla_outline_elemental_palette；不是新完整设计，不把四部位、颜色或60裁片计数。654名称族、640甲名称族、215保守学习组不变，独立有效设计总数仍未核定，适用1000门槛未满足。

review.py已验证源JAR/17条目/7反汇编/三份固定上下文、四槽实际供应器与材质、60矩形、289保护路径。新贴图制作0、游戏启动0、清单删除0。实际穿戴五视角、所有运行hook及最终视觉验收待验，获选精致旧稿与D2/PNC其余待验范围保留。Main独立核收及主清单管理仍单独进行。
