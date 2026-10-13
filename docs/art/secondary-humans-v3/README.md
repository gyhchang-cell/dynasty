# 五名次级人类：自然比例与原创像素

实际资源、编辑器源、冻结构建和真实 GeckoLib 4.8.4 面烘焙已通过；新版客户端画面 **PENDING**。本轮没有启动图形客户端，先前显示器不可用的 GLFW 失败未重试。没有改声音、亮度或关闭用户正在运行的愚者存档；仅在本地修改。

对象为普通人类 `bandit_thug`、`night_watchman`、`herb_picker`、`famished_refugee`、`swindler`，遵循用户最新版《建模要求.txt》00.10、11、19、20。没有把百姓改为怪物，也没有修改纸剪童子等非人类、其他聊天的 Boss/精英/奇观/FTB。

先修正轮廓：头部由窄长4×5×4改为6.5×6.5×6；表情与发际线绘入头部UV，原悬浮眉眼、长鼻与下巴体块退出几何；保留旧jaw骨名。胸/腰/骨盆分别组织，山匪胸宽7.5、其他正常角色7、饥民6；四肢保留肩肘腕、髋膝踝层级，前臂2.5×4×2.5、脚3×2×4。帽冠按头部适配。道具、握点、原骨架层级与95段动画保留：巡夜提灯/梆子、背篓草帽/镰刀、驼背行囊/手杖、长袍/算盘、单肩护甲/佩刀形成职业轮廓。碰撞仍为0.6×1.8格，Renderer无新增整体缩放。

实际重新查看了用户提供的 [Human Companions人物图](https://media.forgecdn.net/attachments/423/810/models.png)：参考方脸、眼白、发际线、腰带、袖口及靴子的层次，未复制任何像素或模型。参考图片仍在本地私有 `build/maintenance/npc-art-references/human-companions.png`，不打入游戏。

| ID | 图集/纯色数 | 当前体块/面 | 改前面 |
|---|---|---|---|
| bandit_thug | 128×128 / 20 | 31 / 186 | 228 |
| night_watchman | 128×128 / 23 | 28 / 168 | 210 |
| herb_picker | 128×128 / 21 | 30 / 180 | 222 |
| famished_refugee | 128×128 / 18 | 26 / 156 | 198 |
| swindler | 128×128 / 19 | 32 / 192 | 234 |

逐面像素UV、两像素外扩留边，肤色/头发/布料/皮革/木金属由有限纯色表达，正背面衣领和脸发不重复，没有滤镜、噪点、渐变或外部贴图。图集尺寸依用户19.3选择；不再沿用这五人的旧16px四色肖像策略。其余23只历史策略、另三只64px机关/岩兽图集保留。

`software-views.png`与`software-before-after.png`已实际查看正面、45度、左右侧、背面、纯黑剪影；`software/`另有灰模和代表移动/攻击。前后及同批使用公共世界包围和同相机。**这些全部是软件诊断，不是游戏截图，也没有声称已与实机玩家同框验收。** 具体世界尺寸见 `validation.json`；帽冠/持杖等可见包围不等同于碰撞箱。

权威几何源：`tools/art/secondary-cuboid/build_humans.py`；贴图/UV源：`human_atlas.py`。`pixel16.export`已接入五人例外，旧几何生成器最终导出不会恢复旧四色图。运行文件仍为 `assets/dynasty/{geo,animations}/secondary/<id>` 和 `textures/entity/secondary/<id>.png`，原 `expansion/ExpansionClient` 绑定不变。`blockbench/`五份真实bbmodel嵌入当前PNG，附原动画文件。

验证：`check_humans.py`确认源与资源逐字节再生成一致、骨名/父子关系保留、95动画字节保留、逐岛留边、编辑器体块和图集对应、五道具实际手掌/柄接触；2375个姿态采样仍在原渲染包围内。`verify_models.py`确认31实体/589动画。真实GeckoLib烘焙147 Cuboid/882面并逐顶点核对UV，见 `native-bake.log`。冻结5130源文件的离线build/reobfJar通过；Jar内15个geo/PNG/动画与本地资源一致，未包含QA代码，见 `verification.json` 和 `build.log`。构建期间其他源继续更新，冻结Jar没有覆盖共享整合包Jar。

提示词先备份在 `build/maintenance/secondary-humans-v3/prompt-before/`。本轮没有删除cod4/cod6条款：仍欠新版实机画面、与实际玩家同框、原版基础面数上限、自然生态和真人联机等验收。这里只证明比上一版减少210个面，未声称已低于原版基础怪预算。后续不要用旧版客户端记录证明本版通过，也不要为验图唤醒屏幕。
