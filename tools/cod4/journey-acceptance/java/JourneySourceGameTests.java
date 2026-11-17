package com.dynasty.expansion;

import com.dynasty.DynastyStats;
import com.dynasty.cod3.DynastyNpcEntity;
import com.dynasty.cod3.NpcContent;
import java.util.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.inventory.MerchantMenu;
import net.minecraft.world.item.*;
import net.minecraft.world.item.trading.*;
import net.minecraftforge.gametest.*;

/** Source actors/locations are fixtures. Outputs come from native deaths and actual paid transactions. */
@GameTestHolder("dynasty_journey_qa") @PrefixGameTestTemplate(false)
public final class JourneySourceGameTests {
    private static ItemStack stack(String id, int count) { return new ItemStack(ExpansionContent.item(id), count); }

    private static ItemStack harvest(GameTestHelper h, ServerPlayer p, String entity, String item, int required) {
        var collected = stack(item, 0);
        int count = 0;
        for (int attempt = 0; attempt < 40 && count < required; attempt++) {
            var mob = SecondaryMobs.TYPES.get(entity).get().create(h.getLevel());
            mob.setNoAi(true); mob.setPos(p.position()); mob.getRandom().setSeed(251L + attempt);
            h.getLevel().addFreshEntity(mob); mob.setHealth(1);
            h.assertTrue(mob.hurt(p.damageSources().playerAttack(p), 10000) && mob.isDeadOrDying(), "Native player credited death: " + entity);
            var drops = h.getLevel().getEntitiesOfClass(ItemEntity.class, mob.getBoundingBox().inflate(2));
            for (var drop : drops) {
                if (drop.getItem().is(ExpansionContent.item(item))) {
                    if (collected.isEmpty()) collected = drop.getItem().copy();
                    count += drop.getItem().getCount();
                }
                drop.discard();
            }
            mob.discard();
        }
        h.assertTrue(count >= required, "Registered actor's actual death produced " + item + ": " + count);
        collected.setCount(required);
        JourneyRecipeGameTests.record(item, "native_player_death_source", true,
            "Actual " + entity + " death -> " + count + " item(s); seeded actor fixture, not natural spawn/combat difficulty proof");
        return collected;
    }

    private static ItemStack trade(GameTestHelper h, ServerPlayer p, Merchant merchant, MerchantOffer offer,
                                   ItemStack costA, ItemStack costB) {
        if (merchant instanceof DynastyNpcEntity npc) {
            h.assertTrue(npc.trade(p), "Original NPC authority opens its native trade menu");
        } else {
            merchant.setTradingPlayer(p);
            merchant.openTradingScreen(p, net.minecraft.network.chat.Component.literal("Journey original merchant"), 1);
        }
        h.assertTrue(p.containerMenu instanceof MerchantMenu, "Actual existing merchant entry created MerchantMenu");
        var menu = (MerchantMenu)p.containerMenu;
        menu.setSelectionHint(merchant.getOffers().indexOf(offer));
        int before = offer.getUses();
        // A short payment must not produce a purchasable result or change stock.
        var shortCost = costA.copy(); shortCost.shrink(1); menu.getSlot(0).set(shortCost); menu.getSlot(1).set(costB.copy());
        h.assertTrue(menu.getSlot(2).getItem().isEmpty() && offer.getUses() == before, "Short actual payment rejected");
        menu.getSlot(0).set(costA.copy()); menu.getSlot(1).set(costB.copy());
        var expected = offer.getResult().copy();
        h.assertTrue(ItemStack.matches(menu.getSlot(2).getItem(), expected), "Native offer selected exactly");
        var taken = menu.getSlot(2).remove(64); menu.getSlot(2).onTake(p, taken);
        h.assertTrue(ItemStack.matches(expected, taken) && menu.getSlot(0).getItem().isEmpty()
            && menu.getSlot(1).getItem().isEmpty() && offer.getUses() == before + 1, "Exact costs and one stock use");
        h.assertTrue(menu.getSlot(2).getItem().isEmpty(), "No repeat output without fresh payment");
        p.closeContainer();
        return taken;
    }

    @GameTest(template="bow_ritual_test", batch="journey_sources", timeoutTicks=300)
    public static void allTenCod4MaterialsComeFromTheirActualRegisteredDeathTables(GameTestHelper h) {
        var p = JourneyRecipeGameTests.player(h);
        try {
            for (var source : new String[][]{
                {"clockwork_rat","qimen_cable"}, {"wooden_magpie","qimen_gear"},
                {"red_fox","fox_pelt"}, {"gray_wolf","wolf_fang"}, {"giant_python","python_gall"},
                {"crab_soldier","crab_shell"}, {"river_imp","kappa_scale"}, {"stone_sprite","sprite_jade"},
                {"lantern_ghost","lantern_oil"}, {"locust_swarm","locust_dust"}})
                harvest(h, p, source[0], source[1], 2);
            h.succeed();
        } finally { p.discard(); }
    }

    @GameTest(template="bow_ritual_test", batch="journey_sources", timeoutTicks=300)
    public static void originalMaterialLootPaysExistingNpcTradesAndBuysExistingQimenMaterials(GameTestHelper h) {
        var p = JourneyRecipeGameTests.player(h);
        try {
            for (var source : new String[][]{
                {"baibao_jin","red_fox","fox_pelt","copper_coin"},
                {"ba_tu","gray_wolf","wolf_fang","copper_coin"},
                {"hei_po","giant_python","python_gall","healing_salve"},
                {"hei_po","locust_swarm","locust_dust","healing_salve"},
                {"huang_laohan","crab_soldier","crab_shell","copper_coin"},
                {"huang_laohan","river_imp","kappa_scale","copper_coin"}}) {
                DynastyNpcEntity npc = NpcContent.NPCS.get(source[0]).get().create(h.getLevel());
                npc.setNoAi(true); npc.setPos(p.position()); npc.ensureContentTrades();
                var offer = npc.getOffers().stream().filter(o -> o.getBaseCostA().is(ExpansionContent.item(source[2]))
                    && o.getResult().is(ExpansionContent.item(source[3]))).findFirst().orElseThrow();
                var material = harvest(h, p, source[1], source[2], offer.getCostA().getCount());
                var purchased = trade(h, p, npc, offer, material, ItemStack.EMPTY);
                JourneyRecipeGameTests.record(source[0] + "/" + source[2], "native_loot_to_npc_transaction", true,
                    "Actual death material -> original MerchantMenu -> " + purchased + "; short payment/replay rejected; one stock consumed");
                if (source[2].equals("kappa_scale")) {
                    h.assertTrue(purchased.getCount() == 8, "Original kappa payment earns eight coins");
                    DynastyStats.setRank(p, 3); // Existing unlock fixture only, not proof of obtaining official rank.
                    var minister = new ProgressionMerchant(p);
                    var gear = minister.getOffers().stream().filter(o -> o.getResult().is(ExpansionContent.item("qimen_gear"))).findFirst().orElseThrow();
                    var bought = trade(h, p, minister, gear, purchased, ItemStack.EMPTY);
                    h.assertTrue(bought.is(ExpansionContent.item("qimen_gear")) && bought.getCount() == 1, "Native earned coins buy original gear");
                    JourneyRecipeGameTests.record("qimen_gear", "native_loot_coin_shop_chain", true,
                        "river_imp actual drops -> Huang Laohan two scales/eight coins -> original minister eight coins/one gear; rank-three unlock is fixture");
                }
                npc.discard();
            }
            h.succeed();
        } finally { p.discard(); }
    }
}
