# 原稿实际接入 · 2026-10-16

用户最新授权：所有完成的获选美术默认覆盖到游戏，不再等单独提醒。本批将 v5 的 50 件饰品、4 件材料和 v6 的 8 件机械物品实际接入；含旧批替换，累计 225 件独立原稿。未选中的 399 张现有物品贴图保持本轮前哈希。

保留源 PNG 全部主体 RGBA 像素，只裁透明边并补 2px 透明边，不降采样、不减色。`original_item` Forge 几何加载器采用原生 ItemModelGenerator 生成正反面和厚度，FaceBakery 烘焙，保留原版展示姿态和附魔光效渲染通路，独立纹理避免超出共用图集容量。共享 atlas 只排除这些确切 ID；CPU Stitcher 检查剩余 1955 张原版/Dynasty 图块为 2048×2048。粒子采用原版铁粒图块，避免从不属于 atlas 的原稿错误取粒子 UV。

统一发布：`tools/art/inventory-refresh/install.py`。当前完整来源清单：`docs/art/inventory-refresh-v1/generated-manifest.json`。验证：`check_original_runtime.py`，检查原稿像素、模型绑定、atlas 过滤、451 项 JAR 内容、399 张其他贴图。`VerifyDirectOriginals.java` 使用 Minecraft NativeImage、SpriteContents、ItemModelGenerator 对 225 张运行纹理生成 399651 个原生面并核对 UV 范围。完整 build/reobfJar 通过。

`sync_originals.py` 校验三种既有包内本体 JAR 完全一致后，同步本地 Dynasty 实例、模组导出、整合包实例和现有三种导出。路径与哈希见 `installed.json`；替换前文件备份在 `installed-before/`，资源备份在 `before/`。导出名称、内容策略和 FTB 整合方式沿用现有脚本，未新增补装包。

边界：未启动图形客户端，未进行游戏画面验收；原生无窗口检查不等同实机验收。现有愚者 chishi 进程和存档未动（该参考实例没有 Dynasty 模组，未向它擅自添加模组）。磁盘上的 Dynasty 实例将在下次正常加载本体时使用这些原稿，不声称现有进程已热更新。
