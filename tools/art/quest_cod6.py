"""Preserve cod6's authored paid-army FTB tasks when regenerating merged recipes."""
import re
# Same order as ArmyEncounters.BOSSES. The previous encounter opens the next.
QUESTS = {
    "100000000000014b": "rebel_general",
    "100000000000014f": "eunuch_mastermind",
    "1000000000000152": "undead_first_emperor",
    "10000000000001c5": "nine_heaven_general",
    "10000000000001d9": "dragon_king",
    "1000000000000191": "dragon_emperor",
}
NOTICE="&6军阵关卡&r：科举中第后，手持虎符打开关卡页。购兵、编队并部署后开战；击败本关首领且仍有士兵存活才会完成。全军覆没判败，重伤兵可在募兵台付费修整。"
TEXT={
"右键打开调兵界面，选择阵型与人数并实际召出部队。兵力条件看界面提示；潜行右键只是威慑，不算列阵。不要攻击自己的军队。":"先做两枚虎符，留一枚调兵。工作台上排放三个铜锭，中排放木板、虎符、木板，下排两角各放一块木板，取出募兵台。右键募兵台选兵并确认购买：刀卫12银币、弩卫16银币、盾卫20银币。",
"手持虎符右键，在调兵界面成功召集部队；只打开界面不算完成。":"在募兵台买兵后，带虎符到平坦的干地，站直右键打开兵册。点「快速编队」再点「出阵」；手动编队可选兵点阵位，每页九个阵位，可翻页。队伍出现在场上才记录进度。收阵保留伤势，重伤兵回募兵台付费修整。"
}
def expected_tasks(quest):
    target=quest["target"].removeprefix("dynasty:")
    if quest["kind"]=="kill" and quest["id"].lower() in QUESTS:
        task_id=re.search(r'id: "([0-9a-fA-F]+)"',quest["tasks"])[1]
        return '[{ id: "'+task_id+'", type: "advancement", advancement: "dynasty:army_clear_'+target+'" }]'
    return quest["tasks"]
def apply(chapters):
    for chapter in chapters:
        for quest in chapter["quests"]:
            quest["description"]=[TEXT.get(line,line) for line in quest["description"]]
            tasks=expected_tasks(quest)
            if tasks!=quest["tasks"]:
                quest["description"].insert(0,NOTICE)
                quest["tasks"]=tasks
