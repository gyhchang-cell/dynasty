#!/usr/bin/env python3
"""Build a verified, save-free ritual/sculpture release. Never syncs a launcher or edits a save."""
from pathlib import Path
from datetime import datetime
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
JAR_NAME = "dynasty-1.4.0.jar"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def verify_jar(path):
    with zipfile.ZipFile(path) as jar:
        assert jar.testzip() is None, "Corrupt core jar"
        for name in (
            "com/dynasty/ritual/ZhenyuanSovereign.class",
            "com/dynasty/ritual/ZhenyuanRitualService.class",
            "com/dynasty/client/ZhenyuanNodeRenderer.class",
            "com/dynasty/structure/megabuild/SculptureWorkshop.class",
            "data/dynasty/dimension/zhenyuan_arena.json",
            "data/dynasty/ritual/zhenyuan_altar.json",
            "data/dynasty/sculptures/longque_sanctuary.json",
            "data/dynasty/sculptures/longque_sanctuary.vox.gz",
            "data/dynasty/sculptures/yunqi_manor.json",
            "data/dynasty/sculptures/yunqi_manor.vox.gz",
        ):
            assert name in jar.namelist(), "Missing release feature: " + name
        for path in (ROOT / "src/main/resources").rglob("*"):
            if not path.is_file():
                continue
            name = path.relative_to(ROOT / "src/main/resources").as_posix()
            expected = (ROOT / "build/resources/main" / name) if name in ("META-INF/mods.toml", "pack.mcmeta") else path
            assert jar.read(name) == expected.read_bytes(), "Stale packaged resource: " + name
        assert not any("ZhenyuanRenderQa" in n for n in jar.namelist()), "Test renderer leaked into production"


def main():
    jar = ROOT / "build/libs" / JAR_NAME
    verify_jar(jar)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    release = ROOT / "dist" / ("zhenyuan-sculptures-" + stamp)
    backup = ROOT / "build/backups" / ("before-zhenyuan-" + stamp)
    release.mkdir(parents=True, exist_ok=False)
    backup.mkdir(parents=True, exist_ok=False)
    staged = ROOT / "modpack/mods" / JAR_NAME
    if staged.exists():
        shutil.copy2(staged, backup / JAR_NAME)
    archive_names = ["dynasty-modpack-1.4.0.zip", "dynasty-1.4.0.mrpack", "dynasty-1.4.0-manual.zip"]
    for name in archive_names:
        old = ROOT / "dist" / name
        if old.exists():
            shutil.copy2(old, backup / name)
    shutil.copy2(jar, staged)
    for script in ("make_uploadable_packs.py", "make_manual_and_guide.py"):
        subprocess.run([sys.executable, str(ROOT / "tools/art" / script)], cwd=ROOT, check=True)
    readme = ROOT / "docs/ritual/zhenyuan-v3.md"
    validation = ROOT / "docs/ritual/validation.json"
    report = {"core_sha256": digest(jar.read_bytes()), "backup": str(backup), "no_live_sync": True,
              "no_save_files": True, "artifacts": {}}
    for name in archive_names:
        source = ROOT / "dist" / name
        with zipfile.ZipFile(source, "a", zipfile.ZIP_DEFLATED) as archive:
            prefix = "" if name.endswith("manual.zip") else "overrides/"
            archive.write(readme, prefix + "镇渊终战与巨型建筑-说明.md")
            if validation.exists():
                archive.write(validation, prefix + "dynasty-ritual-validation.json")
        with zipfile.ZipFile(source) as archive:
            assert archive.testzip() is None, "Corrupt archive: " + name
            names = archive.namelist()
            assert not any(n.startswith(("saves/", "overrides/saves/")) for n in names), "Save accidentally packaged"
            assert not any(Path(n).name.lower().startswith(("worldedit-", "worldedit-mod-", "prefab-")) for n in names), "Workshop-only mod leaked"
            target = ("mods/" if name.endswith("manual.zip") else "overrides/mods/") + JAR_NAME
            assert digest(archive.read(target)) == report["core_sha256"], "Old core in " + name
        shutil.copy2(source, release / name)
        report["artifacts"][name] = {"sha256": digest(source.read_bytes()), "bytes": source.stat().st_size}
    shutil.copy2(jar, release / JAR_NAME)
    if readme.exists():
        shutil.copy2(readme, release / "镇渊终战与巨型建筑-说明.md")
    if validation.exists():
        shutil.copy2(validation, release / "validation.json")
    report_file = release / "release-verification.json"
    report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("VERIFIED_RELEASE", release)
    print("BACKUP", backup)


if __name__ == "__main__":
    main()
