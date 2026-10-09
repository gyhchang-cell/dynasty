package com.dynasty.blueprint;

import java.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.item.*;
import net.minecraft.world.inventory.*;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;
import net.minecraftforge.registries.ForgeRegistries;

@GameTestHolder("dynasty_army")
@PrefixGameTestTemplate(false)
public final class SalvageGameTests {
    private static Item item(String id){return ForgeRegistries.ITEMS.getValue(new ResourceLocation(id.contains(":")?id:"dynasty:"+id));}
    private static net.minecraftforge.common.util.FakePlayer player(GameTestHelper h){
        var p=new net.minecraftforge.common.util.FakePlayer(h.getLevel(),new com.mojang.authlib.GameProfile(UUID.randomUUID(),"cod1-salvage"));
        p.setPos(net.minecraft.world.phys.Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(5,3,5))));return p;
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=40,batch="salvage")
    public static void everyOriginalMobLootTableProducesItsNamedFunctionalDrops(GameTestHelper h){
        var expected=new HashMap<>(Map.of(
            "zuwu_daoshou",Set.of("copper_coin","broken_iron_blade","coarse_linen"),
            "ludun_jiashi",Set.of("heavy_shield_remnant","wrought_iron_billet","damaged_chainmail"),
            "fufa_jijiu",Set.of("cinnabar","talisman_paper","dry_peach_branch"),
            "shanjing_shanxiao",Set.of("shanxiao_claw","ghost_face_fur","green_beast_gall"),
            "juma_changqiangbing",Set.of("iron_spearhead","tough_wood_shaft","rusted_lamellar_plate"),
            "liannu_zhenzu",Set.of("minecraft:leather","short_crossbow_bolt","bronze_gear_part"),
            "tiesuo_chihou",Set.of("fine_steel_chain","iron_grappling_claw","swift_boot_scrap"),
            "kuijun_sishi",Set.of("poor_gunpowder","pottery_fragment","bloodied_cloth"),
            "zhenwang_zhangqiguan",Set.of("broken_tiger_tally","black_army_banner_scrap","vengeful_war_soul")));
        expected.put("mingsha_shixie",Set.of("resonant_scorpion_shell","metal_sting_needle","pure_yellow_sand"));
        expected.put("kumu_shujing",Set.of("ancient_tree_heart","hardened_dead_bark","glowing_parasite_mushroom"));
        expected.put("chimu_zhuha",Set.of("red_toad_gland","tough_toad_hide","poison_gel"));
        expected.put("muxue_feilu",Set.of("pointed_dead_tooth","rusted_helmet_spike","yin_air_sac"));
        expected.put("zhiren_jianke",Set.of("tough_bamboo_sliver","paper_cutting_knife","painted_cinnabar"));
        expected.put("fuhun_baibu_tongzi",Set.of("white_wax_tear","wronged_shroud","pale_milk_tooth"));
        expected.put("shibian_lishi",Set.of("blackened_bone","congealed_corpse_oil","strongman_wrist_weight"));
        for(var entry:expected.entrySet()){
            var type=ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation("dynasty",entry.getKey()));var entity=type.create(h.getLevel());
            var params=new net.minecraft.world.level.storage.loot.LootParams.Builder(h.getLevel())
                .withParameter(net.minecraft.world.level.storage.loot.parameters.LootContextParams.THIS_ENTITY,entity)
                .withParameter(net.minecraft.world.level.storage.loot.parameters.LootContextParams.ORIGIN,entity.position())
                .withParameter(net.minecraft.world.level.storage.loot.parameters.LootContextParams.DAMAGE_SOURCE,h.getLevel().damageSources().genericKill())
                .create(net.minecraft.world.level.storage.loot.parameters.LootContextParamSets.ENTITY);
            var table=h.getLevel().getServer().getLootData().getLootTable(type.getDefaultLootTable());var seen=new HashSet<Item>();
            for(int seed=1;seed<=64;seed++)for(var stack:table.getRandomItems(params,seed)){
                // A legitimate uniform min=0 roll can return an empty stack before entity-drop filtering.
                if(stack.isEmpty())continue;
                h.assertTrue(stack.getCount()<=4,"Loot ranges remain bounded: "+entry.getKey()+" "+stack);seen.add(stack.getItem());
            }
            var wanted=new HashSet<Item>();for(String id:entry.getValue())wanted.add(item(id));
            h.assertTrue(!wanted.contains(Items.AIR)&&seen.equals(wanted),"Loaded loot table yields exactly the registered original design drops: "+entry.getKey());
        }
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=30,batch="salvage")
    public static void specialMaterialsNoLongerProvideGenericAnvilRepair(GameTestHelper h){
        var p=player(h);var menu=new AnvilMenu(0,p.getInventory());
        for(var pair:new String[][]{
            {"tough_toad_hide","minecraft:leather_chestplate"},{"rusted_helmet_spike","minecraft:iron_helmet"},{"tough_bamboo_sliver","minecraft:bow"},{"paper_cutting_knife","minecraft:shears"},{"wronged_shroud","minecraft:leather_helmet"},{"strongman_wrist_weight","minecraft:chainmail_chestplate"},{"broken_iron_blade","minecraft:iron_sword"},{"broken_iron_blade","tie_jian"},{"coarse_linen","minecraft:leather_helmet"},{"heavy_shield_remnant","minecraft:shield"},
            {"wrought_iron_billet","minecraft:iron_pickaxe"},{"damaged_chainmail","minecraft:chainmail_chestplate"},{"dry_peach_branch","minecraft:bow"},
            {"shanxiao_claw","minecraft:iron_axe"},{"ghost_face_fur","minecraft:leather_chestplate"},{"iron_spearhead","minecraft:iron_sword"},
            {"tough_wood_shaft","minecraft:crossbow"},{"rusted_lamellar_plate","minecraft:iron_leggings"},{"bronze_gear_part","minecraft:crossbow"},
            {"fine_steel_chain","minecraft:chainmail_boots"},{"iron_grappling_claw","minecraft:iron_axe"},{"swift_boot_scrap","minecraft:leather_boots"},
            {"bloodied_cloth","minecraft:leather_chestplate"},{"yin_jade_shard","sword_jade"},{"nether_tatter","minecraft:leather_leggings"},
            {"refined_wrought_iron","minecraft:iron_helmet"},{"broken_heart_mirror","minecraft:iron_chestplate"}}){
            var base=new ItemStack(item(pair[1]));h.assertTrue(base.isDamageableItem(),"Existing repair target is damageable: "+pair[1]);
            base.setDamageValue(Math.min(100,base.getMaxDamage()/2));base.getOrCreateTag().putString("foreign","keep");
            menu.getSlot(0).set(base);menu.getSlot(1).set(new ItemStack(item(pair[0]),4));menu.createResult();
            var output=menu.getSlot(2).getItem();
            h.assertTrue(output.isEmpty()&&base.getTag().getString("foreign").equals("keep"),"No generic anvil repair for "+pair[0]);
        }
        var advancedBow=new ItemStack(item("chang_gong"));advancedBow.setDamageValue(100);
        h.assertTrue(advancedBow.isDamageableItem()&&advancedBow.getItem() instanceof BowItem,"Negative fixture uses actual Dynasty bow");
        menu.getSlot(0).set(advancedBow);menu.getSlot(1).set(new ItemStack(BlueprintSalvage.DRY_PEACH_BRANCH.get()));menu.createResult();
        h.assertTrue(menu.getSlot(2).getItem().isEmpty(),"Ordinary wood salvage cannot bypass advanced bow repair materials");
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=65,batch="salvage")
    public static void beastGallConsumesThroughNormalUseAndCuresOnlyPoison(GameTestHelper h){
        var p=player(h);h.getLevel().addNewPlayer(p);p.getFoodData().setFoodLevel(20);
        // FakePlayer has no network listener tick; execute the same native living tick explicitly.
        h.onEachTick(()->{if(!p.isRemoved())p.doTick();});
        p.addEffect(new MobEffectInstance(MobEffects.POISON,200));p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,200));
        p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(BlueprintSalvage.GREEN_BEAST_GALL.get(),2));
        BlueprintSalvage.GREEN_BEAST_GALL.get().use(h.getLevel(),p,InteractionHand.MAIN_HAND);
        h.runAfterDelay(10,()->h.assertTrue(p.hasEffect(MobEffects.POISON)&&p.getMainHandItem().getCount()==2,"No instant cure or early consumption"));
        h.runAfterDelay(40,()->{
            h.assertTrue(!p.hasEffect(MobEffects.POISON)&&p.hasEffect(MobEffects.MOVEMENT_SLOWDOWN),"Normal completed use removes only poison");
            h.assertTrue(p.getMainHandItem().getCount()==1&&p.getFoodData().getFoodLevel()==20,"Consumes one gall even at full hunger; no food duplication");
            p.discard();h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=30,batch="salvage")
    public static void recoveredBoltLoadsAndFiresFromVanillaCrossbow(GameTestHelper h){
        var p=player(h);var crossbow=new ItemStack(Items.CROSSBOW);p.setItemInHand(InteractionHand.MAIN_HAND,crossbow);
        var bolts=new ItemStack(BlueprintSalvage.SHORT_CROSSBOW_BOLT.get(),4);p.getInventory().add(bolts);
        h.assertTrue(p.getProjectile(crossbow).is(BlueprintSalvage.SHORT_CROSSBOW_BOLT.get()),"Vanilla projectile tag selects recovered bolts");
        Items.CROSSBOW.use(h.getLevel(),p,InteractionHand.MAIN_HAND);
        ((CrossbowItem)Items.CROSSBOW).releaseUsing(crossbow,h.getLevel(),p,crossbow.getUseDuration()-CrossbowItem.getChargeDuration(crossbow));
        h.assertTrue(CrossbowItem.isCharged(crossbow)&&p.getInventory().countItem(BlueprintSalvage.SHORT_CROSSBOW_BOLT.get())==3,"Actual loading consumes one bolt");
        Items.CROSSBOW.use(h.getLevel(),p,InteractionHand.MAIN_HAND);
        h.assertTrue(!CrossbowItem.isCharged(crossbow)&&h.getLevel().getEntitiesOfClass(net.minecraft.world.entity.projectile.AbstractArrow.class,
            p.getBoundingBox().inflate(3),e->e.getOwner()==p).size()==1,"Vanilla release creates one real arrow entity");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=30,batch="salvage")
    public static void recoveredMaterialsCraftThroughServerRecipeManager(GameTestHelper h){
        var p=player(h);
        for(var row:new String[][]{{"pure_yellow_sand","4","minecraft:sand",""},{"ancient_tree_heart","1","minecraft:golden_apple","minecraft:apple"},{"poison_gel","4","minecraft:slime_ball",""},{"pointed_dead_tooth","2","minecraft:bone_meal",""},{"painted_cinnabar","2","cinnabar",""},{"white_wax_tear","2","minecraft:candle","minecraft:string"},{"pale_milk_tooth","2","minecraft:bone_meal",""},{"blackened_bone","2","minecraft:bone_meal",""},{"poor_gunpowder","4","minecraft:gunpowder",""},{"pottery_fragment","4","minecraft:brick",""},
            {"broken_tiger_tally","4","tiger_crest",""},{"black_army_banner_scrap","6","minecraft:black_banner","minecraft:stick"},
            {"vengeful_war_soul","1","minecraft:experience_bottle","minecraft:glass_bottle"}}){
            var menu=new CraftingMenu(0,p.getInventory(),ContainerLevelAccess.create(h.getLevel(),h.absolutePos(new BlockPos(2,2,2))));
            int count=Integer.parseInt(row[1]);for(int i=1;i<=count;i++)menu.getSlot(i).set(new ItemStack(item(row[0])));
            if(!row[3].isEmpty())menu.getSlot(count+1).set(new ItemStack(item(row[3])));
            h.assertTrue(menu.getSlot(0).getItem().is(item(row[2])),"Loaded functional recycling recipe: "+row[0]);
            var output=menu.getSlot(0).remove(1);menu.getSlot(0).onTake(p,output);
            for(int i=1;i<=count;i++)h.assertTrue(menu.getSlot(i).getItem().isEmpty(),"Crafting consumes salvage once: "+row[0]);
        }
        var fire=new CraftingMenu(0,p.getInventory(),ContainerLevelAccess.create(h.getLevel(),h.absolutePos(new BlockPos(2,2,2))));
        fire.getSlot(1).set(new ItemStack(BlueprintSalvage.RED_TOAD_GLAND.get()));fire.getSlot(2).set(new ItemStack(Items.GUNPOWDER));fire.getSlot(3).set(new ItemStack(Items.COAL));
        h.assertTrue(fire.getSlot(0).getItem().is(Items.FIRE_CHARGE),"Actual toad gland recipe produces fire charge");
        var charge=fire.getSlot(0).remove(1);fire.getSlot(0).onTake(p,charge);
        for(int i=1;i<=3;i++)h.assertTrue(fire.getSlot(i).getItem().isEmpty(),"Fire-charge craft consumes each ingredient once");
        h.succeed();
    }
}
