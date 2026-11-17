# 普通物品完整筛查与重画 v14

用户授权：全部重做剩余差贴图，保留精致老图。审查857个物品模型，其中281个本地generated图标实际查看联系表；选中97件普通物品，再补9件借用不合适原版图的食物、油、蛇胆等，共106件。all-models-audit.json记录全模型分类；audit.json记录本地generated审图范围。盔甲、武器、刷怪蛋和放置方块属于独立模型/并行开发范围，本轮保留；已批准的265件原稿及精致旧饰品不重画。

使用内置image_gen逐件生成，参考accessories-mc-v11真实1000件物品研究及style-target.png。不是1000个整合包。完整提示为prompt-prefix.txt + selection.json中的subject；三种药水返修提示见refinement-prompts.json，原料玉返修见jade-refinement.json。原稿保存在sources，原贴图和模型保存在before；被否决首稿保存在rejected。

药水首稿红金配色会干扰原药效染色，且三种轮廓相似，因此改为中性灰药瓶，区分饮用/投掷/滞留轮廓。original_item加载器增加可选tint_index，默认-1保持既有图不变，三种药水设置0保留既有PotionUtils颜色处理。原料玉首稿误作玉环，改成未雕刻的玉块。没有修改注册ID、配方、掉落、任务或战斗逻辑。

运行资源仅裁透明边并补2px，不降采样、减色或有损压缩。gallery-*为生成原稿缩略预览，inventory-size-review为32px尺寸读图检查，均非游戏截图。未启动客户端、修改存档、操作声音亮度或推送GitHub。美术完成不代替清单内玩法/JEI/真人条件验收，因此未删除这些提示词。

验证与部署结果见后续validation.json、native.log、build.log、installed.json及preservation.json。

最终结果：离线build/reobfJar通过（1m9s）；371件累计原稿RGBA/模型/图集/JAR共743项完全匹配，errors为空。无窗口Minecraft原生解码、挤出、UV及药水面染色检查371张/642609面通过。当前批次外已有PNG全部哈希保持一致。3个既有导出包内嵌本体JAR验证后同步11处本地实例/导出文件。FTB依赖检查、74项官方哈希核验通过，补装0。完整106件原稿在originals-106.zip；总览all-106.png。
