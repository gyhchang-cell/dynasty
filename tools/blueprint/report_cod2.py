"""Report native Cod2 evidence and real asset metadata without treating catalogs as completion.

Run after the opt-in native snapshot with --runtime, --server-log, --solo and --pair.
This script never changes the user's prompt or its source requirements.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HUMANOIDS = {"SWORD", "SHIELD", "PRIEST", "SPEAR", "CROSSBOW", "SCOUT", "POWDER", "FLAG", "AXE_GUARD", "GHOST", "CORPSE", "CHILD", "PAPER", "DROWNER", "STONE_GUARD", "YECHA"}
CHANGES = [
    ("src/main/java/com/dynasty/worldevent/DynastyWorldEventManager.java", "全服务器并发、存活参与/发奖、取消死亡与实体类型校验"),
    ("src/main/java/com/dynasty/worldevent/WorldEventGameTests.java", "四项新增生命周期回归；异步实体加载测试修复"),
    ("src/main/java/com/dynasty/blueprint/BlueprintSpawns.java", "已加载实体区块就绪检查；保留其他聊天的独立修改"),
    ("src/main/java/com/dynasty/dungeon/DungeonFrameworkGameTests.java", "真实驻军测试区隔离，保留实体和持久化断言"),
    ("src/main/java/com/dynasty/dungeon/DungeonTrapGameTests.java", "冲锤测试区隔离，避免其他房间核心干扰"),
    ("src/main/java/com/dynasty/blueprint/EcologyRules.java", "复用五种已存在的Cod1原生刷怪器，禁止重复登记"),
    ("src/main/java/com/dynasty/blueprint/EcologyGameTests.java", "扫描实际Biome刷怪表的重复与入口保留断言"),
    ("src/main/java/com/dynasty/dungeon/Cod2AuditGameTests.java", "新增：真实注册表、依赖、资源及服务器攻击时间轴导出"),
    ("tools/blueprint/cod2-test.init.gradle", "可选原生快照导出参数"),
    ("tools/blueprint/run_cod2_clients.py", "临时QA客户端默认静音"),
    ("tools/blueprint/report_cod2.py", "新增：以真实证据生成报告，不修改提示词"),
    ("docs/blueprint-cod2/README.md", "指向最新核验；保留历史记录"),
    ("docs/blueprint-cod2/IMPLEMENTATION_MAP.json", "校正陈旧状态，保留原始需求和未完成项"),
    ("docs/blueprint-cod2/DELETIONS_20261010.json", "新增：五段纯删除的原文、行号、备份和哈希"),
    ("docs/blueprint-cod2/LOCAL_AUDIT_20261010.md", "新增：核验报告；同名JSON保留快照与资源元数据"),
]
PLACEMENTS = [
    ("主世界", "荒漠/恶地，地下三层", "6000–9000", "昭明帝"),
    ("主世界", "山地/喀斯特，四层圆坑", "6000–9000", "刑天遗卫"),
    ("主世界", "荒原/沙地，城防与堑壕", "5000–8000", "公孙无妄"),
    ("主世界", "高山绝壁，垂直寺院", "6000–9000", "黑风法王"),
    ("复用阴司；否则主世界地下", "地下街区与血河", "待落地", "彼岸冥舟"),
    ("主世界", "湿热山地/丛林/沼泽，地下", "5000–8000", "蛇母娘娘"),
    ("复用神域；否则主世界高山上空", "浮岛/云桥", "8000–12000", "九霄木鸢"),
    ("主世界", "雪山/冰原/冻海，冰下洞窟", "6000–10000", "沉渊骨龙"),
    ("主世界", "极高山/孤峰，登峰路线", "8000–12000", "玄天剑煞"),
    ("复用现有四象终局区域", "固定唯一四岛区域", "唯一，不随机刷", "混元祖兽，保留现有最终Boss"),
]
MECHANISMS = [
    ("断龙石、兽眼、翻板、毒箭、水银闸、吊篮", "DungeonMechanismBlockEntity；房间/instance保存，阶段BE同步，接触帧服务器判定", "既有结构局部回归；完整探索未实机验证"),
    ("齿轮水闸、冲锤、履带、蒸汽、升降机", "已有crusher/conveyor/steam/elevator独立块与时钟；水闸和结构绑定待做", "冲锤单/双客户端局部QA；整座未实现"),
    ("扎马坑、地雷、箭雨、炸墙捷径", "已有mine/arrow_rain独立块；无真实爆炸；扎马坑和预设墙切换待做", "独立伤害/掩体服务端测试；整座未实现"),
    ("断木、幻镜、经幢、喷火、铁索捷径", "已有resettable_floor/shortcut基础；mirror_altar/scripture_pillar/flame_vent及结构绑定待做", "整座未实现；未实机验证"),
    ("鬼打墙、铡刀、封门、引魂灯、水闸", "已有seal_door基础；loop_gate/guillotine/soul_lantern/gate待做", "整座未实现；未实机验证"),
    ("毒藤、落石、瘴气、栈道捷径", "poison_vine/rockfall_anchor/miasma_vent及结构绑定待做", "整座未实现；未实机验证"),
    ("云砖、丹炉火、阴阳砖、上升气流", "fading_cloud_tile/flame_vent/yin_yang_tile/updraft_vent待做", "整座未实现；未实机验证"),
    ("滑冰寒冷、冰锥、热源、融冰墙", "自定义cold/heat/icicle/sealed_ice控制器待做；原版冰只提供材质与摩擦", "整座未实现；未实机验证"),
    ("飞剑阵、罡风、剑底座、倒剑桥", "已有wind_field独立块；sword_array/pedestal/桥piece切换待做", "罡风有限速度服务端测试；整座未实现"),
    ("四象碑、重力、避难点、光桥、中央门", "已有seal_door基础；四象/重力/避难/碰撞光桥及固定区域绑定待做", "整座未实现；未实机验证"),
]


def path_text(path):
    path = Path(path).resolve()
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def cell(value):
    if value is None:
        return "—"
    if isinstance(value, list):
        value = ", ".join(map(str, value))
    return str(value).replace("|", "/").replace("\n", " ")


def table(headers, rows):
    return "\n".join(["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |", *["| " + " | ".join(cell(v) for v in row) + " |" for row in rows]])


def assets(entity):
    geometry = ROOT / entity["geo"]
    animation = ROOT / entity["animation"]
    out = dict(entity, acceptance="PARTIAL；本轮未逐模型实机验收", boneCount=None, baseHeadRatio=None, shoulderJointWaistRatio=None, clips=[], silhouetteBones=[], weaponGripBones=[], texture=None, missing=[])
    for file in (geometry, animation):
        if not file.is_file():
            out["missing"].append(path_text(file))
    if out["missing"]:
        return out
    bones = json.loads(geometry.read_text())["minecraft:geometry"][0]["bones"]
    indexed = {b["name"]: b for b in bones}
    out["boneCount"] = len(bones)
    head = indexed.get("head", {}).get("cubes", [])
    feet = [c for b in bones if any(part in b["name"] for part in ("foot", "toe", "heel")) for c in b.get("cubes", [])]
    if head and feet and head[0]["size"][1] > 0:
        out["baseHeadRatio"] = round((head[0]["origin"][1] + head[0]["size"][1] - min(c["origin"][1] for c in feet)) / head[0]["size"][1], 3)
    left, right, waist = indexed.get("left_shoulder"), indexed.get("right_shoulder"), indexed.get("waist", {}).get("cubes", [])
    if left and right and waist and waist[0]["size"][0] > 0:
        out["shoulderJointWaistRatio"] = round(abs(left["pivot"][0] - right["pivot"][0]) / waist[0]["size"][0], 3)
    out["silhouetteBones"] = [b["name"] for b in bones if b.get("cubes") and any(part in b["name"] for part in ("shield", "quiver", "bow", "spear", "blade", "sword", "cape", "cloak", "skirt", "chain", "crown", "helmet"))]
    out["weaponGripBones"] = [b["name"] for b in bones if any(part in b["name"] for part in ("wrist", "hand", "grip", "weapon"))]
    for name, clip in json.loads(animation.read_text())["animations"].items():
        out["clips"].append({"name": name, "durationSeconds": clip.get("animation_length"), "loop": clip.get("loop", False), "boneTracks": len(clip.get("bones", {}))})
    model = (ROOT / "src/main/java/com/dynasty/blueprint/client/TemplateMobModel.java").read_text()
    atlas = "imperial_soldier"
    for choices, texture in re.findall(r'case\s+((?:"[^"]+"\s*,?\s*)+)\s*->\s*"([^"]+)"', model):
        if entity["id"].split(":")[1] in re.findall(r'"([^"]+)"', choices):
            atlas = texture
            break
    out["texture"] = f"src/main/resources/assets/dynasty/textures/entity/{atlas}.png"
    if not (ROOT / out["texture"]).is_file():
        out["missing"].append(out["texture"])
    out["geoSha256"], out["animationSha256"] = digest(geometry), digest(animation)
    return out


def client_evidence(directory, roles):
    result = {"directory": path_text(directory), "roles": {}}
    for role in roles:
        folder = Path(directory) / "results"
        passed = folder / (role + "-PASS.txt")
        stages = [n for n in range(10) if (folder / f"{n}-{role}").is_file()]
        result["roles"][role] = {"passed": passed.is_file() and len(stages) == 10, "stages": stages, "result": passed.read_text().strip() if passed.is_file() else "未通过/未实机验证"}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--server-log", type=Path, required=True)
    parser.add_argument("--solo", type=Path, required=True)
    parser.add_argument("--pair", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "docs/blueprint-cod2/LOCAL_AUDIT_20261010.md")
    args = parser.parse_args()
    runtime = json.loads(args.runtime.read_text())
    design = json.loads((ROOT / "docs/blueprint-cod2/IMPLEMENTATION_MAP.json").read_text())
    log = args.server_log.read_text(errors="replace")
    passed = re.findall(r"All (\d+) required tests passed", log)
    server = {"passed": bool(passed) and "BUILD SUCCESSFUL" in log and " failed!" not in log, "tests": int(passed[-1]) if passed else None, "log": path_text(args.server_log), "sha256": digest(args.server_log)}
    solo, pair = client_evidence(args.solo, ["host"]), client_evidence(args.pair, ["host", "peer"])
    models = [assets(e) for e in runtime["entities"]]
    report = dict(runtime, serverEvidence=server, soloEvidence=solo, pairEvidence=pair, assetMetadata=models, runtimeSnapshotSha256=digest(args.runtime), modifiedFiles=[dict(path=path, purpose=purpose) for path, purpose in CHANGES], complete=False)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.with_suffix(".json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    sections = ["# Cod2 本地核验与补完记录 · 2026-10-10", "**未全部完成。** 本报告来自真实服务端注册表、现有资源和实机局部 QA。框架、目录、注册 ID、单个场景通过均不代表整项成品完成。已验证基础任务从外部 `cod2.txt` 删除，原文备份及删除记录见 `DELETIONS_20261010.json`。", "## 本轮实现与验证", "修正事件服务器全局并发上限、死亡玩家参与/奖励/祝福判定、被取消死亡与实体类型不匹配的账本更新；真实压缩 `.dat` 文件测试验证离线奖励、清理预约及冷却恢复。沉沙玄宫驻军等待实际实体区块就绪。修正新合入 Cod1 物种的重复生态刷怪表登记，并扫描全部实际 Biome 刷怪表验证每种至多一条、至少保留一个有效入口。", f"服务端：{server['tests']} 项，{'通过，构建成功' if server['passed'] else '未通过，见日志'}。单客户端：{solo['roles']['host']['result']}。双客户端：host={pair['roles']['host']['result']}；peer={pair['roles']['peer']['result']}。", "客户端 10 阶段涵盖：真实奖励模型、阴兵队列与雾、资源重载、客机 TCP 断线重连、停止后清理、玄鸟祝福与武器耐久同步、冲锤三阶段实际 Renderer、再次天象及现有维度切换后清理。使用临时世界、静音，不改变系统音量；不等于地牢完整通关或30事件验收。", "## 10 地下城世界落点表", "下表保留原设计落点，只有沉沙玄宫已经注册实际结构。其8192格是候选网格间距，实际平均发现距离未测；其他行均是未实现的要求。"]
    rows = []
    registered = {d["id"]: d for d in runtime["registeredDungeons"]}
    for source, placement in zip(design["dungeons"], PLACEMENTS):
        live = registered.get("dynasty:" + source["id"])
        rows.append([source["name"], placement[0], placement[1], placement[2], live["minDistanceFromSpawn"] if live else "待落实", placement[3], "PARTIAL；缺Boss/精英/奖励/完整美术与探索验收" if live else "未实现"])
    sections.append(table(["地下城", "维度要求", "地形/层级", "原要求间距", "最小出生点距离", "Boss要求", "状态"], rows))
    sections.extend(["沉沙玄宫实际缺失：" + "；".join(runtime["chenshaMissingDependencies"]) + "。披鳞执金吾、巨锤金甲力士亦未注册；其余九座没有成品结构，不能用现有 Boss 改名或空钩子充数。", "## 地下城机关实现表", table(["机关", "方块/类", "保存与同步", "伤害/动画", "本轮验收边界"], [["断龙石/三兽眼/封门", "自定义 DungeonMechanismBlock/BlockEntity", "房间SavedData、实例UUID、目标位掩码、BE包", "服务端解谜；封门碰撞/开门进度", "既有服务端局部测试；本轮未跑整座地牢"], ["毒箭/翻板", "自定义 pressure_trap_emitter/resettable_floor", "房间时钟；BE阶段快照", "接触帧生成限量毒箭/失碰撞/恢复", "服务端回归；本轮未完整探索验收"], ["返程吊篮/石碑", "自定义 elevator/shortcut", "SavedData永久解锁；目标楼层", "已加载安全目标，有限楼层式传送", "服务端回归；未把货物测试当实机地牢通关"], ["水银闸/护城渠", "房间控制器/受保护mercury_channel", "服务端计时、暂停卸载；专用不可挖块", "预警、区域接触；幻想粒子液面", "服务端回归；本轮未实机末室验收"], ["冲锤/履带/蒸汽/地雷/箭雨/罡风", "自定义六种TRAP + DungeonTrapProfile", "同一房间时钟，持久化阶段/剩余tick", "预警后有限伤害或速度；冲锤Renderer", "冲锤显示/同步通过单/双端局部QA；不等于对应地牢完成"], ["其余设计机关", "尚缺真实实现/结构绑定", "待实现", "待实现", "未实机验证"]])])
    sections.append(table(["地下城", "机关要求", "自定义/状态/动画/同步", "实机边界"], [[source["name"], *mechanism] for source, mechanism in zip(design["dungeons"], MECHANISMS)]))
    sections.extend(["## 10 生态规则表", "权重/group为EcologyRule定义值；使用已有Cod1刷怪器的物种保留其实际原生权重，并禁止二次登记。自然分布、所有原文协同/天气行为、缺失精英与神域角色均未整项验收。"])
    rows = []
    for source, rule in zip(design["ecology"], runtime["ecology"]):
        members = [f"{m['mobType'].split(':')[1]} w={m['weight']} g={m['minGroup']}–{m['maxGroup']} cap={m['localCap']}" for m in rule["members"]]
        rows.append([source["name"], "#" + rule["dimensionTag"], rule["biomeTag"] or rule["structureTag"] or "固定阵眼范围待绑定", f"{rule['minY']}–{rule['maxY']}", rule["timeWindow"] + "/" + rule["weather"], f"普通{rule['caps']['ordinary']}/飞行{rule['caps']['flying']}/精英{rule['caps']['elite']}", members or "无自然池；原角色待绑定"])
    sections.append(table(["区域", "维度类型Tag", "Biomes/结构Tag", "Y", "时间/天气", "local cap", "物种/权重/group"], rows))
    sections.append("实际缺失生态实体：" + "；".join(runtime["missingEcologyEntities"]) + "。未绑定原文角色：" + "、".join(runtime["unboundEcologyRoles"]) + "。阵营、捕食目标、world state说明详见同名JSON，字符串状态说明不等于相应行为已经实现。")
    sections.extend(["## 30 随机事件触发表", "3个基础控制器可运行，27个仍UNIMPLEMENTED；3个运行模板的完整原奖励分支、场景叙事和自然触发验收仍为PARTIAL。手动命令不会把UNIMPLEMENTED事件替换成通用事件。所有触发参数来自当前实际Definition。"])
    sections.append(table(["事件", "维度Tag", "区域Tag/Y", "时间/天气", "冷却/稀有度", "半径/时限tick", "控制器/状态"], [[e["name"], e["dimensionTag"], (e["biomeTag"] or e["structureTag"] or "维度范围") + f" / {e['minY']}–{e['maxY']}", f"{e['startTime']}–{e['endTime']} / {e['weather']}", f"{e['cooldown']} / 1:{e['rarity']}", f"{e['radius']} / {e['duration']}", e["controller"] + " / " + e["acceptance"]] for e in runtime["events"]]))
    sections.extend(["实例seed、参与UUID、actor UUID、临时方块原状态及奖励托管有保存接口；取消死亡与类型不匹配不能写入击杀，已卸载UUID不算死亡。成功/失败、奖励与清理框架仅验证已运行模板，未实现事件不能声称已拥有原文分支。", "## 已有返工人形模型清单", "本轮未重绘模型。以下记录实际已有资源，替代过时的“模型全部未启动”报告。头身比为主颅面首个网格到脚部最低网格的静态测量；肩腰比为肩轴距离/腰部首个网格宽，不含甲片外轮廓。空值需要专门视觉测量；测量和骨骼存在不等于握持/穿模/剪影验收通过。"])
    human = [m for m in models if m["kind"] in HUMANOIDS]
    sections.append(table(["实体/职业", "基础头身比", "肩轴/腰比", "骨骼数", "geo / texture", "握持/LOD"], [[m["id"] + " / " + m["kind"], m["baseHeadRatio"], m["shoulderJointWaistRatio"], m["boneCount"], m["geo"] + " / " + str(m["texture"]), f"{len(m['weaponGripBones'])}个腕/掌/握点；二级动画{m['secondaryDistance']}格外停更，网格LOD待验"] for m in human]))
    sections.extend(["## 11 类 AnimationProfile 完成表", "共享枚举/语义已经完成；各物种有独立动画资源，但全部职业覆盖、动作质量、所有击中帧、变TPS、移速与远距LOD仍未整项实机验收。逐clip循环/时长、实际移速属性、二级距离及geo摘要在同名JSON；服务端伤害关键帧直接导出自SkillDefinition，不从画面或同名attack剪辑推断。"])
    sections.append(table(["Profile", "适用已注册实体", "资源/循环/时长", "二级距离", "状态"], [[p["id"], [m["id"].split(":")[1] for m in models if m["profile"] == p["id"]], f"独立动画；{sum(len(m['clips']) for m in models if m['profile'] == p['id'])}个clip，明细见JSON", p["secondaryDistance"], "枚举/映射已验；完整动画质量PARTIAL"] for p in runtime["animationProfiles"]]))
    sections.extend(["## 性能、清理与剩余范围", "服务器事件全局最多3个，单维度最多保存256个实例；每20tick事件生成预算为2个，触发每200–400tick分批6个候选。生态空闲行为按UUID错峰32tick、12格查询；地牢只访问已加载marker，不为创建实体新增区块票。现有候选网格间距和上述预算不是生成距离/TPS测量；完整自然结构生成性能、同屏压力及长期多人负载仍未验证。", "仍需完成：第一座缺失Boss/精英/最终奖励/美术与完整通关；其余九座地牢与机关；七个缺失生态精英和四个未绑定角色，以及十区原文特殊行为；27个事件的控制器和全部30个的具体原文分支；人形全方位/纯黑剪影/握持穿模验收；11类完整动画同步与LOD验收；旧世界、真实服务器重启及双人完整自然探索测试。以上仍保留在提示词，不标DONE。", "## 本轮修改/新增文件", table(["文件", "用途"], CHANGES), "外部 `cod2.txt` 删除三段已验证基础要求，以及本轮完成的实施映射审核和基线构建要求；其他需求原样保留。证据目录仅存文本结果、日志与截图，不包含测试世界或玩家存档。", "## 证据", f"原生快照：`{path_text(args.runtime)}`，SHA-256 `{digest(args.runtime)}`。服务端日志：`{server['log']}`，SHA-256 `{server['sha256']}`。单端：`{solo['directory']}`；双端：`{pair['directory']}`。同名JSON保留30事件缺失依赖、10生态阵营/捕食状态、30已注册实体资源与完整服务端技能时间轴。"])
    args.output.write_text("\n\n".join(sections) + "\n")
    print(json.dumps({"report": str(args.output), "server": server, "humanoids": len(human), "complete": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
