"""Verify real compass lookup keys and all Dynasty navigation registry names.

Run: python3 tools/art/verify_compass_localization.py
No Minecraft launch or asset generation; inspects the shipped optional mod JARs.
"""
import json
from pathlib import Path
import re
import subprocess

from gen_dynasty3_json import WORLDGEN_NAMES, worldgen_lang

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "src/main/resources/data/dynasty"
LANG = ROOT / "src/main/resources/assets/dynasty/lang"


def registered_names():
    result = {}
    for kind, folders in {
        "structure": ("worldgen/structure", "worldgen/structure_set"),
        "biome": ("worldgen/biome",),
        "dimension": ("dimension",),
    }.items():
        result[kind] = set()
        for folder in folders:
            base = DATA / folder
            result[kind].update(p.relative_to(base).with_suffix("").as_posix()
                                for p in base.rglob("*.json"))
    return result


def localization_errors(languages=None):
    if languages is None:
        languages = {locale: json.loads((LANG / f"{locale}.json").read_text())
                     for locale in ("zh_cn", "en_us")}
    errors = []
    for kind, names in registered_names().items():
        authored = set(WORLDGEN_NAMES[kind])
        for name in sorted(names - authored):
            errors.append(f"生成器缺少 {kind}.dynasty.{name} 的中英名")
        for name in sorted(authored - names):
            errors.append(f"生成器中 {kind}.dynasty.{name} 已无对应注册文件")
        for name in sorted(names):
            key = f"{kind}.dynasty.{name.replace('/', '.')}"
            for locale, values in languages.items():
                value = values.get(key)
                if not value or value == key:
                    errors.append(f"{locale} 缺少 {key}")
                elif value != worldgen_lang(locale).get(key):
                    errors.append(f"{locale} {key} 与生成器不一致")
                elif locale == "zh_cn" and not re.search(r"[\u3400-\u9fff]", value):
                    errors.append(f"{key} 中文名仍是英文")
    return errors


def method_body(bytecode, method):
    match = re.search(r"^  (?:public|private).*\b" + re.escape(method)
                      + r"\([^\n]*\);\n(.*?)(?=^  (?:public|private)|\Z)",
                      bytecode, re.M | re.S)
    if not match:
        raise AssertionError(f"JAR 中找不到 {method}")
    return match.group(1)


def verify_actual_lookup():
    cases = (
        ("ExplorersCompass-1.20.1-1.4.0-forge.jar", "explorerscompass", "StructureUtils",
         (("getPrettyStructureName", "structure"), ("getDimensionName", "dimension"))),
        ("NaturesCompass-1.20.1-1.12.0-forge.jar", "naturescompass", "BiomeUtils",
         (("getBiomeName", "biome"), ("getDimensionName", "dimension"))),
    )
    for filename, package, class_name, methods in cases:
        jar = ROOT / "modpack/mods" / filename
        code = subprocess.check_output([
            "javap", "-p", "-c", "-classpath", str(jar),
            f"com.chaosthedude.{package}.util.{class_name}",
        ], text=True)
        for method, prefix in methods:
            body = method_body(code, method)
            assert re.search(r"// String " + prefix + r"\s*$", body, re.M), (method, prefix)
            assert "net/minecraft/Util.m_137492_:" in body, method  # makeDescriptionId
            assert "language/I18n.m_118938_:" in body, method     # client translation lookup
        if package == "explorerscompass":
            assert "translateStructureNames" in method_body(code, "getPrettyStructureName")


if __name__ == "__main__":
    errors = localization_errors()
    if errors:
        raise SystemExit("\n".join(errors))
    verify_actual_lookup()
    counts = ", ".join(f"{kind}={len(names)}" for kind, names in registered_names().items())
    print(f"罗盘汉化：通过；{counts}，中英齐全；两个实际 JAR 的 lookup 已核验。")
