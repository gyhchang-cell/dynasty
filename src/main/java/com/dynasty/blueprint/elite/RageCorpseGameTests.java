package com.dynasty.blueprint.elite;

import com.dynasty.blueprint.BlueprintSpawnState;
import com.dynasty.blueprint.combat.AttackState;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.item.*;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicReference;

/** Native acceptance source prepared during the user's Java pause; no case has run yet. */
@GameTestHolder("dynasty_army")
@PrefixGameTestTemplate(false)
public final class RageCorpseGameTests {
    private static final net.minecraft.server.level.TicketType<UUID> TICKET=net.minecraft.server.level.TicketType.create("dynasty_corpse_qa",UUID::compareTo);
    private record Ticket(net.minecraft.world.level.ChunkPos chunk,UUID id){}
    private static final Map<ServerLevel,List<Ticket>> TICKETS=new HashMap<>();
    private static final Map<ServerLevel,List<Entity>> FIXTURES=new HashMap<>();
    private static final Map<ServerLevel,Boolean> GRIEF_RULES=new HashMap<>();
    private static <T extends Entity>T own(GameTestHelper h,T e){FIXTURES.computeIfAbsent(h.getLevel(),k->new ArrayList<>()).add(e);return e;}
    @AfterBatch(batch="rage_corpse") public static void release(ServerLevel world){
        var grief=GRIEF_RULES.remove(world);if(grief!=null)world.getGameRules().getRule(GameRules.RULE_MOBGRIEFING).set(grief,world.getServer());
        var fixtures=FIXTURES.remove(world);if(fixtures!=null)for(var e:fixtures)if(!e.isRemoved())e.discard();
        var tickets=TICKETS.remove(world);if(tickets!=null)for(var t:tickets)world.getChunkSource().removeRegionTicket(TICKET,t.chunk(),2,t.id(),true);
    }
    private static RageCorpse caster(GameTestHelper h){
        var chunks=new HashSet<net.minecraft.world.level.ChunkPos>();for(int x:new int[]{0,15})for(int z:new int[]{0,15})chunks.add(new net.minecraft.world.level.ChunkPos(h.absolutePos(new BlockPos(x,2,z))));
        for(var chunk:chunks){var t=new Ticket(chunk,UUID.randomUUID());h.getLevel().getChunkSource().addRegionTicket(TICKET,chunk,2,t.id(),true);TICKETS.computeIfAbsent(h.getLevel(),k->new ArrayList<>()).add(t);}
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=0;y<10;y++)h.setBlock(x,y,z,y<=1?Blocks.STONE:Blocks.AIR);
        var m=own(h,h.spawn(EliteContent.RAGE_CORPSE.get(),new BlockPos(7,2,3)));m.setNoAi(true);m.setPersistenceRequired();return m;
    }
    private static Cow target(GameTestHelper h,int x,int z){var c=own(h,h.spawn(EntityType.COW,new BlockPos(x,2,z)));c.setNoAi(true);c.setNoGravity(true);c.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);c.setHealth(1000);return c;}
    @GameTest(template="bow_ritual_test",timeoutTicks=155,batch="rage_corpse")
    public static void fullSpinTellEightyActiveTicksAndFortyTickCounterWindow(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,7);var start=m.position();var recovery=new AtomicReference<Vec3>();
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(401,victim),"Native spin begins"));
        h.runAfterDelay(25,()->h.assertTrue(m.phase()==AttackState.WINDUP&&victim.getHealth()==1000&&m.position().distanceToSqr(start)<.01,"All twenty-two tell ticks are harmless and planted"));
        h.runAfterDelay(45,()->h.assertTrue(m.phase()==AttackState.ACTIVE&&m.getZ()>start.z+.4,"Spin physically translates during the eighty-tick active phase"));
        h.runAfterDelay(107,()->{recovery.set(m.position());h.assertTrue(m.phase()==AttackState.RECOVERY&&victim.getHealth()<1000,"Full active phase ends in an exposed counter window");});
        h.runAfterDelay(144,()->h.assertTrue(m.phase()==AttackState.RECOVERY&&m.position().distanceToSqr(recovery.get())<.01,"Forty-tick counter window does not chase the target"));
        h.runAfterDelay(148,()->{h.assertTrue(m.phase()==AttackState.IDLE&&!m.attack().ready(401,h.getLevel().getGameTime()),"Recovery ends without clearing consumed skill cooldown");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=85,batch="rage_corpse")
    public static void leapActuallyTravelsEightBlocksInTwentyClippedSteps(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,9);var start=m.position();
        var rule=h.getLevel().getGameRules().getRule(GameRules.RULE_MOBGRIEFING);boolean old=rule.get();GRIEF_RULES.putIfAbsent(h.getLevel(),old);
        h.runAfterDelay(4,()->{rule.set(false,h.getLevel().getServer());m.setNoAi(false);h.assertTrue(m.startSkill(402,victim),"Loaded eight-block landing is legal");victim.discard();h.assertTrue(Math.abs(m.landing().subtract(start).horizontalDistance()-8)<.001,"Fractional landing retains exactly eight blocks");});
        h.runAfterDelay(17,()->h.assertTrue(m.position().distanceToSqr(start)<.01,"Full fourteen-tick windup has no flight displacement"));
        h.runAfterDelay(28,()->{h.assertTrue(m.getY()>start.y+1.5&&m.getZ()>start.z+3&&m.getZ()<start.z+5,"Mid-flight has actual height and intermediate collision position");h.assertTrue(!m.noPhysics&&!m.isNoGravity(),"Flight never enables phasing or persistent no-gravity");});
        h.runAfterDelay(39,()->{try{h.assertTrue(Math.abs(m.position().subtract(start).horizontalDistance()-8)<.08&&Math.abs(m.getY()-start.y)<.1,"Native collision reaches the advertised endpoint after twenty steps");h.assertTrue(h.getBlockState(new BlockPos(7,1,11)).is(Blocks.STONE),"Mob griefing disabled preserves the landing floor");h.succeed();}finally{rule.set(old,h.getLevel().getServer());}});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=90,batch="rage_corpse")
    public static void aNewSolidWallInterruptsFlightAndGravityResumes(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,9);var start=m.position();
        h.runAfterDelay(4,()->{m.setNoAi(false);h.assertTrue(m.startSkill(402,victim),"Clear route starts");victim.discard();});
        h.runAfterDelay(17,()->{for(int x=0;x<16;x++)for(int y=2;y<9;y++)h.setBlock(x,y,7,Blocks.STONE);});
        h.runAfterDelay(35,()->{h.assertTrue(m.skillId()==0&&m.phase()==AttackState.STUN&&!m.attack().ready(402,h.getLevel().getGameTime()),"New obstacle cancels flight into a real counter window and retains cooldown");h.assertTrue(m.getZ()<=h.absolutePos(new BlockPos(7,2,7)).getZ()-2+.01&&!m.isNoGravity(),"Four-block collider remains on the near side of the wall");});
        h.runAfterDelay(65,()->{h.assertTrue(Math.abs(m.getY()-start.y)<.15,"Ordinary travel brings the interrupted actor back to the floor");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=90,batch="rage_corpse")
    public static void acceptedHeavyDamageAndUnloadGapCannotReplayALanding(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,9);var restored=new AtomicReference<RageCorpse>();var saved=new CompoundTag();
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(402,victim),"Interruptible tell begins"));
        h.runAfterDelay(8,()->{float hp=m.getHealth();h.assertTrue(m.hurt(m.damageSources().mobAttack(victim),30)&&hp-m.getHealth()>=12,"Actual armored contact reaches the advertised heavy threshold");h.assertTrue(m.phase()==AttackState.STUN&&!m.attack().ready(402,h.getLevel().getGameTime()),"Accepted heavy damage stops the cast without a cooldown refund");});
        h.runAfterDelay(40,()->{m.attack().load(new CompoundTag(),RageCorpse::skill,h.getLevel().getGameTime());h.assertTrue(m.startSkill(402,victim),"Independent unload scenario starts");victim.discard();});
        h.runAfterDelay(57,()->{m.save(saved);m.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);});
        h.runAfterDelay(62,()->{var actor=own(h,EliteContent.RAGE_CORPSE.get().create(h.getLevel()));actor.load(saved);actor.setNoAi(false);h.getLevel().addFreshEntity(actor);restored.set(actor);});
        h.runAfterDelay(82,()->{var actor=restored.get();h.assertTrue(actor.getUUID().equals(m.getUUID())&&actor.skillId()==0&&!actor.isNoGravity()&&!actor.attack().ready(402,h.getLevel().getGameTime()),"Original UUID/cooldown survive while a missed flight interval cancels safely");h.assertTrue(h.getBlockState(new BlockPos(7,1,11)).is(Blocks.STONE),"Cancelled old landing never causes delayed terrain destruction");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=150,batch="rage_corpse")
    public static void bloodLocksFacingRespectsWallsAndCorrosionExpires(GameTestHelper h){
        var m=caster(h);var near=target(h,7,7);var far=target(h,7,10);var side=target(h,11,7);float[] armor={0};
        near.getAttribute(Attributes.ARMOR).setBaseValue(10);armor[0]=(float)near.getAttributeValue(Attributes.ARMOR);
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(403,near),"Belly blood cast begins"));
        h.runAfterDelay(12,()->{m.setTarget(side);for(int x=5;x<=9;x++)for(int y=2;y<6;y++)h.setBlock(x,y,9,Blocks.STONE);});
        h.runAfterDelay(44,()->{h.assertTrue(near.getHealth()<1000&&near.hasEffect(EliteContent.RAGE_CORROSION.get())&&near.getAttributeValue(Attributes.ARMOR)==armor[0]-4,"Actual accepted blood damage applies finite native armor corrosion");h.assertTrue(far.getHealth()==1000&&side.getHealth()==1000,"Wall and lateral safe route remain outside damage despite a new target");});
        h.runAfterDelay(145,()->{h.assertTrue(!near.hasEffect(EliteContent.RAGE_CORROSION.get())&&near.getAttributeValue(Attributes.ARMOR)==armor[0],"Corrosion expires without leaving a permanent armor modifier");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=30,batch="rage_corpse")
    public static void corrosionWearsRealArmorOncePerSecondAndRemovalRestoresArmor(GameTestHelper h){
        var p=own(h,new net.minecraftforge.common.util.FakePlayer(h.getLevel(),new com.mojang.authlib.GameProfile(UUID.randomUUID(),"corpse-wear")));
        p.setItemSlot(EquipmentSlot.CHEST,new ItemStack(Items.IRON_CHESTPLATE));p.getAttribute(Attributes.ARMOR).setBaseValue(10);double before=p.getAttributeValue(Attributes.ARMOR);
        p.addEffect(new MobEffectInstance(EliteContent.RAGE_CORROSION.get(),100));var effect=EliteContent.RAGE_CORROSION.get();
        h.assertTrue(!effect.isDurationEffectTick(99,0)&&effect.isDurationEffectTick(100,0),"Only exact second boundaries produce wear");
        effect.applyEffectTick(p,0);h.assertTrue(p.getItemBySlot(EquipmentSlot.CHEST).getDamageValue()==1,"One real durability point per equipped armor second");
        p.removeEffect(effect);h.assertTrue(p.getAttributeValue(Attributes.ARMOR)==before,"Removing the finite effect removes the native modifier");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=80,batch="rage_corpse")
    public static void shallowCraterHonorsGriefingAndProtectsContainersAndOres(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,9);var world=h.getLevel();var rule=world.getGameRules().getRule(GameRules.RULE_MOBGRIEFING);boolean old=rule.get();GRIEF_RULES.putIfAbsent(world,old);
        h.setBlock(6,1,11,Blocks.CHEST);h.setBlock(8,1,11,Blocks.DIAMOND_ORE);
        h.runAfterDelay(4,()->{rule.set(true,world.getServer());m.setNoAi(false);h.assertTrue(m.startSkill(402,victim),"Actual destructive landing starts");victim.discard();});
        h.runAfterDelay(42,()->{try{h.assertTrue(h.getBlockState(new BlockPos(7,1,11)).isAir()&&h.getBlockState(new BlockPos(7,0,11)).is(Blocks.STONE),"Actual impact removes only one shallow floor layer");h.assertTrue(h.getBlockState(new BlockPos(6,1,11)).is(Blocks.CHEST)&&h.getBlockState(new BlockPos(8,1,11)).is(Blocks.DIAMOND_ORE),"Containers and ores never enter destruction allowlist");h.assertTrue(h.getBlockState(new BlockPos(7,1,15)).is(Blocks.STONE),"Terrain outside three-block radius remains intact");h.succeed();}finally{rule.set(old,world.getServer());}});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=100,batch="rage_corpse")
    public static void tombSlotRetainsUnloadedUuidAndUsesDeathCooldown(GameTestHelper h){
        var fixture=caster(h);var feet=fixture.blockPosition();fixture.discard();String key="corpse-native@"+feet.asLong()+":rage_corpse";var world=h.getLevel();
        h.startSequence().thenWaitUntil(()->h.assertTrue(world.isPositionEntityTicking(feet),"Tomb fixture is entity-ticking")).thenExecute(()->{
            var rule=world.getGameRules().getRule(GameRules.RULE_DOMOBSPAWNING);boolean old=rule.get();rule.set(true,world.getServer());try{
                h.assertTrue(EliteEncounters.spawnRageCorpse(world,key,feet,feet.offset(0,0,8)),"Loaded open vault supports one ordinary structure actor");var marker=BlueprintSpawnState.get(world).markers.get(key);var actor=(RageCorpse)own(h,world.getEntity(marker.members.iterator().next()));var tag=new CompoundTag();actor.save(tag);actor.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);
                h.assertTrue(!EliteEncounters.spawnRageCorpse(world,key,feet,feet.offset(0,0,8)),"Unloaded UUID reserves its structure slot");var restored=own(h,EliteContent.RAGE_CORPSE.get().create(world));restored.load(tag);world.addFreshEntity(restored);restored.hurt(restored.damageSources().genericKill(),10000);
                h.assertTrue(marker.members.isEmpty()&&marker.nextSpawn==world.getGameTime()+12000&&!EliteEncounters.spawnRageCorpse(world,key,feet,feet.offset(0,0,8)),"Confirmed death begins persistent twelve-thousand-tick cooldown");
            }finally{rule.set(old,world.getServer());}
        }).thenSucceed();
    }
}
