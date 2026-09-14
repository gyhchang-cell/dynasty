#!/usr/bin/env python3
"""额外生成：手动安装包（mods/ 里全部 jar 的 zip，给朋友/服主直接用）+ 上传指南。"""
import json, os, zipfile

ROOT = os.path.expanduser("~/Desktop/dynasty")
DIST = os.path.join(ROOT, "dist")
MODS = os.path.join(ROOT, "modpack", "mods")
VERSION = "1.4.0"

MOD_NAMES = sorted(n for n in os.listdir(MODS) if n.endswith(".jar")) if os.path.isdir(MODS) else []
MOD_COUNT = len(MOD_NAMES)
CONFIG_DIR = os.path.join(ROOT, "modpack", "config")

README = """Dynasty 王朝 · 手动安装包 %s
================================
1) 安装 Minecraft 1.20.1 + Forge 47.4.10
2) 把下面 %d 个 jar 全部放进 .minecraft/mods/
3) 启动游戏；首次进世界会收到《王朝说明书》与《百宝妆匣》
4) 玩：背包左上角「✦ 王朝任务」+ 内置图鉴；饰品放进 Curios 的槽位或「✦ 饰品」按钮

模组清单（%d 个）：
%s

说明：除 dynasty 本体外，其余都是优化 / 信息 / 操作 / 生存便利类模组，
      不改玩法、不加数值；不想要哪个直接删掉对应 jar 也不会崩。
连锁采掘已做进本体：按住潜行破坏矿石或原木即可连带采集。
""" % (VERSION, MOD_COUNT, MOD_COUNT, "\n".join("  " + n for n in MOD_NAMES))

zip_path = os.path.join(DIST, "dynasty-%s-manual.zip" % VERSION)
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for name in MOD_NAMES:
        z.writestr("mods/" + name, open(os.path.join(MODS, name), "rb").read())
    # 配置（FTB 任务书等）一起打包，解压即用
    if os.path.isdir(CONFIG_DIR):
        for base, _dirs, files in os.walk(CONFIG_DIR):
            for name in files:
                full = os.path.join(base, name)
                rel = os.path.relpath(full, CONFIG_DIR)
                z.writestr("config/" + rel.replace(os.sep, "/"), open(full, "rb").read())
    z.writestr("安装说明-README.txt", README)
print("手动安装包:", zip_path, os.path.getsize(zip_path), "bytes", "(%d jars)" % MOD_COUNT)

GUIDE = """# 上传整合包指南（照做即可）

## 一共三个文件（都在 `dist/` 里）

| 文件 | 用途 | 上传到哪 |
| --- | --- | --- |
| `dynasty-modpack-%s.zip` | **CurseForge 整合包格式**（内含 `manifest.json`，模组由启动器自动下载；我们自己的模组在 `overrides/mods/`） | CurseForge → 上传项目 → 类型选 **Modpack** |
| `dynasty-%s.mrpack` | **Modrinth 整合包格式**（`modrinth.index.json` + CDN 下载地址 + 哈希） | Modrinth → 上传项目 → 类型选 **Modpack** |
| `dynasty-%s-manual.zip` | 免启动器的手动包（直接是 `mods/` 里全部 jar） | 网盘/群里发给朋友、或服务端用 |

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
* 把 `dist/dynasty-%s-manual.zip` 解压，把 `mods/` 里 16 个 jar 丢进你自己的实例 → 能进游戏就说明包没问题。
* 或直接双击整合包 zip 用 Prism/HMCL"从压缩包导入"试一次。
""" % (VERSION, VERSION, VERSION, VERSION, VERSION, VERSION, VERSION, VERSION)

guide = os.path.join(ROOT, "docs", "upload.md")
open(guide, "w", encoding="utf-8").write(GUIDE)
print("上传指南:", guide)
print("dist 内容:", sorted(os.listdir(DIST)))
