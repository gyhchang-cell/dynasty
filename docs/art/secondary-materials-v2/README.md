# 2026-10-11 夜间续作：机关鼠、木鹊、石精

当前状态：实际资源、编辑器源、构建、GeckoLib 原生面烘焙通过；新版游戏画面 **PENDING**。原生客户端尝试在进入游戏前报告 `Can't find a primary monitor`，未唤醒屏幕，未继续重试。用户的“愚者chishi”进程和存档保持运行；未改亮度、未开启声音、未推送 GitHub。

遵循用户最新版《建模要求.txt》19.3/20/27。这三个目标的图集使用64×64真实逐面UV，分别11/10/8种纯色、两像素外扩留边；历史16px肖像策略继续用于其他28只。参考实际查看的是用户愚者实例中 Goety 2.5.36.1 的 `assets/goety/textures/entity/servants/redstone_golem/redstone_golem.png`：借鉴平静大石面、受力裂缝和材质边界，没有复制它的任何像素、模型或造型。无法读取 Java 游戏窗口，没有声称已在该存档里观察 Boss。

| 实体ID | 实际改动 | 保留 |
|---|---|---|
| clockwork_rat | 木壳顺纹、铜钥匙/口鼻、铁关节和分节尾、双侧青玉眼 | 原专用四足机关体、18骨/29体块、19动画 |
| wooden_magpie | 木翼顺纹、铜翼轴/胸板、铁喙/足爪、正侧背独立UV | 原鸟体与分层翼/翼梢/尾、14骨/27体块、19动画 |
| stone_sprite | 复查后将竖板石身改为低伏岩兽：12×4×11主岩背、错层岩冠、6×3×3前探石面、四个分开的3×1.5×3落足；石灰/苔痕/青玉眼 | 原ID、四足/岩背骨语义、14骨/17体块、19动画及原技能、碰撞、掉落 |

原形状先以灰模/黑剪影检查，石精不通过后返工主体，另外两只保留原有明确机关/鸟形。最终正面、45度、左右侧、背面、灰模、纯黑剪影与代表移动/攻击均已检查实际PNG和逐面UV。`software-views.png`、`software-before-after.png`及`software/` **全部是软件诊断，不是游戏截图**；前后和同批对照使用公共世界坐标包围，避免逐只放大掩盖比例。

权威源是 `tools/art/secondary-cuboid/build_invertebrates.py:rat`、`build_fliers.py:bird`、`build_additional.py:stone` 和 `material_atlas.py`。`pixel16.export`已接入这三个例外，再跑旧几何生成器不会恢复四色UV。运行资源位于 `assets/dynasty/geo/secondary`、`textures/entity/secondary` 和原 `animations/secondary`；`blockbench/`包含三份真实可编辑bbmodel（嵌入对应PNG）和三份原动画。现有 `expansion/ExpansionClient` 注册/Renderer绑定不改。

验证：

- `check_materials.py`：三只源几何完全一致、57动画字节保留、逐岛两像素留边、bbmodel嵌入图/体块数一致；1425个动画包围采样仍在原4×4渲染边界内。完整可见尺寸和包围见 `validation.json`。碰撞仍为机关鼠0.6×0.45、木鹊0.7×0.6、石精0.9×0.85格；未改导航或受击逻辑。
- `verify_models.py`：31个实际资源、589动画通过；新材质策略只适用于这三只。
- `MaterialBakeCheck`：真实GeckoLib4.8.4解析/烘焙73Cuboid、438个面，逐顶点UV在其实际像素岛内；这是无GLFW的原生库检查，不是客户端画面验收。首次缺少GeckoLib内置mclib类的日志保留，补入同一依赖Jar内部的mclib-20后通过，未改生产依赖。
- 最终冻结源的 `build`/reobfJar通过，Jar内9个geo/PNG/动画与当前本地资源逐字节一致。构建/包内证据见 `verification.json`，完整日志在 `build/maintenance/secondary-materials-v2`。没有将冻结Jar覆盖其他开发者继续更新的modpack Jar。

原提示词备份在 `build/maintenance/secondary-materials-v2/prompt-before/`。本轮没有删除cod4/cod6段落：真实客户端、自然生态、基础面数约束和真人联机等相应验收仍待完成，不能沿用旧版客户端截图作为新版完成证据。

继续范围：先读最新Git状态和本文件；不重复启动显示器不可用的客户端、不唤醒屏幕。继续清单中独立且可验证的实现缺口，避开其他聊天的Boss/炼丹方士/奇观/FTB章节。夜间续作已恢复至北京时间2026-10-12 09:00，到时暂停并汇报未验项。下次可做图形测试时，先准备 `QuietWindowAgent`；客户端脚本会拒绝缺少隐藏窗口agent的启动。只停止隔离测试子进程。
