package com.dynasty.keju;

/**
 * 答题界面的纯几何计算（不引用任何 Minecraft / 客户端类，可脱离游戏单测）。
 *
 * {@code KejuScreen} 用同一份公式排版：面板居中且不越出窗口、可视区至少 24 像素、
 * 内容超高时给出滚动范围、滚动值被夹在范围内、鼠标命中换算用同一个 contentTop。
 * 之所以把它独立出来，是因为界面换行依赖客户端字体、无法在无客户端环境里跑；
 * 但「小窗口放不下就滚、绝不越界」这类结论可以在这里用测试断言。
 *
 * Pure geometry for the exam screen so layout/scroll invariants can be tested
 * without a Minecraft client. KejuScreen uses exactly these formulas.
 */
public final class KejuLayout {

    /** 面板到窗口边缘的最小留白 / outer margin */
    public static final int OUTER = 16;
    /** 面板内边距 / inner padding */
    public static final int PAD = 10;
    /** 字体行高 / text line height */
    public static final int LINE = 9;
    /** 选项之间的间隔 / gap between options */
    public static final int OPTION_GAP = 6;
    /** 滚轮一格 / scroll step per wheel notch */
    public static final int SCROLL_STEP = 18;
    /** 面板最小宽度 / minimum panel width */
    public static final int MIN_PANEL = 200;
    /** 面板最大宽度（宽屏也不拉成长条）/ maximum panel width */
    public static final int MAX_PANEL = 420;
    /** 面板最小高度 / minimum panel height */
    public static final int MIN_PANEL_HEIGHT = 96;
    /** 标题占的行数 / title lines */
    public static final int TITLE_LINES = 1;
    /** 标题区额外留白 / extra space under the title */
    public static final int TITLE_EXTRA = 8;
    /** 题干区额外留白（含分隔线）/ extra space under the question block */
    public static final int QUESTION_EXTRA = 10;
    /** 选项卡片上下内边距合计 / vertical padding inside an option card */
    public static final int OPTION_PADDING = 8;
    /** 选项文字缩进 + 序号占位 / option text inset */
    public static final int TEXT_INSET = 14;
    /** 可视区最小高度 / minimum viewport height */
    public static final int MIN_VIEWPORT = 24;

    private final int width;
    private final int height;
    private final int panelX;
    private final int panelY;
    private final int panelW;
    private final int panelH;
    private final int viewTop;
    private final int viewBottom;

    private KejuLayout(int width, int height, int panelX, int panelY, int panelW, int panelH,
                       int viewTop, int viewBottom) {
        this.width = width;
        this.height = height;
        this.panelX = panelX;
        this.panelY = panelY;
        this.panelW = panelW;
        this.panelH = panelH;
        this.viewTop = viewTop;
        this.viewBottom = viewBottom;
    }

    /** 按窗口逻辑尺寸（已含 GUI 缩放）算出面板与可视区。 */
    public static KejuLayout of(int width, int height) {
        int panelW = Math.min(MAX_PANEL, Math.max(MIN_PANEL, width - OUTER * 2));
        int panelH = Math.max(MIN_PANEL_HEIGHT, height - OUTER * 2);
        // 窗口特别小时，面板退让为整个窗口，但绝不越界（宁可整屏面板，不画到屏幕外）
        panelW = Math.min(panelW, Math.max(1, width));
        panelH = Math.min(panelH, Math.max(1, height));
        int panelX = (width - panelW) / 2;
        int panelY = (height - panelH) / 2;
        int titleH = TITLE_LINES * LINE + TITLE_EXTRA;
        int footer = panelH < 150 ? 28 : 40;
        int viewTop = panelY + PAD + titleH;
        int viewBottom = Math.max(viewTop + MIN_VIEWPORT, panelY + panelH - PAD - footer);
        return new KejuLayout(width, height, panelX, panelY, panelW, panelH, viewTop, viewBottom);
    }

    public int width() {
        return width;
    }

    public int height() {
        return height;
    }

    public int panelX() {
        return panelX;
    }

    public int panelY() {
        return panelY;
    }

    public int panelW() {
        return panelW;
    }

    public int panelH() {
        return panelH;
    }

    public int viewTop() {
        return viewTop;
    }

    public int viewBottom() {
        return viewBottom;
    }

    /** 面板左右内边距之间的可用宽度。/ usable width inside the panel. */
    public int innerWidth() {
        return panelW - PAD * 2;
    }

    /** 文本换行宽度（留出序号缩进）。/ wrap width for question text. */
    public int textWidth() {
        return Math.max(40, innerWidth() - TEXT_INSET);
    }

    public int viewportHeight() {
        return Math.max(1, viewBottom - viewTop);
    }

    /** 题干区高度（按换行后的行数）。/ height of the question block. */
    public static int questionBlockHeight(int questionLines) {
        return Math.max(1, questionLines) * LINE + QUESTION_EXTRA;
    }

    /** 选项卡片高度（随换行行数增长）。/ height of one option card. */
    public static int optionHeight(int optionLines) {
        return Math.max(1, optionLines) * LINE + OPTION_PADDING;
    }

    /** 内容总高度：题干区 + 若干选项（最后一个之后不留间隔）。 */
    public static int contentHeight(int questionLines, int... optionLineCounts) {
        int cursor = questionBlockHeight(questionLines);
        for (int lines : optionLineCounts) {
            cursor += optionHeight(lines) + OPTION_GAP;
        }
        return optionLineCounts.length == 0 ? cursor : cursor - OPTION_GAP;
    }

    /** 每个选项相对内容顶部的偏移（渲染与命中测试共用同一份）。 */
    public static int[] optionTops(int questionLines, int... optionLineCounts) {
        int[] tops = new int[optionLineCounts.length];
        int cursor = questionBlockHeight(questionLines);
        for (int i = 0; i < optionLineCounts.length; i++) {
            tops[i] = cursor;
            cursor += optionHeight(optionLineCounts[i]) + OPTION_GAP;
        }
        return tops;
    }

    /** 最大滚动量（内容没超出可视区时为 0）。/ maximum scroll offset. */
    public int maxScroll(int contentHeight) {
        return Math.max(0, contentHeight - viewportHeight());
    }

    public int clampScroll(int scroll, int contentHeight) {
        return clamp(scroll, 0, maxScroll(contentHeight));
    }

    /** 内容顶部的屏幕 y（内容坐标 = 屏幕 y - contentTop）。/ screen y of the content top. */
    public int contentTop(int scroll) {
        return viewTop - scroll;
    }

    /** 鼠标是否落在可滚动可视区内 / is the mouse inside the scroll viewport. */
    public boolean insideViewport(double mouseX, double mouseY) {
        return mouseY >= viewTop && mouseY < viewBottom && mouseX >= panelX && mouseX <= panelX + panelW;
    }

    /** 让某个选项完全可见所需的滚动值（键盘切换时用）。 */
    public int scrollToReveal(int optionTop, int optionBottom, int scroll, int contentHeight) {
        if (optionTop < scroll) {
            return clampScroll(optionTop, contentHeight);
        }
        if (optionBottom > scroll + viewportHeight()) {
            return clampScroll(optionBottom - viewportHeight(), contentHeight);
        }
        return clampScroll(scroll, contentHeight);
    }

    public static int clamp(int value, int min, int max) {
        return value < min ? min : (value > max ? max : value);
    }
}
