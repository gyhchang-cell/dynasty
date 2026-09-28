"""结构性契约检查：本轮改动里**无法在无游戏环境下运行**的那部分，用源码断言钉住。

覆盖：
  1. 叛将血条：按玩家订阅（不是全局开关）、节流、跨维度与移除清理、只登记候选；
  2. 悬停：不再重复原版属性、已删除内部实现说明、只追加不清空、客户端类不进服务器；
  3. 文案：新增翻译键与文档片段一致。

用法：python3 tools/eqdev/test_source_contracts.py
"""
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BOSSES = os.path.join(ROOT, "src/main/java/com/dynasty/entity/DynastyBosses.java")
SUBS = os.path.join(ROOT, "src/main/java/com/dynasty/entity/DynastyBossBarSubscriptions.java")
VISIBILITY = os.path.join(ROOT, "src/main/java/com/dynasty/entity/BossBarVisibility.java")
TOOLTIPS = os.path.join(ROOT, "src/main/java/com/dynasty/client/DynastyTooltips.java")
TEXT = os.path.join(ROOT, "src/main/java/com/dynasty/client/DynastyTooltipText.java")
GATE = os.path.join(ROOT, "src/main/java/com/dynasty/client/DynastyTooltipGate.java")
TRINKETS = os.path.join(ROOT, "src/main/java/com/dynasty/DynastyTrinketTips.java")
LANG_SNIPPET = os.path.join(ROOT, "docs/eqdev/tooltip-lang-additions.json")
OLD_BACKUP = "/tmp/DynastyTooltips.orig.bak"

passed = 0
failures = []


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def check(name, ok, detail=""):
    global passed
    if ok:
        passed += 1
    else:
        failures.append(name + (" —— " + detail if detail else ""))


def rebel_general_body(text):
    """截出 RebelGeneral 那一段（到下一个 static class 为止）。"""
    start = text.index("public static class RebelGeneral")
    rest = text[start + 10:]
    end = rest.index("public static class ")
    return rest[:end]


def main():
    bosses = read(BOSSES)
    subs = read(SUBS)
    tooltips = read(TOOLTIPS)
    rebel = rebel_general_body(bosses)

    # ---------- 1. 血条 ----------
    check("血条：RebelGeneral 的 startSeenByPlayer 只登记候选，不再直接 addPlayer",
          "barSubscriptions.startSeenByPlayer(player)" in rebel
          and "startSeenByPlayer" in rebel
          and "this.bossEvent.addPlayer(player)" not in rebel)
    check("血条：RebelGeneral 的 stopSeenByPlayer 会退订",
          "barSubscriptions.stopSeenByPlayer(player)" in rebel)
    check("血条：RebelGeneral 死亡 / 移除都会清干净",
          "barSubscriptions.clear()" in rebel and rebel.count("barSubscriptions.clear()") >= 2)
    check("血条：没有用全局 visible 开关（setVisible）代替逐玩家判定",
          "setVisible(" not in bosses and "setVisible(" not in subs)
    check("血条：AI 步进里接了订阅管理器（否则永远不会订阅）",
          "barSubscriptions.tick()" in rebel)
    check("血条：管理器内部按间隔错峰，不每 tick 扫世界",
          "CHECK_INTERVAL" in subs and "if (--this.cooldown > 0)" in subs
          and "getEntitiesOfClass" not in subs and "forEach" not in subs)
    check("血条：只在跟踪自己的玩家集合上判定（candidates）",
          "Map<UUID, Memory> candidates" in subs and "getPlayerList().getPlayer(entry.getKey())" in subs)
    check("血条：跨维度会收起血条", "player.level() != level" in subs)
    check("血条：记录会过期清理（不会无限增长）",
          "FORGET_TICKS" in subs and "iterator.remove()" in subs)
    check("血条：判定逻辑与 MC 类型解耦（可单测）",
          "net.minecraft" not in read(VISIBILITY))
    check("血条：生成校验区分自然生成与其它入口（自然生成才做严格落点校验）",
          "DynastySpawnPlacement.strict(reason)" in rebel and "hasStandingSpace" in rebel
          and "if (!DynastySpawnPlacement.strict(reason))" in rebel)

    # ---------- 2. 悬停 ----------
    check("悬停：只追加、不清空整份 tooltip",
          ".clear()" not in tooltips and "tip.add(" in tooltips)
    check("悬停：不再重复原版的攻击力 / 护甲 / 韧性 / 耐久行",
          "攻击力：" not in tooltips and "韧性：" not in tooltips
          and "耐久：" not in tooltips and "护甲：" not in tooltips
          and "appendStats" not in tooltips and "appendArmorStats" not in tooltips)
    check("悬停：已删除「每秒自动刷新 / 换维度不会丢」等内部实现说明",
          "每秒自动刷新" not in tooltips and "换维度不会丢" not in tooltips
          and "refreshed every second" not in tooltips)
    check("悬停：套装只保留「套装详情见图鉴」指引，没有长篇套装展开",
          "套装效果：" not in tooltips and "setCodexHint" in read(TEXT))
    check("悬停：默认 / Shift 两个视图分开（详情只在 Shift 时追加）",
          "if (shift)" in tooltips and "holdShift(zh)" in tooltips)
    check("悬停：装备判定走客户端事件类，服务端不会加载",
          "value = Dist.CLIENT" in tooltips)
    check("悬停：共享类里的 Shift 检查用 DistExecutor 包住（服务器安全）",
          "DistExecutor.unsafeCallWhenOn(Dist.CLIENT" in read(TRINKETS))
    check("悬停：Shift 状态只在客户端类里碰 GLFW",
          "GLFW" in read(GATE) and "GLFW" not in read(TRINKETS))
    check("悬停：数值折叠按运算类型（不是把修饰符相加）",
          "OP_MULTIPLY_BASE" in read(TEXT) and "multiplyTotal *=" in read(TEXT))
    check("悬停：Shift 提示走翻译键键并带回退（不会显示原始键名）",
          "I18n.exists" in read(TEXT) and "Component.translatable" in read(TEXT))

    # ---------- 3. 文案片段 ----------
    keys = set(re.findall(r'new Text\("([^"]+)"', read(TEXT)))
    snippet = json.load(open(LANG_SNIPPET, encoding="utf-8"))
    zh = set(snippet["zh_cn"])
    en = set(snippet["en_us"])
    check("文案：Java 用到的每个键都在语言片段里（zh）", keys <= zh, str(sorted(keys - zh)))
    check("文案：Java 用到的每个键都在语言片段里（en）", keys <= en, str(sorted(keys - en)))
    check("文案：片段里没有多余键", zh == keys and en == keys, str(sorted(zh ^ keys)))
    for lang in ("zh_cn", "en_us"):
        path = os.path.join(ROOT, "src/main/resources/assets/dynasty/lang/%s.json" % lang)
        body = json.load(open(path, encoding="utf-8"))
        expected = snippet[lang]
        check("文案：%s.json 已合并且与片段一致" % lang,
              all(body.get(key) == value for key, value in expected.items()),
              "不一致：" + str([key for key, value in expected.items() if body.get(key) != value]))

    print()
    if failures:
        print("通过 %d 项，失败 %d 项" % (passed, len(failures)))
        for failure in failures:
            print("  ❌", failure)
        return 1
    print("通过 %d 项，失败 0 项" % passed)
    print("✅ 结构性契约（血条订阅 / 悬停展示 / 文案键）全部符合本轮约定")
    return 0


if __name__ == "__main__":
    sys.exit(main())
