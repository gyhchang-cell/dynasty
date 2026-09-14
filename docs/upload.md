# 上传整合包指南（照做即可）

## 一共三个文件（都在 `dist/` 里）

| 文件 | 用途 | 上传到哪 |
| --- | --- | --- |
| `dynasty-modpack-1.4.0.zip` | **CurseForge 整合包格式**（内含 `manifest.json`，模组由启动器自动下载；我们自己的模组在 `overrides/mods/`） | CurseForge → 上传项目 → 类型选 **Modpack** |
| `dynasty-1.4.0.mrpack` | **Modrinth 整合包格式**（`modrinth.index.json` + CDN 下载地址 + 哈希） | Modrinth → 上传项目 → 类型选 **Modpack** |
| `dynasty-1.4.0-manual.zip` | 免启动器的手动包（直接是 `mods/` 里全部 jar） | 网盘/群里发给朋友、或服务端用 |

> 注意：上传时选的是**上面这三个文件**，不是文件夹本身。文件夹（`modpack/`）是给你本地查看和生成的源材料。

## CurseForge 具体步骤
1. CurseForge 网站 → `Create Project` → `Minecraft` → ``Modpack``（不是 Mod！）
2. 填名称（Dynasty 王朝）、简介、版本 `1.4.0`、游戏版本 `1.20.1`、加载器 `Forge`、上传 logo（可先用 `modpack/logo.png`，没有可随便截游戏图）
3. 上传文件：选 `dist/dynasty-modpack-1.4.0.zip`（**不要**解压，zip 原样上传）
4. 提交审核。审核可能提示"请把 Dynasty 本体也发布到 CurseForge 后改为 manifest 引用"——若遇到，把本体发布成独立 Mod 后告诉我，我把 manifest 改成引用形式。

## Modrinth 具体步骤
1. Modrinth → `Create a project` → 类型选 **Modpack**
2. 版本号 `1.4.0`，支持的加载器选 Forge、游戏版本 `1.20.1`
3. 上传 `dist/dynasty-1.4.0.mrpack`
4. 同样，若审核要求本体也发布到 Modrinth，告诉我，我改成 index 引用。

## 自测（上传前先验证能不能装）
* 把 `dist/dynasty-1.4.0-manual.zip` 解压，把 `mods/` 里 16 个 jar 丢进你自己的实例 → 能进游戏就说明包没问题。
* 或直接双击整合包 zip 用 Prism/HMCL"从压缩包导入"试一次。
