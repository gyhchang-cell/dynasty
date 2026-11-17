# 十二件盔甲图标的原版比例微调

用户认可 v28 整体，要求保留设计，只把比例和像素风格稍微拉回 Minecraft 原版。本轮只调整竹甲、织锦袍、朱砂符甲的十二张库存图标，不另起设计，不新增内容。

使用内置 imagegen 逐件编辑 v28 原稿，并以真实 Minecraft 1.20.1 原版盔甲图标为轮廓参考。保留橄榄竹片与绳结、紫色交领织锦、红白符纸三种身份；缩掉头盔外挑边、收敛肩块与部分装饰厚度，轮廓更方、色块更简洁。全部物品模型变换与图集绑定保持字节不变，因此观察到的比例变化来自实际贴图。

靴子第一版收得过矮，已弃用并再次编辑：最终三双宽高比分别约 1.35、1.37、1.42，原版下界合金靴约 1.40。保留直筒与短方鞋头，没有改成宽矮便鞋。弃用稿仅留在 rejected-drafts，不接入游戏。

- [sources/](sources/)：十二张最终完整生成原稿；未压成 16px，未降采样或量化。
- [generated.json](generated.json)：最终获选稿、逐件完整提示词与生成路径；初次提示词见 plan.json，靴子修正提示词见 boot-revision-plan.json。
- [selection.json](selection.json)：运行 PNG 的透明方形裁边与 2px 留边。主体 RGBA 与获选原稿逐像素一致。
- [after.png](after.png)、[comparison.png](comparison.png)、[inventory-32px.png](inventory-32px.png)：实际运行资源的大图、新旧对照与 32px 可读性检查，均非游戏截图。
- [reference-refinement.json](reference-refinement.json)：原版比例与本轮调整范围。复用既有参考，不声称重新看过一千个项目。

验证：一次无窗口 Java 检查完成实际 PNG 解码、13809 个原生挤出面的 UV 及图集 codec 检查。56 张穿戴 UV、642 张范围外物品图标、合计 1102 张范围外 PNG 均保持哈希不变，十二个模型 JSON 也保持字节一致。源码数值、逻辑、配方、注册 ID 没有改动。未启动或重启游戏，实机画面仍待验；未动声音、亮度或存档。

使用现有资源补丁发布流程覆盖本地 JAR 与已有三种导出文件的现存副本，逐项验证其他 ZIP 负载保持一致；不推送 GitHub。部署回读见 DELIVERY.json、installed-readback.json，最终验证见 final-check.json。
