"""Merge only the title-screen strings; safe to run after other language generators.

python3 tools/art/gen_title_lang.py
python3 tools/art/gen_title_lang.py --check
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STRINGS = {
    "zh_cn": {
        "ui.dynasty.title.eyebrow": "东方神话 · 山河征途",
        "ui.dynasty.title.tagline": "执神兵，御千军，开一代王朝。",
        "ui.dynasty.title.language": "语言",
        "ui.dynasty.title.accessibility": "无障碍",
        "ui.dynasty.title.vanilla_hint": "F6 · 原版菜单",
        "ui.dynasty.title.path_1": "玄武守御 · 防守反击",
        "ui.dynasty.title.path_2": "游龙剑舞 · 连招收势",
        "ui.dynasty.title.path_3": "逐星射艺 · 标记追击",
        "ui.dynasty.title.path_4": "道门律令 · 法器控场",
    },
    "en_us": {
        "ui.dynasty.title.eyebrow": "EASTERN MYTHS / A NEW REIGN",
        "ui.dynasty.title.tagline": "Divine arms. Loyal armies. Your dynasty.",
        "ui.dynasty.title.language": "Language",
        "ui.dynasty.title.accessibility": "Accessibility",
        "ui.dynasty.title.vanilla_hint": "F6 / Original menu",
        "ui.dynasty.title.path_1": "Black Tortoise / Guard & counter",
        "ui.dynasty.title.path_2": "Dragon Dance / Chain & finish",
        "ui.dynasty.title.path_3": "Star Chaser / Mark & pursue",
        "ui.dynasty.title.path_4": "Taoist Edicts / Relics & control",
    },
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check without writing language files")
    args = parser.parse_args()
    problems = []
    for locale, additions in STRINGS.items():
        path = ROOT / "src/main/resources/assets/dynasty/lang" / (locale + ".json")
        data = json.loads(path.read_text(encoding="utf-8"))
        if args.check:
            problems.extend(f"{locale}: {key} missing or stale" for key, value in additions.items()
                            if data.get(key) != value)
        elif any(data.get(key) != value for key, value in additions.items()):
            data.update(additions)
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if problems:
        raise SystemExit("\n".join(problems))
    print("Title language: 9 keys × 2 locales " + ("verified" if args.check else "merged"))


if __name__ == "__main__":
    main()
