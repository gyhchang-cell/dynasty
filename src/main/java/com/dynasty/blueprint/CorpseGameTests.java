package com.dynasty.blueprint;

import java.util.List;
import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

@GameTestHolder("dynasty_army")
@PrefixGameTestTemplate(false)
public final class CorpseGameTests {
    private static TemplateMob corpse(GameTestHelper h){
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=1;y<=10;y++)
            h.setBlock(x,y,z,y==1||y==10?Blocks.STONE:Blocks.AIR);
        var mob=h.spawn(BlueprintEntities.SHIBIAN_LISHI.get(),new BlockPos(7,2,7));mob.setNoAi(true);return mob;
    }
    private static net.minecraft.world.entity.animal.Cow target(GameTestHelper h,int z){
        var cow=h.spawn(EntityType.COW,new BlockPos(7,2,z));cow.setNoAi(true);cow.setNoGravity(true);
        cow.getAttribute(Attributes.MAX_HEALTH).setBaseValue(200);cow.setHealth(200);return cow;
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=45,batch="corpse")
    public static void acceptedDamageSpillsOnceAndReloadPreservesCooldown(GameTestHelper h){
        var mob=corpse(h);var cow=target(h,10);var area=mob.getBoundingBox().inflate(8);
        h.assertTrue(mob.hurt(mob.damageSources().mobAttack(cow),1),"First real hit is accepted");
        h.assertTrue(h.getLevel().getEntitiesOfClass(CorpseMiasma.class,area).size()==1,"Accepted hit creates one real cloud");
        for(int i=0;i<5;i++){mob.invulnerableTime=0;mob.hurt(mob.damageSources().mobAttack(cow),1);}
        h.assertTrue(h.getLevel().getEntitiesOfClass(CorpseMiasma.class,area).size()==1,"Repeated hits cannot bypass spill cooldown");
        var tag=new CompoundTag();mob.save(tag);mob.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);
        var copy=BlueprintEntities.SHIBIAN_LISHI.get().create(h.getLevel());copy.load(tag);h.getLevel().addFreshEntity(copy);
        copy.invulnerableTime=0;copy.hurt(copy.damageSources().mobAttack(cow),1);
        h.assertTrue(h.getLevel().getEntitiesOfClass(CorpseMiasma.class,area).size()==1,"Entity reload preserves spillCooldown");
        // Nearby corpses share the cap even when individual cooldowns are independent.
        for(int i=0;i<4;i++){
            var other=h.spawn(BlueprintEntities.SHIBIAN_LISHI.get(),new BlockPos(7+i%2,2,7+i/2));other.setNoAi(true);
            other.hurt(other.damageSources().mobAttack(cow),1);
        }
        h.assertTrue(h.getLevel().getEntitiesOfClass(CorpseMiasma.class,area).size()==3,"Nearby burst stops at three lightweight clouds");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=140,batch="corpse")
    public static void miasmaAppliesRealEffectsAndExpiresAcrossUnloadedTime(GameTestHelper h){
        var mob=corpse(h);var cow=target(h,10);var cloud=new CorpseMiasma(BlueprintEntities.CORPSE_MIASMA.get(),h.getLevel());
        cloud.setPos(cow.position());cloud.setOwner(mob);cloud.activate(h.getLevel().getGameTime());h.getLevel().addFreshEntity(cloud);
        var saved=new CompoundTag();
        h.runAfterDelay(8,()->{
            h.assertTrue(cow.hasEffect(MobEffects.POISON)&&cow.hasEffect(MobEffects.MOVEMENT_SLOWDOWN),"Standing in patch applies real poison and slow");
            cloud.save(saved);cloud.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);
        });
        h.runAfterDelay(90,()->{
            var loaded=new CorpseMiasma(BlueprintEntities.CORPSE_MIASMA.get(),h.getLevel());loaded.load(saved);h.getLevel().addFreshEntity(loaded);
            h.runAfterDelay(2,()->{
                h.assertTrue(loaded.isRemoved(),"Unloaded time counts against four-second cloud lifespan");
                h.assertTrue(!cow.hasEffect(MobEffects.POISON)&&!cow.hasEffect(MobEffects.MOVEMENT_SLOWDOWN),"Effects expire after exiting; no permanent attribute change");h.succeed();
            });
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=100,batch="corpse")
    public static void continuouslyLoadedMiasmaLivesExactlyFourSeconds(GameTestHelper h){
        var mob=corpse(h);var cloud=new CorpseMiasma(BlueprintEntities.CORPSE_MIASMA.get(),h.getLevel());
        cloud.setPos(mob.position());cloud.setOwner(mob);cloud.activate(h.getLevel().getGameTime());h.getLevel().addFreshEntity(cloud);
        h.runAfterDelay(75,()->h.assertTrue(!cloud.isRemoved(),"Patch remains for its authored lifetime"));
        h.runAfterDelay(82,()->{h.assertTrue(cloud.isRemoved(),"Loaded patch cleans itself up at80 ticks");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=55,batch="corpse")
    public static void groundSmashHasWarningAndSingleContact(GameTestHelper h){
        var mob=corpse(h);var cow=target(h,9);var behind=target(h,5);
        h.assertTrue(mob.startSkill(ArmySkills.CORPSE_SMASH,cow),"Real server skill starts");
        h.runAfterDelay(18,()->h.assertTrue(cow.getHealth()==200,"Twenty-tick warning does no early damage"));
        h.runAfterDelay(25,()->{
            h.assertTrue(cow.getHealth()==189.5F,"One authored contact deals base damage times1.5");
            h.assertTrue(behind.getHealth()==200,"Front hammer shape does not hit behind");
        });
        h.runAfterDelay(49,()->{h.assertTrue(cow.getHealth()==189.5F&&mob.skillId()==0,"No repeated contacts or stale action");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=650,batch="corpse_world")
    public static void realTombEntrySpawnsPersistentCorpsesOnlyOnAuthoredFloor(GameTestHelper h){
        var level=h.getLevel();var id=new net.minecraft.resources.ResourceLocation("dynasty","imperial_tomb");
        var structure=level.registryAccess().registryOrThrow(net.minecraft.core.registries.Registries.STRUCTURE).get(id);
        var origin=new BlockPos(2048,32,2048);var chunk=new net.minecraft.world.level.ChunkPos(origin);
        var piece=new com.dynasty.structure.TombPiece(com.dynasty.structure.DynastyStructures.TOMB_PIECE.get(),0,origin);
        var box=piece.getBoundingBox();var start=new net.minecraft.world.level.levelgen.structure.StructureStart(structure,chunk,0,
            new net.minecraft.world.level.levelgen.structure.pieces.PiecesContainer(List.of(piece)));
        level.getChunk(chunk.x,chunk.z).setStartForStructure(structure,start);
        for(int x=box.minX()>>4;x<=box.maxX()>>4;x++)for(int z=box.minZ()>>4;z<=box.maxZ()>>4;z++){
            var part=level.getChunk(x,z);part.addReferenceForStructure(structure,chunk.toLong());
            piece.postProcess(level,level.structureManager(),level.getChunkSource().getGenerator(),net.minecraft.util.RandomSource.create(4),
                new net.minecraft.world.level.levelgen.structure.BoundingBox(x*16,box.minY(),z*16,x*16+15,box.maxY(),z*16+15),part.getPos(),origin);
        }
        for(var paperFloor:piece.paperSwordsmanPositions())h.assertTrue(com.dynasty.entity.DynastySpawnPlacement.hasStandingSpace(level,paperFloor,
            BlueprintEntities.ZHIREN_JIANKE.get().getDimensions().makeBoundingBox(paperFloor.getX()+.5,paperFloor.getY(),paperFloor.getZ()+.5)),"Paper courtyard marker has actual generated standing space");
        var childFloor=piece.shroudChildPosition();
        h.assertTrue(com.dynasty.entity.DynastySpawnPlacement.hasStandingSpace(level,childFloor,
            BlueprintEntities.FUHUN_BAIBU_TONGZI.get().getDimensions().makeBoundingBox(childFloor.getX()+.5,childFloor.getY(),childFloor.getZ()+.5)),"Child marker is a real collision-free gallery floor");
        var positions=piece.corpsePositions();var entrant=positions.get(0).offset(0,0,10);
        h.assertTrue(box.isInside(entrant),"Entrant is inside the actual oriented antechamber");
        for(var pos:positions)h.assertTrue(com.dynasty.entity.DynastySpawnPlacement.hasStandingSpace(level,pos,
            BlueprintEntities.SHIBIAN_LISHI.get().getDimensions().makeBoundingBox(pos.getX()+.5,pos.getY(),pos.getZ()+.5)),"Authored giant has collision-free generated floor");
        var player=new net.minecraftforge.common.util.FakePlayer(level,new com.mojang.authlib.GameProfile(UUID.randomUUID(),"corpse-entry")){
            @Override public boolean isCreative(){return true;}
        };
        player.setPos(Vec3.atBottomCenterOf(entrant));level.addNewPlayer(player);
        boolean spawning=level.getGameRules().getBoolean(net.minecraft.world.level.GameRules.RULE_DOMOBSPAWNING);
        level.getGameRules().getRule(net.minecraft.world.level.GameRules.RULE_DOMOBSPAWNING).set(true,level.getServer());
        String key=id+"@"+chunk.toLong()+":corpses";
        h.runAfterDelay(550,()->{
            var data=BlueprintSpawnState.get(level);var marker=data.markers.get(key);
            h.assertTrue(marker!=null&&marker.produced==2&&marker.members.size()==2,"Ordinary structure entry ticks produce exactly two corpses");
            var saved=BlueprintSpawnState.load(data.save(new CompoundTag())).markers.get(key);
            h.assertTrue(saved.members.equals(marker.members),"Restart checkpoint preserves exact member identities");
            var paperKey=id+"@"+chunk.toLong()+":paper_swordsmen";var papers=data.markers.get(paperKey);
            h.assertTrue(papers!=null&&papers.produced==3&&papers.members.size()==3,"Real tomb entry produces three courtyard paper swordsmen within shared tick budget");
            h.assertTrue(BlueprintSpawnState.load(data.save(new CompoundTag())).markers.get(paperKey).members.equals(papers.members),"Paper squad identities survive SavedData restart checkpoint");
            for(var member:List.copyOf(papers.members)){
                var paper=(TemplateMob)level.getEntity(member);h.assertTrue(paper.kind()==TemplateMob.Kind.PAPER&&!paper.isNoAi(),"Authored courtyard owns active paper AI");
                var nbt=new CompoundTag();paper.save(nbt);paper.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);
                h.assertTrue(!BlueprintSpawns.spawnPaperSwordsman(level,paperKey,piece.paperSwordsmanPositions(),entrant),"Unloaded paper member is never replaced");
                var loaded=BlueprintEntities.ZHIREN_JIANKE.get().create(level);loaded.load(nbt);level.addFreshEntity(loaded);loaded.hurt(level.damageSources().genericKill(),10000);
            }
            h.assertTrue(papers.members.isEmpty()&&papers.nextSpawn>=level.getGameTime()+11999,"Final paper death preserves encounter cooldown");
            var childKey=id+"@"+chunk.toLong()+":shroud_child";var childMarker=data.markers.get(childKey);
            h.assertTrue(childMarker!=null&&childMarker.produced==1&&childMarker.members.size()==1,"Same ordinary tomb entry also produces exactly one shroud child");
            var childSaved=BlueprintSpawnState.load(data.save(new CompoundTag())).markers.get(childKey);
            h.assertTrue(childSaved.members.equals(childMarker.members),"Child uses the same persistent encounter ledger");
            var child=(TemplateMob)level.getEntity(childMarker.members.iterator().next());
            h.assertTrue(child.kind()==TemplateMob.Kind.CHILD&&!child.isNoAi(),"Actual child AI is active in authored tomb");
            var childNbt=new CompoundTag();child.save(childNbt);child.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);
            h.assertTrue(!BlueprintSpawns.spawnShroudChild(level,childKey,piece.shroudChildPosition(),entrant),"Unloaded child retains its slot");
            var childCopy=BlueprintEntities.FUHUN_BAIBU_TONGZI.get().create(level);childCopy.load(childNbt);level.addFreshEntity(childCopy);
            childCopy.hurt(level.damageSources().genericKill(),10000);
            h.assertTrue(childMarker.members.isEmpty()&&childMarker.nextSpawn>=level.getGameTime()+11999,"Child death preserves encounter cooldown");
            UUID uuid=marker.members.iterator().next();var mob=(TemplateMob)level.getEntity(uuid);
            h.assertTrue(mob.kind()==TemplateMob.Kind.CORPSE&&!mob.isNoAi(),"Encounter owns the actual active corpse entity");
            var tag=new CompoundTag();mob.save(tag);mob.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);
            h.assertTrue(marker.members.contains(uuid)&&!BlueprintSpawns.spawnTombCorpse(level,key,positions,entrant),"Unloading cannot duplicate encounter slots");
            var copy=BlueprintEntities.SHIBIAN_LISHI.get().create(level);copy.load(tag);level.addFreshEntity(copy);
            for(UUID member:List.copyOf(marker.members))level.getEntity(member).hurt(level.damageSources().genericKill(),10000);
            h.assertTrue(marker.members.isEmpty()&&marker.nextSpawn>=level.getGameTime()+11999,"Deaths release slots and retain ten-minute cooldown");
            h.assertTrue(!BlueprintSpawns.spawnTombCorpse(level,key,positions,entrant),"No immediate respawn");
            player.discard();level.getGameRules().getRule(net.minecraft.world.level.GameRules.RULE_DOMOBSPAWNING).set(spawning,level.getServer());h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=240,batch="corpse")
    public static void recoveredCorpseOilFuelsRealFurnaceWithoutDuplication(GameTestHelper h){
        corpse(h);var pos=new BlockPos(3,2,3);h.setBlock(pos,Blocks.FURNACE);
        var furnace=(net.minecraft.world.level.block.entity.FurnaceBlockEntity)h.getLevel().getBlockEntity(h.absolutePos(pos));
        furnace.setItem(0,new net.minecraft.world.item.ItemStack(net.minecraft.world.item.Items.RAW_IRON));
        furnace.setItem(1,new net.minecraft.world.item.ItemStack(BlueprintSalvage.CONGEALED_CORPSE_OIL.get()));
        h.runAfterDelay(8,()->h.assertTrue(furnace.getItem(1).isEmpty()&&h.getLevel().getBlockState(h.absolutePos(pos))
            .getValue(net.minecraft.world.level.block.FurnaceBlock.LIT),"Furnace consumes real corpse oil and starts burning"));
        h.runAfterDelay(220,()->{
            h.assertTrue(furnace.getItem(0).isEmpty()&&furnace.getItem(2).is(net.minecraft.world.item.Items.IRON_INGOT)
                &&furnace.getItem(2).getCount()==1,"One oil fuel drives one ordinary smelt without duplicating ingredients");h.succeed();
        });
    }

    @GameTest(template="bow_ritual_test",timeoutTicks=115,batch="corpse")
    public static void autonomousPursuitUsesBoundThenReturnsToIdle(GameTestHelper h){
        var mob=corpse(h);var cow=target(h,14);var initial=mob.position();
        mob.setNoAi(false);mob.setTarget(cow);
        boolean[] sprinted={false},bounded={false};
        // Spawn begins airborne: the first path request may fail until gravity lands the mob,
        // then CombatGoal retries on its existing ten-tick budget. Observe the whole pursuit.
        h.onEachTick(()->{
            if(mob.isSprinting())sprinted[0]=true;
            if(mob.isSprinting()&&mob.getDeltaMovement().y>.1)bounded[0]=true;
        });
        h.runAfterDelay(90,()->{
            h.assertTrue(cow.getHealth()<200&&sprinted[0]&&bounded[0]&&mob.position().distanceTo(initial)>3,
                "Real AI must sprint, physically bound, approach and damage target; sprint="+sprinted[0]+" bound="+bounded[0]
                +" at="+mob.position()+" hp="+cow.getHealth()+" path="+mob.getNavigation().getPath());
            h.assertTrue(!mob.noPhysics&&!mob.isNoAi()&&!mob.isNoGravity(),"Real navigation and gravity stay enabled");
            cow.discard();mob.setTarget(null);
            h.runAfterDelay(2,()->{h.assertTrue(!mob.isSprinting(),"Losing target clears run state");h.succeed();});
        });
    }

}
