# cod3 NPC Cuboid 资源重做

2026-10-11。本轮直接替换已有 15 个 NPC 的模型、动画和贴图，保留实体 ID、原资源路径及 `animation.npc.*` 十一个状态名。此次没有修改生产 Java 的战斗、任务、AI、注册或伤害逻辑。

先看过全部角色的现有 Forge/GeckoLib 渲染：[原模型对照](before.png)。原骨架已有胸、腰、骨盆分段；问题是各角色比例、帽型和动作相似，手持物多数固定在胸骨，旧贴图生成器加入随机噪点。首批选择百宝金、黑婆和墨机子，分别强化行囊体积、驼背姿态和机械半身，之后重做其余十二个。

## 实际资源及制作规格

运行时文件在 `src/main/resources/assets/dynasty/geo/npc/`、`animations/npc/`、`textures/entity/npc/`。每个角色一份 geo.json、一份 animation.json、一张 PNG，共 45 份实际资源；`blockbench/` 保留十五份内嵌贴图的 bbmodel 和可导入 Animation 模式的配套动画 JSON。

编辑时在安装 GeckoLib 插件的 Blockbench 中打开对应 bbmodel，再在 Animation 模式导入同名 animation.json。源文件包含内嵌 PNG，不依赖本机绝对贴图路径；不要重新导出成 Java Vanilla 模型。修改后维持相同资源 ID，并重新核对运行时资源、动画和源文件。

每个模型 41–60 个 Cuboid，30–36 个骨骼。人形层级为 `root → pelvis → waist → chest → neck → head`；肩、上臂、肘、前臂、腕、手和大腿、膝、小腿、踝、足分别分层。护甲、衣裙、背包、披风和机械钳附于对应躯干或关节。手持物挂在手骨上，拥有与掌心一致的 pivot/locator；药碗及古琴有抵消前臂倾斜的动作姿态。

成人胸宽 5.5–10 模型单位，胸深 3.5–7；头宽约 5.5，成年人整体接近 1.9 米，小圆子约 1.4 米。只用长方体、粗阶梯和少量平面，古琴七弦为七条平面；无球、圆柱、圆滑曲面或写实细分。体型及主要部件规划如下：

| 角色 | 主要体块及轮廓 | idle / work |
|---|---|---|
| 百宝金 | 宽腹、三层行囊、腰包、算盘 | 拨算珠 / 另一手拨算盘 |
| 黑婆 | 前倾胸背、背部驼峰、银辫、肩蜈蚣、长裙 | 端药碗 / 搅药 |
| 墨机子 | 左半胸甲、粗义肢、肘框、开合机械钳、三叠目镜 | 开合钳 / 改装动作 |
| 老陈 | 粗前臂、厚围裙、眼罩、阶梯胡须、锻锤 | 站立呼吸 / 提锤落锤 |
| 韩冲 | 厚扎甲、护耳铁盔、肩甲、环首刀 | 扶刀远眺 / 巡视，walk 不对称跛行 |
| 青玄子 | 细腰长袍、竹簪、两级葫芦、竹简卷轴 | 持卷静立 / 展卷手势 |
| 阿吉 | 窄胸细腰、歪肩、残甲片、麻绳束带 | 轻抖 / 警惕张望 |
| 曹承福 | 横翼礼帽、宽袖、长紫袍、拂尘、夜间灯笼 | 叠袖侍立 / 俯首侍候 |
| 红菱 | 外扩布裙、长发、花篮、独立两节蛇尾 | 持篮 / 招呼，react/danger 显示蛇尾 |
| 楚弄玉 | 白蒙眼带、广袖黑裙、长发、七弦古琴 | 抱琴 / 右腕拨弦 |
| 小圆子 | 放大头身比、双抓髻、药篓、铜铲 | 小幅跳动 / 挖药 |
| 赛半仙 | 阶梯墨镜、长衫、白布幡、铜钱 | 摇钱 / 翻腕占卜 |
| 巴图 | 宽厚肩胸、狼皮帽、厚皮袄、阶梯猎弓 | 持弓 / 俯身布置陷阱 |
| 燕赤风 | 破阶梯斗笠、裂尾披风、双剑 | 披风轻摆 / 磨剑手势 |
| 黄老汉 | 短水靠、短裤、裸小腿、宽笠、竹节篙 | 持篙静立 / 推拉撑船 |

所有新 NPC PNG 为真实 **16×16、四种纯色** 的原创正面像素肖像。四周两格白边，各色块最小 2×2；模型逐面 UV 取对应肖像内的纯色岛，白色前景配饰与未使用背景分开取样。没有模糊渐变、抗锯齿或噪点，放大审阅只使用最近邻。后续资源继续遵守资源目录 AGENTS.md 的用户规范。

## 三个技术参考的实际应用

- [Blockbench 的 Bedrock codec](https://github.com/JannisX11/blockbench/blob/master/js/formats/bedrock/bedrock.js)：核对 cuboid origin/size、父子骨骼、pivot、逐面 `uv`/`uv_size`，以及编辑器和 Bedrock 导出之间 X 坐标、X/Y 角度及上下 UV 的转换。bbmodel 按该坐标关系生成，并逐一与运行资源核对。
- [GeckoLib 1.20.1 GeoModel](https://github.com/bernie-g/geckolib/blob/1.20.1/Forge/src/main/java/software/bernie/geckolib/model/GeoModel.java) 和 [AnimationProcessor](https://github.com/bernie-g/geckolib/blob/1.20.1/core/src/main/java/software/bernie/geckolib/core/animation/AnimationProcessor.java)：核对资源分路径、加载缓存、骨骼初始旋转与动画叠加，以及动画不存在/骨骼不存在的处理。实际验收使用项目已安装的 GeckoLib 4.8.4，而非升级依赖。
- [Blockbench Plugins 的 GeckoLib codec](https://github.com/JannisX11/blockbench-plugins/blob/master/plugins/geckolib/src/ts/codec.ts)：核对 GeckoLib 项目格式、逐面 UV 和声明贴图分辨率。参考格式实现，不复制其他模组模型或贴图，也不声称已经通过 MCP 操作 Blockbench。

## 审阅与验证

[首批及校尉五视角](review-1.png) · [隐士至琴姬五视角](review-2.png) · [药童至艄公五视角](review-3.png)。每行依次为正面、45°、90°侧面、背面和纯黑剪影。它们来自实际 Forge OpenGL 环境加载运行时资源后的 GeckoLib 渲染。检测所有 75 幅图的非空、完整画幅和纯黑剪影；复审时扩大背面镜头，避免行囊遮近镜头而裁掉帽顶。

静态验收见 `resource-validation.json`，检查父子拓扑、胸腰骨盆、手持物 pivot、逐面整数 UV、四颜色、两格白边、最小色区、循环首尾和时间长度，以及 bbmodel 的骨骼坐标和内嵌贴图。全部 165 个动画名通过实际 GeckoLib 加载。

原始资源保存在忽略的 `build/cod3-art-20261010/original/`。生成器 `tools/art/cod3/rebuild_npcs.py` 可复现资源；旧 `tools/cod3/build_npc_resources.py` 入口已转到新生成器，防止目录再生成时恢复通用模型和噪点贴图。导出源文件用 `export_sources.py`，静态检查用 `validate.py`。实机及构建最终证据见 `verification.json`。

最终验收包含两客户端各 210 个完整场景、300 张截图；琴姬及黑婆动作调整后各追加 28 个场景、40 张截图，最后再对黑婆的搅药动作各检查一场、两张截图。合计 478 个场景、684 张真实游戏截图。`native/` 保留全部数值证据及精选正面、45°、侧面、背面、work、walk、react 图，完整截图仍在 `build/cod3-client/`。

两个客户端通过普通实体同步包接收测试姿态，在临时平坦世界使用正式 `Cod3NpcRenderer`、资源缓存和动画控制器。测试夹具固定位置并强制状态，验证的是美术加载、各状态动画、握持及缩放，不用于宣称 AI 或剧情行为已经完成。动态骨骼两帧采样均有变化；手持道具挂点至手骨的最大距离约 0.0626 米。两格羊毛柱作为游戏中两米高度参考。末场执行真实资源重载。

全量测试的一次 Host 结束流程遇到 Peer 先退出的竞态，300 条真实检查当时已全部记录。仅在该临时测试 JVM 内调用已有完成导出方法恢复记录，没有补造场景或数值；`native/host/completion-recovery.txt` 留痕。测试源文件已修正结束检查顺序，后续两次针对动作的检查正常自行退出。

最终 Jar 为 `build/cod3-art-20261010/dynasty-1.4.0-cod3-npc-art.jar`，SHA-256 `b9b51847dffd47f3f6885c70bdd3448ecebca2537932c49b7408ec992a2b2b4d`。已逐份核对 Jar、最新源资源及对应实机运行快照的 SHA；QA 类不在发布包内。构建使用独立输出目录及独立 Gradle 项目缓存，避免并行开发的编译输出互相清理。本轮没有提交或推送 GitHub。

验收后已从外部 `cod3.txt` 及项目内镜像删除两条已完成的通用建模要求：人形关节分段及十五个角色的独立造型/随身物/idle。删除原文和依据保存在 `docs/cod3/deletions-20261010.json`，剩余清单 1443 行。

本目录记录美术交付。原 cod3 表内牵驴、赠犬、剧情解锁、战斗击杀和世界状态等复合要求不能仅凭模型检查判定完成，因此仍保留在原任务清单；未注册的设计 Boss 不通过本轮创建战斗实体。其他开发者正在处理的 Boss 美术也没有覆盖。
