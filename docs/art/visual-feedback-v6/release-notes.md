# 2026-09-25 · 第六轮视觉与宝库反馈

- 12张盔甲图标：将军、玉甲、天界各四件，正面平面轮廓。保留穿戴模型。
- 宫砖、玉矿、龙晶矿替换为32×32像素方块纹理。本轮没有重绘全部方块。
- 手持48件及弓24模型帧改为真实几何父模型，避免Minecraft自动生成器覆盖封边；原图像未缩减。
- 青龙下落躯干轴向延长25%。
- 四派新增11段既有武器的锻造进化，非11件全新注册物品；删除下方重复图鉴链接，保留旧任务进度。
- 新机关宝库净空间13×8×5，双材料箱、信标遗物台、照明/红毯/工作区；箱子不因重复交互补货。
- 新布局版本3；老结构继续旧布局，不覆盖已经生成的建筑，不修改存档。

## 复现与交付

`python3 tools/art/package_visual_feedback_v6.py` 导入已审阅的图像生成结果；仅做裁切、缩放、留边。源图与原资源均保留。
旧版 `package_build_feedback.py` 会恢复旧盔甲图，若运行它，必须随后重跑v6美术打包；勿将旧画廊当本轮产物。
构建后运行 `package_visual_release_v6.py` 核对JAR所有资源与源文件一致并制作更新包。
`deploy_build_feedback.py --payload dist/dynasty-visual-feedback-v6-update.zip` 只更新JAR/任务，自动备份，拒绝在目标实例运行时安装。

## 验证边界

已完成编译构建、任务/封闭空间/父链验证和离屏模型预览。尚未在用户客户端实拍复核全部手持物品，不应声称全部视觉问题已游戏内验收。
巨型主世界建筑仍为DeepSeek待执行任务，不在本更新包中。桌面Word提供独立文件职责、至少十万有效非空气方块、可通行内装和稀疏生成验收要求。
建筑参考研究：[When Dungeons Arise](https://www.curseforge.com/minecraft/mc-mods/when-dungeons-arise)、[Cataclysm](https://www.curseforge.com/minecraft/mc-mods/lendercataclysm)。仅参考尺度、层次和探索用途，不复制其资源。
