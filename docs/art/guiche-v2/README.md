# 鬼车九首鸟：Cuboid 美术资源

适用于 Dynasty / Minecraft Forge 1.20.1 / GeckoLib 4.8.4。

## 已交付资源

- `src/main/resources/assets/dynasty/geo/blueprint/elite/guiche_jiushouniao.geo.json`
- `src/main/resources/assets/dynasty/animations/blueprint/elite/guiche_jiushouniao.animation.json`
- `src/main/resources/assets/dynasty/textures/entity/blueprint/elite/guiche_jiushouniao.png`
- `blockbench/guiche_jiushouniao.bbmodel`，内嵌贴图；同目录动画 JSON 可在 Blockbench 的动画模式中导入。

模型使用 224 个长方体，保留全部 74 根骨骼的名字、顺序和父子关系。主要体块是宽胸、收腹、阶梯背羽、分层双翼和五片长尾羽；八条三段颈链分别承载女人面孔、弯喙与下颌，中央第九颈保留断桩。静态展翼宽度 80 模型单位，即 5 格。面孔使用粗眉眼、白面、黑发和暗红泪痕；全部原创，无第三方模型或贴图。

最终贴图为实际 16×16 RGB PNG，白底一像素边距，色区以 2×2 像素为单位。四种纯色包含白色、灰色、炭黑和灰红；各 Cuboid 面复用实际色岛，无透明度、渐变、平滑过滤或隐藏的大图集。`nian_beast.png` 保持原字节。

七段动画名称和长度保持兼容：`fly / peck / bomb / dive / hurt / stunned / death`。啄击接触峰对应 12～72 tick、每 4 tick 一次；血弹 20 tick，俯冲 24 tick。飞行动作增加翼梢和羽片延迟；死亡采用压低躯干、双翼错落展开、颈部向前折叠、收腿着地。第 44～100 tick 的模型最低点不低于地面。

## 查看与验证

- `review.png`：实际导出资源的正面、45°、90°、背面、纯黑剪影和落地死亡姿态；属于软件预览。
- `actions.png`：关键帧软件预览。
- `validation.json`：74 骨父子契约、UV、16×16 四色白边、关键帧和地面范围。
- `native/strict16-final/`：最终资源的隔离原生客户端记录。以 `host/PASS.txt` 及其运行资源 SHA 为完成依据。
- `native/strict16-2/`：七动画十四场景通过；随后视觉检查发现共面闪烁，已错开领圈、喙尖、尾羽、翼尖、发侧和趾尖的接缝，最终复核见上一项。
- `native/strict16-1/`：场景首次渲染前提前读取骨骼的测试失败；随后增加了真实模型渲染等待条件，不作为通过证据。
- `native/solo-2/` 是之前 128×128 版本的历史验证，不作为最终贴图的验证证据；`solo-1` 为已修正的眩晕测试诊断。

本批只完成美术资源验收。实体的生产世界入口、活动战斗重连、服务器重启及完整平衡验收由原开发任务继续维护，不据此删除整只精英的剩余提示词。

## 编辑与重建

技术参考：[Blockbench](https://github.com/JannisX11/blockbench)、[GeckoLib 1.20.1](https://github.com/bernie-g/geckolib/tree/1.20.1)、[Blockbench GeckoLib 插件](https://github.com/JannisX11/blockbench-plugins/tree/master/plugins/geckolib)。源项目在 Blockbench 安装对应插件后打开；独立动画 JSON 需另行导入。源文件的坐标、骨骼、Cuboid 和内嵌贴图已与运行资源核对，尚未声称完成本机 Blockbench UI 的打开操作。

生成脚本使用 Python 3 和 Pillow；预览/验证额外使用 NumPy。完整验证器还检查已有鬼车实体与本地渲染器，须在该子系统接入后运行；此独立美术分支尚不包含该子系统。

```sh
python3 tools/art/guiche/build_model.py
python3 tools/art/guiche/export_blockbench.py
python3 tools/art/guiche/validate.py
python3 tools/art/guiche/review_model.py
```

使用 JDK 17 构建。客户端 QA 单独编译，不进入生产 JAR：

```sh
./gradlew --offline --max-workers=2 \
  -I tools/art/guiche/qa.init.gradle \
  -PguicheArtBuild=build/guiche-art-build build guicheArtQaClasses
```

`run_native.py` 复用项目已经准备好的 Forge launch JSON，将当前编译资源和类复制到一次性运行目录，再启动一个自动退出的测试客户端；不使用玩家存档。没有准备好的 Forge launch 文件时，不可将本工具的运行描述当作已经验证成功。

## GitHub 交付边界

此美术分支以远端 `main` 的 `7286bf6990db0753802fe1e63a355b07ed34f3af` 为基线。该基线尚未包含正在其他聊天开发的鬼车实体子系统，所以本分支交付实际资源、编辑源和美术验证工具，不拷贝其他开发者尚未提交的战斗/任务代码。

共享本地项目已经绑定独立贴图。远端实体代码合入时，应用 `renderer-binding.patch`，将 `GhostBirdRenderer` 的贴图路径改为独立 PNG，并移除旧共享贴图的逐骨骼染色。单独合入资源分支不会在尚无该实体的旧版本中新增实体注册。
