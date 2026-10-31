# 竹甲、织锦袍、朱砂符甲：十二件旧图重绘

2026-10-26，接续用户“继续做没做过的差贴图”的直接授权。三套十二张物品栏图标此前未进入获选原稿集，现已逐件用内置 imagegen 重做并覆盖项目、已有本地 Dynasty JAR 与三种导出的现存副本。精致旧图、已认可高阶套装、所有穿戴 UV 保留。

竹甲按早期便宜装备处理：宽竹片、草黄截面、粗绳固定，不添加黄金宝石。织锦袍依材料源码的官服轻甲定位，用折布帽、交领和宽绣边，避免通用金属甲换紫色。朱砂符甲依符纸与朱砂的真实材料定位，用大符纸面、朱砂印笔与红绑带，区别普通红甲。

制作前实际查看旧图筛选页、原版四件盔甲轮廓、上一轮获选原稿和既有千图参考中的一页；沿用已经留档的 1000 张去重盔甲图标参考，不声称本轮重新研究一千个项目。来源与观察见 [reference-study.json](reference-study.json)。不复制参考像素。

每件完整提示词及生成路径见 [generation/](generation/)，全部提示词汇集于 [plan.json](plan.json)，完整生成原稿见 [sources/](sources/)。运行 PNG 只做透明裁边、补齐方形透明画布与 2px 透明边，主体 RGBA 逐像素保持，没有降采样或量化。方形画布用于避免原版挤出路径将长宽不同的图标拉伸；不以修改原稿内容解决比例问题。获选边界与源文件由 [selection.json](selection.json) 和共享原稿发布器登记，后续可重现。

已实际检查 [after.png](after.png)、[comparison.png](comparison.png) 和 [inventory-32px.png](inventory-32px.png) 的外形、材质区分与缩略可读性。它们是实际运行资源预览，均非游戏截图。

- 无窗口原生检查：Minecraft NativeImage 解码、ItemModelGenerator 的 18480 个挤出面及 UV 范围、图集 codec，12/12 通过；只启动一次无窗口 Java 检查，没有开启游戏客户端。
- 全体 456 件原稿像素检查通过，构建 JAR 中 913 个对应资源条目一致。
- 本地 6 个现有 JAR、6 个现有导出副本均回读通过，每份 25 个目标资源条目。仅补丁覆盖本批 PNG、物品模型、图集过滤；其他代码、模组、FTB 任务及配置等 ZIP 负载逐项保持。
- 56 张穿戴 UV、642 张范围外物品图、26 张状态图标哈希不变。两张并行修改的鲁班 Boss 贴图已保留，没有写回。

本轮不包含帝王/门派动态图案制作、穿戴效果重做或游戏内验收。COD4 动态图案研究仍是另外的 171 处已核对实现，尚未达到单项 1000 门槛；这批库存图标和千张美术参考不充抵该计数。当前 cod4/cod6 待办是行为、视觉实机或联机整项，本批图标交付不满足整项删除条件，因此没有删清单。未推送 GitHub，未重启现有客户端，未动用户存档、声音、亮度。

证据见 [final-check.json](final-check.json)、[source-check.json](source-check.json)、[preservation-check.json](preservation-check.json)、[native.log](native.log)、[DELIVERY.json](DELIVERY.json)、[installed-readback.json](installed-readback.json)。
