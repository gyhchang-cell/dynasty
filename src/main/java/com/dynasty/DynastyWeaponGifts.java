package com.dynasty;

import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * 兵器的「非合成」获取方式：达成条件后由朝廷 / 机缘授予。
 *
 *  * 官阶御赐：尚书（12 阶）→ 御赐金锏；丞相（17 阶）→ 尚方宝剑
 *  * 战绩习得：击败 5 种不同的 Boss → 七星宝刀
 *  * 特定击杀：白天击败凤凰 → 射日弓
 *  * （Boss 直掉与宝箱掉落见 DynastyBossDrops 与宝箱战利品表）
 *
 * Weapons obtained by conditions rather than crafting only. Each gift is granted once.
 */
@SuppressWarnings("null")
public final class DynastyWeaponGifts {

    private DynastyWeaponGifts() {
    }

    private static final String FLAG = "dynasty_gift_";
    private static final String BOSS_KINDS = "dynasty_boss_kinds";
    private static final String BOSS_LIST = "dynasty_boss_kinds_list";

    /** 每 40 tick 检查一次「官阶 / 战绩」条件 / periodic condition check */
    public static void tick(ServerPlayer player) {
        int rank = DynastyStats.getRank(player);
        if (rank >= 12) {
            grant(player, "gilded_mace", "官至尚书，朝廷御赐金锏");
        }
        if (rank >= 17) {
            grant(player, "supreme_sword", "官至丞相，获尚方宝剑");
        }
        if (player.getPersistentData().getInt(BOSS_KINDS) >= 5) {
            grant(player, "seven_star_saber", "连破五种强敌，武艺大成");
        }
    }

    /** 击杀结算：记录击败过的 Boss 种类；白天斩凤凰给射日弓 / kill hook */
    public static void onMobKill(ServerPlayer player, EntityType<?> type) {
        ResourceLocation id = ForgeRegistries.ENTITY_TYPES.getKey(type);
        if (id == null || !id.getNamespace().equals(Dynasty.MODID)) {
            return;
        }
        String path = id.getPath();
        if (isBoss(path)) {
            String seen = player.getPersistentData().getString(BOSS_LIST);
            if (!("," + seen + ",").contains("," + path + ",")) {
                player.getPersistentData().putString(BOSS_LIST,
                        seen.isEmpty() ? path : seen + "," + path);
                player.getPersistentData().putInt(BOSS_KINDS,
                        player.getPersistentData().getInt(BOSS_KINDS) + 1);
            }
        }
        if (path.equals("phoenix") && player.level().isDay()) {
            grant(player, "sunbow", "白日射落凤凰，领悟射日弓");
        }
    }

    private static boolean isBoss(String path) {
        return switch (path) {
            case "dragon_emperor", "rebel_general", "eunuch_mastermind",
                 "undead_first_emperor", "nine_heaven_general", "dragon_king" -> true;
            default -> false;
        };
    }

    /** 已斩获的 Boss 种类数（给成就 / 任务看）/ number of distinct bosses defeated */
    public static int bossKinds(ServerPlayer player) {
        return player.getPersistentData().getInt(BOSS_KINDS);
    }

    /** 授予一把武器（同一种只给一次）/ grant a weapon once */
    private static void grant(ServerPlayer player, String weapon, String reason) {
        String key = FLAG + weapon;
        if (player.getPersistentData().getBoolean(key)) {
            return;
        }
        player.getPersistentData().putBoolean(key, true);
        Item item = ForgeRegistries.ITEMS.getValue(new ResourceLocation(Dynasty.MODID, weapon));
        if (item == null) {
            return;
        }
        ItemStack stack = new ItemStack(item);
        if (!player.getInventory().add(stack)) {
            player.drop(stack, false);
        }
        player.level().playSound(null, player.getX(), player.getY(), player.getZ(),
                SoundEvents.UI_TOAST_CHALLENGE_COMPLETE, SoundSource.PLAYERS, 0.8F, 1.2F);
        player.sendSystemMessage(Component.literal("§6[机缘] §r获得兵器 §e"
                + stack.getHoverName().getString() + "§7（" + reason + "）"));
    }
}
