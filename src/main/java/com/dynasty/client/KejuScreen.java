package com.dynasty.client;

import com.dynasty.keju.KejuLayout;
import com.dynasty.network.AnswerKejuPacket;
import com.dynasty.network.DynastyNetwork;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.util.FormattedCharSequence;
import org.lwjgl.glfw.GLFW;

import java.util.ArrayList;
import java.util.List;

/**
 * 科举答题界面（GUI）。
 *
 * 克制的国风试卷面板：标题 / 题干区 / 三个选项区 / 固定底部的操作提示与「确认作答」按钮，
 * 全部用现有字体与 {@code GuiGraphics} 绘制（不新增任何贴图）。题干与选项按实际字体宽度
 * 换行，选项高度随内容增长；内容超过可视区时用滚轮滚动（scissor 裁剪，不截断文字、
 * 不缩小字号）。支持鼠标点击、数字键 1/2/3、↑↓ / Tab 切换、Enter 确认；
 * Esc 关闭不判错也不发奖励，且同一次界面最多发送一次答案包。
 *
 * 本轮没有结果回包，界面不会假装知道答对 / 答错：提交后直接关闭，
 * 判分反馈仍由服务端聊天消息给出。
 *
 * Keju answer screen: a restrained exam-paper panel with wrapped text, a
 * scrollable question/option area and a fixed confirm button.
 */
public class KejuScreen extends Screen {

    /** 选项序号，与数字键 1/2/3 一致。/ option marks matching keys 1/2/3. */
    private static final String[] MARKS = {"①", "②", "③"};

    // 排版常量与纯几何类（com.dynasty.keju.KejuLayout）共用一份，可脱离游戏单测
    private static final int LINE = KejuLayout.LINE;
    private static final int OPTION_GAP = KejuLayout.OPTION_GAP;
    private static final int SCROLL_STEP = KejuLayout.SCROLL_STEP;

    private final int index;
    private final String question;
    private final String[] options;

    /** 面板内边距（与几何类共用）。*/
    private static final int PAD = KejuLayout.PAD;

    /** 纯几何结果（窗口尺寸变化时在 relayout 中重算；公式见 com.dynasty.keju.KejuLayout）。*/
    private KejuLayout layout = KejuLayout.of(320, 240);

    private int panelX;
    private int panelY;
    private int panelW;
    private int panelH;
    private int viewTop;
    private int viewBottom;
    private int contentHeight;
    private int scroll;

    /** 已选中的选项（0 = 未选择）；提交按钮据此启用。*/
    private int selected;
    /** 键盘高亮（与 selected 同步移动）。*/
    private int focused;
    /** 防止连点：同一次界面只发一个答案包。*/
    private boolean submitted;

    private final List<FormattedCharSequence> questionLines = new ArrayList<>();
    private final List<List<FormattedCharSequence>> optionLines = new ArrayList<>();
    private final List<Integer> optionTops = new ArrayList<>();
    private final List<Integer> optionHeights = new ArrayList<>();
    private Button confirm;

    public KejuScreen(int index, String question, String[] options) {
        super(Component.translatable("screen.dynasty.keju"));
        this.index = index;
        this.question = question == null ? "" : question;
        this.options = options == null ? new String[]{} : options.clone();
    }

    @Override
    protected void init() {
        relayout();
    }

    /** 按当前窗口逻辑尺寸重算面板、换行与滚动范围（缩放或调整窗口后都会重跑）。 */
    private void relayout() {
        KejuLayout geometry = KejuLayout.of(this.width, this.height);
        this.layout = geometry;
        panelX = geometry.panelX();
        panelY = geometry.panelY();
        panelW = geometry.panelW();
        panelH = geometry.panelH();
        viewTop = geometry.viewTop();
        viewBottom = geometry.viewBottom();
        int inner = geometry.innerWidth();
        int textWidth = geometry.textWidth();

        questionLines.clear();
        questionLines.addAll(wrap(this.question, textWidth));
        optionLines.clear();
        optionHeights.clear();
        for (int i = 0; i < this.options.length; i++) {
            List<FormattedCharSequence> lines =
                    wrap(MARKS[Math.min(i, MARKS.length - 1)] + " " + this.options[i], textWidth);
            optionLines.add(lines);
            optionHeights.add(lines.size() * LINE + 8);
        }

        int contentLines = questionLines.size();
        int[] tops = new int[optionLines.size()];
        int cursor = KejuLayout.questionBlockHeight(contentLines);
        for (int i = 0; i < optionLines.size(); i++) {
            tops[i] = cursor;
            cursor += optionHeights.get(i) + OPTION_GAP;
        }
        optionTops.clear();
        for (int top : tops) {
            optionTops.add(top);
        }
        contentHeight = optionLines.isEmpty() ? KejuLayout.questionBlockHeight(contentLines) : cursor - OPTION_GAP;
        scroll = geometry.clampScroll(scroll, contentHeight);

        int buttonW = Math.max(80, Math.min(160, inner));
        this.clearWidgets();
        confirm = Button.builder(Component.literal("确认作答"), b -> submit())
                .bounds(panelX + (panelW - buttonW) / 2, panelY + panelH - 10 - 18, buttonW, 18)
                .build();
        confirm.active = selected > 0 && !submitted;
        this.addRenderableWidget(confirm);
    }

    /** 按实际字体宽度换行；空文本也占一行，保证排版稳定。 */
    private List<FormattedCharSequence> wrap(String text, int width) {
        List<FormattedCharSequence> lines = new ArrayList<>(this.font.split(Component.literal(text), width));
        if (lines.isEmpty()) {
            lines.add(Component.empty().getVisualOrderText());
        }
        return lines;
    }

    private int viewportHeight() {
        return layout.viewportHeight();
    }

    private int maxScroll() {
        return layout.maxScroll(contentHeight);
    }

    private static int clamp(int value, int min, int max) {
        return KejuLayout.clamp(value, min, max);
    }

    /** 滚动到让某个选项完全可见（键盘切换时用，鼠标滚动不强制）。 */
    private void scrollIntoView(int slot) {
        if (slot < 1 || slot > optionTops.size()) {
            return;
        }
        int top = optionTops.get(slot - 1);
        scroll = layout.scrollToReveal(top, top + optionHeights.get(slot - 1), scroll, contentHeight);
    }

    @Override
    public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        this.renderBackground(graphics);
        graphics.fill(panelX - 1, panelY - 1, panelX + panelW + 1, panelY + panelH + 1, 0xFF3B2F22);
        graphics.fill(panelX, panelY, panelX + panelW, panelY + panelH, 0xFFF3E9D2);
        graphics.drawCenteredString(this.font, this.title, panelX + panelW / 2, panelY + PAD, 0xFF6B4A16);

        graphics.enableScissor(panelX + 1, viewTop, panelX + panelW - 1, viewBottom);
        int contentTop = viewTop - scroll;
        int cursor = contentTop;
        for (FormattedCharSequence line : questionLines) {
            graphics.drawString(this.font, line, panelX + PAD, cursor, 0xFF241C14, false);
            cursor += LINE;
        }
        graphics.fill(panelX + PAD, cursor + 3, panelX + panelW - PAD, cursor + 4, 0x60724E22);
        for (int slot = 0; slot < optionLines.size(); slot++) {
            drawOption(graphics, slot, contentTop + optionTops.get(slot), mouseX, mouseY);
        }
        graphics.disableScissor();

        drawScrollBar(graphics);
        graphics.drawString(this.font, hint(), panelX + PAD, panelY + panelH - PAD - 30, 0xFF6B5A44, false);
        super.render(graphics, mouseX, mouseY, partialTick);
    }

    /** 单个选项卡片：底色随「已选 / 悬停 / 键盘焦点」变化，高度随换行数增长。 */
    private void drawOption(GuiGraphics graphics, int slot, int top, int mouseX, int mouseY) {
        int left = panelX + PAD;
        int right = panelX + panelW - PAD;
        int height = optionHeights.get(slot);
        boolean selectedHere = selected == slot + 1;
        boolean focusedHere = focused == slot + 1;
        boolean hovered = mouseX >= left && mouseX < right && mouseY >= top && mouseY < top + height;
        int background = selectedHere ? 0x66C9A961 : (hovered || focusedHere ? 0x33C9A961 : 0x14FFFFFF);
        graphics.fill(left, top, right, top + height, background);
        graphics.fill(left, top, left + 2, top + height, selectedHere ? 0xFF7A4B12 : 0x557A4B12);
        if (focusedHere) {
            graphics.fill(left, top, right, top + 1, 0xFF3F6FA8);
            graphics.fill(left, top + height - 1, right, top + height, 0xFF3F6FA8);
        }
        int color = selectedHere ? 0xFF4A2C05 : 0xFF241C14;
        int textY = top + 4;
        for (FormattedCharSequence line : optionLines.get(slot)) {
            graphics.drawString(this.font, line, left + 8, textY, color, false);
            textY += LINE;
        }
    }

    /** 内容超出可视区时画一条细滚动条（不遮字、不改变排版）。 */
    private void drawScrollBar(GuiGraphics graphics) {
        int max = maxScroll();
        if (max <= 0) {
            return;
        }
        int trackX = panelX + panelW - 5;
        graphics.fill(trackX, viewTop, trackX + 2, viewBottom, 0x30724E22);
        int height = Math.max(12, viewportHeight() * viewportHeight() / Math.max(1, contentHeight));
        int offset = (viewportHeight() - height) * scroll / max;
        graphics.fill(trackX, viewTop + offset, trackX + 2, viewTop + offset + height, 0xB0724E22);
    }

    /** 固定底部的一行操作提示（鼠标与键盘都能照做）。 */
    private String hint() {
        if (submitted) {
            return "§7已提交，等待放榜…";
        }
        if (selected == 0) {
            return "§71/2/3 或鼠标选择 · ↑↓/Tab 切换 · Esc 关闭";
        }
        return "§7已选 " + selected + " · Enter 或「确认作答」提交 · Esc 关闭";
    }

    @Override
    public boolean mouseClicked(double mouseX, double mouseY, int button) {
        if (super.mouseClicked(mouseX, mouseY, button)) {
            return true;
        }
        if (button != 0) {
            return false;
        }
        int slot = optionAt(mouseX, mouseY);
        if (slot > 0) {
            select(slot);
            return true;
        }
        return false;
    }

    @Override
    public boolean mouseScrolled(double mouseX, double mouseY, double delta) {
        if (maxScroll() <= 0) {
            return super.mouseScrolled(mouseX, mouseY, delta);
        }
        scroll = clamp(scroll - (int) Math.round(delta * SCROLL_STEP), 0, maxScroll());
        return true;
    }

    @Override
    public boolean keyPressed(int keyCode, int scanCode, int modifiers) {
        if (keyCode == GLFW.GLFW_KEY_1 || keyCode == GLFW.GLFW_KEY_2 || keyCode == GLFW.GLFW_KEY_3) {
            select(keyCode - GLFW.GLFW_KEY_1 + 1);
            return true;
        }
        if (keyCode == GLFW.GLFW_KEY_KP_1 || keyCode == GLFW.GLFW_KEY_KP_2 || keyCode == GLFW.GLFW_KEY_KP_3) {
            select(keyCode - GLFW.GLFW_KEY_KP_1 + 1);
            return true;
        }
        if (keyCode == GLFW.GLFW_KEY_TAB || keyCode == GLFW.GLFW_KEY_DOWN || keyCode == GLFW.GLFW_KEY_UP) {
            int step = keyCode == GLFW.GLFW_KEY_UP || (modifiers & GLFW.GLFW_MOD_SHIFT) != 0 ? -1 : 1;
            moveFocus(step);
            return true;
        }
        if (keyCode == GLFW.GLFW_KEY_ENTER || keyCode == GLFW.GLFW_KEY_KP_ENTER) {
            submit();
            return true;
        }
        // Esc 由父类处理：只关界面，不判错、不发奖励。
        return super.keyPressed(keyCode, scanCode, modifiers);
    }

    /** 选中某个选项（越界 / 已提交时忽略）。 */
    private void select(int slot) {
        if (submitted || slot < 1 || slot > optionLines.size()) {
            return;
        }
        selected = slot;
        focused = slot;
        if (confirm != null) {
            confirm.active = true;
        }
    }

    /** 键盘循环切换：Tab / ↓ 前进，Shift+Tab / ↑ 后退，并保证选中项可见。 */
    private void moveFocus(int step) {
        int count = optionLines.size();
        if (submitted || count <= 0) {
            return;
        }
        int current = focused == 0 ? (step > 0 ? 0 : count + 1) : focused;
        int next = current + step;
        if (next > count) {
            next = 1;
        } else if (next < 1) {
            next = count;
        }
        select(next);
        scrollIntoView(next);
    }

    /** 鼠标命中测试：把屏幕坐标换算成内容坐标再比对选项区间。 */
    private int optionAt(double mouseX, double mouseY) {
        if (!layout.insideViewport(mouseX, mouseY)) {
            return 0;
        }
        int contentY = (int) mouseY - layout.contentTop(scroll);
        for (int slot = 0; slot < optionTops.size(); slot++) {
            int top = optionTops.get(slot);
            if (contentY >= top && contentY < top + optionHeights.get(slot)) {
                return slot + 1;
            }
        }
        return 0;
    }

    /** 提交作答：未选择不发；同一次界面最多发一个包（连点无效），随后关闭。 */
    private void submit() {
        if (submitted || selected <= 0) {
            return;
        }
        submitted = true;
        if (confirm != null) {
            confirm.active = false;
        }
        DynastyNetwork.CHANNEL.sendToServer(new AnswerKejuPacket(index, selected));
        this.onClose();
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }
}
