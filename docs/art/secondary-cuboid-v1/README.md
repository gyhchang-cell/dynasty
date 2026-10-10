# Dynasty 次级生物 Cuboid 美术重做

本地任务，2026-10-10 夜间开始。优先完成河童 `river_imp`、树精 `tree_spirit`、虾兵 `shrimp_soldier`，随后继续 cod4/cod6 中经实际轮廓审查判定较差的模型。保留实体 ID、旧骨骼名称与控制器七态，未改战斗、任务、AI、属性和掉落。九首鬼车、cod2 模型与 NPC 正由其他聊天处理，本轮不覆盖。

## 首批体块与骨架

- 河童：17 模型单位高（原碰撞高 1.1 格），短胸腹与骨盆、阶梯背甲、方盘、短喙、蹼足；root → body → neck/head/dish、shell、左右分节手臂，pelvis → 双腿、尾部。步行交替摆足，攻击双臂划击。
- 树精：34 模型单位高（原碰撞高 2.2 格），树桩、树结面具、四条根足、双枝臂、非对称断枝冠。保留 leg/foot/branch 旧名称并改为根足/枝杈含义。攻击先举枝再下砸，root 不平移阵位。
- 虾兵：20 模型单位高（原碰撞高 1.25 格），分层甲壳、额剑、粗方触须、钳臂、四段腹尾与扇尾、六条泳足。枪挂 left_grip 子骨；动作由钳臂驱动，同一骨空间计算握点，无第二次缩放。

资源为原创建模：只用 Cuboid；每只独立 128×128 PNG，四种纯色，无渐变/照片/抗锯齿/随机噪点；每个面的 UV 按模型单位映射，纹样在 2px 网格上。物品图标未来遵循用户另行指定的 16×16、白边、四色、至少 2×2 色区规则，实体 UV 不套用图标边距布局。

## 验证状态

初版五面软件审查已完成（正面/45°/90°/背面/纯黑）。文件名含 review 的图片均为软件渲染，**不是游戏内截图**。已检查 UV 边界、四色、旧骨骼保留与循环接缝。原始源文件在 source/，原提示词备份在桌面 `code x提示词/美术重做原文备份-20261010`。

本体及 QA 构建成功。真实 Forge 客户端运行 `cuboid-seven-final-01` 完成 77 个阶段：每只正面/45°/90°/背面与七态动作；每只 19 个动画名称实际烘焙成功，旧骨骼无缺失，虾兵武器确挂握持骨。PNG 是原始游戏帧。窗口经 agent 禁止显示/获取焦点，音量为零，QA 还逐 tick 确认隐藏状态。单只截图时记录的 FPS 不能当作 20 只持续性能验收。

`cuboid-first-three-01` 的相机裁切和正背标签有问题，仅保留作为诊断，不作为视觉完成证据；随后 `cuboid-first-three-02` 与 `cuboid-seven-final-01` 已修正相机。最后鲤精尾扇分段重叠面已修，已在 cuboid-carp-tail-final-01 完成额外 11 阶段真实客户端重验；其余六只与 seven-final 运行的资源字节相同。验证代码只选择原有同步动画状态，未做战斗玩法/真人联机验收。

## 第二批体块与骨架

- 鲤精：横置鱼身、阶梯背鳍、双胸鳍、分节尾与扇尾；root/body → neck/head/jaw、fins、tail/tail_tip/tail_fan。游动由尾部左右摆与胸鳍开合驱动。
- 螺女：17.5 模型单位高，腹足底座、胸/腰/骨盆上身、粗阶梯壳；root/body → pelvis/waist/chest/head、shell 与腹足尾。原 fin 骨改为双臂保留名字，缩壳时腰身俯收。
- 灯笼鬼：21 单位高，四根柱框、四片纸面、两层顶盖、悬挂杆、分节流苏；纸面和流苏各有子骨。技能时纸面开合。
- 石精：13.5 单位高，低矮主石/顶石、嵌入面、四条短石足；body/boulder、neck/head、四组 leg/foot。行走交替抬石足，施法主石起伏。

原提示词备份在桌面 `code x提示词/美术重做原文备份-20261010`。模型总覆盖还剩 12 只。原文全模型泛化条目只能缩为其余 ID；20 只负载/寻路/粒子、生态、两名真人联机等独立条目继续保留。cod6 尚无本轮可删除的已完整验收模型段落。

## 第三批体块与骨架

- 蟹兵：15 单位高，12×5×8 主甲壳，阶梯背盾、双眼柄、六条有间隙的侧足、双钳。root/body → carapace、neck/head/eyes、arm/claw/pincer、leg/foot。钳口子骨合拢，横行时侧足交替支撑。
- 尸甲虫：8 单位高，8×3×9 腹体、左右鞘翅留缝、六足与独立双颚。root/body → neck/head/mandible/antenna、elytron、leg/foot、tail。技能展开双鞘翅，攻击颚部咬合。
- 毒蝎：10 单位高，低矮腹甲、双螯、六足、四段上弯尾与刺。尾由 body → tail → tail_1/2/3 → stinger，刺随分节蓄力前刺；腿足之间留空隙，避免并成两条长板。
- 机关鼠：7 单位高，6×4×6 木壳、尖吻、大耳、四条关节腿、三段尾与后部方孔发条。root/body → neck/head/ears、key、tail链、leg/foot。追击步幅加快，啃咬俯首，发条摆转。

第三批已在 cuboid-invertebrates-final-01 通过 44 个真实客户端阶段，已复查原始截图并缩减对应四只的模型待办范围。审查中发现的眼片/尾部共面闪烁已用体块层次修正；未改碰撞尺寸或 AI。

## 第四、五批体块与骨架

灰狼：高肩胸、短尾、前腿/后腿跗节、双层耳与独立下颚；野猪：10单位宽肩胸、黑鬃、扁鼻与外露阶梯獠牙；金钱豹：12单位长腹体、低头、长分节尾、2×2像素硬边斑点；红狐：窄胸、尖吻、大耳、三段蓬松尾与白尾尖。四只保留旧耳/獠牙等骨名，增加 chest、shin、jaw 专用骨，攻击分别扑咬、冲顶、低伏扑击与尾摆。四只已通过 cuboid-beasts-final-01 的44阶段真实客户端验收，已复查原始游戏截图。

灰隼：宽翼、钩喙、独立翼尖；精卫：短翼红冠、衔石挂 beak 子骨；机关鹊：木板翼、方形十字齿轮、长尾；蝠妖：大耳、短体、阶梯翼膜和双獠牙。均为10～13单位高的独立体块比例，保留旧翼/脚骨名，分别拍翼、俯冲与机关摆翼。蝠妖翼膜用0.5单位厚度的长方体，正面纯黑轮廓可读；齿轮十字分成相邻体块避免重叠共面。飞行组已在 cuboid-fliers-final-01 通过44阶段真实客户端验收，并复查了原始游戏截图。

## 技术参考（固定源码版本）

- [Blockbench bedrock codec](https://github.com/JannisX11/blockbench/blob/7c92e27d237e365110030d73e92c5d1605f0d311/js/formats/bedrock/bedrock.js)：导出 cube origin 的 X 镜像、X/Y 旋转符号、骨骼绝对 pivot 与 per-face UV；上下面 UV 可负向，几何与编辑器坐标不能重复翻转。
- [GeckoLib Forge 1.20.1 BakedModelFactory](https://github.com/bernie-g/geckolib/blob/7d6f32db9168a24e14b327c0ad9f8f87dfc204de/Forge/src/main/java/software/bernie/geckolib/loading/object/BakedModelFactory.java)：1/16 单位转换、父骨与 Cuboid、box/per-face UV 的加载语义。[GeoModel](https://github.com/bernie-g/geckolib/blob/7d6f32db9168a24e14b327c0ad9f8f87dfc204de/Forge/src/main/java/software/bernie/geckolib/model/GeoModel.java)按具体资源路径选择模型、动画、贴图；默认可能忽略缺骨，因此本任务另行验证动画引用。[BakedAnimationsAdapter](https://github.com/bernie-g/geckolib/blob/7d6f32db9168a24e14b327c0ad9f8f87dfc204de/Forge/src/main/java/software/bernie/geckolib/loading/json/typeadapter/BakedAnimationsAdapter.java)将秒转 20tick 并读取数字关键帧。本项目运行依赖固定 4.8.4，没有照抄新版 API。
- [blockbench-plugins GeckoLib codec](https://github.com/JannisX11/blockbench-plugins/blob/91ac60fa067008937393e88c902f8871406f55ed/plugins/geckolib/src/ts/codec.ts)与 [events](https://github.com/JannisX11/blockbench-plugins/blob/91ac60fa067008937393e88c902f8871406f55ed/plugins/geckolib/src/ts/events.ts)：GeckoLib 格式复用 Bedrock 几何编解码，支持单贴图、骨架、逐面 UV 与动画文件；插件会处理导出动画符号及插值。资源直接保存最终导出格式，避免额外插件转换造成双重镜像。未复制这些项目的美术或程序代码；软件审查工具复用本仓库已有 Cuboid 栅格审查实现。

生成器：tools/art/secondary-cuboid/build_models.py；审查：review_models.py；原生客户端：qa.init.gradle + run_native.py。隔离工作树为 `/Users/a15356015027/.codex/worktrees/cod4-cod6-mining-upgrade/dynasty`，分支 `codex/secondary-cuboid-art-20261010`。源冻结记录 source-snapshot.json，避免读取其他聊天正在改写的编译输入。
