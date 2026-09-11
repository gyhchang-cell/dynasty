package com.dynasty.client;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;

/**
 * 虎符调兵界面：选择阵型与人数，无需输入指令。
 * Tiger Tally screen: pick a formation and count, no commands required.
 */
@SuppressWarnings("null")
public class ArmyScreen extends Screen {

    private static final String[][] FORMATIONS = {
            {"square", "方阵", "均衡推进"},
            {"wedge", "锋矢阵", "集中突破"},
            {"crane", "雁行阵", "两翼包抄"},
            {"line", "横阵", "正面拒敌"},
            {"circle", "圆阵", "四面固守"},
    };

    private int formation = 1;
    private int count = 12;

    public ArmyScreen() {
        super(Component.literal("虎符调兵"));
    }

    @Override
    protected void init() {
        int cx = this.width / 2;
        int top = this.height / 2 - 70;
        for (int i = 0; i < FORMATIONS.length; i++) {
            final int idx = i;
            this.addRenderableWidget(Button.builder(Component.literal(FORMATIONS[i][1]), b -> {
                this.formation = idx;
                this.rebuildWidgets();
            }).bounds(cx - 150, top + i * 22, 90, 20).build());
        }
        this.addRenderableWidget(Button.builder(Component.literal("− 4"), b -> this.changeCount(-4))
                .bounds(cx + 10, top + 22, 50, 20).build());
        this.addRenderableWidget(Button.builder(Component.literal("+ 4"), b -> this.changeCount(4))
                .bounds(cx + 66, top + 22, 50, 20).build());
        this.addRenderableWidget(Button.builder(Component.literal("§6列阵"), b -> {
            ClientArmy.send(this.formation, this.count);
            this.onClose();
        }).bounds(cx - 60, top + 110, 120, 20).build());
        this.addRenderableWidget(Button.builder(Component.literal("关闭"), b -> this.onClose())
                .bounds(cx - 40, top + 134, 80, 20).build());
    }

    private void changeCount(int delta) {
        this.count = Math.max(4, Math.min(64, this.count + delta));
        this.rebuildWidgets();
    }

    @Override
    public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        this.renderBackground(graphics);
        int cx = this.width / 2;
        int top = this.height / 2 - 70;
        graphics.fill(cx - 170, top - 26, cx + 170, top + 160, 0xC8000000);
        graphics.drawCenteredString(this.font, "§6✦ 虎符 · 调兵列阵 ✦", cx, top - 16, 0xFFFFFF);
        graphics.drawString(this.font, "§7选择阵型：", cx - 150, top - 2, 0xAAAAAA);
        graphics.drawString(this.font, "§7人数：§f" + this.count + " §8(4-64)", cx + 10, top + 10, 0xFFFFFF);
        graphics.drawString(this.font, "§e" + FORMATIONS[this.formation][1] + " §7— §f"
                + FORMATIONS[this.formation][2], cx - 150, top + 92, 0xFFFFFF);
        graphics.drawCenteredString(this.font, "§8按「列阵」召唤禁军；他们会跟随你并攻击怪物", cx, top + 148, 0xFFFFFF);
        super.render(graphics, mouseX, mouseY, partialTick);
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }
}
