#!/usr/bin/env python3
"""Build a scoped local update bundle; never touch launchers, saves or accounts."""
import hashlib
import json
from datetime import datetime
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[2]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    candidates = [p for p in (ROOT / "build/libs").glob("dynasty-*.jar")
                  if not any(suffix in p.name for suffix in ("-sources", "-javadoc", "-dev"))]
    assert len(candidates) == 1, f"Expected exactly one production JAR: {candidates}"
    jar = candidates[0]
    contract = json.loads((ROOT / "docs/content/schools-v1-contract.json").read_text())
    with zipfile.ZipFile(jar) as archive:
        names = set(archive.namelist())
        for cls in ("DynastySchoolWeapons", "DynastySchoolCombat", "DynastyCodexSchools"):
            assert f"com/dynasty/{cls}.class" in names, f"Stale JAR: {cls}"
        for item in contract["items"]:
            assert f'assets/dynasty/textures/item/{item["id"]}.png' in names
            assert f'data/dynasty/recipes/{item["id"]}.json' in names
        for trial in contract["trials"]:
            assert f'data/dynasty/advancements/{trial["id"]}.json' in names
        assert "assets/dynasty/textures/gui/title/imperial-dawn.png" in names
        assert not any("ImperialRuntimeQa" in name or "DynastyTitleQa" in name for name in names)
        # Ensure no source changes happened after building the JAR.
        for path in (ROOT / "src/main/resources").rglob("*"):
            if path.is_file():
                name = path.relative_to(ROOT / "src/main/resources").as_posix()
                # Gradle expands project variables in these two metadata templates.
                expected = (ROOT / "build/resources/main" / name).read_bytes() if name in ("META-INF/mods.toml", "pack.mcmeta") else path.read_bytes()
                assert name in names and archive.read(name) == expected, f"Rebuild changed resource: {name}"

    quest_root = ROOT / "modpack/config/ftbquests/quests"
    assert len(list((quest_root / "chapters").glob("*.snbt"))) == 35
    for route in ("guard", "sword", "archer", "talisman"):
        assert (quest_root / f"chapters/dynasty_build_{route}.snbt").is_file()
    payload = {f"mods/{jar.name}": jar.read_bytes()}
    payload.update({"config/ftbquests/quests/" + p.relative_to(quest_root).as_posix(): p.read_bytes()
                    for p in sorted(quest_root.rglob("*.snbt"))})
    readme = """Dynasty 王朝 · 四脉新章与攻击视野修正 · 2026-09-23

这是现有 Minecraft 1.20.1 / Forge 王朝整合包的增量更新，不是完整整合包。
内容：4条可自由切换的流派、4件武器、8件饰品、48个流派任务、
任务总览与饰品图鉴重排、原创主菜单。总计35章565任务。
包含青龙竖直俯冲、后羿弓移除准心法阵的最新修正；其他结界效果保留。
保留488条旧任务的身份/目标/奖励、59个主线节点及五项万能槽里程碑。

安装：
1. 完全退出游戏，备份你正在使用实例的 saves 文件夹与 config/ftbquests。
2. 确认“游戏文件夹”是启动器中当前 Dynasty 实例，而不是公共 .minecraft 或其他整合包。
3. 先备份该实例 mods 中旧 dynasty JAR，再用本包 mods 中新 JAR 替换。
   不要同时保留两个 Dynasty JAR；无需删除或替换其他模组。
4. 把本包 config/ftbquests/quests 合并到实例同名位置，覆盖同名任务配置。
   不要删除 saves 内的 ftbquests / ftbteams 进度，不要创建新存档来更新。
5. 重新启动游戏。服务端与所有客户端均须更新 Dynasty JAR；服务端也需任务配置。

使用：任务书进入“山河总览”；四流派可选且不阻塞旧主线。
饰品需要放入 Curios 对应槽位/万能槽，背包持有仅用于任务检测。
F6可临时返回原版标题菜单，永久回退参数为 -Ddynasty.vanillaMenu=true。
本工具没有向任何启动器实例安装文件、修改存档、提交或上传GitHub。
具体测试范围及已知限制见项目 docs/content/schools-remaster-v1.md。
"""
    payload["安装说明.txt"] = readme.encode("utf-8")
    manifest = {"release": "schools-remaster-v1", "date": "2026-09-23",
                "chapters": 35, "quests": 565, "school_quests": 48,
                "sha256": {name: digest(data) for name, data in payload.items()}}
    payload["update-manifest.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    output = ROOT / "dist/dynasty-schools-2026-09-23-update.zip"
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in payload.items():
            archive.writestr(name, data)
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
        assert all(archive.read(name) == data for name, data in payload.items())

    project_jar = ROOT / "modpack/mods" / jar.name
    if project_jar.exists() and project_jar.read_bytes() != jar.read_bytes():
        backup = ROOT / "build/backups" / ("schools-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
        backup.mkdir(parents=True, exist_ok=False)
        shutil.copy2(project_jar, backup / project_jar.name)
        print("Old project JAR backup:", backup / project_jar.name)
    project_jar.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(jar, project_jar)
    print("Project JAR:", project_jar)
    print("JAR SHA-256:", digest(jar.read_bytes()))
    print("Update bundle:", output)
    print("No game instances, worlds, progress files, commits or uploads were changed.")


if __name__ == "__main__":
    main()
