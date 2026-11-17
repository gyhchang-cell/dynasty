# 星辰坠落·流星雨

对应 cod3 奇观 #20；改掉原来在整个 45 秒里一起缓慢下降的菱形点阵。流星现在分批出现，每条只短暂划过天空：淡金方形亮点、三段硬边冷色尾迹，沿自己的世界空间路线快速斜落，再淡出。不会撞地或变成战斗弹射物。

## 参考与原创边界

本项复用已逐张查看的 100 张 [Skyrim 夜空/天气画面](https://stepmodifications.org/wiki/SkyrimSE:Weather_Compares)，用于暗部留白、云层与天空对比，再补看六张《集合啦！动物森友会》流星画面，检查主亮点、长短尾迹和疏密。其中包括 [Nintendo Life](https://www.nintendolife.com/guides/animal-crossing-new-horizons-star-wand-meteor-showers-star-fragments-and-how-to-make-a-wish-on-a-shooting-star-explained)、[GameWith](https://gamewith.jp/atsumori/article/show/196717)、[Neoseeker](https://www.neoseeker.com/animal-crossing-new-horizons/extras/Meteor_Showers) 的实际游戏截图；完整六张来源见 `references.json`。

100 张基础参考与极光任务共用，本项共参考 106 张；两项合计仍是 106 张独立画面，不宣称 206 张或 106 款游戏。图片只保留在本地 build，未复制到运行素材或提交目录。参考的是静态画面和尾迹形态，未声称观看过参考动画视频。

## 接入和联动

`ScenicEventDefinition.of(20)` → `ScenicEvents` 保存与同步 → `Cod3VfxRenderer` → 共用 `ScenicSkyRenderer` → 独立 `ScenicMeteors.mesh`。

沿用主世界平原、晴夜、45 秒、原编号/seed/start。极光与流星共用夜间和天气可见性、寿命/区域淡出、透明面排序、四角近距离剔除及现有清理规则；具体几何和节奏分别定义。预览入口也调用相同正式几何，不另存一份展示用造型。

近/中/远按 20/14/8 条轨迹降级，同一轨迹的坐标与服务器时间在 LOD 间不改变；额外轨迹在切档前淡出。最多 180 个面，实际同时出现的数量更少，无服务端实体、碰撞、音效、伤害、奖励或地形破坏。

`MeteorGeometryQa.java` 直接采样正式代码 2,275 组 seed/时刻/距离，并检查日雨隐藏、有效边界和不同 LOD 的共同轨迹。附带四视角和动图是实际几何的软件投影，**不冒充游戏截图**。最终专用服与原生客户端验收见 `verification.json`。

最终联合构建、五项专用服测试、两项共二十四场景/四十八次实际截图通过。本项清单行已删除并同步到镜像。`native/contact.png` 是当前发布输入的实际游戏截图；软件动图是加速采样预览。完整范围与限制见 [联合记录](../../cod3/continuation-2026-10-18-night-sky.md)。
