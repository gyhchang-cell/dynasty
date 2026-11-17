package com.dynasty.dungeon;

import com.dynasty.blueprint.BlueprintSpawnState;
import com.dynasty.blueprint.elite.EliteContent;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.Level;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;
import java.util.UUID;

/** Native regressions prepared for a later authorized Java run. */
@GameTestHolder("dynasty_cod2")
@PrefixGameTestTemplate(false)
public final class ChenshaGarrisonGameTests {
    @GameTest(template="bow_ritual_test",batch="cod2_elite_garrison")
    public static void existingEliteBodiesFitTheirAuthoredLandings(GameTestHelper h){
        checkBody(h,ChenshaGarrisons.jinwuOffset(),EliteContent.JINWU.get());
        checkBody(h,ChenshaGarrisons.hammerOffset(),EliteContent.HAMMER.get());
        h.succeed();
    }
    private static void checkBody(GameTestHelper h,BlockPos feet,EntityType<?> type){
        var box=type.getDimensions().makeBoundingBox(feet.getX()+.5,feet.getY(),feet.getZ()+.5);
        for(int x=(int)Math.floor(box.minX);x<Math.ceil(box.maxX);x++)
            for(int z=(int)Math.floor(box.minZ);z<Math.ceil(box.maxZ);z++){
                h.assertTrue(ChenshaPiece.cell(x,feet.getY()-1,z).is(DungeonContent.MASONRY.get()),
                    "The full elite footprint sits on protected dry masonry, not chains or a mercury moat");
                for(int y=feet.getY();y<Math.ceil(box.maxY);y++)h.assertTrue(ChenshaPiece.cell(x,y,z).isAir(),
                    "Existing elite body must fit without shrinking its registered dimensions");
            }
    }
    @GameTest(template="bow_ritual_test",batch="cod2_elite_garrison")
    public static void singletonMembershipSurvivesReloadAndCannotRespawn(GameTestHelper h){
        h.assertTrue(ChenshaGarrisons.maySpawn(false,0,0,0,100),"Fresh marker is eligible");
        h.assertTrue(!ChenshaGarrisons.maySpawn(false,0,0,101,100),"Deferred marker cannot skip its schedule");
        var state=new BlueprintSpawnState();var id=UUID.randomUUID();String key=ChenshaGarrisons.key(id,false);
        var marker=new BlueprintSpawnState.Marker(key,ChenshaGarrisons.jinwuOffset());
        marker.produced=1;marker.members.add(UUID.randomUUID());state.markers.put(key,marker);
        var restored=BlueprintSpawnState.load(state.save(new CompoundTag())).markers.get(key);
        h.assertTrue(restored.members.equals(marker.members),"Unloaded member UUID survives disk-shaped serialization");
        h.assertTrue(!ChenshaGarrisons.maySpawn(restored.cleared,restored.produced,restored.members.size(),0,100),
            "An unloaded actor without a live world lookup still occupies its only slot");
        restored.members.clear();
        h.assertTrue(!ChenshaGarrisons.maySpawn(false,restored.produced,0,0,100),"Produced empty legacy marker never duplicates an elite");
        h.assertTrue(!ChenshaGarrisons.maySpawn(true,0,0,0,100),"Cleared markers never respawn");
        h.assertTrue(!key.equals(ChenshaGarrisons.key(id,true))&&!key.equals(ChenshaGarrisons.key(UUID.randomUUID(),false)),
            "Elite roles and separate dungeons have separate membership keys");
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod2_elite_garrison")
    public static void crossDimensionDeathReleasesTheOverworldOwner(GameTestHelper h){
        var owner=h.getLevel().getServer().overworld();var destination=owner.getServer().getLevel(Level.NETHER);
        h.assertTrue(destination!=null,"Cross-dimension fixture requires the normal Nether dimension");
        var actor=EliteContent.JINWU.get().create(destination);h.assertTrue(actor!=null,"Existing Jinwu type is registered");
        var instance=UUID.randomUUID();String key=ChenshaGarrisons.key(instance,false);
        var data=BlueprintSpawnState.get(owner);var marker=new BlueprintSpawnState.Marker(key,BlockPos.ZERO);
        marker.produced=1;marker.members.add(actor.getUUID());data.markers.put(key,marker);
        try{
            ChenshaGarrisons.bindOwner(actor,instance,false);
            var saved=actor.saveWithoutId(new CompoundTag());
            h.assertTrue(saved.getCompound("ForgeData").getCompound("ChenshaGarrison").hasUUID("Instance"),
                "Portal/reload ownership is stored in the entity's persistent Forge data");
            ChenshaGarrisons.release(actor);
            h.assertTrue(marker.cleared&&marker.members.isEmpty(),"Destination death clears the owning Overworld singleton");
            long next=marker.nextSpawn;ChenshaGarrisons.release(actor);
            h.assertTrue(marker.nextSpawn==next,"Death and terminal removal callbacks are idempotent");
        }finally{data.markers.remove(key);data.setDirty();}
        h.succeed();
    }
}
