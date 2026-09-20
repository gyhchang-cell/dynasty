"""One-time migration snapshot. Refuse to overwrite the frozen save-ID contract."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEST = Path(__file__).with_name("quest_legacy_v1.json")


def snapshot():
    if DEST.exists():
        raise SystemExit("The immutable legacy snapshot already exists; do not regenerate it.")
    chapters = []
    for path in sorted((ROOT / "modpack/config/ftbquests/quests/chapters").glob("*.snbt")):
        text = path.read_text()
        chapter = {"file": path.stem, "id": re.search(r'\n\tid: "([^"]+)"', text)[1], "quests": []}
        for raw in re.findall(r'\n\t\t\{\n(.*?)\n\t\t\}', text, re.S):
            def field(key):
                return re.search(r'^\t\t\t' + key + r': (.*)$', raw, re.M)[1]
            task = field("tasks")
            kind = re.search(r'type: "([^"]+)"', task)[1]
            target = re.search(r'(?:item: \{ id|entity|dimension|advancement): "([^"]+)"', task)[1]
            count = re.search(r'(?:count|value): (\d+)L', task)
            chapter["quests"].append({"id": json.loads(field("id")), "title": json.loads(field("title")),
                "icon": field("icon"), "kind": kind, "target": target,
                "count": int(count[1]) if count else 1, "tasks": task, "rewards": field("rewards")})
        chapters.append(chapter)
    DEST.write_text(json.dumps(chapters, ensure_ascii=False, indent=2) + "\n")
    print("Frozen", sum(len(c["quests"]) for c in chapters), "existing quests with task/reward IDs intact")


if __name__ == "__main__":
    snapshot()
