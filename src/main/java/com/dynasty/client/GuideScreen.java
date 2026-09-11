package com.dynasty.client;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import org.lwjgl.glfw.GLFW;

/**
 * 王朝图鉴界面：内置多页指南（无需额外模组）。
 * Dynasty Codex screen: a built-in multi-page guide (no extra mods required).
 */
@SuppressWarnings("null")
public class GuideScreen extends Screen {

    private static final String[][] PAGES = {
            {"王朝图鉴 · Dynasty Codex", "§7本模组加入了一个完整的东方王朝：", "§7世界、建筑、科举、军队、神兽与节日。",
             "§7使用 §f← →§7 或下方按钮翻页。", "", "§8右键手中的《王朝图鉴》随时打开。"},
            {"一、开局指南", "§f1.§7 打开背包，点左上角 §6✦ 王朝任务§7 查看任务顺序。",
             "§f2.§7 挖玉矿（jade_ore）与朱砂，制作玉器与符箓。",
             "§f3.§7 用 §f玉门 (jade_portal)§7 前往 §6天朝·龙庭§7。",
             "§f4.§7 用 §f冥门 (underworld_portal)§7 前往 §5地府§7。",
             "§f5.§7 科举中第获得官阶；用 §f虎符§7 调动禁军。"},
            {"一点五、怎么看物品用法", "§7把鼠标悬停在物品上，按住 §eShift§7 即可看到：",
             "§7• §f用法说明§7：右键/左键能做什么。",
             "§7• §c攻击力§7 / §b护甲§7 / §7耐久§7 等数值。",
             "§7• §6套装加成§7：王朝盔甲的减伤与生命加成。",
             "§8不按 Shift 时只显示一行提示，不占屏幕。"},
            {"二、天朝·龙庭", "§7真实的噪声地形与 4 个自定义群系：",
             "§a天朝平原§7 / §a玉林§7 / §a龙脊山脉§7 / §a碧海云海§7",
             "§7地表以汉白玉为基岩，玉石与龙晶藏于地下。",
             "§7空气中弥漫着龙气：怪物在白天也会出现。", "",
             "§8提示：宫殿结构会在地表随机生成。"},
            {"三、地府", "§7黑石与岩浆的世界，天顶封闭、永无天日。",
             "§5幽冥荒原§7 与 §5忘川河畔§7 两大群系。",
             "§7敌对生物：兵马俑、刺客、叛军、九尾狐。",
             "§7深处仍可寻得玉矿与龙晶矿。", "",
             "§8小心：脚下就是岩浆海。"},
            {"四、宏伟建筑", "§6皇家宫殿§7：48×48 的完整宫殿群——",
             "§7三层台基、城墙垛口、四座角楼、太和殿、",
             "§7御花园、金柱廊庑与宝箱。",
             "§6帝陵地宫§7：地下墓道、双耳室、主墓室、",
             "§7棺椁与陪葬品。",
             "§8用 /locate structure dynasty:palace 寻找。"},
            {"五、科举与官阶", "§7右键 §f科举试卷§7 打开答题界面（三选一）。",
             "§7答对获得功名与增益；每 100 功名晋升一阶：",
             "§7布衣 → 秀才 → 举人 → 进士 → 翰林 →",
             "§7尚书 → 大学士 → 丞相 → 摄政王",
             "§7忠诚与叛乱都会影响王朝稳定。", "§8右键 §f玉玺§7 查看王朝档案。"},
            {"六、军队与阵型", "§7右键 §f虎符§7 打开调兵界面，选择阵型与人数：",
             "§f方阵§7 均衡推进  §f锋矢阵§7 突破敌阵",
             "§f雁行阵§7 两翼包抄  §f横阵§7 正面拒敌  §f圆阵§7 四面固守",
             "§7禁军会跟随你、攻击怪物，并自动传送归队。",
             "§7忠诚越高，军队士气越高。", "§8潜行右键虎符 = 威慑周围生物。"},
            {"七、神兽与妖魔", "§a麒麟§7：喂食仙桃可获民心。",
             "§6凤凰§7：浴火飞行，喷吐火焰。",
             "§d九尾狐§7：受击瞬移，爪牙附缓慢。",
             "§c年兽§7：春节现身，惧爆竹（爆炸伤害加倍）。",
             "§7材料：麒麟角 / 凤凰羽 / 九尾狐尾。", "§8小怪：大臣、刺客、弓兵、锦衣卫、叛军。"},
            {"八、Boss 与战功", "§4龙帝§7：血量 1024，龙息火球 + 召唤禁军。",
             "§c叛将§7：冲锋击退，召来叛军。",
             "§5宦官首脑§7：施放虚弱与失明，放出刺客。",
             "§7Boss 与神兽拥有「士气减伤」，普通武器几乎无效，",
             "§7需要 §6玉剑 / 龙晶剑 / 方天画戟§7 才能造成有效伤害。",
             "§8击败 Boss 获得大量功名、忠诚与宝物。"},
            {"九、节日与丹药", "§7按现实日期自动开启节日：",
             "§f春节§7(2/1-2/20) §f端午§7(6/1-6/10) §f中秋§7(9/15-9/25)",
             "§f重阳§7(10/1-10/10) §f除夕§7(12/31-1/2)",
             "§7节日发放食物、烟花与祝福效果。",
             "§7药水可在酿造台制作：龙威 / 铁壁 / 疾风 / 民心 / 天命。",
             "§7丹药：长寿丹、凝神丹、金创药。"},
            {"十、数值一览", "§7武器（总攻击力）：青铜剑 §f1000§7 / 官银剑 §f1200§7 /",
             "§7玉剑 §f1500§7 / 龙晶剑 §f1900§7 / 方天画戟·龙晶镐 §f2048§7（上限）。",
             "§7护甲：玉甲 §f53§7 / 将军铠 §f60§7 / 龙鳞甲 §f71§7（含韧性 20）。",
             "§7套装减伤：玉甲 §f60%§7 / 将军铠 §f72%§7 / 龙鳞甲 §f80%§7。",
             "§7套装生命：§f+600 / +800 / +1000§7（总生命最高 §f1020§7）。",
             "§8生命超过 80 时血条会变成紧凑条，避免上百颗心掉帧。"},
            {"十一、管理员指令（正常游玩不需要）", "§f/dynasty keju§7 打开答题界面（同科举试卷）",
             "§f/dynasty stats§7 查看官阶与民心（同玉玺）",
             "§f/dynasty army formation <阵型> <人数>§7 列阵（同虎符）",
             "§f/dynasty guide§7 获得一本王朝图鉴",
             "§f/dynasty festival <spring|dragonboat|midautumn|double9|newyear>§7",
             "§f/dynasty found§7 开国（获得天命与民心）"},
            {"十二、兵器进化链", "§7武器可以一步步升级（都是合成，不用指令）：",
             "§f青铜剑 1000§7 → §f唐刀 1000·极速§7 → §f环首刀 1100·反击§7 →",
             "§f银剑 1200§7 → §f长枪 1300·距离+3§7 → §f玉剑 1500§7 →",
             "§f巨阙 1700·重击§7 → §f破军斧 1750·破甲§7 → §f龙晶剑 1900§7 →",
             "§f方天画戟 2048·横扫§7（玉笛 1450·范围削弱、龙吟弓 远程）",
             "§8在任务界面「图鉴」页可查每把武器的配方与妙用。"},
            {"十三、饰品与槽位", "§7开局赠送 §f百宝妆匣§7，右键打开 6 个饰品槽。",
             "§7饰品带在身上（或放进 Curios 槽）也会生效：",
             "§f玉佩§7 减伤 8%  §f玉璧§7 生命 +150",
             "§f金印§7 功名 +25%  §f龙鳞护符§7 护甲 +12",
             "§f凤羽翎§7 速度+缓降  §f麒麟角坠§7 幸运+回复",
             "§f狐尾坠§7 跳跃 II  §f锦囊§7 水肺+夜视",
             "§f铜镜§7 每 30 秒净化负面  §f司南§7 显示坐标"},
            {"十四、图鉴怎么用", "§7打开背包 → 左上角「§6✦ 王朝任务§7」→ 选「§6图鉴§7」页签：",
             "§7左侧是所有物品，点一下即可看到",
             "§f· 来源（合成配方或掉落 / 任务奖励）",
             "§f· 配方材料（直接显示物品图标）",
             "§f· 妙用（这把武器/饰品到底强在哪）",
             "§8按住 Shift 悬停背包里的物品，也能看到同样的说明。"},
            {"十五、开局 30 分钟路线", "§f1.§7 先挖玉与朱砂，做 §f青铜剑§7 与 §f王朝手札§7。",
             "§f2.§7 做 §f科举试卷§7 答题升官，做 §f玉玺§7 看档案。",
             "§f3.§7 攒材料升到 §f玉剑/巨阙§7，做 §f玉甲§7（减伤 60%）。",
             "§f4.§7 用 §f虎符§7 调兵、做 §f百宝妆匣§7 与饰品。",
             "§f5.§7 穿 §f玉门§7 进天朝、穿 §f冥门§7 进地府，收集龙晶。",
             "§8任务界面会一步步引导你，跟着做就不会迷路。"},
            {"王朝图鉴 · 完", "§7愿你的王朝长治久安。",
             "§8—— 制作：Dynasty Mod ——", "", "§8本指南为模组内置，无需 Patchouli。", ""},
    };

    private int page = 0;

    public GuideScreen() {
        super(Component.translatable("screen.dynasty.guide"));
    }

    @Override
    protected void init() {
        int y = this.height - 40;
        this.addRenderableWidget(Button.builder(Component.literal("◀ 上一页"), b -> this.flip(-1))
                .bounds(this.width / 2 - 110, y, 100, 20).build());
        this.addRenderableWidget(Button.builder(Component.literal("下一页 ▶"), b -> this.flip(1))
                .bounds(this.width / 2 + 10, y, 100, 20).build());
        this.addRenderableWidget(Button.builder(Component.literal("关闭"), b -> this.onClose())
                .bounds(this.width / 2 - 40, y + 24, 80, 20).build());
    }

    private void flip(int delta) {
        this.page = Math.max(0, Math.min(PAGES.length - 1, this.page + delta));
    }

    @Override
    public boolean keyPressed(int keyCode, int scanCode, int modifiers) {
        if (keyCode == GLFW.GLFW_KEY_LEFT || keyCode == GLFW.GLFW_KEY_A) {
            this.flip(-1);
            return true;
        }
        if (keyCode == GLFW.GLFW_KEY_RIGHT || keyCode == GLFW.GLFW_KEY_D) {
            this.flip(1);
            return true;
        }
        return super.keyPressed(keyCode, scanCode, modifiers);
    }

    @Override
    public boolean mouseScrolled(double mouseX, double mouseY, double delta) {
        this.flip(delta > 0 ? -1 : 1);
        return true;
    }

    @Override
    public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        this.renderBackground(graphics);
        int centerX = this.width / 2;
        int top = 40;
        graphics.fill(centerX - 180, top - 16, centerX + 180, this.height - 52, 0xC0000000);

        String[] content = PAGES[this.page];
        graphics.drawCenteredString(this.font, content[0], centerX, top, 0xFFE9B8);
        int y = top + 22;
        for (int i = 1; i < content.length; i++) {
            graphics.drawCenteredString(this.font, content[i], centerX, y, 0xFFFFFF);
            y += 14;
        }
        graphics.drawCenteredString(this.font,
                "§7第 " + (this.page + 1) + " / " + PAGES.length + " 页", centerX, this.height - 60, 0xAAAAAA);
        super.render(graphics, mouseX, mouseY, partialTick);
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }
}
