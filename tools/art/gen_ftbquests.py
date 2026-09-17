"""把王朝的完整成长线做成 FTB Quests 任务书（11 章，约 300 条，环环相扣）。

输出：
  modpack/config/ftbquests/quests/data.snbt              （全局默认：物品不收取）
  modpack/config/ftbquests/quests/chapters/dynasty_c1..c11.snbt

规则：
  * 每章内部按顺序串成一条链（前一条没完成，后面的锁着）；
    需要「同时满足多个前置」的地方用 opts["extra"] 加额外前置（FTB 原生 dependencies，默认要求全部完成）。
  * 任务判定全部用系统原生类型：item / kill / dimension / advancement。
  * 武器、护甲的说明里会写明「配方需要先做出上一级」，做成一条升级长链。
  * 奖励 = 物品 + 经验；另外每条任务都给功名（`/dynasty merit N`），
    功名越高官阶越高 → 属性加成 + 更多饰品槽。

运行：python3 tools/art/gen_ftbquests.py
"""
import glob
import heapq
import json
import math
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT, "modpack", "config", "ftbquests", "quests")
CH_DIR = os.path.join(OUT_DIR, "chapters")
LANG = os.path.join(ROOT, "src/main/resources/assets/dynasty/lang/zh_cn.json")

# 升级链：item → 它配方里需要的上一级物品（写进任务说明，做成「慢慢升级」的体验）
UPGRADE = {
    "shi_ge": "mu_mao", "tong_dao": "shi_ge", "tie_jian": "tong_dao",
    "sword_bronze": "tie_jian", "tang_dao": "sword_bronze", "huan_shou_dao": "tang_dao",
    "chang_gong": "lie_gong", "chang_qiang": "huan_shou_dao", "yu_di": "chang_qiang",
    "sword_silver": "yu_di", "sword_jade": "sword_silver", "juque_sword": "sword_jade",
    "pojun_axe": "juque_sword", "dragon_bow": "chang_gong",
    # 弓·速射支线：长弓 → 神臂弓 → 落雁弓 → 天狼弓
    # Bow (rapid-fire branch): chang_gong -> shenbi -> luoyan -> tianlang
    "shenbi_bow": "chang_gong", "luoyan_bow": "shenbi_bow", "tianlang_bow": "luoyan_bow",
    "sword_dragon_crystal": "juque_sword", "halberd_fangtian": "pojun_axe",
    "xuantian_axe": "pojun_axe", "tianzi_sword": "halberd_fangtian",
    "pickaxe_jade": "jade", "pickaxe_dragon_crystal": "pickaxe_jade",
    "sea_trident": "sword_dragon_crystal",
    "zhanma_dao": "huan_shou_dao",
    "dragon_slayer": "sword_dragon_crystal",
    "general_helmet": "cloth_helmet", "general_chestplate": "cloth_chestplate",
    "general_leggings": "cloth_leggings", "general_boots": "cloth_boots",
    "jade_helmet": "general_helmet", "jade_chestplate": "general_chestplate",
    "jade_leggings": "general_leggings", "jade_boots": "general_boots",
    "dragon_scale_helmet": "jade_helmet", "dragon_scale_chestplate": "jade_chestplate",
    "dragon_scale_leggings": "jade_leggings", "dragon_scale_boots": "jade_boots",
    "xuantian_helmet": "dragon_scale_helmet", "xuantian_chestplate": "dragon_scale_chestplate",
    "xuantian_leggings": "dragon_scale_leggings", "xuantian_boots": "dragon_scale_boots",
    "sea_silk_helmet": "dragon_scale_helmet", "sea_silk_chestplate": "dragon_scale_chestplate",
    "sea_silk_leggings": "dragon_scale_leggings", "sea_silk_boots": "dragon_scale_boots",
    "dark_iron_helmet": "sea_silk_helmet", "dark_iron_chestplate": "sea_silk_chestplate",
    "dark_iron_leggings": "sea_silk_leggings", "dark_iron_boots": "sea_silk_boots",
}

# 贵重程度（决定奖励与功名多少）：1 普通 → 5 终盘
TIER = {
    "dragon_crystal": 5, "xuantian_jade": 5, "dragon_emperor_seal": 5, "emperor_bone": 5,
    "tianzi_sword": 5, "xuantian_axe": 5, "halberd_fangtian": 5, "dragon_throne": 5,
    "xuantian_helmet": 5, "xuantian_chestplate": 5, "xuantian_leggings": 5, "xuantian_boots": 5,
    "sword_dragon_crystal": 4, "dragon_bow": 4, "pojun_axe": 4, "juque_sword": 4,
    "shenbi_bow": 3, "luoyan_bow": 4, "tianlang_bow": 4,
    "dragon_scale": 4, "dragon_scale_helmet": 4, "dragon_scale_chestplate": 4,
    "dragon_scale_leggings": 4, "dragon_scale_boots": 4, "dragon_coin": 4, "jade_seal": 4,
    "sword_jade": 3, "sword_silver": 3, "jade_helmet": 3, "jade_chestplate": 3,
    "jade_leggings": 3, "jade_boots": 3, "refined_steel": 3, "blueprint": 3, "brocade": 3,
    "rebel_head": 3, "eunuch_token": 3, "phoenix_feather": 3, "immortal_peach": 3,
    "palace_bricks": 3, "marble_block": 3, "crimson_pillar": 3, "general_chestplate": 3,
    "gold_coin": 3, "jade_coin": 3, "silver_ingot": 3, "silk": 3, "soul_talisman": 3,
    "thunder_talisman": 3, "vajra_talisman": 3,
}

DIM = {
    "celestial_dynasty": "dynasty:celestial_dynasty",
    "underworld": "dynasty:underworld",
    "jiuxiao": "dynasty:jiuxiao",
    "dragon_palace": "dynasty:dragon_palace",
}
DIM_ICONS = {
    "dynasty:celestial_dynasty": "dynasty:jade_portal",
    "dynasty:underworld": "dynasty:return_talisman",
    "dynasty:jiuxiao": "dynasty:cloud_portal",
    "dynasty:dragon_palace": "dynasty:dragon_gate",
}

# 精简：这些目标直接不要（凑数/装饰/重复的），另外全局只保留每个目标的第一次出现
# Trim list: drop these targets entirely; every target also keeps only its first occurrence.
DROP_TARGETS = {
    # 吃食只留饺子 / 茶 / 美酒三样 / representative foods only
    "dynasty:tangyuan", "dynasty:zongzi", "dynasty:mooncake", "dynasty:niangao",
    "dynasty:osmanthus_cake", "dynasty:candied_hawthorn", "dynasty:dragon_beard_candy",
    "dynasty:longevity_noodles", "dynasty:hotpot", "dynasty:roast_duck", "dynasty:cured_meat",
    "dynasty:baijiu",
    # 装饰方块过多 / too many decorative blocks
    "dynasty:brocade", "dynasty:roof_tile", "dynasty:plaque", "dynasty:screen",
    "dynasty:festival_lantern", "dynasty:taiko_drum", "dynasty:incense_burner",
    "dynasty:bronze_block",
    # 符箓 / 药水只留主力 / main talismans and potions only
    "dynasty:wind_talisman", "dynasty:stealth_talisman", "dynasty:vajra_talisman",
    "dynasty:soul_talisman", "dynasty:dynasty_splash_potion", "dynasty:dynasty_lingering_potion",
    "dynasty:pill_focus",
    # 饰品不再精简：全部 38 件都进「十二、饰品图鉴」，按五类分开排
    # All trinkets are listed in the trinket codex now (five classes).
    # 布衣套意义不大（开局就能做）/ cloth armour is trivial
    "dynasty:cloth_helmet", "dynasty:cloth_chestplate", "dynasty:cloth_leggings",
    "dynasty:cloth_boots",
}

DIM_ICONS = {
    "dynasty:celestial_dynasty": "dynasty:jade_portal",
    "dynasty:underworld": "dynasty:return_talisman",
    "dynasty:jiuxiao": "dynasty:cloud_portal",
}

_NAMES = None


def names():
    """物品中文名（从模组 lang 里读）/ localized item names"""
    global _NAMES
    if _NAMES is None:
        raw = json.load(open(LANG, encoding="utf-8"))
        out = {}
        for prefix in ("item.dynasty.", "block.dynasty."):
            for key, value in raw.items():
                if key.startswith(prefix):
                    out[key[len(prefix):]] = value
        # 成就标题（用整键查）
        for key, value in raw.items():
            if key.startswith("advancements.dynasty."):
                out[key] = value
        # 原版物品的中文名（任务里偶尔用到）
        out.update({
            "minecraft:gold_ingot": "金锭", "minecraft:iron_ingot": "铁锭",
            "minecraft:nether_star": "下界之星", "minecraft:paper": "纸",
        })
        _NAMES = out
    return _NAMES


def display(target):
    key = target.split(":")[-1]
    return names().get(key, key)


def item_icon(target):
    return target


def kill_icon(entity):
    return "minecraft:iron_sword"


def adv_icon(adv):
    return "minecraft:knowledge_book"


def dim_icon(target):
    return DIM_ICONS.get(target, "dynasty:jade_portal")

# ---------------------------------------------------------------- 步骤简写
def I(item, count=1, **opts):
    """获得王朝物品 / obtain a Dynasty item"""
    return ("item", "dynasty:" + item, count, opts)


def K(entity, count=1, **opts):
    """击杀生物 / kill mobs"""
    return ("kill", "dynasty:" + entity, count, opts)


def D(dim, **opts):
    """进入维度 / visit a dimension"""
    return ("dimension", DIM[dim], 1, opts)


def A(adv, **opts):
    """成就 / advancement"""
    return ("advancement", "dynasty:" + adv, 1, opts)


# ---------------------------------------------------------------- 各章内容
CH1 = [
    # ---- ① 兵器启蒙线：王朝的第一把武器 ----
    I("mu_mao", 1, desc="两根木棍 + 一块木板，王朝的第一把武器。"),
    I("shi_ge", 1),
    I("tong_dao", 1),
    I("tie_jian", 1),
    I("sword_bronze", 1,
      desc="青铜剑：铁剑 + 青铜锭×3 + 兵器图纸（图纸在「二、农桑百工」里拿）。"),
    # ---- ② 冶炼与开矿线 ----
    I("bronze_ingot", 4, branch=True, desc="铜 + 锡（或原版铜锭）熔成青铜锭，王朝的起步材料。"),
    I("refined_steel", 2),
    I("pickaxe_jade", 1),
    I("jade", 4, desc="挖玉矿（y 30 以下）。"),
    I("jade_block", 1),
    I("cinnabar", 2),
    # ---- ③ 文书与蚕桑线（后面所有图纸、试卷、符箓都靠它）----
    I("bamboo_slip", 4, branch=True, desc="竹子切片晾干，写字、做图纸都要它。"),
    I("ink_stick", 2),
    I("ink_brush", 1),
    I("talisman_paper", 2),
    I("raw_silk", 4),
    I("silk", 2),
    I("dynasty_manual", 1, desc="开局就送，右键打开内置手册。"),
    # ---- ④ 货币与医药线 ----
    I("copper_coin", 8, branch=True,
      desc="铜钱是王朝最基础的货币，挖矿、翻箱子、做买卖都能得。"),
    I("jade_coin", 4),
    I("gold_coin", 4),
    I("healing_salve", 2),
    # ---- ⑤ 弓线起点：这里做出猎弓，后面「十、兵器谱」接着往下升 ----
    I("lie_gong", 1, branch=True, desc="三根木棍 + 三根线：第一把远程武器，弓线从这里开始。"),
]

CH2 = [
    # ---- ① 总纲线：图纸和图鉴，王朝所有装备的起点 ----
    I("blueprint", 1, desc="兵器图纸：王朝期之后所有武器、护甲进化都要它。"),
    I("dynasty_guide", 1, desc="王朝图鉴：右键查看全部内容索引。"),
    # ---- ② 庖厨线 ----
    I("dumpling", 4, branch=True, desc="王朝最实在的食物，先管饱。"),
    I("tea", 4),
    I("wine", 2),
    # ---- ③ 营造线（宫殿建材，龙椅要用）----
    I("marble_block", 4, branch=True, desc="汉白玉：宫殿与龙椅的主料。"),
    I("palace_bricks", 16),
    I("crimson_pillar", 4),
    I("imperial_lantern", 4),
    I("chime_bell", 1),
    I("altar", 1, desc="法阵·祭坛：拿到 Boss 信物后在这里反复召唤。"),
    # ---- ④ 符箓线 ----
    I("fire_talisman", 1, branch=True, desc="符箓分五行，战斗前贴一张。"),
    I("thunder_talisman", 1),
    I("return_talisman", 1, desc="归乡符：一次性传送回出生点，下地府前必备。"),
    # ---- ⑤ 丹药线 ----
    I("dynasty_potion", 1, branch=True, desc="王朝药水：六大效果系列，从「铁壁」到「龙威」。"),
    I("pill_longevity", 1),
    # ---- ⑥ 农桑线（第二十七轮补：让「农桑百工」名副其实）----
]

CH3 = [
    # ---- ① 刀线：唐刀 → 屠龙刀 → 青龙偃月刀 / 玄武盾刀 ----
    I("tang_dao", 1, desc="兵器谱的第一把：青铜剑同级的唐刀，攻速最快。"),
    I("huan_shou_dao", 1),
    I("zhanma_dao", 1, desc="合成：环首刀 + 精钢×3；宫殿宝箱里也能开出来。"),
    I("seven_star_saber", 1, desc="条件获得：击败 5 种不同的 Boss 后武艺大成。"),
    I("dragon_slayer", 1, desc="屠龙刀：龙晶剑 + 龙宫玉印 + 龙帝玉玺（三样都齐了才做得出来）。"),
    I("qinglong_dao", 1, desc="青龙偃月刀（刀线·第二阶）：环首刀 + 青龙鳞×2 + 精钢，攻 2600。"),
    I("xuanwu_blade", 1, desc="玄武盾刀（刀线·终点）：屠龙刀 + 玄武甲片 + 玄天玉，攻 4000。"),
    # ---- ② 剑线：官银剑 → 天子剑 → 龙渊剑 / 混元珠杖 ----
    I("sword_silver", 1, branch=True, desc="剑线的起点，官银铸剑、中庸可靠。"),
    I("sword_jade", 1),
    I("juque_sword", 1, desc="重击：命中击退并施加缓慢 II。"),
    I("sword_dragon_crystal", 1, desc="★ 需要「宦官首脑」掉落的内廷令牌，附魔值 40。"),
    I("tianzi_sword", 1, extra=["dynasty:halberd_fangtian"],
      desc="天子剑：王朝的终点武器，需要方天画戟 + 玄天玉 + 龙帝玉玺 + 帝骸骨 + 内廷令牌 + 传国玉玺。"),
    I("longyuan_sword", 1, desc="龙渊剑（剑线·第二阶）：龙晶剑 + 龙晶 + 玉印，攻 1800。"),
    I("hunyuan_staff", 1, desc="混元珠杖（剑线·终点）：天子剑 + 混元珠 + 帝骸骨，攻 5000 —— 全模组最强兵器。"),
    # ---- ③ 长柄线：长枪 → 方天画戟 → 霸王枪 / 太乙拂尘 ----
    I("chang_qiang", 1, branch=True, desc="长柄武器：攻击距离 +3。"),
    I("yu_di", 1, desc="玉笛：右键范围削弱敌人心神。"),
    I("dragon_spear", 1, desc="击败亡故始皇必掉；长柄武器，攻击距离 +3。"),
    I("halberd_fangtian", 1, extra=["dynasty:sword_dragon_crystal"],
      desc="方天画戟：破军战斧 + 龙晶剑 + 帝骸骨，横扫千军。"),
    I("bawang_spear", 1, desc="霸王枪（长柄线·第二阶）：龙胆亮银枪 + 白虎牙 + 精钢，攻 3000。"),
    I("taiyi_whisk", 1, desc="太乙拂尘（长柄线·终点）：玉笛 + 太乙玉 + 丝绸，攻 3600。"),
    # ---- ④ 斧钺线：破军战斧 → 玄天钺 → 巨灵斧 / 雷霆锤 ----
    I("pojun_axe", 1, branch=True, desc="需要击败叛将拿到「叛将首级」才能打造；破甲。"),
    I("xuantian_axe", 1, desc="玄天钺：破军战斧 + 龙晶×2 + 龙帝玉玺，攻 1400。"),
    I("juling_axe", 1, desc="巨灵斧（斧线·第二阶）：破军战斧 + 龙晶 + 精钢，攻 2200。"),
    I("leiting_hammer", 1, desc="雷霆锤（斧线·终点）：玄天钺 + 雷部令牌 + 龙晶，攻 3300。"),
    # ---- ⑤ 弓线：长弓 →（速射 / 穿透 两支）→ 后羿弓（两支在终点合体）----
    I("chang_gong", 1, branch=True,
      desc="长弓：弓系的分水岭 —— 往下一分为「速射」与「穿透」两条支线。"),
    I("shenbi_bow", 1, desc="神臂弓（支线·速射）：长弓 + 精钢×3 + 丝绸×2 + 图纸，箭矢 ×2.8 + 70。"),
    I("luoyan_bow", 1, desc="落雁弓（支线·速射）：神臂弓 + 精钢×4 + 银锭×2 + 图纸，箭矢 ×3.3 + 120。"),
    I("tianlang_bow", 1, desc="天狼弓（支线·速射）：落雁弓 + 龙晶×2 + 精钢×6，箭矢 ×3.8 + 200、穿透 1。"),
    I("dragon_bow", 1,
      desc="龙吟弓（支线·穿透）：长弓 + 龙鳞×2 + 凤凰羽 + 龙晶，箭矢 ×3.5 + 150、穿透 3。"),
    I("sunbow", 1, desc="条件获得：白天击败凤凰后领悟射日弓（箭矢 ×4.5 + 280）。"),
    I("houyi_bow", 1, desc="后羿弓（弓线·终点）：射日弓 + 天狼弓 + 凤凰羽 —— 速射与穿透两支在终点合体。"),
    # ---- ⑥ 奇兵线：只能从人身上打出来的名器 ----
    K("assassin", 4, branch=True, desc="刺客：鱼肠剑的稀有掉落来源（约 4%）。"),
    I("yuchang_dagger", 1, desc="鱼肠剑：刺客稀有掉落，攻速极快。"),
    I("qinggang_sword", 1, desc="青釭剑：击败宦官首脑必掉；帝陵宝箱也有机会开出。"),
    I("yitian_sword", 1, desc="倚天剑：击败叛将必掉。"),
    # ---- ⑦ 御赐线：官阶换来的名器（配合「三、朝堂科举」）----
    I("gilded_mace", 1, branch=True, desc="条件获得：官阶升到「尚书」（第 12 阶）时朝廷御赐。"),
    I("supreme_sword", 1, desc="尚方宝剑：官阶升到「丞相」（第 17 阶）时获赐，攻击 1550。"),
    I("zhuque_fan", 1, desc="朱雀羽扇（御赐线·终点）：尚方宝剑 + 朱雀羽 + 凤凰羽，攻 4400。"),
    # ---- ⑧ 里程碑（本卷的成就收束）----
    A("jade_sword", name="玉剑出鞘", branch=True),
    A("full_jade_armor", name="全套玉甲"),
    A("dragon_crystal", name="龙晶之光"),
    A("grand_marshal", name="兵马大元帅"),
    A("slay_emperor", name="斩帝", desc="击败亡故始皇。"),
]

# ---------------------------------------------------------------- 甲胄谱
# 两条「流派」线 + 一套终点合体甲：
#   * 竹甲流（轻甲，10 阶）—— 竹 → 皮 → 织锦 → 青铜 → 白银 → 朱砂 → 凤凰 → 麒麟 → 天将 → 龙王
#   * 将军流（重甲，6 阶）—— 将军 → 玉 → 龙鳞 → 玄天 → 鲛绡 → 玄铁（之后接「玄武→…→混元」终盘线）
#   每条流派按 4 个部位成列（同部位的升级链）；末尾「鸿蒙帝铠」把两条线的终点逐件合体。
# Armour codex: two playstyle ladders (light / heavy), each split by slot, capped by the
# graduation set that merges both ladders' final pieces.
ARMOR_LADDERS = [
    ("竹甲流",
     "轻甲流派：竹 → 皮 → 织锦 → 青铜 → 白银 → 朱砂 → 凤凰 → 麒麟 → 天将 → 龙王，"
     "抗性与生命一路看涨，终点是「龙王鳞铠」。",
     [("bamboo", "竹甲"), ("leather", "皮甲"), ("brocade", "织锦袍"), ("bronze", "青铜甲"),
      ("silver", "白银铠"), ("cinnabar", "朱砂符甲"), ("phoenix", "凤凰羽衣"),
      ("qilin", "麒麟鳞甲"), ("sky", "天将云铠"), ("draco_king", "龙王鳞铠")]),
    ("将军流",
     "重甲流派：将军 → 玉 → 龙鳞 → 玄天 → 鲛绡 → 玄铁，护甲与抗击退最高，"
     "之后接「玄武 → 朱雀 → 青龙 → 白虎 → 北斗 → 天罡 → 地煞 → 太乙 → 紫微 → 混元」终盘线。",
     [("general", "将军铠"), ("jade", "玉甲"), ("dragon_scale", "龙鳞甲"),
      ("xuantian", "玄天真龙铠"), ("sea_silk", "鲛绡甲"), ("dark_iron", "玄铁重铠")]),
]

# 毕业甲：两条流派线的终点合体（龙王鳞铠 + 混元甲 → 鸿蒙帝铠）
ARMOR_FINALE = ("鸿蒙帝铠",
                "毕业甲：龙王鳞铠 + 混元甲 逐件合成 —— 竹甲流与将军流都做到终点，才凑得出这套。")
ARMOR_TIER_NOTE = {
    "bamboo": "布衣同部位 + 竹子 + 丝绸，最便宜的过渡甲。",
    "silver": "青铜甲同部位 + 银锭，中期性价比最高的一套。",
    "sky": "麒麟鳞甲同部位 + 天将令 + 玄天玉（要先打赢九霄天将）。",
    "draco_king": "天将云铠同部位 + 龙王令 + 龙晶 + 龙鳞 —— 全模组最硬的一套。",
    "general": "布衣同部位 + 青铜锭 + 图纸，王朝的正规军甲。",
    "xuantian": "龙鳞甲同部位 + 玄天玉 + 龙晶 + 帝骸骨 + 龙帝玉玺。",
    "sea_silk": "龙鳞甲同部位 + 龙鳞×2 + 丝绸×2，水战轻甲（每件减伤 26%）。",
    "dark_iron": "鲛绡甲同部位 + 精钢×3 + 玄天玉，护甲最高的重甲（每件减伤 30%）。",
}
ARMOR_SLOTS = [("helmet", "头盔"), ("chestplate", "胸甲"), ("leggings", "护腿"), ("boots", "靴子")]
CH4 = []
for _ladder_name, _ladder_intro, _ladder in ARMOR_LADDERS:
    for _slot, _slot_name in ARMOR_SLOTS:
        for _i, (_tier, _tier_name) in enumerate(_ladder):
            _note = ARMOR_TIER_NOTE.get(_tier)
            _head = (_i == 0)
            _desc = None
            if _head:
                _parts = ["【%s·%s】" % (_ladder_name, _slot_name)]
                if _slot == "helmet":                     # 每流派的头盔列写一句流派说明
                    _parts.append(_ladder_intro)
                if _note:
                    _parts.append(_note)
                _desc = " ".join(_parts)
            CH4.append(I("%s_%s" % (_tier, _slot), 1, branch=_head, desc=_desc,
                         group=(_ladder_name if _head else None)))

# 毕业甲「鸿蒙帝铠」：单独一条线（1 列 4 件），排在两条流派线之后
for _i, (_slot, _slot_name) in enumerate(ARMOR_SLOTS):
    CH4.append(I("hongmeng_%s" % _slot, 1, branch=(_i == 0),
                 desc=("【%s·%s】%s" % (ARMOR_FINALE[0], _slot_name, ARMOR_FINALE[1])
                       if _i == 0 else None),
                 group=(ARMOR_FINALE[0] if _i == 0 else None)))

CH5 = [
    # ---- ① 文房线（本章起点：纸墨 → 试卷 → 中第）----
    I("exam_paper", 2, desc="科举试卷：右键开始答题，答对一题即入门。"),
    A("exam_passed", name="科举中第"),
    A("keju", name="科举之路", desc="把一整套卷子答完。"),
    A("rank_scholar", name="金榜题名", desc="官阶升至「进士」。"),
    # ---- ② 藏书线 ----
    # ---- ③ 官阶线：一级一级往上考（功名越高，属性与饰品槽越多）----
    A("rank_official", name="官阶初授", branch=True, desc="第一次拿到官阶，王朝从此记你的名字。"),
    A("rank_hanlin", name="翰苑清贵", desc="官阶升至翰林（第 10 阶）。"),
    A("rank_minister", name="位列部堂", desc="官阶升至尚书（第 12 阶）——朝廷御赐金锏。"),
    A("rank_grand_secretary", name="天下共主", desc="官阶升至大学士（第 13 阶）。"),
    A("rank_chancellor", name="位极人臣", desc="官阶升至丞相（第 17 阶）——获赐尚方宝剑。"),
    A("rank_prince_regent", name="摄政天下", desc="官阶升至摄政王（第 18 阶）。"),
    A("rank_son_of_heaven", name="君临天下", desc="官阶升至天子（第 20 阶），王朝的顶点。"),
    # ---- ④ 印信线：玉玺与圣旨 ----
    I("official_seal", 1, branch=True, desc="官印：身份的凭证。"),
    I("jade_seal", 1, desc="传国玉玺：天子剑、屠龙刀都要它。"),
    I("edict", 2, desc="圣旨：用来安抚民心、调动官员。"),
    # ---- ⑤ 朝堂线 ----
    A("met_minister", name="拜见大臣", branch=True, desc="找到大臣并右键交谈一次。"),
    A("dynasty_root", name="王朝开端", desc="王朝正式立起来了。"),
    # ---- ⑥ 登基线：坐一次龙椅 ----
    I("dragon_throne", 1, branch=True, desc="龙椅：坐上去你就是王朝之主。"),
    # ---- ⑦ 俸禄线 ----
    I("silver_coin", 16, branch=True, desc="俸禄：做官之后按官阶发。"),
    I("silver_ingot", 8),
]

CH6 = [
    # ---- ① 征兵线 ----
    I("tiger_tally", 1, desc="虎符：右键列阵，召唤禁军。"),
    A("army_led", name="虎符调兵", desc="用虎符列阵召唤禁军。"),
    K("royal_guard", 8, desc="禁军：王朝的正规军，平时在城里巡逻。"),
    # ---- ② 平叛线 ----
    K("rebel_soldier", 10, branch=True, desc="叛乱值高时会刷出叛军，也可以主动去剿。"),
    I("rebel_head", 1, desc="叛将首级：破军战斧的材料。"),
    K("rebel_general", 1, desc="叛将：掉「叛将首级」，倚天剑也从他那掉。"),
    K("rebel_soldier", 20, desc="反复清剿：叛乱值高时会一直刷叛军。"),
    A("rebellion_calmed", name="安抚民心", desc="把叛乱值压回安全线。"),
    # ---- ③ 内廷线（宦官与刺客）----
    K("assassin", 8, branch=True, desc="刺客会翻墙来刺杀你，鱼肠剑就从他们身上掉。"),
    K("eunuch_mastermind", 1, desc="宦官首脑：掉内廷令牌。"),
    I("eunuch_token", 1, desc="内廷令牌：龙晶剑的材料。"),
    # ---- ④ 帝陵线 ----
    K("terracotta_warrior", 3, branch=True, desc="兵俑：帝陵的守卫，成群结队。"),
    K("undead_first_emperor", 1, desc="亡故始皇：帝国陵墓的 Boss，掉帝骸骨。"),
    # ---- ⑤ 军械线 ----
    # ---- ⑥ 军需线 ----
]

CH6 += [
    # ---- ① 叛将：看预警再冲 / boss mechanics: Rebel General ----
    K("rebel_general", 1, branch=True,
      desc="叛将一阶段会「冲锋」（提前 1 秒低吼 + 粒子预警，撞上来会击飞），"
           "血量 33% 后进入「死战」：举起护盾减伤 60%，要打满 10 下才破防，"
           "破防后有 7 秒破绽（伤害 ×2.5）——集火就在这个窗口。"),
    K("rebel_general", 2, desc="再战叛将：熟悉机制后稳定刷「叛将首级」。"),
    K("rebel_soldier", 30, branch=True, desc="清剿叛军：叛乱值越高刷得越多，先断兵源再打首领。"),
    K("royal_guard", 20, desc="禁军战功：把锦衣卫练到能拉满一个方阵。"),
    # ---- ② 宦官首脑：阴毒与刺客 / Eunuch Mastermind ----
    K("eunuch_mastermind", 1, branch=True,
      desc="宦官首脑近身会瞬移脱战、丢阴毒咒术（虚弱 + 失明）与毒雾。"
           "血量 25% 进入「阴毒罩体」：护盾减伤 55%，打满 8 下破防后才有破绽。"),
    K("eunuch_mastermind", 2, desc="再战宦官首脑：内廷令牌是他的必掉物。"),
    K("assassin", 10, branch=True, desc="刺客会从背后刺杀：清理他们能少掉很多血，鱼肠剑也从他们身上掉。"),
    # ---- ③ 亡故始皇：俑军与凋零 / Undead First Emperor ----
    K("undead_first_emperor", 2, branch=True,
      desc="始皇 66% 进入「俑阵」：护盾减伤 65%，打满 10 下破防；33% 进入「暴走」，"
           "地面会出现凋零领域（预警圈内必躲），并且会抽干俑军给自己回血 —— 先清小怪再打他。"),
    K("terracotta_warrior", 20, branch=True, desc="兵俑成军：帝陵里的兵马俑会成片涌出，先扫干净再进主殿。"),
    K("imperial_soldier", 12, desc="帝国士兵是友军：列阵时他们会替你顶住叛军，刷一场大胜。"),
]

CH7 = [
    # ---- ① 入境线 ----
    I("jade_portal", 2, desc="天朝传送门：传送到天朝·龙庭的传送门。"),
    D("celestial_dynasty", desc="穿过天朝传送门进入天朝·龙庭。"),
    A("entered_celestial", name="踏入天朝"),
    # ---- ② 龙晶矿脉线 ----
    I("dragon_crystal_ore", 2, branch=True, desc="天朝地下的龙晶矿，先做龙晶镐才挖得动。"),
    I("dragon_crystal", 4, desc="龙晶：玄天系列与帝兵的核心材料。"),
    I("pickaxe_dragon_crystal", 1),
    I("dragon_scale", 8, desc="龙鳞：天朝龙族身上剥下来的。"),
    # ---- ③ 龙帝线（本章 Boss）----
    K("dragon_emperor", 1, branch=True, desc="龙帝：天朝的最高统治者，建议先做好法阵·祭坛。"),
    A("slay_dragon_emperor", name="龙帝陨落"),
    I("dragon_emperor_seal", 1, desc="龙帝玉玺：玄天钺、玄天甲都要它。"),
    I("emperor_bone", 2, desc="帝骸骨：帝兵与玄天甲的核心材料。"),
    I("xuantian_jade", 2, desc="玄天玉：天朝地下的至宝。"),
    I("dragon_coin", 4),
    # ---- ④ 龙庭营造线（契机支线）----
    I("immortal_peach", 4, desc="蟠桃：天朝特产，回血也喂神兽。"),
    # ---- ⑤ 归途线（契机支线）----
    # ---- ⑥ 契机·白玉开采线 ----
]

CH7 += [
    # ---- ④ 龙帝：三阶段机制 / Dragon Emperor mechanics ----
    K("dragon_emperor", 1, branch=True,
      desc="龙帝会丢龙息火球、近身放火焰爆发（6 格内灼烧 + 虚弱）。血量 70% 进入二阶段"
           "「龙鳞护体」：护盾减伤 70%，必须打满 12 下才破防，破防后 7 秒破绽（伤害 ×2.5）；"
           "35% 进入终阶段「焚天怒火」：地面先出预警圈、1 秒后爆开，必须走位躲开；"
           "他还会抽干禁军给自己回血 —— 先清小怪再打本体。"),
    K("dragon_emperor", 2, desc="再战龙帝：玉玺与帝骸骨是高阶装备的唯一凭据，值得反复刷。"),
    K("jade_guard", 20, branch=True, desc="玉甲卫是天朝的常规守军，成群出现：先清场再找龙帝。"),
    K("royal_guard", 30, desc="天朝禁军规模更大，打满 30 个就当练手。"),
    I("dragon_emperor_seal", 1, desc="龙帝玉玺：玄天、龙王、混元三条线的终盘条件。"),
    I("xuantian_jade", 4, branch=True, desc="玄天玉：用帝骸骨 + 龙晶 + 玉在天朝合成，终盘套的主料。"),
]

CH8 = [
    # ---- ① 入境线 ----
    D("underworld", desc="穿过地府传送门进入地府——脚下就是岩浆海，先把归乡符放进背包。"),
    A("entered_underworld", name="下探地府"),
    # ---- ② 九尾狐线 ----
    K("nine_tailed_fox", 6, branch=True, desc="地府的九尾狐，掉狐尾。"),
    I("fox_tail", 4),
    K("nine_tailed_fox", 16, desc="把狐群清干净。"),
    # ---- ③ 亡者线 ----
    K("undead_first_emperor", 2, branch=True, desc="亡故始皇在地府也会出现，反复讨伐拿帝骸骨。"),
    K("assassin", 6, desc="冥界也会混进刺客。"),
    # ---- ④ 契机·黄泉路 ----
    # ---- ⑤ 契机·幽冥灯火 ----
    # ---- ⑥ 契机·冥火线 ----
]

CH9 = [
    # ---- ① 麒麟线 ----
    I("immortal_peach", 8, desc="蟠桃：喂麒麟 / 自用回血。"),
    I("qilin_horn", 2, desc="麒麟角：做麒麟角符、麒麟鳞甲都要它。"),
    A("qilin_friend", name="祥瑞麒麟", desc="拿蟠桃喂一次麒麟。"),
    # ---- ② 契机·牧场线 ----
    # ---- ③ 凤凰线 ----
    K("phoenix", 2, branch=True, desc="凤凰：白天打败它会领悟射日弓。"),
    I("phoenix_feather", 4, desc="凤凰羽：龙吟弓、凤凰羽衣都要它。"),
    K("phoenix", 4, desc="反复猎取凤羽。"),
    # ---- ④ 年兽线 ----
    K("nian_beast", 3, branch=True, desc="年兽：春节前后会出现。"),
    K("nian_beast", 5, desc="年兽：越打越熟。"),
    A("beast_friend", name="与兽为友", desc="和神兽相处的第一步。"),
    # ---- ⑤ 灵兽驯养线（第二十七轮补）----
    # ---- ⑥ 猎获线 ----
    K("qilin", 2, branch=True, desc="麒麟：喂过蟠桃之后再来打，掉麒麟角。"),
    K("phoenix", 6, desc="凤凰：反复猎取，凤羽永远不嫌多。"),
    K("nian_beast", 8, desc="年兽：打到它怕你。"),
]

# ---------------------------------------------------------------- 饰品图鉴
# 按「用途 + 前中后期」分成 5 类，一类一条线 —— 画出来就是 5 条从左到右的链，
# 从入门佩饰一路排到传世至宝，一类比一类靠后。
# Trinket codex: five classes (early -> legendary), one horizontal line each.
TRINKET_CLASSES = [
    ("入门佩饰（前期）", "材料便宜、开局就能做，先戴起来", [
        ("jade_pendant", "玉佩：减伤 8%，开局第一件。"),
        ("jade_bi_disc", "玉璧：生命 +150。"),
        ("silk_pouch", "锦囊：水下呼吸 + 夜视，跑图最实用。"),
        ("bronze_mirror", "铜镜：每 30 秒自动净化一个负面效果。"),
        ("jade_cicada", "玉蝉：血量低于 30% 时自动获得抗性 II + 迅捷。"),
        ("moon_pendant", "月华佩：夜里给夜视 + 攻击 +10% + 攻速 +10%。"),
        ("south_pointing_compass", "司南：常驻抗性提升（永远知道家在哪个方向）。"),
        ("cinnabar_pouch", "朱砂囊：持续清除中毒 / 凋零 / 失明 / 饥饿。"),
    ]),
    ("通灵瑞兽（中期 · 神兽掉落）", "打神兽、做神兽材料得来的", [
        ("jade_tortoise", "玉龟：水战 —— 水下呼吸 + 海豚 + 抗性。"),
        ("fox_tail_charm", "狐尾符：跳跃提升 II + 移速 +5%。"),
        ("qilin_horn_charm", "麒麟角符：再生 + 攻击 +10% + 护甲 +4。"),
        ("phoenix_feather_charm", "凤羽符：缓降 + 移速 +10%。"),
        ("sun_feather", "金乌翎：白天攻击 +15% + 击退 +0.3；夜里改给抗性。"),
        ("auspicious_bell", "瑞兽铃：攻速 +10%，每 20 秒自动驱散虚弱与缓慢。"),
        ("war_horse_bell", "战马铃：骑乘时给坐骑加速 + 抗性；步战时自己 +5 护甲。"),
        ("dragon_whisker", "龙须：攻速 +15% + 击退 +0.5。"),
    ]),
    ("功名文房（中期 · 朝堂与学识）", "升官、读书人专用", [
        ("gold_seal_charm", "金印：功名 +25%，还会持续给你忠诚度。"),
        ("imperial_seal_charm", "御玺佩：功名 +40%（最高）+ 生命 +100、护甲 +4。"),
        ("merit_badge", "功牌：生命 +200、抗击退 +0.3。"),
        ("inkstone", "砚台：攻速 +12%、攻击 +6%。"),
        ("bamboo_flute", "竹笛：每 5 秒吹一曲，8 格内敌人缓慢。"),
        ("star_compass", "星盘：攻击 +12%、移速 +6%。"),
        ("cloud_brocade", "云锦囊：生命 +160、护甲 +8（中期最舒服的一件）。"),
        ("jade_crown", "玉冠：生命 +220。"),
    ]),
    ("战阵护身（中后期 · 战斗）", "上阵前换上这一排", [
        ("heart_mirror", "护心镜：护甲 +8。"),
        ("iron_waist_token", "玄铁腰牌：生命 +150、护甲 +6、抗击退 +0.2。"),
        ("war_drum_charm", "战鼓坠：力量 I，并给 12 格内的友军一起加力量。"),
        ("storm_charm", "雷纹护符：常驻抗性；雷雨天额外给力量 II + 迅捷。"),
        ("dragon_scale_charm", "龙鳞护符：护甲 +12、抗击退 +0.4。"),
        ("tiger_crest", "虎符残片：每 40 秒威压八面，让 8 格内敌人放弃锁定你。"),
        ("tiger_token", "虎符玉佩：移速 +8% + 跳跃提升。"),
        ("phoenix_ring", "凤凰指环：着火即灭火并加速；常驻火焰抗性 + 移速 +3%。"),
    ]),
    ("传世至宝（终盘 · 神物）", "一件就能改变终盘的打法", [
        ("dragon_pearl", "龙珠：攻击 +25%、抗击退 +0.3。"),
        ("dragon_bone_ring", "龙骨戒：护甲 +10、抗击退 + 攻击。"),
        ("sea_conch", "海螺：水下呼吸；水下攻击 +30%、护甲 +10。"),
        ("tomb_candle", "长明烛：夜视 + 持续清除凋零（地府必备）。"),
        ("sky_feather", "天羽：跳跃提升 II、移速 +8%。"),
        ("dragon_king_scale", "龙王逆鳞：攻击 +20%、抗击退 +0.5、护甲 +6（龙宫终极饰品）。"),
    ]),
]
# 第三十二轮：30 件新饰品按主题追加到既有的 5 类里（保持「五类五列」的布局不变，
# 新增类别会把这一章拉得过宽 —— 自检里「跨度 > 40 格」就是这么踩出来的）。
_TRINKET_EXTRA = [
    ("入门佩饰（前期）", [
        ("conch_horn", "海螺号：生命 +240、移速 +8%。"),
        ("jade_brush_holder", "玉笔筒：攻速 +12%、攻击 +6%。"),
        ("ink_slab_charm", "砚台坠：幸运 +2、生命 +160。"),
        ("scroll_case_charm", "书箱坠：攻速 +10%、幸运 +1。"),
    ]),
    ("通灵瑞兽（中期 · 神兽掉落）", [
        ("qilin_hoof_charm", "麒麟蹄：生命 +260、攻速 +8%。"),
        ("turtle_blood_charm", "龟血符：生命 +300、护甲 +16，残血自动抗性。"),
        ("fox_spirit_pendant", "狐灵佩：移速 +12%、幸运 +2。"),
        ("phoenix_wing_charm", "凤翼坠：移速 +10%、常驻缓降。"),
        ("dragon_blood_pearl", "龙血珠：生命 +360、攻击 +14%。"),
        ("immortal_crane_feather", "仙鹤羽：移速 +12%、缓降（跑图最舒服）。"),
    ]),
    ("功名文房（中期 · 朝堂与学识）", [
        ("phoenix_hairpin", "凤钗：生命 +240、幸运 +1。"),
        ("dragon_robe_sash", "龙袍玉带：护甲 +14、生命 +200。"),
        ("mandarin_rank_badge", "补子官徽：幸运 +2、生命 +180。"),
        ("imperial_pearl_earring", "东珠耳坠：生命 +200、幸运 +1。"),
        ("gilded_lotus_crown", "金莲冠：攻击 +10%、移速 +5%。"),
        ("scholar_ink_badge", "墨玉印坠：生命 +180、幸运 +1。"),
    ]),
    ("战阵护身（中后期 · 战斗）", [
        ("war_banner_charm", "战旗坠：攻击 +12%、攻速 +6%。"),
        ("iron_helmet_plume", "盔缨：护甲 +12、移速 +6%。"),
        ("pike_tassel", "枪缨：攻击 +10%、攻击距离 +1。"),
        ("drum_beater", "鼓槌：攻速 +15%、攻击 +5%。"),
        ("armor_piercer_token", "破甲符牌：攻击 +16%、击退 +0.35。"),
        ("dragon_scale_sash", "龙鳞带：护甲 +16、抗击退 +0.45。"),
    ]),
    ("传世至宝（终盘 · 神物）", [
        ("thunder_seal_charm", "雷印符：攻击 +14%、攻速 +10%。"),
        ("star_diagram_charm", "星图佩：幸运 +3、生命 +140。"),
        ("zen_bead_string", "禅珠串：生命 +220，残血自动生命恢复。"),
        ("alchemy_furnace_charm", "丹炉坠：生命 +260、常驻再生。"),
        ("pearl_net_charm", "珠网坠：生命 +200、幸运 +2。"),
        ("storm_anchor_charm", "镇海锚坠：护甲 +20、击退 +0.5。"),
        ("guqin_tassel", "琴穗：攻速 +8%、生命 +120。"),
        ("tide_compass_charm", "潮信坠：攻击距离 +2、移速 +6%。"),
    ]),
]
for _extra_cls, _extra_items in _TRINKET_EXTRA:
    for _cls_name, _cls_note, _cls_items in TRINKET_CLASSES:
        if _cls_name == _extra_cls:
            _cls_items.extend(_extra_items)

CH10 = []
for _cls_name, _cls_note, _cls_items in TRINKET_CLASSES:
    for _i, (_item, _item_desc) in enumerate(_cls_items):
        CH10.append(I(_item, 1, branch=(_i == 0),
                      desc=("【%s】%s —— 本类：%s。" % (_cls_name, _item_desc, _cls_note)
                            if _i == 0 else _item_desc)))

# 十二、饰品图鉴的第 6 类（原版材料类，第二十九轮补）：饰品工坊的材料来源
CH10 += [
]

# 终章（原 CH11）已经取消：里面的东西全是前面各章的重复，
# 被「同一目标只保留第一次出现」的规则整章删空了，所以直接删掉免得留一堆死数据。
# The old "finale" chapter was entirely made of duplicates and got emptied by the
# first-occurrence rule, so it is gone.

CH9 += [
    # ---- ① 麒麟：祥瑞之兽 ----
    K("qilin", 1, branch=True,
      desc="麒麟平时温和，受击才反击：喂一颗蟠桃能换忠诚，麒麟角与玉料都靠它。"),
    K("qilin", 3, desc="多喂几次：凑齐麒麟鳞甲与麒麟角坠的材料。"),
    # ---- ② 凤凰：涅槃火羽 ----
    K("phoenix", 1, branch=True,
      desc="凤凰会飞、会喷火，血量 50% 起「涅槃火羽」护盾（打满 8 下破防，破绽 ×2.5）；"
           "在白天击败它才能领悟射日弓。"),
    K("phoenix", 3, desc="反复挑战凤凰：凤凰羽是凤凰羽衣与龙吟弓的主料。"),
    # ---- ③ 年兽：怕红怕响 ----
    K("nian_beast", 1, branch=True,
      desc="年兽 50% 血后暴怒：护盾打满 8 下破防，破绽期才是集火窗口。"),
    K("nian_beast", 3, desc="年兽镇宅：精钢与年味道具的稳定来源。"),
    # ---- ④ 九尾狐：幻影 ----
    K("nine_tailed_fox", 1, branch=True,
      desc="九尾狐用幻影（失明）糊住视野，破防后的破绽期才有输出。"),
    K("nine_tailed_fox", 3, desc="狐尾丝线：织造与狐尾坠的材料。"),
]

CH12 = [
    # ---- ① 入境线 ----
    I("cloud_portal", 1, desc="九霄传送门：玉石块×4 + 龙晶 + 凤凰羽，右键进入九霄天界。"),
    D("jiuxiao", desc="穿过九霄传送门进入九霄天界——云海之上的天将领地。"),
    A("entered_jiuxiao", name="登临九霄"),
    # ---- ② 云兵线（本章 Boss）----
    K("archer", 10, branch=True, desc="天将召唤的云兵弓手：先清小兵再打主将。"),
    K("nine_heaven_general", 1, desc="九霄天将：会落雷、冲锋与召唤云兵，先备好归乡符与金创药。"),
    A("slay_sky_general", name="天将伏诛"),
    I("sky_token", 1, desc="天将令：拿到后可在法阵·祭坛重复召唤天将。"),
    K("nine_heaven_general", 3, desc="反复讨伐：天将令可以反复用来召唤。"),
    # ---- ③ 契机·云梯线 ----
    # ---- ④ 契机·雷池与天马 ----
    # ---- ⑤ 契机·云海线 ----
    # ---- ⑥ 空战线 ----
    K("archer", 30, branch=True, desc="云兵弓手：九霄的空中杂兵，上云台前先清干净。"),
    K("archer", 50, desc="云兵清空：让九霄的天空安静下来。"),
]

CH12 += [
    # ---- ④ 天将：云盾与雷狱 / Nine-Heaven General mechanics ----
    K("nine_heaven_general", 1, branch=True,
      desc="天将会冲锋、掷矛，血量 60% 起「云盾成形」：护盾减伤 70%，必须打满 12 下破防，"
           "破绽期伤害 ×2.5；30% 起「九天雷狱」——落雷圈先预警 1 秒再结算，站着不动必吃；"
           "他还会抽云兵回血，先清小怪。"),
    K("nine_heaven_general", 2, desc="再战天将：天将令是天将云铠的前置。"),
    K("thunder_envoy", 24, branch=True, desc="雷使成群劈雷：先清雷使，再单挑天将。"),
    I("thunder_talisman", 4, desc="雷符：抗雷与反伤，打天将前先贴一张。"),
    I("return_talisman", 2, branch=True, desc="归乡符：九霄掉下来能直接回城，别省。"),
]

CH13 = [
    # ---- ① 入境线 ----
    I("dragon_gate", 1, desc="龙宫传送门：玉石块×4 + 龙晶 + 龙鳞×2，右键往返龙宫。"),
    D("dragon_palace", desc="穿过龙宫传送门进入东海龙宫——龙宫整片泡在水里，先把避水珠戴上。"),
    A("entered_dragon_palace", name="深入龙宫"),
    I("sea_pearl", 1, branch=True,
      desc="避水珠：水下呼吸 + 海豚 + 水下攻防加成（当饰品戴，下水就有效）。"),
    # ---- ② 龙王线（本章 Boss）----
    K("dragon_king", 1, branch=True, desc="东海龙王：落雷 + 潮汐拉扯 + 虾兵蟹将，注意被拉进水里。"),
    A("slay_dragon_king", name="沧海定波"),
    I("sea_token", 1, desc="龙宫玉印：可在法阵·祭坛反复召唤龙王。"),
    I("sea_trident", 1, extra=["dynasty:sword_dragon_crystal"],
      desc="分水三叉戟：龙晶剑 + 龙宫玉印 + 龙鳞×2，水里打架更强。"),
    K("dragon_king", 3, desc="反复讨伐：玉印可以反复召唤龙王。"),
    # ---- ③ 契机·海底建材线 ----
    # ---- ④ 契机·寻宝线 ----
    # ---- ⑤ 契机·渔获线 ----
]

# (章节文件, 标题, 图标, 步骤, 入口依赖, 分组序号, 副标题)
#   入口依赖：
#     "first" = 第一章（无前置）
#     "prev"  = 接上一章末尾（主线层层递进）
#     "c1"    = 接第一章末尾（独立支线章，可以早点开始，例如装备/图鉴）
#   分组序号 = CHAPTER_GROUPS 的下标（任务书左侧栏折叠标题）
#   副标题   = 章节标题下面那行小字（像「愚者」那样给一章一句话简介）
# ================================================================================
# 第三十一轮：把「收集原版物品」的任务全部删掉，换成王朝自己的内容。
#
# 玩家反馈：
#   * 「任务收集原版东西没有意义」——木头、圆石、铁锭这些生存本来就要做；
#   * 「多拓展啊，Boss 机制啥的」——任务应该讲清楚每个 Boss 怎么打。
#
# 于是这里按「Boss 机制 / 关卡机制 / 战功阶梯 / 维度与派系」重新铺内容：
# 每条 Boss 任务都会写明它的阶段、护盾、破绽窗口和预警圈，玩家照着打就能过。
# ================================================================================
CH5 += [
    # ---- ① 官阶线：功名换来的八级台阶（成就 = 真实进度）----
    A("rank_scholar", name="入仕·书生", branch=True, desc="功名达标即可授官，官阶越高属性加成越高。"),
    A("rank_official", name="九品·官员"),
    A("rank_hanlin", name="翰林学士"),
    A("rank_minister", name="尚书"),
    A("rank_grand_secretary", name="大學士"),
    A("rank_chancellor", name="丞相"),
    A("rank_prince_regent", name="摄政王"),
    A("rank_son_of_heaven", name="天子", desc="王朝官阶的顶点：全员属性上限再抬一档。"),
    # ---- ② 科举与印信 ----
    A("exam_passed", name="金榜题名", branch=True),
    A("keju", name="科举开考"),
    A("met_minister", name="拜见大臣", desc="朝堂上的 NPC 会发功名与任务。"),
    I("official_seal", 1, branch=True, desc="官印：官阶身份的凭证，也是不少配方的条件。"),
    I("edict", 1, desc="圣旨：朝廷调令，可以召唤禁军与钦差。"),
    I("dragon_throne", 1, desc="龙椅：坐在上面可以在天朝行使天子权柄。"),
    I("south_pointing_compass", 1, desc="司南开路：指着方向找遗迹与传送门。"),
]

CH13 += [
    # ---- ④ 龙王：龙鳞与怒涛 / Dragon King mechanics ----
    K("dragon_king", 2, branch=True,
      desc="龙王三阶段：60% 血起「龙鳞护体」——护盾减伤 70%，必须打满 12 下破防，"
           "破绽期伤害 ×2.5；30% 起「怒涛」——潮汐把玩家往他身边拉，同时地面预警圈 1 秒后爆开，"
           "他还会抽干虾兵蟹将回血，所以先清小怪再打本体。"),
    K("merfolk", 24, branch=True, desc="鲛人成群游来：先清鲛人，免得多线挨打。"),
    I("jade_crown", 1, desc="玉冠：天朝官帽式的头饰，顺路收一件。"),
    I("dragon_king_scale", 1, desc="龙王逆鳞：龙宫最硬的战利品，龙王鳞铠的象征。"),
]

# ================================================================================
# 第三十一轮（续）：+10 套甲（40 件）与 +50 件饰品，按「在哪拿到就写在哪一章」铺进任务书。
# 甲胄不塞进「甲胄谱」，而是放进对应的世界章节 —— 玩家打到那一章就能看见这套甲怎么来。
# ================================================================================
CH1 += [
    K("assassin", 2, branch=True, desc="王朝各地都有刺客出没，夜里别裸奔。"),
    K("rebel_soldier", 5, desc="叛军会成小队来抢粮，先挡几波练手。"),
    K("nian_beast", 2, desc="年兽过年才出来闹，打两只正好练走位。"),
    K("terracotta_warrior", 2, desc="野外的兵俑会自己站起来，打碎它们。"),
    K("royal_guard", 4, desc="锦衣卫在城里巡逻，切磋几场。"),
    K("archer", 5, desc="弓兵会远程点你，先学会拉近距离。"),
]

CH2 += [
    # ---- 玉器（10 件）：玉料线的成品，农桑百工里最先能做出来的一批饰品 ----
    I("jade_marrow_charm", 1, branch=True, desc="玉髓佩：生命 +180、护甲 +5，最实在的一件。"),
    I("jade_ruyi", 1, desc="玉如意：幸运 +2（常驻幸运 II）。"),
    I("jade_ring", 1, desc="玉扳指：攻速 +10%、攻击距离 +1。"),
    I("jade_belt_hook", 1, desc="玉带钩：护甲 +8、抗击退 +0.3。"),
    I("jade_flying_apsara", 1, desc="玉飞天：移速 +8%、常驻缓降。"),
    I("jade_bixie", 1, desc="玉辟邪：击退 +0.4、攻击 +8%。"),
    I("jade_kylin", 1, desc="玉麒麟：生命 +220、攻击 +10%。"),
    I("jade_silkworm", 1, desc="玉蚕：生命 +120，残血时自动生命恢复。"),
    I("jade_cong", 1, desc="玉琮：护甲 +12、抗击退 +0.4。"),
    I("jade_zhang", 1, desc="玉璋：攻击 +12%、攻速 +8%。"),
]

# 玩家反馈「全是竖着排太难看了，最好有横有竖、有些从中心往外、有些分支」。
# 这里给每章指定一种排布风格（实现在 layout_rows / layout_cols / layout_fan / layout_tree）：
#   rows 横排　cols 竖排　fan 中心放射　tree 主干+树枝
CH5 += [
    # ---- 文人（10 件）：科举与书房路线的饰品 ----
    I("poem_scroll", 1, branch=True, desc="诗文卷轴：幸运 +2（常驻幸运 II）。"),
    I("seal_charm", 1, desc="印章坠：生命 +100、幸运 +1。"),
    I("go_board", 1, desc="棋盘坠：攻速 +10%。"),
    I("guqin_string", 1, desc="古琴弦：攻速 +8%。"),
    I("tea_cup", 1, desc="茶盏：生命 +200，常驻生命恢复。"),
    I("wine_gourd", 1, desc="酒葫芦：生命 +240、击退 +0.3。"),
    I("incense_sachet", 1, desc="香囊：生命 +160、常驻再生。"),
    I("folding_fan", 1, desc="折扇：移速 +6%、攻速 +8%。"),
    I("mirror_pouch", 1, desc="铜镜袋：护甲 +10、常驻抗性。"),
    I("brush_rack", 1, desc="笔架坠：攻速 +14%、攻击 +6%。"),
]

CH6 += [
    # ---- 兵器配饰（10 件）：军营线的饰品 ----
    I("saber_tassel", 1, branch=True, desc="刀穗：攻击 +7%、攻速 +5%。"),
    I("sword_tassel", 1, desc="剑穗：攻击 +6%、攻击距离 +1。"),
    I("arrow_quiver", 1, desc="箭囊：攻击 +8%、移速 +4%。"),
    I("bow_string", 1, desc="弓弦护腕：攻速 +12%、攻击 +5%。"),
    I("wrist_guard", 1, desc="护腕：护甲 +10、抗击退 +0.3。"),
    I("knee_guard", 1, desc="护膝：移速 +5%、抗击退 +0.2。"),
    I("belt_buckle", 1, desc="腰带扣：护甲 +6、生命 +120。"),
    I("scale_plate", 1, desc="甲片：护甲 +9、抗击退 +0.25。"),
    I("iron_pauldron", 1, desc="铁护肩：护甲 +14、攻击 +5%。"),
    I("horse_stirrup", 1, desc="马镫：移速 +10%（只在骑乘时生效）。"),
    # ---- 白虎铠（8→4 件：攻杀流）----
    I("baihu_helmet", 1, branch=True, desc="白虎铠：每件减伤 35%、生命 +1300，攻击 +15%、击退 +0.3。"),
    I("baihu_chestplate", 1),
    I("baihu_leggings", 1),
    I("baihu_boots", 1),
    # ---- 青龙鳞（攻守兼备）----
    I("qinglong_helmet", 1, branch=True, desc="青龙鳞：每件减伤 34%、生命 +1200，攻击 +10%。"),
    I("qinglong_chestplate", 1),
    I("qinglong_leggings", 1),
    I("qinglong_boots", 1),
]

# ---------------------------------------------------------------- 排布风格
CH7 += [
    # ---- 朱雀羽：火里来火里去 ----
    I("zhuque_helmet", 1, branch=True, desc="朱雀羽：每件减伤 30%、生命 +1000，抗火。"),
    I("zhuque_chestplate", 1),
    I("zhuque_leggings", 1),
    I("zhuque_boots", 1),
    # ---- 混元甲：毕业套（龙帝玉玺 + 帝骸骨）----
    I("hunyuan_helmet", 1, branch=True,
      desc="混元甲：每件减伤 42%、生命 +3200，四件封顶 92% —— 王朝的毕业护甲。"),
    I("hunyuan_chestplate", 1),
    I("hunyuan_leggings", 1),
    I("hunyuan_boots", 1),
]

CH8 += [
    # ---- 地府战功线 ----
    K("undead_first_emperor", 3, branch=True,
      desc="再战始皇：三阶段机制打熟了就能稳定刷帝骸骨。"),
    K("soul_soldier", 16, desc="冥卒成群从忘川爬上来，先清干净再进主殿。"),
    K("soul_soldier", 40, desc="冥卒成军：地府的野外压力主要来自它们。"),
    K("terracotta_warrior", 30, desc="帝王陵的兵马俑会一直复活，打满 30 个）。"),
    I("underworld_portal", 1, branch=True, desc="地府传送门：往返阴阳两界，别忘了带归乡符。"),
    I("deepslate_jade_ore", 4, desc="深层玉矿：地府与深层的玉脉更肥。"),
    I("jade_ore", 8, desc="玉矿：玉器与玉甲的主料，顺手挖一背包。"),
    # ---- 道家（10 件）：地府与符箓路线 ----
    I("bagua_mirror", 1, branch=True, desc="八卦镜：护甲 +14、常驻抗性 I。"),
    I("peach_sword", 1, desc="桃木剑：攻击 +16%。"),
    I("talisman_pouch", 1, desc="符纸包：幸运 +3。"),
    I("alchemy_pendant", 1, desc="炼丹坠：生命 +200、再生 I。"),
    I("golden_pill", 1, desc="金丹：生命 +400、再生 II（最贵的保命饰品）。"),
    I("cloud_pattern", 1, desc="云纹佩：移速 +12%、抗击退 +0.3。"),
    I("star_dial", 1, desc="星斗盘：攻击 +12%、攻速 +10%。"),
    I("tiangang_talisman", 1, desc="天罡符：攻击 +18%、抗击退 +0.4。"),
    I("disha_talisman", 1, desc="地煞符：护甲 +18、击退 +0.4。"),
    I("purple_qi_pearl", 1, desc="紫气珠：生命 +320、攻击 +14%。"),
    # ---- 玄武甲 / 地煞甲：地府的防御向奖励 ----
    I("xuanwu_helmet", 1, branch=True, desc="玄武甲：每件减伤 33%、生命 +1100，抗击退 +0.5。"),
    I("xuanwu_chestplate", 1),
    I("xuanwu_leggings", 1),
    I("xuanwu_boots", 1),
    I("disha_helmet", 1, branch=True, desc="地煞甲：每件减伤 38%、生命 +1900，护甲 +40、抗击退 +0.6。"),
    I("disha_chestplate", 1),
    I("disha_leggings", 1),
    I("disha_boots", 1),
]

CH9 += [
    # ---- 灵兽（10 件）：神兽线掉的材料做的饰品 ----
    I("crane_feather", 1, branch=True, desc="鹤羽：移速 +10%、常驻缓降。"),
    I("tiger_claw", 1, desc="虎爪：攻击 +12%、击退 +0.4。"),
    I("leopard_tail", 1, desc="豹尾：移速 +12%、攻速 +6%。"),
    I("deer_antler", 1, desc="鹿角：生命 +260、常驻再生。"),
    I("snake_gall", 1, desc="蛇胆：攻击 +10%（水下额外生效）。"),
    I("bear_paw", 1, desc="熊掌：生命 +300、攻击 +8%。"),
    I("turtle_shell", 1, desc="龟甲：护甲 +16、抗击退 +0.5。"),
    I("rhino_horn", 1, desc="犀角：攻击 +14%、护甲 +6。"),
    I("ivory_tusk", 1, desc="象牙：攻击距离 +2、攻击 +6%。"),
    I("hawk_eye", 1, desc="鹰眼：攻击 +10%、攻击距离 +2。"),
]

CH12 += [
    # ---- 北斗甲 / 天罡甲：九霄的星石与雷部奖励 ----
    I("beidou_helmet", 1, branch=True, desc="北斗甲：每件减伤 36%、生命 +1500，移速 +8%。"),
    I("beidou_chestplate", 1),
    I("beidou_leggings", 1),
    I("beidou_boots", 1),
    I("tiangang_helmet", 1, branch=True, desc="天罡甲：每件减伤 37%、生命 +1700，攻击 +18%。"),
    I("tiangang_chestplate", 1),
    I("tiangang_leggings", 1),
    I("tiangang_boots", 1),
]

CH13 += [
    # ---- 太乙甲 / 紫微甲：龙宫与帝星的奖励 ----
    I("taiyi_helmet", 1, branch=True, desc="太乙甲：每件减伤 39%、生命 +2200，全属性小幅提升。"),
    I("taiyi_chestplate", 1),
    I("taiyi_leggings", 1),
    I("taiyi_boots", 1),
    I("ziwei_helmet", 1, branch=True, desc="紫微甲：每件减伤 40%、生命 +2600，幸运 +3。"),
    I("ziwei_chestplate", 1),
    I("ziwei_leggings", 1),
    I("ziwei_boots", 1),
]

# ================================================================================
# 第三十二轮：7 个高阶材料 / 6 把帝兵 / 30 件饰品（食物按既有精简规则不进任务书）
# ================================================================================
CH2 += [
    # ---- 10 套甲 / 10 件兵器点名要的高阶材料（此前只出现在配方里、做不出来）----
    I("xuanwu_shell", 1, branch=True, desc="玄武壳：龙鳞×2 + 精钢×2 + 图纸 —— 玄武甲与玄武系兵器的甲片。"),
    I("qinglong_scale", 1, desc="青龙鳞：龙鳞×2 + 龙晶 + 图纸。"),
    I("baihu_fang", 1, desc="白虎牙：龙晶×2 + 精钢×2 + 图纸。"),
    I("zhuque_feather", 1, desc="朱雀羽：凤凰羽×2 + 朱砂×2 + 图纸。"),
    I("taiyi_jade", 1, desc="太乙玉：玄天玉 + 玉×2 + 图纸。"),
    I("thunder_token", 1, desc="雷部令：符纸×2 + 朱砂×2 + 图纸。"),
    I("hunyuan_pearl", 1, desc="混元珠：龙晶×2 + 龙帝玉玺 + 帝骸骨（毕业材料）。"),
]

CH3 += [
    # ---- 6 把帝兵：材料都来自上面那一批 / six weapons built from the new materials ----
    I("qilin_war_axe", 1, branch=True, desc="麒麟战斧（斧线）：麒麟角 + 精钢×2 + 图纸，攻 2000、特攻 +250。"),
    I("taiyi_sword", 1, desc="太乙法剑（剑线）：太乙玉 + 龙晶 + 图纸，攻 2300、特攻 +300。"),
    I("baihu_glaive", 1, desc="白虎戟（长柄）：白虎牙 + 精钢×2 + 图纸，攻 2600、特攻 +330（攻击距离 +3）。"),
    I("thunder_spear", 1, desc="雷霆枪（长柄）：雷部令 + 精钢×2 + 图纸，攻 2900、特攻 +360（攻击距离 +3）。"),
    I("ziwei_saber", 1, desc="紫微刀（刀线）：龙晶 + 玄天玉 + 图纸，攻 3200、特攻 +400。"),
    I("zhuque_bow", 1, desc="朱雀弓（弓线）：朱雀羽 + 凤凰羽 + 龙吟弓 + 图纸，箭矢 ×4.0 + 300、穿透 2。"),
]

CHAPTER_LAYOUT = {
    "dynasty_c1": "rows",       # 初入王朝：一条条横着看最清楚
    "dynasty_c2": "cols",       # 农桑百工：一类一列
    "dynasty_c3": "cols",       # 兵器谱：和甲胄谱一样「一类一列」，别再堆成方阵（玩家反馈乱）
    "dynasty_c4": "cols",       # 甲胄谱：一类一列
    "dynasty_c10": "cols",      # 饰品图鉴：五类五列
    "dynasty_c5": "fan",        # 朝堂科举：中心开花
    "dynasty_c6": "rows",       # 军旅平叛：横排
    "dynasty_c9": "fan",        # 神兽与帝王：中心开花
    "dynasty_c7": "fan",        # 天朝·龙庭：中心开花
    "dynasty_c8": "fan",        # 地府幽冥：中心开花
    "dynasty_c12": "rows",      # 九霄天界：横排
    "dynasty_c13": "fan",       # 东海龙宫：中心开花
}

CHAPTERS = [
    ("dynasty_c1", "一、初入王朝", "dynasty:dynasty_manual", CH1, "first", 0,
     "从一根木棍开始：先活下来，再谈王朝。"),
    ("dynasty_c2", "二、农桑百工", "dynasty:silk", CH2, "prev", 0,
     "种桑养蚕、开矿烧砖：王朝的粮仓与工坊。"),
    # ---- 装备 / 图鉴三章排在前面：这样兵器谱、甲胄谱、饰品图鉴才能**收全** ----
    #     它们不参与主线递进（mode = "c1"），主线接着「二、农桑百工」往下走。
    # The three codex chapters are listed early so they own every gear quest; they do not
    # take part in the main storyline chain.
    ("dynasty_c3", "十、兵器谱", "dynasty:sword_bronze", CH3, "c1", 2,
     "38 把兵器八条线：刀 / 剑 / 长柄 / 斧钺 / 弓（速射·穿透两支）/ 奇兵 / 御赐 / 毕业神兵。"),
    ("dynasty_c4", "十一、甲胄谱", "dynasty:general_chestplate", CH4, "c1", 2,
     "17 套主线甲胄 × 4 件（竹甲 → 龙王鳞铠）；10 套终盘甲（玄武/朱雀/青龙/白虎/北斗/天罡/地煞/太乙/紫微/混元）"
     "写在各世界章节里：在哪拿到就写在哪。"),
    ("dynasty_c10", "十二、饰品图鉴", "dynasty:heart_mirror", CH10, "c1", 2,
     "图鉴收录 38 件饰品，分五类：入门 → 通灵 → 功名 → 战阵 → 传世，只放 Curios；"
     "另有 50 件新饰品（玉器 / 兵器配饰 / 灵兽 / 文人 / 道家）按材料所在的章节铺开。"),
    # ---- 王朝主线 ----
    ("dynasty_c5", "三、朝堂科举", "dynasty:exam_paper", CH5, "prev", 0,
     "答对试卷换功名，功名换官阶、属性与饰品槽。"),
    ("dynasty_c6", "四、军旅与平叛", "dynasty:tiger_tally", CH6, "prev", 0,
     "虎符调兵、平定叛乱，把江山守住。"),
    ("dynasty_c9", "五、神兽与帝王", "dynasty:qilin_horn", CH9, "prev", 0,
     "麒麟、凤凰、年兽、九尾狐，还有龙帝与始皇。"),
    # ---- 万里山河 ----
    ("dynasty_c7", "六、天朝·龙庭", "dynasty:dragon_crystal", CH7, "prev", 1,
     "穿过天朝传送门，去龙晶与汉白玉的国度。"),
    ("dynasty_c8", "七、地府幽冥", "dynasty:return_talisman", CH8, "prev", 1,
     "地府传送门之后是忘川，脚下就是岩浆海。"),
    ("dynasty_c12", "八、九霄天界", "dynasty:cloud_portal", CH12, "prev", 1,
     "九霄传送门之上，天将把守九霄。"),
    ("dynasty_c13", "九、东海龙宫", "dynasty:dragon_gate", CH13, "prev", 1,
     "龙宫传送门入海，龙王的宝库在等你。"),
]


def load_recipes():
    """
    把数据包里的配方读成「成品 → 材料」表，用来推导任务的前置：
    要做出某件东西，必须先拿到它的材料 —— 这样任务顺序就一定是合乎逻辑的。
    Recipe table: result item -> ingredient items, used to derive quest dependencies.
    """
    out = {}
    recipe_dir = os.path.join(ROOT, "src/main/resources/data/dynasty/recipes")
    for path in glob.glob(os.path.join(recipe_dir, "*.json")):
        try:
            data = json.load(open(path, encoding="utf-8"))
        except Exception:
            continue
        result = data.get("result")
        if isinstance(result, dict):
            result_id = result.get("item")
        else:
            result_id = result if isinstance(result, str) else None
        if not result_id:
            continue
        ingredients = set()
        for entry in data.get("ingredients", []):          # 无序配方
            if isinstance(entry, dict) and entry.get("item"):
                ingredients.add(entry["item"])
        for entry in data.get("key", {}).values():          # 有序配方
            if isinstance(entry, dict) and entry.get("item"):
                ingredients.add(entry["item"])
        if ingredients:
            out[result_id] = ingredients
    return out


RECIPES = load_recipes()


def order_steps(rows):
    """
    按配方把一章里的任务排好：材料任务排在成品任务前面。
    这样「配方前置」全都是往前指的边，章节读起来也正好是制作顺序。
    Sorts a chapter's quests so that ingredients come before the things made from them;
    that keeps every recipe dependency pointing backwards (acyclic) and reads naturally.
    """
    index_of = {}
    for i, step in enumerate(rows):
        if step[0] == "item":
            index_of.setdefault(step[1], i)
    after = {i: set() for i in range(len(rows))}      # i must come before after[i]
    indegree = {i: 0 for i in range(len(rows))}
    for i, step in enumerate(rows):
        for ingredient in RECIPES.get(step[1], ()):
            j = index_of.get(ingredient)
            if j is None or j == i or i in after[j]:
                continue
            after[j].add(i)
            indegree[i] += 1
    heapq.heapify(ready := [i for i in range(len(rows)) if indegree[i] == 0])
    out = []
    while ready:
        i = heapq.heappop(ready)
        out.append(rows[i])
        for k in sorted(after[i]):
            indegree[k] -= 1
            if indegree[k] == 0:
                heapq.heappush(ready, k)
    return out if len(out) == len(rows) else rows       # 有环就保持原样，交给序号兜底

# FTB Quests 根文件（全局默认值）。
# 键名全部按 FTB Quests 2001.4.22 的 BaseQuestFile 字段来（version / default_reward_team /
# default_consume_items …）。以前写成 file_version / default_team_consume_items，
# 那些键 FTB 根本不认 —— 等于整份默认值没生效，这里一并修正。
# Keys must match the real BaseQuestFile fields, otherwise FTB silently ignores them.
FILE_DEFAULTS = """{
\tdefault_autoclaim_rewards: "enabled"
\tdefault_consume_items: false
\tdefault_quest_disable_jei: false
\tdefault_quest_shape: "circle"
\tdefault_reward_team: false
\tdetection_delay: 20
\tdisable_gui: false
\tdrop_book_on_death: false
\tdrop_loot_crates: false
\temergency_items_cooldown: 300
\tgrid_scale: 0.5d
\tlock_message: ""
\tloot_crate_no_drop: {
\t\tboss: 0
\t\tmonster: 600
\t\tpassive: 4000
\t}
\tpause_game: false
\tprogression_mode: "linear"
\tshow_lock_icons: true
\ttitle: "Dynasty 王朝"
\tversion: 13
}
"""

# 章节分组：任务书左侧栏的折叠标题（「愚者 / 登神者」都是这么分组的）。
# 每组第一个字符必须是 0-7，FTB 用 Long.parseLong(id, 16)【有符号】解析。
# Chapter groups: the collapsible headers in the quest-book sidebar.
CHAPTER_GROUPS = [
    ("王朝主线", "&6&l王朝主线"),
    ("万里山河", "&2&l万里山河"),
    ("神兵宝甲", "&c&l神兵宝甲"),
]


CHAPTER_PER_ROW = 8


def quest_id(index):
    # 注意：FTB Quests 用 Long.parseLong(id, 16)【有符号】解析 id，
    # 所以首字符必须是 0-7（原名 d7… 高位为 1，会解析失败 → 前置线连不上）。
    # IDs must stay below 0x8000000000000000 or FTB fails to parse them and dependencies break.
    return "1%015x" % index


def task_id(index):
    return "2%015x" % index


def reward_id(index, slot):
    return "3%013x%02x" % (index, slot)


def chapter_id(number):
    return "4%015x" % number


def chapter_group_id(number):
    """章节分组 id：前缀 5，后面是顺序号（0-7 开头才是有符号 long）。"""
    return "5%015x" % number


def escape(text):
    return text.replace('"', "'")


def dim_name(target):
    if target.endswith("celestial_dynasty"):
        return "天朝·龙庭"
    if target.endswith("jiuxiao"):
        return "九霄天界"
    if target.endswith("dragon_palace"):
        return "东海龙宫"
    return "地府"


def adv_title(target):
    key = "advancements.dynasty.%s.title" % target.split(":")[-1]
    return names().get(key, target.split(":")[-1])


def adv_desc(target):
    key = "advancements.dynasty.%s.description" % target.split(":")[-1]
    return names().get(key, "")


def title_for(kind, target, count, opts):
    if opts.get("name"):
        return opts["name"]
    if kind == "item":
        name = display(target)
        return "%s ×%d" % (name, count) if count > 1 else name
    if kind == "kill":
        return "剿灭 %s ×%d" % (display(target), count)
    if kind == "dimension":
        return "踏入%s" % dim_name(target)
    return adv_title(target)


def desc_for(kind, target, count, opts):
    parts = []
    if kind == "item":
        parts.append("收集「%s」×%d。" % (display(target), count))
    elif kind == "kill":
        parts.append("击杀「%s」×%d。" % (display(target), count))
    elif kind == "dimension":
        parts.append("进入「%s」一次。" % dim_name(target))
    else:
        text = adv_desc(target)
        parts.append(("完成成就「%s」。" % adv_title(target)) + (" " + text if text else ""))
    prev = UPGRADE.get(target.split(":")[-1]) if kind == "item" else None
    if prev:
        parts.append("升级链：配方需要先做出上一级的「%s」，一把一把往上换。" % display(prev))
    if opts.get("desc"):
        parts.append(opts["desc"])
    return "".join(parts)


def icon_for(kind, target):
    if kind == "item":
        return target
    if kind == "kill":
        return "minecraft:iron_sword"
    if kind == "dimension":
        return dim_icon(target)
    return "minecraft:knowledge_book"


def task_line(index, kind, target, count):
    if kind == "item":
        return ('{ id: "%s", type: "item", item: { id: "%s", Count: 1b }, count: %dL }'
                % (task_id(index), target, count))
    if kind == "kill":
        return ('{ id: "%s", type: "kill", entity: "%s", value: %dL }'
                % (task_id(index), target, count))
    if kind == "dimension":
        return ('{ id: "%s", type: "dimension", dimension: "%s", value: 1L }'
                % (task_id(index), target))
    return ('{ id: "%s", type: "advancement", advancement: "%s" }'
            % (task_id(index), target))


def auto_rewards(kind, target, count):
    """奖励：物品 + 经验 + 功名（功名用来升官阶）。"""
    if kind == "item":
        tier = TIER.get(target.split(":")[-1], 1)
    elif kind == "kill":
        tier = 3
    else:
        tier = 2
    rewards = [("dynasty:copper_coin", 6 * tier + 4)]
    if tier >= 3:
        rewards.append(("dynasty:gold_coin", tier))
    # 任务给的功名不多：功名主要靠杀敌 / 与 NPC 交互 / 首次获得新物品（见 DynastyMerit）
    return rewards, 4 + 2 * tier, 8 + 4 * tier


def rewards_line(index, rewards, xp, merit):
    out = []
    slot = 0
    for item, count in rewards:
        out.append('{ id: "%s", type: "item", item: { id: "%s", Count: 1b }, count: %d }'
                   % (reward_id(index, slot), item, count))
        slot += 1
    if xp > 0:
        out.append('{ id: "%s", type: "xp", value: %d }' % (reward_id(index, slot), xp))
        slot += 1
    if merit > 0:
        # 以玩家身份执行、临时给 2 级权限（命令本身要 OP 才能手动用）
        out.append('{ id: "%s", type: "command", command: "dynasty merit %d", '
                   'elevate_perms: true, silent: true }' % (reward_id(index, slot), merit))
    return ", ".join(out)



# 排布间距：一条链上相邻任务 1.0 格是一格（FTB 的坐标就是「一个任务一格」），
# 这里留 1.5 格 —— 线短、看得清；两条链之间再空 1.0 格。
# 参考《愚者》：链内 1.0~1.5，链间 2.0 上下。以前用的是 2.0 / 2.0+2.0，太散。
# Spacing: 1.5 cells along a chain (FTB draws lines between quest centres), 1.0 extra
# between two separate chains. The old 2.0 / +2.0 made every chapter look stretched out.
STEP_X = 1.5
STEP_Y = 1.5
CHAIN_GAP = 1.0

# 排布约束（玩家反馈：任务不要离中心太远、别拉太长；散开之后就地平铺/绕着中心转）
#   MAX_RUN  —— 一条直线最多连着摆几个，再多就「折」到下一行 / 下一列
#   R_MAX    —— 中心放射的最大半径（超过就不再往外拉）
#   BEND_DEG —— 超过半径上限后，每多一个节点绕中心转多少度（继续沿弧线发展）
#   MAX_WIDTH—— 枝干形里，一层最多铺多宽，超了换一层
MAX_RUN = 8
MAX_COL = 10                  # 竖排章一列最多几个（列少一点，整章才方正）
FAN_R0 = 2.4                  # 放射章：中心到每条线第一个任务的距离（留空，中心不挤）
FAN_STEP = 1.7                # 放射章：沿线方向每多一个任务往外走多少
R_MAX = 9.0                   # 放射章半径上限（超过就绕中心转，不再往外拉）
BEND_DEG = 13.0
MAX_WIDTH = 12.0
TREE_WIDTH = 16.0             # 枝干形里一层最多铺多宽（够放两条枝）
COL_PITCH = STEP_X + 0.25     # 竖排章里列与列的间距（比行距紧一点，整章更方正）
COLS_PER_BLOCK = 10           # 竖排章一段最多几列，超了换到下面一段（别拉成一条长横杠）
GROUP_GAP = 0.9               # 同一段里换「流派 / 分组」时多留的空（列带按 group 标记分开）
PER_BAND = int(MAX_WIDTH / STEP_X) + 1                     # 横排一层最多摆几个节点位


def layout_flow(nodes, children, dx=STEP_X, dy=STEP_Y, gap=CHAIN_GAP):
    """
    （备用）树形排布：x 按层级向右推进、父节点居中于子节点之间。

    现在默认用的是 {@link layout_lines}（按线排、和前置解耦）。这个树形排布只在
    需要「看得出分叉」的特殊章节才会用得上，先留着。
    Optional tree layout, kept for reference; chapters use layout_lines.
    """
    pos = {}
    cursor = [0.0]

    def walk(node, depth):
        kids = children.get(node, [])
        if not kids:
            pos[node] = (depth * dx, cursor[0])
            cursor[0] += dy
            return pos[node][1]
        ys = [walk(kid, depth + 1) for kid in kids]
        y = sum(ys) / len(ys)
        pos[node] = (depth * dx, y)
        return y

    for root in nodes:
        walk(root, 0)
        cursor[0] += gap                       # 章节内的不同支线之间留点空
    if pos:                                    # 垂直居中：上下各占一半
        low = min(y for _, y in pos.values())
        high = max(y for _, y in pos.values())
        mid = (low + high) / 2.0
        pos = {n: (x, y - mid) for n, (x, y) in pos.items()}
    return pos


def split_lines(rows):
    """把一章的步骤按 branch 标记切成若干条「线」（线内是顺着做的）。"""
    lines, cur = [], []
    for pos, step in enumerate(rows):
        if pos > 0 and step[3].get("branch"):
            lines.append(cur)
            cur = []
        cur.append(pos)
    if cur:
        lines.append(cur)
    return lines


def center(pos):
    """整章以原点居中 / centre the chapter on the origin."""
    if not pos:
        return pos
    xs = [x for x, _ in pos.values()]
    ys = [y for _, y in pos.values()]
    mx, my = (min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0
    return {n: (x - mx, y - my) for n, (x, y) in pos.items()}


def wrap_runs(line, per=MAX_RUN):
    """把一条线切成若干段（每段最多 per 个）—— 用来「折行」，别把线拉太长。"""
    return [line[i:i + per] for i in range(0, len(line), per)] or [[]]


def layout_rows(rows):
    """
    横排：**一层里能塞几条线就塞几条**（线之间留一格空隙），塞不下才换下一层。
    每条线自己最多 MAX_RUN 个节点，超了折到下一层——所以一章不会变成十几层高，
    也不会横着拉出很远，整章贴近中心。

    Horizontal bands packed by width: several runs share a band when they fit, so a chapter stays
    a compact block instead of a tall stack of rows.
    """
    lines = split_lines(rows)
    pos = {}
    band = 0
    col = 0
    for line in lines:
        for chunk in wrap_runs(line, per=PER_BAND):
            if col > 0 and col + len(chunk) > PER_BAND:
                band += 1
                col = 0
            for i, p in enumerate(chunk):
                pos[p] = ((col + i) * STEP_X, -band * (STEP_Y + CHAIN_GAP))
            col += len(chunk) + 1          # 线之间留一格，别粘在一起
            if col > PER_BAND:
                band += 1
                col = 0
    return center(pos)


def layout_cols(rows):
    """
    竖排：每条线一列，**一列最多 MAX_RUN 个**，超出的在右边紧挨着再起一列（折列）；
    一「段」最多 COLS_PER_BLOCK 列，超过就换到下面一段（左对齐重排）——
    所以「兵器谱 / 甲胄谱 / 饰品图鉴」这类图鉴章是方方正正的几块，不会拉成一条长横杠。

    Vertical columns with wrapping and block packing: each line is one column, long columns
    fold into the next one, and a block holds at most COLS_PER_BLOCK columns before the rest
    continues in a new block below.
    """
    lines = split_lines(rows)
    pos = {}
    x, y0, used, height = 0.0, 0.0, 0, 0
    group = None
    for line in lines:
        line_group = rows[line[0]][3].get("group")     # 线首上的分组标记（流派 / 合体）
        chunks = wrap_runs(line, per=MAX_COL)
        if used and used + len(chunks) > COLS_PER_BLOCK:       # 换下一段
            y0 -= (height - 1) * STEP_Y + STEP_Y + CHAIN_GAP
            x, used, height = 0.0, 0, 0
        elif used and line_group and group and line_group != group:
            x += GROUP_GAP                                     # 同段里换流派：留一道空
        if line_group:
            group = line_group
        for ci, chunk in enumerate(chunks):
            for i, p in enumerate(chunk):
                pos[p] = (x + ci * COL_PITCH, y0 - i * STEP_Y)
        x += len(chunks) * COL_PITCH
        used += len(chunks)
        height = max(height, max(len(c) for c in chunks))
    return center(pos)


def layout_fan(rows):
    """
    中心放射：章首放正中，**每条线（含主线）按 360°/线数 均匀分角**往外散；
    第一环留出 FAN_R0 的空档（中心不挤成一团），沿线按 FAN_STEP 往外走；
    散到 R_MAX 就不再往外拉，多出来的节点绕中心转（沿圆弧继续发展）。

    Radial layout: every line gets an even slice of 360° (so the star looks regular), the first
    ring is pushed out by FAN_R0, and anything past R_MAX curves around the centre instead of
    stretching further out.
    """
    lines = split_lines(rows)
    pos = {}
    if not lines:
        return pos
    trunk = lines[0]
    slice_deg = 360.0 / len(lines)                     # 均匀分角，星形才看得出规律
    max_drift = slice_deg * 0.35                       # 绕圈时最多偏离自己扇区多少（不扫到邻居）
    in_cap = int((R_MAX - FAN_R0) / FAN_STEP) + 1      # 半径上限内能放几个

    def place(node, angle_deg, step_index, drift_per):
        r = FAN_R0 + (step_index - 1) * FAN_STEP
        theta = math.radians(angle_deg)
        if r > R_MAX:                                  # 到半径上限就绕中心转，不再往外拉
            theta += math.radians(drift_per * (r - R_MAX) / FAN_STEP)
            r = R_MAX
        pos[node] = (math.cos(theta) * r, math.sin(theta) * r)

    pos[trunk[0]] = (0.0, 0.0)                         # 章首：正中心
    for li, seg in enumerate(lines):
        seg = seg[1:] if li == 0 else seg              # 主线去掉章首（它就在中心）
        angle = 180.0 + li * slice_deg                 # 主线从左边开始，一圈均匀铺开
        overflow = max(0, len(seg) - in_cap)
        drift = min(BEND_DEG, max_drift / overflow) if overflow else BEND_DEG
        for j, node in enumerate(seg, start=1):
            place(node, angle, j, drift)
    return center(pos)


def layout_tree(rows):
    """
    枝干形：主线横着走（**一段最多 MAX_RUN 个，超了折到下一行**），
    支线从主线旁边「平着发展」——上下分两层铺开，宽度超了就换一层。
    这样兵器谱这种「一条主线 + 一堆支线」的章节是扁的，不会横着拉出十几格。

    Tree layout: a wrapped horizontal trunk with branches growing *flat* in lanes above and below.
    """
    lines = split_lines(rows)
    pos = {}
    if not lines:
        return pos

    # 主干：折行（蛇形），每段最多 MAX_RUN 个
    y = 0.0
    trunk_bands = 0
    forward = True
    for chunk in wrap_runs(lines[0]):
        seq = chunk if forward else list(reversed(chunk))
        for i, p in enumerate(seq):
            pos[p] = (i * STEP_X, y)
        forward = not forward
        y -= STEP_Y + CHAIN_GAP
        trunk_bands += 1

    # 支线：一上一下交替；每侧按「流式」平铺，宽度超过 MAX_WIDTH 就再往外一层
    above = [seg for i, seg in enumerate(lines[1:]) if i % 2 == 0]
    below = [seg for i, seg in enumerate(lines[1:]) if i % 2 == 1]

    def flow(side_lines, direction):
        x = 0.0
        lane = 1
        for seg in side_lines:
            chunks = wrap_runs(seg)
            width = max(len(chunk) for chunk in chunks) * STEP_X
            if x > 0.0 and x + width > TREE_WIDTH:
                lane += 1
                x = 0.0
            for ci, chunk in enumerate(chunks):
                for i, p in enumerate(chunk):
                    pos[p] = (x + i * STEP_X, direction * (lane + ci) * (STEP_Y + CHAIN_GAP))
            x += width + CHAIN_GAP

    flow(above, 1.0)
    flow(below, -1.0)
    return center(pos)


LAYOUTS = {
    "rows": layout_rows,      # 横排
    "cols": layout_cols,      # 竖排
    "fan": layout_fan,        # 中心往外放射（均匀分角 + 半径上限）
    "tree": layout_tree,      # 主干 + 树枝（备用：目前没有章节用，兵器谱已改竖排）
}


def layout_lines(rows, style="rows"):
    """按章节风格排布 / dispatch by chapter layout style."""
    return LAYOUTS.get(style, layout_rows)(rows)


def build():
    os.makedirs(CH_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "data.snbt"), "w", encoding="utf-8") as f:
        f.write(FILE_DEFAULTS)
    print("file defaults: data.snbt")

    # 章节分组（左侧栏折叠标题）/ chapter groups for the quest-book sidebar
    groups = "\n".join('\t\t{ id: "%s", title: "%s" }'
                       % (chapter_group_id(i + 1), CHAPTER_GROUPS[i][1])
                       for i in range(len(CHAPTER_GROUPS)))
    with open(os.path.join(OUT_DIR, "chapter_groups.snbt"), "w", encoding="utf-8") as f:
        f.write("{\n\tchapter_groups: [\n%s\n\t]\n}\n" % groups)
    print("chapter groups: %d 组" % len(CHAPTER_GROUPS))

    # 第一遍：精简 + 登记索引
    #   * DROP_TARGETS 里的目标直接删除
    #   * 同一个目标全局只留第一次出现（避免「再交 64 个金币」这种凑数任务）
    flat = []
    by_target = {}
    kept_steps = []
    seen = set()
    dupes = []
    for number, (filename, title, icon, steps, _entry, _group, _sub) in enumerate(CHAPTERS):
        rows = []
        for step in steps:
            kind, target, count, opts = step
            key = "%s:%s:%s" % (kind, target, count if kind == "kill" else "")
            if target in DROP_TARGETS:
                continue
            if key in seen:
                # 全局去重：同一件事（同一件物品 / 同一个击杀数）只留第一次出现的那条
                dupes.append("第 %d 章重复：%s %s（已合并到前面的章节）" % (number + 1, kind, target))
                continue
            seen.add(key)
            rows.append(step)
        # 分段：带 branch 标记的任务开始「新的一条线」（支线 / 分类 / 分槽位），
        # 段内独立排序 —— 这样「材料 → 成品」的排序不会把一条链拆散、两串串到一起。
        # Steps flagged branch=True start a new line; each line is sorted on its own so the
        # recipe ordering can never interleave two chains.
        segments, cur = [], []
        for step in rows:
            if step[3].get("branch") and cur:
                segments.append(cur)
                cur = []
            cur.append(step)
        if cur:
            segments.append(cur)
        rows = [step for seg in segments for step in order_steps(seg)]
        kept_steps.append(rows)
        for pos, step in enumerate(rows):
            kind, target, count, opts = step
            index = len(flat)
            flat.append((number, pos, kind, target, count, opts, index))
            by_target.setdefault("%s:%s" % (kind, target), index)

    # 章节入口：主线接上一章末尾，独立章接第一章末尾
    # chapter entries: story chapters chain to the previous chapter, side chapters to chapter 1
    entry_of = {}
    prev_last = None
    first_last = None
    for number, chapter in enumerate(CHAPTERS):
        mode = chapter[4] if len(chapter) > 4 else "prev"
        if mode == "first":
            entry_of[number] = None
        elif mode == "c1":
            entry_of[number] = first_last
        else:
            entry_of[number] = prev_last
        last_index = len([f for f in flat if f[0] < number and True]) - 1
        # 本章最后一条（用于给下一章当入口）
        chapter_indices = [f[6] for f in flat if f[0] == number]
        this_last = chapter_indices[-1] if chapter_indices else prev_last
        if mode == "first" or first_last is None:
            first_last = this_last
        # 注意：装备/图鉴章（mode == "c1"）**不参与主线递进**，
        # 它们虽然排在前面（这样才能完整收录所有兵器/甲胄/饰品），
        # 但主线下一章要接的仍然是「上一章主线」，不能接图鉴章。
        # Side/codex chapters are listed early so they own every item quest, but they must
        # not take over the main storyline chain.
        if mode != "c1":
            prev_last = this_last

    warnings = []

    # ---- 前置图（全局）:先算全部前置（允许跨章、允许往前指），再只删掉真正成环的回边 ----
    # 为什么要全局做：环可能跨章节（金币↔银币、青铜剑←兵器图纸←竹简←青铜剑）。
    # 有环时 FTB 的 Quest.isVisible 会无限递归 → 一打开任务书就 StackOverflow 崩溃。
    # Build the dependency graph globally first, then remove only the back-edges that
    # actually close a cycle, so every legitimate cross-chapter link survives.
    raw_deps = {}
    for number, (filename, title, icon, steps, _entry, _group, _sub) in enumerate(CHAPTERS):
        rows = kept_steps[number]
        base = len([f for f in flat if f[0] < number])
        for pos, step in enumerate(rows):
            kind, target, count, opts = step
            index = base + pos
            inside_lo, inside_hi = base, base + len(rows)          # 本章任务的 id 区间
            deps = set()
            # ① 配方材料：材料任务必须先完成
            for ingredient in RECIPES.get(target, ()):
                found = by_target.get("item:" + ingredient)
                if found is not None and found != index:
                    deps.add(found)
            # ④ 手写的额外前置（支线的挂点）——先算，因为它比「接上一条」优先：
            #    支线的第一条要挂在指定任务上（或章首），不能被兜底串成一条线。
            for ref in step[3].get("extra", []):
                ref = str(ref)
                if ref.startswith("kill:"):
                    found = by_target.get("kill:" + ref[5:])
                elif ref.startswith("dim:"):
                    found = by_target.get("dimension:dynasty:" + ref[4:])
                elif ref.startswith("adv:"):
                    found = by_target.get("advancement:dynasty:" + ref[4:])
                else:
                    found = by_target.get("item:" + ref, by_target.get("kill:" + ref))
                if found is None:
                    warnings.append("未找到额外前置 %s（第 %d 章）" % (ref, number + 1))
                elif found < index and found not in deps:
                    deps.add(found)
            # ② 章节入口 / 支线挂点：
            #   * 本章第一条 → 接上一章末尾（保证章节按顺序解锁）
            #   * 每条支线的线首 → 接**本章第一条**，这样书里能看见「链条」，
            #     而且只锁一条（不会像以前那样一层层卡死）
            if not deps:
                if pos == 0:
                    entry = entry_of.get(number)
                    if entry is not None and entry != index:
                        deps.add(entry)
                elif opts.get("branch") and index != base:
                    deps.add(base)
            raw_deps[index] = deps

    WHITE, GRAY, BLACK = 0, 1, 2
    color = {}
    dropped = []

    def visit(node):
        color[node] = GRAY
        for nxt in sorted(raw_deps.get(node, ())):
            if color.get(nxt) == GRAY:                 # 指回栈里的节点 = 回边，删掉
                raw_deps[node].discard(nxt)
                dropped.append((node, nxt))
                continue
            if color.get(nxt, WHITE) == WHITE:
                visit(nxt)
        color[node] = BLACK

    for node in sorted(raw_deps):
        if color.get(node, WHITE) == WHITE:
            visit(node)
    print("前置图：%d 条前置，删掉 %d 条会成环的回边（跨章前置其余全部保留）"
          % (sum(len(d) for d in raw_deps.values()), len(dropped)))
    for node, nxt in dropped[:8]:
        warnings.append("删掉回边：任务 %d 不再前置任务 %d（否则成环）" % (node, nxt))

    per_chapter = {}
    for number, (filename, title, icon, _ignored, _entry_mode, _group, _sub) in enumerate(CHAPTERS):
        steps = kept_steps[number]
        base = len([f for f in flat if f[0] < number])

        node_deps = {}
        for pos, step in enumerate(steps):
            index = base + pos
            node_deps[index] = sorted(raw_deps.get(index, ()))
        # 排布只看「线」，不看前置（见 layout_lines 的说明）；
        # 每章按 CHAPTER_LAYOUT 选横排 / 竖排 / 中心放射 / 枝干。
        coords_local = layout_lines(steps, CHAPTER_LAYOUT.get(filename, "rows"))
        coords = {base + pos: xy for pos, xy in coords_local.items()}
        chapter_last = base + len(steps) - 1
        # 每条线的第一个任务（画成菱形，表示「这里开始一条新线」）
        line_heads = {base + pos for pos, step in enumerate(steps)
                      if step[3].get("branch")}
        line_heads.add(base)

        body = []
        for pos, step in enumerate(steps):
            kind, target, count, opts = step
            index = base + pos
            deps = node_deps[index]
            deps_txt = ""
            if deps:
                deps_txt = "\n\t\t\tdependencies: [%s]" % ", ".join(
                    '"%s"' % quest_id(d) for d in deps)

            rewards, xp, merit = auto_rewards(kind, target, count)
            if opts.get("rewards"):
                rewards = opts["rewards"]
            if opts.get("xp") is not None:
                xp = opts["xp"]
            if opts.get("merit") is not None:
                merit = opts["merit"]

            x, y = coords.get(index, (0.0, 0.0))
            subtitle = ""
            if number == 0 and pos == 0:
                subtitle = ('\n\t\t\tsubtitle: "任务不再一条条卡死：'
                            '只有配方 / 剧情门槛会锁，其余可以随便挑着做"')

            # 节点形状（照「愚者」的做法分主次，主线一眼能看出头尾）：
            #   shape: 章首齿轮 / 线首菱形 / 章末六边形 / 其余用全局默认圆点
            # Node shapes: gear for the chapter opener, diamond for line heads,
            # hexagon for the chapter finale, everything else the global default (circle).
            if index == base and base == min(coords):
                shape_txt = '\n\t\t\tshape: "gear"\n\t\t\tsize: 2.0d'
            elif index in line_heads:
                shape_txt = '\n\t\t\tshape: "diamond"\n\t\t\tsize: 1.5d'
            elif index == chapter_last:
                shape_txt = '\n\t\t\tshape: "hexagon"\n\t\t\tsize: 2.0d'
            else:
                shape_txt = ""

            body.append(
                '\t\t{\n'
                '\t\t\tid: "%s"\n'
                '\t\t\ttitle: "%s"%s%s\n'
                '\t\t\tx: %.1fd\n'
                '\t\t\ty: %.1fd\n'
                '\t\t\ticon: { id: "%s" }\n'
                '\t\t\tdescription: ["%s"]\n'
                '\t\t\ttasks: [%s]\n'
                '\t\t\trewards: [%s]%s\n'
                '\t\t}'
                % (quest_id(index), escape(title_for(kind, target, count, opts)), subtitle,
                   shape_txt, x, y, icon_for(kind, target),
                   escape(desc_for(kind, target, count, opts)),
                   task_line(index, kind, target, count),
                   rewards_line(index, rewards, xp, merit), deps_txt))
        per_chapter[number] = (filename, title, icon, body, len(steps))

    for number in sorted(per_chapter):
        filename, title, icon, body, count = per_chapter[number]
        group = CHAPTERS[number][5]
        subtitle = CHAPTERS[number][6]
        text = ('{\n'
                '\tdefault_hide_dependency_lines: false\n'
                '\tdefault_quest_shape: ""\n'
                '\tfilename: "%s"\n'
                '\tgroup: "%s"\n'
                '\ticon: { id: "%s" }\n'
                '\tid: "%s"\n'
                '\torder_index: %d\n'
                '\tquest_links: [ ]\n'
                '\tquests: [\n%s\n\t]\n'
                '\tsubtitle: ["%s"]\n'
                '\ttitle: "%s"\n'
                '}\n'
                % (filename, chapter_group_id(group + 1), icon, chapter_id(number),
                   number, ",\n".join(body), escape(subtitle), escape(title)))
        with open(os.path.join(CH_DIR, filename + ".snbt"), "w", encoding="utf-8") as f:
            f.write(text)
        print("chapter: %-16s %3d 条  %s §  %s" % (filename + ".snbt", count, title,
                                                   CHAPTER_GROUPS[group][0]))

    print("任务总数：%d，章节：%d" % (len(flat), len(CHAPTERS)))
    if dupes:
        print("重复任务（已合并）：%d 条" % len(dupes))
        for d in dupes:
            print("   -", d)
    if warnings:
        print("WARN:")
        for w in warnings:
            print("   -", w)


if __name__ == "__main__":
    build()

