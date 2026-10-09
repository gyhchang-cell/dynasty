package com.dynasty.army;
import com.dynasty.*;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.gametest.*;
import java.util.UUID;
@GameTestHolder("dynasty_cod6") @PrefixGameTestTemplate(false)
public final class ArmyEncounterGameTests {
    @GameTest(template="bow_ritual_test")
    public static void lockedRosterAndInterruptedRecovery(GameTestHelper h) {
        var p=new net.minecraftforge.common.util.FakePlayer(h.getLevel(),new com.mojang.authlib.GameProfile(UUID.randomUUID(),"cod6-arena"));
        p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,new ItemStack(DynastyItems.TIGER_TALLY.get()));
        p.moveTo(h.absolutePos(new BlockPos(2,2,2)),0,0);
        var state=new CompoundTag();state.putUUID("Id",UUID.randomUUID());state.putString("Phase","ACTIVE");state.putInt("Stage",0);
        state.putString("ReturnDimension",h.getLevel().dimension().location().toString());state.putDouble("ReturnX",p.getX());state.putDouble("ReturnY",p.getY());state.putDouble("ReturnZ",p.getZ());
        ArmyRoster.data(p).put("Encounter",state);
        var r=new CompoundTag();r.putUUID("Id",UUID.randomUUID());r.putUUID("Entity",UUID.randomUUID());r.putString("State","DEPLOYED");r.putFloat("Health",420);r.putInt("Slot",0);ArmyRoster.soldiers(p).add(r);
        h.assertTrue(ArmyRoster.deploy(p,0,1)==0&&ArmyRoster.recall(p)==0,"Active battle allowed roster swap");
        var menu=new ArmyMenu(95,p.getInventory(),null);h.assertTrue(!menu.clickMenuButton(p,(menu.view.get(2)<<8)|13),"Battle allowed quick fill");
        ArmyEncounters.finish(p,false,"test interruption");
        h.assertTrue(r.getString("State").equals("WOUNDED")&&!r.hasUUID("Entity"),"Unconfirmed carrier duplicated after recovery");
        h.assertTrue(!p.getPersistentData().getBoolean("dynasty_firstkill_rebel_general"),"Defeat granted first kill");p.discard();h.succeed();
    }
    @GameTest(template="bow_ritual_test")
    public static void firstKillReceiptAndNewBossBudget(GameTestHelper h) {
        var p=new net.minecraftforge.common.util.FakePlayer(h.getLevel(),new com.mojang.authlib.GameProfile(UUID.randomUUID(),"cod6-receipt"));
        DynastyBossCombat.awardFirstKill(p,"rebel_general");int count=p.getInventory().countItem(net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(new net.minecraft.resources.ResourceLocation("dynasty","rebel_head")));
        DynastyBossCombat.awardFirstKill(p,"rebel_general");h.assertTrue(p.getInventory().countItem(net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(new net.minecraft.resources.ResourceLocation("dynasty","rebel_head")))==count&&count==1,"First kill reward repeated");
        var boss=com.dynasty.entity.DynastyEntities.REBEL_GENERAL.get().create(h.getLevel());h.getLevel().addFreshEntity(boss);
        h.assertTrue(boss.getMaxHealth()>=8000,"Boss stayed at old 1024 HP cap");
        float before=boss.getMaxHealth();var save=boss.saveWithoutId(new CompoundTag());boss.discard();var restored=com.dynasty.entity.DynastyEntities.REBEL_GENERAL.get().create(h.getLevel());restored.load(save);
        h.getLevel().addFreshEntity(restored);h.assertTrue(restored.getMaxHealth()==before,"Join duplicated balance multiplier");restored.discard();p.discard();h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=400)
    public static void realBattlefieldPrepareDeployStartAndEvacuate(GameTestHelper h) {
        var p=new net.minecraftforge.common.util.FakePlayer(h.getLevel(),new com.mojang.authlib.GameProfile(UUID.randomUUID(),"cod6-field"));
        p.setGameMode(net.minecraft.world.level.GameType.CREATIVE);p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,new ItemStack(DynastyItems.TIGER_TALLY.get()));
        p.getInventory().setItem(1,new ItemStack(DynastyItems.SILVER_COIN.get(),64));
        p.moveTo(h.absolutePos(new BlockPos(3,2,3)),0,0);h.getLevel().addNewPlayer(p);
        try {
            h.assertTrue(ArmyEncounters.prepare(p,0),"Could not allocate empty battlefield");
            h.assertTrue(p.level().dimension()==ArmyEncounters.DIM,"Player did not enter existing Jiuxiao dimension");
            for(int role=0;role<3;role++){ArmyRoster.recruit(p,role);ArmyRoster.soldiers(p).getCompound(role).putInt("Slot",role);}
            h.assertTrue(ArmyRoster.deploy(p,0,3)==3,"Battlefield rejected formation footprint");
            h.assertTrue(ArmyEncounters.start(p),"Battle did not start with paid troops");
            var state=ArmyEncounters.session(p);var boss=p.serverLevel().getEntity(state.getUUID("Boss"));
            h.assertTrue(boss!=null&&boss.isAlive(),"Boss missing after server-authorized start");
            h.assertTrue(!ArmyEncounters.start(p),"Repeated start duplicated boss");
            ArmyEncounters.finish(p,false,"QA撤离");
            h.assertTrue(p.level()==h.getLevel(),"Return dimension lost");
            for(var value:ArmyRoster.soldiers(p))h.assertTrue(((CompoundTag)value).getString("State").equals("RESERVE"),"Surviving deployed soldier lost on return");
            h.assertTrue(!p.getPersistentData().getBoolean("dynasty_firstkill_rebel_general"),"Evacuation gave victory reward");
        } finally {if(ArmyEncounters.inside(p))ArmyEncounters.finish(p,false,"QA cleanup");p.serverLevel().players().remove(p);p.discard();}
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=400)
    public static void actualBossDeathReceiptThenArmyWipeDefeat(GameTestHelper h) {
        var p=new net.minecraft.server.level.ServerPlayer(h.getLevel().getServer(),h.getLevel(),new com.mojang.authlib.GameProfile(UUID.randomUUID(),"cod6-results"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.setGameMode(net.minecraft.world.level.GameType.CREATIVE);p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,new ItemStack(DynastyItems.TIGER_TALLY.get()));
        p.getInventory().setItem(1,new ItemStack(DynastyItems.SILVER_COIN.get(),64));p.moveTo(h.absolutePos(new BlockPos(3,2,3)),0,0);h.getLevel().addNewPlayer(p);
        try {
            ArmyRoster.recruit(p,2);ArmyRoster.soldiers(p).getCompound(0).putInt("Slot",1);
            h.assertTrue(ArmyEncounters.prepare(p,0)&&ArmyRoster.deploy(p,0,1)==1&&ArmyEncounters.start(p),"Victory fixture not ready");
            var state=ArmyEncounters.session(p);var boss=(net.minecraft.world.entity.LivingEntity)p.serverLevel().getEntity(state.getUUID("Boss"));
            boss.hurt(p.damageSources().playerAttack(p),1000000);
            ArmyEncounters.settleOutcome(p);
            h.assertTrue(state.getString("Phase").equals("WON"),"Actual boss death did not settle victory");
            h.assertTrue(p.getInventory().countItem(DynastyRelics.REBEL_HEAD.get())>=2,"Boss drops stranded in the evacuated battlefield");
            var adv=p.server.getAdvancements().getAdvancement(new net.minecraft.resources.ResourceLocation("dynasty","army_clear_rebel_general"));
            h.assertTrue(p.getAdvancements().getOrStartProgress(adv).isDone(),"Quest receipt missing");
            h.assertTrue(p.level()==h.getLevel(),"Victory did not return commander");
            h.assertTrue(ArmyEncounters.prepare(p,0)&&ArmyRoster.deploy(p,0,1)==1&&ArmyEncounters.start(p),"Defeat fixture not ready");
            state=ArmyEncounters.session(p);var row=ArmyRoster.soldiers(p).getCompound(0);
            var soldier=(net.minecraft.world.entity.LivingEntity)p.serverLevel().getEntity(row.getUUID("Entity"));
            soldier.hurt(p.damageSources().genericKill(),1000000);
            ArmyEncounters.settleOutcome(p);
            h.assertTrue(state.getString("Phase").equals("LOST")&&row.getString("State").equals("WOUNDED"),"Actual troop wipe did not preserve defeat/wound");
        } finally {if(ArmyEncounters.inside(p))ArmyEncounters.finish(p,false,"QA cleanup");p.serverLevel().players().remove(p);p.discard();}
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=400)
    public static void bossAndLastSoldierSameTickWinInBothOrders(GameTestHelper h) {
        var p=new net.minecraft.server.level.ServerPlayer(h.getLevel().getServer(),h.getLevel(),new com.mojang.authlib.GameProfile(UUID.randomUUID(),"cod6-same-tick"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.setGameMode(net.minecraft.world.level.GameType.CREATIVE);p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,new ItemStack(DynastyItems.TIGER_TALLY.get()));
        p.getInventory().setItem(1,new ItemStack(DynastyItems.SILVER_COIN.get(),64));p.moveTo(h.absolutePos(new BlockPos(3,2,3)),0,0);h.getLevel().addNewPlayer(p);
        try {
            ArmyRoster.recruit(p,2);var row=ArmyRoster.soldiers(p).getCompound(0);row.putInt("Slot",1);
            for(boolean bossFirst:new boolean[]{false,true}) {
                if(row.getString("State").equals("WOUNDED"))h.assertTrue(ArmyRoster.repair(p,0),"Could not treat prior casualty");
                h.assertTrue(ArmyEncounters.prepare(p,0)&&ArmyRoster.deploy(p,0,1)==1&&ArmyEncounters.start(p),"Same-tick fixture not ready");
                var state=ArmyEncounters.session(p);
                h.assertTrue(state.getList("LockedRoster",10).size()==1,"Battle did not persist locked roster");
                var boss=(net.minecraft.world.entity.LivingEntity)p.serverLevel().getEntity(state.getUUID("Boss"));
                var soldier=(net.minecraft.world.entity.LivingEntity)p.serverLevel().getEntity(row.getUUID("Entity"));
                if(bossFirst)boss.hurt(p.damageSources().playerAttack(p),1000000);
                soldier.hurt(p.damageSources().genericKill(),1000000);
                if(!bossFirst)boss.hurt(p.damageSources().playerAttack(p),1000000);
                h.assertTrue(state.getString("Phase").equals("ACTIVE"),"Death callback settled before end-tick snapshot");
                ArmyEncounters.settleOutcome(p);
                h.assertTrue(state.getString("Phase").equals("WON")&&row.getString("State").equals("WOUNDED"),"Simultaneous victory/wipe depends on death order");
                int rewards=p.getInventory().countItem(DynastyRelics.REBEL_HEAD.get());
                ArmyEncounters.settleOutcome(p);ArmyEncounters.finish(p,true,"duplicate");
                h.assertTrue(p.getInventory().countItem(DynastyRelics.REBEL_HEAD.get())==rewards,"Repeated settlement duplicated loot");
            }
        } finally {if(ArmyEncounters.inside(p))ArmyEncounters.finish(p,false,"QA cleanup");p.serverLevel().players().remove(p);p.discard();}h.succeed();
    }
    @GameTest(template="bow_ritual_test")
    public static void activeRetreatRequiresFreshSecondClick(GameTestHelper h) {
        var p=new net.minecraftforge.common.util.FakePlayer(h.getLevel(),new com.mojang.authlib.GameProfile(UUID.randomUUID(),"cod6-confirm"));
        p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,new ItemStack(DynastyItems.TIGER_TALLY.get()));
        var state=new CompoundTag();state.putUUID("Id",UUID.randomUUID());state.putString("Phase","ACTIVE");state.putInt("Stage",0);
        state.putString("ReturnDimension",h.getLevel().dimension().location().toString());ArmyRoster.data(p).put("Encounter",state);
        var menu=new ArmyMenu(98,p.getInventory(),null);int first=(menu.view.get(2)<<8)|201;
        h.assertTrue(menu.clickMenuButton(p,first)&&ArmyEncounters.active(p),"First retreat click forfeited battle");
        h.assertTrue(!menu.clickMenuButton(p,first)&&ArmyEncounters.active(p),"Repeated packet confirmed retreat");
        h.assertTrue(!ArmyRoster.recruit(p,0),"Active encounter allowed direct recruitment");
        h.assertTrue(menu.clickMenuButton(p,(menu.view.get(2)<<8)|201)&&state.getString("Phase").equals("LOST"),"Confirmed retreat did not settle defeat");
        p.discard();h.succeed();
    }

}
