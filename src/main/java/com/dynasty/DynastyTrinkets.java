package com.dynasty;

import net.minecraft.core.NonNullList;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * 饰品系统：借鉴 Curios 的思路与槽位——
 * 1) 我们的饰品使用 Curios 的物品标签（data/curios/tags/items/*.json），装上 Curios 后可直接放进它的槽位；
 * 2) 没有 Curios 时也能用：本模组自带 6 个饰品槽（右键「百宝妆匣」打开）。
 * 每件饰品都有独特效果，按住 Shift 悬停即可查看。
 *
 * Trinket system: Curios-compatible item tags plus a built-in six-slot trinket pouch.
 */
@SuppressWarnings("null")
public final class DynastyTrinkets {

    private DynastyTrinkets() {
    }

    public static final int SLOTS = 6;
    public static final String NBT_KEY = "dynasty_trinkets";

    public static final DeferredRegister<Item> ITEMS =
            DeferredRegister.create(ForgeRegistries.ITEMS, Dynasty.MODID);

    /** 百宝妆匣：右键打开饰品槽 / Trinket Box: opens the six accessory slots */
    public static final RegistryObject<Item> TRINKET_BOX = ITEMS.register("trinket_box",
            () -> new TrinketBoxItem(new Item.Properties().stacksTo(1)));

    // ---- 饰品 / accessories ----
    public static final RegistryObject<Item> JADE_PENDANT = charm("jade_pendant");
    public static final RegistryObject<Item> JADE_BI_DISC = charm("jade_bi_disc");
    public static final RegistryObject<Item> GOLD_SEAL_CHARM = charm("gold_seal_charm");
    public static final RegistryObject<Item> DRAGON_SCALE_CHARM = charm("dragon_scale_charm");
    public static final RegistryObject<Item> PHOENIX_FEATHER_CHARM = charm("phoenix_feather_charm");
    public static final RegistryObject<Item> QILIN_HORN_CHARM = charm("qilin_horn_charm");
    public static final RegistryObject<Item> FOX_TAIL_CHARM = charm("fox_tail_charm");
    public static final RegistryObject<Item> SILK_POUCH = charm("silk_pouch");
    public static final RegistryObject<Item> SOUTH_POINTING_COMPASS = charm("south_pointing_compass");

    private static RegistryObject<Item> charm(String name) {
        return ITEMS.register(name, () -> new Item(new Item.Properties().stacksTo(1)));
    }

    /** 全部饰品 id / all accessory ids */
    public static final List<String> IDS = List.of(
            "jade_pendant", "jade_bi_disc", "gold_seal_charm", "dragon_scale_charm",
            "phoenix_feather_charm", "qilin_horn_charm", "fox_tail_charm", "silk_pouch",
            "south_pointing_compass", "bronze_mirror");

    /** 需要注册进 Curios 的饰品物品 / items that get a Curios capability */
    public static List<RegistryObject<Item>> accessoryItems() {
        List<RegistryObject<Item>> list = new ArrayList<>();
        list.add(JADE_PENDANT);
        list.add(JADE_BI_DISC);
        list.add(GOLD_SEAL_CHARM);
        list.add(DRAGON_SCALE_CHARM);
        list.add(PHOENIX_FEATHER_CHARM);
        list.add(QILIN_HORN_CHARM);
        list.add(FOX_TAIL_CHARM);
        list.add(SILK_POUCH);
        list.add(SOUTH_POINTING_COMPASS);
        list.add(DynastyFineItems.BRONZE_MIRROR);
        return list;
    }

    public static boolean isAccessory(ItemStack stack) {
        String id = idOf(stack);
        return id != null && IDS.contains(id);
    }

    public static String idOf(ItemStack stack) {
        if (stack == null || stack.isEmpty()) {
            return null;
        }
        ResourceLocation id = ForgeRegistries.ITEMS.getKey(stack.getItem());
        if (id == null || !id.getNamespace().equals(Dynasty.MODID)) {
            return null;
        }
        return id.getPath();
    }

    // ---------------------------------------------------------------- 存储
    public static NonNullList<ItemStack> load(Player player) {
        NonNullList<ItemStack> list = NonNullList.withSize(SLOTS, ItemStack.EMPTY);
        ListTag tag = player.getPersistentData().getList(NBT_KEY, CompoundTag.TAG_COMPOUND);
        for (int i = 0; i < Math.min(SLOTS, tag.size()); i++) {
            list.set(i, ItemStack.of(tag.getCompound(i)));
        }
        return list;
    }

    public static void save(Player player, List<ItemStack> items) {
        ListTag tag = new ListTag();
        for (int i = 0; i < SLOTS; i++) {
            ItemStack stack = i < items.size() ? items.get(i) : ItemStack.EMPTY;
            tag.add(stack.isEmpty() ? new CompoundTag() : stack.save(new CompoundTag()));
        }
        player.getPersistentData().put(NBT_KEY, tag);
        if (player instanceof ServerPlayer serverPlayer) {
            apply(serverPlayer);
            DynastyTrinketSync.send(serverPlayer);
        }
    }

    public static boolean has(Player player, String id) {
        return activeIds(player).contains(id);
    }

    /**
     * 生效中的饰品：饰品槽 + 背包（装在 Curios 槽里、或直接带在身上都算）。
     * Active trinkets: our six slots plus the inventory, so Curios-placed charms also work.
     */
    public static java.util.Set<String> activeIds(Player player) {
        java.util.Set<String> out = new java.util.LinkedHashSet<>();
        for (ItemStack stack : load(player)) {
            String id = idOf(stack);
            if (id != null) {
                out.add(id);
            }
        }
        for (int i = 0; i < player.getInventory().getContainerSize(); i++) {
            String id = idOf(player.getInventory().getItem(i));
            if (id != null) {
                out.add(id);
            }
        }
        String offhand = idOf(player.getOffhandItem());
        if (offhand != null) {
            out.add(offhand);
        }
        // Curios 槽位里的饰品（通过反射桥接，没有 Curios 时自动跳过）
        // trinkets worn in Curios slots (reflectively bridged; skipped when Curios is absent)
        DynastyCuriosSetup.collectEquipped(player, out);
        out.retainAll(IDS);
        return out;
    }

    public static List<String> equippedIds(Player player) {
        return new ArrayList<>(activeIds(player));
    }

    /** 玉佩：额外 8% 减伤 / jade pendant: extra 8% reduction */
    public static float extraDamageReduction(Player player) {
        return has(player, "jade_pendant") ? 0.08F : 0.0F;
    }

    /** 金印：功名 +25% / gold seal charm: +25% merit */
    public static float meritMultiplier(Player player) {
        return has(player, "gold_seal_charm") ? 1.25F : 1.0F;
    }

    // ---------------------------------------------------------------- 效果
    private static final Attribute[] ATTRS = {
            Attributes.MAX_HEALTH, Attributes.ARMOR, Attributes.KNOCKBACK_RESISTANCE,
            Attributes.MOVEMENT_SPEED, Attributes.LUCK};

    private static final String[] ATTR_NAMES = {
            "dynasty_trinket_health", "dynasty_trinket_armor", "dynasty_trinket_kb",
            "dynasty_trinket_speed", "dynasty_trinket_luck"};

    private static UUID uuid(String id, int attr) {
        return UUID.nameUUIDFromBytes(("dynasty_trinket_" + id + "_" + attr).getBytes());
    }

    private static void addAttr(Player player, String id, int attr, double amount) {
        AttributeInstance instance = player.getAttribute(ATTRS[attr]);
        if (instance != null) {
            instance.addTransientModifier(new AttributeModifier(uuid(id, attr),
                    ATTR_NAMES[attr], amount, AttributeModifier.Operation.ADDITION));
        }
    }

    private static void clearAttrs(Player player, String id) {
        for (int a = 0; a < ATTRS.length; a++) {
            AttributeInstance instance = player.getAttribute(ATTRS[a]);
            if (instance != null) {
                instance.removeModifier(uuid(id, a));
            }
        }
    }

    /** 每 20 tick 刷新一次饰品效果 / refresh effects every second */
    public static void tick(ServerPlayer player) {
        apply(player);
        if (player.tickCount % 600 == 0 && has(player, "bronze_mirror")) {
            // 铜镜：每 30 秒净化一个负面效果 / mirror cleanses one debuff every 30s
            player.getActiveEffects().stream()
                    .filter(effect -> !effect.getEffect().isBeneficial())
                    .findFirst()
                    .ifPresent(effect -> {
                        player.removeEffect(effect.getEffect());
                        player.sendSystemMessage(net.minecraft.network.chat.Component.literal(
                                "§9[铜镜] §r映照心魔，净化了一个负面效果。"));
                    });
        }
        if (has(player, "gold_seal_charm") && player.tickCount % 1200 == 0) {
            DynastyStats.addLoyalty(player, 2);
        }
    }

    private static void apply(ServerPlayer player) {
        // 每个饰品最多计算一次 / every accessory is counted at most once
        for (String id : IDS) {
            clearAttrs(player, id);
        }
        java.util.Set<String> active = activeIds(player);
        for (String id : active) {
            switch (id) {
                case "jade_bi_disc" -> addAttr(player, id, 0, 150.0D);
                case "dragon_scale_charm" -> {
                    addAttr(player, id, 1, 12.0D);
                    addAttr(player, id, 2, 0.4D);
                }
                case "phoenix_feather_charm" -> {
                    addAttr(player, id, 3, 0.10D);
                    player.addEffect(new MobEffectInstance(MobEffects.SLOW_FALLING, 60, 0, true, false));
                }
                case "qilin_horn_charm" -> {
                    addAttr(player, id, 4, 3.0D);
                    player.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 60, 0, true, false));
                }
                case "fox_tail_charm" -> {
                    player.addEffect(new MobEffectInstance(MobEffects.JUMP, 60, 1, true, false));
                    addAttr(player, id, 3, 0.05D);
                }
                case "silk_pouch" -> {
                    player.addEffect(new MobEffectInstance(MobEffects.WATER_BREATHING, 60, 0, true, false));
                    player.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION, 300, 0, true, false));
                }
                case "south_pointing_compass" ->
                        player.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, 60, 0, true, false));
                default -> {
                    // 玉佩 / 金印 / 铜镜 通过事件与定时逻辑生效
                }
            }
        }
        if (player.getHealth() > player.getMaxHealth()) {
            player.setHealth(player.getMaxHealth());
        }
    }
}
