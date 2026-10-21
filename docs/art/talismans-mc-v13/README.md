# COD4-9首次重画：7种符箓 · 2026-10-18

本次继续用户指示，完成此前没有进入任何选图/原稿清单的7张现有符箓：御风、隐身、火、雷、归乡、金刚、摄魂。读取TalismanCharmItem的真实用途后保留身份与主要配色，改善纸边、折角、主符纹和轮廓。原模型与32px旧图在before。没有更改ID、功能、配方、掉落或其他开发者逻辑。

内置image_gen逐件生成，实际提示集为prompt-prefix.txt加selection.json的subject，参考图为../accessories-mc-v11/references/style-target.png，沿用其1000件物品实查记录。原稿sources原样保留，运行发布只裁透明边并补2px，未缩成16px、量化或有损压缩。已查看前后图和32px读图预览。this-session-15.png合并本轮8件消耗品与7张符箓，originals-15.zip收纳两批原PNG；不是游戏截图。

离线build/reobfJar通过。265件原稿/模型/图集/JAR共531项匹配，无窗口Minecraft原生解码、厚度和UV检查265张/488693个面通过。其余已有贴图本轮哈希未变，见preservation.json；在旧全局基线外的并行武器变化单列记录，未回滚。

导出最终核验发现make_modpack.py用文件名字典序选择dynasty-*.jar，会误选dynasty-playtest-helper-1.4.0.jar并留下旧本体。已改成按gradle.properties的mod_version精确选择发行JAR，缺失则报错。测试辅助源JAR保留；本工具误拷入modpack的同哈希副本备份到before-export后移出。重新导出3种既有包，核对它们内嵌JAR与当前构建逐字节一致，再同步本地实例与桌面导出。未改导出名称、格式或FTB内容。详见installed.json和pack.log。

本轮未启动游戏，没有图形客户端实测；未操作存档、声音、亮度或推送GitHub。任务原文的JEI导航、使用动作、持续时长与Build收益验收仍保留，未以美术完成代替整项完成。
