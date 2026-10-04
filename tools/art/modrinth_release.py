"""Modrinth-specific publication policy; never changes the playable instance.

Restricted FTB jars are not redistributed. Quest configuration is retained and
exact official download instructions travel with the pack. Other jars must be
resolved by their exact content hash, or have an explicitly reviewed licence.
"""
import hashlib
import json
from pathlib import Path
import subprocess
from urllib.error import URLError
from urllib.request import Request, urlopen

from check_modrinth_pack import ALLOWED_HOSTS
from urllib.parse import urlsplit

API = "https://api.modrinth.com/v2"
USER_AGENT = "Dynasty-modpack-publishing/1.4.0 (local release validation)"
MANUAL = {
    "ftb-library-forge-2001.2.13.jar": {
        "name": "FTB Library", "version": "2001.2.13",
        "page": "https://www.curseforge.com/minecraft/mc-mods/ftb-library-forge/files",
        "reason": "FTB 的跨平台再分发许可限制；从原作者页面自行安装。",
    },
    "ftb-teams-forge-2001.3.2.jar": {
        "name": "FTB Teams", "version": "2001.3.2",
        "page": "https://www.curseforge.com/minecraft/mc-mods/ftb-teams-forge/files/7499810",
        "reason": "任务队伍与共享进度所需；FTB 的跨平台再分发许可限制。",
    },
    "ftb-quests-forge-2001.4.22.jar": {
        "name": "FTB Quests", "version": "2001.4.22",
        "page": "https://www.curseforge.com/minecraft/mc-mods/ftb-quests-forge/files/8078538",
        "reason": "王朝任务书、主线展示与任务奖励所需；不将 FTB 文件打包再分发。",
    },
    "ftb-ultimine-forge-2001.1.8.jar": {
        "name": "FTB Ultimine", "version": "2001.1.8",
        "page": "https://www.curseforge.com/minecraft/mc-mods/ftb-ultimine-forge/files/7880472",
        "reason": "连锁采掘功能所需；FTB 的跨平台再分发许可限制。",
    },
    "item-filters-forge-2001.1.0-build.59.jar": {
        "name": "Item Filters", "version": "2001.1.0-build.59",
        "page": "https://www.curseforge.com/minecraft/mc-mods/item-filters/files/4838266",
        "reason": "原包中的任务筛选器；本轮不另行制作 LGPL 二进制/对应源码再分发包。",
    },
}
RESTRICTED_PREFIXES = ("ftb-quests-", "ftb-library-", "ftb-teams-", "ftb-ultimine-")
EMBEDDED = {
    "alltheleaks-1.1.3+1.20.1-forge.jar": {
        "sha1": "428d98891486f7a9e4864f7fe4fafa8223ad23d1",
        "sha512": "04691ff068e19a864723ed069c392977d23a222bde181b97d363423ff69f9d6a3c1dc28bfe9b89fc954ffcce447a9b128c45264140aa3ff14cb4953a11141424",
        "size": 1274165,
        "license": "MIT",
        "license_file": "licenses/alltheleaks-MIT.txt",
        "permission": "https://www.curseforge.com/minecraft/mc-mods/alltheleaks/license",
    },
}


def request_json(endpoint, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    request = Request(API + endpoint, data=data,
                      headers={"User-Agent": USER_AGENT, "Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=45) as response:
            return json.load(response)
    except URLError:
        # python.org's macOS runtime may lack installed CA roots. Use the native
        # curl trust store; do not disable TLS certificate verification.
        command = ['curl', '--fail', '--silent', '--show-error', '--retry', '2',
                   '--max-time', '45', '-H', 'User-Agent: ' + USER_AGENT]
        if data is not None:
            command += ['-H', 'Content-Type: application/json', '--data-binary', '@-']
        command += [API + endpoint]
        result = subprocess.run(command, input=data, capture_output=True, check=True)
        return json.loads(result.stdout)


def unique_sources(sources):
    records = {}
    for filename, url in sources:
        if filename in records and records[filename] != url:
            raise ValueError("同一模组存在冲突的下载地址: " + filename)
        records[filename] = url
    return list(records.items())


def prepare_release(sources, mods, lookup=None):
    mods = Path(mods)
    resolved, manual, embedded = [], [], []
    for filename, _original_url in unique_sources(sources):
        data = (mods / filename).read_bytes()
        hashes = {a: hashlib.new(a, data).hexdigest() for a in ("sha1", "sha512")}
        record = {"path": "mods/" + filename, "hashes": hashes, "fileSize": len(data)}
        if filename in MANUAL:
            manual.append({**MANUAL[filename], "filename": filename, **record})
        elif filename.startswith(RESTRICTED_PREFIXES):
            raise ValueError("未经许可的 FTB 版本不能写进 Modrinth 包: " + filename)
        elif filename in EMBEDDED:
            permission = EMBEDDED[filename]
            if any(hashes[a] != permission[a] for a in hashes) or len(data) != permission["size"]:
                raise ValueError("许可核验对应的模组版本/哈希发生变化: " + filename)
            embedded.append({**record, "filename": filename, **permission})
        else:
            resolved.append(record)

    if lookup is None:
        lookup = request_json("/version_files", {
            "hashes": [r["hashes"]["sha1"] for r in resolved], "algorithm": "sha1",
        })
    missing = []
    for record in resolved:
        sha1 = record["hashes"]["sha1"]
        version = lookup.get(sha1, {})
        matching = [f for f in version.get("files", [])
                    if all(f.get("hashes", {}).get(a) == value for a, value in record["hashes"].items())
                    and f.get("size") == record["fileSize"]]
        if not matching:
            missing.append(record["path"])
            continue
        remote = matching[0]
        parsed = urlsplit(remote["url"])
        if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
            raise ValueError("官方查询返回了不被接受的地址: " + remote["url"])
        if "1.20.1" not in version.get("game_versions", []) or "forge" not in version.get("loaders", []):
            raise ValueError("模组文件未标注支持 Minecraft 1.20.1 Forge: " + record["path"])
        # Client-only rendering/UI files must not be installed on a dedicated server.
        environment = version.get("environment")
        if environment == "client_only":
            env = {"client": "required", "server": "unsupported"}
        else:
            # These jars are already part of the tested single-player instance.
            # Server-logic utilities (Noisium/harvesting/etc.) must remain on the
            # physical client for its integrated server; do not silently drop them.
            env = {"client": "required", "server": "required"}
        record.update({"downloads": [remote["url"]], "env": env})
    if missing:
        raise ValueError("以下文件无法按完整 SHA-1/SHA-512 找到同版本官方来源，已停止导出，不会擅自删模组:\n"
                         + "\n".join(missing))
    return resolved, manual, embedded


def manual_guide(manual):
    lines = [
        "Dynasty 王朝 1.4.0 — Modrinth 安装注意事项 / Required manual dependencies",
        "Minecraft 1.20.1 / Forge 47.4.10",
        "",
        "重要：此 Modrinth 包不是完整开箱即用版。",
        "任务配置、主线章节及 Dynasty 本体保留；以下原包依赖不能通过此包自动安装。",
        "在进入新世界或已有存档之前，先从原作者页面下载指定的 Forge 1.20.1 文件。",
        "将下载的 .jar 放入这个新实例的 mods 文件夹，再启动游戏。不要下载 NeoForge/Fabric 或 1.21 版本。",
        "多人：客户端与服务器均安装同版本依赖，保留整合包 config/ftbquests/ 配置。",
        "缺少 FTB Quests/Library/Teams 时不会有完整的王朝任务书、任务奖励及队伍共享进度。",
        "缺少 Ultimine 时没有原包的连锁采掘。不要在依赖未补齐时继续既有主线存档。",
        "",
        "IMPORTANT: Install the following exact Forge 1.20.1 versions into mods/ before playing.",
        "FTB quest/team progression is not available until the FTB dependencies are installed.",
        "The quest configuration is included; no FTB binaries are redistributed in this pack.",
        "",
    ]
    for filename in MANUAL:
        record = next((r for r in manual if r["filename"] == filename), None)
        if record:
            lines += [f"{record['name']} — {record['version']}", f"  文件名: {filename}",
                      f"  原作者下载页: {record['page']}", f"  SHA-1: {record['hashes']['sha1']}",
                      f"  用途/说明: {record['reason']}", ""]
    lines += ["许可说明: https://feed-the-beast.com/raw/docs/mod-license",
              "如希望启动器自动安装完整依赖，请使用作者已发布的 CurseForge 版本。", ""]
    return "\n".join(lines)
