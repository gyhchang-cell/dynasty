"""FTB 任务书自检（每次导出自动跑）。

钉死几条踩过的坑：
  1. 任务 id 必须能被 FTB 的 Long.parseLong(id, 16)【有符号】解析 → 数值 < 0x8000000000000000
  2. 每条 dependencies 都必须指向真实存在的任务 id（否则前置线不会画出来）
  3. 任务里引用的物品 / 实体 / 成就 / 维度必须真实存在
  4. 坐标不能全挤在一个点上（那样在一章里只看得到一个任务）

运行：python3 tools/art/verify_ftbquests.py [mods_jar_or_dir]
"""
import glob
import json
import os
import re
import sys
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CHAPTER_DIR = os.path.join(ROOT, "modpack/config/ftbquests/quests/chapters")
MAX_SIGNED_LONG = 0x7FFFFFFFFFFFFFFF
MAX_FAR = 11.0          # 任务离章节中心的最大距离（玩家反馈：别散太开、支线别拉太长）

problems = []


def jar_path():
    if len(sys.argv) > 1 and sys.argv[1].endswith(".jar"):
        return sys.argv[1]
    jars = [p for p in glob.glob(os.path.join(ROOT, "build/libs/dynasty-*.jar"))
            if "sources" not in p and "javadoc" not in p]
    return jars[0] if jars else None


def reaches(graph, start, target, seen=None):
    """start 能不能（顺着前置）走到 target —— 用来判断某条前置是不是「必须删掉否则成环」。"""
    if seen is None:
        seen = set()
    if start == target:
        return True
    if start in seen:
        return False
    seen.add(start)
    return any(reaches(graph, nxt, target, seen) for nxt in graph.get(start, []))


def cycle_check(graph, quest_ids):
    """真正的环检测：FTB 的 Quest.isVisible 会顺着前置递归，有环 = 打开任务书 StackOverflow 崩溃。

    Real cycle detection — a single cycle in the dependency graph makes FTB's
    Quest.isVisible recurse until the stack overflows.
    """
    color, stack, cycles = {}, [], []

    def visit(node):
        color[node] = 1
        stack.append(node)
        for nxt in graph.get(node, []):
            if nxt not in quest_ids:
                continue
            if color.get(nxt) == 1:
                cycles.append(stack[stack.index(nxt):] + [nxt])
            elif color.get(nxt, 0) == 0:
                visit(nxt)
        stack.pop()
        color[node] = 2

    for node in sorted(quest_ids):
        if color.get(node, 0) == 0:
            visit(node)
    return cycles


def recipe_logic_check(quest_targets, deps_by_quest, graph):
    """
    任务逻辑检查：做某件东西的任务，必须把「配方里的材料任务」列为前置。
    这样就不会出现「先做铜剑再收铜锭」这种颠倒顺序。
    唯一的例外：这条前置如果加上去会成环（材料任务本身要靠它解锁），
    那它必须被删掉，不算问题。
    """
    recipe_dir = os.path.join(ROOT, "src/main/resources/data/dynasty/recipes")
    targets = set(quest_targets.values())
    by_item = {item: qid for qid, item in quest_targets.items()}
    recipes = []
    for path in glob.glob(os.path.join(recipe_dir, "*.json")):
        try:
            data = json.load(open(path, encoding="utf-8"))
        except Exception:
            continue
        result = data.get("result")
        result_id = result.get("item") if isinstance(result, dict) else None
        if not result_id:
            continue
        ingredients = set()
        for entry in data.get("ingredients", []):
            if isinstance(entry, dict) and entry.get("item"):
                ingredients.add(entry["item"])
        for entry in data.get("key", {}).values():
            if isinstance(entry, dict) and entry.get("item"):
                ingredients.add(entry["item"])
        recipes.append((result_id, ingredients))

    ingredients_of = {}
    for rid, ing in recipes:
        ingredients_of.setdefault(rid, set()).update(ing)
    checked = 0
    for result_id, ingredients in recipes:
        if result_id not in targets:
            continue
        want = {ingredient for ingredient in ingredients if ingredient in by_item}
        if not want:
            continue
        checked += 1
        # 用「成品的任务 id」去查它的前置任务 / look up deps by the product's quest id
        result_qid = by_item.get(result_id)
        have = {quest_targets[r] for r in deps_by_quest.get(result_qid, [])
                if r in quest_targets}
        missing = want - have
        # 双向配方（币种互兑 / 玉石与玉块互压）不算顺序颠倒 / mutual recipes are fine
        missing = {m for m in missing if result_id not in ingredients_of.get(m, set())}
        # 加上去会成环的，作者必须删掉 —— 不算问题
        missing = {m for m in missing
                   if not reaches(graph, by_item.get(m), result_qid)}
        if missing:
            problems.append("「%s」的配方材料 %s 没有作为前置（顺序颠倒）"
                            % (result_id, ", ".join(sorted(missing))))
    print("配方顺序检查：%d 件合成物（共读到 %d 条配方）" % (checked, len(recipes)))


def layout_check(name, coords, problems):
    """
    排布自检：一章不能太散、也不能挤成一列 / 一行。

    玩家反馈过的三个毛病，现在都钉在这里：
      * 「饰品图鉴」38 个任务全挤在一竖列（y 从 0 排到 85 格）→ 找都找不到；
      * 一章的链子全堆在下面 → 得一直往下拖；
      * 放射章 / 枝干章的支线一路往外拉，任务离章节中心十几格 → 现在硬性要求 ≤ MAX_FAR 格。
    间距约定见 gen_ftbquests.py 的 STEP_X / STEP_Y / CHAIN_GAP（1.5 / 1.5 / 1.0）。

    Layout lint: quests must be spread over both axes but stay compact.
    """
    if len(coords) < 2:
        return None
    xs = [float(a) for a, _b in coords]
    ys = [float(b) for _a, b in coords]
    rows = sorted(set(ys))
    gaps = [b - a for a, b in zip(rows, rows[1:])]
    span_x, span_y = max(xs) - min(xs), max(ys) - min(ys)
    # 离章节中心有多远（center() 会把整章居中，所以取坐标绝对值的最大者即可）
    far = max(max(abs(v) for v in xs), max(abs(v) for v in ys))
    if len(set(xs)) <= 1 and len(coords) > 3:
        problems.append("%s: %d 个任务全挤在一竖列（x 只有一个值）" % (name, len(coords)))
    if len(rows) <= 1 and len(coords) > 6:
        problems.append("%s: %d 个任务全挤在一行（y 只有一个值）" % (name, len(coords)))
    if gaps and max(gaps) > 4.5:
        problems.append("%s: 相邻两行最大空档 %.1f 格（任务之间离得太远）" % (name, max(gaps)))
    if span_y > 40:
        problems.append("%s: 纵向跨度 %.0f 格，太竖了（该拆成多条链）" % (name, span_y))
    if span_x > 40:
        problems.append("%s: 横向跨度 %.0f 格，太横了（该拆成多条链）" % (name, span_x))
    if far > MAX_FAR:
        problems.append("%s: 最远任务离章节中心 %.1f 格（超过 %.0f 格，散得太开 / 支线拉太长）"
                        % (name, far, MAX_FAR))
    return span_x, span_y, (max(gaps) if gaps else 0.0), far


def main():
    jar = jar_path()
    items, advancements = set(), set()
    if jar and os.path.exists(jar):
        with zipfile.ZipFile(jar) as z:
            for n in z.namelist():
                if n.startswith("assets/dynasty/models/item/") and n.endswith(".json"):
                    items.add(n.split("/")[-1][:-5])
                if n.startswith("data/dynasty/advancements/") and n.endswith(".json"):
                    advancements.add(n.split("/")[-1][:-5])
    else:
        problems.append("找不到构建出的 jar（先 ./gradlew build）")

    entities = set()
    ent_file = os.path.join(ROOT, "src/main/java/com/dynasty/entity/DynastyEntities.java")
    if os.path.exists(ent_file):
        entities = set(re.findall(r'"([a-z_]+)"', open(ent_file, encoding="utf-8").read()))

    chapters = sorted(glob.glob(os.path.join(CHAPTER_DIR, "*.snbt")))
    if not chapters:
        problems.append("没有找到任何任务章节 snbt")

    quest_ids = set()
    deps = []
    per_chapter = []
    quest_targets = {}
    deps_by_quest = {}
    for path in chapters:
        text = open(path, encoding="utf-8").read()
        ids = re.findall(r'\n\t\t\tid: "([0-9a-fA-F]{6,16})"', text)
        quest_ids.update(ids)
        deps += re.findall(r'"([0-9a-fA-F]{6,16})"', " ".join(
            re.findall(r"dependencies: \[([^\]]*)\]", text)))
        # 逐个任务块：取「任务 id → 物品目标 / 前置」用于配方顺序检查
        for block in re.split(r"\n\t\t\},?", text):
            qid = re.search(r'\n\t\t\tid: "([0-9a-fA-F]{6,16})"', block)
            if not qid:
                continue
            item = re.search(r'tasks: \[\{ id: "2[0-9a-f]{15}", type: "item", item: \{ id: "([^"]+)"', block)
            if item:
                quest_targets[qid.group(1)] = item.group(1)
            dep = re.search(r"dependencies: \[([^\]]*)\]", block)
            if dep:
                refs = re.findall(r'"([0-9a-fA-F]{6,16})"', dep.group(1))
                deps_by_quest[qid.group(1)] = refs
        coords = re.findall(r"\n\t\t\tx: (-?[\d.]+)d\n\t\t\ty: (-?[\d.]+)d", text)
        unique = len(set(coords))
        stats = layout_check(os.path.basename(path), coords, problems)
        per_chapter.append((os.path.basename(path), len(ids), unique, stats))

        for qid in ids:
            if int(qid, 16) > MAX_SIGNED_LONG:
                problems.append("%s: id %s 高位为 1，FTB 解析会失败" % (os.path.basename(path), qid))
        for ref in re.findall(r'item: \{ id: "([^"]+)"', text):
            ns, path_id = ref.split(":") if ":" in ref else ("minecraft", ref)
            if ns == "dynasty" and path_id not in items:
                problems.append("%s: 物品 %s 不存在" % (os.path.basename(path), ref))
        for ref in re.findall(r'type: "kill", entity: "([^"]+)"', text):
            if ref.startswith("minecraft:"):
                continue          # 原版生物（幻翼 / 凋灵骷髅…）不在这里校验
            if ref.split(":")[-1] not in entities:
                problems.append("%s: 实体 %s 不存在" % (os.path.basename(path), ref))
        for ref in re.findall(r'advancement: "([^"]+)"', text):
            if ref.split(":")[-1] not in advancements:
                problems.append("%s: 成就 %s 不存在" % (os.path.basename(path), ref))

    for dep in deps:
        if dep not in quest_ids:
            problems.append("依赖 %s 指向不存在的任务（前置线不会显示）" % dep)

    # ---- 章节分组（左侧栏折叠标题）自检 / chapter-group sanity check ----
    quests_dir = os.path.dirname(CHAPTER_DIR)
    group_file = os.path.join(quests_dir, "chapter_groups.snbt")
    group_ids = set()
    group_titles = []
    if os.path.exists(group_file):
        gtext = open(group_file, encoding="utf-8").read()
        for gid, gtitle in re.findall(r'id: "([0-9a-fA-F]+)", title: "([^"]*)"', gtext):
            if int(gid, 16) > MAX_SIGNED_LONG:
                problems.append("章节分组 id %s 高位为 1，FTB 解析会失败" % gid)
            if gid in group_ids:
                problems.append("章节分组 id %s 重复" % gid)
            group_ids.add(gid)
            group_titles.append(gtitle.replace("&6&l", "").replace("&2&l", "")
                                .replace("&c&l", ""))
        print("章节分组：%d 组（%s）" % (len(group_ids), "、".join(group_titles)))
    else:
        problems.append("缺少 chapter_groups.snbt（任务书左侧栏不会分组）")

    grouped = 0
    for path in chapters:
        text = open(path, encoding="utf-8").read()
        ref = re.search(r'\n\tgroup: "([0-9a-fA-F]*)"', text)
        if not ref:
            problems.append("%s: 没有 group 字段" % os.path.basename(path))
        elif ref.group(1):
            grouped += 1
            if ref.group(1) not in group_ids:
                problems.append("%s: group %s 在 chapter_groups.snbt 里不存在"
                                % (os.path.basename(path), ref.group(1)))
        if '\n\tsubtitle: [' not in text:
            problems.append("%s: 章节没有副标题" % os.path.basename(path))
    if group_ids and grouped != len(chapters):
        problems.append("有 %d 个章节没归入任何分组（共 %d 章）" % (len(chapters) - grouped, len(chapters)))

    # ---- data.snbt 键名自检：写错键 FTB 会静默忽略（踩过一次） ----
    # Wrong keys in data.snbt are silently ignored by FTB, so pin the real field names.
    known_keys = {
        "autoclaim_rewards", "block_progress", "default_autoclaim_rewards",
        "default_consume_items", "default_quest_disable_jei", "default_quest_shape",
        "default_reward_team", "detection_delay", "disable_gui", "drop_book_on_death",
        "drop_loot_crates", "emergency_items", "emergency_items_cooldown", "grid_scale",
        "hide_excluded_quests", "icon", "lock_message", "loot_crate_no_drop", "pause_game",
        "progression_mode", "quest_disable_jei", "reward_team", "show_lock_icons",
        "title", "version",
    }
    data_file = os.path.join(quests_dir, "data.snbt")
    if os.path.exists(data_file):
        for key in re.findall(r"^\t([a-z_]+):", open(data_file, encoding="utf-8").read(),
                              re.MULTILINE):
            if key not in known_keys:
                problems.append("data.snbt 里的键 %s 不是 FTB 字段（会被忽略）" % key)
    else:
        problems.append("缺少 data.snbt")

    print("任务章节：%d 个，任务 %d 条，前置 %d 条" % (len(chapters), len(quest_ids), len(deps)))
    graph = {qid: deps_by_quest.get(qid, []) for qid in quest_ids}
    cycles = cycle_check(graph, quest_ids)
    print("前置图环检测：%d 处环（有环 = 打开任务书会 StackOverflow 崩溃）" % len(cycles))
    for cyc in cycles[:5]:
        problems.append("前置图有环：%s" % " → ".join(cyc))
    recipe_logic_check(quest_targets, deps_by_quest, graph)
    for name, count, unique, stats in per_chapter:
        flag = "" if unique > 1 or count <= 1 else "  ← 坐标全挤在一起？"
        if stats:
            print("   %-18s %3d 条  横向 %5.1f 格  纵向 %5.1f 格  离中心 %4.1f 格  最大行距 %4.1f%s"
                  % (name, count, stats[0], stats[1], stats[3], stats[2], flag))
        else:
            print("   %-18s %3d 条%s" % (name, count, flag))

    if problems:
        print("任务书自检：发现问题 ❌")
        for p in problems[:20]:
            print("   -", p)
        sys.exit(1)
    print("任务书自检：通过 ✅（id 可解析 / 前置都能连上 / 引用都存在 / 坐标已铺开 / 章节已分组）")


if __name__ == "__main__":
    main()
