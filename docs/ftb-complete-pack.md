# 一次导出全部整合包

继续使用原来的 `3-打包整合包.command` 或 `打包整合包.command`。
两个入口共用 exportModpack，先构建最新 Dynasty，再导出全部格式。
无需单独执行 FTB 入口。工程目录不再写死为某个用户的桌面路径。

生成的 `dist/dynasty-1.4.0-manual.zip` 是完整本地客户端整合包，
包含最新 Dynasty、工程的发布模组、FTB、任务配置及资源包。
导出成功后也复制到桌面 `导出/Dynasty整合包`。

| 依赖 | 固定版本 |
| --- | --- |
| FTB Library | 2001.2.13 |
| FTB Teams | 2001.3.2 |
| FTB Quests | 2001.4.22 |
| FTB Ultimine | 2001.1.8 |
| Item Filters | 2001.1.0-build.59 |
| Architectury | 9.2.14 Forge |
| Cloth Config | 11.1.136 Forge |

任务章节和 ID 保持原样。依赖缺失、哈希不符、混装版本、损坏 jar、
任务章节缺失或依赖声明检查失败时停止，不再吞掉打包异常后显示成功。
完整包验证完成后才原子替换旧产物。随包 JSON 记录文件哈希和章节数量。

安装时将 mods、config、resourcepacks 一起复制到独立的 Minecraft 1.20.1 /
Forge 47.4.10 客户端实例根目录。不是专用服务器包；旧实例请先备份，
避免同时保留旧版同名模组。完整包导出器不读取或改写 saves；原 Gradle
导出任务仍保留原有 HMCL 同步行为。

CurseForge ZIP 和 Modrinth .mrpack 仍在同一次操作中生成。
Modrinth 公开发布流程仍排除 FTB 二进制并附补装说明，不应把它与
包含全部 FTB 的 manual.zip 混淆。此次不变更公开平台分发策略。
若联网核验 Modrinth 失败，会明确报错；已生成的完整本地包留在 dist，
但不会把整轮导出标记为全部成功。

需要 Java 17、Python 3 和 Gradle 离线缓存；首次缺缓存时先正常联网 build。
测试：`python3 -m unittest discover -s tools/art -p test_export_ftb_complete.py -v`。
七项合成 jar 测试覆盖完整输出、配置保留、最新核心选择、缺依赖、错误哈希、
混装版本、缺章节、缺构建、传递依赖缺失和失败时保留旧产物。
云端不能获取真实 jar，尚未执行完整 Gradle 构建、真实打包或游戏验收。
