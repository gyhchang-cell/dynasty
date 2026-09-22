"""用临时题库压正式校验器：非法输入必须报出原因，不能抛 traceback 或静默修正。

被测对象是生产脚本 `tools/art/verify_keju.py`（用 `--bank` 指向临时文件），
不是另写一份校验逻辑；临时文件都放在临时目录里，绝不碰正式题库。

用法：python3 tools/keju/test_verify_keju.py
"""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
VERIFIER = os.path.join(ROOT, "tools/art/verify_keju.py")

passed = 0
failures = []


def question(text, options=("甲", "乙", "丙"), correct=1):
    return {"q": text, "a": list(options), "correct": correct}


def tier(tid="county", zh="县试", en="County", min_merit=0, merit=12, questions=None):
    return {"id": tid, "zh": zh, "en": en, "minMerit": min_merit, "merit": merit,
            "questions": questions if questions is not None else
            [question("%s 第 %d 题" % (tid, i)) for i in range(10)]}


def valid_bank():
    return {"tiers": [tier("county", "县试", "County", 0, 12),
                      tier("metropolitan", "会试", "Metropolitan", 400, 25),
                      tier("palace", "殿试", "Palace", 1600, 45)]}


def run_case(name, payload, expect_code, needles):
    """payload 可以是 dict（写成 JSON）、字符串（原样写入造坏 JSON）或 None（造缺文件）。"""
    global passed
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "questions.json")
        if isinstance(payload, str):
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(payload)
        elif payload is None:
            path = os.path.join(tmp, "missing.json")
        else:
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False)
        proc = subprocess.run([sys.executable, VERIFIER, "--bank", path],
                              capture_output=True, text=True)
        out = (proc.stdout or "") + (proc.stderr or "")
        problems = []
        if "Traceback" in out:
            problems.append("出现 traceback")
        if proc.returncode != expect_code:
            problems.append("退出码 %d（期望 %d）" % (proc.returncode, expect_code))
        for needle in needles:
            if needle not in out:
                problems.append("输出里没有 %r" % needle)
        if problems:
            failures.append("%s —— %s\n%s" % (name, "；".join(problems), out.strip()))
        else:
            passed += 1


def main():
    global passed
    # 正式题库基线（3 档 / 45 题 / 7 条兜底）必须仍然通过
    real = subprocess.run([sys.executable, VERIFIER], capture_output=True, text=True)
    real_out = (real.stdout or "") + (real.stderr or "")
    if real.returncode == 0 and "档位 3 个，题目 45 条，Java 兜底 7 条" in real_out:
        passed += 1
    else:
        failures.append("正式题库基线 —— 期望 3 档 / 45 题 / 7 条兜底且通过\n%s" % real_out.strip())

    run_case("合法题库通过", valid_bank(), 0, ["通过 ✅"])
    run_case("缺文件", None, 1, ["题库文件缺失"])
    run_case("损坏 JSON", "{\"tiers\":[{\"id\":\"a\",", 1, ["JSON 解析失败"])
    run_case("根节点不是对象", "[]", 1, ["缺少 tiers 数组"])
    run_case("tiers 为空数组", {"tiers": []}, 1, ["tiers 必须是非空数组"])

    too_few = valid_bank()
    too_few["tiers"][0]["questions"] = [question("只有 9 题 %d" % i) for i in range(9)]
    run_case("每档少于 10 题", too_few, 1, ["题目不足 10 条"])

    too_many = valid_bank()
    too_many["tiers"][0]["questions"] = [question("太多 %d" % i) for i in range(201)]
    run_case("单档多于 200 题", too_many, 1, ["题目过多"])

    many_tiers = {"tiers": [tier("t%d" % i, "档%d" % i, "T%d" % i, 0 if i == 0 else i * 10, 5)
                            for i in range(9)]}
    run_case("档位多于 8 档", many_tiers, 1, ["档位过多"])

    four = valid_bank()
    four["tiers"][0]["questions"][0] = question("四选项", ("甲", "乙", "丙", "丁"))
    run_case("第四个选项", four, 1, ["选项不是 3 个"])

    dup_options = valid_bank()
    dup_options["tiers"][0]["questions"][0] = question("重复选项", ("甲", "甲", "丙"))
    run_case("选项重复", dup_options, 1, ["选项内有重复"])

    for value, label in ((0, "答案 0"), (4, "答案 4"), (True, "答案 true"),
                         ("1", "答案是字符串"), (1.5, "答案是小数")):
        bank = valid_bank()
        bank["tiers"][0]["questions"][0] = question("坏答案", correct=value)
        expect = ["答案下标越界"] if isinstance(value, int) and not isinstance(value, bool) else ["答案必须是整数"]
        run_case(label, bank, 1, expect)

    descending = valid_bank()
    descending["tiers"][2]["minMerit"] = 100
    run_case("门槛倒序", descending, 1, ["严格递增"])

    equal = valid_bank()
    equal["tiers"][1]["minMerit"] = 0
    run_case("门槛相等", equal, 1, ["严格递增"])

    not_zero = valid_bank()
    not_zero["tiers"][0]["minMerit"] = 10
    run_case("第一档门槛不是 0", not_zero, 1, ["第一档 minMerit 必须是 0"])

    string_min = valid_bank()
    string_min["tiers"][0]["minMerit"] = "0"
    run_case("minMerit 是字符串", string_min, 1, ["minMerit 必须是整数"])

    bool_min = valid_bank()
    bool_min["tiers"][0]["minMerit"] = True
    run_case("minMerit 是布尔", bool_min, 1, ["minMerit 必须是整数"])

    zero_merit = valid_bank()
    zero_merit["tiers"][0]["merit"] = 0
    run_case("奖励功名为 0", zero_merit, 1, ["奖励功名必须为正整数"])

    dup_id = valid_bank()
    dup_id["tiers"][1]["id"] = "county"
    run_case("档位 id 重复", dup_id, 1, ["id 与", "重复"])

    empty_id = valid_bank()
    empty_id["tiers"][0]["id"] = ""
    run_case("档位 id 为空", empty_id, 1, ["id 必须是非空字符串"])

    blank_zh = valid_bank()
    blank_zh["tiers"][0]["zh"] = "   "
    run_case("中文名为空白", blank_zh, 1, ["中文名必须是非空字符串"])

    blank_question = valid_bank()
    blank_question["tiers"][0]["questions"][0] = question("")
    run_case("空题干", blank_question, 1, ["题干不能是空白字符串"])

    numeric_question = valid_bank()
    numeric_question["tiers"][0]["questions"][0] = {"q": 123, "a": ["甲", "乙", "丙"], "correct": 1}
    run_case("题干不是字符串", numeric_question, 1, ["题干必须是非空字符串"])

    space_question = valid_bank()
    space_question["tiers"][0]["questions"][0] = question("    ")
    run_case("空白题干", space_question, 1, ["题干不能是空白字符串"])

    dup_question = valid_bank()
    dup_question["tiers"][1]["questions"][0] = question("county 第 0 题")
    run_case("题干重复", dup_question, 1, ["题干重复"])

    long_question = valid_bank()
    long_question["tiers"][0]["questions"][0] = question("长" * 201)
    run_case("题干超长", long_question, 1, ["题干超长"])

    long_option = valid_bank()
    long_option["tiers"][0]["questions"][0] = question("选项超长", ("甲" * 101, "乙", "丙"))
    run_case("选项超长", long_option, 1, ["选项超长"])

    missing_correct = valid_bank()
    missing_correct["tiers"][0]["questions"][0] = {"q": "缺答案", "a": ["甲", "乙", "丙"]}
    run_case("缺少 correct", missing_correct, 1, ["答案必须是整数"])

    print()
    if failures:
        print("通过 %d 项，失败 %d 项" % (passed, len(failures)))
        for failure in failures:
            print("  ❌ %s" % failure)
        return 1
    print("通过 %d 项，失败 0 项" % passed)
    print("✅ 科举校验器（正式题库基线 + 临时坏题库）全部符合预期")
    return 0


if __name__ == "__main__":
    sys.exit(main())
