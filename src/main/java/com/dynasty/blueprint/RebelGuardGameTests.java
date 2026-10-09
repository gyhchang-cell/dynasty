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
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

@GameTestHolder("dynasty_army")
@PrefixGameTestTemplate(false)
public final class RebelGuardGameTests {
    private static TemplateMob guard(GameTestHelper h){
        for(int x=0;x<16;x++)for(int z=0;z<16;z++){
            h.setBlock(x,1,z,Blocks.STONE);
            for(int y=2;y<=10;y++)h.setBlock(x,y,z,y==10?Blocks.STONE:Blocks.AIR);
        }
        var mob=h.spawn(BlueprintEntities.PIJIA_PANJIANG_HUWEI.get(),new BlockPos(7,2,7));
        mob.setNoAi(true);mob.setNoGravity(true);mob.setYRot(0);return mob;
    }
    private static Cow target(GameTestHelper h,int z){
        var cow=h.spawn(EntityType.COW,new BlockPos(7,2,z));cow.setNoAi(true);cow.setNoGravity(true);
        cow.getAttribute(Attributes.MAX_HEALTH).setBaseValue(200);cow.setHealth(200);
        cow.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);return cow;
    }
    private static void hit(TemplateMob guard,Cow source){
        guard.invulnerableTime=0;guard.hurt(guard.damageSources().mobAttack(source),1);guard.setDeltaMovement(net.minecraft.world.phys.Vec3.ZERO);
    }
    private static void health(GameTestHelper h,Cow mob,float expected,String why){h.assertTrue(Math.abs(mob.getHealth()-expected)<.02,why+": "+mob.getHealth());}
    @GameTest(template="bow_ritual_test",timeoutTicks=65,batch="guard")
    public static void doubleAxeClampUsesTwoContactsAndLeavesRearSafe(GameTestHelper h){
        var guard=guard(h);var front=target(h,9);var rear=target(h,5);
        h.assertTrue(guard.startSkill(ArmySkills.AXE_CLAMP,front),"Start authored clamp");
        h.runAfterDelay(14,()->health(h,front,200,"Windup is harmless"));
        h.runAfterDelay(19,()->health(h,front,190.8F,"Right axe has one contact"));
        h.runAfterDelay(27,()->{health(h,front,181.6F,"Left axe is a second authored contact");health(h,rear,200,"Clamp does not strike behind guard");});
        h.runAfterDelay(50,()->{health(h,front,181.6F,"Recovery cannot repeat either contact");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=80,batch="guard")
    public static void counterHasHalfSecondPoiseOneCircleHitAndNoReloadReplay(GameTestHelper h){
        var guard=guard(h);var front=target(h,9);var rear=target(h,5);TemplateMob[] loaded={guard};
        h.assertTrue(!guard.startSkill(ArmySkills.AXE_COUNTER,front),"Uncharged counter cannot be requested");
        hit(guard,front);h.runAfterDelay(11,()->hit(guard,front));h.runAfterDelay(22,()->hit(guard,front));
        h.runAfterDelay(27,()->{
            h.assertTrue(guard.skillId()==ArmySkills.AXE_COUNTER&&guard.getAttributeValue(Attributes.KNOCKBACK_RESISTANCE)>=1,"Third frontal hit starts poise");
            guard.interruptAttack(40);h.assertTrue(guard.skillId()==ArmySkills.AXE_COUNTER,"Counter cannot be interrupted by external stun");
            health(h,front,200,"Gold windup precedes damage");health(h,rear,200,"No warning damage behind");
        });
        h.runAfterDelay(35,()->{
            health(h,front,185.6F,"Circle contact hits front once");health(h,rear,185.6F,"Circle contact covers rear once");
            var saved=new CompoundTag();guard.save(saved);long epoch=guard.skillStartTime();UUID uuid=guard.getUUID();
            guard.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);
            var copy=BlueprintEntities.PIJIA_PANJIANG_HUWEI.get().create(h.getLevel());copy.load(saved);h.getLevel().addFreshEntity(copy);loaded[0]=copy;
            h.assertTrue(copy.getUUID().equals(uuid)&&copy.skillStartTime()==epoch,"Reload keeps identity and action epoch");
        });
        h.runAfterDelay(66,()->{
            health(h,front,185.6F,"Reload cannot replay spent circle frame");health(h,rear,185.6F,"No duplicate rear hit");
            h.assertTrue(loaded[0].getAttributeValue(Attributes.KNOCKBACK_RESISTANCE)<1,"Poise modifier clears after recovery");h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=105,batch="guard")
    public static void rearHitsAndExpiredFrontWindowCannotChargeCounter(GameTestHelper h){
        var guard=guard(h);var front=target(h,9);var rear=target(h,5);
        hit(guard,rear);hit(guard,rear);hit(guard,rear);
        h.assertTrue(guard.skillId()==0,"Rear strikes never charge frontal counter");
        hit(guard,front);hit(guard,front);
        h.runAfterDelay(65,()->{
            hit(guard,front);h.assertTrue(guard.skillId()==0,"Expired two-hit window does not cause immediate counter");
            var saved=new CompoundTag();guard.addAdditionalSaveData(saved);
            h.assertTrue(saved.getCompound("ArmyActionState").getInt("FrontalHits")==1,"Fresh window starts at one");h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=25,batch="guard")
    public static void rejectedCounterFollowupCannotLeavePreviousAnimationRunning(GameTestHelper h){
        var guard=guard(h);var close=target(h,9);var remote=target(h,13);remote.setPos(guard.getX(),guard.getY(),guard.getZ()+50);
        h.assertTrue(guard.startSkill(ArmySkills.AXE_CLAMP,close),"Begin original close-range action");
        hit(guard,remote);hit(guard,remote);hit(guard,remote);
        h.assertTrue(guard.attack().current()==null&&guard.skillId()==0&&guard.skillStartTime()<0,"Out-of-range counter cancels both old clock and tracked animation");
        h.runAfterDelay(14,()->{h.assertTrue(guard.skillId()==0&&guard.visualAnimation().equals("idle"),"Failed follow-up cannot leave a permanent attack clip");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=25,batch="guard")
    public static void recoveredPartsRejectOldGenericAnvilRepair(GameTestHelper h){
        var player=new net.minecraftforge.common.util.FakePlayer(h.getLevel(),new com.mojang.authlib.GameProfile(UUID.randomUUID(),"guard-repair"));
        var tool=new ItemStack(Items.IRON_AXE);tool.setDamageValue(100);tool.setHoverName(net.minecraft.network.chat.Component.literal("Veteran"));
        tool.enchant(net.minecraft.world.item.enchantment.Enchantments.UNBREAKING,2);tool.getOrCreateTag().putString("foreign","preserve");
        var menu=new net.minecraft.world.inventory.AnvilMenu(0,player.getInventory());
        menu.getSlot(0).set(tool);menu.getSlot(1).set(new ItemStack(BlueprintSalvage.KAISHAN_AXE_BLADE.get(),3));menu.createResult();
        h.assertTrue(menu.getSlot(2).getItem().isEmpty(),"Recovered parts no longer perform generic repair");
        h.assertTrue(tool.getDamageValue()==100&&tool.isEnchanted()&&tool.getTag().getString("foreign").equals("preserve")&&menu.getSlot(1).getItem().getCount()==3,"Rejected repair preserves inputs");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=340,batch="guard_world")
    public static void actualDeathsDropRegisteredMaterialsAndReloadCannotDuplicateThem(GameTestHelper h){
        var guard=guard(h);var ghost=h.spawn(BlueprintEntities.YINBING_GUIZU.get(),new BlockPos(10,2,10));ghost.setNoAi(true);
        var area=guard.getBoundingBox().inflate(8);
        // Other batches can leave moving drops near this fixture. Count only the six
        // registered guard/ghost materials, excluding entities already present beforehand.
        var materials=java.util.Set.of(BlueprintSalvage.KAISHAN_AXE_BLADE.get(),BlueprintSalvage.REFINED_WROUGHT_IRON.get(),
            BlueprintSalvage.BROKEN_HEART_MIRROR.get(),BlueprintSalvage.YIN_JADE_SHARD.get(),BlueprintSalvage.NETHER_TATTER.get(),BlueprintSalvage.ANCIENT_COIN_RUST.get());
        var prior=h.getLevel().getEntitiesOfClass(net.minecraft.world.entity.item.ItemEntity.class,area).stream().map(Entity::getUUID).collect(java.util.stream.Collectors.toSet());
        java.util.function.Predicate<net.minecraft.world.entity.item.ItemEntity> ours=e->!prior.contains(e.getUUID())&&materials.contains(e.getItem().getItem());
        guard.hurt(h.getLevel().damageSources().genericKill(),10000);ghost.hurt(h.getLevel().damageSources().genericKill(),10000);
        var dropped=h.getLevel().getEntitiesOfClass(net.minecraft.world.entity.item.ItemEntity.class,area,ours);
        dropped.forEach(e->{e.setNoGravity(true);e.setDeltaMovement(net.minecraft.world.phys.Vec3.ZERO);});
        h.assertTrue(dropped.stream().anyMatch(e->e.getItem().is(BlueprintSalvage.REFINED_WROUGHT_IRON.get())),"Real guard death invokes registered loot table");
        h.assertTrue(dropped.stream().anyMatch(e->e.getItem().is(BlueprintSalvage.YIN_JADE_SHARD.get())),"Real ghost death invokes registered loot table");
        int count=dropped.stream().mapToInt(e->e.getItem().getCount()).sum();
        var saved=new CompoundTag();guard.save(saved);guard.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);
        var copy=BlueprintEntities.PIJIA_PANJIANG_HUWEI.get().create(h.getLevel());copy.load(saved);h.getLevel().addFreshEntity(copy);
        copy.die(h.getLevel().damageSources().genericKill());
        h.runAfterDelay(15,()->{
            int after=h.getLevel().getEntitiesOfClass(net.minecraft.world.entity.item.ItemEntity.class,area,ours).stream().mapToInt(e->e.getItem().getCount()).sum();
            h.assertTrue(after==count,"Reloading corpse and repeated death callback cannot repeat loot: before="+count+" after="+after);h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=340,batch="guard_world")
    public static void realGateEntrySpawnsTwoPersistentUpperGuards(GameTestHelper h){
        var level=h.getLevel();var id=new net.minecraft.resources.ResourceLocation("dynasty","great_wall_gate");
        var structure=level.registryAccess().registryOrThrow(net.minecraft.core.registries.Registries.STRUCTURE).get(id);
        var origin=new BlockPos(1792,100,1792);var chunk=new net.minecraft.world.level.ChunkPos(origin);
        var piece=new com.dynasty.structure.WallGatePiece(com.dynasty.structure.DynastyStructures.WALL_GATE_PIECE.get(),0,origin);
        var box=piece.getBoundingBox();var start=new net.minecraft.world.level.levelgen.structure.StructureStart(structure,chunk,0,
            new net.minecraft.world.level.levelgen.structure.pieces.PiecesContainer(List.of(piece)));
        level.getChunk(chunk.x,chunk.z).setStartForStructure(structure,start);
        var generator=level.getChunkSource().getGenerator();
        for(int x=box.minX()>>4;x<=box.maxX()>>4;x++)for(int z=box.minZ()>>4;z<=box.maxZ()>>4;z++){
            var part=level.getChunk(x,z);part.addReferenceForStructure(structure,chunk.toLong());
            piece.postProcess(level,level.structureManager(),generator,net.minecraft.util.RandomSource.create(9),
                new net.minecraft.world.level.levelgen.structure.BoundingBox(x*16,box.minY(),z*16,x*16+15,box.maxY(),z*16+15),part.getPos(),origin);
        }
        var positions=piece.upperGuardPositions();var entrant=positions.get(0).below(8);
        var player=new net.minecraftforge.common.util.FakePlayer(level,new com.mojang.authlib.GameProfile(UUID.randomUUID(),"gate-entry")){
            @Override public boolean isCreative(){return true;}
        };
        player.setPos(net.minecraft.world.phys.Vec3.atBottomCenterOf(entrant));level.addNewPlayer(player);
        boolean spawning=level.getGameRules().getBoolean(net.minecraft.world.level.GameRules.RULE_DOMOBSPAWNING);
        level.getGameRules().getRule(net.minecraft.world.level.GameRules.RULE_DOMOBSPAWNING).set(true,level.getServer());
        String key=id+"@"+chunk.toLong()+":upper_guards";
        h.runAfterDelay(270,()->{
            var data=BlueprintSpawnState.get(level);var marker=data.markers.get(key);
            h.assertTrue(marker!=null&&marker.produced==2&&marker.members.size()==2,"Ordinary entry ticks produce exactly two authored guards");
            var saved=BlueprintSpawnState.load(data.save(new CompoundTag())).markers.get(key);
            h.assertTrue(saved.members.equals(marker.members)&&saved.produced==2,"Restart checkpoint retains identities and slot count");
            UUID uuid=marker.members.iterator().next();var guard=(TemplateMob)level.getEntity(uuid);
            h.assertTrue(guard.kind()==TemplateMob.Kind.AXE_GUARD&&!guard.isNoAi(),"Spawned guard uses real AI");
            var tag=new CompoundTag();guard.save(tag);guard.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);
            h.assertTrue(marker.members.contains(uuid)&&!BlueprintSpawns.spawnGateGuard(level,key,positions,entrant),"Unload does not free a slot or duplicate the guard");
            var copy=BlueprintEntities.PIJIA_PANJIANG_HUWEI.get().create(level);copy.load(tag);level.addFreshEntity(copy);
            for(UUID member:List.copyOf(marker.members))level.getEntity(member).hurt(level.damageSources().genericKill(),10000);
            h.assertTrue(marker.members.isEmpty()&&marker.nextSpawn>=level.getGameTime()+11999,"Deaths release members and start real cooldown");
            h.assertTrue(!BlueprintSpawns.spawnGateGuard(level,key,positions,entrant),"Immediate re-entry cannot bypass cooldown");
            player.discard();level.getGameRules().getRule(net.minecraft.world.level.GameRules.RULE_DOMOBSPAWNING).set(spawning,level.getServer());h.succeed();
        });
    }
}
