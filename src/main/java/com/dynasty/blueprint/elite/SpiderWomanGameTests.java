package com.dynasty.blueprint.elite;

import com.dynasty.blueprint.*;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.gametest.*;
import java.util.*;

@GameTestHolder("dynasty_army")
@PrefixGameTestTemplate(false)
public final class SpiderWomanGameTests {
    private static final net.minecraft.server.level.TicketType<UUID> TICKET=net.minecraft.server.level.TicketType.create("dynasty_tianzhu_qa",UUID::compareTo);
    private record Ticket(net.minecraft.world.level.ChunkPos chunk,UUID id){}
    private static final Map<ServerLevel,List<Ticket>> TICKETS=new HashMap<>();
    private static final Map<ServerLevel,List<Entity>> FIXTURES=new HashMap<>();
    @AfterBatch(batch="spider_woman") public static void release(ServerLevel level){
        var fixtures=FIXTURES.remove(level);if(fixtures!=null)for(var e:fixtures){if(e instanceof SpiderWoman caster)caster.clearOwned();if(!e.isRemoved())e.discard();}
        var tickets=TICKETS.remove(level);if(tickets!=null)for(var t:tickets)level.getChunkSource().removeRegionTicket(TICKET,t.chunk(),2,t.id(),true);
    }
    private static <T extends Entity>T own(GameTestHelper h,T e){FIXTURES.computeIfAbsent(h.getLevel(),k->new ArrayList<>()).add(e);return e;}
    private static SpiderWoman mob(GameTestHelper h,boolean ceiling){
        var chunks=new HashSet<net.minecraft.world.level.ChunkPos>();for(int x:new int[]{0,15})for(int z:new int[]{0,15})chunks.add(new net.minecraft.world.level.ChunkPos(h.absolutePos(new BlockPos(x,2,z))));
        for(var c:chunks){var t=new Ticket(c,UUID.randomUUID());h.getLevel().getChunkSource().addRegionTicket(TICKET,c,2,t.id(),true);TICKETS.computeIfAbsent(h.getLevel(),k->new ArrayList<>()).add(t);}
        for(int x=0;x<16;x++)for(int z=0;z<16;z++){h.setBlock(x,1,z,Blocks.STONE);for(int y=2;y<8;y++)h.setBlock(x,y,z,Blocks.AIR);if(ceiling)h.setBlock(x,6,z,Blocks.STONE);}
        var m=own(h,h.spawn(EliteContent.SPIDER_WOMAN.get(),new BlockPos(7,ceiling?4:2,5)));m.setNoAi(false);m.setPersistenceRequired();m.bindEncounter("spider-woman@"+m.getUUID()+":spider_woman");return m;
    }
    private static Cow target(GameTestHelper h){var c=own(h,h.spawn(EntityType.COW,new BlockPos(7,2,8)));c.setNoAi(true);c.setNoGravity(true);c.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);c.setHealth(1000);return c;}
    @GameTest(template="bow_ritual_test",timeoutTicks=80,batch="spider_woman")
    public static void ceilingAdhesionRequiresAnActualSolidFaceAndStopsWhenItIsRemoved(GameTestHelper h){
        var m=mob(h,true);h.runAfterDelay(4,()->h.assertTrue(m.attachedToCeiling()&&m.isNoGravity()&&Math.abs(m.getY()-h.absolutePos(new BlockPos(7,4,5)).getY())<.1,"Actual native support holds the registered body at the ceiling"));
        h.runAfterDelay(8,()->{for(int x=5;x<=10;x++)for(int z=3;z<=8;z++)h.setBlock(x,6,z,Blocks.AIR);});
        h.runAfterDelay(25,()->{h.assertTrue(!m.attachedToCeiling()&&!m.isNoGravity()&&m.getY()<h.absolutePos(new BlockPos(7,4,5)).getY()-.5,"Removing physical support restores native gravity rather than retaining a flying actor");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=170,batch="spider_woman")
    public static void acidHasATwentyTickTellSixCloudCapAndOwnerDeathCleanup(GameTestHelper h){
        var m=mob(h,true);var victim=target(h);
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(371,victim),"Ceiling acid starts through the authoritative timeline"));
        h.runAfterDelay(22,()->h.assertTrue(h.getLevel().getEntitiesOfClass(SkullBloodPool.class,m.getBoundingBox().inflate(20),p->p.ownedBy(m)).isEmpty(),"The complete twenty-tick tell is harmless"));
        h.runAfterDelay(55,()->{var pools=h.getLevel().getEntitiesOfClass(SkullBloodPool.class,m.getBoundingBox().inflate(20),p->p.ownedBy(m));h.assertTrue(pools.size()==6&&victim.hasEffect(net.minecraft.world.effect.MobEffects.MOVEMENT_SLOWDOWN),"Actual clouds apply native severe slow and never exceed six");m.hurt(m.damageSources().genericKill(),10000);h.assertTrue(pools.stream().allMatch(Entity::isRemoved),"Parent death removes all damaging pools immediately");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=160,batch="spider_woman")
    public static void breakableEggsHatchInThreeSecondsAndOwnerDeathRemovesTheBrood(GameTestHelper h){
        var m=mob(h,false);var victim=target(h);
        var egg=own(h,EliteContent.SPIDER_BROOD.get().create(h.getLevel()));egg.moveTo(m.getX()+3,m.getY(),m.getZ(),0,0);egg.launch(m,victim);h.getLevel().addFreshEntity(egg);
            var broken=own(h,EliteContent.SPIDER_BROOD.get().create(h.getLevel()));broken.moveTo(m.getX()-3,m.getY(),m.getZ(),0,0);broken.launch(m,victim);h.getLevel().addFreshEntity(broken);
            var player=own(h,new net.minecraft.server.level.ServerPlayer(h.getLevel().getServer(),h.getLevel(),new com.mojang.authlib.GameProfile(UUID.randomUUID(),"spider-egg-counter")));
            player.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),player);
            player.setGameMode(net.minecraft.world.level.GameType.SURVIVAL);player.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,new net.minecraft.world.item.ItemStack(com.dynasty.DynastyGear.SWORD_BRONZE.get()));player.moveTo(broken.position().add(0,0,-1));h.getLevel().addNewPlayer(player);
            h.onEachTick(()->{if(!player.isRemoved())player.doTick();});
        h.runAfterDelay(24,()->{player.resetAttackStrengthTicker();for(int tick=0;tick<22;tick++)player.doTick();h.assertTrue(broken.getMaxHealth()==6&&broken.getHealth()==4&&!broken.hatched(),"Breakable egg begins with only four health");player.attack(broken);h.assertTrue(broken.isRemoved()&&!broken.hatched(),"Actual charged bronze-player attack breaks the egg before native hatch");player.discard();});
        h.runAfterDelay(58,()->h.assertTrue(!egg.hatched(),"Egg remains breakable until the full sixty-tick incubation"));
        h.runAfterDelay(64,()->{h.assertTrue(egg.hatched()&&egg.getHealth()==6,"The same entity becomes a native moving spider, without duplicating its owner slot");m.hurt(m.damageSources().genericKill(),10000);h.assertTrue(egg.isRemoved(),"Owner death ends the surviving brood immediately");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=290,batch="spider_woman")
    public static void absoluteBroodLifetimeAndMissedEggHatchCannotReplayAfterUnload(GameTestHelper h){
        var m=mob(h,false);var victim=target(h);var egg=own(h,EliteContent.SPIDER_BROOD.get().create(h.getLevel()));egg.moveTo(m.getX()+3,m.getY(),m.getZ(),0,0);egg.launch(m,victim);h.getLevel().addFreshEntity(egg);
        var stale=own(h,EliteContent.SPIDER_BROOD.get().create(h.getLevel()));stale.moveTo(m.getX()-3,m.getY(),m.getZ(),0,0);stale.launch(m,victim);var tag=new CompoundTag();stale.save(tag);stale.discard();
        var restored=new java.util.concurrent.atomic.AtomicReference<SpiderBrood>();
        h.runAfterDelay(65,()->{var loaded=own(h,EliteContent.SPIDER_BROOD.get().create(h.getLevel()));loaded.load(tag);h.getLevel().addFreshEntity(loaded);restored.set(loaded);});
        h.runAfterDelay(67,()->h.assertTrue(restored.get()!=null&&restored.get().isRemoved(),"An unloaded egg cannot catch up a missed hatch and spawn danger on login"));
        h.runAfterDelay(264,()->{h.assertTrue(egg.isRemoved(),"Original adult/brood ownership does not extend the absolute 260-tick lifetime");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=70,batch="spider_woman")
    public static void acceptedHeavyContactCancelsTheTellWithoutResettingCooldown(GameTestHelper h){
        var m=mob(h,true);var victim=target(h);
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(371,victim),"Native supported acid begins its tell"));
        h.runAfterDelay(8,()->{float before=m.getHealth();h.assertTrue(m.hurt(m.damageSources().mobAttack(victim),20)&&before-m.getHealth()>=8,"Real accepted contact crosses the heavy-hit counter threshold");h.assertTrue(m.phase()==com.dynasty.blueprint.combat.AttackState.STUN&&m.skillId()==0&&!m.attack().ready(371,h.getLevel().getGameTime()),"Heavy contact cancels only the tell and preserves its cooldown");});
        h.runAfterDelay(35,()->{h.assertTrue(h.getLevel().getEntitiesOfClass(SkullBloodPool.class,m.getBoundingBox().inflate(20),p->p.ownedBy(m)).isEmpty(),"An interrupted tell never catches up its damaging release");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=90,batch="spider_woman")
    public static void dropUsesNativeLandingAndPersistsTheConsumedReleaseFrame(GameTestHelper h){
        var m=mob(h,true);var victim=target(h);victim.setPos(m.getX(),victim.getY(),m.getZ());
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(372,victim),"Attached body starts the twelve-tick drop tell"));
        h.runAfterDelay(14,()->h.assertTrue(victim.getHealth()==1000&&m.attachedToCeiling(),"No landing damage before the complete tell"));
        h.runAfterDelay(19,()->{var data=new CompoundTag();m.save(data);var old=m.attack().save();h.assertTrue(old.getIntArray("Fired").length==1,"Only the release frame was consumed");m.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);var loaded=own(h,EliteContent.SPIDER_WOMAN.get().create(h.getLevel()));loaded.load(data);h.getLevel().addFreshEntity(loaded);h.assertTrue(loaded.getUUID().equals(m.getUUID())&&!loaded.attack().ready(372,h.getLevel().getGameTime())&&Arrays.equals(old.getIntArray("Fired"),loaded.attack().save().getIntArray("Fired")),"UUID, consumed contact and cooldown survive native actor load");});
        h.runAfterDelay(45,()->{h.assertTrue(victim.getHealth()<1000,"Real block-clipped falling body reaches the two-block landing area");h.succeed();});
    }
}
