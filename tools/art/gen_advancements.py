"""生成「自动判定用」成就（trigger = minecraft:impossible，由模组代码发放）。

FTB 任务书用 advancement 任务来判定「玩家真的做过这件事」，而不是让玩家自己点完成。
运行：python3 tools/art/gen_advancements.py
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "src/main/resources/data/dynasty/advancements")
os.makedirs(OUT, exist_ok=True)

# id: (图标, 标题中文/英文, 描述中文/英文)
ADVANCEMENTS = {
    "exam_passed": ("minecraft:writable_book", "科举中第", "Exam passed",
                    "在科举中答对至少一题", "Answer at least one exam question"),
    "rank_official": ("dynasty:official_seal", "官阶初授", "First office",
                      "功名晋升，获得第一个官阶", "Reach your first official rank"),
    "rank_scholar": ("dynasty:jade_seal", "金榜题名", "Scholar",
                     "官阶升至举人（第 3 阶）", "Reach rank 3"),
    "rank_hanlin": ("dynasty:ink_stick", "翰苑清贵", "Hanlin scholar",
                    "官阶升至翰林（第 10 阶）", "Reach rank 10"),
    "rank_minister": ("dynasty:official_seal", "位列部堂", "Minister",
                      "官阶升至尚书（第 12 阶）", "Reach rank 12"),
    "rank_grand_secretary": ("dynasty:edict", "天下共主", "Grand Secretary",
                             "官阶升至大学士（第 13 阶）", "Reach rank 13"),
    "rank_chancellor": ("dynasty:gold_coin", "位极人臣", "Chancellor",
                        "官阶升至丞相（第 17 阶）", "Reach rank 17"),
    "rank_prince_regent": ("dynasty:jade_seal", "摄政天下", "Prince Regent",
                           "官阶升至摄政王（第 18 阶）", "Reach rank 18"),
    "rank_son_of_heaven": ("dynasty:dragon_emperor_seal", "君临天下", "Son of Heaven",
                           "官阶升至天子（第 19 阶）", "Reach rank 19"),
    "met_minister": ("minecraft:emerald", "拜见大臣", "Meet the minister",
                     "与大臣交谈，听取朝堂建议", "Talk to a minister"),
    "army_led": ("dynasty:tiger_tally", "虎符调兵", "Raise an army",
                 "用虎符列阵召集禁军", "Summon imperial guards with the tiger tally"),
    "rebellion_calmed": ("dynasty:official_seal", "安抚民心", "Calm the realm",
                         "把叛乱值压到 20 以下", "Push rebellion below 20"),
    "qilin_friend": ("dynasty:immortal_peach", "祥瑞麒麟", "Qilin friend",
                     "以仙桃结交麒麟", "Befriend a qilin with an immortal peach"),
    "entered_celestial": ("dynasty:jade_portal", "踏入天朝", "Entered the celestial realm",
                          "穿过天朝传送门进入天朝·龙庭", "Enter the celestial dynasty"),
    "entered_underworld": ("dynasty:return_talisman", "下探地府", "Entered the underworld",
                           "穿过地府传送门进入地府", "Enter the underworld"),
}


def main():
    for name, (icon, zh_title, en_title, zh_desc, en_desc) in ADVANCEMENTS.items():
        data = {
            "display": {
                "icon": {"item": icon},
                "title": {"translate": "advancements.dynasty.%s.title" % name},
                "description": {"translate": "advancements.dynasty.%s.description" % name},
                "frame": "task",
                "show_toast": True,
                "announce_to_chat": False,
                "hidden": False,
            },
            "criteria": {"code": {"trigger": "minecraft:impossible"}},
            "requirements": [["code"]],
            "parent": "dynasty:dynasty_root",
        }
        with open(os.path.join(OUT, name + ".json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("advancement:", name)
    print("共", len(ADVANCEMENTS), "个")


if __name__ == "__main__":
    main()
