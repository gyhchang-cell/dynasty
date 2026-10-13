package com.dynasty.blueprint.boss;

import com.dynasty.blueprint.combat.AttackState;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.*;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.phys.*;
import net.minecraftforge.gametest.*;
import java.util.*;

/** Native acceptance SOURCES. These have not run: the user's Java/build pause remains active. */
@GameTestHolder("dynasty_army") @PrefixGameTestTemplate(false)
public final class WoodKiteGameTests {
    private static final TicketType<UUID> TYPE=TicketType.create("dynasty_kite_qa",UUID::compareTo);
    private record Ticket(ChunkPos chunk,UUID id){}
    private static final Map<ServerLevel,List<Ticket>> TICKETS=new HashMap<>();
    private static final Map<ServerLevel,List<Entity>> OWNED=new HashMap<>();
    private static final Map<ServerLevel,Set<Long>> SITES=new HashMap<>();
    private static <T extends Entity> T own(GameTestHelper h,T e){OWNED.computeIfAbsent(h.getLevel(),k->new ArrayList<>()).add(e);return e;}
    @AfterBatch(batch="wood_kite") public static void release(ServerLevel w){
        var entities=OWNED.remove(w);if(entities!=null)for(var e:entities){if(e instanceof WoodKite k)for(var b:k.bombs())b.discard();if(!e.isRemoved())e.discard();}
        var sites=SITES.remove(w);if(sites!=null){var state=StargazerPlatformState.get(w);for(long pos:sites)state.platforms.remove(pos);state.setDirty();}
        var tickets=TICKETS.remove(w);if(tickets!=null)for(var ticket:tickets)w.getChunkSource().removeRegionTicket(TYPE,ticket.chunk(),2,ticket.id(),true);
    }
    private static WoodKite caster(GameTestHelper h){
        var relative=h.absolutePos(new BlockPos(32,1,32));var origin=new BlockPos(relative.getX()-17,199,relative.getZ()-17);
        var piece=new StargazerPlatformPiece(origin);var bounds=piece.getBoundingBox();
        for(int x=(bounds.minX()-26)>>4;x<=(bounds.maxX()+26)>>4;x++)for(int z=(bounds.minZ()-26)>>4;z<=(bounds.maxZ()+26)>>4;z++){
            var ticket=new Ticket(new ChunkPos(x,z),UUID.randomUUID());h.getLevel().getChunkSource().addRegionTicket(TYPE,ticket.chunk(),2,ticket.id(),true);TICKETS.computeIfAbsent(h.getLevel(),k->new ArrayList<>()).add(ticket);
            var chunk=h.getLevel().getChunk(x,z);piece.postProcess(h.getLevel(),h.getLevel().structureManager(),h.getLevel().getChunkSource().getGenerator(),net.minecraft.util.RandomSource.create(12),new BoundingBox(x*16,199,z*16,x*16+15,207,z*16+15),chunk.getPos(),origin);
        }
        var site=StargazerPlatformState.get(h.getLevel()).register(piece.centre());SITES.computeIfAbsent(h.getLevel(),k->new HashSet<>()).add(site.centre.asLong());
        h.assertTrue(StargazerPlatforms.summon(h.getLevel(),site),"Actual loaded platform and socket summon one reserved bird");
        var kite=own(h,(WoodKite)h.getLevel().getEntity(site.boss));kite.setNoAi(true);return kite;
    }
    private static Cow target(GameTestHelper h,WoodKite k,double x,double z){
        var cow=own(h,EntityType.COW.create(h.getLevel()));var at=k.centre().add(x,0,z);cow.moveTo(at.x,at.y,at.z,0,0);cow.setNoAi(true);cow.setNoGravity(true);
        cow.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);cow.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);cow.setHealth(1000);h.getLevel().addFreshEntity(cow);return cow;
    }
    private static ServerPlayer player(GameTestHelper h,WoodKite k){
        var p=own(h,new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new com.mojang.authlib.GameProfile(UUID.randomUUID(),"kite-qa")));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.setGameMode(GameType.SURVIVAL);var at=k.centre().add(0,0,8);p.moveTo(at.x,at.y,at.z,0,0);p.setNoGravity(true);p.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);p.setHealth(1000);h.getLevel().addNewPlayer(p);h.onEachTick(p::doTick);return p;
    }
    @GameTest(template="cauldron_pit_test",timeoutTicks=280,batch="wood_kite")
    public static void genuineHighOctagonOutsideAscentAndProtectedTenSecondEntrance(GameTestHelper h){
        var k=caster(h);var c=k.arenaCentre();var ground=c.offset(0,-60,-18);var rope=new StargazerApproachPiece(ground);
        rope.postProcess(h.getLevel(),h.getLevel().structureManager(),h.getLevel().getChunkSource().getGenerator(),net.minecraft.util.RandomSource.create(12),rope.getBoundingBox(),new ChunkPos(ground),ground);
        h.runAfterDelay(8,()->{h.assertTrue(c.getY()==201&&h.getLevel().getBlockState(c.offset(17,-1,0)).is(WoodKiteContent.PLANK.get())&&h.getLevel().isEmptyBlock(c.offset(17,0,0)),"Floor200,35-block extent and genuinely unguarded edge");h.assertTrue(h.getLevel().getBlockState(ground.above(20)).is(BlockTags.CLIMBABLE)&&h.getLevel().getBlockState(c.offset(0,0,-18)).is(WoodKiteContent.ROPE.get()),"Actual continuous tagged first-arrival rope outside the lip");});
        h.runAfterDelay(199,()->h.assertTrue(k.intro()&&!k.hurt(k.damageSources().magic(),100),"Whole200-tick intro is protected"));
        h.runAfterDelay(205,()->{h.assertTrue(!k.intro()&&k.position().distanceToSqr(k.centre())<4&&k.isNoGravity()&&!k.noPhysics&&k.getHealth()==k.getMaxHealth(),"Native clipped aircraft lands and keeps real collision");h.succeed();});
    }
    @GameTest(template="cauldron_pit_test",timeoutTicks=365,batch="wood_kite")
    public static void eightActualSlowBombsLandBeforeFuseThenAllExpire(GameTestHelper h){
        var k=caster(h);var c=target(h,k,0,8);
        h.runAfterDelay(205,()->h.assertTrue(k.startSkill(522,c),"Bomb bay attack begins"));
        h.runAfterDelay(228,()->h.assertTrue(k.bombs().isEmpty(),"No projectile before24-tick tell"));
        h.runAfterDelay(274,()->h.assertTrue(k.bombs().size()==8&&k.bombs().stream().anyMatch(b->!b.landed()),"Eight real entities descend slowly; no instant ground explosions"));
        h.runAfterDelay(360,()->{h.assertTrue(k.bombs().isEmpty(),"Every bomb has detonated once or expired with no residual mine");h.succeed();});
    }
    @GameTest(template="cauldron_pit_test",timeoutTicks=300,batch="wood_kite")
    public static void heavyInterruptKeepsCooldownAndInvalidatesRealBombOwnerEpoch(GameTestHelper h){
        var k=caster(h);var c=target(h,k,0,8);
        h.runAfterDelay(205,()->h.assertTrue(k.startSkill(522,c),"Bomb sequence begins"));
        h.runAfterDelay(235,()->{h.assertTrue(!k.bombs().isEmpty(),"Real projectile exists before parry");long epoch=k.bombEpoch();k.parried(40);h.assertTrue(k.phase()==AttackState.STUN&&k.bombEpoch()!=epoch&&k.bombs().isEmpty()&&!k.attack().ready(522,h.getLevel().getGameTime()),"Parry consumes owner effects and preserves attack cooldown");});
        h.runAfterDelay(279,()->{h.assertTrue(k.skillId()==0&&k.bombs().isEmpty(),"No late volley or stale fuse after stun");h.succeed();});
    }
    @GameTest(template="cauldron_pit_test",timeoutTicks=380,batch="wood_kite")
    public static void sixtyPercentMetalMorphFourScarsAndExactFifteenPercentCap(GameTestHelper h){
        var k=caster(h);var c=target(h,k,0,8);var site=StargazerPlatformState.get(h.getLevel()).platforms.get(k.arenaCentre().asLong());
        h.runAfterDelay(205,()->k.setHealth(k.getMaxHealth()*.599F));
        h.runAfterDelay(210,()->h.assertTrue(k.form()==2&&k.transition()&&!k.startSkill(525,c),"True60percent phase has a48-tick protected shell removal"));
        h.runAfterDelay(258,()->h.assertTrue(!k.transition()&&k.startSkill(525,c),"Four lightning impacts start only after morph"));
        h.runAfterDelay(345,()->{h.assertTrue(site.removed.size()+site.charred.size()==StargazerPlatforms.FLOOR_LOSS_CAP,"Four authored patches consume floor15percent rounded down");h.assertTrue(h.getLevel().getBlockState(site.centre.below()).is(WoodKiteContent.SOCKET.get()),"Central socket and frame excluded");});
        h.runAfterDelay(378,()->{for(var b:site.charred.entrySet())h.assertTrue(h.getLevel().getBlockState(BlockPos.of(b.getKey())).is(WoodKiteContent.CHARRED.get()),"No unconstrained vanilla fire spread");h.assertTrue(site.removed.size()+site.charred.size()<=StargazerPlatforms.FLOOR_LOSS_CAP,"Total cap persists across staggered collapse");h.succeed();});
    }
    @GameTest(template="cauldron_pit_test",timeoutTicks=380,batch="wood_kite")
    public static void actualDescendingMeteorGroundWaveHitsFloorAndSparesJump(GameTestHelper h){
        var k=caster(h);var ground=target(h,k,0,11);var jump=target(h,k,3,11);
        h.runAfterDelay(205,()->k.setHealth(k.getMaxHealth()*.59F));
        h.runAfterDelay(258,()->h.assertTrue(k.startSkill(526,ground),"Metal meteor ascends for60ticks"));
        h.runAfterDelay(310,()->h.assertTrue(k.getY()>k.centre().y+45&&ground.getHealth()==1000,"Actual high actor before descent, never early damage"));
        h.runAfterDelay(316,()->jump.setPos(jump.getX(),k.centre().y+.65,jump.getZ()));
        h.runAfterDelay(341,()->{h.assertTrue(ground.getHealth()<1000&&jump.getHealth()==1000,"Real ground wave reaches floor body and excludes raised feet");h.assertTrue(!k.noPhysics&&k.getY()<k.centre().y+.1&&Math.abs(k.getHealth()-k.getMaxHealth()*.59F)<.01,"Meteor respects native movement and returns to platform");h.succeed();});
    }
    @GameTest(template="cauldron_pit_test",timeoutTicks=290,batch="wood_kite")
    public static void bombReloadAndCasterTimeGapCannotReplayAnyDamage(GameTestHelper h){
        var k=caster(h);var c=target(h,k,0,8);
        h.runAfterDelay(205,()->h.assertTrue(k.startSkill(522,c),"Volley begins"));
        h.runAfterDelay(235,()->{var bomb=k.bombs().get(0);var n=bomb.saveWithoutId(new CompoundTag());var reloaded=own(h,WoodKiteContent.BOMB.get().create(h.getLevel()));reloaded.load(n);bomb.discard();h.getLevel().addFreshEntity(reloaded);var saved=k.saveWithoutId(new CompoundTag());saved.putLong("KiteLast",h.getLevel().getGameTime()-20);k.load(saved);});
        h.runAfterDelay(285,()->{h.assertTrue(k.skillId()==0&&k.bombs().isEmpty()&&c.getHealth()==1000,"Reloaded projectile is spent and missed server clock cancels original volley");h.succeed();});
    }
    @GameTest(template="cauldron_pit_test",timeoutTicks=450,batch="wood_kite")
    public static void unloadIsReservationOnlyConfirmedDeathUnlocksOnePersistentRope(GameTestHelper h){
        var k=caster(h);var state=StargazerPlatformState.get(h.getLevel());var site=state.platforms.get(k.arenaCentre().asLong());
        h.runAfterDelay(8,()->{var n=k.saveWithoutId(new CompoundTag());k.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);h.assertTrue(site.boss!=null&&!site.defeated&&!StargazerPlatforms.summon(h.getLevel(),site),"Unloaded bird keeps its UUID reservation");var restored=own(h,WoodKiteContent.KITE.get().create(h.getLevel()));restored.load(n);restored.setNoAi(true);h.getLevel().addFreshEntity(restored);restored.hurt(restored.damageSources().genericKill(),10000);h.assertTrue(site.defeated&&site.boss==null,"Only actual matching-UUID death unlocks reward state");});
        h.runAfterDelay(235,()->{StargazerPlatforms.extendRope(h.getLevel(),site,12);h.assertTrue(h.getLevel().getBlockState(site.centre.below()).is(WoodKiteContent.ROPE.get()),"Central reward rope actually replaces its own socket after220-tick death");var loaded=StargazerPlatformState.load(state.save(new CompoundTag()));h.assertTrue(loaded.platforms.get(site.centre.asLong()).defeated&&!StargazerPlatforms.summon(h.getLevel(),site),"Victory is saved and cannot summon duplicate boss");h.succeed();});
    }
    @GameTest(template="cauldron_pit_test",timeoutTicks=40,batch="wood_kite")
    public static void dropsHaveRealOtherHandRepairAndConsumableSlowFalling(GameTestHelper h){
        var k=caster(h);var p=player(h,k);var sword=new ItemStack(Items.IRON_SWORD);sword.setDamageValue(200);p.setItemInHand(InteractionHand.OFF_HAND,sword);p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(WoodKiteContent.CORE.get()));
        WoodKiteContent.CORE.get().use(h.getLevel(),p,InteractionHand.MAIN_HAND);h.assertTrue(sword.getDamageValue()==20&&p.getMainHandItem().isEmpty(),"One actual core repairs180durability in the other hand");
        p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(WoodKiteContent.FEATHER.get()));WoodKiteContent.FEATHER.get().use(h.getLevel(),p,InteractionHand.MAIN_HAND);
        h.assertTrue(p.hasEffect(net.minecraft.world.effect.MobEffects.SLOW_FALLING)&&p.getMainHandItem().isEmpty(),"One feather grants actual120-tick Slow Falling");h.succeed();
    }
    private WoodKiteGameTests(){}
}
