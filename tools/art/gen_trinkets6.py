"""Four-school metadata. No copied/tinted artwork: 128px original assets are supplied separately."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = json.loads((ROOT / "docs/content/schools-v1-contract.json").read_text())
ITEMS = {entry["id"]: entry for entry in CONTRACT["items"]}
TRINKETS = {
    key: (entry["zh"], entry["en"], key, (255, 255, 255), entry["recipe"], tuple(entry["spec"]))
    for key, entry in ITEMS.items() if entry["kind"] == "accessory"
}
TEXTURE_SIZE = {key: 128 for key in TRINKETS}
SCHOOL_TEXT = {key: (entry["zh_effect"], entry["en_effect"]) for key, entry in ITEMS.items()}

if __name__ == "__main__":
    from gen_schools import main
    main()
