package com.dynasty.army;
import com.dynasty.*;
import com.dynasty.entity.*;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.gametest.*;
import java.util.UUID;
// Keep paid-roster placement/recall separate from large worldgen fixtures.
// Forced GameTest chunks become entity-visible asynchronously. Allow one second of
// loading before testing real projectiles, travel or immediate roster lookup.
@GameTestHolder("dynasty_cod6") @PrefixGameTestTemplate(false)
public final class ArmyRosterGameTests {
    private static net.minecraftforge.common.util.FakePlayer player(GameTestHelper h) {
        var p=new net.minecraftforge.common.util.FakePlayer(h.getLevel(),new com.mojang.authlib.GameProfile(UUID.randomUUID(),"cod6-army"));
        p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,new ItemStack(DynastyItems.TIGER_TALLY.get()));
        p.getInventory().setItem(1,new ItemStack(DynastyItems.SILVER_COIN.get(),64));
        p.moveTo(h.absolutePos(new BlockPos(8,2,2)),0,0);h.getLevel().addNewPlayer(p);return p;
    }
    private static void remove(net.minecraftforge.common.util.FakePlayer p){p.serverLevel().players().remove(p);p.discard();}
    @GameTest(template="bow_ritual_test",setupTicks=20,batch="cod6_paid_roster")
    public static void paidMenuRejectsReplayAndRemotePurchase(GameTestHelper h) {
        var p=player(h);var pos=h.absolutePos(new BlockPos(3,2,3));h.getLevel().setBlockAndUpdate(pos,ArmyContent.DESK.get().defaultBlockState());
        try {
            var menu=new ArmyMenu(91,p.getInventory(),pos);int code=menu.view.get(2)<<8;
            h.assertTrue(menu.clickMenuButton(p,code),"Purchase rejected");
            h.assertTrue(!menu.clickMenuButton(p,code),"Repeated revision spent twice");
            h.assertTrue(ArmyRoster.coins(p)==52&&ArmyRoster.soldiers(p).size()==1,"Payment/roster mismatch");
            p.moveTo(p.getX()+100,p.getY(),p.getZ());
            h.assertTrue(!menu.clickMenuButton(p,menu.view.get(2)<<8),"Remote table request accepted");
            var id=ArmyRoster.soldiers(p).getCompound(0).getUUID("Id");
            var copy=ArmyRoster.data(p).copy();p.getPersistentData().put(ArmyRoster.KEY,copy);
            h.assertTrue(ArmyRoster.find(p,id)!=null,"Player save lost soldier identity");
        } finally {remove(p);}h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=120,setupTicks=20,batch="cod6_paid_roster")
    public static void threeRolesRecallKeepHealthAndSlots(GameTestHelper h) {
        // Recall's real quiet-period and collision checks must not borrow nearby
        // combat/world-build fixtures. Keep native AI and all deployment rules.
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=51;y<=58;y++)
            h.setBlock(x,y,z,y==51||y==58||x==0||x==15||z==0||z==15?Blocks.STONE:Blocks.AIR);
        var p=player(h);p.moveTo(h.absolutePos(new BlockPos(8,52,2)),0,0);
        for(int i=0;i<3;i++){h.assertTrue(ArmyRoster.recruit(p,i),"Could not buy role "+i);ArmyRoster.soldiers(p).getCompound(i).putInt("Slot",i);}
        h.assertTrue(ArmyRoster.deploy(p,0,3)==3,"Formation deploy failed");
        h.assertTrue(ArmyRoster.deploy(p,0,3)==0,"Tally duplicated active soldiers");
        var r=ArmyRoster.soldiers(p).getCompound(1);
        var s=(ImperialSoldier)h.getLevel().getEntity(r.getUUID("Entity"));s.setHealth(432);
        // Stop goal ticking to inspect exactly the saved cooldown during the channel.
        s.setNoAi(true);s.getPersistentData().putInt("ArmyAttackCooldown",17);
        h.assertTrue(ArmyRoster.recall(p)==3,"Recall request failed");
        h.assertTrue(r.getString("State").equals("DEPLOYED")&&!ArmyRoster.completeRecall(p,s),"Recall skipped 40-tick channel");
        h.runAfterDelay(45,()->{
            try {
                ArmyRoster.completeRecall(p,s);
                for(var row:ArmyRoster.soldiers(p)) {
                    var n=(net.minecraft.nbt.CompoundTag)row;
                    if(n.hasUUID("Entity")&&h.getLevel().getEntity(n.getUUID("Entity")) instanceof ImperialSoldier remaining)ArmyRoster.completeRecall(p,remaining);
                }
                h.assertTrue(r.getFloat("Health")==432,"Recall healed unit");
                for(var row:ArmyRoster.soldiers(p))h.assertTrue(((net.minecraft.nbt.CompoundTag)row).getString("State").equals("RESERVE"),"Native quiet-period recall must finish each role: "+row);
                h.assertTrue(ArmyRoster.deploy(p,0,3)==3,"Redeploy failed at native collision/support/state gate: owner="+p.position()+", roster="+ArmyRoster.soldiers(p));
                var returned=(ImperialSoldier)h.getLevel().getEntity(r.getUUID("Entity"));
                h.assertTrue(returned.getHealth()==432&&returned.getPersistentData().getInt("ArmyAttackCooldown")==17,"Redeploy reset health/cooldown");
                h.assertTrue(returned.getPersistentData().getInt("ArmySlot")==1,"Stable slot lost");
                p.setYRot(180);h.assertTrue(returned.getPersistentData().getFloat("ArmyYaw")==0,"Camera turn rotates formation");
                h.assertTrue(ArmyRoster.coins(p)==16,"Unexpected coin total");
            } finally {ArmyRoster.recallNow(p,true);remove(p);}h.succeed();
        });
    }
    private static void floor(GameTestHelper h) {
        for(int x=0;x<16;x++)for(int z=0;z<16;z++){h.setBlock(x,1,z,Blocks.STONE);for(int y=2;y<7;y++)h.setBlock(x,y,z,Blocks.AIR);}
    }
    @GameTest(template="bow_ritual_test",setupTicks=20,batch="cod6_paid_roster")
    public static void directionsAndBlockedDeployAreAtomic(GameTestHelper h) {
        var origin=net.minecraft.world.phys.Vec3.ZERO;
        h.assertTrue(ArmyRoster.slot(origin,0,1,0).z>0&&ArmyRoster.slot(origin,90,1,0).x<0
            &&ArmyRoster.slot(origin,180,1,0).z<0&&ArmyRoster.slot(origin,270,1,0).x>0,"Minecraft cardinal yaw mismatch");
        var p=player(h);
        try {
            ArmyRoster.recruit(p,0);ArmyRoster.soldiers(p).getCompound(0).putInt("Slot",0);
            var block=net.minecraft.core.BlockPos.containing(ArmyRoster.slot(p.position(),0,0,0));
            h.getLevel().setBlockAndUpdate(block,Blocks.STONE.defaultBlockState());
            h.assertTrue(ArmyRoster.deploy(p,0,1)==0,"Deployed into solid block");
            h.assertTrue(ArmyRoster.soldiers(p).getCompound(0).getString("State").equals("RESERVE"),"Failed deployment consumed asset");
        } finally {remove(p);}h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod6_recall_damage",timeoutTicks=140,setupTicks=20)
    public static void environmentalDamageDelaysRecallAndReplayDoesNotResetIt(GameTestHelper h) {
        floor(h);
        // Other combat fixtures can fire beyond their template. Keep this quiet-period test enclosed.
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=2;y<=7;y++)
            if(x==0||x==15||z==0||z==15||y==7)h.setBlock(x,y,z,Blocks.STONE);
        var p=player(h);ArmyRoster.recruit(p,0);var row=ArmyRoster.soldiers(p).getCompound(0);row.putInt("Slot",1);
        h.assertTrue(ArmyRoster.deploy(p,0,1)==1,"Recall fixture failed");
        var soldier=(ImperialSoldier)h.getLevel().getEntity(row.getUUID("Entity"));
        if(soldier==null){ArmyRoster.recallNow(p,true);remove(p);h.fail("Forced fixture chunk must expose the deployed carrier after loading");return;}
        soldier.setNoAi(true);soldier.setNoGravity(true);
        ArmyRoster.recall(p);long first=row.getLong("RecallAt");
        h.runAfterDelay(15,()->{
            ArmyRoster.recall(p);h.assertTrue(row.getLong("RecallAt")==first,"Double click restarted recall");
            soldier.hurt(soldier.damageSources().generic(),1);
            h.assertTrue(row.getLong("RecallAt")>first,"Environmental damage did not delay recall");
        });
        h.runAfterDelay(42,()->h.assertTrue(!ArmyRoster.completeRecall(p,soldier)&&soldier.isAlive(),"Recall completed too soon after damage"));
        h.runAfterDelay(60,()->{
            try {h.assertTrue(ArmyRoster.completeRecall(p,soldier),"Quiet period did not finish recall");
                h.assertTrue(row.getFloat("Health")<ArmyRoster.HEALTH[0]&&!row.getBoolean("RecallRequested"),"Recall lost injury/pending state");
            } finally {ArmyRoster.recallNow(p,true);remove(p);}h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",setupTicks=20,batch="cod6_paid_roster")
    public static void malformedPresetAndFormationFailWithoutMutation(GameTestHelper h) {
        floor(h);var p=player(h);
        try {
            for(int i=0;i<2;i++){ArmyRoster.recruit(p,i);ArmyRoster.soldiers(p).getCompound(i).putInt("Slot",i);}
            var before=ArmyRoster.soldiers(p).copy();var preset=new net.minecraft.nbt.ListTag();
            for(var value:before){var row=((net.minecraft.nbt.CompoundTag)value).copy();row.putInt("Slot",0);preset.add(row);}
            ArmyRoster.data(p).put("Preset0",preset);
            h.assertTrue(!ArmyMenu.loadPreset(p,0)&&ArmyRoster.soldiers(p).equals(before),"Duplicate preset changed current formation");
            preset.getCompound(1).putInt("Slot",1);preset.getCompound(1).putUUID("Id",preset.getCompound(0).getUUID("Id"));
            h.assertTrue(!ArmyMenu.loadPreset(p,0)&&ArmyRoster.soldiers(p).equals(before),"Duplicate soldier accepted");
            preset.getCompound(1).putUUID("Id",before.getCompound(1).getUUID("Id"));
            h.assertTrue(ArmyMenu.loadPreset(p,0)&&ArmyRoster.soldiers(p).equals(before),"Valid saved formation no longer loads");
            ArmyRoster.soldiers(p).getCompound(1).putInt("Slot",0);
            h.assertTrue(ArmyRoster.deploy(p,0,2)==0,"Overlapping formation deployed");
            ArmyRoster.soldiers(p).getCompound(1).putInt("Slot",1);
            h.assertTrue(ArmyRoster.deploy(p,0,1)==0,"Silently deployed half the selected formation");
            ArmyRoster.soldiers(p).getCompound(1).putFloat("Health",Float.NaN);
            h.assertTrue(ArmyRoster.deploy(p,0,2)==0,"Non-finite soldier health accepted");
        } finally {ArmyRoster.recallNow(p,true);remove(p);}h.succeed();
    }
    @GameTest(template="bow_ritual_test",setupTicks=20,batch="cod6_paid_roster")
    public static void treatmentKeepsEquipmentCooldownAndRejectsStaleCarrier(GameTestHelper h) {
        floor(h);var p=player(h);
        try {
            ArmyRoster.recruit(p,0);var row=ArmyRoster.soldiers(p).getCompound(0);row.putInt("Slot",1);
            h.assertTrue(ArmyRoster.deploy(p,0,1)==1,"Treatment fixture failed");
            var soldier=(ImperialSoldier)h.getLevel().getEntity(row.getUUID("Entity"));
            soldier.setItemSlot(net.minecraft.world.entity.EquipmentSlot.MAINHAND,new ItemStack(net.minecraft.world.item.Items.DIAMOND_SWORD));
            soldier.getPersistentData().putInt("ArmyAttackCooldown",19);
            var old=soldier.saveWithoutId(new net.minecraft.nbt.CompoundTag());
            soldier.hurt(soldier.damageSources().genericKill(),1000000);
            h.assertTrue(row.getString("State").equals("WOUNDED"),"Soldier death did not preserve asset");
            h.assertTrue(ArmyRoster.repair(p,0)&&ArmyRoster.deploy(p,0,1)==1,"Paid repair/redeploy failed");
            var returned=(ImperialSoldier)h.getLevel().getEntity(row.getUUID("Entity"));
            h.assertTrue(returned.getMainHandItem().is(net.minecraft.world.item.Items.DIAMOND_SWORD)
                &&returned.getPersistentData().getInt("ArmyAttackCooldown")==19,"Treatment erased equipment/cooldown");
            var stale=com.dynasty.entity.DynastyEntities.IMPERIAL_SOLDIER.get().create(h.getLevel());stale.load(old);
            stale.setUUID(returned.getUUID()); // UUID alone cannot validate a stale deployment generation.
            h.assertTrue(!ArmyRoster.valid(stale,p),"Stale generation accepted");
        } finally {ArmyRoster.recallNow(p,true);remove(p);}h.succeed();
    }
    @GameTest(template="bow_ritual_test",setupTicks=20,batch="cod6_paid_roster")
    public static void pendingCarrierReloadsAfterOwnerChangesDimension(GameTestHelper h) {
        floor(h);var p=player(h);
        try {
            ArmyRoster.recruit(p,0);var row=ArmyRoster.soldiers(p).getCompound(0);row.putInt("Slot",1);
            h.assertTrue(ArmyRoster.deploy(p,0,1)==1,"Cross-dimension fixture failed");
            var soldier=(ImperialSoldier)h.getLevel().getEntity(row.getUUID("Entity"));soldier.setHealth(321);
            var saved=soldier.saveWithoutId(new net.minecraft.nbt.CompoundTag());soldier.discard();
            var destination=p.server.getLevel(ArmyEncounters.DIM);p.teleportTo(destination,0,150,0,0,0);
            ArmyRoster.recallNow(p,true);
            var restored=com.dynasty.entity.DynastyEntities.IMPERIAL_SOLDIER.get().create(h.getLevel());restored.load(saved);
            h.assertTrue(restored.getOwner()==p,"Unloaded carrier cannot resolve owner in another dimension");
            h.assertTrue(ArmyRoster.completeRecall(p,restored)&&row.getFloat("Health")==321,"Pending cross-dimension recall lost state");
            h.assertTrue(row.getString("State").equals("RESERVE")&&!row.hasUUID("Entity"),"Carrier remained stuck deployed");
        } finally {remove(p);}h.succeed();
    }

}
