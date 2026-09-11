package com.dynasty.client;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;

/**
 * 王朝档案界面（官阶 / 功名 / 忠诚 / 叛乱）——由玉玺打开，无需指令。
 * Dynasty records screen (rank / merit / loyalty / rebellion), opened by the Jade Seal.
 */
@SuppressWarnings("null")
public class StatsScreen extends Screen {

    private static final String[] RANK_ZH = {
            "布衣", "童生", "秀才", "举人", "贡士", "进士", "翰林", "侍郎", "尚书", "大学士", "丞相", "摄政王"
    };

    private int rank, merit, loyalty, rebellion;

    public StatsScreen() {
        super(Component.literal("王朝档案"));
    }

    public void refresh(int rankIn, int meritIn, int loyaltyIn, int rebellionIn) {
        this.rank = rankIn;
        this.merit = meritIn;
        this.loyalty = loyaltyIn;
        this.rebellion = rebellionIn;
    }

    @Override
    protected void init() {
        this.addRenderableWidget(Button.builder(Component.literal("关闭"), b -> this.onClose())
                .bounds(this.width / 2 - 40, this.height / 2 + 70, 80, 20).build());
    }

    @Override
    public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        this.renderBackground(graphics);
        int cx = this.width / 2;
        int top = this.height / 2 - 60;
        graphics.fill(cx - 120, top - 18, cx + 120, top + 96, 0xC8000000);
        graphics.drawCenteredString(this.font, "§6✦ 王朝档案 ✦", cx, top - 8, 0xFFFFFF);
        String rankName = RANK_ZH[Math.max(0, Math.min(RANK_ZH.length - 1, this.rank))];
        graphics.drawCenteredString(this.font, "§7官阶：§f" + rankName, cx, top + 12, 0xFFFFFF);
        graphics.drawCenteredString(this.font, "§7功名：§f" + this.merit + " §8(每 100 功名晋升一阶)", cx, top + 28, 0xFFFFFF);
        graphics.drawCenteredString(this.font, "§7忠诚：§f" + this.loyalty + "%", cx, top + 44, 0xFFFFFF);
        graphics.drawCenteredString(this.font, "§7叛乱：§f" + this.rebellion + "%", cx, top + 60, 0xFFFFFF);
        graphics.drawCenteredString(this.font, this.rebellion >= 80 ? "§c民怨沸腾，叛军将起！"
                : (this.rebellion >= 40 ? "§e民心浮动，宜施仁政。" : "§a民心安定。"), cx, top + 78, 0xFFFFFF);
        super.render(graphics, mouseX, mouseY, partialTick);
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }
}
