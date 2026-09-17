"""科举题库自检：结构 / 选项 / 答案 / 重复 / 档位门槛 / 内置兜底数量。

判定标准只收紧不放松：题里出现重复的题干、选项不够三个、答案下标越界、
档位门槛不是升序、单档题数不足 10、题库总数为 0 —— 任一都判失败。

用法：python3 tools/art/verify_keju.py
"""
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BANK = os.path.join(ROOT, "src/main/resources/data/dynasty/keju/questions.json")
JAVA = os.path.join(ROOT, "src/main/java/com/dynasty/DynastyKeju.java")

MIN_PER_TIER = 10
problems = []

with open(BANK, encoding="utf-8") as f:
    data = json.load(f)

tiers = data.get("tiers")
if not isinstance(tiers, list) or not tiers:
    problems.append("题库没有 tiers")
    tiers = []

seen_texts = {}
seen_ids = set()
last_min = -1
total = 0

for tier in tiers:
    for key in ("id", "zh", "en", "minMerit", "merit", "questions"):
        if key not in tier:
            problems.append("档位缺少字段 %s：%s" % (key, tier.get("id", "?")))
    tid = tier.get("id", "?")
    if tid in seen_ids:
        problems.append("档位 id 重复：%s" % tid)
    seen_ids.add(tid)
    min_merit = tier.get("minMerit", 0)
    if min_merit < last_min:
        problems.append("档位门槛不是升序：%s（%s < %s）" % (tid, min_merit, last_min))
    last_min = min_merit
    if tier.get("merit", 0) <= 0:
        problems.append("档位奖励功名必须为正：%s" % tid)
    questions = tier.get("questions", [])
    if len(questions) < MIN_PER_TIER:
        problems.append("档位题目不足 %d 条：%s（%d）" % (MIN_PER_TIER, tid, len(questions)))
    for q in questions:
        text = q.get("q", "")
        options = q.get("a", [])
        correct = q.get("correct", 0)
        if not text:
            problems.append("空题干（%s）" % tid)
        if text in seen_texts:
            problems.append("题干重复：%s（%s 与 %s）" % (text, tid, seen_texts[text]))
        seen_texts[text] = tid
        if len(options) != 3:
            problems.append("选项不是 3 个：%s" % text)
        elif len(set(options)) != 3:
            problems.append("选项内有重复：%s" % text)
        if not isinstance(correct, int) or correct < 1 or correct > 3:
            problems.append("答案下标越界：%s（%s）" % (text, correct))
        total += 1
    print("   %-14s %-6s 门槛 %-6s 功名 %-4s 题数 %d"
          % (tid, tier.get("zh", "?"), min_merit, tier.get("merit", 0), len(questions)))

# 内置兜底题库：数量必须与 Java 里的 FALLBACK 行数一致（不能悄悄变少）
java = open(JAVA, encoding="utf-8").read()
fallback_block = re.search(r"FALLBACK\s*=\s*\{(.*?)\};", java, re.S)
fallback_count = len(re.findall(r'\{"[^"]+",\s*"[^"]+",\s*"[^"]+",\s*"[^"]+",\s*"[1-3]"\}', fallback_block.group(1))) if fallback_block else 0
if fallback_count < 7:
    problems.append("Java 兜底题库少于 7 题（当前 %d）" % fallback_count)

print("科举题库：档位 %d 个，题目 %d 条，Java 兜底 %d 条" % (len(tiers), total, fallback_count))
if problems:
    print("科举题库自检：失败 ❌")
    for p in problems:
        print("   -", p)
    raise SystemExit(1)
print("科举题库自检：通过 ✅（选项 3 个 / 答案下标合法 / 无重复题干 / 门槛升序 / 每档 ≥ %d 题）" % MIN_PER_TIER)
