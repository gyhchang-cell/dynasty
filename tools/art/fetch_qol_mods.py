"""下载整合包要带的「优化 / 便利 / 生存」模组（Forge 1.20.1）。

原则：
  * 优化类：只提升帧数与内存，不改玩法；
  * 便利类：信息显示、操作、连锁采掘（连锁已由本体内置，故不再带 Vein Mining）；
  * 生存类：死亡保护、定位、地图、睡眠、收割等，让长时间生存更舒服；
  * 只用主流、仍在维护的项目；自动解析必需前置（如 Waystones → Balm）。

运行：python3 tools/art/fetch_qol_mods.py
输出：libs/*.jar 以及 tools/art/qol_mods.json（供 make_modpack.py 使用）
"""
import json
import os
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LIBS = os.path.join(ROOT, "libs")
os.makedirs(LIBS, exist_ok=True)

# slug -> 说明（写进整合包简介）
SLUGS = {
    # ---- 性能优化 ----
    "embeddium": "渲染优化（帧数）",
    "ferrite-core": "内存占用优化",
    "modernfix": "启动提速 + 内存优化",
    "entityculling": "实体渲染剔除（帧数）",
    "immediatelyfast": "即时渲染优化（帧数）",
    "clumps": "经验球合并（减少卡顿）",
    "memoryleakfix": "内存泄漏修复",
    # ---- 信息与操作 ----
    "jade": "准星查看方块/生物信息",
    "appleskin": "显示饱食度与饱和度",
    "mouse-tweaks": "鼠标拖拽整理物品",
    "crafting-tweaks": "合成台整理/轮换配方",
    # ---- 生存便利 ----
    "corpse": "死亡后掉落物装进尸体，跑回去就能全拿回来",
    "waystones": "传送石：激活后可跨地图传送（长线生存不迷路）",
    "explorers-compass": "结构指南针：直接搜索宫殿/帝陵等结构",
    "natures-compass": "群系指南针：搜索天朝、地府等群系",
    "xaeros-minimap": "小地图（客户端）",
    "xaeros-world-map": "大地图（客户端）",
    "comforts": "睡袋 / 吊床：不用床也能睡觉过夜",
    "rightclickharvest": "右键收割成熟作物（不用反复破坏）",
    "torohealth-damage-indicators-updated": "伤害数字显示（打得准不准一眼看出来）",
    "torchmaster": "火把大师：范围阻止刷怪，营地更安全",
    # ---- 从「愚者」整合包里筛出来的辅助模组（只保留辅助/优化/信息类）----
    "noisium": "世界生成性能优化（开新图更快，服务端友好）",
    "radium": "服务端逻辑优化（Lithium 系，AI/红石/物理更省 CPU）",
    "saturn": "内存占用优化（降低内存压力）",
    "async-locator": "结构定位异步化（/locate 与结构搜索不再卡主线程）",
    "spark": "性能分析器（卡了随时看是谁的锅）",
    "alltheleaks": "内存泄漏修复（长时间挂机更稳）",
    "better-advancements": "更好的进度界面（可搜索、有进度条）",
    "controlling": "按键搜索与冲突提示（模组多了必备）",
    "jecharacters": "JEI/界面支持拼音搜索中文名（中文玩家神器）",
    "enchantment-descriptions": "附魔显示具体效果说明",
    "just-enough-resources-jer": "JEI 里看矿石产出与掉落来源",
    "great-scrollable-tooltips": "超长提示可滚动（我们的物品说明很长）",
    "item-borders": "物品按稀有度加边框，一眼识别",
    "legendary-tooltips": "豪华提示框（边框+动效）",
    "travelers-titles": "到新群系弹地名标题",
    "tips": "加载界面显示小贴士",
    "trashslot": "内置垃圾桶格（丢垃圾不用挖坑）",
    "attributefix": "放宽原版属性上限（大数值装备不再被截断）",
    "yeetus-experimentus": "关掉「实验性世界」警告弹窗",
    "customskinloader": "正版/离线皮肤加载（多人一起玩更顺眼）",
    "shoulder-surfing-reloaded": "第三人称越肩视角（打 Boss 更爽）",
    "construction-wand": "建造法杖：一次放一排方块（盖宫殿省手）",
    "sophisticated-backpacks": "背包：可升级的随身储物（生存辅助）",
    "polymorph": "配方冲突选择器（模组多了也不会抢配方）",
    "chickenchunks": "区块加载器（挂机农场/刷怪塔不用蹲守）",
    "openloader": "从 config 目录加载数据包/资源包（便于改包）",
    # ---- 再加一批：只影响性能 / 画面 / 声音 / 界面，完全不碰玩法 ----
    "starlight": "光照引擎重写（大幅提升区块加载与帧数）",
    "dynamic-fps": "动态帧率（后台自动降帧，省电省风扇）",
    "moreculling": "更聪明的面剔除（帧数，尤其建筑密集时）",
    "fast-ip-ping": "服务器列表延迟刷新更快",
    "fallingleaves": "飘落的树叶（纯画面氛围）",
    "not-enough-animations": "角色动画（走路/挥砍更自然，纯画面）",
    "3dskinlayers": "皮肤外层 3D 化（帽檐/披风立体，纯画面）",
    "eating-animation": "吃东西有咀嚼动画（纯画面）",
    "visuality": "粒子特效增强（尘土/血雾，纯画面）",
    "sound-physics-remastered": "声音物理（洞穴回声/水下闷响，纯音效）",
    "betterf3": "F3 调试信息排版更清爽",
    "just-zoom": "缩放键（望远镜式放大，纯客户端功能）",
    "chat-heads": "聊天栏显示头像",
    "debugify": "修一批原版小 bug（不改变玩法平衡）",
    "toast-control": "关掉成就/配方弹窗刷屏",
    "cameraoverhaul": "更顺滑的第三人称镜头（不改战斗手感）",
    "fresh-animations": "生物动画（走路/攻击更生动，纯画面）",
    "entity-model-features": "实体模型细节（配合动画模组，纯画面）",
}

UA = {"User-Agent": "dynasty-modpack-builder/1.0 (personal use)"}

# 必须认准文件名的项目（否则会拿到不兼容的构建）
PIN = {
    "customskinloader": "ForgeV2",   # Universal 版缺类 → 启动崩溃
}


def api(url):
    """用 curl 取 JSON（本机 python 缺少证书链，curl 正常工作）。"""
    out = subprocess.run(["curl", "-sL", "--max-time", "60", url],
                         capture_output=True, text=True).stdout
    return json.loads(out)


def download(url, target):
    subprocess.run(["curl", "-sL", "--max-time", "300", "-o", target, url], check=True)


def best_version(slug):
    """取该模组最新的 Forge 1.20.1 版本 / newest Forge 1.20.1 version"""
    url = ("https://api.modrinth.com/v2/project/" + slug +
           "/version?loaders=%5B%22forge%22%5D&game_versions=%5B%221.20.1%22%5D")
    versions = api(url)
    if not versions:
        return None, None
    # 某些项目要认准文件名（例如 CustomSkinLoader 必须用 ForgeV2 版本，
    # Universal 版缺类会导致崩服：customskinloader/fake/itf/IFakeIResourceManager$V1）
    pin = PIN.get(slug)
    for version in versions:
        for f in version["files"]:
            if pin and pin in f["filename"]:
                return version, f
    version = versions[0]
    for f in version["files"]:
        if f.get("primary"):
            return version, f
    return version, version["files"][0]


def project_slug(project_id):
    try:
        return api("https://api.modrinth.com/v2/project/" + project_id).get("slug")
    except Exception:
        return None


def main():
    records = {}
    notes = dict(SLUGS)
    queue = list(SLUGS.keys())
    seen = set()
    depth = {slug: 0 for slug in SLUGS}

    while queue:
        slug = queue.pop(0)
        if slug in seen:
            continue
        seen.add(slug)
        try:
            version, f = best_version(slug)
        except Exception as error:
            print("FAIL", slug, error)
            continue
        if not version:
            print("SKIP", slug, "(没有 Forge 1.20.1 版本)")
            continue
        filename = f["filename"]
        target = os.path.join(LIBS, filename)
        if not os.path.exists(target):
            download(f["url"], target)
        records[slug] = {
            "slug": slug,
            "name": version["name"],
            "version": version["version_number"],
            "filename": filename,
            "url": f["url"],
            "sha1": f["hashes"]["sha1"],
            "sha512": f["hashes"]["sha512"],
            "size": os.path.getsize(target),
            "client": version.get("client_side", "required"),
            "server": version.get("server_side", "required"),
            "note": notes.get(slug, "前置库 / dependency"),
        }
        print("OK  ", slug, filename, os.path.getsize(target), "bytes")
        # 解析必需前置 / resolve required dependencies
        if depth.get(slug, 0) < 2:
            for dep in version.get("dependencies", []):
                if dep.get("dependency_type") != "required":
                    continue
                if dep.get("project_id") and dep["project_id"] not in seen:
                    dep_slug = project_slug(dep["project_id"])
                    if dep_slug and dep_slug not in seen:
                        depth[dep_slug] = depth.get(slug, 0) + 1
                        print("    → 需要前置:", dep_slug)
                        queue.append(dep_slug)

    out_path = os.path.join(os.path.dirname(__file__), "qol_mods.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(list(records.values()), f, ensure_ascii=False, indent=2)
    print("saved", out_path, len(records), "mods")

    # 清理已经不再需要的 jar（例如已被本体连锁替代的 Vein Mining）
    keep = {r["filename"] for r in records.values()}
    keep.add("curios-forge-5.14.1+1.20.1.jar")
    keep.add("jei-1.20.1-forge-15.59.0.210.jar")
    keep.add("OverflowingBars-v8.0.1-1.20.1-Forge.jar")
    keep.add("PuzzlesLib-v8.1.33-1.20.1-Forge.jar")
    # FTB 系列（由 fetch_ftb_mods.py 下载，登记在 ftb_mods.json）
    ftb_json = os.path.join(os.path.dirname(__file__), "ftb_mods.json")
    if os.path.exists(ftb_json):
        for record in json.load(open(ftb_json, encoding="utf-8")):
            keep.add(record["filename"])
    for folder in (LIBS, os.path.join(ROOT, "modpack", "mods"), os.path.join(ROOT, "整合包实例", "mods")):
        if not os.path.isdir(folder):
            continue
        for name in os.listdir(folder):
            if name.endswith(".jar") and name not in keep and not name.startswith("dynasty-"):
                os.remove(os.path.join(folder, name))
                print("删除旧模组:", os.path.relpath(os.path.join(folder, name), ROOT))


if __name__ == "__main__":
    main()
