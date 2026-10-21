# 奇门物品图标补齐 v16

继续用户“剩余差贴图全部改、精致老图保留”的授权。复查当前普通 generated 模型和已有原稿清单后，未改的普通饰品多数属于需保护的精致旧图，本轮不覆盖它们。选择三个确有名称/图像不符的旧图标：飞爪原用原版绊线钩、绳镖原用三叉戟、流星锤原用下界合金斧。

先读取 ExpansionWeapons 实际用途：飞爪牵引敌人/攀引方块，绳镖牵引，流星锤蓄力范围打击。绘制三钩铁爪与附绳、带红布结的尖镖与绳圈、带大链环的重锤与手环，清楚区分结构。本轮仅改图标与其模型引用，不改实体、伤害、冷却、触发、注册ID、配方或存档。

内置 image_gen 逐件生成；实际提示词和参考路径记录 prompts.json，原稿 sources/ 与 originals-3.zip。沿用 accessories-mc-v11 的实际1000件物品参考记录，非声称本轮重新研究1000个整合包。实际查看本轮三个原稿及32像素库存预览。图片 this-round-3.png / inventory-size-review.png 为文件预览，非游戏截图。

沿用 original_item 加载器，运行PNG仅裁透明外边距并补2px，主体RGBA逐像素保持原稿，不降采样/减色。保存原 generated + handheld 继承所得显示变换，避免物品改图后手持姿态退化；发布器读取选择文件的 display，使后续重新导出不丢失该设置。其余原稿仍沿用原设置。

source-validation.json 检查本轮精确RGBA、手持显示和其他既有物品PNG哈希；validation.json 检查累计原稿/JAR；native.log 是无窗口Minecraft PNG/挤出面/UV检查，不是游戏实机验收。build.log 记录本次完整离线 build/reobfJar。没有启动游戏、关闭既有客户端、修改存档、声音或亮度，也没有推送GitHub。未删除仍含玩法或真人验收的提示词。

导出沿用现有三个文件，不重生成任务/配置/模组依赖。refresh_existing_exports.py 仅替换 overrides/mods/dynasty-1.4.0.jar，逐项验证其他entry的内容哈希与成员名称保持一致；旧包以硬链接备份在before/exports。export-validation.json 与 installed.json 分别记录导出核对和本地同步结果。

最终结果：离线build成功（23秒）；380张累计原稿、761项JAR资源匹配检查通过；Minecraft无窗口资源验证380张、658175个挤出面通过。三份现有导出仅替换本体JAR，其他成员逐项保持；同步11处本地游戏/导出文件。初次JAR检查遇到归档写入期间暂不可读，已在归档稳定后重新完整通过，并核对最终同步JAR哈希一致。尚未启动图形客户端验证实际新画面。
