# tools/maintenance —— 王朝基础质量检查（只读）

一套**只读**、只用 Python 标准库、路径基于脚本自身位置（不依赖当前目录）的检查工具，
用来在每次更新后一次性发现「资源引用 / 语言文件 / 配方 JSON」里的低级问题。

## 一条命令跑全部

```bash
python3 tools/maintenance/check_all.py
```

输出（示例为真实项目当前状态）：

```
[资源引用] 文件 506（模型 485、本地贴图 529、parent 引用 485、贴图引用 449、本地 overrides 引用 3、本地 blockstate 引用 23） · 错误 0 · 警告 0 · 跳过 0
[语言] 文件 2（zh_cn 键 600、en_us 键 600、带占位符的键 4） · 错误 0 · 警告 0 · 跳过 0
[配方] 文件 414（类型：minecraft:crafting_shapeless 392、类型：minecraft:crafting_shaped 19、类型：minecraft:smelting 3） · 错误 0 · 警告 0 · 跳过 0

=== 汇总 ===
检查文件 922 个 · 确认错误 0 · 警告 0 · 跳过 0
```

* 每个问题都会打印**文件路径 + 相关字段 + 原因**，例如
  `❌ .../models/item/houyi_bow.json [textures.layer0]: 贴图不存在：dynasty:item/xxx（缺 .../textures/item/xxx.png）`。
* **任一确认错误 → 退出码 1**；只有警告/跳过 → 0（可直接接进 CI 或收尾脚本）。
* 常用参数：

```bash
python3 tools/maintenance/check_all.py --only resources,recipes      # 只跑其中几项
python3 tools/maintenance/check_all.py --json /tmp/dynasty-check.json # 可选 JSON 报告（默认不写任何文件）
python3 tools/maintenance/check_all.py --root /别的/仓库              # 检查别的检出（测试用）
```

**默认不在项目里生成任何文件**；`--json` 的路径由调用者决定。

## 单项检查

| 脚本 | 检查内容 | 退出码 |
| --- | --- | --- |
| `check_resources.py` | 模型 JSON 可解析；`parent` / `textures` / `overrides[].model` / blockstate 引用的**本地**模型与贴图是否存在；`#贴图变量` 沿父链解析；**父模型循环引用** | 有错误 → 1 |
| `check_translations.py` | JSON 可解析；**重复键**（不被解析器静默覆盖）；空白译文；中英**键集合差异**；`%s`/`%d`/`%1$s`/`%%` 占位符兼容（顺序可不同） | 有错误 → 1 |
| `check_recipes.py` | 配方 JSON 可解析；按类型检查必要字段；有序合成的图案尺寸/未定义字符/未使用字符/空格；结果数量有效性；内容相同的重复配方；不支持类型明确跳过 | 有错误 → 1 |

可以单独运行，例如 `python3 tools/maintenance/check_recipes.py --root <路径> --data src/main/resources/data`。

### 判定口径（为什么不会乱报）

* **错误（error）**：只在本工具能**静态确定**时给出 —— 本地命名空间引用却找不到文件、
  `#变量` 在**本地父链走到底**仍无定义、父链成环、JSON 坏了、配方违反原版会抛错的规则。
* **警告（warning）**：无法静态判定或原版不报错但可疑 —— 父链接到 `minecraft:`/其他模组就断了、
  贴图来自外部命名空间、配方产物 `count > 64`、`cookingtime ≤ 0`、配方内容完全相同（可能重复）。
* **跳过（skip）**：明确不套用普通规则 —— `minecraft:crafting_special_*` 等特殊配方、
  其他模组的自定义配方类型（会写明类型名与原因）。`forge:conditional` 会**展开内层配方**继续检查，
  问题路径写成 `<文件>#recipes[0].recipe`。
* **不检查**：物品是否已注册（不靠文件名猜注册表）、配方数值平衡、资源有没有被引用（未使用素材不算问题，也不会删）。

## 测试

```bash
python3 tools/maintenance/test_maintenance_checks.py          # 直接跑
python3 -m unittest discover -s tools/maintenance -p 'test_*.py'   # 或 discover
```

* **57 个用例全部通过**（`Ran 57 tests ... OK`），全部在**临时目录**里构造样本，不读写真实资源；
  覆盖正常 / 缺失 / 损坏 JSON / 继承贴图 / `#变量` / 外部命名空间 / 循环引用 / blockstate multipart /
  overrides / 重复语言键 / 空译文 / 键集合差异 / 占位符换序与不匹配 / 有序合成各种图案错误 /
  结果数量 / 重复配方 / 条件配方展开 / 不支持类型跳过 / 退出码 / JSON 报告结构。
* 想避免生成 `__pycache__` 可加 `PYTHONDONTWRITEBYTECODE=1`。

## 文件

```
tools/maintenance/checklib.py               共用的问题对象与 JSON 读取（Issue/Report）
tools/maintenance/check_resources.py        资源引用检查
tools/maintenance/check_translations.py     语言文件检查
tools/maintenance/check_recipes.py          配方检查
tools/maintenance/check_all.py              统一入口（汇总 + 可选 JSON 报告）
tools/maintenance/test_maintenance_checks.py 单元测试
```

## 与项目已有自检的关系

* `tools/art/verify_*.py` 是**内容完整性**自检（装备六处齐全、任务书连通、词条覆盖、宝箱表引用等），
  由 `./gradlew exportModpack` 串起来；本目录的工具是**格式与引用**检查，两者互补、互不替代。
* 已核对：`tools/art/verify_gear.py` 只判断「配方文件是否存在」，**没有**配方格式校验，所以这里不是重复实现；
  本工具**没有**改动 `tools/art/` 下任何脚本，也没有改 `build.gradle`。

## 同目录的文档（上一批维护产物）

`accessories.md`（169 件饰品）、`weapons.md`（52 件武器）、`bosses.md`（6 位 Boss）、`dimensions.md`、
`materials.md`、`translation-changes.md`、`manual-test-checklist.md`、`bug-report-template.md`、`completed.md`。
