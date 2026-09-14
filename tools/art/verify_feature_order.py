"""复刻原版 FeatureSorter 的排序检查，定位「特征顺序成环」。

原版算法（net.minecraft.world.level.biome.FeatureSorter#buildFeaturesPerStep）：
  1. 给每个 PlacedFeature 分配一个「全局首次出现序号」；
  2. 把一个生物群系的 features（11 个 stage 拍平）变成 (stage, 序号) 列表；
  3. **只给列表里相邻的两个特征加一条边**：前者必须在后者之前生成；
  4. 对整张图做 DFS；发现环 → `Feature order cycle found` → **生成区块时直接崩**。

我们踩过：把建筑特征加进 jade_forest / celestial_plains 之后成环了。

运行：python3 tools/art/verify_feature_order.py
"""
import glob
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BIOME_DIR = os.path.join(ROOT, "src/main/resources/data/dynasty/worldgen/biome")
STAGES = 11


def load_biomes():
    biomes = {}
    for path in sorted(glob.glob(os.path.join(BIOME_DIR, "*.json"))):
        biomes[os.path.basename(path)[:-5]] = json.load(open(path, encoding="utf-8"))
    return biomes


def build_graph(biomes):
    """返回 (graph, entries, index)：graph 的 key 是 (stage, 全局序号)。"""
    index, entries = {}, []
    for name in sorted(biomes):
        flat = []
        for stage, features in enumerate(biomes[name].get("features", [])):
            for feature in features:
                if feature not in index:
                    index[feature] = len(index)
                flat.append((stage, index[feature]))
        entries.append((name, flat))
    graph = {}
    for _name, flat in entries:
        for first, second in zip(flat, flat[1:]):     # 只连相邻两个（和原版一致）
            graph.setdefault(first, set()).add(second)
    return graph, entries, index


def find_cycle(graph):
    """DFS 找出一条真实的环（对应原版 Graph.depthFirstSearch）。"""
    state, path, found = {}, [], []

    def visit(node):
        state[node] = 1
        path.append(node)
        for nxt in sorted(graph.get(node, ())):
            if state.get(nxt) == 1:
                found.append(path[path.index(nxt):] + [nxt])
                return True
            if state.get(nxt, 0) == 0 and visit(nxt):
                return True
        path.pop()
        state[node] = 2
        return False

    for node in sorted(graph):
        if state.get(node, 0) == 0 and visit(node):
            return found[0]
    return None


def main():
    biomes = load_biomes()
    graph, entries, index = build_graph(biomes)
    reverse = {value: key for key, value in index.items()}
    problems = []

    for name, data in biomes.items():
        steps = data.get("features", [])
        if len(steps) != STAGES:
            problems.append("biome/%s.json：features 应该有 %d 个 stage，实际 %d"
                            % (name, STAGES, len(steps)))
        flat = [feature for step in steps for feature in step]
        repeated = sorted({feature for feature in flat if flat.count(feature) > 1})
        if repeated:
            # 原版自己的下界生物群系也会重复（patch_fire 在两个 stage 里），
            # 只要不成环就没问题，所以这里只提示不报错。
            print("   ⚠ %s：同一特征出现多次（原版也这样，只要不成环就行）：%s"
                  % (name, ", ".join(repeated)))

    cycle = find_cycle(graph)
    print("特征顺序检查：生物群系 %d 个，特征 %d 种，连边 %d 条"
          % (len(biomes), len(index), sum(len(value) for value in graph.values())))
    if cycle:
        names = " → ".join(reverse.get(node, str(node)) for node in cycle)
        problems.append("特征顺序成环（生成区块必崩）：%s" % names)
        for node in cycle:
            where = []
            for name, flat in entries:
                stages = sorted({stage for stage, gid in flat if gid == node})
                if stages:
                    where.append("%s(stage %s)" % (name, ",".join(str(s) for s in stages)))
            print("   %-34s %s" % (reverse.get(node, node), " / ".join(where)))

    if problems:
        print("特征顺序检查：发现问题 ❌")
        for problem in problems[:10]:
            print("   -", problem)
        sys.exit(1)
    print("特征顺序检查：通过 ✅（不会出现 Feature order cycle）")


if __name__ == "__main__":
    main()
