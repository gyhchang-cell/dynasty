#!/usr/bin/env python3
"""tools/maintenance 检查工具的单元测试（标准库 unittest）。

原则：**只在临时目录里构造样本**，绝不读写真实项目资源；
每个用例都有实际断言（错误/警告/跳过/退出码/JSON 报告结构），不为凑数重复同一断言。

运行：
    python3 tools/maintenance/test_maintenance_checks.py
    python3 -m unittest discover -s tools/maintenance -p 'test_*.py'
"""
import importlib.util
import json
import os
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def load_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, filename))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


resources = load_module("check_resources", "check_resources.py")
translations = load_module("check_translations", "check_translations.py")
recipes = load_module("check_recipes", "check_recipes.py")
runner = load_module("check_all", "check_all.py")


def texts(issues):
    """Issue 列表 → ["path [field]: message", ...]，方便断言可定位性。"""
    return ["%s [%s]: %s" % (i.path, i.field, i.message) for i in issues]


def joined(issues):
    return "\n".join(texts(issues))


class TempRepo:
    """在临时目录里搭一个最小仓库骨架。"""

    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = self._tmp.name

    def close(self):
        self._tmp.cleanup()

    def write_text(self, rel, text):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
        return path

    def write_json(self, rel, data):
        return self.write_text(rel, json.dumps(data, ensure_ascii=False, indent=2))

    def model(self, name, data, kind="item"):
        return self.write_json("src/main/resources/assets/dynasty/models/%s/%s.json" % (kind, name), data)

    def texture(self, name, kind="item"):
        return self.write_text(
            "src/main/resources/assets/dynasty/textures/%s/%s.png" % (kind, name), "png")

    def blockstate(self, name, data):
        return self.write_json("src/main/resources/assets/dynasty/blockstates/%s.json" % name, data)

    def lang(self, language, data):
        return self.write_json(
            "src/main/resources/assets/dynasty/lang/%s.json" % language, data)

    def lang_raw(self, language, text):
        return self.write_text(
            "src/main/resources/assets/dynasty/lang/%s.json" % language, text)

    def recipe(self, name, data):
        return self.write_json("src/main/resources/data/dynasty/recipes/%s.json" % name, data)

    def recipe_raw(self, name, text):
        return self.write_text("src/main/resources/data/dynasty/recipes/%s.json" % name, text)


class ResourceCheckTest(unittest.TestCase):
    """资源引用：继承 / #变量 / 外部命名空间 / 缺贴图 / 循环引用 / blockstate / overrides。"""

    def setUp(self):
        self.repo = TempRepo()
        self.addCleanup(self.repo.close)

    def check(self):
        return resources.check(self.repo.root)

    def test_inheritance_resolves_texture_variable(self):
        self.repo.model("base", {"parent": "minecraft:block/cube",
                                 "textures": {"all": "dynasty:block/base_tex"}}, kind="block")
        self.repo.texture("base_tex", kind="block")
        self.repo.model("child", {"parent": "dynasty:block/base", "textures": {"particle": "#all"}})
        self.assertEqual(self.check().errors, [])

    def test_texture_variable_missing_in_local_chain_is_error(self):
        self.repo.model("base", {"textures": {"layer0": "dynasty:item/base_tex"}})
        self.repo.texture("base_tex")
        self.repo.model("child", {"parent": "dynasty:item/base", "textures": {"layer0": "#ghost"}})
        self.assertIn("#ghost", joined(self.check().errors))

    def test_texture_variable_via_external_parent_is_warning(self):
        self.repo.model("base", {"parent": "minecraft:item/generated",
                                 "textures": {"layer0": "dynasty:item/base_tex"}})
        self.repo.texture("base_tex")
        self.repo.model("child", {"parent": "dynasty:item/base", "textures": {"layer0": "#ghost"}})
        report = self.check()
        self.assertEqual(report.errors, [])
        self.assertIn("#ghost", joined(report.warnings))

    def test_external_namespace_texture_is_not_local_missing(self):
        self.repo.model("vanilla_ref", {"parent": "item/generated",
                                        "textures": {"layer0": "minecraft:item/apple"}})
        report = self.check()
        self.assertEqual(report.errors, [])
        self.assertGreaterEqual(report.details.get("外部贴图引用", 0), 1)

    def test_missing_local_texture_is_error(self):
        self.repo.model("broken", {"parent": "item/generated",
                                   "textures": {"layer0": "dynasty:item/nope"}})
        self.assertIn("textures/item/nope.png", joined(self.check().errors))

    def test_missing_local_parent_is_error(self):
        self.repo.model("orphan", {"parent": "dynasty:block/does_not_exist"})
        self.assertIn("does_not_exist", joined(self.check().errors))

    def test_missing_assets_dir_is_error(self):
        report = self.check()
        self.assertTrue(any(i.field == "(目录)" for i in report.errors))

    def test_invalid_json_is_error(self):
        self.repo.write_text("src/main/resources/assets/dynasty/models/item/bad.json", "{not json")
        self.assertIn("JSON 解析失败", joined(self.check().errors))

    def test_parent_cycle_is_error(self):
        self.repo.model("a", {"parent": "dynasty:item/b"})
        self.repo.model("b", {"parent": "dynasty:item/a"})
        self.assertIn("循环引用", joined(self.check().errors))

    def test_self_parent_cycle_is_error(self):
        self.repo.model("self", {"parent": "dynasty:item/self"})
        self.assertIn("循环引用", joined(self.check().errors))

    def test_chain_through_external_parent_is_not_cycle(self):
        self.repo.model("a", {"parent": "dynasty:item/b"})
        self.repo.model("b", {"parent": "minecraft:item/generated"})
        self.assertEqual(self.check().errors, [])

    def test_overrides_missing_local_model_is_error(self):
        self.repo.texture("bow")
        self.repo.model("bow", {"parent": "item/generated",
                                "textures": {"layer0": "dynasty:item/bow"},
                                "overrides": [{"predicate": {"pulling": 1},
                                               "model": "dynasty:item/bow_pulling_0"}]})
        self.assertIn("bow_pulling_0", joined(self.check().errors))

    def test_overrides_external_model_is_ignored(self):
        self.repo.model("bow", {"parent": "item/generated",
                                "textures": {"layer0": "minecraft:item/bow"},
                                "overrides": [{"predicate": {"pulling": 1},
                                               "model": "minecraft:item/bow_pulling_0"}]})
        report = self.check()
        self.assertEqual(report.errors, [])
        self.assertGreaterEqual(report.details.get("外部 overrides 引用", 0), 1)

    def test_blockstate_missing_local_model_is_error(self):
        self.repo.blockstate("widget", {"variants": {"": {"model": "dynasty:block/widget"}}})
        self.assertIn("blockstates/widget.json", joined(self.check().errors))

    def test_blockstate_multipart_missing_model_is_error(self):
        self.repo.blockstate("lamp", {"multipart": [
            {"apply": {"model": "dynasty:block/lamp_on"}},
            {"apply": [{"model": "minecraft:block/torch"}]}]})
        errors = joined(self.check().errors)
        self.assertIn("lamp_on", errors)
        self.assertIn("multipart[0]", errors)

    def test_clean_tree_exit_zero_and_broken_tree_exit_one(self):
        self.repo.model("ok", {"parent": "item/generated",
                               "textures": {"layer0": "dynasty:item/ok"}})
        self.repo.texture("ok")
        self.assertEqual(resources.main(["--root", self.repo.root]), 0)
        self.repo.model("bad", {"parent": "item/generated",
                                "textures": {"layer0": "dynasty:item/gone"}})
        self.assertEqual(resources.main(["--root", self.repo.root]), 1)


class TranslationCheckTest(unittest.TestCase):
    """语言：解析 / 重复键 / 空译文 / 键集合 / 占位符 / 可定位性。"""

    def setUp(self):
        self.repo = TempRepo()
        self.addCleanup(self.repo.close)

    def check(self):
        return translations.check(self.repo.root)

    def test_clean_pair_passes(self):
        self.repo.lang("zh_cn", {"item.dynasty.a": "甲", "item.dynasty.b": "%s 打 %s"})
        self.repo.lang("en_us", {"item.dynasty.a": "A", "item.dynasty.b": "%s hits %s"})
        self.assertEqual(self.check().errors, [])

    def test_duplicate_key_is_error_not_silently_overwritten(self):
        self.repo.lang_raw("zh_cn", '{"dup": "第一次", "dup": "第二次"}')
        self.repo.lang("en_us", {"dup": "x"})
        errors = joined(self.check().errors)
        self.assertIn("重复键", errors)
        self.assertIn("zh_cn.json", errors)

    def test_blank_translation_is_error(self):
        self.repo.lang("zh_cn", {"item.dynasty.a": "   "})
        self.repo.lang("en_us", {"item.dynasty.a": "A"})
        self.assertIn("空白译文", joined(self.check().errors))

    def test_key_set_difference_both_directions(self):
        self.repo.lang("zh_cn", {"only.zh": "只有中文"})
        self.repo.lang("en_us", {"only.en": "only english"})
        errors = joined(self.check().errors)
        self.assertIn("only.zh", errors)
        self.assertIn("only.en", errors)

    def test_missing_language_file_is_error(self):
        self.repo.lang("zh_cn", {"a": "甲"})
        self.assertIn("语言文件不存在", joined(self.check().errors))

    def test_non_string_value_is_error(self):
        self.repo.lang("zh_cn", {"a": 123})
        self.repo.lang("en_us", {"a": "A"})
        self.assertIn("必须是字符串", joined(self.check().errors))

    def test_placeholder_type_mismatch(self):
        self.repo.lang("zh_cn", {"k": "%s 打了 %d 下"})
        self.repo.lang("en_us", {"k": "%s hit %s times"})
        self.assertIn("占位符不兼容", joined(self.check().errors))

    def test_placeholder_count_mismatch(self):
        self.repo.lang("zh_cn", {"k": "%1$s 被击败"})
        self.repo.lang("en_us", {"k": "%1$s was slain by %2$s"})
        self.assertIn("占位符不兼容", joined(self.check().errors))

    def test_placeholder_reorder_is_compatible(self):
        self.repo.lang("zh_cn", {"k": "%2$s 召来的青龙击败了 %1$s"})
        self.repo.lang("en_us", {"k": "%1$s was slain by %2$s's dragon"})
        self.assertEqual(self.check().errors, [])

    def test_escaped_percent_is_not_placeholder(self):
        self.repo.lang("zh_cn", {"k": "暴击率 100%%"})
        self.repo.lang("en_us", {"k": "Crit chance 100%%"})
        self.assertEqual(self.check().errors, [])

    def test_mixed_indexed_and_plain_is_warning(self):
        self.repo.lang("zh_cn", {"k": "%1$s 与 %s"})
        self.repo.lang("en_us", {"k": "%1$s and %s"})
        self.assertIn("混用", joined(self.check().warnings))

    def test_invalid_json_is_error(self):
        self.repo.lang_raw("zh_cn", "{oops")
        self.repo.lang("en_us", {})
        self.assertIn("JSON 解析失败", joined(self.check().errors))

    def test_issue_carries_path_and_field_and_exit_code(self):
        self.repo.lang("zh_cn", {"item.dynasty.x": ""})
        self.repo.lang("en_us", {"item.dynasty.x": "X"})
        report = self.check()
        self.assertTrue(all(i.path.endswith(".json") and i.field for i in report.errors))
        self.assertEqual(translations.main(["--root", self.repo.root]), 1)


class RecipeCheckTest(unittest.TestCase):
    """配方：必要字段 / 有序图案 / 结果数量 / 重复 / 不支持类型 / 条件包装。"""

    def setUp(self):
        self.repo = TempRepo()
        self.addCleanup(self.repo.close)

    def scan(self):
        return recipes.scan(self.repo.root)

    def test_valid_shaped_recipe_passes(self):
        self.repo.recipe("ok", {"type": "minecraft:crafting_shaped",
                                "pattern": ["SS", "SS"],
                                "key": {"S": {"item": "minecraft:stick"}},
                                "result": {"item": "dynasty:x", "count": 2}})
        self.assertEqual(self.scan().errors, [])

    def test_shaped_pattern_symbol_not_defined_is_error(self):
        self.repo.recipe("bad", {"type": "minecraft:crafting_shaped",
                                 "pattern": ["SX"],
                                 "key": {"S": {"item": "minecraft:stick"}},
                                 "result": {"item": "dynasty:x"}})
        self.assertIn("未在 key 中定义", joined(self.scan().errors))

    def test_shaped_unused_key_symbol_is_error(self):
        self.repo.recipe("bad", {"type": "minecraft:crafting_shaped",
                                 "pattern": ["S"],
                                 "key": {"S": {"item": "minecraft:stick"},
                                         "Z": {"item": "minecraft:coal"}},
                                 "result": {"item": "dynasty:x"}})
        self.assertIn("没用到的字符", joined(self.scan().errors))

    def test_shaped_rows_must_be_same_width(self):
        self.repo.recipe("bad", {"type": "minecraft:crafting_shaped",
                                 "pattern": ["SS", "S"],
                                 "key": {"S": {"item": "minecraft:stick"}},
                                 "result": {"item": "dynasty:x"}})
        self.assertIn("等宽", joined(self.scan().errors))

    def test_shaped_too_many_rows_or_columns_is_error(self):
        self.repo.recipe("rows", {"type": "minecraft:crafting_shaped",
                                  "pattern": ["S", "S", "S", "S"],
                                  "key": {"S": {"item": "minecraft:stick"}},
                                  "result": {"item": "dynasty:x"}})
        self.assertIn("行数超过 3", joined(self.scan().errors))
        self.repo.recipe("cols", {"type": "minecraft:crafting_shaped",
                                  "pattern": ["SSSS"],
                                  "key": {"S": {"item": "minecraft:stick"}},
                                  "result": {"item": "dynasty:x"}})
        self.assertIn("最多 3 个字符", joined(self.scan().errors))

    def test_shaped_space_in_key_is_reserved_symbol_error(self):
        self.repo.recipe("bad", {"type": "minecraft:crafting_shaped",
                                 "pattern": ["S S"],
                                 "key": {"S": {"item": "minecraft:stick"},
                                         " ": {"item": "minecraft:coal"}},
                                 "result": {"item": "dynasty:x"}})
        self.assertIn("保留符号", joined(self.scan().errors))

    def test_shaped_space_in_pattern_is_fine(self):
        self.repo.recipe("ok", {"type": "minecraft:crafting_shaped",
                                "pattern": ["S S", " S "],
                                "key": {"S": {"item": "minecraft:stick"}},
                                "result": {"item": "dynasty:x"}})
        self.assertEqual(self.scan().errors, [])

    def test_shaped_key_symbol_must_be_one_character(self):
        self.repo.recipe("bad", {"type": "minecraft:crafting_shaped",
                                 "pattern": ["S"],
                                 "key": {"SS": {"item": "minecraft:stick"}},
                                 "result": {"item": "dynasty:x"}})
        self.assertIn("恰好 1 个字符", joined(self.scan().errors))



    def test_shaped_missing_result_item_is_error(self):
        self.repo.recipe("bad", {"type": "minecraft:crafting_shaped",
                                 "pattern": ["S"],
                                 "key": {"S": {"item": "minecraft:stick"}},
                                 "result": {"count": 1}})
        self.assertIn("缺少 item 字段", joined(self.scan().errors))

    def test_result_count_zero_is_error_and_big_count_is_warning(self):
        self.repo.recipe("zero", {"type": "minecraft:crafting_shapeless",
                                  "ingredients": [{"item": "minecraft:stick"}],
                                  "result": {"item": "dynasty:x", "count": 0}})
        report = self.scan()
        self.assertIn("必须 ≥1", joined(report.errors))
        self.assertEqual([i.path for i in report.errors if "zero.json" not in i.path], [])
        self.repo.recipe("big", {"type": "minecraft:crafting_shapeless",
                                 "ingredients": [{"item": "minecraft:stick"}],
                                 "result": {"item": "dynasty:x", "count": 70}})
        report = self.scan()
        self.assertIn("超过 64", joined([i for i in report.warnings if "big.json" in i.path]))
        self.assertEqual([i.path for i in report.errors if "zero.json" not in i.path], [])

    def test_shapeless_empty_and_too_many_ingredients_are_errors(self):
        self.repo.recipe("empty", {"type": "minecraft:crafting_shapeless",
                                   "ingredients": [],
                                   "result": {"item": "dynasty:x"}})
        self.assertIn("非空数组", joined(self.scan().errors))
        self.repo.recipe("many", {"type": "minecraft:crafting_shapeless",
                                  "ingredients": [{"item": "minecraft:stick"}] * 10,
                                  "result": {"item": "dynasty:x"}})
        self.assertIn("最多 9 个原料", joined(self.scan().errors))

    def test_shapeless_empty_ingredient_entry_is_warning(self):
        self.repo.recipe("hollow", {"type": "minecraft:crafting_shapeless",
                                    "ingredients": [{"item": "minecraft:stick"}, []],
                                    "result": {"item": "dynasty:x"}})
        report = self.scan()
        self.assertEqual(report.errors, [])
        self.assertIn("incomplete", joined(report.warnings))

    def test_cooking_accepts_string_or_object_result(self):
        self.repo.recipe("str", {"type": "minecraft:smelting",
                                 "ingredient": {"item": "dynasty:jade_ore"},
                                 "result": "dynasty:jade", "experience": 0.7, "cookingtime": 200})
        self.repo.recipe("obj", {"type": "minecraft:smelting",
                                 "ingredient": {"item": "dynasty:jade_ore"},
                                 "result": {"item": "dynasty:jade", "count": 2},
                                 "experience": 0.7, "cookingtime": 200})
        self.assertEqual(self.scan().errors, [])

    def test_cooking_missing_ingredient_and_empty_array_are_errors(self):
        self.repo.recipe("noing", {"type": "minecraft:smelting",
                                   "result": "dynasty:jade"})
        self.assertIn("缺少 ingredient", joined(self.scan().errors))
        self.repo.recipe("emptyarr", {"type": "minecraft:smelting",
                                      "ingredient": [], "result": "dynasty:jade"})
        self.assertIn("空数组", joined(self.scan().errors))

    def test_cooking_time_and_experience_warnings(self):
        self.repo.recipe("fast", {"type": "minecraft:smelting",
                                  "ingredient": {"item": "dynasty:jade_ore"},
                                  "result": "dynasty:jade", "cookingtime": 0, "experience": -1})
        report = self.scan()
        self.assertEqual(report.errors, [])
        warnings = joined(report.warnings)
        self.assertIn("瞬间完成", warnings)
        self.assertIn("负数经验", warnings)

    def test_stonecutting_requires_count(self):
        self.repo.recipe("nocount", {"type": "minecraft:stonecutting",
                                     "ingredient": {"item": "minecraft:stone"},
                                     "result": "minecraft:slab"})
        self.assertIn("缺少 count", joined(self.scan().errors))
        self.repo.recipe("ok", {"type": "minecraft:stonecutting",
                                "ingredient": {"item": "minecraft:stone"},
                                "result": "minecraft:slab", "count": 2})
        errors = self.scan().errors
        self.assertEqual([i.path for i in errors if "nocount.json" not in i.path], [])


    def test_smithing_transform_fields_and_trim_without_result(self):
        self.repo.recipe("tpl", {"type": "minecraft:smithing_transform",
                                 "base": {"item": "minecraft:iron_sword"},
                                 "addition": {"item": "minecraft:netherite_ingot"},
                                 "result": {"item": "minecraft:netherite_sword"}})
        self.assertIn("缺少 template", joined(self.scan().errors))
        self.repo.recipe("trim", {"type": "minecraft:smithing_trim",
                                  "template": {"item": "minecraft:wayfinder_armor_trim_smithing_template"},
                                  "base": {"item": "minecraft:iron_chestplate"},
                                  "addition": {"item": "minecraft:gold_ingot"}})
        errors = self.scan().errors
        self.assertEqual([i.path for i in errors if "tpl.json" not in i.path], [])

    def test_special_and_unknown_types_are_skipped_not_errored(self):
        self.repo.recipe("special", {"type": "minecraft:crafting_special_repairitem"})
        self.repo.recipe("custom", {"type": "create:mixing", "ingredients": []})
        report = self.scan()
        self.assertEqual(report.errors, [])
        self.assertEqual(len(report.skips), 2)
        self.assertIn("特殊配方", joined(report.skips))
        self.assertIn("不支持的配方类型 create:mixing", joined(report.skips))

    def test_conditional_wrapper_is_expanded_and_inner_errors_located(self):
        self.repo.recipe("cond", {"type": "forge:conditional", "recipes": [
            {"conditions": [{"type": "forge:mod_loaded", "modid": "x"}],
             "recipe": {"type": "minecraft:crafting_shaped", "pattern": ["SX"],
                        "key": {"S": {"item": "minecraft:stick"}},
                        "result": {"item": "dynasty:x"}}}]})
        errors = joined(self.scan().errors)
        self.assertIn("#recipes[0].recipe", errors)
        self.assertIn("未在 key 中定义", errors)

    def test_conditional_malformed_is_error(self):
        self.repo.recipe("bad", {"type": "forge:conditional", "recipes": [{"conditions": []}]})
        self.assertIn("缺少 recipe 对象", joined(self.scan().errors))
        self.repo.recipe("nonelist", {"type": "forge:conditional", "recipes": {}})
        self.assertIn("非空 recipes 数组", joined(self.scan().errors))

    def test_identical_recipes_under_two_names_are_flagged_duplicate(self):
        recipe = {"type": "minecraft:crafting_shapeless",
                  "ingredients": [{"item": "minecraft:stick"}],
                  "result": {"item": "dynasty:x"}}
        self.repo.recipe("first", recipe)
        self.repo.recipe("second", dict(recipe))
        report = self.scan()
        self.assertEqual(report.errors, [])
        duplicate_warnings = [i for i in report.warnings if "内容完全相同" in i.message]
        self.assertEqual(len(duplicate_warnings), 2)
        self.assertIn("recipes/second.json", duplicate_warnings[0].message)

    def test_broken_json_and_nested_directory_are_handled(self):
        self.repo.recipe_raw("broken", "{not json")
        self.repo.write_json("src/main/resources/data/dynasty/recipes/nested/deep.json",
                             {"type": "minecraft:crafting_shapeless",
                              "ingredients": [{"item": "minecraft:stick"}],
                              "result": {"item": "dynasty:x"}})
        report = self.scan()
        self.assertIn("JSON 解析失败", joined(report.errors))
        self.assertEqual(report.files_checked, 2)

    def test_recipes_exit_codes(self):
        self.repo.recipe("ok", {"type": "minecraft:crafting_shapeless",
                                "ingredients": [{"item": "minecraft:stick"}],
                                "result": {"item": "dynasty:x"}})
        self.assertEqual(recipes.main(["--root", self.repo.root]), 0)
        self.repo.recipe_raw("broken", "{oops")
        self.assertEqual(recipes.main(["--root", self.repo.root]), 1)



class RunnerTest(unittest.TestCase):
    """统一入口：汇总计数 / 退出码 / JSON 报告 / --only 过滤。"""

    def setUp(self):
        self.repo = TempRepo()
        self.addCleanup(self.repo.close)
        self.repo.lang("zh_cn", {"a": "甲"})
        self.repo.lang("en_us", {"a": "A"})
        self.repo.recipe("ok", {"type": "minecraft:crafting_shapeless",
                                "ingredients": [{"item": "minecraft:stick"}],
                                "result": {"item": "dynasty:x"}})
        self.repo.model("ok", {"parent": "item/generated",
                               "textures": {"layer0": "dynasty:item/ok"}})
        self.repo.texture("ok")

    def test_all_three_checks_run_and_clean_tree_is_zero(self):
        reports = runner.run_checks(self.repo.root)
        self.assertEqual([r.name for r in reports], ["resources", "translations", "recipes"])
        self.assertEqual(sum(len(r.errors) for r in reports), 0)
        self.assertEqual(runner.main(["--root", self.repo.root]), 0)

    def test_totals_count_files_and_issues(self):
        import io
        self.repo.model("bad", {"parent": "item/generated",
                                "textures": {"layer0": "dynasty:item/gone"}})
        reports = runner.run_checks(self.repo.root)
        buffer = io.StringIO()
        total = runner.print_reports(reports, stream=buffer.write)
        self.assertEqual(total["errors"], 1)
        self.assertEqual(total["files"], sum(r.files_checked for r in reports))
        self.assertIn("确认错误 1", buffer.getvalue())

    def test_only_filter_skips_other_checks(self):
        reports = runner.run_checks(self.repo.root, only={"recipes"})
        self.assertEqual([r.name for r in reports], ["recipes"])

    def test_json_report_structure(self):
        reports = runner.run_checks(self.repo.root)
        data = runner.build_json_report(self.repo.root, reports,
                                        {"files": 0, "errors": 0, "warnings": 0, "skipped": 0})
        self.assertEqual(data["tool"], "tools/maintenance/check_all.py")
        self.assertEqual(set(data["checks"][0]), {"name", "files_checked", "details",
                                                  "counts", "errors", "warnings", "skipped"})

    def test_broken_tree_makes_runner_exit_one(self):
        self.repo.recipe_raw("broken", "{oops")
        self.assertEqual(runner.main(["--root", self.repo.root]), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
