package com.dynasty.army;
import com.dynasty.*;
import com.dynasty.entity.*;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.gametest.*;
import java.util.UUID;
@GameTestHolder("dynasty_cod6") @PrefixGameTestTemplate(false)
public final class ArmyRosterGameTests {
    private static net.minecraftforge.common.util.FakePlayer player(GameTestHelper h) {
        var p=new net.minecraftforge.common.util.FakePlayer(h.getLevel(),new com.mojang.authlib.GameProfile(UUID.randomUUID(),"cod6-army"));
        p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,new ItemStack(DynastyItems.TIGER_TALLY.get()));
        p.getInventory().setItem(1,new ItemStack(DynastyItems.SILVER_COIN.get(),64));
        p.moveTo(h.absolutePos(new BlockPos(8,2,2)),0,0);h.getLevel().addNewPlayer(p);return p;
    }
    private static void remove(net.minecraftforge.common.util.FakePlayer p){p.serverLevel().players().remove(p);p.discard();}
    @GameTest(template="bow_ritual_test")
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
    @GameTest(template="bow_ritual_test")
    public static void threeRolesRecallKeepHealthAndSlots(GameTestHelper h) {
        for(int x=0;x<16;x++)for(int z=0;z<16;z++){h.setBlock(x,1,z,Blocks.STONE);for(int y=2;y<7;y++)h.setBlock(x,y,z,Blocks.AIR);}
        var p=player(h);
        try {
            for(int i=0;i<3;i++){h.assertTrue(ArmyRoster.recruit(p,i),"Could not buy role "+i);ArmyRoster.soldiers(p).getCompound(i).putInt("Slot",i);}
            h.assertTrue(ArmyRoster.deploy(p,0,3)==3,"Formation deploy failed");
            h.assertTrue(ArmyRoster.deploy(p,0,3)==0,"Tally duplicated active soldiers");
            var r=ArmyRoster.soldiers(p).getCompound(1);
            var s=(ImperialSoldier)h.getLevel().getEntity(r.getUUID("Entity"));s.setHealth(432);
            s.getPersistentData().putInt("ArmyAttackCooldown",17);
            h.assertTrue(ArmyRoster.recall(p)==3,"Recall failed");
            h.assertTrue(r.getFloat("Health")==432,"Recall healed unit");
            h.assertTrue(ArmyRoster.deploy(p,0,3)==3,"Redeploy failed");
            s=(ImperialSoldier)h.getLevel().getEntity(r.getUUID("Entity"));
            h.assertTrue(s.getHealth()==432&&s.getPersistentData().getInt("ArmyAttackCooldown")==17,"Redeploy reset health/cooldown");
            h.assertTrue(s.getPersistentData().getInt("ArmySlot")==1,"Stable slot lost");
            p.setYRot(180);h.assertTrue(s.getPersistentData().getFloat("ArmyYaw")==0,"Camera turn rotates formation");
            h.assertTrue(ArmyRoster.coins(p)==16,"Unexpected coin total");
            ArmyRoster.recall(p);
        } finally {remove(p);}h.succeed();
    }
    @GameTest(template="bow_ritual_test")
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
}
