// QA copy of existing QiConstitutionGameTests; only the discovery namespace is changed.
package com.dynasty.expansion;

import com.mojang.authlib.GameProfile;
import java.util.UUID;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

/** Real Forge acceptance and native equipment; no claim of human multiplayer/graphics. */
@GameTestHolder("dynasty_armor_qa")
@PrefixGameTestTemplate(false)
public final class QiConstitutionGameTests {
    private static ServerPlayer player(GameTestHelper helper) {
        var player = new ServerPlayer(helper.getLevel().getServer(), helper.getLevel(),
                new GameProfile(UUID.randomUUID(), "QiNative"));
        player.connection = new net.minecraft.server.network.ServerGamePacketListenerImpl(
                helper.getLevel().getServer(), new net.minecraft.network.Connection(
                net.minecraft.network.protocol.PacketFlow.SERVERBOUND), player);
        return player;
    }

    private static void equip(ServerPlayer player, String set, int count) {
        var slots = new EquipmentSlot[]{EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET};
        var suffixes = new String[]{"helmet", "chestplate", "leggings", "boots"};
        for (int i = 0; i < slots.length; i++) player.setItemSlot(slots[i],
                i < count ? new ItemStack(ExpansionContent.item(set + "_" + suffixes[i])) : ItemStack.EMPTY);
    }

    @GameTest(template = "bow_ritual_test", batch = "qi_day", timeoutTicks = 20)
    public static void dayConstitutionBlocksNativeAndSharedApplicationsWithoutConsumingYang(GameTestHelper h) {
        h.getLevel().setDayTime(6000); h.getLevel().updateSkyBrightness();
        var player = player(h);
        equip(player, "tiangang", 4);
        ExpansionEffects.apply(player, ExpansionEffects.YANG, 100);
        double damage = player.getAttributeValue(Attributes.ATTACK_DAMAGE);
        ExpansionEffects.apply(player, ExpansionEffects.YIN, 100);
        h.assertTrue(player.hasEffect(ExpansionEffects.YANG.get()) && !player.hasEffect(ExpansionEffects.YIN.get()),
                "Immune Yin does not neutralise the existing Yang buff");
        h.assertTrue(!player.addEffect(new MobEffectInstance(ExpansionEffects.YIN.get(), 100, 2))
                && !player.hasEffect(ExpansionEffects.YIN.get())
                && player.getAttributeValue(Attributes.ATTACK_DAMAGE) == damage,
                "Native addEffect is also denied without consuming existing attributes");
        h.assertTrue(player.addEffect(new MobEffectInstance(MobEffects.POISON, 100)),
                "Constitution does not grant unrelated poison immunity");
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test", batch = "qi_night", timeoutTicks = 20)
    public static void nightConstitutionBlocksYangWithoutConsumingYinAndUnequippingImmediatelyRestoresAcceptance(GameTestHelper h) {
        h.getLevel().setDayTime(18000); h.getLevel().updateSkyBrightness();
        var player = player(h);
        equip(player, "disha", 4);
        ExpansionEffects.apply(player, ExpansionEffects.YIN, 100);
        ExpansionEffects.apply(player, ExpansionEffects.YANG, 100);
        h.assertTrue(player.hasEffect(ExpansionEffects.YIN.get()) && !player.hasEffect(ExpansionEffects.YANG.get()),
                "Immune Yang does not neutralise existing Yin");
        h.assertTrue(!player.addEffect(new MobEffectInstance(ExpansionEffects.YANG.get(), 100)),
                "Native beneficial Yang applications are explicitly blocked too");
        equip(player, "disha", 3);
        h.assertTrue(player.addEffect(new MobEffectInstance(ExpansionEffects.YANG.get(), 100)),
                "Unequipping one piece restores native acceptance without a cached lease");
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test", batch = "qi_transition", timeoutTicks = 20)
    public static void nativeEquipmentChangeAndDawnCleanseExistingQiButDoNotAffectAnotherPlayer(GameTestHelper h) {
        h.getLevel().setDayTime(6000); h.getLevel().updateSkyBrightness();
        var player = player(h);
        var other = player(h);
        player.addEffect(new MobEffectInstance(ExpansionEffects.YIN.get(), 100, 2));
        other.addEffect(new MobEffectInstance(ExpansionEffects.YIN.get(), 100, 2));
        equip(player, "tiangang", 4);
        // Native equipment-change dispatch happens in LivingEntity.tick, not setItemSlot.
        net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(new net.minecraftforge.event.entity.living.LivingEquipmentChangeEvent(
                player, EquipmentSlot.FEET, ItemStack.EMPTY, player.getItemBySlot(EquipmentSlot.FEET)));
        h.assertTrue(!player.hasEffect(ExpansionEffects.YIN.get()) && other.hasEffect(ExpansionEffects.YIN.get()),
                "Equipment event cleanses only its owner through the native removal API");
        h.getLevel().setDayTime(18000); h.getLevel().updateSkyBrightness();
        h.assertTrue(player.addEffect(new MobEffectInstance(ExpansionEffects.YIN.get(), 100)),
                "Day set loses immunity at night even while still equipped");
        h.getLevel().setDayTime(6000); h.getLevel().updateSkyBrightness();
        net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(new net.minecraftforge.event.entity.living.LivingEvent.LivingTickEvent(player));
        h.assertTrue(!player.hasEffect(ExpansionEffects.YIN.get()), "Dawn tick cleanses an already active Yin effect");
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test", batch = "qi_partial", timeoutTicks = 20)
    public static void partialSetsInventoryAndWrongTimeKeepOriginalThreeLayerAndNeutralisationRules(GameTestHelper h) {
        h.getLevel().setDayTime(6000); h.getLevel().updateSkyBrightness();
        var player = player(h);
        equip(player, "tiangang", 3);
        player.getInventory().add(new ItemStack(ExpansionContent.item("tiangang_boots")));
        for (int i = 0; i < 4; i++) ExpansionEffects.apply(player, ExpansionEffects.YIN, 100);
        h.assertTrue(player.getEffect(ExpansionEffects.YIN.get()).getAmplifier() == 2,
                "Inventory does not count as worn gear; original three-layer cap remains");
        ExpansionEffects.apply(player, ExpansionEffects.YANG, 100);
        h.assertTrue(!player.hasEffect(ExpansionEffects.YIN.get()) && !player.hasEffect(ExpansionEffects.YANG.get()),
                "Original opposite-Qi cancellation remains for ordinary players");
        equip(player, "disha", 4);
        h.assertTrue(player.addEffect(new MobEffectInstance(ExpansionEffects.YANG.get(), 100)),
                "Night set grants no immunity by day");
        h.succeed();
    }
}
