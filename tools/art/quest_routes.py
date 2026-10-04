"""Optional Dynasty build journeys. Stable IDs; old equipment is linked, never copied.

This module is called by quest_story only after its legacy/main book is complete.
Mechanic trials must point to real server-granted advancements, not checkmarks.
"""
import json
from pathlib import Path

GROUPS = [(6, "&6&l山河总览 · 先选方向"), (1, "&6&l主线旅程 · 从这里开始"),
          (7, "&c&l王朝流派 · 选一条试试"), (2, "&2&l支线探索 · 自由选择"),
          (3, "&b&l装备与配方 · 按需查询"), (4, "&d&l饰品搭配 · 按槽位查询"),
          (5, "&8旧版记录 · 非推荐")]

# Keys and numeric ranges are save identities, independent of title/order changes.
ROUTES = {
    "guard": dict(base=0x30000, chapter=0x510, title="玄武守御", color="#7bb7ab",
        weapon="zhenyue_blade", trinkets=("zhenguan_mirror", "huben_bracer"),
        style="bastion", slogan="稳住阵脚，再还以重击", dimension="celestial_dynasty",
        enemy="zombie", boss="rebel_general", armor="bronze_chestplate",
        backup="heart_mirror", graduate="qinglong_dao"),
    "sword": dict(base=0x30100, chapter=0x511, title="游龙剑舞", color="#87c9dc",
        weapon="liuyun_sword", trinkets=("liancheng_tassel", "tayun_pendant"),
        style="ribbon", slogan="走位连击，进退有度", dimension="celestial_dynasty",
        enemy="assassin", boss="eunuch_mastermind", armor="brocade_chestplate",
        backup="sword_tassel", graduate="longyuan_sword"),
    "archer": dict(base=0x30200, chapter=0x512, title="逐星射艺", color="#d9bf79",
        weapon="zhuxing_bow", trinkets=("guanxing_pendant", "mingxian_ring"),
        style="constellation", slogan="看准时机，让每一箭有价值", dimension="jiuxiao",
        enemy="rebel_soldier", boss="nine_heaven_general", armor="leather_chestplate",
        backup="arrow_quiver", graduate="houyi_bow"),
    "talisman": dict(base=0x30300, chapter=0x513, title="道门律令", color="#c6a5de",
        weapon="chiling_brush", trinkets=("sitian_seal", "dingfeng_silk"),
        style="ritual", slogan="留足退路，用律令掌控交战节奏", dimension="underworld",
        enemy="terracotta_warrior", boss="undead_first_emperor", armor="cinnabar_chestplate",
        backup="talisman_pouch", graduate="thunder_talisman"),
}


def load_contracts():
    from gen_curios import SLOT_NAMES
    raw = json.loads((Path(__file__).resolve().parents[2] / "docs/content/schools-v1-contract.json").read_text())
    items = {item["id"]:item for item in raw["items"]}
    trials = {trial["id"]:trial for trial in raw["trials"]}
    fields = {
        "guard": ("格挡后的反击", "在主世界找僵尸，先观察攻击朝向；不要把『正面可格挡伤害减半』当成全方向无敌。",
                  "天朝·龙庭", "带两座天朝传送门，设置回程据点后再向外探索。",
                  "叛将主要按主线先在主世界寻找；本页的天朝远行是独立支线，不是要求在天朝等叛将。冲锋预警优先侧移，守势不能取代躲大招。"),
        "sword": ("三击成势", "在主世界与刺客交手，控制攻击冷却与后退节奏。普通敌人可能一击倒下；真正的三连试炼应选择能承受三次命中的高生命敌人，不要攻击友军。",
                  "天朝·龙庭", "进入天朝后先留回程门、照明与战斗空间，别在狭窄地形被援军堵住。",
                  "天朝寻找宦官首脑。清理援兵、等待攻击冷却，再对同一目标打连段；换目标会重置，不要为保连击硬吃毒雾。"),
        "archer": ("第二箭追星", "在主世界找叛军练满蓄与距离，提前准备箭矢。普通小怪可能首箭就倒下；标记试炼要选能承受两箭的高生命敌人。不是连按两下左键。",
                   "九霄天界", "按主线准备九霄传送门与回程门，带缓降手段与搭路方块；先保证能站稳，再选射击位。",
                   "九霄天将有落雷和位移。先离开预警圈、确保背后不是悬崖，再抓机会满蓄；不要为第二箭站桩坠落。"),
        "talisman": ("敕令后的蓄势", "在地府找兵马俑战士；控场后留足距离蓄势。敌人必须在视线内，不能隔墙释放；移动或松手过早会取消蓄势。",
                     "地府幽冥", "按主线制作地府门，带第二座回程门、照明与恢复品。先建安全落脚点，再探索地府敌人。",
                     "在地府寻找不死始皇。Boss 的控场效果比普通敌人短，看到大招先躲，不要把缓慢当定身或免伤。")}
    result = {}
    for key,spec in ROUTES.items():
        title,field,dim_title,dim,boss = fields[key]
        trial_id="build_"+key+"_trial"
        result[key] = {"intro":raw["stage"]+" "+raw["rules"],
            "weapon":items[spec["weapon"]]["zh_effect"],
            "trinkets":[items[item]["zh_effect"] + f" 对应{SLOT_NAMES[items[item]['slot']]}分类槽或万能槽。" for item in spec["trinkets"]],
            "trial_title":title,"advancement":"dynasty:"+trial_id,"trial":trials[trial_id]["condition"],
            "field":field,"dimension_title":dim_title,"dimension":dim,"boss":boss}
    return result


def code(prefix, number):
    return f"{prefix}{number:015x}"


def jump(label, target):
    from boss_quest_guides import jump as native_jump
    return native_jump(label, target)


def reward(number, xp=0, item=None, count=1):
    """New rewards are personal, non-repeatable supplies/XP; never slot/merit commands."""
    rows = []
    if xp:
        rows.append(f'{{ id: "{code(3, 0x500000 + number*4)}", type: "xp", xp: {xp}, team_reward: false }}')
    if item:
        rows.append(f'{{ id: "{code(3, 0x500001 + number*4)}", type: "item", item: {{ id: "{item}", Count: {count}b }}, team_reward: false }}')
    return "[" + ", ".join(rows) + "]"


def node(number, title, kind, target, purpose, how, *, count=1, items=None, xp=0,
         reward_item=None, reward_count=1, role="build"):
    fields = {"item": f'item: {{ id: "{target}", Count: 1b }}, count: {count}L',
              "kill": f'entity: "{target}", value: {count}L',
              "advancement": f'advancement: "{target}"', "dimension": f'dimension: "{target}", value: 1L'}
    if items:
        task_rows = [f'{{ id: "{code(2, 0x500000 + number*16+i)}", type: "item", '
                     f'item: {{ id: "{item}", Count: 1b }}, count: {amount}L }}'
                     for i, (item, amount) in enumerate(items)]
    else:
        field = ", " + fields[kind] if kind in fields else ""
        task_rows = [f'{{ id: "{code(2, number)}", type: "{kind}"{field} }}']
    return {"id":code(1, number), "title":title, "display_title":title,
        "kind":kind, "target":target, "count":count, "items":items or [],
        "icon":f'{{ id: "{target if kind=="item" else "dynasty:dynasty_manual"}" }}',
        "tasks":"[" + ", ".join(task_rows) + "]", "rewards":reward(number, xp, reward_item, reward_count),
        "purpose":purpose, "how":how, "deps":[], "role":role, "shape":"square" if kind=="checkmark" else "circle",
        "size":1.0, "subtitle":"阅读确认 · 不检测操作" if kind=="checkmark" else "真实检测 · 可选流派，不阻塞主线",
        "description":["&6&l为什么做&r", purpose, "", "&e&l现在怎么做&r", how]}


def add_recipe(q, recipes, name):
    if q["kind"] != "item":
        return
    q["recipe_ids"] = [r["id"] for r in recipes.get(q["target"], [])]
    for recipe in recipes.get(q["target"], []):
        text = " + ".join(f"{name(k)}×{v}" for k, v in recipe["ingredients"].items())
        q["description"] += ["", "&b&l材料与制作&r", text + f" → {name(q['target'])}×{recipe['output']}。",
                             "点击本页任务栏里的物品图标，直接打开 JEI 合成界面；多条配方任选一种。也可悬停按 R，任务不收走物品。"]


def themed_branches(key, base, contract):
    """Different play preparation, not four copies of collect food / compass / portal."""
    if key == "guard":
        return {
            6: node(base+6,"备用盾 · 不把守势当无敌","item","minecraft:shield",
                "先练面向来击，再用镇岳刀完成自己的格挡反击。",
                "六块木板与一块铁锭制作盾牌。盾牌用于观察敌人的正面攻击；招式试炼必须换成镇岳刀本身右键格挡。保持后方有退路，范围大招要离开预警，不能靠举盾硬吃。",xp=10),
            7: node(base+7,"守住一线 · 迎击三只僵尸","kill","minecraft:zombie",
                "在较低压力下练习接击、反击与后撤。",contract["field"]+" 主世界夜间或黑暗洞穴可遇到僵尸；亲自击败3只。此处记录普通击杀，不检测是否格挡；真实格挡反击由招式试炼负责。",count=3,xp=45),
            8: node(base+8,"伤后恢复 · 金创药两份","item","dynasty:healing_salve",
                "格挡减伤并不等于不掉血，准备脱离战斗后的恢复。",
                "制作金创药×2并放在背包。右键使用会消耗；此目标只检测持有，不要求浪费药品。朱砂来自神庙、法阵遗迹或帝陵地宫宝箱，不是挖矿材料。",count=2,xp=20),
            9: node(base+9,"重甲改装 · 青铜补片","item","dynasty:bronze_ingot",
                "身法不熟时优先补防具，别只把材料投到伤害上。",
                "备青铜锭×3。现有织锦胸甲加这3块青铜可升级青铜胸甲；已有更好防具就不必降级。下方旧防具图鉴给完整升级链，本任务只检测这批材料。",count=3,xp=15),
            11: node(base+11,"会战底牌 · 一枚金苹果","item","minecraft:golden_apple",
                "给叛将会战留一份应急恢复，而不是为了任务吃掉。",
                "苹果放工作台中心、周围8格金锭制作普通金苹果。持有即可完成。开战前确认饥饿与生命状态，低血时先离开预警，再找机会恢复。",xp=15),
        }
    if key == "sword":
        return {
            6: node(base+6,"练步装束 · 一双轻靴","item","minecraft:leather_boots",
                "给练习场准备低成本装备，先练冷却节奏与走位。",
                "四块皮革制作皮革靴子；只是战备持有目标，不检测穿戴，也不会凭空提供闪避或疾风。实战可以继续穿更强防具，不要求脱装。",xp=10),
            7: node(base+7,"辨影出剑 · 应对刺客","kill","dynasty:assassin",
                "练习识别近身威胁；切目标保命比硬续连段更重要。",contract["field"]+" 主世界夜间或天朝探索寻找刺客，亲自击败2只。此处只检测击杀；同目标三连的严格检测在招式试炼。",count=2,xp=45),
            8: node(base+8,"系佩备料 · 丝与锦","item","dynasty:silk",
                "把机动路线的后续材料留好，按需制作丝带与佩饰。",
                "备丝绸×4、织锦×2；原料来源和配方可按 R 查看。可用于现有锦衣、丝质饰品的不同配方，但不是要求把本页所有饰品做完。",count=4,items=[("dynasty:silk",4),("dynasty:brocade",2)],xp=15),
            9: node(base+9,"龙庭行走 · 留出退路","dimension","dynasty:celestial_dynasty",
                "在新地形中练习进退，不把连段当作站桩理由。",contract["dimension"]+" 地图入口与回程材料可点下方旧主线导航。实际进入天朝即可检测；狭窄房间先清路，再接战。",xp=40),
            11: node(base+11,"换位底牌 · 两枚末影珍珠","item","minecraft:ender_pearl",
                "为被包围时的换位准备选项；它不是无代价闪现。",
                "从末影人掉落或村民交易取得末影珍珠×2。投掷可换位但会受伤；先确认落点、悬崖和当前血量。这里只检测持有，不要求为了任务投掷。",count=2,xp=15),
        }
    if key == "archer":
        return {
            6: node(base+6,"箭囊装满 · 六十四支箭","item","minecraft:arrow",
                "先备弹药，再练两次满蓄，不在标记窗口里临时找箭。",
                "燧石、木棍、羽毛各1可合成4支箭；准备64支普通箭。击败骷髅也会掉落。持有检测不消耗弹药，附魔省箭不替代本次战备。",count=64,xp=15),
            7: node(base+7,"对射观察 · 四名骷髅","kill","minecraft:skeleton",
                "练习借掩体避箭、重新探身满蓄的节奏。",
                "主世界夜间或黑暗洞穴可遇到骷髅。亲自击败4只；不要求指定武器。普通骷髅可能一箭倒下，第二箭标记试炼要另找能承受两箭的高生命敌人。",count=4,xp=45),
            8: node(base+8,"自建靶场 · 两块标靶","item","minecraft:target",
                "用清楚的靶心练落点，把练射场与安全区分开。",
                "每块标靶用干草块放中心、四个正方向红石粉制作。准备2块，建议分远近摆在土墙前，避免射向家畜或村民。本任务只检测持有，不检测搭建，也不能代替活体标记试炼。",count=2,xp=20),
            9: node(base+9,"云台防坠 · 水与搭路石","item","minecraft:water_bucket",
                "九霄高台射击首先要站稳；先修护栏、留退路。",
                "准备水桶×1、圆石×64，进入九霄后用于安全落脚和护栏。这里只检测持有，不保证你已经搭好平台；水不是自动救命，仍需熟悉落点与操作。",items=[("minecraft:water_bucket",1),("minecraft:cobblestone",64)],xp=20),
            11: node(base+11,"观星寻敌 · 望远镜","item","minecraft:spyglass",
                "先看地形和目标，再选择射击位，不盲目向悬崖追击。",
                "紫水晶碎片×1和铜锭×2竖排合成望远镜。九霄的观星建筑可用探索者罗盘搜索 dynasty:star_altar；它不保证生成 Boss。先按旧主线进入九霄，再寻找建筑。持有完成，不检测观察动作。",xp=20),
        }
    return {
        6: node(base+6,"符墨备齐 · 纸与朱砂","item","dynasty:talisman_paper",
            "为符箓与阵地准备备料，别把控制理解成无限资源。",
            "备符纸×8、朱砂×2。朱砂从神庙、法阵遗迹或帝陵地宫宝箱探索取得；符纸按 R 查配方。此目标不消耗材料，也不是说敕令笔每次使用都消耗这些物品。",count=8,items=[("dynasty:talisman_paper",8),("dynasty:cinnabar",2)],xp=15),
        7: node(base+7,"俑阵练法 · 两名兵俑","kill","dynasty:terracotta_warrior",
            "练习视线内控场、拉开距离、站定蓄势。",contract["field"]+" 先经下方地府行旅进入对应维度，亲自击败2只。此处仅检测击杀；隔墙或对友军释放不会完成招式试炼。",count=2,xp=45),
        8: node(base+8,"丹法战备 · 两枚长生丹","item","dynasty:pill_longevity",
            "蓄势时不能随意移动，先为失误准备恢复选项。",
            "朱砂、糖、玉各1制作长生丹，准备2枚。使用可获得再生，但不是持续无敌；这里只检测持有，不要求吃掉。先退到安全处再恢复。",count=2,xp=20),
        9: node(base+9,"幽冥行旅 · 落脚再施法","dimension","dynasty:underworld",
            "先抵达能找到兵俑与不死始皇的维度，再选择练习场。",contract["dimension"]+" 点击旧主线入口查门与回程的完整步骤；实际进入地府即可完成。",xp=40),
        11: node(base+11,"阵地修整 · 石墙与照明","item","minecraft:cobblestone",
            "自己搭出能撤退的施法阵地，而不是原地被包围。",
            "备圆石×32、火把×16。建议留两格高出口、开阔视线和后撤通道；敕令不会穿墙生效。本任务只检测这批方块，不检测摆放，更不会自动建造法阵或提供结界。",count=32,items=[("minecraft:cobblestone",32),("minecraft:torch",16)],xp=15),
    }


def add_routes(chapters, recipes, name, contracts):
    """contracts is supplied by the equipment content generator (no invented mechanics)."""
    old = [q for c in chapters for q in c["quests"]]
    old_items = {q["target"]:q for q in old if q["kind"]=="item"}
    boss_guides = {q["target"]:q for q in old if q["target"].startswith("guide:")}
    for index,(key, spec) in enumerate(ROUTES.items()):
        contract = contracts[key]
        base, weapon = spec["base"], "dynasty:" + spec["weapon"]
        assert weapon in recipes, "Build weapon has no actual recipe: " + weapon
        # Select one complete, explicitly identified recipe; never AND alternative recipes.
        recipe = recipes[weapon][0]
        ingredients = list(recipe["ingredients"].items())
        assert all(not k.startswith("#") and " / " not in k for k,_ in ingredients), "Build material task needs resolved direct ingredients"
        prep = "、".join(f"{name(k)}×{n}" for k,n in ingredients)
        branches=themed_branches(key,base,contract)
        rows = [
            node(base, spec["title"] + " · 先读招式", "checkmark", "guide:build_"+key,
                 spec["slogan"] + "。这是可选路线，选一条练熟就好，不要求四派全做。",
                 contract["intro"] + " 阅读勾选只表示看过；真正的操作检测在后面的『招式试炼』。"),
            node(base+1, "备料 · 第一件流派兵器", "item", ingredients[0][0],
                 "先准备一条真实配方的材料，避免边做边猜还缺什么。",
                 f"本页采用配方 {recipe['id']}：{prep}。同时放在背包等待检测，再制作武器；不会收走材料。",
                 count=ingredients[0][1], items=ingredients, xp=15),
            node(base+2, "成器 · " + name(weapon), "item", weapon,
                 "获得本流派的核心操作载体。", contract["weapon"] + " 合成后先放在背包完成检测。", xp=25),
            node(base+3, "配饰一 · " + name("dynasty:"+spec["trinkets"][0]), "item", "dynasty:"+spec["trinkets"][0],
                 "第一件专属配饰；可按自己的材料进度制作。", contract["trinkets"][0] + " 此节点只检测持有，效果需要在 Curios 实际佩戴。", xp=20),
            node(base+4, "配饰二 · " + name("dynasty:"+spec["trinkets"][1]), "item", "dynasty:"+spec["trinkets"][1],
                 "第二件配饰提供另一项补强，不是打 Boss 的强制门槛。", contract["trinkets"][1] + " 此节点只检测持有，效果需要实际佩戴。", xp=20),
            node(base+5, "招式试炼 · " + contract["trial_title"], "advancement", contract["advancement"],
                 "亲自触发流派机制，让装备效果从文字变成操作。", contract["trial"] + " 由服务器授予成就后自动完成，不是手动勾选。", xp=80),
            branches[6],branches[7],branches[8],branches[9],
            node(base+10, "可选会战 · " + name("dynasty:"+spec["boss"]), "kill", "dynasty:"+spec["boss"],
                 "检验走位与恢复，不是新的主线通关条件。", contract["boss"] + " 亲自击败一次即可；该目标不检测指定武器，不要求反复刷同一 Boss。", xp=100),
            branches[11],
        ]
        growth = ((1, "入门"), (3, "精进"), (6, "登堂"), (10, "宗师"))
        route_methods = {
            "guard": "镇岳刀或佩戴镇关镜／虎贲护腕后的其他剑，满蓄命中敌对生物。镇关镜让护甲韧性转化为额外伤害，虎贲护腕再增加12%；守住之后也能反击。",
            "sword": "流云剑或佩戴连城穗／踏云佩后的其他剑，满蓄命中敌对生物。连城穗常驻增加16%伤害，踏云佩移动攻击再增加12%；流云剑仍保留独有三连。",
            "archer": "逐星弓满蓄暴击箭，或佩戴观星佩／鸣弦戒后用其他弓射出的满蓄暴击箭命中敌对生物。观星佩对发光目标额外增加25%伤害，鸣弦戒再增加12%；不用对准宠物练级。",
            "talisman": "敕令笔或佩戴司天印／定风绢后的其他剑，满蓄命中敌对生物。司天印对缓慢目标额外增加25%伤害，定风绢站定攻击再增加15%；敕令控场是这条路线的强项。",
        }
        for rank, label in growth:
            offset = 0x20 + rank
            rows.append(node(base+offset, f"{label} · {spec['title']} {rank}阶", "advancement",
                f"dynasty:school_{key}_rank_{rank}",
                "这是会保存的流派熟练度，不会因换武器、换流派或死亡清零；每阶提高该路线伤害。",
                route_methods[key] + " 击中较高生命值的敌人获得更多练习点。下一阶需求随阶数平方增长；本节点由服务器真实授予成就，不是阅读勾选。",
                xp=30+rank*15))
        dependencies = {1:[0],2:[1],3:[2],4:[2],5:[2],6:[0],7:[5],8:[0],9:[0],10:[7],11:[0]}
        if key=="archer": dependencies.update({7:[6],9:[8]})
        if key=="talisman": dependencies.update({7:[5,9],9:[11]})
        growth_indices = [12, 13, 14, 15]
        for i,q in enumerate(rows):
            q["route"] = key
            if i in growth_indices:
                q["deps"] = [rows[5]["id"]] if i == 12 else [rows[i-1]["id"]]
                q["shape"] = "diamond"
                q["size"] = 1.2
                icon_item = (spec["weapon"], spec["trinkets"][0], spec["trinkets"][1], spec["graduate"])[i-12]
                q["icon"] = f'{{ id: "dynasty:{icon_item}" }}'
                q["description"] += ["", "&6&l成长规则&r",
                    "每次有效命中获得练习点，目标生命上限越高、练习点越多；1阶约需8点，之后需求递增。伤害倍率随阶数增长，不消耗熟练度。"]
            else:
                q["deps"] = [code(1,base+d) for d in dependencies.get(i,[])]
            if i in (0,2,5,10):
                q["shape"] = "diamond" if i != 0 else "gear"
                q["size"] = 1.15
            add_recipe(q, recipes, name)
            if i == 10:
                q["description"].insert(0,jump("查看 Boss 地点、预警与召唤",boss_guides["guide:"+spec["boss"]]["id"]))
            q["description"] += ["", "&a&l完成后去哪&r",
                "优先完成『成器 → 招式试炼』；本页侧枝是这套打法的战备与实战选项，不必全清。想换流派随时回总览，主线无需等待本页。"]
        links = []
        for offset,(field,label) in enumerate((("armor","旧装备参考 · 防具"),("backup","旧饰品参考 · 补短板"),("graduate","长远目标 · 不必现在做"))):
            target = old_items["dynasty:"+spec[field]]
            links.append({"id":code(6,base+offset),"linked_quest":target["id"],"title":label,
                          "shape":"square","size":1.0,"target":target["target"]})
        alternatives = {"guard":("tang_dao","qinglong_dao"), "sword":("tang_dao","longyuan_sword"),
                        "archer":("chang_gong","dragon_bow"), "talisman":("tang_dao","tianzi_sword")}
        for offset,item in enumerate(alternatives[key],start=3):
            target = old_items["dynasty:"+item]
            links.append({"id":code(6,base+offset),"linked_quest":target["id"],
                          "title":"旧兵器参考 · "+name(target["target"]),
                          "shape":"square","size":1.0,"target":target["target"]})
        # Reuse the existing navigation/return quest instead of four fresh compass tasks.
        travel=next(q for q in old if q["target"]==({"guard":"explorerscompass:explorerscompass",
            "sword":"dynasty:jade_portal","archer":"dynasty:cloud_portal","talisman":"dynasty:underworld_portal"}[key])
            or (key=="guard" and q["id"]==code(1,0x1000b)))
        for q in rows:
            q["description"].append(jump("旧主线导航 · 罗盘 / 维度 / 回程",travel["id"]))
        from quest_growth import refine_route
        refine_route(rows,key,spec,recipes,name)
        # These were duplicate reference icons, not quests: removing the links does
        # not delete the original catalog quests or their saved completion/rewards.
        links=[]
        chapters.append({"file":"dynasty_build_"+key,"id":code(4,spec["chapter"]),"title":spec["title"] + " · " + spec["slogan"],
            "goal":"杀怪提升熟练度与武器等级；锻造进化保留等级。沿连线查看下一步材料和成品。",
            "group":7,"main":False,"order":index,"quests":rows,"quest_links":links,"layout":spec["style"],"route":key})


def add_home(chapters):
    byfile = {c["file"]:c for c in chapters}
    first = byfile["dynasty_story_01"]["quests"][0]
    final = next(q for q in byfile["dynasty_story_08"]["quests"] if q['target']=='dynasty:story_visit_longque_sanctuary')
    rows = [node(0x40000, "从这里看懂整本任务书", "checkmark", "guide:home",
                 "主线告诉你下一步去哪；流派让你决定怎样战斗。不是把所有页面清空才算通关。",
                 "新玩家点击『安家起步』；青铜装备与图纸就绪后可旁听任一流派。四种流派能随时切换、不锁职业。老玩家已完成的任务身份、奖励和五项加槽里程碑不变。",
                 role="guide")]
    entries = [("安家起步 · 主线 01",first["id"],"没有据点和工具：先从工作台、照明和铁剑开始。", "dynasty:dynasty_manual"),
               ("工坊已成 · 主线 02",byfile["dynasty_story_02"]["quests"][0]["id"],"有据点后：导航罗盘、图纸、青铜与饰品佩戴。", "dynasty:blueprint"),
               ("维度探索 · 主线 04",byfile["dynasty_story_04"]["quests"][0]["id"],"已平叛、知道回程方法：按主线探索天朝、幽冥、九霄、龙宫。", "dynasty:jade_portal"),
               ("问鼎之后 · 龙阙终章",final["id"],"已打败龙帝：深入龙阙，转入第 09 章四象镇渊。配装可以自选，主线并未结束。", "dynasty:tianzi_sword")]
    cards=[]
    for i,(title,target,how,icon) in enumerate(entries):
        cards.append({"asset":"card_stage_"+str(i),"target":target,"x":-5.0,"y":-3.0+i*3,"hover":[title,how]})
        rows[0]["description"] += [jump(title,target),how]
    for i,(key,spec) in enumerate(ROUTES.items()):
        cards.append({"asset":"card_"+key,"target":code(4,spec["chapter"]),"x":5.0,"y":-3.0+i*3,"hover":[spec["title"],spec["slogan"],"点击选择，自由切换，不阻塞主线"]})
        rows[0]["description"].append(jump("流派 · "+spec["title"],code(1,spec["base"])))
    home={"file":"dynasty_home","id":code(4,0x500),"title":"王朝 · 山河总览","goal":"先按进度找主线，再选一条喜欢的战斗路线；点击题签或任务说明中的蓝字跳转。",
          "group":6,"main":False,"order":0,"quests":rows,"layout":"home","home_cards":cards}
    for i,q in enumerate(rows):
        q.update(x=0.0, y=-5.8,
                 size=1.25 if i==0 else 1.05,shape="gear" if i==0 else "square")
    chapters.append(home)
