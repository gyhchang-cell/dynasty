# D42：既有甲壳甲整套绑定补齐

本轮只读核对固定 Pathogen 1.19.2 原始 JAR 的 aquatic 代表。原图曾见 `armor-biome-shell-reference-20261104`，本轮补齐此前未完整证明的四槽注册→supplier→具体装备槽→客户端分槽模型→128×128穿戴图引用。不是新设计，不把八个环境色拆成八套。

四件图标均为原生16×16；原生穿戴图128×128，原稿未经缩小或改色。`aquatic-whole-native-source.png` 已实际查看，是第三方原始参考排版，非新稿、非游戏截图。深绿甲壳用少量青色离散亮簇强调额面和肋片，短宽胸部与分开的直腿、直靴仍可辨。借鉴材质分区与层级方法，不复制原图或几何。

## 关键区别

头盔取 Head；胸甲取 Body/LeftArm/RightArm；裤子取 LeftLeg/RightLeg；靴子另取 leftBoot/rightBoot。其余 HumanoidModel 部件为空。四件共享 `pathogen:textures/entities/armor_hardened_aquatic.png`。客户端 MOD 订阅的注册事件通过实际 bootstrap1 接到 createBodyLayer，图集声明128×128。它不是普通原版L1/L2布局，不能把图库换图当成自动适配。

`review.py` 在固定反汇编文本上核对实际方法指令和注册 bootstrap；`verify.py` 核对22个原生文件、13份类反汇编、4条装备链、要求快照及289个生产资源哈希。通过只代表有限静态证据。javap不执行模组代码，未启动游戏。

## 保留的边界

未逐方块恢复全部模型UV，未实际穿戴、五视角或游戏验证；1.19.2参考不等于Dynasty 1.20.1兼容性证明。PNC root bridge和额外穿戴消费者的先前待验不因本轮关闭。D2袖口、旧L2和材质问题仍留待满足制作前提后处理。

累计654个已审名称族、640个盔甲名称族、215个保守学习组。这些不是1000个已验收独立设计；独立设计总数尚未核定，门槛仍未满足。本轮新增名称、设计信用、生产修改、清单删除均为0。
