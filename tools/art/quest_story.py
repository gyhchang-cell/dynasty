"""Editorial quest graph. Legacy save identities are immutable, layout/order are not.

Invoked only by gen_ftbquests.build(). Recipes are guidance, NOT implicit AND gates.
All chapters are constructed and validated before any generated file is replaced.
"""
import copy
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

from gen_curios import classifications, SLOT_NAMES

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "src/main/resources/data/dynasty"
OUT = ROOT / "modpack/config/ftbquests/quests"
DOC = ROOT / "docs/quests-remaster"
LEGACY = Path(__file__).with_name("quest_legacy_v1.json")
# Explicit IDs: adding/reordering/renaming a tutorial must not change save identity.
TUTORIAL_IDS = {
    "先读这一页 · 路线怎么走": 0x10000,
    "搭起工作台": 0x10001,
    "安置储物箱": 0x10002,
    "点亮第一晚": 0x10003,
    "烧炼矿物": 0x10004,
    "先学会挡伤害": 0x10005,
    "选择你的防具与饰品": 0x10006,
    "先准备水下生存": 0x10007,
    "返回龙庭，整理终战配装": 0x10008,
    "你来决定毕业流派": 0x10009,
}
LANG = json.loads((ROOT / "src/main/resources/assets/dynasty/lang/zh_cn.json").read_text())
SLOTS = classifications()
VANILLA = dict(zip(
    "crafting_table furnace chest white_bed torch shield oak_planks stick cobblestone copper_ingot iron_ingot gold_ingot coal paper ink_sac bamboo string sugar glistering_melon_slice ender_pearl redstone diamond leather feather flint gunpowder glass_bottle iron_nugget gold_nugget wheat water_bucket bow nether_star prismarine_shard blaze_powder slime_ball bone obsidian emerald lapis_lazuli black_dye dried_kelp netherite_ingot rotten_flesh spider_eye golden_apple apple egg honey_bottle book carrot potato beef porkchop chicken cod salmon kelp sand quartz amethyst_shard phantom_membrane experience_bottle magma_cream glowstone_dust nautilus_shell heart_of_the_sea".split(),
    "工作台 熔炉 箱子 白色床 火把 盾牌 橡木木板 木棍 圆石 铜锭 铁锭 金锭 煤炭 纸 墨囊 竹子 线 糖 闪烁的西瓜片 末影珍珠 红石粉 钻石 皮革 羽毛 燧石 火药 玻璃瓶 铁粒 金粒 小麦 水桶 弓 下界之星 海晶碎片 烈焰粉 黏液球 骨头 黑曜石 绿宝石 青金石 黑色染料 干海带 下界合金锭 腐肉 蜘蛛眼 金苹果 苹果 鸡蛋 蜂蜜瓶 书 胡萝卜 马铃薯 生牛肉 生猪排 生鸡肉 生鳕鱼 生鲑鱼 海带 沙子 下界石英 紫水晶碎片 幻翼膜 附魔之瓶 岩浆膏 荧石粉 鹦鹉螺壳 海洋之心".split()))
STRUCTURES = {"imperial_tomb":"帝陵地宫", "imperial_mausoleum":"帝王陵", "ritual_circle":"法阵遗迹",
    "temple":"神庙", "palace_ruin":"宫殿遗迹", "watchtower":"烽火台", "barracks":"兵营",
    "palace":"宫殿", "pagoda":"宝塔", "academy":"书院", "great_wall":"长城", "inn":"驿站"}


def name(target):
    ns, short = target.lstrip("#").split(":", 1)
    if ns == "minecraft" and short in VANILLA:
        return VANILLA[short]
    return LANG.get(f"item.{ns}.{short}", LANG.get(f"block.{ns}.{short}",
        LANG.get(f"entity.{ns}.{short}", target)))


def strings(obj):
    if isinstance(obj, dict):
        if obj.get("type") == "minecraft:item":
            yield obj.get("name", "")
        for value in obj.values():
            yield from strings(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from strings(value)


def ingredient(entry):
    if isinstance(entry, list):
        return " / ".join(ingredient(e) for e in entry)
    return entry.get("item", "#" + entry.get("tag", "unknown"))


def recipe_index():
    result = defaultdict(list)
    for path in sorted((DATA / "recipes").glob("*.json")):
        data = json.loads(path.read_text())
        output = data.get("result")
        target = output.get("item") if isinstance(output, dict) else output
        if not target:
            continue
        entries = data.get("ingredients", [])
        if "pattern" in data:
            entries = [data["key"][char] for row in data["pattern"] for char in row if char != " "]
        if "ingredient" in data:
            entries = [data["ingredient"]]
        result[target].append({"id": path.stem, "type": data["type"],
            "ingredients": dict(Counter(ingredient(e) for e in entries)),
            "output": output.get("count", 1) if isinstance(output, dict) else 1})
    return result


def loot_index():
    result = defaultdict(list)
    for path in sorted((DATA / "loot_tables").rglob("*.json")):
        kind = path.parent.name
        location = (name("dynasty:" + path.stem) if kind in ("entities", "blocks")
                    else STRUCTURES.get(path.stem, path.stem))
        for item in set(strings(json.loads(path.read_text()))):
            result[item].append((kind, location))
    # Some first-kill tokens are event drops, not JSON loot entries. Keep their
    # source auditable against the actual switch rather than inventing recipes.
    event = (ROOT / "src/main/java/com/dynasty/DynastyBossDrops.java").read_text()
    for entity, body in re.findall(r'case "([a-z_]+)" -> (.*?)(?=\n\s*case |\n\s*default)', event, re.S):
        for constant in re.findall(r'drop\(event, Dynasty\w+\.([A-Z_]+),', body):
            result["dynasty:"+constant.lower()].append(("entities",name("dynasty:"+entity)))
    return result


# Text below is hand-authored from local behavior, recipes, loot and biome modifiers.
HINTS = {
 "mu_mao":"两根木棍加一块橡木木板合成；当前配方指定橡木，不是任意木板。夜里先避开王朝精英怪。",
 "jade":"铁镐开采主世界地下玉矿；先留一部分玉做饰品，再把多余的九块玉压成玉石块。",
 "cinnabar":"当前没有可挖的朱砂矿！探索神庙、法阵遗迹、帝陵地宫的宝箱取得，箱子有概率出货，不保证每箱都有。",
 "bamboo_slip":"去丛林找竹子，线可由蜘蛛掉落。竹简用于兵器图纸，不是一次性的任务交付品。",
 "blueprint":"青铜期装备的关键材料。提前备好纸、徽墨和竹简；先做一张，再按选定装备路线补数量。",
 "bronze_ingot":"新增基础冶材配方：铜锭×3 + 铁锭×1 → 青铜锭×4；不需要找不存在的锡矿。",
 "sword_bronze":"这里演示一次完整升级：旧铁剑 + 青铜锭 + 图纸。之后可以在兵器路线中选弓、刀、剑，不必把所有武器都造一遍。",
 "jade_pendant":"放入 Curios 的项链槽或万能槽才生效；放背包不生效。需要的丝绸可以查它的配方，不要求先刷某个 Boss。",
 "exam_paper":"纸 + 墨囊，一次合成一份。拿在手中右键，选择答案；答对才会完成下一项科举里程碑。",
 "tiger_tally":"右键打开调兵界面，选择阵型与人数并实际召出部队。兵力条件看界面提示；潜行右键只是威慑，不算列阵。不要攻击自己的军队。",
 "return_talisman":"用符纸 + 末影珍珠制作；右键消耗一张，回主世界出生点附近的安全落脚位置，并清除负面效果。不是回床。出发前至少备两张。",
 "dragon_crystal":"主世界 Y=-60 至 -5 的深层有龙晶矿，先用铁镐采集。任务检测龙晶，不要求精准采集矿石；帝陵宝箱和部分 Boss 也可能掉落。",
 "dragon_crystal_ore":"这是可选矿石样本收藏，普通挖掘掉龙晶；要矿石本体需精准采集。不会阻塞主线。",
 "jade_portal":"合成一次得到两座门。放下第一座并右键前往天朝；把第二座带过去，在安全位置放下作为回程门。对面不会自动生成门。",
 "underworld_portal":"一次合成两座，右键方块往返地府。带第二座门、归乡符、照明和搭路方块，先建立安全据点再探索。",
 "cloud_portal":"凤凰羽来自凤凰的掉落。一次得到两座门，带好回程物品与缓降手段，九霄的高差比地面更危险。",
 "dragon_gate":"龙鳞按下方掉落来源收集。进入龙宫前先准备水下呼吸药水或已获得的水下饰品；不要入水后才找材料。",
 "dragon_emperor_seal":"这是龙帝的战利品，也用于祭坛复战和高阶装备。优先留一枚，不要全投入合成。",
 "emperor_bone":"来自不死始皇、龙帝的掉落。用于下一步玄天玉和终盘兵甲；不是普通骷髅的骨头。旧任务检测两块，数量不足可用已有信物在祭坛复战。制作下一步玄天玉前先让这项完成检测。",
 "ritual_altar":"祭坛周围 3×3 环内摆四块玉石块，手持对应 Boss 信物右键召唤。信物先靠首次讨伐获得，不能把祭坛当免费初见入口。",
 "sunbow":"非合成获取：在白天亲自击败凤凰，机缘系统会授予一把射日弓，每位玩家只授予一次。保留它，后羿弓配方需要用到。",
 "gilded_mace":"非合成获取：官阶达到第 12 阶（尚书）后，朝廷自动授予一把御赐金锏。每位玩家一次；用 /dynasty stats 查看官阶。",
 "supreme_sword":"非合成获取：官阶达到第 17 阶（丞相）后，朝廷自动授予一把尚方宝剑。每位玩家一次，不要随意丢弃。",
 "seven_star_saber":"非合成获取：亲自击败五种不同的 Boss 后授予一次。可计入：叛将、宦官首脑、不死始皇、九霄天将、龙王、龙帝；重复击败同一种不增加种类数。",
}
ADV = {
 "exam_passed":"手持科举试卷右键答题，至少答对一次。不是仅获得试卷，也不要求先升到天子。",
 "army_led":"手持虎符右键，在调兵界面成功召集部队；只打开界面不算完成。",
 "entered_celestial":"亲自进入天朝·龙庭，稍等游戏检测维度。",
 "entered_underworld":"亲自进入地府幽冥。",
 "entered_jiuxiao":"亲自进入九霄天界。",
 "entered_dragon_palace":"亲自进入东海龙宫。",
 "slay_emperor":"亲自击败不死始皇后由战斗事件授予成就。",
 "slay_dragon_emperor":"亲自击败龙帝后由战斗事件授予成就。",
 "slay_sky_general":"亲自击败九霄天将后由战斗事件授予成就。",
 "slay_dragon_king":"亲自击败东海龙王后由战斗事件授予成就。",
 "qilin_friend":"拿蟠桃与麒麟互动；这是友善路线，不要求杀麒麟。",
 "met_minister":"找到大臣并右键交谈。",
 "rebellion_calmed":"叛乱值降至 20 或以下时自动检查；这不是击杀数量任务。",
}
for rank, value in {"official":1,"scholar":3,"hanlin":10,"minister":12,"grand_secretary":13,
                     "chancellor":17,"prince_regent":18,"son_of_heaven":19}.items():
    ADV["rank_" + rank] = f"官阶达到第 {value} 阶时自动检查；通过战斗、科举和探索积累功名，用 /dynasty stats 查看差多少。"
BOSS = {
 "rebel_general":"主世界稀有自然生成，也可留意兵营一带。备好整套防具与恢复品；看到冲锋预警向侧面让开，先清附近叛军。",
 "eunuch_mastermind":"进入天朝·龙庭后寻找自然生成的宦官首脑，不要在主世界宫殿等待。先清刺客等援兵，中了负面状态及时脱离，别在狭窄地形硬扛。",
 "undead_first_emperor":"探索帝陵，或在地府寻找自然生成的不死始皇。带恢复品，避开地面预警，留出能后撤的空间。",
 "nine_heaven_general":"在九霄天界寻找自然生成的天将。落雷前先移动，清理援兵后再输出，不要被击落云台。",
 "dragon_king":"在东海龙宫寻找龙王。先保障水下呼吸，再处理潮汐位移与援兵；不要为了追伤害耗尽氧气。",
 "dragon_emperor":"在天朝·龙庭寻找龙帝。先准备当前能做的高阶防具和饰品，避开龙焰与地面预警；护盾阶段先打破防，再利用输出窗口。",
}


def build_book():
    legacy = json.loads(LEGACY.read_text())
    recipes, loot = recipe_index(), loot_index()
    original = [q for c in legacy for q in c["quests"]]
    by_key = {(q["kind"], q["target"], q["count"]): q for q in original}
    used, chapters = set(), []
    milestones = json.loads((DATA / "curios_progression.json").read_text())
    milestone_ids = {v["quest_id"] for v in milestones.values()}

    def take(short, purpose, how=None, kind="item", count=None):
        matches = [q for (k,t,n),q in by_key.items() if k == kind and t == "dynasty:"+short and (count is None or n == count)]
        if len(matches) != 1:
            raise ValueError((short, kind, count, len(matches)))
        q = copy.deepcopy(matches[0])
        if q["id"] in used:
            raise ValueError("Quest reused: " + short)
        used.add(q["id"])
        q.update(purpose=purpose, how=how, deps=[], role="main")
        return q

    def new(title, purpose, how, item=None, count=1):
        i = TUTORIAL_IDS[title]
        kind = "item" if item else "checkmark"
        task = (f'{{ id: "2{i:015x}", type: "item", item: {{ id: "{item}", Count: 1b }}, count: {count}L }}'
                if item else f'{{ id: "2{i:015x}", type: "checkmark" }}')
        return {"id":f"1{i:015x}","title":title,"icon":f'{{ id: "{item or "dynasty:dynasty_manual"}" }}',
            "kind":kind,"target":item or "guide", "count":count,"tasks":"["+task+"]","rewards":"[]",
            "purpose":purpose,"how":how,"deps":[],"role":"main"}

    def chapter(title, goal, quests):
        ci = len(chapters)
        # One explicit spine, not a graph of every recipe ingredient / alternative.
        previous = chapters[-1]["quests"][-1]["id"] if chapters else None
        for index,q in enumerate(quests):
            q["deps"] = [previous] if previous else []
            previous = q["id"]
            q["display_title"] = f"{index+1:02d} · {q['title']}"
        chapters.append({"file":f"dynasty_story_{ci+1:02d}", "id":f"4{0x100+ci:015x}", "title":title,
            "goal":goal,"group":1,"quests":quests,"main":True})

    chapter("01 · 安家与第一把兵器", "终点：有安全据点，做出铁剑；不要第一天就挑战王朝 Boss。", [
        new("先读这一页 · 路线怎么走", "不用面对几百个任务猜下一步。先只看『主线旅程』。",
            "按编号和连线推进；六边形为永久加槽里程碑。支线/图鉴随时查，不需要收齐。阅读页手动勾选且没有奖励，其余任务按实际行为检测。老玩家已完成节点保留，不必重领。"),
        new("搭起工作台", "先拥有 3×3 合成空间。", "砍树做四块木板，在背包合成格摆成 2×2。", "minecraft:crafting_table"),
        new("安置储物箱", "先把备用材料存好，再出门冒险。", "八块木板在工作台围成一圈。任务只检测持有；放到据点、记录坐标。", "minecraft:chest"),
        new("点亮第一晚", "照明和退路比第一把神兵重要。", "木棍加煤炭或木炭做火把；造一个封闭小屋，条件允许就做床设置重生点。", "minecraft:torch", 8),
        new("烧炼矿物", "铜锭和铁锭是接下来升级的基础。", "八块圆石围成一圈做熔炉；用燃料烧炼粗铜、粗铁。先留一把镐的材料。", "minecraft:furnace"),
        take("mu_mao", "认识第一把王朝武器。"),
        take("shi_ge", "学会把旧武器作为下一把的材料。"),
        take("tong_dao", "用已经烧好的铜锭继续升级。"),
        take("tie_jian", "完成本章基础兵器路线；还不适合裸装打 Boss。"),
        new("先学会挡伤害", "拥有攻击手段后，再补防御和食物。", "六块木板加铁锭做盾，放副手使用。盾不是万能防御，Boss 大招仍要躲。下一章准备图纸和王朝装备。", "minecraft:shield"),
    ])
    chapter("02 · 工坊、图纸与配装", "终点：能制作青铜期装备，并知道饰品在哪里佩戴。", [
        take("bronze_ingot", "先解决青铜材料来源。"),
        take("cinnabar", "朱砂串起徽墨、图纸与符箓。先探索遗迹取得。"),
        take("bamboo_slip", "准备图纸的竹简底材。"),
        take("ink_stick", "把煤炭和朱砂制成徽墨，补齐图纸材料。"),
        take("blueprint", "真正进入装备升级阶段。"),
        take("sword_bronze", "把本章准备的材料用在一把真实武器上。"),
        take("jade", "准备玉器与未来传送门的共用材料。"),
        new("选择你的防具与饰品", "这里开始自由配装，不强迫收齐所有套装。",
            "打开『装备与配方』，选当前材料能做的一套防具；饰品优先补生存。Curios 中分类佩戴，背包内不生效。推荐查玉佩、护心镜的节点。这是阅读确认，不检测穿戴；确认后进入科举和平叛。"),
    ])
    chapter("03 · 入仕与平叛", "终点：答对科举、首次击败叛将，领取两个永久万能槽。", [
        take("exam_paper", "先制作实际用于答题的试卷。"),
        take("exam_passed", "答对一次，解锁第一项永久槽位里程碑。", kind="advancement"),
        take("tiger_tally", "战斗前先了解友军支援。"),
        take("army_led", "真正召集一次部队，认识军队操作。", kind="advancement"),
        take("rebel_general", "首次 Boss 挑战；成功后获得第二个永久万能槽。", kind="kill", count=1),
        take("rebel_head", "确认收起首战信物，以后可用于武器或复战。"),
    ])
    chapter("04 · 做好回程，再入天朝", "终点：建立天朝往返路线，领取第三个永久万能槽，再取得内廷令牌。", [
        take("talisman_paper", "先制作跨维度旅行的保底回程材料。"),
        take("return_talisman", "必须先有回程办法，再进入陌生维度。"),
        take("dragon_crystal", "先在主世界获得门的核心材料，避免误以为必须先进入天朝。"),
        take("jade_portal", "准备两座门，一座留家里，一座带到对面。"),
        take("celestial_dynasty", "放置传送门并右键，实际到达新世界。", "到达后先放回程门、记录坐标，再探索附近地形。不要急着打龙帝。", kind="dimension"),
        take("entered_celestial", "入境里程碑：获得第三个永久万能槽。", kind="advancement"),
        take("eunuch_mastermind", "入境后才挑战这里的宦官首脑，取得内廷令牌。", kind="kill", count=1),
        take("eunuch_token", "保留这份战利品，兵器路线中的龙晶剑等会用到。"),
    ])
    chapter("05 · 幽冥帝陵", "终点：击败不死始皇，取得帝骸骨和第四个永久万能槽。", [
        take("underworld_portal", "把天朝旅行经验用到第二个维度。"),
        take("underworld", "进入地府，先建立可撤退的据点。", "手持两座门和归乡符进入；从安全位置向外探索。地府危险不靠交任务消除。", kind="dimension"),
        take("entered_underworld", "记录已经抵达地府。", kind="advancement"),
        take("undead_first_emperor", "拿到帝骸骨，推进高阶装备路线。", kind="kill", count=1),
        take("slay_emperor", "斩帝里程碑：领取第四个永久万能槽。", kind="advancement"),
        take("emperor_bone", "战后先确认战利品数量，不要漏捡关键材料。"),
        take("xuantian_jade", "用已有材料制作玄天玉，为更高阶装备做准备。"),
    ])
    chapter("06 · 九霄试炼", "终点：取得天将令；先改善配装，再挑战高空 Boss。", [
        take("cloud_portal", "准备登天入口和回程入口。"),
        take("jiuxiao", "抵达九霄，先确认站脚点和撤离方向。", "右键九霄传送门进入；准备缓降、搭路方块与归乡符，别直接跳入云海。", kind="dimension"),
        take("entered_jiuxiao", "记录登临九霄。", kind="advancement"),
        take("nine_heaven_general", "检验自己的走位与配装，不是堆击杀数量。", kind="kill", count=1),
        take("slay_sky_general", "确认首次天将讨伐成就。", kind="advancement"),
        take("sky_token", "保存天将信物，可在祭坛复战或制作相关装备。"),
    ])
    chapter("07 · 东海定波", "终点：击败龙王，领取第五个永久万能槽。", [
        new("先准备水下生存", "龙宫之前先解决呼吸问题，不把缺氧当难度。",
            "准备水下呼吸药水，或你已经获取且实际佩戴生效的水下饰品；再检查护甲、食物和两张归乡符。阅读确认不代表游戏已经替你检查装备。"),
        take("dragon_gate", "准备龙宫的双向入口。"),
        take("dragon_palace", "亲自进入龙宫，先设立安全回程点。", "放置龙宫传送门并右键。确认氧气与水下呼吸效果仍有效，别直接下潜追怪。", kind="dimension"),
        take("entered_dragon_palace", "记录龙宫探索。", kind="advancement"),
        take("dragon_king", "清楚自己的续航后再挑战龙王。", kind="kill", count=1),
        take("slay_dragon_king", "完成第五项里程碑：开局一格加五格，共六个万能槽。", kind="advancement"),
        take("sea_token", "拿走龙宫玉印，完成这一条探索线路。"),
    ])
    chapter("08 · 问鼎与毕业路线", "终点：击败龙帝；毕业装备按自己的流派选择，不要求全收集。", [
        new("返回龙庭，整理终战配装", "用前几章的战利品改善装备，再打龙帝。",
            "回到天朝·龙庭。检查一整套防具、实际佩戴的饰品和恢复品；查兵器谱选择自己能做的进阶武器。任务书不会要求先做必须用龙帝掉落才能合成的毕业装备。"),
        take("dragon_emperor", "完成旅程最终讨伐。", kind="kill", count=1),
        take("slay_dragon_emperor", "记录龙帝首杀；不是要求重复再杀一次。", kind="advancement"),
        take("dragon_emperor_seal", "把终战战利品带回，开启自己的毕业配装。"),
        new("你来决定毕业流派", "主线到此收束，后续是自己的目标。",
            "近战查天子剑、青龙偃月刀；远程查后羿弓。按真实配方逐级制作，选一条就好。还可继续官阶、建设、饰品搭配和祭坛复战。它们是可选玩法，不是通关欠下的清单。"),
    ])

    # Remaining legacy quests stay addressable and keep every task/reward ID.
    # Accessories are grouped by actual Curios slots rather than a wall of 169 icons.
    catalog_titles = {"dynasty_c1":"材料与入门补充", "dynasty_c2":"百工、营造与进阶材料", "dynasty_c3":"兵器路线 · 按需选一条",
        "dynasty_c4":"护甲图鉴 · 选择一套", "dynasty_c5":"官阶与朝堂", "dynasty_c6":"军旅再挑战",
        "dynasty_c7":"天朝战利品与配装", "dynasty_c8":"幽冥战利品与配装", "dynasty_c9":"灵兽与游历",
        "dynasty_c12":"九霄战利品与配装", "dynasty_c13":"龙宫战利品与配装"}
    accessories = defaultdict(list)
    retired = []
    for c in legacy:
        rows = []
        for base in c["quests"]:
            if base["id"] in used:
                continue
            q = copy.deepcopy(base)
            q.update(deps=[],role="optional",purpose="可选补充；不要求完成本页来解锁主线。",how=None)
            short = q["target"].split(":")[-1]
            if q["kind"] == "kill" and short in {"royal_guard","imperial_soldier","jade_guard"}:
                q.update(role="legacy",purpose="旧版进度存档，不是当前推荐目标。",how="旧版曾要求击杀守军；现在保留记录与原奖励以兼容旧档，不再把它放入推荐路线。不要为了推进主线攻击友军。")
                retired.append(q)
            elif q["kind"] == "item" and short in SLOTS:
                accessories[SLOTS[short]].append(q)
            else:
                rows.append(q)
        if rows:
            chapters.append({"file":c["file"],"id":c["id"],"title":catalog_titles.get(c["file"],"补充图鉴"),
                "goal":"自由查询，无需清空；物品任务不消耗物品。制作材料见节点内配方，不作为隐形门槛。",
                "group":3 if c["file"] in {"dynasty_c3","dynasty_c4","dynasty_c2","dynasty_c1"} else 2,"quests":rows,"main":False})
    for i,(slot,slot_name) in enumerate(SLOT_NAMES.items()):
        rows = accessories[slot]
        # Preserve c10 identity for the first slot; other categories are new chapters.
        chapters.append({"file":"dynasty_c10" if i==0 else "dynasty_accessory_"+slot,
            "id":next(c["id"] for c in legacy if c["file"]=="dynasty_c10") if i==0 else f"4{0x200+i:015x}",
            "title":"饰品 · "+slot_name,"goal":"佩戴位置清楚，按需求挑选；分类槽或万能槽均可，放背包不生效。",
            "group":4,"quests":rows,"main":False})
    chapters.append({"file":"dynasty_legacy","id":"4000000000000300","title":"旧版记录 · 非推荐路线",
        "goal":"仅兼容旧存档，不连接主线，不建议为清任务攻击守军。","group":5,"quests":retired,"main":False})

    allquests = [q for c in chapters for q in c["quests"]]
    where = {q["target"]:c["title"] for c in chapters for q in c["quests"] if q["kind"]=="item"}
    for ci,c in enumerate(chapters):
        c["order"] = ci
        rows = c["quests"]
        columns = 5 if c["main"] else min(10, max(4, math.ceil(math.sqrt(len(rows)))))
        rowcount = math.ceil(len(rows)/columns)
        for index,q in enumerate(rows):
            row,col = divmod(index,columns)
            # Main uses a two/three-row serpentine, keeping arrows local.
            if c["main"] and row % 2:
                col = columns-1-col
            q["x"] = (col-(columns-1)/2)*1.8
            q["y"] = (row-(rowcount-1)/2)*2.4
            short = q["target"].split(":")[-1]
            q["shape"] = "hexagon" if q["id"] in milestone_ids else "square" if q["kind"]=="checkmark" else "circle"
            q["subtitle"] = "永久 +1 万能饰品槽" if q["id"] in milestone_ids else "主线 · 按连线前进" if c["main"] else "可选 · 不阻塞主线"
            desc = ["&6&l为什么做&r",q["purpose"],"","&e&l现在怎么做&r"]
            if q["how"]:
                desc.append(q["how"])
            elif q["kind"]=="item":
                desc.append(f"获得{name(q['target'])} ×{q['count']}，放在背包等待检测。")
                if short in HINTS:
                    desc.append(HINTS[short])
            elif q["kind"]=="kill":
                desc.extend([f"亲自击败{name(q['target'])} ×{q['count']}；只观察战斗不会计数。",
                             BOSS.get(short,"探索对应世界的自然生成区域。已完成首杀后，重复讨伐仅是可选挑战，不是推进章节的要求。")])
            elif q["kind"]=="advancement":
                desc.append(ADV.get(short,"这是旧版成就补充记录。以游戏进度界面中的实际条件为准；该补充节点不阻塞主线。"))
            if q["kind"]=="item":
                rs = recipes.get(q["target"],[])
                q["recipe_ids"] = [r["id"] for r in rs]
                if rs:
                    desc.extend(["","&b&l材料与制作&r"])
                    for r in rs:
                        parts = [f"{name(k) if ' / ' not in k else ' 或 '.join(name(v) for v in k.split(' / '))}×{v}" for k,v in r["ingredients"].items()]
                        method = "烧炼" if r["type"].endswith(("smelting","blasting","smoking")) else "合成"
                        desc.append(f"{method}：{' + '.join(parts)} → {name(q['target'])}×{r['output']}。")
                    desc.append("多条配方是任选一种，不是全部完成。悬停物品按 R 看摆法，按 U 看用途。标签材料可用哪些物品，以配方界面为准。")
                    refs = sorted({where[k] for r in rs for k in r["ingredients"] if k in where and where[k]!=c["title"]})
                    if refs:
                        desc.append("材料任务可查："+"；".join(refs)+"。这些是导航，不是额外锁定条件。")
                sources = loot.get(q["target"],[])
                if sources:
                    desc.extend(["","&a&l掉落与探索&r"])
                    for kind,loc in sources:
                        desc.append(("可能掉落：" if kind=="entities" else "探索宝箱：" if kind=="chests" else "方块掉落表：")+loc+"（留意概率与工具条件）。")
                if not rs and not sources and short not in HINTS and not q["target"].startswith("minecraft:"):
                    q["unverified_source"] = True
                    desc.append("暂未从数据配方/掉落表核实生存来源；此项仅留作收藏记录，不作为主线要求。")
                if short in SLOTS:
                    desc.extend(["","&d&l佩戴方法&r",f"{SLOT_NAMES[SLOTS[short]]}槽或万能饰品槽；必须实际佩戴，背包/副手不生效。",
                                 "先看物品提示中的效果，再按生存、输出或探索需求搭配；不要求把同类饰品全做出来。"])
                desc.append("&8仅检测物品，不会收走；升级会消耗旧装备，先让该任务完成检测再合成下一件。")
            if q["id"] in milestone_ids:
                desc.extend(["","&6&l里程碑奖励&r","永久 +1 万能饰品槽。原任务与奖励 ID 保留，旧档已领取不会重复增加。"])
            if c["main"]:
                nxt = rows[index+1]["title"] if index+1<len(rows) else chapters[ci+1]["title"] if ci<7 else "自由选择毕业装备、营造或复战"
                desc.extend(["","&a&l完成后去哪&r", "下一步："+nxt+"。"])
            else:
                desc.extend(["","&a&l完成后去哪&r","回到『主线旅程』继续未完成节点，或留在此页选择真正需要的装备。无需清空本页。"])
            q["description"] = desc
    from boss_quest_guides import add_guides
    add_guides(chapters)
    validate(chapters, original)
    return chapters


def validate(chapters, original=None):
    from boss_quest_guides import validate_links
    validate_links(chapters)
    original = original if original is not None else [q for c in json.loads(LEGACY.read_text()) for q in c["quests"]]
    allq = [q for c in chapters for q in c["quests"]]
    byid = {q["id"]:q for q in allq}
    assert len(byid)==len(allq), "Duplicate quest ID"
    for old in original:
        q = byid[old["id"]]
        assert q["tasks"]==old["tasks"] and q["rewards"]==old["rewards"], "Save contract changed: "+old["id"]
    main = [q for c in chapters if c["main"] for q in c["quests"]]
    mainids = {q["id"] for q in main}
    assert not main[0]["deps"], "No accessible root"
    for i,q in enumerate(main):
        assert q["deps"]==([] if i==0 else [main[i-1]["id"]]), "Broken main spine"
        assert not q.get("unverified_source"), "Unobtainable main target: "+q["target"]
        assert all(d in mainids for d in q["deps"]), "Catalog gates main quest"
        assert not (q["kind"]=="kill" and q["target"] in {"dynasty:royal_guard","dynasty:imperial_soldier","dynasty:jade_guard"}), "Friendly kill gate"
    for q in allq:
        assert all(d in byid for d in q["deps"]), "Dangling dependency"
        if q["role"]!="main":
            assert not q["deps"], "Optional content is gated"
        if q["kind"]=="checkmark":
            assert q["rewards"]=="[]", "Reading page must not farm rewards"
    identities = [c["id"] for c in chapters] + list(byid)
    identities += [i for q in allq for i in re.findall(r'\{ id: "([0-9a-f]{16})", type:',q["tasks"]+q["rewards"])]
    assert len(identities)==len(set(identities)), "Duplicate object IDs"
    assert all(0<int(i,16)<0x8000000000000000 for i in identities), "Invalid signed long ID"


def encode(chapter):
    quote = lambda s: json.dumps(s,ensure_ascii=False)
    blocks = []
    for q in chapter["quests"]:
        lines = ["\t\t{", f'\t\t\tid: "{q["id"]}"', '\t\t\ttitle: '+quote(q.get("display_title",q["title"])),
            '\t\t\tsubtitle: '+quote(q["subtitle"]), f'\t\t\tshape: "{q["shape"]}"',
            '\t\t\tsize: 1.0d',f'\t\t\tx: {q["x"]:.2f}d',f'\t\t\ty: {q["y"]:.2f}d',
            '\t\t\ticon: '+q["icon"], '\t\t\tdescription: '+quote(q["description"]),
            '\t\t\ttasks: '+q["tasks"], '\t\t\trewards: '+q["rewards"]]
        if q["deps"]:
            lines.append('\t\t\tdependencies: '+quote(q["deps"]))
        lines.append('\t\t}')
        blocks.append('\n'.join(lines))
    return ('{\n\tdefault_hide_dependency_lines: false\n\tdefault_quest_shape: ""\n'
        f'\tfilename: "{chapter["file"]}"\n\tgroup: "5{chapter["group"]:015x}"\n'
        f'\ticon: {chapter["quests"][0]["icon"]}\n\tid: "{chapter["id"]}"\n'
        f'\torder_index: {chapter["order"]}\n\tquest_links: [ ]\n\tquests: [\n'+',\n'.join(blocks)+'\n\t]\n'
        '\tsubtitle: '+quote([chapter["goal"]])+'\n\ttitle: '+quote(chapter["title"])+'\n}\n')


def build(defaults):
    chapters = build_book()
    files = {c["file"]+".snbt":encode(c) for c in chapters}
    previous = {p.name for p in (OUT/"chapters").glob("*.snbt")}
    # Do not remove somebody else's chapter. All known legacy chapter filenames survive.
    unknown = previous - set(files)
    assert not unknown, "Unexpected existing chapters; inspect before migration: "+str(unknown)
    for filename,text in files.items():
        (OUT/"chapters"/filename).write_text(text)
    groups = ["&6&l主线旅程 · 从这里开始","&2&l支线探索 · 自由选择","&b&l装备与配方 · 按需查询",
              "&d&l饰品搭配 · 按槽位查询","&8旧版记录 · 非推荐"]
    (OUT/"chapter_groups.snbt").write_text('{\n\tchapter_groups: [\n'+ '\n'.join(
        f'\t\t{{ id: "5{i+1:015x}", title: "{t}" }}' for i,t in enumerate(groups))+'\n\t]\n}\n')
    (OUT/"data.snbt").write_text(defaults)
    DOC.mkdir(parents=True,exist_ok=True)
    (DOC/"book.json").write_text(json.dumps(chapters,ensure_ascii=False,indent=2)+'\n')
    unresolved = [q["target"] for c in chapters for q in c["quests"] if q.get("unverified_source")]
    (DOC/"source-audit.json").write_text(json.dumps({"optional_unverified":unresolved},ensure_ascii=False,indent=2)+'\n')
    print(f'Quest remaster: {len(chapters)} chapters / {sum(len(c["quests"]) for c in chapters)} nodes; 488 legacy IDs preserved; {len(unresolved)} optional sources need follow-up.')


if __name__ == "__main__":
    raise SystemExit("Run gen_ftbquests.py, the single quest generation entry point.")
