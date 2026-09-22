"""科举题库自检：结构 / 选项 / 答案 / 重复 / 档位门槛 / 上限 / 内置兜底。

判定标准只收紧不放松。这里的数字与 Java 加载器（`com.dynasty.keju.KejuRules`）
和网络包（`com.dynasty.keju.KejuNet` / `OpenKejuPacket`）必须完全一致，
脚本会直接读出 Java 里的常量来核对，避免两边各写一套：

  每档 10..200 题 / 最多 8 档 / 题库总 800 题 / 题干 ≤ 200 字 / 选项 ≤ 100 字 /
  每题正好 3 个互不相同的选项 / 答案必须是真的整数 1..3（不接受布尔或字符串）/
  档位 id 非空且唯一 / 中英名非空 / 门槛非负且严格递增（第一档必须是 0）/
  奖励功名为正整数 / 题干全库不重复。

用法：
  python3 tools/art/verify_keju.py                    # 校验正式题库
  python3 tools/art/verify_keju.py --bank <path>      # 校验任意题库（测试用临时输入）
"""
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_BANK = os.path.join(ROOT, "src/main/resources/data/dynasty/keju/questions.json")
JAVA_KEJU = os.path.join(ROOT, "src/main/java/com/dynasty/DynastyKeju.java")
JAVA_RULES = os.path.join(ROOT, "src/main/java/com/dynasty/keju/KejuRules.java")
JAVA_OPEN_PACKET = os.path.join(ROOT, "src/main/java/com/dynasty/network/OpenKejuPacket.java")

MIN_PER_TIER = 10
MAX_PER_TIER = 200
MAX_TIERS = 8
MAX_TOTAL_QUESTIONS = 800
MAX_QUESTION_CHARS = 200
MAX_OPTION_CHARS = 100
CHOICES = 3
FALLBACK_MIN = 7

# Java 侧同名常量（名字 -> 期望值），逐个核对，防止 Java / Python 判定漂移
JAVA_CONSTANTS = {
    "MIN_PER_TIER": MIN_PER_TIER,
    "MAX_PER_TIER": MAX_PER_TIER,
    "MAX_TIERS": MAX_TIERS,
    "MAX_TOTAL_QUESTIONS": MAX_TOTAL_QUESTIONS,
    "MAX_QUESTION_CHARS": MAX_QUESTION_CHARS,
    "MAX_OPTION_CHARS": MAX_OPTION_CHARS,
    "CHOICES": CHOICES,
    "FALLBACK_MIN_QUESTIONS": FALLBACK_MIN,
}


def is_int(value):
    """Python 的 bool 是 int 的子类，必须显式排除。"""
    return isinstance(value, int) and not isinstance(value, bool)


def as_text(value):
    return value if isinstance(value, str) else None


def check_java_constants(problems):
    if not os.path.exists(JAVA_RULES):
        problems.append("缺少 Java 规则类：%s" % JAVA_RULES)
        return
    text = open(JAVA_RULES, encoding="utf-8").read()
    for name, expected in sorted(JAVA_CONSTANTS.items()):
        match = re.search(r"public static final int %s\s*=\s*(\d+)\s*;" % name, text)
        if not match:
            problems.append("KejuRules.java 里找不到常量 %s（Java 与 Python 判定必须同源）" % name)
            continue
        actual = int(match.group(1))
        if actual != expected:
            problems.append("常量 %s 不一致：Java=%d，校验器=%d" % (name, actual, expected))
    if os.path.exists(JAVA_OPEN_PACKET):
        packet = open(JAVA_OPEN_PACKET, encoding="utf-8").read()
        if "KejuNet.MAX_QUESTION_CHARS" not in packet or "KejuNet.MAX_OPTION_CHARS" not in packet:
            problems.append("OpenKejuPacket.java 没有使用 KejuNet 的长度上限（网络与题库校验必须同源）")


def check_fallback(problems):
    """Java 内置兜底题库题数必须 ≥ 7（不能悄悄变少）。"""
    java = open(JAVA_KEJU, encoding="utf-8").read()
    block = re.search(r"FALLBACK\s*=\s*\{(.*?)\};", java, re.S)
    rows = re.findall(
        r'\{"[^"]+",\s*"[^"]+",\s*"[^"]+",\s*"[^"]+",\s*"[1-3]"\}', block.group(1)) if block else []
    if len(rows) < FALLBACK_MIN:
        problems.append("Java 兜底题库少于 %d 题（当前 %d）" % (FALLBACK_MIN, len(rows)))
    return len(rows)


def check_tier_fields(bank_path, ti, tier, seen_ids, state, problems):
    """档位字段检查：id / 中英名 / 门槛 / 奖励 / 题量。返回该档的定位字符串。"""
    where = "档位 #%d" % ti
    if not isinstance(tier, dict):
        problems.append("%s：%s：档位必须是 JSON 对象" % (bank_path, where))
        return where
    for key in ("id", "zh", "en", "minMerit", "merit", "questions"):
        if key not in tier:
            problems.append("%s：%s：缺少字段 %s" % (bank_path, where, key))
    tid = as_text(tier.get("id"))
    if tid is None or not tid.strip():
        problems.append("%s：%s：id 必须是非空字符串（不能是空白）" % (bank_path, where))
    elif tid in seen_ids:
        problems.append("%s：%s：id 与 %s 重复" % (bank_path, where, seen_ids[tid]))
    else:
        seen_ids[tid] = where
        where = "档位 #%d（id=%s）" % (ti, tid)
    for key, label in (("zh", "中文名"), ("en", "英文名")):
        value = as_text(tier.get(key))
        if value is None or not value.strip():
            problems.append("%s：%s：%s必须是非空字符串" % (bank_path, where, label))
    min_merit = tier.get("minMerit")
    if not is_int(min_merit):
        problems.append("%s：%s：minMerit 必须是整数（不接受字符串 / 布尔 / 小数）" % (bank_path, where))
    else:
        if min_merit < 0:
            problems.append("%s：%s：minMerit 不能为负：%s" % (bank_path, where, min_merit))
        if ti == 0 and min_merit != 0:
            problems.append("%s：%s：第一档 minMerit 必须是 0" % (bank_path, where))
        if state["last_min"] is not None and min_merit <= state["last_min"]:
            problems.append("%s：%s：minMerit 必须严格递增（%s 不大于上一档 %s）"
                            % (bank_path, where, min_merit, state["last_min"]))
        state["last_min"] = min_merit
    merit = tier.get("merit")
    if not is_int(merit):
        problems.append("%s：%s：merit 必须是整数（不接受字符串 / 布尔 / 小数）" % (bank_path, where))
    elif merit <= 0:
        problems.append("%s：%s：奖励功名必须为正整数：%s" % (bank_path, where, merit))
    questions = tier.get("questions")
    if not isinstance(questions, list):
        problems.append("%s：%s：questions 必须是数组" % (bank_path, where))
        return where
    if len(questions) < MIN_PER_TIER:
        problems.append("%s：%s：题目不足 %d 条（%d）" % (bank_path, where, MIN_PER_TIER, len(questions)))
    if len(questions) > MAX_PER_TIER:
        problems.append("%s：%s：题目过多（%d > %d）" % (bank_path, where, len(questions), MAX_PER_TIER))
    print("   %-14s %-6s 门槛 %-6s 功名 %-4s 题数 %d"
          % (tid or "?", as_text(tier.get("zh")) or "?", min_merit, merit, len(questions)))
    return where


def check_question(bank_path, where, qi, question, seen_texts, problems):
    """单题检查：题干 / 三个选项 / 答案（错类型、空白、重复、超长都报原因）。"""
    qwhere = "%s 题目 #%d" % (where, qi)
    if not isinstance(question, dict):
        problems.append("%s：%s：题目必须是 JSON 对象" % (bank_path, qwhere))
        return
    text = as_text(question.get("q"))
    if text is None:
        problems.append("%s：%s：题干必须是非空字符串" % (bank_path, qwhere))
    elif not text.strip():
        problems.append("%s：%s：题干不能是空白字符串" % (bank_path, qwhere))
    else:
        if len(text) > MAX_QUESTION_CHARS:
            problems.append("%s：%s：题干超长（%d > %d 字）"
                            % (bank_path, qwhere, len(text), MAX_QUESTION_CHARS))
        if text in seen_texts:
            problems.append("%s：%s：题干重复（与 %s 相同）" % (bank_path, qwhere, seen_texts[text]))
        else:
            seen_texts[text] = qwhere
    options = question.get("a")
    if not isinstance(options, list):
        problems.append("%s：%s：缺少 a 选项数组" % (bank_path, qwhere))
        options = []
    elif len(options) != CHOICES:
        problems.append("%s：%s：选项不是 %d 个（当前 %d，禁止截断 / 补足）"
                        % (bank_path, qwhere, CHOICES, len(options)))
    seen_options = set()
    for oi, option in enumerate(options):
        owhere = "%s 选项 #%d" % (qwhere, oi)
        if not isinstance(option, str) or not option.strip():
            problems.append("%s：%s：选项必须是非空字符串" % (bank_path, owhere))
            continue
        if len(option) > MAX_OPTION_CHARS:
            problems.append("%s：%s：选项超长（%d > %d 字）"
                            % (bank_path, owhere, len(option), MAX_OPTION_CHARS))
        if option in seen_options:
            problems.append("%s：%s：选项内有重复：%s" % (bank_path, owhere, option))
        seen_options.add(option)
    correct = question.get("correct")
    if not is_int(correct):
        problems.append("%s：%s：答案必须是整数 1..%d（不接受布尔 / 字符串 / 小数）"
                        % (bank_path, qwhere, CHOICES))
    elif correct < 1 or correct > CHOICES:
        problems.append("%s：%s：答案下标越界：%s（必须 1..%d）" % (bank_path, qwhere, correct, CHOICES))


def check_tiers(bank_path, tiers, problems):
    """逐档校验，返回题库总题数。"""
    seen_ids = {}
    seen_texts = {}
    state = {"last_min": None}
    total = 0
    for ti, tier in enumerate(tiers):
        where = check_tier_fields(bank_path, ti, tier, seen_ids, state, problems)
        questions = tier.get("questions") if isinstance(tier, dict) else None
        if not isinstance(questions, list):
            continue
        total += len(questions)
        for qi, question in enumerate(questions):
            check_question(bank_path, where, qi, question, seen_texts, problems)
    return total


def main(argv):
    bank_path = DEFAULT_BANK
    if "--bank" in argv:
        index = argv.index("--bank")
        if index + 1 >= len(argv):
            print("用法：verify_keju.py [--bank <题库路径>]")
            return 2
        bank_path = argv[index + 1]

    problems = []
    tiers = []
    total = 0
    if not os.path.exists(bank_path):
        problems.append("%s：题库文件缺失" % bank_path)
    else:
        raw = open(bank_path, encoding="utf-8").read()
        try:
            data = json.loads(raw)
        except ValueError as error:
            problems.append("%s：JSON 解析失败：%s" % (bank_path, error))
            data = None
        if data is not None:
            if not isinstance(data, dict) or "tiers" not in data:
                problems.append("%s：题库缺少 tiers 数组" % bank_path)
            elif not isinstance(data["tiers"], list) or not data["tiers"]:
                problems.append("%s：tiers 必须是非空数组" % bank_path)
            else:
                tiers = data["tiers"]
                if len(tiers) > MAX_TIERS:
                    problems.append("%s：档位过多（%d > %d）" % (bank_path, len(tiers), MAX_TIERS))
                total = check_tiers(bank_path, tiers, problems)
                if total == 0:
                    problems.append("%s：题库总题数为 0" % bank_path)
                elif total > MAX_TOTAL_QUESTIONS:
                    problems.append("%s：题库总题数过多（%d > %d）"
                                    % (bank_path, total, MAX_TOTAL_QUESTIONS))

    check_java_constants(problems)
    fallback_count = check_fallback(problems)

    print("科举题库：档位 %d 个，题目 %d 条，Java 兜底 %d 条" % (len(tiers), total, fallback_count))
    if problems:
        print("科举题库自检：失败 ❌（%s）" % bank_path)
        for problem in problems:
            print("   -", problem)
        return 1
    print("科举题库自检：通过 ✅（选项 %d 个 / 答案整数 1..%d / 无重复题干 / 门槛严格递增且首档为 0 / "
          "每档 %d..%d 题 / 题干 ≤ %d 字 / 选项 ≤ %d 字）"
          % (CHOICES, CHOICES, MIN_PER_TIER, MAX_PER_TIER, MAX_QUESTION_CHARS, MAX_OPTION_CHARS))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
