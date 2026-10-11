# 白鹿参考观察与原创设计记录

2026-10-11 实际读取用户《建模要求.txt》，并查看以下官方模型源码和展示图。参考只用于造型方法，没有导入第三方模型、贴图、动画、音效或建筑；未升级 Forge、GeckoLib，也未安装插件。

| 实际查看来源 | 观察到的方法 | 本批采用或保留的区别 |
|---|---|---|
| [暮色森林 DeerModel 源码](https://github.com/TeamTwilight/twilightforest/blob/latest/src/main/java/twilightforest/client/model/entity/DeerModel.java) | 横向躯干、前伸的吻部、单独颈部和左右角枝共同形成鹿形；角枝属于头部层级。源码使用四足模型及长方体，而非人形装备叠加。 | 用这些一般解剖关系复核原创白鹿；本批是更紧凑的躯干、阶梯颈、粗角枝和独立上腿→小腿→蹄骨骼，另有随头变换的衔草挂点。没有复制坐标、UV 或纹理。 |
| [灾变 Ignis 官方展示](https://media.forgecdn.net/attachments/510/182/2022-10-30_21.png)，来源为 [官方 CurseForge 页面](https://www.curseforge.com/minecraft/mc-mods/lendercataclysm) | 实际在浏览器观察：大盾与长剑的体量差异主导剪影，厚边框与暗亮像素分区让装备结构清楚。 | 留作后续重甲小 Boss 的参考；白鹿不套用其武器、盾形、甲片或配色。截图中的光影效果也不变成贴图渐变。 |
| [灾变 Ignited Revenant 官方展示](https://media.forgecdn.net/attachments/510/175/2022-10-30_21.png) | 实际在浏览器观察：环绕主体的分离盾片、紧凑头部和尖角形成明显间隙，暗色大面由少量亮线分区。 | 留作后续悬浮小 Boss 的轮廓方法参考。本批是接地四足生物，不借用悬浮结构。 |

本批直接相关参考是暮色森林鹿的兽形结构。灾变两张为静态展示，不能据此声称观察过攻击蓄力、运动重量或动画关键帧。没有下载或打包这些展示图；以上链接保留来源，交付图全部来自 Dynasty 自己的原生渲染。

白鹿原设计的主躯干为 6×7×12 模型单位，胸部和阶梯颈独立；根骨→身体→胸→颈→头→耳/鹿角/灵芝，身体另接四条上腿→小腿→蹄链和短尾。总计 37 个 Cuboid、23 骨骼，采用待机、对角交替走路、低头、回望、受惊五种循环。鼻帽、灵芝顶盖和白尾尖稍突出相邻色块，避免异色共面闪烁。五视角和黑剪影由实际 GeckoLib 渲染验证。

技术格式继续采用之前已核对的 [Blockbench Bedrock 导出](https://github.com/JannisX11/blockbench/blob/master/js/formats/bedrock/bedrock.js)、[GeckoLib 1.20.1](https://github.com/bernie-g/geckolib/tree/1.20.1) 与 [官方 GeckoLib 插件](https://github.com/JannisX11/blockbench-plugins/tree/master/plugins/geckolib)。实际运行依赖仍是项目的 GeckoLib 4.8.4。
