package com.dynasty;

import java.util.ArrayList;
import java.util.List;

/**
 * 王朝图鉴数据：每件物品的「来源 / 配方 / 妙用」，供 Shift 悬停提示与任务界面的图鉴页共用。
 * Codex data: source, recipe and use of every item — shared by the Shift tooltips and the quest screen.
 */
public final class DynastyCodex {

    private DynastyCodex() {
    }

    /** 图鉴条目 / one codex entry */
    public record Entry(String id, String zhSource, String enSource, String zhUse, String enUse,
                        String... ingredients) {
    }

    private static List<Entry> entries;

    public static List<Entry> all() {
        if (entries == null) {
            entries = new ArrayList<>();
            DynastyCodexWeapons.add(entries);
            DynastyCodexGear.add(entries);
            DynastyCodexGear3.add(entries);      // 第三十一轮：10 套甲 + 50 件饰品（脚本生成）
            DynastyCodexAll.add(entries);        // 第三十四轮：全部 130 件表驱动饰品（脚本生成）
            DynastyCodexItems.add(entries);
            DynastyCodexTools.add(entries);
            // 去重：先登记的优先（Gear3 里那 50 件饰品比 All 里的版本更早，保留它们）
            List<Entry> unique = new ArrayList<>(entries.size());
            java.util.Set<String> seen = new java.util.HashSet<>();
            for (Entry entry : entries) {
                if (seen.add(entry.id())) {
                    unique.add(entry);
                }
            }
            entries = unique;
        }
        return entries;
    }

    public static Entry find(String id) {
        for (Entry entry : all()) {
            if (entry.id().equals(id)) {
                return entry;
            }
        }
        return null;
    }

    public static int count() {
        return all().size();
    }
}
