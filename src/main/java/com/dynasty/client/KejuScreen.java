package com.dynasty.client;

import com.dynasty.network.AnswerKejuPacket;
import com.dynasty.network.DynastyNetwork;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;

/**
 * 科举答题界面（GUI）。
 * The Keju (imperial examination) answer screen.
 */
@SuppressWarnings("null")
public class KejuScreen extends Screen {

    private static final String[] MARKS = {"①", "②", "③"};

    private final int index;
    private final String question;
    private final String[] options;

    public KejuScreen(int index, String question, String[] options) {
        super(Component.translatable("screen.dynasty.keju"));
        this.index = index;
        this.question = question;
        this.options = options;
    }

    @Override
    protected void init() {
        int w = 240;
        int x = (this.width - w) / 2;
        int y = this.height / 2 - 10;
        for (int i = 0; i < this.options.length; i++) {
            final int choice = i + 1;
            this.addRenderableWidget(Button.builder(
                    Component.literal(MARKS[i] + " " + this.options[i]),
                    b -> {
                        DynastyNetwork.CHANNEL.sendToServer(new AnswerKejuPacket(this.index, choice));
                        this.onClose();
                    }).bounds(x, y + i * 26, w, 20).build());
        }
    }

    @Override
    public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        this.renderBackground(graphics);
        graphics.drawCenteredString(this.font, "§6✦ 科举考试 ✦", this.width / 2, this.height / 2 - 80, 0xFFFFFF);
        graphics.drawCenteredString(this.font, this.question, this.width / 2, this.height / 2 - 55, 0xFFFFFF);
        graphics.drawCenteredString(this.font, "§7请选择一个答案", this.width / 2, this.height / 2 - 33, 0xAAAAAA);
        super.render(graphics, mouseX, mouseY, partialTick);
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }
}
