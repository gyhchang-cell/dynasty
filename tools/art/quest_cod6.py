"""Preserve cod6's authored paid-army FTB tasks when regenerating merged recipes."""
import re
QUESTS={"100000000000014b","100000000000014f","1000000000000152","10000000000001c5","10000000000001d9","1000000000000191"}
NOTICE="&6军阵关卡&r：科举中第后，手持虎符打开关卡页。购兵、编队并部署后开战；击败本关首领且仍有士兵存活才会完成。全军覆没判败，重伤兵可在募兵台付费修整。"
TEXT={
"右键打开调兵界面，选择阵型与人数并实际召出部队。兵力条件看界面提示；潜行右键只是威慑，不算列阵。不要攻击自己的军队。":"先合成募兵台，在台前用银币购买刀卫/弩卫/盾卫。右键虎符打开兵册，快速编队或在阵图选兵选位后出阵；最多出战9名。潜行右键仍为威慑。",
"手持虎符右键，在调兵界面成功召集部队；只打开界面不算完成。":"先在募兵台付银币买兵，再手持虎符右键：编队→出阵。成功部署军籍兵才算完成；打开界面不算。伤兵收回后不会自动补满血。"
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
