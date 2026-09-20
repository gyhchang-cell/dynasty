#!/usr/bin/env python3
"""王朝配方基础检查（只读）。规则来自 1.20.1 原版 + Forge 源码（本地已核对）：

  net/minecraft/world/item/crafting/ShapedRecipe.java        pattern/key/dissolvePattern/shrink
  net/minecraft/world/item/crafting/ShapelessRecipe.java     ingredients 非空、≤9
  net/minecraft/world/item/crafting/SimpleCookingSerializer  ingredient/result/experience/cookingtime
  net/minecraft/world/item/crafting/SingleItemRecipe.java    stonecutting：ingredient + result + count
  net/minecraft/world/item/crafting/Smithing*Recipe.java     template/base/addition(+result)
  net/minecraftforge/common/crafting/CraftingHelper.java     result 物品栈：item 必填、count 默认 1
  net/minecraftforge/common/crafting/ConditionalRecipe.java  forge:conditional：recipes[].recipe

检查内容（明确支持的类型才套用规则）：
  1. JSON 能否解析；
  2. 必要字段与类型（pattern/key/ingredients/ingredient/result/template/base/addition/count…）；
  3. 有序合成：图案 1~3 行、每行 ≤3 字符、各行等宽；图案里的字符必须都在 key 里；
     key 里的字符必须都被用到；key 的键必须恰好 1 个字符（UTF-16，与原版一致）；key 不能定义空格（原版保留符号）；
  4. 结果数量：`count` 必须 ≥1（<1 会得到空结果）；>64 只给警告（原版不报错但做不出可堆叠产物）；
  5. 内容完全相同、文件名不同的配方 → 标「可能重复」（只提示，不删除）；
  6. 自定义类型 / 特殊原版配方（crafting_special_*）/ 未知类型 → **明确跳过并写原因**；
     `forge:conditional` 会展开成内层配方继续按内层类型检查。

**不检查**：物品是否已注册（不靠文件名猜注册表）、配方平衡、产物强度。

用法：
    python3 tools/maintenance/check_recipes.py
    python3 tools/maintenance/check_recipes.py --root <路径> --data <相对 data 目录>
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import checklib  # noqa: E402  （同目录，路径基于脚本位置）

CRAFTING_MAX = 3 * 3           # ShapedRecipe.MAX_WIDTH * MAX_HEIGHT = 9
COUNT_WARN_ABOVE = 64          # 原版不报错，但 >64 的产物无法正常堆叠

SUPPORTED = {
    "minecraft:crafting_shaped": "有序合成",
    "minecraft:crafting_shapeless": "无序合成",
    "minecraft:smelting": "熔炼",
    "minecraft:blasting": "高炉",
    "minecraft:smoking": "烟熏",
    "minecraft:campfire_cooking": "营火",
    "minecraft:stonecutting": "切石机",
    "minecraft:smithing_transform": "锻造台（变换）",
    "minecraft:smithing_trim": "锻造台（纹饰）",
}
COOKING = {"minecraft:smelting", "minecraft:blasting",
           "minecraft:smoking", "minecraft:campfire_cooking"}
CONDITIONAL = "forge:conditional"


def utf16_len(text):
    """Java String.length() 的等价长度（非 BMP 字符按 2 算）。"""
    return len(text.encode("utf-16-le")) // 2


def is_ingredient(value):
    """Ingredient.fromJson 能接受：单个对象（item/tag/自定义）或对象数组。"""
    if isinstance(value, dict):
        return True
    if isinstance(value, list):
        return all(isinstance(entry, dict) for entry in value)
    return False


def describe_ingredient_emptiness(value):
    """返回空数组的说明（空数组 = 空 Ingredient，配方会被判为 incomplete）。"""
    if isinstance(value, list) and not value:
        return "是空数组（空 Ingredient → 配方会被判为 incomplete 并丢弃）"
    return None


def check_result_stack(path, field, result, report, allow_string=False, require_object=True):
    """检查 result。返回 True 表示格式可用。"""
    if isinstance(result, str):
        if allow_string:
            return True
        report.error(path, field, "result 必须是对象（含 item），这里是字符串 '%s'" % result)
        return False
    if not isinstance(result, dict):
        report.error(path, field, "result 必须是对象%s，这里是 %s"
                     % ("或字符串" if allow_string else "", type(result).__name__))
        return False
    if not isinstance(result.get("item"), str) or not result.get("item"):
        report.error(path, field + ".item", "缺少 item 字段（或不是字符串）：%r" % (result.get("item"),))
        return False
    return check_count(path, field + ".count", result.get("count", 1), report)


def check_count(path, field, count, report):
    if isinstance(count, bool) or not isinstance(count, int):
        report.error(path, field, "必须是整数，这里是 %r" % (count,))
        return False
    if count < 1:
        report.error(path, field, "必须 ≥1（<1 会得到空结果），这里是 %d" % count)
        return False
    if count > COUNT_WARN_ABOVE:
        report.warning(path, field, "超过 64（原版不报错，但产物无法正常堆叠）：%d" % count)
    return True


def check_ingredient(path, field, value, report, allow_empty_array=False):
    if not is_ingredient(value):
        report.error(path, field, "必须是物品对象（item/tag）或物品对象数组，这里是 %s"
                     % type(value).__name__)
        return
    empty = describe_ingredient_emptiness(value)
    if empty:
        if allow_empty_array:
            report.warning(path, field, empty)
        else:
            report.error(path, field, "空数组：原版会抛 'Item array cannot be empty, at least one item must be defined'")



def check_shaped(path, data, report):
    pattern = data.get("pattern")
    if not isinstance(pattern, list) or not pattern:
        report.error(path, "pattern", "必须是非空字符串数组（原版：'Invalid pattern: empty pattern not allowed'）")
        pattern = []
    elif len(pattern) > 3:
        report.error(path, "pattern", "行数超过 3（原版：'too many rows, 3 is maximum'）：%d 行" % len(pattern))
    width = None
    for i, row in enumerate(pattern):
        field = "pattern[%d]" % i
        if not isinstance(row, str):
            report.error(path, field, "必须是字符串，这里是 %s" % type(row).__name__)
            continue
        if utf16_len(row) > 3:
            report.error(path, field, "每行最多 3 个字符（原版：'too many columns, 3 is maximum'）：%r" % row)
        if width is None:
            width = utf16_len(row)
        elif utf16_len(row) != width:
            report.error(path, field, "各行必须等宽（原版：'each row must be the same width'）："
                                      "%r 宽 %d，首行宽 %d" % (row, utf16_len(row), width))

    key = data.get("key")
    used = set()
    for row in pattern:
        if isinstance(row, str):
            used.update(ch for ch in row if ch != " ")
    if not isinstance(key, dict) or not key:
        report.error(path, "key", "必须是对象（字符 → 物品对象）")
    else:
        for symbol, value in key.items():
            field = "key['%s']" % symbol
            if utf16_len(symbol) != 1:
                report.error(path, field, "键必须恰好 1 个字符（原版：'must be 1 character only'）")
            if symbol == " ":
                report.error(path, field, "空格是原版保留符号，不能写进 key（原版：'is a reserved symbol'）")
                continue
            if symbol not in used:
                report.error(path, field, "key 定义了图案里没用到的字符（原版："
                                          "'Key defines symbols that aren't used in pattern'）")
            check_ingredient(path, field, value, report)
    for symbol in sorted(used):
        if isinstance(key, dict) and symbol not in key:
            report.error(path, "pattern", "图案引用了未在 key 中定义的字符 '%s'（原版："
                                          "'Pattern references symbol ... but it's not defined in the key'）"
                         % symbol)
    if "result" not in data:
        report.error(path, "result", "缺少 result")
    else:
        check_result_stack(path, "result", data["result"], report)


def check_shapeless(path, data, report):
    ingredients = data.get("ingredients")
    if not isinstance(ingredients, list) or not ingredients:
        report.error(path, "ingredients", "必须是非空数组（原版：'No ingredients for shapeless recipe'）")
    elif len(ingredients) > CRAFTING_MAX:
        report.error(path, "ingredients", "最多 9 个原料（原版：'Too many ingredients ... maximum is 9'）：%d 个"
                     % len(ingredients))
    else:
        for i, value in enumerate(ingredients):
            check_ingredient(path, "ingredients[%d]" % i, value, report, allow_empty_array=True)
    if "result" not in data:
        report.error(path, "result", "缺少 result")
    else:
        check_result_stack(path, "result", data["result"], report)



def check_cooking(path, data, report):
    if "ingredient" not in data:
        report.error(path, "ingredient", "缺少 ingredient")
    else:
        check_ingredient(path, "ingredient", data["ingredient"], report)
    if "result" not in data:
        report.error(path, "result", "缺少 result（字符串或含 item 的对象）")
    else:
        check_result_stack(path, "result", data["result"], report, allow_string=True)
    experience = data.get("experience", 0)
    if isinstance(experience, bool) or not isinstance(experience, (int, float)):
        report.error(path, "experience", "必须是数字，这里是 %r" % (experience,))
    elif experience < 0:
        report.warning(path, "experience", "负数经验（原版不报错，但语义可疑）：%r" % experience)
    cooking_time = data.get("cookingtime")
    if cooking_time is not None:
        if isinstance(cooking_time, bool) or not isinstance(cooking_time, int):
            report.error(path, "cookingtime", "必须是整数，这里是 %r" % (cooking_time,))
        elif cooking_time <= 0:
            report.warning(path, "cookingtime", "≤0 会瞬间完成（原版默认 200/100/200）：%d" % cooking_time)


def check_stonecutting(path, data, report):
    if "ingredient" not in data:
        report.error(path, "ingredient", "缺少 ingredient")
    else:
        check_ingredient(path, "ingredient", data["ingredient"], report)
    result = data.get("result")
    if isinstance(result, str):
        pass
    elif isinstance(result, dict):
        report.warning(path, "result", "切石机原版读取的是字符串 result；这里是对象，请确认所用版本的行为")
    else:
        report.error(path, "result", "缺少 result（原版要求字符串）")
    if "count" not in data:
        report.error(path, "count", "缺少 count（原版 SingleItemRecipe 必填）")
    else:
        check_count(path, "count", data["count"], report)


def check_smithing(path, data, report, needs_result):
    for field in ("template", "base", "addition"):
        if field not in data:
            report.error(path, field, "缺少 %s（原版 GsonHelper.getNonNull 会直接抛错）" % field)
        else:
            check_ingredient(path, field, data[field], report)
    if needs_result:
        if "result" not in data:
            report.error(path, "result", "缺少 result")
        else:
            check_result_stack(path, "result", data["result"], report)


def check_one(path, data, report):
    """按类型检查一条配方；返回类型字符串（用于统计）。path 可以是 `文件#recipes[0].recipe`。"""
    if not isinstance(data, dict):
        report.error(path, "type", "配方必须是对象，这里是 %s" % type(data).__name__)
        return "<非对象>"
    recipe_type = data.get("type")
    if not isinstance(recipe_type, str) or not recipe_type:
        report.error(path, "type", "缺少 type 字段")
        return "<无类型>"
    if recipe_type == CONDITIONAL:
        check_conditional(path, data, report)
        return recipe_type
    if recipe_type not in SUPPORTED:
        if recipe_type.startswith("minecraft:crafting_special"):
            report.skip(path, "type", "特殊配方（%s，CustomRecipe 子类，普通合成规则不适用）" % recipe_type)
        else:
            report.skip(path, "type",
                        "不支持的配方类型 %s（自定义/其他模组规则，本工具不套用原版规则）" % recipe_type)
        return recipe_type
    if recipe_type == "minecraft:crafting_shaped":
        check_shaped(path, data, report)
    elif recipe_type == "minecraft:crafting_shapeless":
        check_shapeless(path, data, report)
    elif recipe_type in COOKING:
        check_cooking(path, data, report)
    elif recipe_type == "minecraft:stonecutting":
        check_stonecutting(path, data, report)
    elif recipe_type == "minecraft:smithing_transform":
        check_smithing(path, data, report, needs_result=True)
    elif recipe_type == "minecraft:smithing_trim":
        check_smithing(path, data, report, needs_result=False)
    return recipe_type


def check_conditional(path, data, report):
    """forge:conditional：{"recipes":[{"conditions":[...],"recipe":{...}}]} → 展开内层配方。"""
    recipes = data.get("recipes")
    if not isinstance(recipes, list) or not recipes:
        report.error(path, "recipes", "forge:conditional 必须带非空 recipes 数组（每项含 conditions + recipe）")
        return
    for i, entry in enumerate(recipes):
        field = "recipes[%d]" % i
        if not isinstance(entry, dict):
            report.error(path, field, "每项必须是对象")
            continue
        if "conditions" in entry and not isinstance(entry["conditions"], list):
            report.error(path, field + ".conditions", "必须是数组")
        inner = entry.get("recipe")
        if not isinstance(inner, dict):
            report.error(path, field + ".recipe", "缺少 recipe 对象（Forge 从这里取内层配方）")
            continue
        report.bump("条件配方展开")
        check_one("%s#%s.recipe" % (path, field), inner, report)



def canonical(data):
    """规范化 JSON 文本，用于「内容完全相同」判定（键顺序无关）。"""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def scan(root, data_dir="src/main/resources/data", report=None):
    report = report or checklib.Report("recipes", "配方")
    base = os.path.join(root, data_dir)
    if not os.path.isdir(base):
        report.error(data_dir, "(目录)", "找不到数据目录：%s" % base)
        return report
    seen = {}
    for namespace in sorted(os.listdir(base)):
        recipes_dir = os.path.join(base, namespace, "recipes")
        if not os.path.isdir(recipes_dir):
            continue
        for path in checklib.iter_json_files(recipes_dir):
            rel = checklib.relpath(root, path)
            report.files_checked += 1
            data = checklib.load_json(root, path, report, "type")
            if data is None:
                continue
            recipe_type = check_one(rel, data, report)
            report.bump("类型：%s" % recipe_type)
            if isinstance(data, dict):
                seen.setdefault(canonical(data), []).append(rel)

    for content, files in sorted(seen.items(), key=lambda item: item[1][0]):
        if len(files) > 1:
            for other in files:
                others = [f for f in files if f != other]
                report.warning(other, "(整体)", "与 %s 内容完全相同（可能重复；本工具不删除文件）"
                               % "、".join(others))
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description="王朝配方基础检查（只读）")
    parser.add_argument("--root", default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")),
                        help="仓库根目录（默认脚本上两级）")
    parser.add_argument("--data", default="src/main/resources/data",
                        help="相对仓库根的 data 目录")
    args = parser.parse_args(argv)
    report = scan(args.root, args.data)
    print(report.summary_line())
    report.print_issues()
    if report.errors:
        print("配方自检：发现 %d 个确定错误、%d 个警告、%d 个跳过 ❌（退出码 1）"
              % (len(report.errors), len(report.warnings), len(report.skips)))
        return 1
    print("配方自检：通过 ✅（%d 个警告、%d 个跳过均不是确定错误）"
          % (len(report.warnings), len(report.skips)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
