#!/usr/bin/env python3
"""Read-only preflight for an mrpack; does not certify third-party permissions.

Usage: python3 tools/art/check_modrinth_pack.py dist/dynasty-1.4.0.mrpack
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from urllib.parse import urlsplit
import zipfile


ALLOWED_HOSTS = frozenset({
    "cdn.modrinth.com", "github.com", "raw.githubusercontent.com", "gitlab.com",
})
VALID_ENV = frozenset({"required", "optional", "unsupported"})
FTB_RESTRICTED = ("ftb-quests-", "ftb-library-", "ftb-teams-", "ftb-ultimine-")


def safe_path(value):
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and str(path) == value


def check_pack(archive, mods=None):
    errors, warnings = [], []
    with zipfile.ZipFile(archive) as packed:
        names = packed.namelist()
        if len(names) != len(set(names)):
            errors.append("Duplicate entries in archive")
        for name in names:
            if not safe_path(name.rstrip("/")):
                errors.append(f"Unsafe archive path: {name!r}")
        index = json.loads(packed.read("modrinth.index.json"))
        if index.get("formatVersion") != 1 or index.get("game") != "minecraft":
            errors.append("Expected Minecraft mrpack formatVersion 1")
        for field in ("name", "versionId"):
            if not isinstance(index.get(field), str) or not index[field].strip():
                errors.append(f"Missing {field}")
        paths = set()
        files = index.get("files", [])
        for i, record in enumerate(files):
            path = record.get("path")
            label = f"files[{i}] {path}"
            if not safe_path(path):
                errors.append(f"{label}: unsafe installation path")
                continue
            if path in paths:
                errors.append(f"{label}: duplicate installation path")
            paths.add(path)
            hashes = record.get("hashes", {})
            for algorithm, length in (("sha1", 40), ("sha512", 128)):
                value = hashes.get(algorithm)
                if not isinstance(value, str) or not re.fullmatch(f"[0-9a-f]{{{length}}}", value):
                    errors.append(f"{label}: invalid {algorithm}")
            size = record.get("fileSize")
            if type(size) is not int or size <= 0:
                errors.append(f"{label}: invalid fileSize")
            env = record.get("env", {})
            if any(env.get(side, "required") not in VALID_ENV for side in ("client", "server")):
                errors.append(f"{label}: invalid environment")
            downloads = record.get("downloads", [])
            if not downloads:
                errors.append(f"{label}: missing download URL")
            for url in downloads:
                try:
                    parsed = urlsplit(url)
                    valid = (parsed.scheme == "https" and parsed.hostname in ALLOWED_HOSTS
                             and parsed.username is None and parsed.password is None
                             and parsed.port in (None, 443)
                             and not any(c.isspace() for c in url))
                except (TypeError, ValueError):
                    valid = False
                if not valid:
                    errors.append(f"{label}: disallowed download URL: {url}")
            if mods and path.startswith("mods/"):
                source = Path(mods) / path.removeprefix("mods/")
                if not source.is_file():
                    errors.append(f"{label}: missing local jar")
                else:
                    data = source.read_bytes()
                    if len(data) != size or any(hashlib.new(a, data).hexdigest() != hashes.get(a)
                                                for a in ("sha1", "sha512")):
                        errors.append(f"{label}: local jar does not match hashes/size")
        # Flags are warnings, not permission assumptions: explicit permission may exist.
        distributed = paths | {n.removeprefix("overrides/") for n in names}
        for path in sorted(distributed):
            if PurePosixPath(path).name.startswith(FTB_RESTRICTED):
                warnings.append(f"{path}: FTB cross-platform distribution needs explicit permission")
        return {"pack": str(archive), "version": index.get("versionId"),
                "indexed_files": len(files), "errors": errors, "warnings": warnings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--mods", type=Path, help="Also verify hashes and sizes against local jars")
    args = parser.parse_args()
    try:
        result = check_pack(args.archive, args.mods)
    except (OSError, KeyError, ValueError, zipfile.BadZipFile) as error:
        result = {"errors": [str(error)], "warnings": []}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
