package com.dynasty.dungeon;

import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.common.util.FakePlayer;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;
import java.util.*;

@GameTestHolder("dynasty_cod2")
@PrefixGameTestTemplate(false)
public final class DungeonTrapGameTests {
    private static FakePlayer player(GameTestHelper h,BlockPos pos){
        var p=new FakePlayer(h.getLevel(),new com.mojang.authlib.GameProfile(UUID.randomUUID(),"trap-test")){
            // Forge's default automation player ignores every DamageSource. This fixture exercises real health damage.
            @Override public boolean isInvulnerableTo(net.minecraft.world.damagesource.DamageSource source){return false;}
        };p.setNoGravity(true);
        // FakePlayer.tick is intentionally empty, so its ServerPlayer birth grace never expires.
        // Clear that test-only field instead of bypassing production damage rules.
        try{var grace=net.minecraft.server.level.ServerPlayer.class.getDeclaredField("spawnInvulnerableTime");grace.setAccessible(true);grace.setInt(p,0);}
        catch(ReflectiveOperationException e){throw new IllegalStateException("Damage fixture could not finish spawn grace",e);}
        p.getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.MAX_HEALTH).setBaseValue(200);p.setHealth(200);
        p.setPos(net.minecraft.world.phys.Vec3.atBottomCenterOf(pos));h.getLevel().addNewPlayer(p);return p;
    }
    private static void remove(GameTestHelper h,FakePlayer p){h.getLevel().removePlayerImmediately(p,Entity.RemovalReason.DISCARDED);}
    private static DungeonMechanismBlockEntity marker(GameTestHelper h,BlockPos pos,net.minecraft.world.level.block.Block block,String id){
        h.getLevel().setBlockAndUpdate(pos,block.defaultBlockState());var be=(DungeonMechanismBlockEntity)h.getLevel().getBlockEntity(pos);
        be.configure(UUID.randomUUID(),"qa",id,pos,-1,List.of());return be;
    }
    @GameTest(template="bow_ritual_test",batch="cod2_trap_clocks")
    public static void sixTrapClocksWarnAndRestoreWithoutReplayingContact(GameTestHelper h){
        for(var profile:DungeonTrapProfile.values()){
            var room=new DungeonRoomController();var clock=room.hazard(profile.id+"_qa",false);clock.trigger(100);
            for(int t=1;t<profile.warning;t++){clock.tickActive(100+t);h.assertTrue(!clock.consumeContact(),"No early damage frame: "+profile);}
            clock.tickActive(100+profile.warning);h.assertTrue(clock.phase()==DungeonMechanism.Phase.ACTIVE&&clock.consumeContact()&&!clock.consumeContact(),"One authoritative contact after tell: "+profile);
            var restored=new DungeonRoomController();restored.load(room.save());var copy=restored.hazard(profile.id+"_qa",false);
            h.assertTrue(!copy.consumeContact(),"NBT reload never repeats consumed contact");copy.pause(1000);copy.tickActive(1002);
            h.assertTrue(copy.phase()!=DungeonMechanism.Phase.WARNING,"Unloaded gap does not restart the tell");
        }h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod2_trap_runtime",timeoutTicks=240)
    public static void actualCrusherCoreAllowsEscapeThenDamagesOnlyAtContact(GameTestHelper h){
        var level=h.getLevel();var trapPos=h.absolutePos(new BlockPos(6,1,6));var corePos=h.absolutePos(new BlockPos(3,1,6));var id=UUID.randomUUID();
        var forced=new HashSet<net.minecraft.world.level.ChunkPos>();
        for(var pos:List.of(corePos,trapPos)){
            var chunk=new net.minecraft.world.level.ChunkPos(pos);
            if(!level.getForcedChunks().contains(chunk.toLong())){level.setChunkForced(chunk.x,chunk.z,true);forced.add(chunk);}
        }
        var fixture=new FakePlayer[1];
        var clock=DungeonStateStore.get(level).room(id,"qa").hazard("crusher_qa",false);
        h.startSequence().thenWaitUntil(()->{
            for(var pos:List.of(corePos,trapPos)){
                var chunk=new net.minecraft.world.level.ChunkPos(pos);var loaded=level.getChunkSource().getChunkNow(chunk.x,chunk.z);
                h.assertTrue(loaded!=null&&loaded.getFullStatus().isOrAfter(net.minecraft.server.level.FullChunkStatus.ENTITY_TICKING)
                    &&level.areEntitiesLoaded(chunk.toLong()),"Actual hammer waits for ticking blocks and entity storage");
            }
        }).thenExecute(()->{
            for(int y=1;y<=6;y++)for(int x=0;x<=2;x++)level.setBlockAndUpdate(trapPos.offset(x,y,0),Blocks.AIR.defaultBlockState());
            var trap=marker(h,trapPos,DungeonContent.CRUSHER.get(),"crusher_qa");var core=marker(h,corePos,DungeonContent.CORE.get(),"core");
            trap.configure(id,"qa","crusher_qa",corePos,-1,List.of());core.configure(id,"qa","core",corePos,-1,List.of(trapPos));core.configureRoom(0,false,trapPos,trapPos.above(3));
            fixture[0]=player(h,trapPos.above());
        }).thenWaitUntil(()->h.assertTrue(clock.phase()==DungeonMechanism.Phase.WARNING,"Actual core starts its visible warning"))
        .thenExecute(()->{h.assertTrue(fixture[0].getHealth()==200,"Visible warning has no damage");fixture[0].setPos(net.minecraft.world.phys.Vec3.atBottomCenterOf(trapPos.offset(2,1,0)));})
        .thenWaitUntil(()->h.assertTrue(clock.phase()==DungeonMechanism.Phase.RECOVERY,"First real contact completes before returning"))
        .thenExecute(()->{h.assertTrue(fixture[0].getHealth()==200,"Walking out of actual hammer column avoids first strike");fixture[0].setPos(net.minecraft.world.phys.Vec3.atBottomCenterOf(trapPos.above()));})
        .thenWaitUntil(()->h.assertTrue(fixture[0].getHealth()<200,"Standing beneath later hammer takes real damage"))
        .thenExecute(()->{
            try{h.assertTrue(fixture[0].getHealth()>=192,"Hammer damage remains bounded, health="+fixture[0].getHealth());
                h.assertTrue(level.getBlockState(trapPos).is(DungeonContent.CRUSHER.get()),"Hammer never edits its floor/terrain");h.succeed();
            }finally{remove(h,fixture[0]);level.removeBlock(corePos,false);level.removeBlock(trapPos,false);for(var chunk:forced)level.setChunkForced(chunk.x,chunk.z,false);}
        });
    }
    @GameTest(template="bow_ritual_test",batch="cod2_trap_contacts")
    public static void mineUsesDamageWithoutExplosionAndArrowRainRespectsSolidCover(GameTestHelper h){
        var level=h.getLevel();var pos=h.absolutePos(new BlockPos(6,1,6));var mine=marker(h,pos,DungeonContent.MINE.get(),"mine_qa");var p=player(h,pos.above());
        try{
            var protectedPos=pos.offset(2,1,0);level.setBlockAndUpdate(protectedPos,DungeonContent.MASONRY.get().defaultBlockState());
            DungeonTrapEffects.contact(level,mine,DungeonTrapProfile.MINE);
            h.assertTrue(p.getHealth()==194&&level.getBlockState(protectedPos).is(DungeonContent.MASONRY.get()),"Mine causes bounded server damage without a terrain explosion");
            p.invulnerableTime=0;p.setHealth(200);var rain=marker(h,pos,DungeonContent.ARROW_RAIN.get(),"arrow_rain_qa");
            for(int y=2;y<=13;y++)level.setBlockAndUpdate(pos.above(y),Blocks.AIR.defaultBlockState());var roof=pos.above(4);level.setBlockAndUpdate(roof,Blocks.STONE.defaultBlockState());
            DungeonTrapEffects.contact(level,rain,DungeonTrapProfile.ARROW_RAIN);h.assertTrue(p.getHealth()==200,"Solid cover blocks logical arrow rain");level.setBlockAndUpdate(roof,Blocks.AIR.defaultBlockState());
            DungeonTrapEffects.contact(level,rain,DungeonTrapProfile.ARROW_RAIN);h.assertTrue(p.getHealth()==198,"Uncovered target receives one logical contact without hundreds of arrow entities");h.succeed();
        }finally{remove(h,p);}
    }
    @GameTest(template="bow_ritual_test",batch="cod2_trap_contacts")
    public static void environmentalForcesAreFiniteAndPreserveFastPlayerMovement(GameTestHelper h){
        var level=h.getLevel();var pos=h.absolutePos(new BlockPos(6,1,6));var be=marker(h,pos,DungeonContent.CONVEYOR.get(),"conveyor_qa");var p=player(h,pos.above());
        try{
            for(int n=0;n<30;n++)DungeonTrapEffects.continuous(level,be,DungeonTrapProfile.CONVEYOR);
            h.assertTrue(p.getDeltaMovement().z>0&&p.getDeltaMovement().horizontalDistance()<=.30001,"Conveyor accelerates along facing with a strict horizontal limit");
            p.setDeltaMovement(0,.2,1);DungeonTrapEffects.continuous(level,be,DungeonTrapProfile.WIND_FIELD);
            h.assertTrue(p.getDeltaMovement().z==1&&p.getDeltaMovement().y==.2,"Fast movement and vertical physics are preserved");
            h.assertTrue(!p.noPhysics&&!p.isPassenger(),"No collision/input/riding lock is introduced");h.succeed();
        }finally{remove(h,p);}
    }
    private DungeonTrapGameTests(){}
}
