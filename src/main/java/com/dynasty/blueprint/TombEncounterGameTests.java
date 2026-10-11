package com.dynasty.blueprint;

import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

@GameTestHolder("dynasty_army")
@PrefixGameTestTemplate(false)
public final class TombEncounterGameTests {
    private static final net.minecraft.server.level.TicketType<UUID> ROUTE_TICKET=net.minecraft.server.level.TicketType.create("dynasty_tomb_route_qa",UUID::compareTo);
    private record RouteTicket(net.minecraft.world.level.ChunkPos chunk,UUID token){}
    private static final java.util.Map<ServerLevel,java.util.List<RouteTicket>> ROUTE_TICKETS=new java.util.HashMap<>();
    @net.minecraft.gametest.framework.AfterBatch(batch="tomb_encounter_world")
    public static void releaseRouteTicks(ServerLevel level){
        var tickets=ROUTE_TICKETS.remove(level);if(tickets!=null)for(var ticket:tickets)level.getChunkSource().removeRegionTicket(ROUTE_TICKET,ticket.chunk(),2,ticket.token(),true);
    }
    private record Scene(TemplateMob source, TemplateMob child, TemplateMob paper,
            TemplateMob outsider, net.minecraft.world.entity.animal.Cow victim) {}

    private static Scene scene(GameTestHelper h) {
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=1;y<=8;y++)
            h.setBlock(x,y,z,y==1||y==8||x==0||x==15||z==0||z==15?Blocks.STONE:y<=3?Blocks.WATER:Blocks.AIR);
        String site="tomb@"+UUID.randomUUID();
        var source=h.spawn(BlueprintEntities.SHASHUI_FUNIGUI.get(),new BlockPos(6,3,7));
        var child=h.spawn(BlueprintEntities.FUHUN_BAIBU_TONGZI.get(),new BlockPos(5,3,9));
        var paper=h.spawn(BlueprintEntities.ZHIREN_JIANKE.get(),new BlockPos(9,3,9));
        var outsider=h.spawn(BlueprintEntities.FUHUN_BAIBU_TONGZI.get(),new BlockPos(5,3,12));
        for(var member:java.util.List.of(source,child,paper,outsider)){member.setNoAi(true);member.setNoGravity(true);member.bindEncounter(site+(member==outsider?"-other":""));}
        var victim=h.spawn(EntityType.COW,new BlockPos(7,3,7));victim.setNoAi(true);victim.setNoGravity(true);
        return new Scene(source,child,paper,outsider,victim);
    }

    @GameTest(template="bow_ritual_test",timeoutTicks=75,batch="tomb_encounter")
    public static void actualControlSharesOneVictimOnlyWithinTheAuthoredEncounter(GameTestHelper h) {
        var s=scene(h);
        h.runAfterDelay(3,()->h.assertTrue(s.source.startSkill(ArmySkills.DROWNER_POOL,s.victim),"Deep-water control starts"));
        h.runAfterDelay(23,()->h.assertTrue(s.child.tombSignal.target(s.child)==null,"Tell cannot issue a successful-control signal"));
        h.runAfterDelay(35,()->{
            h.assertTrue(s.victim.hasEffect(BlueprintEntities.DROWNING_BIND.get()),"Real pool applies the actual water bind");
            h.assertTrue(s.child.tombSignal.target(s.child)==s.victim&&s.paper.tombSignal.target(s.paper)==s.victim,"Both loaded allies receive the exact controlled UUID");
            h.assertTrue(s.child.getTarget()==s.victim&&s.paper.getTarget()==s.victim,"Server AI consumes the handoff");
            h.assertTrue(s.outsider.tombSignal.target(s.outsider)==null&&s.outsider.getTarget()==null,"Other tombs cannot join");
            s.victim.setPos(s.victim.getX()+6,s.victim.getY(),s.victim.getZ());
        });
        h.runAfterDelay(49,()->{h.assertTrue(s.child.tombSignal.target(s.child)==null&&s.paper.tombSignal.target(s.paper)==null,"Swimming out revokes both flanks");h.succeed();});
    }

    @GameTest(template="bow_ritual_test",timeoutTicks=65,batch="tomb_encounter")
    public static void supportCannotReplaceTheVictimOfAnAttackAlreadyInFlight(GameTestHelper h) {
        var s=scene(h);var second=h.spawn(EntityType.COW,new BlockPos(5,3,10));second.setNoAi(true);second.setNoGravity(true);
        h.runAfterDelay(3,()->s.source.startSkill(ArmySkills.DROWNER_POOL,s.victim));
        h.runAfterDelay(26,()->h.assertTrue(s.child.startSkill(ArmySkills.CHILD_LAUGH,second),"An independent attack targets the second victim"));
        h.runAfterDelay(35,()->{
            h.assertTrue(s.child.tombSignal.target(s.child)==s.victim,"Pool hands off its selected victim, even with another enemy nearby");
            h.assertTrue(s.child.attack().target().equals(second.getUUID()),"Already-started action retains its original authoritative target UUID");h.succeed();
        });
    }

    @GameTest(template="bow_ritual_test",timeoutTicks=65,batch="tomb_encounter")
    public static void deathAndOcclusionImmediatelyRevokeTheTacticalSignal(GameTestHelper h) {
        var s=scene(h);h.runAfterDelay(3,()->s.source.startSkill(ArmySkills.DROWNER_POOL,s.victim));
        h.runAfterDelay(35,()->{
            h.assertTrue(s.child.tombSignal.target(s.child)==s.victim,"Signal first exists");
            for(int y=2;y<=6;y++)for(int z=4;z<=12;z++)h.setBlock(6,y,z,Blocks.STONE);
            h.assertTrue(s.child.tombSignal.target(s.child)==null,"Solid cover breaks support without changing player input");
            s.source.setHealth(0);
            h.assertTrue(s.paper.tombSignal.target(s.paper)==null,"Dead controller cannot keep allies coordinated");h.succeed();
        });
    }

    @GameTest(template="bow_ritual_test",timeoutTicks=120,batch="tomb_encounter")
    public static void nativeEntityReloadKeepsTheOriginalActionAndAbsoluteSignalExpiry(GameTestHelper h) {
        var s=scene(h);TemplateMob[] member={s.child};
        h.runAfterDelay(3,()->s.source.startSkill(ArmySkills.DROWNER_POOL,s.victim));
        h.runAfterDelay(35,()->{
            var tag=new CompoundTag();member[0].save(tag);var uuid=member[0].getUUID();
            member[0].remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);
            member[0]=BlueprintEntities.FUHUN_BAIBU_TONGZI.get().create(h.getLevel());member[0].load(tag);h.getLevel().addFreshEntity(member[0]);
            h.assertTrue(member[0].getUUID().equals(uuid)&&member[0].tombSignal.target(member[0])==s.victim,"Native save/load retains source, victim, site and action epoch");
            s.source.cancelAction();
            h.assertTrue(member[0].tombSignal.target(member[0])==null,"A cancelled action cannot be resumed by saved coordination");
        });
        h.runAfterDelay(102,()->{h.assertTrue(member[0].tombSignal.target(member[0])==null,"Saved expiry cannot become a permanent target signal");h.succeed();});
    }

    @GameTest(template="bow_ritual_test",timeoutTicks=75,batch="tomb_encounter_world")
    public static void rearApproachFindsTheDryRaisedRimThroughActualStairs(GameTestHelper h) {
        var chunks=new java.util.HashSet<net.minecraft.world.level.ChunkPos>();
        for(int x:new int[]{0,15})for(int z:new int[]{0,15})chunks.add(new net.minecraft.world.level.ChunkPos(h.absolutePos(new BlockPos(x,2,z))));
        for(var chunk:chunks){var ticket=new RouteTicket(chunk,UUID.randomUUID());h.getLevel().getChunkSource().addRegionTicket(ROUTE_TICKET,chunk,2,ticket.token(),true);ROUTE_TICKETS.computeIfAbsent(h.getLevel(),k->new java.util.ArrayList<>()).add(ticket);}
        for(int x=1;x<14;x++)for(int z=1;z<14;z++)for(int y=1;y<=6;y++)h.setBlock(x,y,z,y==1?Blocks.STONE:Blocks.AIR);
        for(int x=3;x<=9;x++)for(int z=3;z<=9;z++)for(int y=2;y<=3;y++)
            h.setBlock(x,y,z,x>=4&&x<=8&&z>=4&&z<=8?Blocks.WATER:Blocks.STONE);
        for(int x=5;x<=7;x++){
            h.setBlock(x,2,10,Blocks.STONE_BRICK_STAIRS.defaultBlockState().setValue(net.minecraft.world.level.block.StairBlock.FACING,net.minecraft.core.Direction.NORTH));
            h.setBlock(x,3,9,Blocks.STONE_BRICK_STAIRS.defaultBlockState().setValue(net.minecraft.world.level.block.StairBlock.FACING,net.minecraft.core.Direction.NORTH));
        }
        var child=h.spawn(BlueprintEntities.FUHUN_BAIBU_TONGZI.get(),new BlockPos(6,2,11));child.setNoAi(false);
        var victim=h.spawn(EntityType.COW,new BlockPos(6,3,6));victim.setNoAi(true);victim.setNoGravity(true);victim.setYRot(180);
        h.onEachTick(()->{
            if(child.tickCount<2||!h.getLevel().isPositionEntityTicking(child.blockPosition())||!child.onGround())return;
            var path=TombEncounterCoordinator.rearRoute(child,victim);
            h.assertTrue(path!=null&&path.canReach()&&path.getEndNode()!=null,"An actual dry rear path exists across both native stair levels: ground="+child.onGround()+" child="+child.position()+" target="+victim.position()+" look="+victim.getLookAngle());
            var end=path.getEndNode();var feet=new BlockPos(end.x,end.y,end.z);
            h.assertTrue(end.y>victim.getBlockY()&&h.getLevel().getFluidState(feet).isEmpty(),"Rear destination uses rim floor height instead of the bound player's submerged feet");
            h.succeed();
        });
    }

    @GameTest(template="bow_ritual_test",timeoutTicks=30,batch="tomb_encounter_world")
    public static void generatedBasinHasOneRealSpawnAndDoesNotChangeLegacyTombLayouts(GameTestHelper h) {
        var level=h.getLevel();var origin=new BlockPos(12288,12,12288);
        var piece=new com.dynasty.structure.TombPiece(com.dynasty.structure.DynastyStructures.TOMB_PIECE.get(),0,origin);
        var box=piece.getBoundingBox();
        for(int x=box.minX()>>4;x<=box.maxX()>>4;x++)for(int z=box.minZ()>>4;z<=box.maxZ()>>4;z++){
            var chunk=level.getChunk(x,z);piece.postProcess(level,level.structureManager(),level.getChunkSource().getGenerator(),
                net.minecraft.util.RandomSource.create(7),new net.minecraft.world.level.levelgen.structure.BoundingBox(x*16,box.minY(),z*16,x*16+15,box.maxY(),z*16+15),chunk.getPos(),origin);
        }
        var at=piece.drownerPositions().get(0);String key="tomb@"+UUID.randomUUID()+":tomb_drowner";
        h.assertTrue(DrownerBehavior.deepWater(level,at),"Authored five-by-five basin has two real water layers");
        h.assertTrue(BlueprintSpawns.spawnTombDrowner(level,key,piece.drownerPositions(),at.offset(7,0,0)),"Actual structure method spawns one supported actor");
        h.assertTrue(!BlueprintSpawns.spawnTombDrowner(level,key,piece.drownerPositions(),at.offset(7,0,0)),"Repeated entrants cannot duplicate it");
        var context=net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext.fromLevel(level);
        var saved=piece.createTag(context);h.assertTrue(saved.getInt("DynastyTombLayout")==3,"New tomb layout persists version three");
        for(int version:new int[]{1,2}){
            var legacy=saved.copy();legacy.putInt("DynastyTombLayout",version);
            var old=new com.dynasty.structure.TombPiece(com.dynasty.structure.DynastyStructures.TOMB_PIECE.get(),legacy);
            h.assertTrue(old.drownerPositions().isEmpty()&&old.createTag(context).getInt("DynastyTombLayout")==version,"Legacy layout "+version+" never gains the new basin");
        }
        h.succeed();
    }
}
