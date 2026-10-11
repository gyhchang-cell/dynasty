package com.dynasty.dungeon;

import java.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty_cod2")
@PrefixGameTestTemplate(false)
public final class DungeonCloudGameTests {
    @GameTest(template="bow_ritual_test",batch="cod2_cloud")
    public static void actualCloudCollisionTracksClockAndSafeRestore(GameTestHelper h){
        var level=h.getLevel();var pos=h.absolutePos(new BlockPos(3,3,3));
        level.setBlockAndUpdate(pos,DungeonContent.CLOUD.get().defaultBlockState());
        var be=(DungeonMechanismBlockEntity)level.getBlockEntity(pos);be.configure(UUID.randomUUID(),"cloud_qa","cloud",pos,-1,List.of());
        var room=new DungeonRoomController();var clock=room.hazard("cloud",true);clock.trigger(100);
        for(int time=102;time<120;time+=2){clock.tickActive(time);be.syncVisual(room);h.assertTrue(!level.getBlockState(pos).getCollisionShape(level,pos).isEmpty(),"Warning remains load bearing");}
        clock.tickActive(120);be.syncVisual(room);h.assertTrue(level.getBlockState(pos).getCollisionShape(level,pos).isEmpty(),"Active cloud truly loses collision");
        var restored=new DungeonRoomController();restored.load(room.save());clock=restored.hazard("cloud",true);
        clock.tickActive(10000);h.assertTrue(clock.phase()==DungeonMechanism.Phase.ACTIVE,"Reload does not fast forward an unloaded floor");
        for(int t=10002;t<=10040;t+=2)clock.tickActive(t);be.syncVisual(restored);
        h.assertTrue(clock.phase()==DungeonMechanism.Phase.RECOVERY&&level.getBlockState(pos).getCollisionShape(level,pos).isEmpty(),"Recovery is still noncolliding");
        var occupant=EntityType.COW.create(level);occupant.setNoAi(true);occupant.setNoGravity(true);occupant.setPos(Vec3.atBottomCenterOf(pos));level.addFreshEntity(occupant);
        for(int t=10042;t<=10076;t+=2)clock.tickActive(t);be.syncVisual(restored);
        h.assertTrue(clock.phase()==DungeonMechanism.Phase.IDLE&&level.getBlockState(pos).getCollisionShape(level,pos).isEmpty(),"Occupied cell cannot materialize into a mob");
        occupant.setPos(occupant.position().add(4,0,0));be.syncVisual(restored);
        h.assertTrue(!level.getBlockState(pos).getCollisionShape(level,pos).isEmpty(),"Clear cell returns to real support");occupant.discard();h.succeed();
    }
    private DungeonCloudGameTests(){}
}
