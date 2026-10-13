# cod3 三套原创奇观资源 · 2026-10-11

已替换青苍龙影、玄武负岳、金乌巡天的程序化占位造型，接入实际 GeckoLib 模型、逐面像素 UV 和四秒循环。三者分别是长体游龙、负山龟蛇和三足鸟，使用独立非人形骨架。资源已打包，实机画面验收待完成。

| 场景 | 运行资源名 | 骨骼 | Cuboid 近/中/远 | PNG | 四秒动作 |
|---|---|---:|---|---|---|
| scenic_01 青苍龙影 | azure_dragon | 21 | 62 / 50 / 26 | 256×256 | 九节躯干依次游动，龙须轻摆 |
| scenic_10 玄武负岳 | mountain_xuanwu | 15 | 56 / 47 / 21 | 256×256 | 四肢对角相位划水，龟首和背蛇独立转动 |
| scenic_25 金乌巡天 | sun_crow | 12 | 48 / 45 / 23 | 128×128 | 翼根与外翼分层扑动，三足收放、尾扇微摆 |

资产在 `src/main/resources/assets/dynasty/{geo,animations,textures/entity}/scenic/`。几何另有 `_medium`、`_far` 文件，共享对应 PNG 和动画。原始生成源是 `tools/art/cod3/scenic_resources.py`；[Blockbench 源文件](blockbench/) 内嵌对应 PNG，旁边保留同名可导入动画。再导出得到的 21 个文件与当前字节相同，见 [确定性检查](determinism.json)。

加载链是 `ScenicEvents → Cod3VisualPacket → Cod3VfxRenderer → ScenicModels → GeoObjectRenderer → 实际资源`。保持三个编号、条件、时长与服务端逻辑。没有注册新生物、碰撞、AI、掉落或任务。锚点距离 ≤32 / 32–96 / >96 使用不同模型，MINIMAL 强制远档；继续共用大型效果 3/2/1 的数量预算。靠近实际模型 24 格内淡出，40 格外达到正常透明度；飞行轨迹和动画都按原始服务器开始时间推进。场景结束、离区与换世界会释放 Actor，缓冲只清本渲染器拥有的 BufferSource。

按实际面长宽分配 UV，窄面至少两像素，图集面岛留边。材质使用离散色阶、清晰块面和稀疏鳞片/羽片，不做模糊、渐变或随机噪点。已修复初版方形面岛拉伸、金乌全金配色、直龙身、玄武腿部同相和几处不同材质共面。全比例运动包围约为龙 18.9×10.0×56.8 米、玄武 27.3×21.0×43.4 米、金乌 31.6×12.2×26.8 米，均只是无碰撞远景；实际数值、资源 SHA 与 81 次动作采样见 [软件检查](software-validation.json)。

各目录包含正面、45°、左右侧面、背面、灰模、纯黑剪影、弱光、两档简化和统一世界比例对照，以及 `idle.webp`。图上均标明软件预览，直接逐面读取实际 PNG，使用最近邻；没有把预览当成游戏截图。预览修正了正背观察方向和动作包围的八角取景。

- [青苍龙影检查图](azure_dragon/overview.png)
- [玄武负岳检查图](mountain_xuanwu/overview.png)
- [金乌巡天检查图](sun_crow/overview.png)
- [参考记录](references.md)
- [最终构建与验收状态](verification.json)
- [四项无界面 GameTest 证据](headless-PASS.txt)

最终 reobf JAR：`build/cod3-scenic-20261011/dynasty-1.4.0-cod3-scenic.jar`。15 个模型/动画/PNG 在 JAR 内逐字节匹配当前资源。QA 源集和测试模板未进入发布包。`tools/cod3/verify_assets.py` 已修正历史 NPC 16px 固定限制，按现有图集声明和逐面 UV 检查；目录 160 定义、15 NPC/165 状态、45 地标校验通过。

仅一次图形客户端实际启动尝试，在更早的资源版本上被 Forge 的 `Can't find a primary monitor` 阻挡，未进入世界。没有原生截图、资源重载或 GL 状态 PASS。保持显示器休眠状态，没有调整亮度；用户的参考客户端继续运行。已修正用于后续复验的 QA 视角和 LOD 选择，但最终版本没有实际运行这个图形 QA。

复验软件资源使用带 Pillow/NumPy 的 Python 运行 `tools/art/cod3/review_scenic.py`。四项无界面测试使用 `-I tools/art/cod3/scenic-server.init.gradle runGameTestServer`；构建时追加项目 JDK17、独立 Gradle 缓存和 `tools/cod3/isolated-build.init.gradle`。客户端入口 `scenic.init.gradle runClient` 仅生成 launch.json；显示器可用时冻结该配置再运行 `run_scenic_client.py`。测试只创建 `build/` 下的临时世界，不打开参考存档。

这里只删去了两条已经证明完成的服务端无实体约束。三个奇观的完整提示继续保留，等待实机画面验收。后续水晶穹顶与玄冰蓝洞已接入真实常驻方块结构和世界生成，见 [两洞穴批次](../cod3-caves-v1/README.md)；其余 20 处完整表现、故事与生态状态仍有未完成工作。
