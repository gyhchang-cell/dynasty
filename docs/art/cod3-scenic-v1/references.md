# 本批实际参考与原创边界

先读取用户新版《建模要求.txt》，按其非人形、真实 UV、专用运动和实际运行绑定要求制作。参考工具接口沿用项目 Forge 1.20.1 / GeckoLib 4.8.4；没有升级依赖。

用户已打开的愚者客户端继续运行。当前工具无法选中 Java 游戏窗口，系统显示器处于不可供新 LWJGL 客户端取得主显示器的状态，因此未声称在参考存档中实地观察。本机整合包位置为 `/Users/a15356015027/Public/.minecraft/versions/愚者chishi`，核实包含暮色森林 `1.20.1-4.3.2508`、Goety `2.5.36.1`、灾变 `3.16`。

青苍龙影参考本机暮色森林 JAR 中 `twilightforest/client/model/entity/NagaModel.class` 的实际 Cuboid 与渲染结构，使用 javap 读取头部、身体和 NagaSegment 分工：学习长体生物的头身辨识，自己的模型改为九节逐渐收细的连续骨架、独立颌部、分叉角和四个小肢体。没有复制娜迦的贴图、模型数据、动作或多实体战斗结构。

玄武负岳参考同 JAR 的 `HydraModel.class`，实际查看宽大主躯干、支撑足、尾和多节颈模型构造。学习宽体量的承重与分节器官连接；本批使用原创分层龟甲、山脊、四肢、龟首与壳上背蛇，不沿用九头蛇的外形、头数或战斗。其背蛇不是普通人形脖子替代品。

金乌巡天参考同 JAR 的 `RavenModel.class` 和 `TinyBirdModel.class`，实际查看头/喙、鸟胸、左右独立翼、尾与脚，以及翼部反向摆动。学习鸟体支点与短喙的分工；本批重新做长跨度的分层羽片、三足、深褐主体和少量金色喙/羽尖，没有复制暮色乌鸦的模型、PNG 或动作曲线。

另实际查看灾变作者官方图库的 [Ignited Revenant 展示](https://media.forgecdn.net/attachments/510/175/2022-10-30_21.png)，可观察深色主体、周边独立板片及少量暖色亮部。只借鉴材质主次和 Cuboid 的读形方法，没有给这三种生物套用其盾片、核心、造型或纹理。官方图库入口为 [Cataclysm](https://www.curseforge.com/minecraft/mc-mods/lendercataclysm/gallery)。一张可打开的封面只含 Logo、另一张图片返回 404，均未作为观察模型的证据。

本批全部 runtime PNG、Geo 和循环动画由项目原创源生成。外部模型字节、材质、动画、音效和建筑没有进入 Dynasty 资源或参考交付目录；本机字节码查看记录只保留在隔离 `build/cod3-scenic-20261011/` 中。
