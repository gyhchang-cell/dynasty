"""Fetch three pinned Forge 1.20.1 integrations, checking upstream SHA-512."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PINS = {
    "patchouli": ("94dtOLgZ", "双页分类图鉴与可点击合成教学", "required"),
    "equipment-compare": ("x1lxEKIp", "对比手中与已装备物品的属性", "unsupported"),
    "lootr": ("mWTXC1ZX", "遗迹宝箱为每位玩家分别提供战利品", "required"),
}

def get(url):
    return subprocess.check_output(["curl", "-fsSL", "--retry", "2", "--max-time", "60",
                                    "-A", "DynastyModpack/1.4.0", url])

def main():
    manifest = ROOT / "tools/art/qol_mods.json"
    rows = json.loads(manifest.read_text())
    for slug, (version, note, server) in PINS.items():
        info = json.loads(get("https://api.modrinth.com/v2/version/" + version))
        assert "forge" in info["loaders"] and "1.20.1" in info["game_versions"]
        file = next(row for row in info["files"] if row["primary"])
        data = get(file["url"])
        assert hashlib.sha512(data).hexdigest() == file["hashes"]["sha512"]
        (ROOT / "libs" / file["filename"]).write_bytes(data)
        record = dict(slug=slug, name=info["name"], version=info["version_number"],
                      filename=file["filename"], url=file["url"], size=len(data),
                      client="required", server=server, note=note, **file["hashes"])
        rows = [row for row in rows if row["slug"] != slug] + [record]
        print(slug, file["filename"], "SHA-512 verified")
    manifest.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n")

if __name__ == "__main__":
    main()
