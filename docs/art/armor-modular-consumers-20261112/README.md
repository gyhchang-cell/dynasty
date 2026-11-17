# D50：D49确切依赖与最终静态消费者补证

仅延续 D49 同一完整配置，不新增候选或有效设计信用。D49 冻结目录未修改。本轮补齐本地可读的继承显隐和库存分层烘焙消费者，供主协调独立审查。

## 固定依赖与范围

同一“锻造之旅/mods”目录的 GeckoLib Forge 1.20.1 **4.8.3**（不是项目4.8.4）和 Tetra 6.9.0 已保存归档及条目哈希。GeoTetraArmor 的 mods.toml 仅明示 Forge/Minecraft 依赖；不能把“同目录存在4.8.3”说成已证实游戏实际加载此版本。Manifest、Mixin配置与refmap已固定，客户端 HumanoidArmorLayerMixin 在原配置中列出；运行时加载、重映射及其他模组干预仍未实测。

## 四槽穿戴静态链

GeoArmorRenderer 4.8.3 的八个 getter 原样寻找 armorHead、armorBody、armorRightArm、armorLeftArm、armorRightLeg、armorLeftLeg、armorRightBoot、armorLeftBoot。其 $2 枚举映射明确 HEAD/CHEST/LEGS/FEET 对应分支1/2/3/4。

applyBoneVisibilityBySlot 首先调用 setAllBonesVisible(false)，再按原版 ModelPart.visible 条件启用头、胸身双臂、双腿或双靴。setBoneVisible 对空骨安全，最终调用 setHidden(!visible)。GeoTetraArmor 重写 reset 并追加 belt；槽位处理先调用父类，再在 LEGS 启用 armorBelt。

全重甲配置对应：头→base/armorHead；胸→base/armorBody、left/armorLeftArm、right/armorRightArm；腿→base/armorBelt、left/armorLeftLeg、right/armorRightLeg；靴→left/armorLeftBoot、right/armorRightBoot。全部根骨在D49原生几何存在。根骨显隐静态关系闭合，不等于所有子骨/立方体最终可见、逐面UV或穿模已通过。

**姿态变换是子类自己的 override**，没有调用父类 applyBaseTransformations。已读其完整方法：头身匹配对应原版部位旋转和位置，腰带在 body/belt 均存在时跟随 body；双臂加左右X偏移及2-Y，双腿/靴左右X偏移及12-Y。双靴变换嵌在对应腿骨存在分支中，当前左右geo同时声明腿与靴，满足该静态条件。不能仅抄父类公式就宣称验证了实际模型。

## 最终库存图标静态链

1. Tetra ClientSetup.modelRegistryReady 通过 RegisterGeometryLoaders 注册 modular_loader。
2. 四份原生模型JSON使用 tetra:modular_loader；ModularModelLoader.read 解析display/可选variants，返回UnresolvedItemModel。
3. UnresolvedItemModel.bake 安装 ModularOverrideList；getOverrideModel 调 IModularItem.getModels。
4. GeoTetraArmor.getModels 读取实际模块模型，过滤nonNull与modelNotGecko，再按renderLayer排序。modelNotGecko是 !type.startsWith("gecko")，所以3D穿戴图不会被拿来当平面库存层。
5. createLayerModel 把每个ModuleModel.location映射到图集材质，并建立该层颜色、自发光、变换和renderType设置。
6. ItemLayerModel.bake 从 SpriteContents 创建物品元素、烘焙四边形，应用图层变换后加入 CompositeModel builder，最终build。上下文不同时还可进入TetraSeparateTransformsModel。

因此本配置库存来源是头1层、胸3层、腿3层、靴2层，共九张模块PNG；不是四张现成完整PNG。未捏造原生扁平合成图，没有把软件贴层预览称为最终库存截图。相同priority的原集合顺序未确定，不宣称最终遮挡次序；实际图集加载、最终着色和GUI显示待验。

## 完整语义判断与边界

D49现在具备同一九模块铁重甲配置的四槽身份、原图、材料选图、根骨消费者及库存最终分层消费者静态证据。研究单位最多是一个完整配置族；换金属、九个模块、三张完全相同穿戴图、三份geo均不另计。来源新、命名新或模块化机制新都不能自动证明与旧池金属板甲/羽饰甲在语义上独立。其头盔附加结构还需按用户紧凑原版比例做适用性独立审查，不把整套作为理想制作模板。

本轮有20条固定源条目、15份只读反汇编、27段带原路径/行号/哈希的方法摘录。review.py核验归档、所有保存输入及289条受保护路径通过。门槛仍未达到，不制作生产美术、不启动游戏、不删主清单。
