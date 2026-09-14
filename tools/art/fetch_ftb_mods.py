"""下载 FTB 系列模组（FTB Quests / FTB Library / FTB Teams）。

FTB 官方只把这几只发布在 CurseForge + 自家 maven，没有上 Modrinth，
所以这里直接从 FTB 官方 maven 取稳定版（2001.x = Minecraft 1.20.1）。

运行：python3 tools/art/fetch_ftb_mods.py
输出：libs/*.jar 以及 tools/art/ftb_mods.json
"""
import hashlib
import json
import os
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LIBS = os.path.join(ROOT, "libs")
os.makedirs(LIBS, exist_ok=True)

MAVEN = "https://maven.ftb.dev/releases/dev/ftb/mods/"
# CurseForge CDN：edge 是新文件的镜像，mediafilez 是旧文件的镜像，两个都试
CF_HOSTS = ["https://edge.forgecdn.net/files/", "https://mediafilez.forgecdn.net/files/"]

# (artifact, version, 说明) —— FTB 官方 maven
ARTIFACTS = [
    ("ftb-quests-forge", "2001.4.22", "FTB 任务：任务书 / 任务章节 / 奖励"),
    ("ftb-library-forge", "2001.2.13", "FTB 系列前置库"),
    ("ftb-teams-forge", "2001.3.2", "FTB 队伍（任务进度共享）"),
]

# CurseForge 上的文件（Modrinth 版本过旧或没有，FTB Quests 需要 itemfilters build.55+）
# (文件名, CurseForge 文件 ID, 说明)
CF_FILES = [
    ("item-filters-forge-2001.1.0-build.59.jar", 4838266, "FTB 任务筛选器（build.59 ≥ 要求 build.55）"),
    ("alltheleaks-1.1.3+1.20.1-forge.jar", 8779054, "内存泄漏修复（长时间挂机更稳）"),
    ("jecharacters-1.20.1-forge-4.6.11.jar", 8771525, "JEI/界面支持拼音搜索中文（中文玩家必备）"),
]


def hashes(path):
    sha1, sha512 = hashlib.sha1(), hashlib.sha512()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            sha1.update(chunk)
            sha512.update(chunk)
    return sha1.hexdigest(), sha512.hexdigest()


def curl(url, target):
    subprocess.run(["curl", "-sL", "--max-time", "300", "-o", target, url], check=True)


def cf_url(file_id, filename, host=None):
    """CurseForge CDN 直链：files/<前4位>/<后3位>/<文件名>"""
    text = str(file_id)
    base = host or CF_HOSTS[0]
    return "%s%s/%s/%s" % (base, text[:4], text[4:], filename)


def main():
    records = []
    jobs = [("%s%s/%s/%s.jar" % (MAVEN, artifact, version, artifact),
             os.path.join(LIBS, "%s-%s.jar" % (artifact, version)), note, True)
            for artifact, version, note in ARTIFACTS]
    jobs += [(cf_url(file_id, filename), os.path.join(LIBS, filename), note, False)
             for filename, file_id, note in CF_FILES]

    for url, target, note, is_maven in jobs:
        filename = os.path.basename(target)
        if not os.path.exists(target) or os.path.getsize(target) < 20000:
            curl(url, target)
            # CurseForge 的文件在两个 CDN 上，一个不行就换另一个
            if not is_maven and os.path.getsize(target) < 20000:
                for host in CF_HOSTS[1:]:
                    curl(cf_url(int(url.rsplit("/", 2)[-2] + url.rsplit("/", 1)[-2]), filename, host), target)
                    if os.path.getsize(target) > 20000:
                        break
        size = os.path.getsize(target)
        if size < 20000:
            print("FAIL", filename, "下载失败或文件过小", size)
            continue
        sha1, sha512 = hashes(target)
        records.append({
            "slug": filename.split("-")[0],
            "name": filename,
            "version": filename[:-4].split("-")[-1],
            "filename": filename,
            "url": url,
            "sha1": sha1,
            "sha512": sha512,
            "size": size,
            "client": "required",
            "server": "required",
            "note": note,
        })
        print("OK  ", filename, size, "bytes")

    out = os.path.join(os.path.dirname(__file__), "ftb_mods.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print("saved", out, len(records), "mods")


if __name__ == "__main__":
    main()
