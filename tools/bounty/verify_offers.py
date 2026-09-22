#!/usr/bin/env python3
"""悬赏委托数据包自检（只读，标准库）：定义、奖励约束、前置、词条、方块资源与配方。

用法：
    python3 tools/bounty/verify_offers.py
    python3 tools/bounty/verify_offers.py --root /别的/仓库
"""
import argparse
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OFFERS_DIR = "src/main/resources/data/dynasty/bounty_offers"
FORBIDDEN_HINTS = ("token", "seal", "rebel_head", "emperor_bone", "xuantian_jade",
                   "supreme_sword", "tianzi_sword", "halberd_fangtian", "dragon_slayer",
                   "unlock_curio", "accessory_slot")


def check_offer(root, where, data, counts, problems, lang):
    for field in ("id", "type", "target_kind", "target", "amount", "weight", "title", "description", "reward"):
        if field not in data:
            problems.append("%s：缺少字段 %s" % (where, field))
    if data.get("type") not in counts:
        problems.append("%s：type 非法 %r" % (where, data.get("type")))
    else:
        counts[data["type"]] += 1
    expect_kind = {"acquire": "item", "hunt": "entity", "explore": "dimension"}.get(data.get("type"))
    if expect_kind and data.get("target_kind") != expect_kind:
        problems.append("%s：type=%s 时 target_kind 必须是 %s" % (where, data.get("type"), expect_kind))
    if not isinstance(data.get("amount"), int) or not 1 <= data["amount"] <= 512:
        problems.append("%s：amount 非法 %r" % (where, data.get("amount")))
    if not isinstance(data.get("weight"), int) or not 1 <= data.get("weight") <= 100:
        problems.append("%s：weight 非法 %r" % (where, data.get("weight")))

    reward = data.get("reward") or {}
    if reward.get("emeralds", 0) > 16:
        problems.append("%s：绿宝石奖励过多 %r" % (where, reward.get("emeralds")))
    if reward.get("experience", 0) > 30:
        problems.append("%s：经验奖励过多 %r" % (where, reward.get("experience")))
    if not reward.get("emeralds") and not reward.get("items") and not reward.get("experience"):
        problems.append("%s：奖励为空" % where)
    for stack in reward.get("items", []):
        item = stack.get("item", "")
        if any(hint in item for hint in FORBIDDEN_HINTS):
            problems.append("%s：奖励里出现禁止物品 %s" % (where, item))
        if not 1 <= stack.get("count", 0) <= 32:
            problems.append("%s：补给数量非法 %r" % (where, stack.get("count")))

    prerequisite = data.get("prerequisite")
    if prerequisite:
        if not prerequisite.startswith("dynasty:"):
            problems.append("%s：前置只允许本模组已核实的进度 ID（当前 %s）" % (where, prerequisite))
        else:
            adv = os.path.join(root, "src/main/resources/data/dynasty/advancements",
                               prerequisite.split(":", 1)[1] + ".json")
            if not os.path.exists(adv):
                problems.append("%s：前置 %s 找不到对应成就文件" % (where, prerequisite))

    if data.get("type") == "explore" and data.get("target", "").startswith("dynasty:"):
        dimension = os.path.join(root, "src/main/resources/data/dynasty/dimension",
                                 data["target"].split(":", 1)[1] + ".json")
        if not os.path.exists(dimension):
            problems.append("%s：考察维度 %s 不是仓库里已有的维度" % (where, data["target"]))
    if data.get("type") == "hunt" and not data.get("target", "").startswith("minecraft:"):
        problems.append("%s：本轮讨伐委托只允许普通原版敌对生物，收到 %s" % (where, data.get("target")))

    for key in (data.get("title"), data.get("description")):
        for language, table in lang.items():
            if key not in table:
                problems.append("%s：%s 缺少词条 %s" % (where, language, key))
            elif not table[key].strip():
                problems.append("%s：%s 的词条 %s 是空白" % (where, language, key))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=ROOT)
    args = parser.parse_args()
    root = args.root
    problems = []

    offers_dir = os.path.join(root, OFFERS_DIR)
    if not os.path.isdir(offers_dir):
        print("找不到委托目录：%s" % offers_dir)
        return 1

    lang = {}
    lang_dir = os.path.join(root, "src/main/resources/assets/dynasty/lang")
    for language in ("zh_cn", "en_us"):
        with open(os.path.join(lang_dir, language + ".json"), encoding="utf-8") as handle:
            lang[language] = json.load(handle)

    ids = {}
    counts = {"acquire": 0, "hunt": 0, "explore": 0}
    names = sorted(name for name in os.listdir(offers_dir) if name.endswith(".json"))
    for name in names:
        where = "%s/%s" % (OFFERS_DIR, name)
        try:
            with open(os.path.join(offers_dir, name), encoding="utf-8") as handle:
                data = json.load(handle)
        except json.JSONDecodeError as error:
            problems.append("%s：JSON 解析失败 %s" % (where, error))
            continue
        check_offer(root, where, data, counts, problems, lang)
        if data.get("id") in ids:
            problems.append("%s：委托 ID 与 %s 重复" % (where, ids[data["id"]]))
        ids[data.get("id")] = where

    required = [
        "src/main/resources/assets/dynasty/blockstates/bounty_board.json",
        "src/main/resources/assets/dynasty/models/block/bounty_board.json",
        "src/main/resources/assets/dynasty/models/item/bounty_board.json",
        "src/main/resources/data/dynasty/recipes/bounty_board.json",
        "src/main/resources/data/dynasty/advancements/recipes/bounty_board.json",
    ]
    for rel in required:
        if not os.path.exists(os.path.join(root, rel)):
            problems.append("缺少文件：%s" % rel)
    for language, table in lang.items():
        for key in ("block.dynasty.bounty_board", "dynasty.bounty.gui.title", "dynasty.bounty.gui.accept",
                    "dynasty.bounty.gui.abandon", "dynasty.bounty.gui.submit", "dynasty.bounty.gui.claim",
                    "dynasty.bounty.gui.target", "dynasty.bounty.gui.progress", "dynasty.bounty.gui.reward",
                    "dynasty.bounty.msg.full", "dynasty.bounty.msg.insufficient", "dynasty.bounty.msg.no_space",
                    "dynasty.bounty.msg.already_claimed", "dynasty.bounty.msg.locked"):
            if key not in table:
                problems.append("%s：缺少界面词条 %s" % (language, key))

    print("委托定义 %d 条：收购 %d / 讨伐 %d / 考察 %d"
          % (len(names), counts["acquire"], counts["hunt"], counts["explore"]))
    if counts["acquire"] < 10 or counts["hunt"] < 4 or counts["explore"] < 4:
        problems.append("数量不足：需要收购 10 / 讨伐 4 / 考察 4")
    if problems:
        print("发现问题 ❌")
        for problem in problems:
            print("   - " + problem)
        return 1
    print("数据包自检：通过 ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())

