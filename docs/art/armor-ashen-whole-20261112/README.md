# D55：Ashen 护目镜与披风四槽布甲原生参考

本批是实际源图、专用 UV 与加载链研究；没有新画 Dynasty 美术，没有运行游戏。参考门槛尚未完成，未删任务。

来源：[Embers Rekindled](https://github.com/RCXcrafter/EmbersRekindled/tree/c900e391c21d21ec35f17f17fba92b96a6fee37e)，固定提交 `c900e391c21d21ec35f17f17fba92b96a6fee37e`。原生配置 Minecraft 1.20.1、Forge 47.1.43、模组 1.20.1-1.4.7。ZIP 与提取文件逐字节对应，见 `verified-source-entries.json`；未执行外部代码。

## 实际查看与整套观察

查看 `native-source-images.png` 的四张16×16原生图标和64×64 `robe.png`；以及四页 `raw-faces-{head,chest,legs,feet}.png`。整数最近邻仅用于研究页，原始PNG无修改。这些是作者源资产，不是 Dynasty 获选稿或游戏截图。

- 护目镜图标用两块金色框、中央暗隙与黑绑带辨认用途；不是闭合头盔。模型是15个方体：八条细框、六条绑带与后脑小块。正面框内部没有完整镜片方体，不能将金色后脑块误说成一整块镜片。
- 披风图标短宽，左右黑色布面包住中央金色长条，靠少量大块明暗区分材质。穿戴模型另有三片长披风与三个前襟片；图标短不等于穿戴也短。前襟正反有接近纯黑与灰黑的差异，中央襟是金色大块。不可为“统一短胸甲”抹掉长披风。
- 两肩共用同一材质语言但使用不同UV位置；从原生裁片可见亮侧分布有别，不默认镜像。护手与靴子均接近黑灰，低对比是对 Dynasty 浅布/竹等目标的反例：不能只换色让所有材料都失去身份。
- 腿图标是暗腰部连接两条金色腿件。穿戴模型实为两只5×5×5护膝和两个上腿块；护膝挂在腿根，上腿块挂在 body。不能按图标补出原生没有的完整长裤几何，也不把上腿块当新胸甲。
- 双靴有分开的直筒和短鞋头；穿戴靴5×6×5，另有5×2×1鞋尖方体，整体不画圆鼓鞋。其暗面块可学，材料几乎不可辨的程度不照搬。

## 实际资源消费者

`RegistryManager` 的 ITEMS（Embers.MODID）注册四个 `AshenArmorGemItem`：`embers:ashen_goggles`→HELMET、`ashen_cloak`→CHESTPLATE、`ashen_leggings`→LEGGINGS、`ashen_boots`→BOOTS。四个 generated item model 的 layer0 均解析到各自原生 PNG。

`AshenArmorGemItem extends AshenArmorItem`，继承 `initializeClient` 的 `ARMOR_MODEL_GETTER` 与 `getArmorTexture` 的 `embers:textures/models/armor/robe.png`。四个 Mesh 均由 `Embers.registerLayerDefinitions` 注册为64×64。模型表初始化实际位于 **AncientGolemRenderer 构造函数**，由实体渲染器注册引用；不是 AddLayers 事件。静态链可追踪，不声称已验证客户端事件先后顺序。

四槽分别15/18/4/4，共41方体、246原始盒网面矩形，均在64×64范围；记录来源表达式、父节点、原点、尺寸、膨胀和姿态。246不是246个设计。原始裁片没有应用 PartPose、烘焙顶点方向或运行穿戴姿态，不能当正侧背、接缝及黑剪影验收。

披风根据玩家披风插值数据旋转；七个附加宝石由 cloak 的 `gem0`…`gem6` NBT存在性控制。`AshenArmorGemItem.attachGem` 写入这些键。基本图标不是七个不同宝石状态；七宝石、四槽、41方体、换色均不增加独立设计数。

## 去重与适用边界

对照已有 `wizard_hat_robe_variants`（同模法袍）、`immersive_robe_open_front`（开襟袍）、`explorer_straps_iron_variant`（绑带轻装）及 D53 warlock 三件上下文：开襟、暗布、金色装饰本身已有，不算新意。此套的护目镜/绑带、披风三片与膝件组合留作 **一个待独立审查整套家族**，不能仅凭新命名空间认定独立。

适用于布/锦/海丝的襟、袖口与大块材质组织学习；工业护目镜与长披风不直接套用 Dynasty 古风短甲。新增已验证设计信用0，新增学习组0；历史654名称/640盔甲名称/215保守学习组保持原义，不是1000门槛通过数。全局已验证适用独立总数与精确缺口均未知（null）。

待验：独立整套语义去重/适用性、实际烘焙面朝向与接缝、运行初始化顺序/装备槽姿态、正面/45度/侧面/背面/黑剪影。参考门槛未核实前不重画、不接入新稿。本批保留已认可资产及原始任务。
