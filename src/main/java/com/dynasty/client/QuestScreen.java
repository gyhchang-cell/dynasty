package com.dynasty.client;

import com.dynasty.DynastyQuests;
import com.dynasty.network.DynastyNetwork;
import com.dynasty.network.QuestClaimPacket;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;

import java.util.ArrayList;
import java.util.List;

/**
 * 王朝任务界面：两个页签 —— 「任务」与「图鉴」（来源 / 配方 / 妙用）。
 * Quest screen with two tabs: quests and the item codex (source / recipe / use).
 */
@SuppressWarnings("null")
public class QuestScreen extends Screen {

    private static final int PER_PAGE = 10;

    private int mode = 0;            // 0 = 任务 / 1 = 图鉴
    private int chapter = 0;
    private int selected = -1;
    private int codexPage = 0;
    private int codexSelected = 0;

    public QuestScreen() {
        super(Component.literal("王朝任务"));
    }

    private boolean zh() {
        return DynastyItemInfo.chinese();
    }

    private List<DynastyQuests.Quest> chapterQuests() {
        List<DynastyQuests.Quest> out = new ArrayList<>();
        String name = DynastyQuests.CHAPTERS[chapter];
        for (DynastyQuests.Quest q : DynastyQuests.all()) {
            if (q.chapter.equals(name)) {
                out.add(q);
            }
        }
        return out;
    }

    private DynastyQuests.Quest selectedQuest() {
        List<DynastyQuests.Quest> list = chapterQuests();
        return selected >= 0 && selected < list.size() ? list.get(selected) : null;
    }

    private List<com.dynasty.DynastyCodex.Entry> codexEntries() {
        List<com.dynasty.DynastyCodex.Entry> entries = com.dynasty.DynastyCodex.all();
        int pages = Math.max(1, (entries.size() + PER_PAGE - 1) / PER_PAGE);
        this.codexPage = Math.max(0, Math.min(pages - 1, this.codexPage));
        int from = this.codexPage * PER_PAGE;
        return entries.subList(from, Math.min(entries.size(), from + PER_PAGE));
    }

    @Override
    protected void init() {
        int x0 = this.width / 2 - 200;
        int y0 = this.height / 2 - 110;

        this.addRenderableWidget(Button.builder(
                Component.literal(mode == 0 ? "§6✦ 任务" : "§7任务"), b -> {
                    this.mode = 0;
                    this.rebuildWidgets();
                }).bounds(x0 + 8, y0 + 4, 80, 18).build());
        this.addRenderableWidget(Button.builder(
                Component.literal(mode == 1 ? "§6✦ 图鉴" : "§7图鉴"), b -> {
                    this.mode = 1;
                    this.rebuildWidgets();
                }).bounds(x0 + 92, y0 + 4, 80, 18).build());

        if (this.mode == 0) {
            initQuests(x0, y0);
        } else {
            initCodex(x0, y0);
        }
        this.addRenderableWidget(Button.builder(Component.literal("关闭"), b -> this.onClose())
                .bounds(x0 + 320, y0 + 198, 70, 20).build());
    }

    private void initQuests(int x0, int y0) {
        for (int i = 0; i < DynastyQuests.CHAPTERS.length; i++) {
            final int idx = i;
            boolean active = i == this.chapter;
            this.addRenderableWidget(Button.builder(
                    Component.literal((active ? "§e" : "§7") + DynastyQuests.CHAPTERS[i]),
                    b -> {
                        this.chapter = idx;
                        this.selected = -1;
                        this.rebuildWidgets();
                    }).bounds(x0 + 8, y0 + 26 + i * 22, 100, 20).build());
        }

        List<DynastyQuests.Quest> quests = chapterQuests();
        for (int i = 0; i < quests.size(); i++) {
            final int idx = i;
            DynastyQuests.Quest q = quests.get(i);
            int progress = ClientQuests.progress(q.index);
            boolean done = ClientQuests.claimed(q.index);
            boolean ready = progress >= q.need && !done;
            String mark = done ? "§a✔ " : (ready ? "§e✦ " : "§8· ");
            this.addRenderableWidget(Button.builder(
                    Component.literal(mark + q.title + " §8" + progress + "/" + q.need),
                    b -> {
                        this.selected = idx;
                        this.rebuildWidgets();
                    }).bounds(x0 + 116, y0 + 26 + i * 22, 130, 20).build());
        }

        DynastyQuests.Quest quest = selectedQuest();
        if (quest != null && !ClientQuests.claimed(quest.index)
                && ClientQuests.progress(quest.index) >= quest.need) {
            this.addRenderableWidget(Button.builder(Component.literal("§6领取奖励"), b ->
                    DynastyNetwork.CHANNEL.sendToServer(new QuestClaimPacket(quest.index)))
                    .bounds(x0 + 218, y0 + 198, 90, 20).build());
        }
    }

    private static ItemStack iconOf(String id) {
        net.minecraft.world.item.Item item = net.minecraftforge.registries.ForgeRegistries.ITEMS
                .getValue(new net.minecraft.resources.ResourceLocation(id));
        return item == null ? ItemStack.EMPTY : new ItemStack(item);
    }

    private void initCodex(int x0, int y0) {
        List<com.dynasty.DynastyCodex.Entry> entries = codexEntries();
        int from = this.codexPage * PER_PAGE;
        for (int i = 0; i < entries.size(); i++) {
            final int idx = from + i;
            boolean active = idx == this.codexSelected;
            com.dynasty.DynastyCodex.Entry entry = entries.get(i);
            ItemStack icon = iconOf("dynasty:" + entry.id());
            this.addRenderableWidget(Button.builder(
                    Component.literal((active ? "§e" : "§7") + icon.getHoverName().getString()),
                    b -> {
                        this.codexSelected = idx;
                        this.rebuildWidgets();
                    }).bounds(x0 + 30, y0 + 30 + i * 17, 140, 15).build());
        }
        this.addRenderableWidget(Button.builder(Component.literal("◀"), b -> {
            this.codexPage--;
            this.rebuildWidgets();
        }).bounds(x0 + 8, y0 + 198, 22, 18).build());
        this.addRenderableWidget(Button.builder(Component.literal("▶"), b -> {
            this.codexPage++;
            this.rebuildWidgets();
        }).bounds(x0 + 148, y0 + 198, 22, 18).build());
    }

    @Override
    public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        this.renderBackground(graphics);
        int x0 = this.width / 2 - 200;
        int y0 = this.height / 2 - 110;
        graphics.fill(x0, y0, x0 + 400, y0 + 226, 0xE0101016);
        graphics.fill(x0 + 2, y0 + 2, x0 + 398, y0 + 24, 0xFF6B1F1F);
        graphics.drawCenteredString(this.font, "§6✦ 王朝任务 · 遊历指南 ✦", this.width / 2, y0 + 8, 0xFFFFFF);
        if (this.mode == 0) {
            renderQuests(graphics, x0, y0);
        } else {
            renderCodex(graphics, x0, y0);
        }
        super.render(graphics, mouseX, mouseY, partialTick);
    }

    private void renderQuests(GuiGraphics graphics, int x0, int y0) {
        int claimed = 0;
        for (DynastyQuests.Quest q : DynastyQuests.all()) {
            if (ClientQuests.claimed(q.index)) {
                claimed++;
            }
        }
        graphics.drawString(this.font, "§7进度：§f" + claimed + "§7/§f" + DynastyQuests.count(),
                x0 + 8, y0 + 210, 0xFFFFFF);

        DynastyQuests.Quest quest = selectedQuest();
        int dx = x0 + 252;
        if (quest == null) {
            graphics.drawString(this.font, zh() ? "§7← 选择章节与任务查看详情" : "§7← pick a chapter and quest",
                    dx - 8, y0 + 40, 0xAAAAAA);
            return;
        }
        int progress = ClientQuests.progress(quest.index);
        boolean done = ClientQuests.claimed(quest.index);
        graphics.drawString(this.font, "§e" + quest.title, dx, y0 + 30, 0xFFFFFF);
        int lineY = y0 + 48;
        for (String line : wrap(quest.desc, 15)) {
            graphics.drawString(this.font, "§7" + line, dx, lineY, 0xFFFFFF);
            lineY += 12;
        }
        lineY += 6;
        graphics.drawString(this.font, "§7目标：§f" + progress + " / " + quest.need, dx, lineY, 0xFFFFFF);
        lineY += 16;
        if (quest.requires.length > 0) {
            StringBuilder sb = new StringBuilder("§7前置：");
            boolean allDone = true;
            for (int req : quest.requires) {
                DynastyQuests.Quest pre = DynastyQuests.get(req);
                boolean ok = ClientQuests.claimed(req);
                allDone &= ok;
                sb.append(ok ? "§a" : "§c").append(pre == null ? "?" : pre.title).append("§7 ");
            }
            graphics.drawString(this.font, sb.toString(), dx, lineY, 0xFFFFFF);
            lineY += 14;
            if (!allDone) {
                graphics.drawString(this.font, zh() ? "§c请先完成前置任务" : "§cFinish the prerequisites first",
                        dx, lineY, 0xFFFFFF);
            }
        }
        lineY += 18;
        graphics.drawString(this.font, zh() ? "§7奖励：" : "§7Rewards:", dx, lineY, 0xFFFFFF);
        int rx = dx + 40;
        for (ItemStack reward : quest.rewards()) {
            graphics.renderItem(reward, rx, lineY - 4);
            graphics.renderItemDecorations(this.font, reward, rx, lineY - 4);
            rx += 20;
        }
        lineY += 26;
        graphics.drawString(this.font, done ? "§a已完成" : (progress >= quest.need ? "§e可领取" : "§7进行中"),
                dx, lineY, 0xFFFFFF);
    }

    private void renderCodex(GuiGraphics graphics, int x0, int y0) {
        List<com.dynasty.DynastyCodex.Entry> entries = codexEntries();
        int from = this.codexPage * PER_PAGE;
        for (int i = 0; i < entries.size(); i++) {
            ItemStack icon = iconOf("dynasty:" + entries.get(i).id());
            graphics.renderItem(icon, x0 + 8, y0 + 30 + i * 17);
        }
        int pages = (com.dynasty.DynastyCodex.count() + PER_PAGE - 1) / PER_PAGE;
        graphics.drawString(this.font, "§7" + (this.codexPage + 1) + "§7/§f" + pages,
                x0 + 36, y0 + 210, 0xFFFFFF);
        graphics.drawString(this.font, zh() ? "§8来源 · 配方 · 妙用" : "§8source · recipe · use",
                x0 + 300, y0 + 210, 0xFFFFFF);

        com.dynasty.DynastyCodex.Entry entry = com.dynasty.DynastyCodex.all().get(this.codexSelected);
        ItemStack icon = iconOf("dynasty:" + entry.id());
        int dx = x0 + 190;
        graphics.drawString(this.font, "§6" + icon.getHoverName().getString(), dx, y0 + 30, 0xFFFFFF);
        int lineY = y0 + 46;
        graphics.drawString(this.font, zh() ? "§7来源：" : "§7Source:", dx, lineY, 0xFFFFFF);
        lineY += 12;
        for (String line : wrap(zh() ? entry.zhSource() : entry.enSource(), 17)) {
            graphics.drawString(this.font, "§f" + line, dx, lineY, 0xFFFFFF);
            lineY += 12;
        }
        lineY += 6;
        if (entry.ingredients().length > 0) {
            graphics.drawString(this.font, zh() ? "§7配方材料：" : "§7Ingredients:", dx, lineY, 0xFFFFFF);
            int rx = dx + 62;
            for (String ingredient : entry.ingredients()) {
                ItemStack stack = iconOf(ingredient);
                graphics.renderItem(stack, rx, lineY - 5);
                graphics.renderItemDecorations(this.font, stack, rx, lineY - 5);
                rx += 20;
            }
            lineY += 22;
        }
        graphics.drawString(this.font, zh() ? "§7妙用：" : "§7Use:", dx, lineY, 0xFFFFFF);
        lineY += 12;
        for (String line : wrap(zh() ? entry.zhUse() : entry.enUse(), 17)) {
            graphics.drawString(this.font, "§a" + line, dx, lineY, 0xFFFFFF);
            lineY += 12;
        }
    }

    private List<String> wrap(String text, int perLine) {
        List<String> out = new ArrayList<>();
        StringBuilder line = new StringBuilder();
        for (char c : text.toCharArray()) {
            line.append(c);
            if (line.length() >= perLine) {
                out.add(line.toString());
                line.setLength(0);
            }
        }
        if (line.length() > 0) {
            out.add(line.toString());
        }
        return out;
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }
}

