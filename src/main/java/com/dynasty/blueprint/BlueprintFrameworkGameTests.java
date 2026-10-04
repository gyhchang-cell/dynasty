package com.dynasty.blueprint;

import com.dynasty.blueprint.combat.*;
import io.netty.buffer.Unpooled;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;

@GameTestHolder("dynasty")
@PrefixGameTestTemplate(false)
public final class BlueprintFrameworkGameTests {
    @GameTest(template="bow_ritual_test")
    public static void cancellingFromDamageCallbackCannotCrashOrContinueOldAction(GameTestHelper h) {
        var clock=new TimedAttack();var hits=new AtomicInteger();
        h.assertTrue(clock.tryStart(TemplateSkills.byId(1),100,Vec3.ZERO,new Vec3(0,0,1),UUID.randomUUID()),"Start");
        clock.advance(112,f->{hits.incrementAndGet();clock.stun(112,10);});
        clock.advance(122,f->hits.incrementAndGet());
        h.assertTrue(hits.get()==1 && clock.current()==null,"Callback interruption aborts safely");
        h.assertTrue(!clock.ready(1,122),"Interruption retains cooldown");h.succeed();
    }
    @GameTest(template="bow_ritual_test")
    public static void missedFramesAndCheckpointCannotRepeatDamage(GameTestHelper h) {
        var clock=new TimedAttack();var hits=new AtomicInteger();
        clock.tryStart(TemplateSkills.byId(1),100,Vec3.ZERO,new Vec3(0,0,1),UUID.randomUUID());
        clock.advance(112,f->hits.incrementAndGet());clock.advance(112,f->hits.incrementAndGet());
        var resumed=new TimedAttack();resumed.load(clock.save(),TemplateSkills::byId,112);
        resumed.advance(112,f->hits.incrementAndGet());resumed.advance(122,f->hits.incrementAndGet());
        h.assertTrue(hits.get()==2,"Each authored contact occurs once across reload");
        var late=new TimedAttack();late.load(clock.save(),TemplateSkills::byId,123);
        late.advance(123,f->hits.incrementAndGet());h.assertTrue(hits.get()==2,"No catch-up burst");h.succeed();
    }
    @GameTest(template="bow_ritual_test")
    public static void geometryBoundedQueriesMatchNarrowPhase(GameTestHelper h) {
        var origin=Vec3.atCenterOf(h.absolutePos(new BlockPos(4,3,4)));
        var forward=new Vec3(0,0,1);
        var near=h.spawn(EntityType.COW,new BlockPos(6,3,8));near.setNoAi(true);near.setNoGravity(true);
        var far=h.spawn(EntityType.COW,new BlockPos(19,3,13));far.setNoAi(true);far.setNoGravity(true);
        var cone=CombatGeometry.query(h.getLevel(),origin,forward,CombatGeometry.Shape.CONE,10,1,120,3,e->true);
        h.assertTrue(cone.contains(near)&&!cone.contains(far),"Cone radial range bounds match filter");
        for(var shape:CombatGeometry.Shape.values()) {
            var found=CombatGeometry.query(h.getLevel(),origin,forward,shape,10,3,120,3,e->true);
            for(var candidate:java.util.List.of(near,far))
                h.assertTrue(found.contains(candidate)==CombatGeometry.contains(origin,forward,shape,10,3,120,3,candidate.getBoundingBox()),"Broad/narrow phase agree: "+shape);
        }
        h.assertTrue(CombatGeometry.query(h.getLevel(),origin,forward,CombatGeometry.Shape.CONE,100000,1,90,2,e->true).isEmpty(),"Oversized searches rejected");
        h.assertTrue(CombatGeometry.query(h.getLevel(),origin,forward,CombatGeometry.Shape.SECTOR,4,1,Double.NaN,2,e->true).isEmpty(),"Non-finite angle rejected");h.succeed();
    }
    @GameTest(template="bow_ritual_test")
    public static void visualPacketRoundTripPreservesIdentityAndServerClock(GameTestHelper h) {
        var data=new BlueprintVisualEvent(new ResourceLocation("minecraft","overworld"),17,UUID.randomUUID(),18,
            1234,5678,"sword_combo",12,36,new Vec3(2,3,4),new Vec3(0,0,1),3.2,110,false);
        var buf=new FriendlyByteBuf(Unpooled.buffer());
        try {BlueprintVisualEvent.encode(data,buf);h.assertTrue(BlueprintVisualEvent.decode(buf).equals(data),"Identity/clock/direction/seed intact");}
        finally {buf.release();}h.succeed();
    }
    @GameTest(template="bow_ritual_test")
    public static void encounterMarkersPreserveUnloadedMembersAndReleaseDiscardedOnes(GameTestHelper h) {
        var state=BlueprintSpawnState.get(h.getLevel());
        var mob=h.spawn(BlueprintEntities.ZUWU_DAOSHOU.get(),new BlockPos(5,2,5));mob.setNoAi(true);
        String key="test@"+mob.getUUID();var marker=new BlueprintSpawnState.Marker(key,mob.blockPosition());
        marker.produced=4;marker.members.add(mob.getUUID());marker.members.add(UUID.randomUUID());state.markers.put(key,marker);
        var copy=BlueprintSpawnState.load(state.save(new CompoundTag()));
        h.assertTrue(copy.markers.get(key).members.size()==2,"Unloaded UUID must not be treated as dead");
        mob.discard();
        h.assertTrue(marker.members.size()==1&&!marker.members.contains(mob.getUUID()),"Permanent discard frees membership");
        h.assertTrue(marker.nextSpawn>=h.getLevel().getGameTime()+12000,"Cooldown persists after removal");
        var after=BlueprintSpawnState.load(state.save(new CompoundTag())).markers.get(key);
        h.assertTrue(after.produced==4 && after.nextSpawn==marker.nextSpawn,"Count/cooldown survive serialization");
        state.markers.remove(key);state.setDirty();h.succeed();
    }
    @GameTest(template="bow_ritual_test")
    public static void transferredEncounterMemberReleasesOriginalWorldMarker(GameTestHelper h) {
        var owner=h.getLevel().getServer().overworld();
        var destination=h.getLevel().getServer().getLevel(net.minecraft.world.level.Level.NETHER);
        h.assertTrue(destination!=null,"Portal destination available");
        var id=UUID.randomUUID();String key="test@portal@"+id;
        var state=BlueprintSpawnState.get(owner);var marker=new BlueprintSpawnState.Marker(key,BlockPos.ZERO);
        marker.members.add(id);marker.produced=4;state.markers.put(key,marker);
        try {
            BlueprintSpawns.releaseMember(destination,id);
            h.assertTrue(marker.members.isEmpty(),"Death after dimension transfer releases Overworld membership");
            h.assertTrue(marker.nextSpawn>=owner.getGameTime()+12000,"Cooldown uses marker owner's game clock");
        } finally {state.markers.remove(key);state.setDirty();}
        h.succeed();
    }
    @GameTest(template="bow_ritual_test")
    public static void nightAndLowLightIncreaseAttemptWeightsWithoutChangingSquadCaps(GameTestHelper h) {
        var sword=TemplateContentDefinitions.ALL.stream().filter(d->d.id().equals("zuwu_daoshou")).findFirst().orElseThrow();
        var priest=TemplateContentDefinitions.ALL.stream().filter(d->d.id().equals("fufa_jijiu")).findFirst().orElseThrow();
        h.assertTrue(TemplateContentDefinitions.effectiveWeight(sword,true,15)>TemplateContentDefinitions.effectiveWeight(sword,false,15),"Swordsmen modestly favor night");
        h.assertTrue(TemplateContentDefinitions.effectiveWeight(priest,false,7)>TemplateContentDefinitions.effectiveWeight(priest,false,15),"Priests favor dark rooms during day");
        h.assertTrue(TemplateContentDefinitions.effectiveWeight(priest,true,15)>TemplateContentDefinitions.effectiveWeight(priest,false,15),"Priests favor night");
        h.assertTrue(priest.localCap()==1&&sword.localCap()==3,"No extra squad members");h.succeed();
    }
}
