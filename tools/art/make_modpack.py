#!/usr/bin/env python3
"""生成整合包：mods / config / modrinth.index.json / curseforge-manifest / 下载脚本（无需联网）。"""
import json, os, shutil, hashlib

ROOT = os.path.expanduser("~/Desktop/dynasty")
PACK = os.path.join(ROOT, "modpack")
MODS = os.path.join(PACK, "mods")
os.makedirs(MODS, exist_ok=True)
os.makedirs(os.path.join(PACK, "config"), exist_ok=True)

D = "https://cdn.modrinth.com/data/"
PACK_MODS = [
    ("curios-forge-5.14.1+1.20.1.jar", os.path.join(ROOT, "libs/curios-forge-5.14.1+1.20.1.jar"),
     D + "vvuO3ImH/versions/IPQlZkz1/curios-forge-5.14.1%2B1.20.1.jar"),
    ("jei-1.20.1-forge-15.59.0.210.jar", os.path.join(ROOT, "libs/jei-1.20.1-forge-15.59.0.210.jar"),
     D + "u6dRKJwZ/versions/4vbuxppk/jei-1.20.1-forge-15.59.0.210.jar"),
    ("OverflowingBars-v8.0.1-1.20.1-Forge.jar",
     os.path.join(ROOT, "libs/OverflowingBars-v8.0.1-1.20.1-Forge.jar"),
     D + "XD7XOrAF/versions/w90XIUWB/OverflowingBars-v8.0.1-1.20.1-Forge.jar"),
    ("PuzzlesLib-v8.1.33-1.20.1-Forge.jar",
     os.path.join(ROOT, "libs/PuzzlesLib-v8.1.33-1.20.1-Forge.jar"),
     D + "QAGBst4M/versions/mIyVGf3d/PuzzlesLib-v8.1.33-1.20.1-Forge.jar"),
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


files = []
for filename, src, url in PACK_MODS:
    shutil.copy2(src, os.path.join(MODS, filename))
    s1, s512 = hashes(os.path.join(MODS, filename))
    files.append({
        "path": "mods/" + filename,
        "hashes": {"sha1": s1, "sha512": s512},
        "env": {"client": "required", "server": "required"},
        "downloads": [url],
        "fileSize": os.path.getsize(os.path.join(MODS, filename)),
    })
    print("pack mod:", filename, files[-1]["fileSize"], "bytes")

own_dir = os.path.join(ROOT, "build/libs")
own_jars = [n for n in sorted(os.listdir(own_dir)) if n.startswith("dynasty-") and n.endswith(".jar")] \
    if os.path.isdir(own_dir) else []
if own_jars:
    shutil.copy2(os.path.join(own_dir, own_jars[-1]), os.path.join(MODS, own_jars[-1]))
    print("pack mod:", own_jars[-1], "(dynasty core)")
else:
    print("WARNING: run ./gradlew build first")

index = {
    "formatVersion": 1,
    "game": "minecraft",
    "versionId": "1.0.0",
    "name": "Dynasty 王朝",
    "summary": "Dynasty 本体 + Curios 饰品槽 + 美化血条(Overflowing Bars + Puzzles Lib) + JEI 配方查询",
    "files": files,
    "dependencies": {"minecraft": "1.20.1", "forge": "47.4.10"},
}
json.dump(index, open(os.path.join(PACK, "modrinth.index.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

cf = {
    "minecraft": {"version": "1.20.1", "modLoaders": [{"id": "forge-47.4.10", "primary": True}]},
    "manifestType": "minecraftModpack", "manifestVersion": 1,
    "name": "Dynasty 王朝", "version": "1.0.0", "author": "Newton",
    "files": [{"filename": os.path.basename(f["path"]), "url": f["downloads"][0],
               "sha1": f["hashes"]["sha1"]} for f in files],
}
json.dump(cf, open(os.path.join(PACK, "curseforge-manifest.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

lines = ["#!/usr/bin/env bash",
         "# 下载 Dynasty 整合包所需的第三方模组（本体 jar 请自行复制进来）",
         "set -e", 'cd "$(dirname "$0")"', "mkdir -p mods", "cd mods", ""]
for f in files:
    lines.append('echo ">> %s"' % os.path.basename(f["path"]))
    lines.append('curl -L --retry 2 -o "%s" "%s"' % (os.path.basename(f["path"]), f["downloads"][0]))
script = os.path.join(PACK, "download_mods.sh")
open(script, "w", encoding="utf-8").write("\n".join(lines) + "\n")
os.chmod(script, 0o755)

print("modpack ready:", PACK)
print("mods:", sorted(os.listdir(MODS)))
