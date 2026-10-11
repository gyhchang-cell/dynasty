# 上传整合包指南（照做即可）

## 自己游玩与平台发布（文件都在 `dist/` 里）

自己游玩优先导入名字带 `complete` 的完整包，包含 FTB 任务、连锁和前置。

| 文件 | 用途 | 上传到哪 |
| --- | --- | --- |
| `dynasty-1.4.0-complete.mrpack` | **完整本地游玩包**（全部模组、FTB 与任务配置） | 直接导入支持 mrpack 的启动器 |
| `dynasty-1.4.0-complete.zip` | 同一完整游玩包的 CurseForge 导入格式 | 直接导入支持该格式的启动器 |
| `dynasty-modpack-1.4.0.zip` | **CurseForge 整合包格式**（内含 `manifest.json`，模组由启动器自动下载；我们自己的模组在 `overrides/mods/`） | CurseForge → 上传项目 → 类型选 **Modpack** |
| `dynasty-1.4.0.mrpack` | **Modrinth 发布格式**（FTB 仍需按随包说明补装） | Modrinth → 上传项目 → 类型选 **Modpack** |
| `dynasty-1.4.0-manual.zip` | 完整本地包（全部模组、FTB 任务和配置） | 本地客户端安装；不是专用服务器包 |

> 带 `complete` 的包和 manual.zip 用于本地安装；公开发布使用表中的平台发布文件。

## CurseForge 具体步骤
1. CurseForge 网站 → `Create Project` → `Minecraft` → ``Modpack``（不是 Mod！）
2. 填名称（Dynasty 王朝）、简介、版本 `1.4.0`、游戏版本 `1.20.1`、加载器 `Forge`、上传 logo（可先用 `modpack/logo.png`，没有可随便截游戏图）
3. 上传文件：选 `dist/dynasty-modpack-1.4.0.zip`（**不要**解压，zip 原样上传）
4. 提交审核。审核可能提示"请把 Dynasty 本体也发布到 CurseForge 后改为 manifest 引用"——若遇到，把本体发布成独立 Mod 后告诉我，我把 manifest 改成引用形式。

## Modrinth 具体步骤
1. Modrinth → `Create a project` → 类型选 **Modpack**
2. 版本号 `1.4.0`，支持的加载器选 Forge、游戏版本 `1.20.1`
3. 上传 `dist/dynasty-1.4.0.mrpack`；此发布格式仍需补装 FTB，完整本地游玩使用 complete.mrpack 或 complete.zip。
4. 同样，若审核要求本体也发布到 Modrinth，告诉我，我改成 index 引用。

## 自测（上传前先验证能不能装）
* 把 `dist/dynasty-1.4.0-manual.zip` 解压，把 `mods/` 中随包附带的 jar 和 `config/` 一起装入独立测试实例；进入测试世界验证，不覆盖正在编辑的建筑存档。
* 或直接双击整合包 zip 用 Prism/HMCL"从压缩包导入"试一次。
