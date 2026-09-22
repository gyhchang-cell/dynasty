package com.dynasty.client;

import com.dynasty.bounty.BountyModel;
import com.dynasty.bounty.BountyStateMachine;
import com.dynasty.bounty.BountyView;
import com.dynasty.network.BountyActionPacket;
import com.dynasty.network.DynastyNetwork;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.util.FormattedCharSequence;

import java.util.List;

/**
 * 悬赏告示板界面（纯代码绘制，不依赖新贴图）。
 *
 * 布局按窗口尺寸计算（支持常见 GUI 缩放）：左边是今天的委托列表，右边是选中委托的详情与按钮；
 * 长文本用 {@code font.split} 折行并限制行数，**不会压到按钮上**。
 * 所有文字都走翻译键；客户端不做判定，只发操作意图。
 */
public class BountyBoardScreen extends Screen {

    private static final int ROW_HEIGHT = 22;
    private static final int MARGIN = 12;
    private static final int DETAIL_LINES = 6;

    private BountyView view;
    private int selected;

    private Button acceptButton;
    private Button abandonButton;
    private Button submitButton;
    private Button claimButton;

    public BountyBoardScreen(BountyView view) {
        super(Component.translatable("dynasty.bounty.gui.title"));
        this.view = view;
    }

    public void update(BountyView updated) {
        this.view = updated;
        if (selected >= updated.entries.size()) {
            selected = 0;
        }
        refreshButtons();
    }

    @Override
    protected void init() {
        int panelX = panelX();
        int buttonY = this.height - MARGIN - 20;
        int width = (this.width - MARGIN * 3) / 4;
        acceptButton = addRenderableWidget(Button.builder(Component.translatable("dynasty.bounty.gui.accept"),
                        button -> send("ACCEPT")).bounds(panelX, buttonY, width, 20).build());
        abandonButton = addRenderableWidget(Button.builder(Component.translatable("dynasty.bounty.gui.abandon"),
                        button -> send("ABANDON")).bounds(panelX + width + 4, buttonY, width, 20).build());
        submitButton = addRenderableWidget(Button.builder(Component.translatable("dynasty.bounty.gui.submit"),
                        button -> send("SUBMIT")).bounds(panelX + (width + 4) * 2, buttonY, width, 20).build());
        claimButton = addRenderableWidget(Button.builder(Component.translatable("dynasty.bounty.gui.claim"),
                        button -> send("CLAIM")).bounds(panelX + (width + 4) * 3, buttonY, width, 20).build());
        addRenderableWidget(Button.builder(Component.translatable("gui.done"),
                        button -> onClose()).bounds(this.width - MARGIN - 60, MARGIN, 60, 20).build());
        refreshButtons();
    }

    private int listX() {
        return MARGIN;
    }

    private int panelX() {
        return Math.max(MARGIN + 160, this.width / 2);
    }

    private int listWidth() {
        return panelX() - MARGIN - MARGIN / 2;
    }

    private int detailWidth() {
        return this.width - panelX() - MARGIN;
    }

    private int listTop() {
        return MARGIN + 34;
    }

    private BountyView.Entry selectedEntry() {
        if (view == null || view.entries.isEmpty()) {
            return null;
        }
        return view.entries.get(Math.max(0, Math.min(selected, view.entries.size() - 1)));
    }

    private void refreshButtons() {
        BountyView.Entry entry = selectedEntry();
        BountyView.State state = entry == null ? null : entry.state;
        if (acceptButton != null) {
            acceptButton.active = state == BountyView.State.AVAILABLE && view.activeCount < view.maxActive;
            abandonButton.active = state == BountyView.State.ACCEPTED || state == BountyView.State.READY;
            submitButton.active = entry != null && entry.type == BountyModel.Type.ACQUIRE
                    && state == BountyView.State.ACCEPTED;
            claimButton.active = state == BountyView.State.READY;
        }
    }

    private void send(String action) {
        BountyView.Entry entry = selectedEntry();
        if (entry != null) {
            DynastyNetwork.CHANNEL.sendToServer(new BountyActionPacket(action, entry.instanceId));
        }
    }

    @Override
    public boolean mouseClicked(double mouseX, double mouseY, int button) {
        if (mouseX >= listX() && mouseX <= listX() + listWidth() && view != null) {
            int index = (int) ((mouseY - listTop()) / ROW_HEIGHT);
            if (index >= 0 && index < view.entries.size()) {
                selected = index;
                refreshButtons();
                return true;
            }
        }
        return super.mouseClicked(mouseX, mouseY, button);
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }

    public static int maxActiveShown() {
        return BountyStateMachine.MAX_ACTIVE;
    }

    // ------------------------------------------------------------------ 绘制

    @Override
    public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        renderBackground(graphics);
        graphics.drawCenteredString(this.font, this.title, this.width / 2, MARGIN, 0xFFE8C86A);
        graphics.drawString(this.font, Component.translatable("dynasty.bounty.gui.header",
                view.day, view.activeCount, view.maxActive), listX(), MARGIN + 16, 0xFFA0A0A0, false);

        int y = listTop();
        for (int i = 0; i < view.entries.size(); i++) {
            BountyView.Entry entry = view.entries.get(i);
            int color = i == selected ? 0xFFFFFFFF : 0xFFB0B0B0;
            if (i == selected) {
                graphics.fill(listX() - 2, y - 2, listX() + listWidth() + 2, y + ROW_HEIGHT - 4, 0x60404040);
            }
            String title = statePrefix(entry).getString() + " " + this.font.plainSubstrByWidth(
                    Component.translatable(entry.titleKey).getString(), Math.max(40, listWidth() - 24));
            graphics.drawString(this.font, title, listX(), y, color, false);
            graphics.drawString(this.font, Component.translatable("dynasty.bounty.gui.progress",
                    entry.progress, entry.amount), listX() + 12, y + 10, 0xFF808080, false);
            y += ROW_HEIGHT;
        }

        BountyView.Entry entry = selectedEntry();
        if (entry != null) {
            renderDetail(graphics, entry);
        }
        if (view.statusKey != null) {
            graphics.drawString(this.font, Component.translatable(view.statusKey), panelX(),
                    this.height - MARGIN - 30, 0xFFFFD060, false);
        }
        super.render(graphics, mouseX, mouseY, partialTick);
    }

    private void renderDetail(GuiGraphics graphics, BountyView.Entry entry) {
        int px = panelX();
        int lineY = MARGIN + 16;
        graphics.drawString(this.font, Component.translatable(entry.titleKey), px, lineY, 0xFFE8C86A, false);
        lineY += 16;
        for (FormattedCharSequence line : wrap(Component.translatable(entry.descKey))) {
            if (lineY > MARGIN + 16 + DETAIL_LINES * 10 + 6) {
                break;
            }
            graphics.drawString(this.font, line, px, lineY, 0xFFD0D0D0, false);
            lineY += 10;
        }
        lineY += 6;
        graphics.drawString(this.font, Component.translatable("dynasty.bounty.gui.target",
                Component.translatable(entry.targetKey), entry.amount), px, lineY, 0xFFFFFFFF, false);
        lineY += 12;
        graphics.drawString(this.font, Component.translatable("dynasty.bounty.gui.progress",
                entry.progress, entry.amount), px, lineY, 0xFFFFFFFF, false);
        lineY += 12;
        graphics.drawString(this.font, Component.translatable("dynasty.bounty.gui.reward"), px, lineY,
                0xFFFFFFFF, false);
        lineY += 11;
        int bottom = this.height - MARGIN - 34;
        for (FormattedCharSequence line : wrap(rewardText(entry))) {
            if (lineY > bottom) {
                break;
            }
            graphics.drawString(this.font, line, px + 4, lineY, 0xFF9BE89B, false);
            lineY += 10;
        }
    }

    private Component rewardText(BountyView.Entry entry) {
        StringBuilder builder = new StringBuilder();
        for (BountyModel.Stack stack : entry.rewardItems()) {
            net.minecraft.world.item.Item item = net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(
                    new net.minecraft.resources.ResourceLocation(stack.item));
            String name = item == null ? stack.item
                    : new net.minecraft.world.item.ItemStack(item).getHoverName().getString();
            if (builder.length() > 0) {
                builder.append("  ");
            }
            builder.append(name).append(" x").append(stack.count);
        }
        if (entry.experience > 0) {
            builder.append("  XP+").append(entry.experience);
        }
        return Component.literal(builder.toString());
    }

    private Component statePrefix(BountyView.Entry entry) {
        return switch (entry.state) {
            case AVAILABLE -> Component.translatable("dynasty.bounty.gui.state.available");
            case ACCEPTED -> Component.translatable("dynasty.bounty.gui.state.accepted");
            case READY -> Component.translatable("dynasty.bounty.gui.state.ready");
            case CLAIMED -> Component.translatable("dynasty.bounty.gui.state.claimed");
            case LOCKED -> Component.translatable("dynasty.bounty.gui.state.locked");
        };
    }

    /** 折行并按详情面板宽度限宽：长文本不会压到按钮上。 */
    private List<FormattedCharSequence> wrap(Component text) {
        return this.font.split(text, Math.max(80, detailWidth()));
    }
}
