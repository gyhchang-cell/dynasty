package com.dynasty;

import com.dynasty.expansion.ContentProgress;
import com.dynasty.expansion.ExpansionContent;
import com.mojang.authlib.GameProfile;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.SmithingRecipe;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.gametest.*;
import java.util.UUID;

@GameTestHolder("dynasty_cod4")
@PrefixGameTestTemplate(false)
public final class SchoolDiscoveryGameTests {
    private static ServerPlayer player(GameTestHelper h){
        var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"school-book"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);return p;
    }
    private static boolean done(ServerPlayer p,String id){var adv=p.server.getAdvancements().getAdvancement(new ResourceLocation("dynasty",id));return adv!=null&&p.getAdvancements().getOrStartProgress(adv).isDone();}
    @GameTest(template="bow_ritual_test",batch="cod4")
    public static void oldRanksDiscoverRealRecipesAndReconcileOriginalMilestonesOnce(GameTestHelper h){
        var p=player(h);var root=new CompoundTag();String[] paths={"guard","sword","archer","talisman"},base={"zhenyue_blade","liuyun_sword","zhuxing_bow","chiling_brush"},branch={"beichen_spear","chengying_sword","fengling_bow","leifu_staff"};
        for(String path:paths){var state=new CompoundTag();state.putInt("rank",3);state.putLong("progress",7);root.put(path,state);}p.getPersistentData().put("dynastySchoolProgression",root);
        ContentProgress.login(new PlayerEvent.PlayerLoggedInEvent(p));
        for(int i=0;i<4;i++){
            h.assertTrue(done(p,"school_"+paths[i]+"_rank_1")&&done(p,"school_"+paths[i]+"_rank_3")&&!done(p,"school_"+paths[i]+"_rank_6"),"Original achieved milestones reconcile without inventing ranks");
            for(String recipe:new String[]{base[i],"branch_"+branch[i],"branch_"+branch[i]+"_advance"})h.assertTrue(p.getRecipeBook().contains(new ResourceLocation("dynasty",recipe)),"Existing registered recipe discovered: "+recipe);
            h.assertTrue(DynastySchoolProgression.progress(p,paths[i])==7,"Discovery does not alter invested combat progress");
        }
        int xp=p.totalExperience;ContentProgress.reconcile(p);h.assertTrue(p.totalExperience==xp&&p.getInventory().isEmpty(),"Repeated login reconciliation pays no XP or replacement equipment");
        var q=player(h);DynastySchoolProgression.onClone(new PlayerEvent.Clone(q,p,true));ContentProgress.reconcile(q);
        h.assertTrue(DynastySchoolProgression.rank(q,"guard")==3&&done(q,"school_guard_rank_3")&&q.getRecipeBook().contains(new ResourceLocation("dynasty","branch_beichen_spear")),"Cloned canonical state can regrant discovery without new progression storage");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4")
    public static void discoveryNeverRestrictsSmithingAndOwnedBranchReconcilesWithoutRank(GameTestHelper h){
        var p=player(h);var branch=(SmithingRecipe)h.getLevel().getRecipeManager().byKey(new ResourceLocation("dynasty","branch_beichen_spear")).orElseThrow();
        var trained=new ItemStack(ExpansionContent.item("zhenyue_blade"));var growth=trained.getOrCreateTagElement(DynastyWeaponProgression.KEY);growth.putUUID("identity",UUID.randomUUID());growth.putInt("level",7);growth.putLong("xp",13);growth.putString("school","guard");
        var smithing=new SimpleContainer(new ItemStack(ExpansionContent.item("blueprint")),trained,new ItemStack(ExpansionContent.item("refined_steel")));
        h.assertTrue(DynastySchoolProgression.rank(p,"guard")==0&&branch.matches(smithing,h.getLevel()),"Rank-zero player can still use the unchanged existing smithing recipe");
        var upgraded=branch.assemble(smithing,h.getLevel().registryAccess());h.assertTrue(upgraded.is(ExpansionContent.item("beichen_spear"))&&upgraded.getTag().equals(trained.getTag()),"Original smithing evolution preserves exact growth investment and identity");
        p.getInventory().setItem(0,upgraded);ContentProgress.reconcile(p);
        h.assertTrue(p.getRecipeBook().contains(new ResourceLocation("dynasty","branch_beichen_spear"))&&p.getRecipeBook().contains(new ResourceLocation("dynasty","branch_beichen_spear_advance")),"Existing owned branch backfills actual discovery on old saves");
        h.assertTrue(DynastySchoolProgression.rank(p,"guard")==0&&!done(p,"school_guard_rank_1"),"Owned equipment does not fake a combat rank");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4")
    public static void wornSchoolAccessoryDiscoversActualRecipeWithoutClaimingCombatRank(GameTestHelper h){
        var p=player(h);SchoolCombatGameTests.equip(p,"body",new ItemStack(ExpansionContent.item("xuanjia_clasp")));
        ContentProgress.reconcile(p);
        h.assertTrue(p.getRecipeBook().contains(new ResourceLocation("dynasty","xuanjia_clasp")),"Actual owned or Curios-worn school ornament backfills its existing recipe");
        h.assertTrue(!done(p,"school_guard_rank_1")&&DynastySchoolProgression.rank(p,"guard")==0,"Wearing an ornament does not fabricate combat mastery");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4")
    public static void actualPhoenixRingTickExtinguishesAndPreservesItsFifteenPercentAttackWindow(GameTestHelper h){
        var p=player(h);SchoolCombatGameTests.equip(p,"ring",new ItemStack(ExpansionContent.item("phoenix_ring")));p.setSecondsOnFire(5);DynastyTrinkets.tick(p);
        h.assertTrue(!p.isOnFire()&&com.dynasty.expansion.EquipmentBehaviors.phoenixAttackActive(p),"Actual worn-ring tick extinguishes while preserving the finite offensive window");
        var target=new net.minecraft.world.entity.monster.Zombie(h.getLevel());var hit=new net.minecraftforge.event.entity.living.LivingHurtEvent(target,p.damageSources().playerAttack(p),100);com.dynasty.expansion.EquipmentBehaviors.hurt(hit);
        h.assertTrue(Math.abs(hit.getAmount()-115)<.001,"Actual extinguished wearer still receives exactly fifteen percent in the existing primary damage hook");
        SchoolCombatGameTests.equip(p,"ring",ItemStack.EMPTY);var bare=new net.minecraftforge.event.entity.living.LivingHurtEvent(target,p.damageSources().playerAttack(p),100);com.dynasty.expansion.EquipmentBehaviors.hurt(bare);
        h.assertTrue(bare.getAmount()==100,"Unequip immediately removes the fire-window attack bonus");h.succeed();
    }
}
