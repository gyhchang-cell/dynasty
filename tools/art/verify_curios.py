"""验证全部饰品分类、万能槽与任务加槽的跨文件契约。"""
import json
import re
from pathlib import Path
from gen_curios import ROOT, DATA, SLOT_NAMES, classifications


def verify():
    mapping = classifications()
    master = json.loads((DATA / "dynasty/tags/items/accessories.json").read_text())["values"]
    assert set(master) == {"dynasty:" + name for name in mapping}
    actual = {}
    for slot in SLOT_NAMES:
        tag = json.loads((DATA / f"curios/tags/items/{slot}.json").read_text())
        for item in tag["values"]:
            if isinstance(item, str) and item.startswith("dynasty:"):
                assert item not in actual, "重复分类：" + item
                actual[item] = slot
        definition = json.loads((DATA / f"dynasty/curios/slots/{slot}.json").read_text())
        assert definition["size"] == (2 if slot == "ring" else 1)
    assert actual == {"dynasty:" + name: slot for name, slot in mapping.items()}
    curio_tag = json.loads((DATA / "curios/tags/items/curio.json").read_text())
    assert not any(isinstance(v, str) and v.startswith("dynasty:") for v in curio_tag["values"]), \
        "curios:curio 是通用物品标签，会绕过分类限制"
    universal = json.loads((DATA / "dynasty/curios/slots/curio.json").read_text())
    assert universal["size"] == 1 and universal["validators"] == ["dynasty:accessory"]
    player = json.loads((DATA / "dynasty/curios/entities/player.json").read_text())
    assert set(player["slots"]) == set(SLOT_NAMES) | {"curio"}
    assert not list(DATA.glob("*/curios/slots/dynasty_trinket.json")), "废弃专属槽被生成器重新创建"
    assert not (DATA / "curios/tags/items/dynasty_trinket.json").exists()

    milestones = json.loads((DATA / "dynasty/curios_progression.json").read_text())
    assert len(milestones) == 5
    assert len({v["quest_id"] for v in milestones.values()}) == 5
    quests = {}
    reward_ids = set()
    for path in (ROOT / "modpack/config/ftbquests/quests/chapters").glob("*.snbt"):
        for block in path.read_text().split("\t\t{\n")[1:]:
            match = re.search(r'^\s*id: "([0-9a-f]+)"', block)
            if match:
                quests[match[1]] = block
            for reward in re.findall(r'\{ id: "([0-9a-f]+)", type:', block):
                assert reward not in reward_ids, "重复任务目标/奖励 ID：" + reward
                reward_ids.add(reward)
    for key, milestone in milestones.items():
        quest = quests[milestone["quest_id"]]
        assert quest.count("dynasty unlock_curio " + key + '"') == 1
        assert "team_reward: false, elevate_perms: true" in quest
        assert 'shape: "hexagon"' in quest
        assert "永久 +1 万能饰品槽" in quest
    print(f"Curios 自检通过：{len(mapping)} 件逐项分类、无通用标签串槽、专属槽移除、5 个个人里程碑奖励一致。")


if __name__ == "__main__":
    verify()
