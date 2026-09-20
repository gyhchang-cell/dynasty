"""创造模式物品栏自检：**凡是注册过的物品，都必须能在创造栏里找到**。

踩过的坑（第三十四轮）：玩家反馈「ChatGPT 画的 6 张新贴图，游戏里只有虎符能看到」——
根因不是贴图，而是 `DynastyTabs` 只逐个列了早期那几十件物品：
表驱动的 130 件饰品（含丹炉坠 / 玉如意 / 酒葫芦 / 凤钗 / 八卦镜）从来没被 `accept` 过，
所以它们在创造栏里根本不存在；虎符是 `DynastyItems` 里单独列进去的，才看得见。
另外还有 7 个高阶材料、26 把兵器、16 件食物/信物、9 件甲与戟、13 件老饰品也一起漏了。

本自检把「注册」和「展示」对齐：逐个 `RegistryObject<Item>` 常量与表驱动批次列表核对，
少一个就报错。

第三十五轮又加了一段：**标签页封面**。封面是 `DynastyItems.DYNASTY_EMBLEM`（「金龙抱玉印」），
它靠 `DynastyTabs.icon(...)` 显示，一旦有人把 icon 换回传国玉玺、或者把封面贴图删掉 /
压成 16×16，玩家看到的就是另一张图 —— 这几条也钉在这里。

运行：python3 tools/art/verify_tab.py
"""
import glob
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
JAVA = os.path.join(ROOT, "src/main/java/com/dynasty")

problems = []

# 需要「整批循环」进创造栏的批次列表（列表里的物品没有逐件常量）
BATCH_LISTS = {
    "DynastyTrinkets.EXTRA_CHARMS": "饰品（表驱动 gen_trinkets3/4/5 共 130 件）",
    "DynastyGear.EXTRA_ARMOR": "护甲（表驱动 gen_armor3 共 10 套 40 件）",
}

# 标签页封面：必须是这张画，且贴图不能糊（96 = 原作 8px 网格 1:1，见 gen_tab_icon.py）
COVER_ITEM = "DynastyItems.DYNASTY_EMBLEM"
COVER_TEXTURE = os.path.join(ROOT, "src/main/resources/assets/dynasty/textures/item/dynasty_emblem.png")
COVER_MIN_SIZE = 64


def check_cover():
    tab = read_tab()
    if (".icon(() -> new ItemStack(%s.get()))" % COVER_ITEM) not in tab:
        problems.append("创造栏封面不是 %s —— 有人把 icon 改回别的物品了（玩家看到的就是旧图）" % COVER_ITEM)
    if not os.path.exists(COVER_TEXTURE):
        problems.append("封面贴图缺失：%s（会显示成紫黑格；跑 tools/art/gen_tab_icon.py 生成）"
                        % os.path.relpath(COVER_TEXTURE, ROOT))
        return
    from PIL import Image
    with Image.open(COVER_TEXTURE) as image:
        if image.width != image.height:
            problems.append("封面贴图不是正方形（实际 %s）" % ("×".join(str(n) for n in image.size),))
        elif image.width < COVER_MIN_SIZE:
            problems.append("封面贴图只有 %d×%d —— 原作是像素画，压到 32 以下就糊成一坨"
                            "（跑 tools/art/gen_tab_icon.py 重新生成）" % image.size)
        if image.convert("RGBA").getchannel("A").getextrema()[1] == 0:
            problems.append("封面贴图全透明（画失败？）")
    if not os.path.exists(os.path.join(ROOT, "tools/art/gen_tab_icon.py")):
        problems.append("封面生成器 tools/art/gen_tab_icon.py 不见了（贴图要能一键重出）")
    elif not os.path.exists(os.path.join(ROOT, "tools/art/sources/tab_cover_source.jpg")):
        problems.append("封面源画 tools/art/sources/tab_cover_source.jpg 不见了"
                        "（生成器就没法重出贴图了；换画也要放这个路径）")


def read_tab():
    return open(os.path.join(JAVA, "DynastyTabs.java"), encoding="utf-8").read()


def verify():
    tab = read_tab()

    for reference, label in BATCH_LISTS.items():
        if reference not in tab:
            problems.append("创造栏没有引用 %s（%s）—— 这一批在游戏里会看不到" % (reference, label))

    total = 0
    for path in sorted(glob.glob(os.path.join(JAVA, "*.java"))):
        name = os.path.basename(path)[:-5]
        if name == "DynastyTabs":
            continue
        text = open(path, encoding="utf-8").read()
        consts = re.findall(r'RegistryObject<Item>\s+([A-Z0-9_]+)\s*=', text)
        if not consts:
            continue
        total += len(consts)
        missing = [c for c in consts if ("%s.%s" % (name, c)) not in tab]
        for const in missing:
            problems.append("%s.%s 已注册但没进创造栏（玩家在创造模式里看不到）" % (name, const))

    check_cover()

    print("创造栏自检：物品常量 %d 个 + 批次列表 %d 组 + 封面 1 张" % (total, len(BATCH_LISTS)))
    if problems:
        print("创造栏自检：发现问题 ❌")
        for problem in problems[:25]:
            print("   -", problem)
        sys.exit(1)
    print("创造栏自检：通过 ✅（所有注册物品都能在创造模式物品栏里找到，封面是「金龙抱玉印」）")


if __name__ == "__main__":
    verify()
