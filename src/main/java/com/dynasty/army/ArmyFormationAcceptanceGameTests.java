package com.dynasty.army;

import com.dynasty.DynastyItems;
import com.dynasty.entity.ImperialSoldier;
import com.mojang.authlib.GameProfile;
import java.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.common.util.FakePlayer;
import net.minecraftforge.gametest.*;

/** Actual native navigation, not just a comparison of ideal slot coordinates. */
@GameTestHolder("dynasty_cod6") @PrefixGameTestTemplate(false)
public final class ArmyFormationAcceptanceGameTests {
    @GameTest(template="bow_ritual_test",batch="cod6_native_formation_walk",timeoutTicks=1900,setupTicks=20)
    public static void ninePaidSoldiersKeepSlotsAcrossFourDirectionsAndCameraTurns(GameTestHelper h) {
        var level=h.getLevel();var center=Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(8,90,5)));
        var forced=forcePlatform(h,-6,-6,22,24);
        for(int x=-6;x<=22;x++)for(int z=-6;z<=24;z++)for(int y=89;y<=94;y++)
            h.setBlock(x,y,z,y==89||y==94?Blocks.STONE:Blocks.AIR);
        var owner=new FakePlayer(level,new GameProfile(UUID.randomUUID(),"formation-walk"));
        owner.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(DynastyItems.TIGER_TALLY.get()));
        owner.moveTo(center.x,center.y,center.z,0,0);level.addNewPlayer(owner);
        var troops=new ArrayList<ImperialSoldier>();var identities=new HashMap<UUID,Integer>();
        Runnable cleanup=()->{troops.forEach(ImperialSoldier::discard);level.players().remove(owner);owner.discard();forced.forEach(c->level.setChunkForced(c.x,c.z,false));};
        h.runAfterDelay(20,()->{
            try {
                for(int i=0;i<9;i++) {
                    owner.getInventory().setItem(2,new ItemStack(DynastyItems.SILVER_COIN.get(),12));
                    h.assertTrue(ArmyRoster.recruit(owner,0),"Paid blade recruitment failed");
                    ArmyRoster.soldiers(owner).getCompound(i).putInt("Slot",i);
                }
                h.assertTrue(ArmyRoster.deploy(owner,0,9)==9,"Native nine-unit deployment failed");
                for(var value:ArmyRoster.soldiers(owner)) {
                    var row=(net.minecraft.nbt.CompoundTag)value;
                    var soldier=(ImperialSoldier)level.getEntity(row.getUUID("Entity"));troops.add(soldier);
                    identities.put(row.getUUID("Id"),row.getInt("Slot"));
                }
            } catch(RuntimeException|Error e){cleanup.run();throw e;}
        });
        // Move the real owner, then let the unmodified entity tick/navigation settle.
        Vec3[] offsets={Vec3.ZERO,Vec3.ZERO,new Vec3(4,0,0),new Vec3(4,0,4),new Vec3(0,0,4),Vec3.ZERO,
            new Vec3(4,0,4),Vec3.ZERO,new Vec3(4,0,0),new Vec3(0,0,4),Vec3.ZERO,
            new Vec3(4,0,0),new Vec3(4,0,4),new Vec3(0,0,4),Vec3.ZERO,
            new Vec3(4,0,4),new Vec3(4,0,0),new Vec3(0,0,4),Vec3.ZERO};
        for(int step=0;step<offsets.length;step++) {
            final int stage=step;final var offset=offsets[step];
            h.runAfterDelay(40+step*90,()->owner.moveTo(center.add(offset).x,center.y,center.add(offset).z,stage*90,0));
            h.runAfterDelay(120+step*90,()->{
                try {
                    for(var soldier:troops) {
                        var tag=soldier.getPersistentData();var id=tag.getUUID("ArmySoldier");
                        h.assertTrue(soldier.isAlive()&&ArmyRoster.valid(soldier,owner),"Walking lost paid identity");
                        h.assertTrue(tag.getInt("ArmySlot")==identities.get(id)&&tag.getFloat("ArmyYaw")==0,"Camera turn changed saved slot/orientation");
                        var ideal=ArmyRoster.slot(owner.position(),0,identities.get(id),0);
                        double error=soldier.position().distanceTo(ideal);
                        System.out.println("COD6 native formation stage="+stage+" slot="+identities.get(id)+" error="+error+" entityTicks="+soldier.tickCount);
                        h.assertTrue(error<=.35,"Native settled slot error "+error+" at stage "+stage+", slot "+identities.get(id)+", actual="+soldier.position()+", ideal="+ideal
                            +", noAI="+soldier.isNoAi()+", water="+soldier.isInWater()+", ground="+soldier.onGround()+", passenger="+soldier.isPassenger()
                            +", nav="+soldier.getNavigation().getPath()+", navTarget="+soldier.getNavigation().getTargetPos()
                            +", nextNode="+(soldier.getNavigation().getPath()==null?"none":soldier.getNavigation().getPath().getNextNodeIndex())
                            +", wanted="+soldier.getMoveControl().getWantedX()+","+soldier.getMoveControl().getWantedZ()
                            +", speed="+soldier.getSpeed()+", velocity="+soldier.getDeltaMovement()+", yaw="+soldier.getYRot()
                            +", clear="+level.noCollision(soldier,soldier.getBoundingBox().expandTowards(ideal.subtract(soldier.position())).deflate(.01))
                            +", floor="+level.getBlockState(soldier.blockPosition().below()));
                    }
                    if(stage==offsets.length-1){cleanup.run();h.succeed();}
                } catch(RuntimeException|Error e){cleanup.run();throw e;}
            });
        }
    }
    /** The walking platform extends past the template's own forced chunks. */
    private static List<net.minecraft.world.level.ChunkPos> forcePlatform(GameTestHelper h,int minX,int minZ,int maxX,int maxZ) {
        var level=h.getLevel();var a=h.absolutePos(new BlockPos(minX,0,minZ));var b=h.absolutePos(new BlockPos(maxX,0,maxZ));
        var added=new ArrayList<net.minecraft.world.level.ChunkPos>();
        for(int x=Math.min(a.getX(),b.getX())>>4;x<=Math.max(a.getX(),b.getX())>>4;x++)
            for(int z=Math.min(a.getZ(),b.getZ())>>4;z<=Math.max(a.getZ(),b.getZ())>>4;z++) {
                var chunk=new net.minecraft.world.level.ChunkPos(x,z);
                if(!level.getForcedChunks().contains(chunk.toLong())) {level.setChunkForced(x,z,true);added.add(chunk);}
            }
        return added;
    }
    @GameTest(template="bow_ritual_test",batch="cod6_native_formation_obstacles",timeoutTicks=160,setupTicks=20)
    public static void finalApproachNeverCrossesWallsOrUnsupportedGaps(GameTestHelper h) {
        var level=h.getLevel();
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=69;y<=74;y++)
            h.setBlock(x,y,z,y==69||y==74?Blocks.STONE:Blocks.AIR);
        var center=Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(8,70,3)));
        var owner=new FakePlayer(level,new GameProfile(UUID.randomUUID(),"formation-obstacle"));
        owner.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(DynastyItems.TIGER_TALLY.get()));
        owner.moveTo(center.x,center.y,center.z,0,0);level.addNewPlayer(owner);
        var troops=new ArrayList<ImperialSoldier>();
        Runnable cleanup=()->{troops.forEach(ImperialSoldier::discard);level.players().remove(owner);owner.discard();};
        h.runAfterDelay(20,()->{
            try {
                owner.getInventory().setItem(2,new ItemStack(DynastyItems.SILVER_COIN.get(),12));
                h.assertTrue(ArmyRoster.recruit(owner,0),"Obstacle fixture purchase failed");
                ArmyRoster.soldiers(owner).getCompound(0).putInt("Slot",1);
                h.assertTrue(ArmyRoster.deploy(owner,0,1)==1,"Obstacle fixture deployment failed");
                var soldier=(ImperialSoldier)level.getEntity(ArmyRoster.soldiers(owner).getCompound(0).getUUID("Entity"));troops.add(soldier);
                var slot=ArmyRoster.slot(owner.position(),0,1,0);soldier.moveTo(slot.x+1.8,slot.y,slot.z,0,0);
                for(int z=0;z<16;z++)for(int y=70;y<74;y++)h.setBlock(9,y,z,Blocks.STONE);
            } catch(RuntimeException|Error e){cleanup.run();throw e;}
        });
        h.runAfterDelay(65,()->{
            try {
                var soldier=troops.get(0);var slot=ArmyRoster.slot(owner.position(),0,1,0);
                h.assertTrue(soldier.getX()>slot.x+.8&&level.noCollision(soldier,soldier.getBoundingBox().deflate(.01)),"Close-slot steering crossed a solid wall");
                // Replace the wall by a one-block-wide trench, with no near floor.
                for(int z=0;z<16;z++)for(int y=66;y<74;y++)h.setBlock(9,y,z,Blocks.AIR);
                soldier.moveTo(slot.x+1.8,slot.y,slot.z,0,0);
            } catch(RuntimeException|Error e){cleanup.run();throw e;}
        });
        h.runAfterDelay(115,()->{
            try {
                var soldier=troops.get(0);
                h.assertTrue(soldier.isAlive()&&soldier.getY()>=center.y-.1,"Close-slot steering walked a paid soldier into an unsupported gap");
                h.assertTrue(ArmyRoster.valid(soldier,owner),"Obstacle lost paid identity");h.succeed();
            } finally {cleanup.run();}
        });
    }
    @GameTest(template="bow_ritual_test",batch="cod6_native_formation_identity",timeoutTicks=160,setupTicks=20)
    public static void copiedTallyCannotControlForeignTroopsAndCasualtyLeavesItsSlotEmpty(GameTestHelper h) {
        var level=h.getLevel();var center=Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(8,60,4)));
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=59;y<=64;y++)
            h.setBlock(x,y,z,y==59||y==64?Blocks.STONE:Blocks.AIR);
        var owner=new FakePlayer(level,new GameProfile(UUID.randomUUID(),"formation-owner"));
        var other=new FakePlayer(level,new GameProfile(UUID.randomUUID(),"formation-foreign"));
        owner.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(DynastyItems.TIGER_TALLY.get()));
        other.setItemInHand(InteractionHand.MAIN_HAND,owner.getMainHandItem().copy());
        owner.moveTo(center.x,center.y,center.z,0,0);other.moveTo(center.x,center.y,center.z-2,0,0);
        level.addNewPlayer(owner);level.addNewPlayer(other);
        var troops=new ArrayList<ImperialSoldier>();var identities=new ArrayList<UUID>();
        Runnable cleanup=()->{troops.forEach(ImperialSoldier::discard);level.players().remove(owner);level.players().remove(other);owner.discard();other.discard();};
        h.runAfterDelay(20,()->{
            try {
                for(int i=0;i<3;i++) {
                    owner.getInventory().setItem(2,new ItemStack(DynastyItems.SILVER_COIN.get(),12));
                    h.assertTrue(ArmyRoster.recruit(owner,0),"Identity fixture recruitment failed");
                    var row=ArmyRoster.soldiers(owner).getCompound(i);row.putInt("Slot",i);identities.add(row.getUUID("Id"));
                }
                h.assertTrue(ArmyRoster.deploy(owner,0,3)==3,"Identity fixture deployment failed");
                for(var id:identities)troops.add((ImperialSoldier)level.getEntity(ArmyRoster.find(owner,id).getUUID("Entity")));
                var menu=new ArmyMenu(97,owner.getInventory(),null);
                h.assertTrue(!menu.clickMenuButton(other,(menu.view.get(2)<<8)|11),"Foreign copied tally operated owner's menu");
                h.assertTrue(new ArmyMenu(98,other.getInventory(),null).total()==0,"Copied tally copied paid assets");
                for(var soldier:troops)h.assertTrue(!ArmyRoster.valid(soldier,other),"Foreign player validated a paid carrier");
                troops.get(1).hurt(troops.get(1).damageSources().genericKill(),1000000);
                var casualty=ArmyRoster.find(owner,identities.get(1));
                h.assertTrue(casualty.getString("State").equals("WOUNDED")&&casualty.getInt("Slot")==1,"Casualty erased paid identity or its gap");
            } catch(RuntimeException|Error e){cleanup.run();throw e;}
        });
        h.runAfterDelay(100,()->{
            try {
                for(int i:new int[]{0,2})h.assertTrue(ArmyRoster.valid(troops.get(i),owner)
                    &&troops.get(i).getPersistentData().getInt("ArmySlot")==i
                    &&ArmyRoster.find(owner,identities.get(i)).getInt("Slot")==i,"Survivor automatically filled casualty's slot");
                h.assertTrue(ArmyRoster.soldiers(owner).size()==3,"Casualty deleted paid asset or generated replacement");h.succeed();
            } finally {cleanup.run();}
        });
    }
    @GameTest(template="bow_ritual_test",batch="cod6_deployment_rollback",setupTicks=20,timeoutTicks=60)
    public static void rejectedSecondCarrierRollsBackOnlyThisDeploymentWithoutDeathOrAssetLoss(GameTestHelper h) {
        var level=h.getLevel();
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=109;y<=114;y++)
            h.setBlock(x,y,z,y==109||y==114?Blocks.STONE:Blocks.AIR);
        var owner=new FakePlayer(level,new GameProfile(UUID.randomUUID(),"rollback-owner"));
        var other=new FakePlayer(level,new GameProfile(UUID.randomUUID(),"rollback-other"));
        var candidates=new ArrayList<ImperialSoldier>();
        java.util.function.Consumer<net.minecraftforge.event.entity.EntityJoinLevelEvent> reject=e->{
            if(e.getEntity() instanceof ImperialSoldier s&&s.getOwner()==owner) {
                candidates.add(s);
                if(s.getPersistentData().getInt("ArmySlot")==1)e.setCanceled(true);
            }
        };
        var deaths=new java.util.concurrent.atomic.AtomicInteger();
        java.util.function.Consumer<net.minecraftforge.event.entity.living.LivingDeathEvent> countDeath=e->{
            if(e.getEntity() instanceof ImperialSoldier s&&s.getOwner()==owner)deaths.incrementAndGet();
        };
        var bus=net.minecraftforge.common.MinecraftForge.EVENT_BUS;
        try {
            for(var p:List.of(owner,other)) {
                p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(DynastyItems.TIGER_TALLY.get()));
                p.getInventory().setItem(2,new ItemStack(DynastyItems.SILVER_COIN.get(),64));
                var at=Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(p==owner?5:12,110,3)));
                p.moveTo(at.x,at.y,at.z,0,0);level.addNewPlayer(p);
            }
            h.assertTrue(ArmyRoster.recruit(other,0),"Foreign paid fixture purchase failed");
            ArmyRoster.soldiers(other).getCompound(0).putInt("Slot",1);
            h.assertTrue(ArmyRoster.deploy(other,0,1)==1,"Foreign paid fixture deployment failed");
            var foreign=(ImperialSoldier)level.getEntity(ArmyRoster.soldiers(other).getCompound(0).getUUID("Entity"));
            foreign.setNoAi(true);
            for(int role=0;role<3;role++) {
                h.assertTrue(ArmyRoster.recruit(owner,role),"Rollback fixture purchase failed");
                ArmyRoster.soldiers(owner).getCompound(role).putInt("Slot",role);
            }
            var paid=ArmyRoster.data(owner).copy();
            var foreignPaid=ArmyRoster.data(other).copy();
            var inventory=owner.getInventory().save(new net.minecraft.nbt.ListTag());
            var box=foreign.getBoundingBox().inflate(20);
            int items=level.getEntitiesOfClass(net.minecraft.world.entity.item.ItemEntity.class,box).size();
            int xp=level.getEntitiesOfClass(net.minecraft.world.entity.ExperienceOrb.class,box).size();
            bus.addListener(reject);bus.addListener(countDeath);
            h.assertTrue(ArmyRoster.deploy(owner,0,3)==0&&candidates.size()==2,"The real second-carrier spawn rejection was not reached");
            h.assertTrue(candidates.stream().allMatch(net.minecraft.world.entity.Entity::isRemoved),"Rejected deployment left a live partial team");
            h.assertTrue(ArmyRoster.data(owner).equals(paid)&&owner.getInventory().save(new net.minecraft.nbt.ListTag()).equals(inventory),"Rollback changed paid records, generation, revision or inventory");
            h.assertTrue(foreign.isAlive()&&ArmyRoster.valid(foreign,other)&&ArmyRoster.data(other).equals(foreignPaid),"Rollback affected another owner's paid soldier");
            h.assertTrue(deaths.get()==0&&level.getEntitiesOfClass(net.minecraft.world.entity.item.ItemEntity.class,box).size()==items
                &&level.getEntitiesOfClass(net.minecraft.world.entity.ExperienceOrb.class,box).size()==xp,"Rollback used a death/drop path");
            bus.unregister(reject);
            h.assertTrue(ArmyRoster.deploy(owner,0,3)==3,"A failed deployment prevented a later legal retry");
            for(var value:ArmyRoster.soldiers(owner)) {
                var row=(net.minecraft.nbt.CompoundTag)value;
                h.assertTrue(row.getLong("Generation")==1&&level.getEntity(row.getUUID("Entity")) instanceof ImperialSoldier,"Retry lost a paid identity or consumed a generation");
            }
            h.succeed();
        } finally {
            bus.unregister(reject);bus.unregister(countDeath);
            candidates.forEach(ImperialSoldier::discard);
            for(var p:List.of(owner,other)) {
                ArmyRoster.recallNow(p,true);
                level.players().remove(p);p.discard();
            }
        }
    }
    private ArmyFormationAcceptanceGameTests(){}
}
