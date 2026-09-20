# 本批次完成报告（completed）

批次主题：**基础质量检查工具**（资源引用 / 语言文件 / 配方 + 统一入口 + 单元测试）。
说明：本文件只记录**本批次**；上一批（翻译补键与文档整理）的产物见文末「前置批次」，
那些文档仍在 `docs/maintenance/` 下，未被本批次修改内容。

约束遵守：只新建/修改 `tools/maintenance/` 与 `docs/maintenance/`；
未改 Java / 模型 / 贴图 / 配方 / 翻译 / 任务书 / 模组 jar；未删改 `tools/art/` 下任何脚本；
未做 Git 提交或回滚；未碰存档；未安装依赖；检查工具**只读**被检查文件。

## 1. 修改 / 新建的文件

```
tools/maintenance/checklib.py                新增  共用 Issue/Report + JSON 读取（只读）
tools/maintenance/check_resources.py         新增  资源引用检查（含父模型循环引用）
tools/maintenance/check_translations.py      新增  语言文件检查
tools/maintenance/check_recipes.py           新增  配方基础检查
tools/maintenance/check_all.py               新增  统一入口（汇总 + 可选 JSON 报告）
tools/maintenance/test_maintenance_checks.py 新增  57 个 unittest（临时目录，不碰真实资源）
docs/maintenance/README.md                   重写  用途 / 运行命令 / 判定口径 / 与 verify_*.py 的关系
docs/maintenance/completed.md                重写  本文件
```

* 没有改动：`tools/art/**`、`src/**`、`modpack/**`、`build.gradle`、任何已有翻译与配置。
* 运行测试会在脚本旁生成 `__pycache__`；本批次结束时已清理，可用 `PYTHONDONTWRITEBYTECODE=1` 避免。

## 2. 实现的检查内容（对照交付要求）

### 交付一：资源引用（`check_resources.py`）

| 要求 | 实现 |
| --- | --- |
| 物品/方块模型引用的 dynasty 本地父模型是否存在 | ✅ `parent` 为 `dynasty:` 但本地无该文件 → 错误 |
| 模型引用的 dynasty 本地贴图是否存在 | ✅ `textures.*` 为 `dynasty:...` 且缺 PNG → 错误 |
| overrides 中的本地模型是否存在 | ✅ `overrides[].model`，本地缺失 → 错误 |
| 父模型是否存在循环引用 | ✅ 沿 `parent` 走链，成环 → 错误（链式打印 `a → b → a`） |
| 正确识别 `#贴图变量` 和父模型继承 | ✅ 递归沿父链解析变量定义（含变量指向变量） |
| 外部命名空间不按本地缺失处理 | ✅ `minecraft:` / 其他模组 → 只计数，不报错 |
| 不能静态确定的单列警告 | ✅ 父链断在外部命名空间、外部贴图引用 → 警告 |
| 不判断“美不美”、不删无用资源 | ✅ 不检查未被引用的资源，不做任何删除 |

### 交付二：语言文件（`check_translations.py`）

JSON 语法、**重复键**（`object_pairs_hook` 抓取，不让解析器静默覆盖）、空白译文、
中英键集合双向差异、`%s`/`%d`/`%1$s`/`%%` 占位符兼容（**允许换序**，个数与类型必须一致；
混用带序号/不带序号给警告）。错误与警告分级，不修改任何译文。

### 交付三：配方（`check_recipes.py`）

JSON 可解析；对**明确可识别的原版类型**校验必要字段与格式：
`crafting_shaped`（pattern 1~3 行、每行 ≤3、各行等宽、图案字符必须在 key、key 字符必须被用到、
key 键必须恰好 1 个 UTF-16 字符、key 不能是空格保留符号）、`crafting_shapeless`（非空、≤9）、
`smelting/blasting/smoking/campfire_cooking`（ingredient/result/experience/cookingtime）、
`stonecutting`（ingredient + 字符串 result + 必填 count）、`smithing_transform` / `smithing_trim`（template/base/addition）；
结果数量：`< 1` 错误、`> 64` 警告；内容完全相同但文件名不同 → 标「可能重复」不删除；
`crafting_special_*` 与自定义类型 → **明确跳过并写原因**；`forge:conditional` → 展开内层配方继续按内层类型检查；
**不**判断物品注册与否，**不**判断平衡。

### 交付四：统一入口（`check_all.py`）

一条命令跑三项，输出「检查文件数 / 确认错误 / 警告 / 跳过」+ 每条问题的
`文件路径 [字段]: 原因`；任一确认错误 → 退出码 1；`--json <路径>` 可选报告（默认不写文件）；
`--only`、`--root` 可选；路径全部基于脚本位置解析（已验证：从 `/tmp` 运行结果一致）。

### 交付五：测试（`test_maintenance_checks.py`）

**57 个用例全部有实际断言**，全部在 `tempfile.TemporaryDirectory()` 里构造样本，
覆盖：正常、缺失、损坏 JSON、继承贴图、`#变量`、外部命名空间、循环引用、blockstate multipart、
overrides、重复语言键、空译文、键集合差异、占位符类型/个数/换序/`%%`、有序合成各种图案错误、
结果数量、重复配方、条件配方展开与畸形、不支持类型跳过、退出码、JSON 报告结构。


## 3. 真实测试与扫描结果

### 3.1 单元测试

```bash
$ python3 tools/maintenance/test_maintenance_checks.py
Ran 57 tests in 0.089s
OK

$ python3 -m unittest discover -s tools/maintenance -p 'test_*.py'
Ran 57 tests in 0.089s
OK
```

编写过程中出现过 4 个失败，全部是**改测试而不是放松检查**：3 个是「同一个临时仓库里放着故意坏掉的
配方，却断言整个仓库零错误」（改成按文件路径断言），1 个是我把资源检查的 3 个用例插到了语言测试类里（移动位置）。

### 3.2 对真实项目执行（只读）

```bash
$ python3 tools/maintenance/check_all.py
[资源引用] 文件 506（模型 485、本地贴图 529、parent 引用 485、贴图引用 449、本地 overrides 引用 3、本地 blockstate 引用 23） · 错误 0 · 警告 0 · 跳过 0
[语言] 文件 2（zh_cn 键 600、en_us 键 600、带占位符的键 4） · 错误 0 · 警告 0 · 跳过 0
[配方] 文件 414（类型：minecraft:crafting_shapeless 392、类型：minecraft:crafting_shaped 19、类型：minecraft:smelting 3） · 错误 0 · 警告 0 · 跳过 0

=== 汇总 ===
检查文件 922 个 · 确认错误 0 · 警告 0 · 跳过 0
（退出码 0）
```

**结论：当前项目在这三项检查下没有发现确定错误、警告或需要跳过的类型。**
（414 个配方全部落在 3 种已支持的原版类型上，所以跳过数为 0。）

### 3.3 反向验证：向「真实数据的副本」注入故障，确认工具真的能抓到

为排除「工具只是什么都没检查」，我把 `src/main/resources/{assets,data}` 复制到 `/tmp/realcheck`，
注入 4 类故障后运行统一入口（**真实项目始终未被修改**）：

```bash
$ python3 tools/maintenance/check_all.py --root /tmp/realcheck
[资源引用] ... 错误 5 ...
   ❌ .../models/block/bronze_block.json [parent]: 父模型循环引用：dynasty:block/bronze_block → dynasty:block/jade_block → dynasty:block/bronze_block
   ❌ .../models/block/jade_block.json [parent]: 父模型循环引用：（反向链）
   ❌ .../models/item/bronze_block.json [parent]: 父模型循环引用：（继承方也被指出）
   ❌ .../models/item/jade_block.json [parent]: 父模型循环引用：
   ❌ .../models/item/houyi_bow.json [textures.layer0]: 贴图不存在：dynasty:item/this_texture_does_not_exist（缺 assets/dynasty/textures/item/this_texture_does_not_exist.png）
[语言] ... 错误 4 ...
   ❌ .../lang/zh_cn.json [zz.dup]: 重复键：解析器会静默覆盖，玩家可能看到错的那条
   ❌ .../lang/zh_cn.json [zz.blank]: 空白译文（玩家会看到空名字）
   ❌ .../lang/en_us.json [zz.blank]: 缺少键（zh 有：   ）
   ❌ .../lang/en_us.json [zz.dup]: 缺少键（zh 有：第二次）
[配方] ... 错误 2 ...
   ❌ .../recipes/zz_injected_bad.json [pattern[1]]: 各行必须等宽（原版：'each row must be the same width'）：'J' 宽 1，首行宽 2
   ❌ .../recipes/zz_injected_bad.json [pattern]: 图案引用了未在 key 中定义的字符 'X'（原版：'Pattern references symbol ... but it's not defined in the key'）

=== 汇总 ===
检查文件 923 个 · 确认错误 11 · 警告 0 · 跳过 0
（退出码 1）
```

注入内容：① 真实模型贴图指向不存在的 PNG；② 真实方块模型互指成环；③ 真实配方目录里放一个
「各行不等宽 + 图案字符未定义」的有序配方；④ 真实 `zh_cn.json` 追加重复键与空白译文。
全部被定位到「文件 + 字段 + 原因」，退出码 1。

### 3.4 不依赖当前工作目录

```bash
$ cd /tmp && python3 /Users/.../dynasty/tools/maintenance/check_all.py
... 检查文件 922 个 · 确认错误 0 ... （退出码 0）
```

## 4. 已知限制（写清避免误解）

1. **只做引用存在性检查**：不看贴图尺寸/透明像素、模型 UV/几何、渲染层（贴图 32×32 由 `verify_gear.py` 管）。
2. **不检查「物品是否注册」**：按要求不靠文件名推断注册表；配方里引用的物品不存在时本工具不报错。
3. **配方只覆盖明确支持的原版类型**：`crafting_special_*`、其他模组自定义类型会**跳过**（打印类型名与原因）；
   `forge:conditional` 只展开 `recipes[].recipe` 这一层。
4. **不判断配方平衡与产物强度**；`count > 64`、`cookingtime ≤ 0`、负数经验只算警告。
5. **重复配方判定 = JSON 内容完全相同**（含 `group`/`category`）；语义等价但写法不同的不会判为重复。
6. **循环引用会在链上每个参与模型各报一条**（每个文件的父链都确实坏了），不是重复报错。
7. **外部命名空间一律不算错**：`minecraft:` / 其他模组的模型与贴图无法静态判定存在性，只计数或给警告。
8. **只做静态检查**：不启动游戏、不加载 Forge，**没有验证任何游戏内表现**；
   39 项人工测试清单（`manual-test-checklist.md`）仍是全部未实测。

## 5. 前置批次（同目录，已交付，本批未改其内容）

* 翻译：`zh_cn.json` / `en_us.json` 各 +8 键（`death.attack.dynasty.solar_judgment` 及其 `.player`、
  `dimension.dynasty.{jiuxiao,dragon_palace}`、4 个群系名），依据见 `translation-changes.md`；
  本批的 `check_translations.py` 现在守着这两份文件（600/600 键、4 个占位符键、0 错误）。
* 文档：`accessories.md`(169 件)、`weapons.md`(52 件)、`bosses.md`(6 位)、`dimensions.md`、`materials.md`、
  `translation-changes.md`、`manual-test-checklist.md`(39 项，全部未实测)、`bug-report-template.md`。
* 与项目既有自检的分工：`tools/art/verify_*.py` 管**内容完整性**（装备六处齐全、任务书连通、词条覆盖、
  宝箱表引用…），本目录管**格式与引用**；已核对 `verify_gear.py` 只判「配方文件是否存在」，没有配方格式校验，
  因此不构成重复实现。本批**未运行也未修改** `tools/art/` 下任何脚本。
