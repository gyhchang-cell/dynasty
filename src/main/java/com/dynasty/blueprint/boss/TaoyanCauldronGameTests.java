package com.dynasty.blueprint.boss;
import com.dynasty.blueprint.combat.AttackState;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.*;
import net.minecraftforge.gametest.*;
import java.util.*;

/** Native acceptance source only. User paused Java; none of these regressions has run. */
@GameTestHolder("dynasty_army") @PrefixGameTestTemplate(false)
public final class TaoyanCauldronGameTests {
    private static final TicketType<UUID> TYPE=TicketType.create("dynasty_cauldron_qa",UUID::compareTo);
    private record Ticket(ChunkPos chunk,UUID id){}
    private static final Map<ServerLevel,List<Ticket>> TICKETS=new HashMap<>();
    private static final Map<ServerLevel,List<Entity>> ENTITIES=new HashMap<>();
    private static final Map<ServerLevel,Set<Long>> PITS=new HashMap<>();
    private static <T extends Entity>T own(GameTestHelper h,T e){ENTITIES.computeIfAbsent(h.getLevel(),k->new ArrayList<>()).add(e);return e;}
    @AfterBatch(batch="taoyan_cauldron") public static void release(ServerLevel world){var es=ENTITIES.remove(world);if(es!=null)for(var e:es){if(e instanceof TaoyanCauldron m)for(var s:m.spells())s.discard();if(!e.isRemoved())e.discard();}var ts=TICKETS.remove(world);if(ts!=null)for(var t:ts)world.getChunkSource().removeRegionTicket(TYPE,t.chunk(),2,t.id(),true);var pits=PITS.remove(world);if(pits!=null){var state=CauldronPitState.get(world);for(var key:pits)state.pits.remove(key);state.setDirty();}}
    private static CauldronPitState.Pit pit(GameTestHelper h){var origin=h.absolutePos(new BlockPos(8,1,8));var piece=new CauldronPitPiece(origin);var box=piece.getBoundingBox();for(int x=box.minX()>>4;x<=box.maxX()>>4;x++)for(int z=box.minZ()>>4;z<=box.maxZ()>>4;z++){var ticket=new Ticket(new ChunkPos(x,z),UUID.randomUUID());h.getLevel().getChunkSource().addRegionTicket(TYPE,ticket.chunk(),2,ticket.id(),true);TICKETS.computeIfAbsent(h.getLevel(),k->new ArrayList<>()).add(ticket);var chunk=h.getLevel().getChunk(x,z);piece.postProcess(h.getLevel(),h.getLevel().structureManager(),h.getLevel().getChunkSource().getGenerator(),net.minecraft.util.RandomSource.create(7),new net.minecraft.world.level.levelgen.structure.BoundingBox(x*16,box.minY(),z*16,x*16+15,box.maxY(),z*16+15),chunk.getPos(),origin);}var pit=CauldronPitState.get(h.getLevel()).register(piece.centre());PITS.computeIfAbsent(h.getLevel(),k->new HashSet<>()).add(pit.centre.asLong());return pit;}
    private static TaoyanCauldron caster(GameTestHelper h){var pit=pit(h);pit.ritualMask=7;h.assertTrue(CauldronPits.summon(h.getLevel(),pit),"Actual generated pit and ritual slot spawn one boss");var m=own(h,(TaoyanCauldron)h.getLevel().getEntity(pit.boss));m.setNoAi(true);return m;}
    private static Cow target(GameTestHelper h,TaoyanCauldron m,double dx,double dz){var c=own(h,net.minecraft.world.entity.EntityType.COW.create(h.getLevel()));c.moveTo(m.getX()+dx,m.getY(),m.getZ()+dz,0,0);c.setNoAi(true);c.setNoGravity(true);c.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);c.setHealth(1000);c.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);h.getLevel().addFreshEntity(c);return c;}
    @GameTest(template="cauldron_pit_test",timeoutTicks=215,batch="taoyan_cauldron")
    public static void realArenaHasTwelvePillarsThreeAltarsAndEightSecondIntro(GameTestHelper h){var m=caster(h);var p=m.arenaCentre();
        h.runAfterDelay(8,()->{int pillars=0,altars=0;for(int i=0;i<12;i++)if(h.getLevel().getBlockState(CauldronPitPiece.pillar(p,i)).is(Blocks.BONE_BLOCK))pillars++;for(int i=0;i<3;i++)if(h.getLevel().getBlockState(CauldronPitPiece.altar(p,i)).is(CauldronPitContent.RITUAL.get()))altars++;h.assertTrue(pillars==12&&altars==3&&h.getLevel().getBlockState(p.offset(19,-3,0)).is(CauldronPitContent.SOUL_OIL.get()),"Real authored pit has oil abyss and twelve bone pillars");});
        h.runAfterDelay(159,()->h.assertTrue(m.intro()&&!m.hurt(m.damageSources().magic(),10)&&m.getHealth()==m.getMaxHealth(),"All160intro ticks are a protected assembly window"));
        h.runAfterDelay(164,()->{h.assertTrue(!m.intro()&&m.form()==1&&!m.noPhysics&&!m.isNoGravity(),"Intro exits into genuine grounded tripod actor");h.succeed();});}
    @GameTest(template="cauldron_pit_test",timeoutTicks=300,batch="taoyan_cauldron")
    public static void fullTwentyTickRamThenTwelveClippedMetresAndOneContact(GameTestHelper h){var m=caster(h);var victim=target(h,m,0,6);var origin=m.position();
        h.runAfterDelay(164,()->h.assertTrue(m.startSkill(501,victim),"Twelve metre fixed-floor charge starts"));
        h.runAfterDelay(183,()->h.assertTrue(m.phase()==AttackState.WINDUP&&m.position().distanceToSqr(origin)<.01&&victim.getHealth()==1000,"All20tell ticks are planted"));
        h.runAfterDelay(197,()->{h.assertTrue(Math.abs(m.position().subtract(origin).horizontalDistance()-12)<.1&&victim.getHealth()<1000&&victim.getHealth()>=1000-18*1.3F-.01,"Actual12m motion, victim hit once across all12frames");});
        h.runAfterDelay(210,()->{h.assertTrue(m.phase()==AttackState.RECOVERY&&!m.attack().ready(501,h.getLevel().getGameTime()),"Recovery retains cooldown");h.succeed();});}
    @GameTest(template="cauldron_pit_test",timeoutTicks=270,batch="taoyan_cauldron")
    public static void newUnbreakableWallCancelsChargeWithoutPhasing(GameTestHelper h){var m=caster(h);var victim=target(h,m,0,6);var wall=m.blockPosition().offset(0,0,7);
        h.runAfterDelay(164,()->h.assertTrue(m.startSkill(501,victim),"Charge locks before new wall"));
        h.runAfterDelay(170,()->{for(int x=-3;x<=3;x++)for(int y=0;y<6;y++)h.getLevel().setBlock(wall.offset(x,y,0),Blocks.OBSIDIAN.defaultBlockState(),3);});
        h.runAfterDelay(192,()->{h.assertTrue(m.phase()==AttackState.STUN&&!m.attack().ready(501,h.getLevel().getGameTime())&&m.getZ()<wall.getZ()-2,"Native collider and non-whitelisted wall stop motion and retain cooldown");h.succeed();});}
    @GameTest(template="cauldron_pit_test",timeoutTicks=290,batch="taoyan_cauldron")
    public static void whipUsesActualLowSweepAndAcceptedHitsApplyFiniteBleeding(GameTestHelper h){var m=caster(h);var victim=target(h,m,5,0);var overhead=target(h,m,5,0);overhead.setPos(overhead.getX(),overhead.getY()+4,overhead.getZ());
        h.runAfterDelay(164,()->h.assertTrue(m.startSkill(502,victim),"Whip locks forward toward flank victim"));
        h.runAfterDelay(181,()->h.assertTrue(victim.getHealth()==1000,"No early whip damage"));
        h.runAfterDelay(215,()->{h.assertTrue(victim.getHealth()<1000&&victim.hasEffect(CauldronPitContent.BLEED.get())&&overhead.getHealth()==1000,"Actual six narrow swept contact frames, low plane and finite accepted-hit bleeding");h.succeed();});}
    @GameTest(template="cauldron_pit_test",timeoutTicks=385,batch="taoyan_cauldron")
    public static void fullOilTellOneSixMetrePatchAndExpiry(GameTestHelper h){var m=caster(h);var victim=target(h,m,0,7);
        h.runAfterDelay(164,()->h.assertTrue(m.startSkill(503,victim),"Oil begins"));h.runAfterDelay(187,()->h.assertTrue(m.spells().isEmpty()&&victim.getHealth()==1000,"Full24tick tell has no trap"));h.runAfterDelay(192,()->h.assertTrue(m.spells().size()==1&&m.spells().get(0).oil(),"One actual bounded radius6oil patch"));h.runAfterDelay(222,()->h.assertTrue(victim.getHealth()<1000&&victim.isOnFire(),"Native grounded body contacts persistent burning oil"));h.runAfterDelay(351,()->{h.assertTrue(m.spells().isEmpty(),"160tick patch expires without permanent fire placement");h.succeed();});}
    @GameTest(template="cauldron_pit_test",timeoutTicks=385,batch="taoyan_cauldron")
    public static void sixtyPercentTransitionThenPhysicalLeapAndSixGrowingCracks(GameTestHelper h){var m=caster(h);var victim=target(h,m,0,9);var start=m.position();
        h.runAfterDelay(164,()->m.setHealth(m.getMaxHealth()*.59F));h.runAfterDelay(166,()->h.assertTrue(m.form()==2&&m.transition()&&Math.abs(m.getAttributeValue(Attributes.MOVEMENT_SPEED)-.27)<.001,"Saved threshold gives eight-strut form and50percent movement increase"));h.runAfterDelay(232,()->h.assertTrue(m.startSkill(505,victim),"Phase2 leap starts after64tick morph"));h.runAfterDelay(247,()->h.assertTrue(m.position().distanceToSqr(start)<.01,"Full16tick tell is planted"));h.runAfterDelay(257,()->h.assertTrue(m.getY()>start.y+3.7&&!m.noPhysics&&!m.isNoGravity(),"Actual native move arc, never invisible teleport or noPhysics"));h.runAfterDelay(270,()->{h.assertTrue(m.position().distanceToSqr(m.landing())<.03&&m.spells().size()==6&&m.spells().stream().noneMatch(CauldronGroundSpell::oil),"Actual grounded impact makes exactly six finite extending fissures");});h.runAfterDelay(315,()->{h.assertTrue(m.spells().size()==6&&m.spells().stream().allMatch(s->s.length()<=16),"Each crack stays finite and truncates at floor/walls");h.succeed();});}
    @GameTest(template="cauldron_pit_test",timeoutTicks=300,batch="taoyan_cauldron")
    public static void heavyInterruptPreservesCooldownSavedTimeGapCannotReplayOil(GameTestHelper h){var m=caster(h);var victim=target(h,m,0,7);
        h.runAfterDelay(164,()->h.assertTrue(m.startSkill(501,victim),"Windup begins"));h.runAfterDelay(170,()->{m.hurt(m.damageSources().magic(),60);h.assertTrue(m.phase()==AttackState.STUN&&!m.attack().ready(501,h.getLevel().getGameTime()),"Accepted35net heavy contact interrupts with50tick stun and retained cooldown");});h.runAfterDelay(226,()->{h.assertTrue(m.startSkill(503,victim),"Next distinct attack starts");var tag=m.saveWithoutId(new CompoundTag());tag.putLong("TaoyanLastCombat",h.getLevel().getGameTime()-25);m.load(tag);});h.runAfterDelay(260,()->{h.assertTrue(m.skillId()==0&&m.spells().isEmpty()&&victim.getHealth()==1000,"Saved time jump safely cancels without replayed persistent traps");h.succeed();});}
    @GameTest(template="cauldron_pit_test",timeoutTicks=260,batch="taoyan_cauldron")
    public static void uuidUnloadIsNotVictoryDeathDrainsOnlyAuthoredOilAndPersists(GameTestHelper h){var m=caster(h);var state=CauldronPitState.get(h.getLevel());var pit=state.pits.get(m.arenaCentre().asLong());
        h.runAfterDelay(8,()->{h.assertTrue(!CauldronPits.summon(h.getLevel(),pit),"Existing UUID prevents duplicate summon");var tag=m.saveWithoutId(new CompoundTag());m.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);h.assertTrue(pit.boss!=null&&!pit.defeated&&!CauldronPits.summon(h.getLevel(),pit),"Unload retains slot and is not victory");var restored=own(h,CauldronPitContent.CAULDRON.get().create(h.getLevel()));restored.load(tag);restored.setNoAi(true);h.getLevel().addFreshEntity(restored);restored.hurt(restored.damageSources().genericKill(),10000);});
        h.runAfterDelay(12,()->{h.assertTrue(pit.defeated&&pit.boss==null&&!CauldronPits.summon(h.getLevel(),pit),"Only confirmed death wins and blocks natural repeat");for(int i=0;i<32;i++)CauldronPits.applyEnvironment(h.getLevel(),pit,64);h.assertTrue(pit.environmentCursor==2000&&!h.getLevel().getBlockState(pit.centre.offset(19,-3,0)).is(CauldronPitContent.SOUL_OIL.get()),"Saved bounded cursor drains genuine authored oil");h.assertTrue(h.getLevel().getBlockState(pit.centre).is(Blocks.QUARTZ_PILLAR),"Actual memorial replaces only empty authored centre");var reloaded=CauldronPitState.load(state.save(new CompoundTag()));h.assertTrue(reloaded.pits.get(pit.centre.asLong()).defeated&&reloaded.pits.get(pit.centre.asLong()).environmentCursor==2000,"Arena victory and environment cursor survive full NBT round trip");});
        h.runAfterDelay(214,()->{h.assertTrue(h.getLevel().getEntitiesOfClass(TaoyanCauldron.class,new AABB(pit.centre).inflate(20)).isEmpty(),"200tick death removes once");h.succeed();});}
}
