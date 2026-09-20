"""Native FTB 2001.4.22 JSON text CHANGE_PAGE links, not commands or web URLs.

Verified locally: TextUtils.parseRawText -> Component.Serializer;
ViewQuestPanel.QuestDescriptionField.handleCustomClickEvent -> parseHexId -> QuestScreen.open.
IDs are explicit and independent of chapter order. Guide pages never gate progression.
"""
import json

GUIDES = {
    "dragon_emperor": (0x20000, "龙帝", "dragon_emperor_seal", "slay_dragon_emperor",
        "天朝·龙庭。制作天朝传送门，放下并右键进入；在该维度探索寻找自然生成的龙帝。不是主世界普通宫殿必刷，也没有固定坐标。",
        "先备高阶成套防具、实际佩戴的饰品、恢复品和归乡符。别为挑战龙帝先要求自己做出依赖龙帝玉玺的毕业装备。",
        "平时躲龙焰和地面预警，别贴着硬吃范围攻击。生命降到 70% 时起龙鳞护盾，打满 12 下破防后抓输出窗口；35% 时进入终阶段，护盾要 10 下。看到圈先离开，注意清理援兵，Boss 会吸取附近小弟回血。"),
    "rebel_general": (0x20001, "叛将", "rebel_head", None,
        "主世界有稀有自然生成，地府和东海龙宫也有生成配置。首次按主线优先在主世界探索寻找；不是每个兵营都保证刷新。",
        "先升级武器并穿好防具，备恢复品。可以用虎符召集友军，但自己参与攻击，避免没有击杀判定。",
        "冲锋、投矛时侧移，先处理附近叛军。生命低于 33% 时进入死战，护盾需 10 下破防，随后利用破绽输出；别站在预警圈里换血。"),
    "eunuch_mastermind": (0x20002, "宦官首脑", "eunuch_token", None,
        "天朝·龙庭的自然生成精英。先进入天朝，再探索寻找；不要按旧说明在主世界宫殿一直等。",
        "准备恢复品和净化负面状态的手段，留出后撤空间，避免被援兵堵在走廊。",
        "先清刺客等援兵，躲开毒雾和地面预警，受负面效果影响时及时调整位置。生命低于 25% 时起阴毒护盾，打满 8 下破防后再集中输出。"),
    "undead_first_emperor": (0x20003, "不死始皇", "emperor_bone", "slay_emperor",
        "地府幽冥有自然生成配置。制作地府传送门并带好第二座回程门与归乡符，进入后建立安全据点再探索；不要把普通帝陵宝箱等同于保证有 Boss。",
        "带恢复品和处理凋零等负面效果的手段。战场要能走位，避免被兵俑围住。",
        "注意地面预警与凋零伤害，先清援兵。生命低于 66% 起俑阵护盾，需要 10 下破防；33% 后进入暴走，护盾需要 8 下。破盾后抓输出窗口，别站原地硬扛领域。"),
    "nine_heaven_general": (0x20004, "九霄天将", "sky_token", "slay_sky_general",
        "九霄天界自然生成。制作九霄传送门进入，探索云台附近的可站立区域；没有保证固定刷新的坐标。",
        "准备缓降或可靠的防坠落手段、搭路方块、恢复品与归乡符。别在平台边缘开战。",
        "落雷预警出现就离开圈子，注意冲锋和援兵。60% 生命起云盾，需要 12 下破防；30% 起雷狱阶段，护盾需要 10 下。先保证不被击落，再利用破盾窗口输出。"),
    "dragon_king": (0x20005, "东海龙王", "sea_token", "slay_dragon_king",
        "东海龙宫自然生成。用龙宫传送门进入，先建立回程入口，再向外探索；不是主世界任意海洋都能找到。",
        "先准备水下呼吸药水，或实际佩戴避水珠等水下饰品，再检查防具、恢复品和归乡符。",
        "注意潮汐位移、浮空与地面预警，先清援兵，随时检查氧气。60% 生命起龙鳞护盾，需要 12 下破防；30% 起怒涛阶段，护盾需要 10 下。破盾后集中输出，但不要追到缺氧。"),
}


def jump(label, target):
    return json.dumps({"text":label,"color":"aqua","underlined":True,
        "clickEvent":{"action":"change_page","value":target},
        "hoverEvent":{"action":"show_text","contents":{"text":"点击在任务书内跳转，无需完成此页"}}},ensure_ascii=False)


def add_guides(chapters):
    quests = [q for c in chapters for q in c["quests"]]
    # The legacy "altar" task is a DIFFERENT decorative block. Do not link to it.
    altar = {"id":"1000000000020006","title":"法阵·祭坛 · 召唤教程",
        "icon":'{ id: "dynasty:ritual_altar" }',"kind":"checkmark","target":"guide:ritual_altar",
        "count":1,"tasks":'[{ id: "2000000000020006", type: "checkmark" }]',"rewards":"[]",
        "purpose":"召唤教学","how":None,"deps":[],"role":"guide","x":0.0,"y":4.8,
        "shape":"square","subtitle":"先取得信物，再召唤复战",
        "description":["&6&l制作正确的祭坛&r","玉石块×4 + 龙晶×1，无序合成法阵·祭坛。注意：装饰用的『祭坛』不是这个方块。",
            "&e&l摆放与使用&r","把法阵·祭坛放在中间；同一高度的八个相邻格里，至少四格摆玉石块。手持对应信物右键中间方块。",
            "成功召唤消耗一枚信物。附近约 80 格已有同种存活 Boss 时拒绝召唤；空手或错误信物不会召唤。",
            "首次先去 Boss 所在维度探索获得信物，不需要先完成这页。阅读无奖励，不阻塞主线。",
            "","&a&l选择 Boss 查看地点与打法&r"]}
    rows = []
    for index,(boss,(number,title,token,adv,location,prepare,tactics)) in enumerate(GUIDES.items()):
        target = f"1{number:015x}"
        main = next(q for q in quests if q["role"]=="main" and q["kind"]=="kill" and q["target"]=="dynasty:"+boss)
        token_quest = next(q for q in quests if q["kind"]=="item" and q["target"]=="dynasty:"+token)
        token_name = token_quest["title"].split(" ×")[0]
        description = [jump("← 返回主线讨伐 · "+title,main["id"]),"",
            "&6&l在哪里打 · 首次寻找&r",location,
            "怪物生成受难度、刷怪条件与附近实体数量影响。和平难度不适合找这些敌对 Boss；自然生成不是到点必刷。",
            "","&e&l开战前准备&r",prepare,"","&c&l怎么打 · 阶段与应对&r",tactics,
            "护盾和阶段机制以战斗提示为准；装备再强也先看预警。",
            "","&d&l怎么召唤 · 有信物后的复战&r",
            f"首次先找到并击败 Boss，取得「{token_name}」。已有信物也可以直接召唤；祭坛不会无中生有地发第一份信物。",
            "放置法阵·祭坛，在与祭坛同一高度的周围 3×3 环（八个相邻位置）摆至少四块玉石块。不是地板下一层。",
            f"手持「{token_name}」右键祭坛。成功召唤消耗一个信物（创造模式除外），无需红石启动。",
            "以操作玩家为中心，附近约 80 格检测范围内不能已有存活的同种 Boss；否则会拒绝召唤且不消耗信物。",
            "召唤出的 Boss 初始有约 10 秒抗性效果；先站稳、留好撤退空间。复战不会重复增加永久饰品槽。",
            jump("查看法阵·祭坛的配方与摆放",altar["id"]),
            jump("查看召唤信物 · "+token_name,token_quest["id"]),
            "","&a&l战后回到路线&r",jump("返回主线讨伐 · "+title,main["id"]),
            "此页为随时可读的攻略，无前置、无奖励；不勾选阅读也不影响任何任务。"]
        rows.append({"id":target,"title":title+" · Boss 图鉴","icon":main["icon"],
            "kind":"checkmark","target":"guide:"+boss,"count":1,
            "tasks":f'[{{ id: "2{number:015x}", type: "checkmark" }}]',"rewards":"[]",
            "purpose":"随时查询的 Boss 攻略","how":None,"deps":[],"role":"guide",
            "x":(index%3-1)*3.2,"y":(index//3-0.5)*3.2,"shape":"square",
            "subtitle":"点击导航 · 地点 / 打法 / 召唤","description":description})
        for q in quests:
            related = ((q["kind"]=="kill" and q["target"]=="dynasty:"+boss)
                or (q["kind"]=="advancement" and adv and q["target"]=="dynasty:"+adv)
                or (q["kind"]=="item" and q["target"]=="dynasty:"+token))
            if related:
                q["description"][0:0] = [jump("点击查看 · "+title+"攻略（地点 / 打法 / 召唤）",target),""]
        altar["description"].append(jump("查看可召唤 Boss · "+title,target))
    rows.append(altar)
    chapters.append({"file":"dynasty_boss_guides","id":"4000000000000400",
        "title":"Boss 图鉴 · 地点与攻略","goal":"任务内点击蓝色下划线文字即可跳转；攻略不设前置、不影响主线。",
        "group":2,"main":False,"order":len(chapters),"quests":rows})


def validate_links(chapters):
    quests = {q["id"]:q for c in chapters for q in c["quests"]}
    count = 0
    for q in quests.values():
        for line in q["description"]:
            if not line.startswith('{"'):
                continue
            component = json.loads(line)
            event = component["clickEvent"]
            assert event["action"]=="change_page", "Guide links must stay within FTB"
            assert event["value"] in quests, "Broken guide jump: "+event["value"]
            count += 1
    for number,*_ in GUIDES.values():
        guide = quests[f"1{number:015x}"]
        assert not guide["deps"] and guide["rewards"]=="[]", "Guide is gated or rewarded"
    return count
