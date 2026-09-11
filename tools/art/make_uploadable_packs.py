#!/usr/bin/env python3
"""生成可直接上传的整合包：
1) dist/dynasty-modpack-1.4.0.zip   —— CurseForge「整合包」上传格式（manifest.json + overrides/）
2) dist/dynasty-1.4.0.mrpack        —— Modrinth「整合包」上传格式（modrinth.index.json + overrides/）
"""
import json, os, shutil, zipfile, hashlib

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


CF_README = """Dynasty 王朝 整合包 1.4.0
=====================
以《Dynasty 王朝》模组为主体，附带：
  * Curios API   —— 饰品槽位（本模组的 10 件饰品直接放进 Curios 的槽）
  * Overflowing Bars + Puzzles Lib —— 更美观的血条/护甲条/饥饿条
  * JEI          —— 配方查询

安装：CurseForge / Prism / HMCL / PCL2 直接安装本整合包即可；首次进世界会收到《王朝说明书》与《百宝妆匣》。
玩法：跟随「✦ 王朝任务」（背包左上角）与内置图鉴，按 兵器进化链 逐步变强。
"""

MR_README = CF_README

# ---------------------------------------------------------------- CurseForge
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
with zipfile.ZipFile(cf_zip, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    z.writestr("overrides/README.txt", CF_README)
    z.writestr("overrides/mods/" + OWN_JAR, open(OURS, "rb").read())
print("CurseForge 包:", cf_zip, os.path.getsize(cf_zip), "bytes")

# ---------------------------------------------------------------- Modrinth
mr_files = []
for filename, url in MR_FILES:
    path = os.path.join(MODS, filename)
    s1, s512 = hashes(path)
    mr_files.append({
        "path": "mods/" + filename,
        "hashes": {"sha1": s1, "sha512": s512},
        "env": {"client": "required", "server": "required"},
        "downloads": [url],
        "fileSize": os.path.getsize(path),
    })
index = {
    "formatVersion": 1,
    "game": "minecraft",
    "versionId": VERSION,
    "name": "Dynasty 王朝",
    "summary": "Dynasty 王朝本体 + Curios 饰品槽 + 美化血条 + JEI",
    "files": mr_files,
    "dependencies": {"minecraft": "1.20.1", "forge": "47.4.10"},
}
mr_zip = os.path.join(DIST, "dynasty-%s.mrpack" % VERSION)
with zipfile.ZipFile(mr_zip, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("modrinth.index.json", json.dumps(index, ensure_ascii=False, indent=2))
    z.writestr("overrides/README.txt", MR_README)
    z.writestr("overrides/mods/" + OWN_JAR, open(OURS, "rb").read())
print("Modrinth 包:", mr_zip, os.path.getsize(mr_zip), "bytes")

# 目录列表打印
for name in (cf_zip, mr_zip):
    with zipfile.ZipFile(name) as z:
        print(" -", os.path.basename(name), "包含:", z.namelist())
