package com.dynasty.client;

import net.minecraft.client.resources.language.I18n;
import net.minecraft.network.chat.Component;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * 用**翻译键**写的补充说明（料理食用用途 / Boss 信物用途 / 传送门目的地与回程提醒）。
 *
 * 为什么单独一个类：现有 {@link DynastyItemUsage} / {@link DynastyBlockInfo} 是把中英文直接写在
 * Java 里的，新增内容按本轮要求必须走翻译键，所以这里只放「路径 → 翻译键」的对应表，
 * Java 里不出现任何一句成段中文；文案全部在 assets/dynasty/lang/{zh_cn,en_us}.json。
 *
 * 行为：
 *   * 只在本模组物品上生效（调用方已过滤）；
 *   * 翻译键缺失（例如玩家用了老词条包）→ 直接跳过该行，不显示原始键名；
 *   * 与已有说明完全重复的行不再追加；没有对应键的物品返回空列表，不影响原有 tooltip。
 *
 * Extra usage lines driven by translation keys, so no prose is hardcoded in Java.
 */
public final class DynastyInfoKeys {

    private DynastyInfoKeys() {
    }

    /** 可复用的共用键 / shared keys */
    private static final String TOKEN_ALTAR = "dynasty.info.token.altar";
    private static final String TOKEN_GUIDE = "dynasty.info.token.guide";
    private static final String PORTAL_RETURN = "dynasty.info.portal.return_hint";
    private static final String STEW_HINT = "dynasty.info.food.stew_hint";

    /** 物品路径 → 翻译键（顺序即显示顺序）/ item path to translation keys */
    private static final Map<String, List<String>> KEYS = Map.ofEntries(
            // ---- 六种基础料理：食用用途（数值与 Java 注册一致，不含任何额外效果）----
            Map.entry("grilled_meat_skewer", List.of("dynasty.info.food.grill")),
            Map.entry("wheat_cake", List.of("dynasty.info.food.wheat_cake")),
            Map.entry("honey_roast", List.of("dynasty.info.food.honey_roast",
                    "dynasty.info.food.honey_bottle_hint")),
            Map.entry("countryside_stew", List.of("dynasty.info.food.countryside_stew", STEW_HINT)),
            Map.entry("mushroom_fish_soup", List.of("dynasty.info.food.mushroom_fish_soup", STEW_HINT)),
            Map.entry("pumpkin_sweet_cake", List.of("dynasty.info.food.pumpkin_sweet_cake")),

            // ---- 六种 Boss 召唤信物（与 RitualAltarBlock 的映射一致）----
            Map.entry("dragon_emperor_seal", List.of(TOKEN_ALTAR, TOKEN_GUIDE)),
            Map.entry("rebel_head", List.of(TOKEN_ALTAR, TOKEN_GUIDE)),
            Map.entry("eunuch_token", List.of(TOKEN_ALTAR, TOKEN_GUIDE)),
            Map.entry("emperor_bone", List.of(TOKEN_ALTAR, TOKEN_GUIDE)),
            Map.entry("sky_token", List.of(TOKEN_ALTAR, TOKEN_GUIDE)),
            Map.entry("sea_token", List.of(TOKEN_ALTAR, TOKEN_GUIDE)),

            // ---- 四座维度传送门：真实目的地 + 使用方式 + 回程提醒 ----
            Map.entry("jade_portal", List.of("dynasty.info.portal.jade_portal", PORTAL_RETURN)),
            Map.entry("underworld_portal", List.of("dynasty.info.portal.underworld_portal", PORTAL_RETURN)),
            Map.entry("cloud_portal", List.of("dynasty.info.portal.cloud_portal", PORTAL_RETURN)),
            Map.entry("dragon_gate", List.of("dynasty.info.portal.dragon_gate", PORTAL_RETURN)));

    /**
     * 该物品的翻译键说明行（已按客户端语言解析）。
     *
     * @param path      物品注册名（不含命名空间）
     * @param skipText  已经显示过的同一行（避免重复追加），可为 null
     */
    public static List<String> lines(String path, String skipText) {
        List<String> out = new ArrayList<>();
        for (String key : KEYS.getOrDefault(path, List.of())) {
            if (!I18n.exists(key)) {
                continue;                                   // 词条缺失 → 不显示原始键名
            }
            String text = Component.translatable(key).getString();
            if (text.isBlank() || text.equals(key) || out.contains(text)
                    || (skipText != null && text.equals(skipText))) {
                continue;
            }
            out.add(text);
        }
        return out;
    }
}
