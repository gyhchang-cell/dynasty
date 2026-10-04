#!/usr/bin/env python3
"""生成可直接上传的整合包：
1) dist/dynasty-modpack-1.4.0.zip   —— CurseForge「整合包」上传格式（manifest.json + overrides/）
2) dist/dynasty-1.4.0.mrpack        —— Modrinth「整合包」上传格式（modrinth.index.json + overrides/）
"""
import argparse, json, os, shutil, zipfile, hashlib
from export_policy import release_mod, release_config
from check_modrinth_pack import check_pack
from modrinth_release import prepare_release, manual_guide

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--platform', choices=('both', 'curseforge', 'modrinth'), default='both')
args = parser.parse_args()

ROOT = os.path.expanduser("~/Desktop/dynasty")
DIST = os.path.join(ROOT, "dist")
MODS = os.path.join(ROOT, "modpack", "mods")
os.makedirs(DIST, exist_ok=True)

VERSION = "1.4.0"
OWN_JAR = "dynasty-%s.jar" % VERSION
OURS = os.path.join(MODS, OWN_JAR)
assert os.path.exists(OURS), "先运行 ./gradlew build 生成 " + OWN_JAR

# CurseForge 项目/文件 ID（经 cfwidget 查得）
CF_FILES = [
    (309927, 6418456),   # Curios API          curios-forge-5.14.1+1.20.1.jar
    (238222, 8851009),   # JEI                 jei-1.20.1-forge-15.59.0.210.jar
    (852662, 5763974),   # Overflowing Bars    OverflowingBars-v8.0.1-1.20.1-Forge.jar
    (495476, 6918565),   # Puzzles Lib         PuzzlesLib-v8.1.33-1.20.1-Forge.jar
]

MR_FILES = [
    ("curios-forge-5.14.1+1.20.1.jar",
     "https://cdn.modrinth.com/data/vvuO3ImH/versions/IPQlZkz1/curios-forge-5.14.1%2B1.20.1.jar"),
    ("jei-1.20.1-forge-15.59.0.210.jar",
     "https://cdn.modrinth.com/data/u6dRKJwZ/versions/4vbuxppk/jei-1.20.1-forge-15.59.0.210.jar"),
    ("OverflowingBars-v8.0.1-1.20.1-Forge.jar",
     "https://cdn.modrinth.com/data/XD7XOrAF/versions/w90XIUWB/OverflowingBars-v8.0.1-1.20.1-Forge.jar"),
    ("PuzzlesLib-v8.1.33-1.20.1-Forge.jar",
     "https://cdn.modrinth.com/data/QAGBst4M/versions/mIyVGf3d/PuzzlesLib-v8.1.33-1.20.1-Forge.jar"),
]

# ---- 优化 / 便利模组（fetch_qol_mods.py 下载并登记）----
QOL_JSON = os.path.join(ROOT, "tools", "art", "qol_mods.json")
QOL = json.load(open(QOL_JSON, encoding="utf-8")) if os.path.exists(QOL_JSON) else []
# ---- FTB 系列（fetch_ftb_mods.py 下载并登记，CF 上没有引用 ID，一并打进 overrides）----
FTB_JSON = os.path.join(ROOT, "tools", "art", "ftb_mods.json")
FTB = json.load(open(FTB_JSON, encoding="utf-8")) if os.path.exists(FTB_JSON) else []
QOL = [r for r in QOL + FTB if release_mod(r['filename'])]
# Mandatory boss animation runtime, shared by clients and dedicated servers.
QOL.append({"filename": "geckolib-forge-1.20.1-4.8.4.jar",
            "url": "https://cdn.modrinth.com/data/8BmcQJ2H/versions/aC5KMoNg/geckolib-forge-1.20.1-4.8.4.jar",
            "client": "required", "server": "required"})
QOL_FILENAMES = [record["filename"] for record in QOL]
for record in QOL:
    MR_FILES.append((record["filename"], record["url"]))

# JEI can occur both in the base dependencies and in the downloaded QOL list.
# Keep one installation entry; refuse conflicting sources instead of hiding them.
mr_sources = {}
for filename, url in MR_FILES:
    if filename in mr_sources and mr_sources[filename] != url:
        raise ValueError("Modrinth 模组下载地址冲突: " + filename)
    mr_sources[filename] = url
MR_FILES = list(mr_sources.items())


def hashes(path):
    sha1, sha512 = hashlib.sha1(), hashlib.sha512()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(1 << 20)
            if not chunk:
                break
            sha1.update(chunk)
            sha512.update(chunk)
    return sha1.hexdigest(), sha512.hexdigest()


def add_config_to(zip_file):
    """把 modpack/config（FTB 任务书等）打进 overrides/config / config"""
    config_dir = os.path.join(ROOT, "modpack", "config")
    if not os.path.isdir(config_dir):
        return
    for base, _dirs, files in os.walk(config_dir):
        for name in files:
            full = os.path.join(base, name)
            rel = os.path.relpath(full, config_dir).replace(os.sep, "/")
            if not release_config(rel):
                continue
            zip_file.writestr("overrides/config/" + rel, open(full, "rb").read())


CF_README = """Dynasty 王朝 整合包 1.4.0（平衡重制）
=============================
以《Dynasty 王朝》模组为主体，另附：
  * Curios API   —— 饰品槽位（本模组的 12 件饰品可直接放进 Curios 槽）
  * Overflowing Bars + Puzzles Lib —— 更美观的血条/护甲条/饥饿条
  * JEI          —— 配方查询
  * 11 个优化/便利模组（都不改玩法）：
      Embeddium / FerriteCore / ModernFix / Entity Culling / ImmediatelyFast
      Clumps / Memory Leak Fix / Jade / AppleSkin / Mouse Tweaks / Vein Mining（连锁挖矿）

本体内容（1.4.0）：
  * 17 把进化武器：木矛(5) → … → 方天画戟(620) → 玄天钺(800) → 天子剑(1140)
  * 5 套进化护甲：布衣 → 将军铠 → 玉甲 → 龙鳞甲 → 玄天真龙甲
  * 5 种新建筑：长城 / 宝塔 / 天坛 / 驿站 / 牌坊
  * Boss 信物门槛：叛将首级、内廷令牌、帝骸骨、龙帝玉玺、凤凰羽
  * 说明书新增「去其他维度」完整教程；物品名下一行简介 + Shift 详细数值

安装：CurseForge / Prism / HMCL / PCL2 直接安装本整合包；
      首次进世界会收到《王朝说明书》与《百宝妆匣》；背包左上角有「✦ 王朝任务」「✦ 饰品」。
"""

MR_README = CF_README

# ---------------------------------------------------------------- CurseForge
outputs = []
manifest = {
    "minecraft": {"version": "1.20.1", "modLoaders": [{"id": "forge-47.4.10", "primary": True}]},
    "manifestType": "minecraftModpack",
    "manifestVersion": 1,
    "name": "Dynasty 王朝",
    "version": VERSION,
    "author": "Newton",
    "description": "以 Dynasty 王朝为主体，附 Curios 饰品槽 / 美化血条 / JEI。",
    "files": [{"projectID": p, "fileID": f, "required": True} for p, f in CF_FILES],
    "overrides": "overrides",
}
cf_zip = os.path.join(DIST, "dynasty-modpack-%s.zip" % VERSION)
if args.platform in ('both', 'curseforge'):
    with zipfile.ZipFile(cf_zip, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        z.writestr("overrides/README.txt", CF_README)
        z.writestr("overrides/mods/" + OWN_JAR, open(OURS, "rb").read())
        # Existing CF export behavior is deliberately left unchanged in this task.
        for filename in QOL_FILENAMES:
            path = os.path.join(MODS, filename)
            if os.path.exists(path):
                z.writestr("overrides/mods/" + filename, open(path, "rb").read())
        add_config_to(z)
    outputs.append(cf_zip)
    print("CurseForge 包:", cf_zip, os.path.getsize(cf_zip), "bytes")

# ---------------------------------------------------------------- Modrinth
if args.platform in ('both', 'modrinth'):
    mr_files, manual, embedded = prepare_release(MR_FILES, MODS)
    index = {
        "formatVersion": 1, "game": "minecraft", "versionId": VERSION,
        "name": "Dynasty 王朝",
        "summary": "中国古代/神话 RPG；本体与任务配置保留。完整任务功能需按随包说明补装 FTB 依赖。",
        "files": mr_files,
        "dependencies": {"minecraft": "1.20.1", "forge": "47.4.10"},
    }
    mr_zip = os.path.join(DIST, "dynasty-%s.mrpack" % VERSION)
    temporary = mr_zip + '.pending'
    guide = manual_guide(manual)
    try:
        with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("modrinth.index.json", json.dumps(index, ensure_ascii=False, indent=2))
            z.writestr("overrides/README.txt", guide)
            z.writestr("overrides/DYNASTY-INSTALL-FIRST.txt", guide)
            z.writestr("overrides/dynasty-manual-dependencies.json", json.dumps(manual, ensure_ascii=False, indent=2))
            z.write(OURS, "overrides/mods/" + OWN_JAR)
            for record in embedded:
                z.write(os.path.join(MODS, record['filename']), "overrides/mods/" + record['filename'])
                z.write(os.path.join(ROOT, "tools", "art", record['license_file']),
                        "overrides/" + record['license_file'])
            add_config_to(z)
        report = check_pack(temporary, MODS)
        if report['errors'] or report['warnings']:
            raise ValueError("Modrinth 发布校验失败: " + json.dumps(report, ensure_ascii=False))
        os.replace(temporary, mr_zip)
    finally:
        if os.path.isfile(temporary):
            os.unlink(temporary)
    outputs.append(mr_zip)
    print("Modrinth 包:", mr_zip, os.path.getsize(mr_zip), "bytes")
    print("官方哈希核验:", len(mr_files), "文件；合法内嵌:", len(embedded), "；需官方补装:", len(manual))

# 目录列表打印
for name in outputs:
    with zipfile.ZipFile(name) as z:
        print(" -", os.path.basename(name), "包含", len(z.namelist()), "项")
