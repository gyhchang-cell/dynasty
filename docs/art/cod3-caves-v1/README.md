# 水晶穹顶与玄冰蓝洞 · 常驻方块结构

清单的 scenic_09、scenic_24 已接入真实压缩 NBT 和原版世界生成。两者均为 31×19×31 的一步拼装洞穴，使用原版方块与像素贴图，不增加生物、AI、碰撞实体、方块实体、奖励、音效或运行中的地形扫描。

| 场景 | 结构/模板 ID | 实际内容 | 自然生成 |
|---|---|---|---|
| 地底星汉·水晶穹顶 | dynasty:scenic_crystal_canopy | 深板岩阶梯洞壁、收窄穹顶、紫晶柱和五个发光星结，方解石阶梯星图 | 主世界生物群系，地下高度 -40～-24；间隔 80 区块、分离 28 |
| 玄冰蓝洞·万年冰花 | dynasty:scenic_ice_bloom | 浮冰洞壁、蓝冰阶梯花簇、壁面晶体、露出的发光端头、防滑方解石十字通路 | 七种原版寒冷群系，地下高度 -40～-24；间隔 96 区块、分离 32 |

文件在 `src/main/resources/data/dynasty/{structures,worldgen/structure,worldgen/structure_set,worldgen/template_pool,tags/worldgen/biome/has_structure}/`。源为 `tools/art/cod3/scenic_caves.py`，详细导出块布局在同目录的 `.blocks.json`；[manifest.json](manifest.json) 记录大小、方块色板和空入口。十个运行文件再生成字节不变。

真实使用标准 `minecraft:jigsaw`、单模板、深度 1 和 rigid 投影，没有递归连接件，最终只有一片。测试发现并修正 1.20.1 深度 0 虽能解析却不会加入根片段的行为。生成只作用于新区块；放置后按普通区块保存，不计时消失、无需周期重建，玩家后续改造也不会被重刷。既有区块没有自动补挖。自然随机奇观不再启动 09/24 的旧计时光场，目录编号和其他奇观逻辑保留。

中间四向通道均有 5 格宽、4 格高净空和连续地面。晶柱/花簇放在通道外，发光端头至少一面接空气；自查修正了早版直墙、被封住的灯、外露花簇位置与刻板直角星线。其余壳体在地下不可见，保留洞壁厚度；模板外的天然地形保持原有生成。

构建和六项独立 GameTest 通过，其中两项在真实 ServerLevel 里放置两份 NBT，检查地面、头部净空、光源、空实体数据和 NBT 保存加载；通过实际注册的 JigsawStructure 生成，确认一片、31 格横向包围、地下高度和冷群系约束。另四项继续覆盖三个远景模型的实际 GeckoLib 烘焙和场景保存/包协议。参考 [六项测试凭据](headless-PASS.txt) 与 [最终验证](verification.json)。自然生成位置搜索和图形画面仍待实机检查，未把单模板放置当成全部整合包试玩。

软件检查直接读取交付的压缩 NBT，并从本机 Minecraft 1.20.1 `client.jar` 逐面采样原版 PNG，附五方向剖视。为了看见内部，剖视移除部分前壁与上顶壳，图上有明确标注；这些不是游戏截图，也没有复制原版 PNG 到 Dynasty。

- [水晶穹顶剖视](scenic_crystal_canopy/45.png)
- [冰花洞穴剖视](scenic_ice_bloom/45.png)
- [软件校验](software-validation.json)

复验：`python3 tools/art/cod3/scenic_caves.py` 再导出；带 Pillow/NumPy 的 Python 执行 `tools/art/cod3/review_caves.py` 检查实际 NBT；独立构建使用 `-I tools/art/cod3/scenic-server.init.gradle build runGameTestServer`，追加 JDK17 和隔离构建参数。管理员可通过原版 `/locate structure dynasty:scenic_crystal_canopy` 或 `/locate structure dynasty:scenic_ice_bloom` 查找新区块中的位置，通过 `/place template dynasty:<模板ID>` 检查模板。测试不修改参考存档。

包含三模型和两洞穴的最新本地包为 `build/cod3-scenic-20261011/dynasty-1.4.0-cod3-scenic-caves.jar`。完整视觉提示尚待实机画面验收，因此清单的两条洞穴整行保留；没有宣称所有 cod3 任务完成。
