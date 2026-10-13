package com.dynasty.blueprint.elite;

import com.dynasty.blueprint.combat.AttackState;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.*;
import net.minecraftforge.gametest.*;
import java.util.*;

/** Native acceptance sources prepared during the user's Java pause; NOT RUN. */
@GameTestHolder("dynasty_army") @PrefixGameTestTemplate(false)
public final class LampJudgeGameTests {
    private static final TicketType<UUID> TYPE=TicketType.create("dynasty_judge_qa",UUID::compareTo);
    private record Ticket(net.minecraft.world.level.ChunkPos chunk,UUID id){}
    private static final Map<ServerLevel,List<Ticket>> TICKETS=new HashMap<>();
    private static final Map<ServerLevel,List<Entity>> FIXTURES=new HashMap<>();
    private static <T extends Entity>T own(GameTestHelper h,T e){FIXTURES.computeIfAbsent(h.getLevel(),k->new ArrayList<>()).add(e);return e;}
    @AfterBatch(batch="lamp_judge") public static void release(ServerLevel world){
        var es=FIXTURES.remove(world);if(es!=null)for(var e:es)if(!e.isRemoved())e.discard();
        var ts=TICKETS.remove(world);if(ts!=null)for(var t:ts)world.getChunkSource().removeRegionTicket(TYPE,t.chunk(),2,t.id(),true);
    }
    private static LampJudge caster(GameTestHelper h){
        var chunks=new HashSet<net.minecraft.world.level.ChunkPos>();for(int x:new int[]{0,15})for(int z:new int[]{0,15})chunks.add(new net.minecraft.world.level.ChunkPos(h.absolutePos(new BlockPos(x,2,z))));
        for(var chunk:chunks){var t=new Ticket(chunk,UUID.randomUUID());h.getLevel().getChunkSource().addRegionTicket(TYPE,chunk,2,t.id(),true);TICKETS.computeIfAbsent(h.getLevel(),k->new ArrayList<>()).add(t);}
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=0;y<14;y++)h.setBlock(x,y,z,y<=1?Blocks.STONE:Blocks.AIR);
        var m=own(h,h.spawn(EliteContent.LAMP_JUDGE.get(),new BlockPos(7,2,4)));m.setNoAi(true);m.setPersistenceRequired();return m;
    }
    private static Cow target(GameTestHelper h,int x,int z){var c=own(h,h.spawn(EntityType.COW,new BlockPos(x,2,z)));c.setNoAi(true);c.setNoGravity(true);c.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);c.setHealth(1000);c.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);return c;}
    private static ServerPlayer player(GameTestHelper h,Vec3 at){
        var p=own(h,new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new com.mojang.authlib.GameProfile(UUID.randomUUID(),"judge-qa")));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.setGameMode(GameType.SURVIVAL);p.moveTo(at);p.setNoGravity(true);h.getLevel().addNewPlayer(p);return p;
    }
    private static List<JudgeSpell> spells(GameTestHelper h,LampJudge m){return h.getLevel().getEntitiesOfClass(JudgeSpell.class,m.getBoundingBox().inflate(68),e->e.ownedBy(m));}
    @GameTest(template="bow_ritual_test",timeoutTicks=80,batch="lamp_judge")
    public static void fortyTickNamedTellThenActualNibDamage(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,10);
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(431,victim),"Named tell starts"));
        h.runAfterDelay(43,()->h.assertTrue(victim.getHealth()==1000&&spells(h,m).isEmpty()&&m.phase()==AttackState.WINDUP,"All40tell ticks are harmless"));
        h.runAfterDelay(46,()->{var pens=spells(h,m).stream().filter(JudgeSpell::pen).toList();h.assertTrue(pens.size()==1&&pens.get(0).getDeltaMovement().y<0,"Exactly one five-metre pen physically descends");for(var p:pens)own(h,p);});
        h.runAfterDelay(58,()->{h.assertTrue(victim.getHealth()<1000&&spells(h,m).isEmpty(),"Actual nib hits once and disappears");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=80,batch="lamp_judge")
    public static void lastFlashLocksMarkAndLeavesARealDodgeWindow(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,10);var locked=new java.util.concurrent.atomic.AtomicReference<Vec3>();
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(431,victim),"Named attack starts"));
        h.runAfterDelay(41,()->{locked.set(m.mark());victim.moveTo(h.absolutePos(new BlockPos(10,2,10)),0,0);});
        h.runAfterDelay(46,()->h.assertTrue(m.mark().distanceToSqr(locked.get())<.001,"Third-flash mark stops tracking before the pen appears"));
        h.runAfterDelay(62,()->h.assertTrue(victim.getHealth()==1000&&spells(h,m).stream().allMatch(e->e.pen()&&e.stuck()),"Three-metre late sidestep avoids nib; missed pen visibly sticks harmlessly in floor"));
        h.runAfterDelay(78,()->{h.assertTrue(spells(h,m).isEmpty(),"Missed floor pen expires within30ticks");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=85,batch="lamp_judge")
    public static void lateSolidRoofStopsPenWithoutVictimDamage(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,10);
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(431,victim),"Attack starts before the roof"));
        h.runAfterDelay(38,()->{for(int x=6;x<=8;x++)for(int z=9;z<=11;z++)h.setBlock(x,5,z,Blocks.STONE);});
        h.runAfterDelay(65,()->{h.assertTrue(victim.getHealth()==1000&&spells(h,m).isEmpty(),"A native collision roof blocks the pen instead of damaging through it");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=155,batch="lamp_judge")
    public static void exactlyFivePersistentCutsAndOwnerDeathCleanup(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,8);
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(432,victim),"Five-cut action starts"));
        h.runAfterDelay(13,()->h.assertTrue(spells(h,m).isEmpty(),"Ten tick tell precedes first cut"));
        h.runAfterDelay(49,()->{var cuts=spells(h,m);h.assertTrue(cuts.size()==5&&cuts.stream().noneMatch(e->e.pen()||e.cage()),"Five impacts10/18/26/34/42 produce exactly five real cuts");for(var e:cuts)own(h,e);m.hurt(m.damageSources().magic(),10000);});
        h.runAfterDelay(52,()->{h.assertTrue(spells(h,m).isEmpty(),"Death clears all five world cuts");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=100,batch="lamp_judge")
    public static void cutTruncatesAtWallAndCannotRepeatedlyHurtOneVictim(GameTestHelper h){
        var m=caster(h);var beforeWall=target(h,7,7);var behindWall=target(h,7,11);var spell=own(h,EliteContent.JUDGE_STROKE.get().create(h.getLevel()));
        for(int x=6;x<=8;x++)for(int y=2;y<=4;y++)h.setBlock(x,y,9,Blocks.STONE);
        h.runAfterDelay(4,()->{spell.launch(m,m.position().add(0,.8,1),new Vec3(0,0,1));h.getLevel().addFreshEntity(spell);});
        var health=new java.util.concurrent.atomic.AtomicReference<Float>();
        h.runAfterDelay(8,()->{h.assertTrue(beforeWall.getHealth()<1000&&behindWall.getHealth()==1000&&spell.strokeLength()<4,"Actual box contact hurts before wall; visual and hit length stop there");health.set(beforeWall.getHealth());});
        h.runAfterDelay(48,()->h.assertTrue(beforeWall.getHealth()==health.get(),"Persistent cut hits a UUID only once even after native invulnerability expires"));
        h.runAfterDelay(88,()->{h.assertTrue(spell.isRemoved(),"Cut lifetime is80ticks");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=215,batch="lamp_judge")
    public static void nativeSixMetreCageConfinesTwoPlayersThenExpires(GameTestHelper h){
        var m=caster(h);var at=m.position().add(0,0,2);var a=player(h,at);var b=player(h,at.add(.6,0,0));
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(433,a),"Two-player circle starts on legal floor"));
        h.runAfterDelay(19,()->h.assertTrue(spells(h,m).isEmpty(),"Full16tick tell before confinement"));
        h.runAfterDelay(23,()->{var cages=spells(h,m).stream().filter(JudgeSpell::cage).toList();h.assertTrue(cages.size()==1&&cages.get(0).trappedCount()==2,"Four visual columns belong to one native cage; both players captured");own(h,cages.get(0));a.moveTo(at.add(5,0,0));b.moveTo(at.add(-5,0,0));});
        h.runAfterDelay(26,()->h.assertTrue(a.position().subtract(m.mark()).horizontalDistanceSqr()<=2.61*2.61&&b.position().subtract(m.mark()).horizontalDistanceSqr()<=2.61*2.61,"Native server positions stay inside diameter6 boundary"));
        h.runAfterDelay(182,()->{h.assertTrue(spells(h,m).isEmpty(),"Cage lifetime is exactly160ticks from formation");a.moveTo(at.add(5,0,0));});
        h.runAfterDelay(186,()->{h.assertTrue(a.position().subtract(m.mark()).horizontalDistanceSqr()>16,"Expiry restores free movement with no residual constraint");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=100,batch="lamp_judge")
    public static void acceptedRearStrikeBreaksCageAndPreservesCooldown(GameTestHelper h){
        var m=caster(h);var p=player(h,m.position().add(0,0,2));
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(433,p),"Cage starts"));
        h.runAfterDelay(25,()->{p.moveTo(m.position().subtract(m.attack().direction().scale(.5)));m.hurt(m.damageSources().playerAttack(p),5);h.assertTrue(m.phase()==AttackState.STUN&&spells(h,m).isEmpty()&&!m.attack().ready(433,h.getLevel().getGameTime()),"Accepted real back hit breaks cage and retains300tick cooldown");});
        h.runAfterDelay(29,()->{p.moveTo(m.mark().add(5,0,0));h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=100,batch="lamp_judge")
    public static void timeGapAndCorruptMarkCannotReplayNamedPen(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,10);var saved=new CompoundTag();
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(431,victim),"Named action begins"));
        h.runAfterDelay(12,()->{m.saveWithoutId(saved);m.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);});
        h.runAfterDelay(20,()->{var restored=own(h,EliteContent.LAMP_JUDGE.get().create(h.getLevel()));restored.load(saved);restored.setNoAi(true);h.getLevel().addFreshEntity(restored);});
        h.runAfterDelay(55,()->{h.assertTrue(victim.getHealth()==1000&&spells(h,m).isEmpty(),"Unloaded checkpoint retains cooldown without dumping delayed pen");saved.putFloat("MarkY",Float.NaN);var corrupt=own(h,EliteContent.LAMP_JUDGE.get().create(h.getLevel()));corrupt.load(saved);h.assertTrue(corrupt.attack().current()==null,"Non-finite mark cancels before it can enter packets or physics");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=75,batch="lamp_judge")
    public static void solidObstructionRejectsArenaAndHeavyHitCancelsTell(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,6);h.setBlock(9,2,6,Blocks.STONE);
        h.runAfterDelay(4,()->{h.assertTrue(!m.startSkill(433,victim),"Full six-metre arena cannot form through a native wall");h.setBlock(9,2,6,Blocks.AIR);h.assertTrue(m.startSkill(433,victim),"Cleared loaded arena starts");});
        h.runAfterDelay(8,()->{m.hurt(m.damageSources().magic(),20);h.assertTrue(m.phase()==AttackState.STUN&&!m.attack().ready(433,h.getLevel().getGameTime()),"Heavy accepted windup hit cancels without refunding cooldown");});
        h.runAfterDelay(40,()->{h.assertTrue(spells(h,m).isEmpty(),"Interrupted tell never leaves pillars or constraints");h.succeed();});
    }
}
