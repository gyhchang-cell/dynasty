# 金乌巡天 · 第二轮

对象：scenic_25，清晨晴天的无碰撞、无AI、无声远景鸟形。资源ID仍为sun_crow；服务端事件40秒、原位置/种子/起始时间、x4世界缩放不变。没有更改任何Boss、战斗判定、任务奖励。

本轮逐页查看247张候选画面，选入100张新参考、11个模组；以SHA256排除已有cod3参考，来源见references.json及reference-notes.md。接触表记录所有候选，不把其中未入选的图标/界面算作参考。

## 实际改动

- 胸部连接短颈、头喙、双翼、尾部、三足；保持12根非人形骨骼、48块原有Cuboid，没有新增人形模板或圆滑曲面。
- 双翼先缓抬、再下压、接滑翔；外翼延迟，尾部配平。循环4秒/80tick，首尾一致；由服务端包的绝对年龄驱动，迟到观察者不会重新起拍。
- 两前足向两侧移动，中央后足更低且前后错开，胸下连接保留；纯黑正面/背面和侧面检查三足结构。
- full/medium/far为48/47/27块，骨骼层级和旋转轴相同。medium保留眼睛，far保留主翼、阶梯翼尖、喙与三足。
- 晴天清晨结束或下雨时，客户端不再继续显示未过期的金乌；仅影响scenic_25。
- 保留现有128×128硬边像素UV和PNG原始字节；没有替换、缩放或模糊贴图。SHA256：51887d8f4ae4b0c763433a78f65f2e6e71d0ed2147d39a9837682381600cf1a9。

## 可编辑源与导出

`tools/art/cod3/scenic_resources.py` 的 crow() 是形体/动画源；只更新金乌、保留原图集用 `python3 tools/art/cod3/update_sun_crow.py`。Blockbench源及单独动画在blockbench/，同时同步旧scenic-v1源目录，避免旧源覆盖新资产。正式资源位于assets/dynasty的geo/scenic、animations/scenic、textures/entity/scenic。

`sun_crow/`中的五方向、灰模、黑剪影和动作联系表是软件预览，取当前正式资源，不冒充游戏画面。最终v5原生复验和人工复查通过，已从两份任务清单删除奇观#25。

## 动画时钟与渲染集成修正

实机帧比对发现旧共同控制器把完整包年龄直接送给循环动画，超过第一轮后卡在末帧。现在按当前烘焙动画长度取绝对包相位；金乌的实际翼骨角度必须和资源文件按包年龄插值得到的角度一致，不能仅凭非零角度判定动画在运行。青龙/玄武共用的循环时钟同步修正，但它们本轮没有完成各自美术验收，清单仍保留。

按本地GeckoLib4.8.4实际字节码与[官方GeoObjectRenderer源码](https://github.com/bernie-g/geckolib/blob/1.20.1/Forge/src/main/java/software/bernie/geckolib/renderer/GeoObjectRenderer.java)核对：null顶点buffer会替换调用者的BufferSource，现明确传入自有顶点buffer，隔离批次提交。

## 最终验收

81组软件动画/UV/骨骼检查、6项专用服测试、17项原生场景/34张开关对照图通过。逐项检查正面、45度、左右侧、背面、远近与最低画质、雨夜禁用、重载、包相位及迟到观察者。实际失败轮次与修正记录见qa-corrections.md。

本地合并包：build/cod3-sun-crow-20261018/dynasty-1.4.0-cod3-scenic-20261018.jar；SHA256 954ffb6d334acd30f4e6be7fcac817167d4bf0bc1b0dd6e67e70d9da7473a374。包含先前验收的银瀑、古阵、水晶穹顶，核对原有class/资源字节一致；测试代码未入包。
