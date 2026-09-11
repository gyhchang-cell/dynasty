#!/usr/bin/env python3
"""额外生成：手动安装包（5 个 jar 的 zip，给朋友/服主直接用）+ 上传指南。"""
import json, os, zipfile

ROOT = os.path.expanduser("~/Desktop/dynasty")
DIST = os.path.join(ROOT, "dist")
MODS = os.path.join(ROOT, "modpack", "mods")
VERSION = "1.4.0"

README = """Dynasty 王朝 · 手动安装包 %s
================================
1) 安装 Minecraft 1.20.1 + Forge 47.4.10
2) 把下面 5 个 jar 放进 .minecraft/mods/
3) 启动游戏；首次进世界会收到《王朝说明书》与《百宝妆匣》
4) 玩：背包左上角「✦ 王朝任务」+ 内置图鉴；饰品放进 Curios 的槽位

模组清单：
  dynasty-%s.jar                  本体（全部玩法）
  curios-forge-5.14.1+1.20.1.jar           饰品槽位
  OverflowingBars-v8.0.1-1.20.1-Forge.jar  美化血条
  PuzzlesLib-v8.1.33-1.20.1-Forge.jar      Overflowing Bars 前置
  jei-1.20.1-forge-15.59.0.210.jar         配方查询
""" % (VERSION, VERSION)

zip_path = os.path.join(DIST, "dynasty-%s-manual.zip" % VERSION)
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for name in sorted(os.listdir(MODS)):
        if name.endswith(".jar"):
            z.writestr("mods/" + name, open(os.path.join(MODS, name), "rb").read())
    z.writestr("安装说明-README.txt", README)
print("手动安装包:", zip_path, os.path.getsize(zip_path), "bytes")

GUIDE = """# 上传整合包指南（照做即可）

## 一共三个文件（都在 `dist/` 里）

| 文件 | 用途 | 上传到哪 |
| --- | --- | --- |
| `dynasty-modpack-%s.zip` | **CurseForge 整合包格式**（内含 `manifest.json`，模组由启动器自动下载；我们自己的模组在 `overrides/mods/`） | CurseForge → 上传项目 → 类型选 **Modpack** |
| `dynasty-%s.mrpack` | **Modrinth 整合包格式**（`modrinth.index.json` + CDN 下载地址 + 哈希） | Modrinth → 上传项目 → 类型选 **Modpack** |
| `dynasty-%s-manual.zip` | 免启动器的手动包（直接是 `mods/` 里 5 个 jar） | 网盘/群里发给朋友、或服务端用 |

> 注意：上传时选的是**上面这三个文件**，不是文件夹本身。文件夹（`modpack/`）是给你本地查看和生成的源材料。

## CurseForge 具体步骤
1. CurseForge 网站 → `Create Project` → `Minecraft` → ``Modpack``（不是 Mod！）
2. 填名称（Dynasty 王朝）、简介、版本 `%s`、游戏版本 `1.20.1`、加载器 `Forge`、上传 logo（可先用 `modpack/logo.png`，没有可随便截游戏图）
3. 上传文件：选 `dist/dynasty-modpack-%s.zip`（**不要**解压，zip 原样上传）
4. 提交审核。审核可能提示"请把 Dynasty 本体也发布到 CurseForge 后改为 manifest 引用"——若遇到，把本体发布成独立 Mod 后告诉我，我把 manifest 改成引用形式。

## Modrinth 具体步骤
1. Modrinth → `Create a project` → 类型选 **Modpack**
2. 版本号 `%s`，支持的加载器选 Forge、游戏版本 `1.20.1`
3. 上传 `dist/dynasty-%s.mrpack`
4. 同样，若审核要求本体也发布到 Modrinth，告诉我，我改成 index 引用。

## 自测（上传前先验证能不能装）
* 把 `dist/dynasty-%s-manual.zip` 解压，把 `mods/` 里 5 个 jar 丢进你自己的实例 → 能进游戏就说明包没问题。
* 或直接双击整合包 zip 用 Prism/HMCL"从压缩包导入"试一次。
""" % (VERSION, VERSION, VERSION, VERSION, VERSION, VERSION, VERSION, VERSION)

guide = os.path.join(ROOT, "docs", "upload.md")
open(guide, "w", encoding="utf-8").write(GUIDE)
print("上传指南:", guide)
print("dist 内容:", sorted(os.listdir(DIST)))
