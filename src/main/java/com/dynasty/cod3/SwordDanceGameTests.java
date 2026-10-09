package com.dynasty.cod3;

import com.dynasty.expansion.*;
import com.mojang.authlib.GameProfile;
import net.minecraft.core.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.item.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.*;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.gametest.*;
import java.util.*;

@GameTestHolder("dynasty_cod4") @PrefixGameTestTemplate(false)
public final class SwordDanceGameTests {
    private static final String KEY="site_sword_scar_wall";
    private static final List<ServerPlayer> PLAYERS=new ArrayList<>();
    private static final Set<UUID> DUMMIES=new HashSet<>();
    private static Long originalDay;
    private static Boolean originalRain,originalThunder;
    private static float originalRainLevel,originalThunderLevel;
    private static BlockPos room(GameTestHelper h){
        if(originalDay==null){originalDay=h.getLevel().getDayTime();originalRain=h.getLevel().isRaining();originalThunder=h.getLevel().isThundering();originalRainLevel=h.getLevel().getRainLevel(1);originalThunderLevel=h.getLevel().getThunderLevel(1);}
        h.getLevel().setDayTime(18000);h.getLevel().setWeatherParameters(10000,0,false,false);h.getLevel().setRainLevel(0);h.getLevel().setThunderLevel(0);h.getLevel().updateSkyBrightness();
        for(int x=0;x<=8;x++)for(int z=0;z<=8;z++){h.setBlock(new BlockPos(x,1,z),Blocks.STONE);var column=h.absolutePos(new BlockPos(x,2,z));for(int y=column.getY();y<h.getLevel().getMaxBuildHeight();y++)h.getLevel().setBlock(new BlockPos(column.getX(),y,column.getZ()),Blocks.AIR.defaultBlockState(),2);}
        var at=h.absolutePos(new BlockPos(3,2,3));h.getLevel().setBlockAndUpdate(at,SmallInteractions.ENTRIES.get("sword_scar_wall").get().defaultBlockState());return at;
    }
    private static ServerPlayer player(GameTestHelper h,BlockPos at){return player(h,at,new GameProfile(UUID.randomUUID(),"dance-native"));}
    private static ServerPlayer player(GameTestHelper h,BlockPos at,GameProfile profile){var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),profile);p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);p.setPos(Vec3.atBottomCenterOf(at.south(2)));p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.IRON_SWORD));for(int i=0;i<3;i++){p.tick();p.doTick();}PLAYERS.add(p);return p;}
    private static void moonlight(GameTestHelper h,ServerPlayer p,BlockPos at,Runnable body){
        h.startSequence().thenWaitUntil(()->h.assertTrue(SwordDance.context(p,at),"Native moonlight/lighting readiness: sky="+h.getLevel().getBrightness(net.minecraft.world.level.LightLayer.SKY,p.blockPosition().above())+", night="+h.getLevel().isNight()+", rain="+h.getLevel().isRainingAt(p.blockPosition())+", pos="+p.position())).thenExecute(body);
    }
    private static void tick(ServerPlayer p){p.tick();p.doTick();}
    private static void use(GameTestHelper h,ServerPlayer p,BlockPos at){h.getLevel().getBlockState(at).use(h.getLevel(),p,InteractionHand.MAIN_HAND,new BlockHitResult(Vec3.atCenterOf(at),Direction.UP,at,false));}
    private static void ready(ServerPlayer p){var n=EquipmentBehaviors.saved(p);n.putLong(KEY+"_start",p.level().getGameTime()-2400);n.putLong(KEY+"_next",p.level().getGameTime());}
    private static void cut(ServerPlayer p,int stage){p.setYRot(stage<2?180:-90);p.move(MoverType.SELF,stage==0?new Vec3(.6,0,0):stage==1?new Vec3(-.6,0,0):new Vec3(0,0,-.6));p.swing(InteractionHand.MAIN_HAND);tick(p);}
    private static void rest(ServerPlayer p){for(int i=0;i<8;i++)tick(p);}
    @AfterBatch(batch="cod4_sword_dance") public static void cleanup(net.minecraft.server.level.ServerLevel l){
        for(var p:PLAYERS){SwordDance.logout(new PlayerEvent.PlayerLoggedOutEvent(p));p.discard();}PLAYERS.clear();for(var id:DUMMIES){var e=l.getEntity(id);if(e!=null)e.discard();}DUMMIES.clear();if(originalDay!=null){l.setDayTime(originalDay);l.setWeatherParameters(10000,originalRain?10000:0,originalRain,originalThunder);l.setRainLevel(originalRainLevel);l.setThunderLevel(originalThunderLevel);l.updateSkyBrightness();originalDay=null;}
    }
    @GameTest(template="bow_ritual_test",batch="cod4_sword_dance",setupTicks=20,timeoutTicks=300)
    public static void repeatedRightClicksStationaryAndWrongFacingCannotManufactureDance(GameTestHelper h){
        var at=room(h);var p=player(h,at);moonlight(h,p,at,()->{use(h,p,at);var root=EquipmentBehaviors.saved(p);h.assertTrue(root.getLong(KEY+"_next")==h.getLevel().getGameTime()+800&&SwordDance.state(p).getInt("Count")==0,"Original interval/focus: root="+root+", night="+h.getLevel().isNight()+", skylight="+h.getLevel().getBrightness(net.minecraft.world.level.LightLayer.SKY,p.blockPosition().above())+", sky="+h.getLevel().canSeeSky(p.blockPosition().above())+", rain="+h.getLevel().isRainingAt(p.blockPosition())+", context="+SwordDance.context(p,at));
        for(int i=0;i<20;i++)use(h,p,at);ready(p);p.setYRot(180);p.swing(InteractionHand.MAIN_HAND);tick(p);h.assertTrue(SwordDance.state(p).getInt("Count")==0&&!SecretTracker.swordDanceClaimed(p),"Twenty real uses and an actual stationary sword swing do not count as movement choreography");rest(p);
        p.move(MoverType.SELF,new Vec3(.6,0,0));p.setYRot(180);p.swing(InteractionHand.OFF_HAND);tick(p);h.assertTrue(SwordDance.state(p).getInt("Count")==0,"Actual off-hand swing does not impersonate main-hand sword input");rest(p);
        p.move(MoverType.SELF,new Vec3(.6,0,0));p.setYRot(0);p.swing(InteractionHand.MAIN_HAND);tick(p);h.assertTrue(SwordDance.state(p).getInt("Count")==0,"Actual wrong-facing swing resets only native choreography");rest(p);
        p.move(MoverType.SELF,new Vec3(.6,0,0));p.setYRot(180);tick(p);h.assertTrue(SwordDance.state(p).getInt("Count")==0,"Actual movement/facing without a fresh swing cannot award a step");h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",batch="cod4_sword_dance",setupTicks=20,timeoutTicks=300)
    public static void actualGroundedNativeAirSwingsMatchThreeStepsAndOriginalRewards(GameTestHelper h){
        var at=room(h);var p=player(h,at);moonlight(h,p,at,()->{use(h,p,at);ready(p);var dummy=new net.minecraft.world.entity.monster.Zombie(h.getLevel());dummy.setPos(p.position().add(2,0,0));dummy.setNoAi(true);h.getLevel().addFreshEntity(dummy);DUMMIES.add(dummy.getUUID());float hp=dummy.getHealth();
        long begin=h.getTick();for(int i=0;i<3;i++){int stage=i;h.runAtTickTime(begin+1+i*10,()->{
            rest(p);EquipmentBehaviors.saved(p).putLong(KEY+"_next",h.getLevel().getGameTime());cut(p,stage);
            h.assertTrue(SwordDance.state(p).getInt("Count")==stage+1,"Actual native MoverType.SELF + main-hand swing after native grounded physics advances one step: stage="+stage+", onGround="+p.onGround()+", pos="+p.position()+", native="+SwordDance.state(p));
            h.assertTrue(EquipmentBehaviors.saved(p).getLong(KEY+"_next")==h.getLevel().getGameTime()+800,"Original eight-hundred-tick stage interval is not shortened");
            if(stage<2)h.assertTrue(!SecretTracker.swordDanceClaimed(p)&&p.getInventory().countItem(ExpansionContent.item("jade"))==0,"Partial real sword dance cannot grant reward");else{
                h.assertTrue(SecretTracker.swordDanceClaimed(p)&&EquipmentBehaviors.saved(p).getBoolean(KEY+"_done")&&p.getInventory().countItem(ExpansionContent.item("jade"))==1&&p.getInventory().countItem(ExpansionContent.item("copper_coin"))==2,"Native original secret 28 gives one jade; original two Site coins and completed task remain");
                var adv=p.server.getAdvancements().getAdvancement(new net.minecraft.resources.ResourceLocation("dynasty","cod4_sword_scar_wall"));h.assertTrue(p.getAdvancements().getOrStartProgress(adv).isDone()&&dummy.getHealth()==hp,"Actual original task advances and air-dance never manufactures damage on a nearby target");dummy.discard();use(h,p,at);h.assertTrue(p.getInventory().countItem(ExpansionContent.item("jade"))==1&&p.getInventory().countItem(ExpansionContent.item("copper_coin"))==2,"Repeated discovery never replays rewards");h.succeed();
            }
        });}
        });
    }
    @GameTest(template="bow_ritual_test",batch="cod4_sword_dance",setupTicks=20,timeoutTicks=300)
    public static void genuineMoonlightWeaponAndPhysicalSiteAreRequired(GameTestHelper h){
        var at=room(h);var p=player(h,at);moonlight(h,p,at,()->{h.getLevel().setDayTime(6000);h.getLevel().updateSkyBrightness();h.assertTrue(!SwordDance.open(p,at),"Daytime is not actual moonlight");h.getLevel().setDayTime(18000);h.getLevel().updateSkyBrightness();var roof=p.blockPosition().above(3);h.getLevel().setBlockAndUpdate(roof,Blocks.STONE.defaultBlockState());h.assertTrue(!SwordDance.open(p,at),"Roofed scene cannot manufacture moonlight");h.getLevel().setBlockAndUpdate(roof,Blocks.AIR.defaultBlockState());h.getLevel().setWeatherParameters(0,10000,true,false);h.getLevel().setRainLevel(1);h.assertTrue(!SwordDance.open(p,at),"Actual rain is not clear moonlight");h.getLevel().setWeatherParameters(10000,0,false,false);h.getLevel().setRainLevel(0);h.getLevel().updateSkyBrightness();use(h,p,at);ready(p);
        p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.BOW));tick(p);h.assertTrue(!SwordDance.state(p).getBoolean("DanceFocused")&&!SecretTracker.swordDanceClaimed(p),"Weapon swap releases active pose/guide ownership rather than retaining a stale sword");p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.IRON_SWORD));use(h,p,at);h.getLevel().setBlockAndUpdate(at,Blocks.STONE.defaultBlockState());tick(p);h.assertTrue(!SwordDance.state(p).getBoolean("DanceFocused")&&!SecretTracker.get(h.getLevel()).claim(p,28,at),"Removed Site/old generic counters are not fresh native dance proof");h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",batch="cod4_sword_dance",setupTicks=20,timeoutTicks=300)
    public static void finalRealSwingCannotBypassOriginalTwoMinuteDeadline(GameTestHelper h){
        var at=room(h);var p=player(h,at);moonlight(h,p,at,()->{use(h,p,at);EquipmentBehaviors.saved(p).putLong(KEY+"_start",h.getLevel().getGameTime()-1600);long begin=h.getTick();
            for(int i=0;i<3;i++){int stage=i;h.runAtTickTime(begin+1+i*10,()->{rest(p);EquipmentBehaviors.saved(p).putLong(KEY+"_next",h.getLevel().getGameTime());cut(p,stage);
                if(stage<2)h.assertTrue(SwordDance.state(p).getInt("Count")==stage+1,"Original physical first two forms are real, not a prefilled readiness flag");else{h.assertTrue(SwordDance.state(p).getInt("Count")==2&&!SecretTracker.swordDanceClaimed(p)&&!EquipmentBehaviors.saved(p).getBoolean(KEY+"_done")&&p.getInventory().countItem(ExpansionContent.item("jade"))==0,"Actual third movement/swing before original >=2400 ticks grants no final count, completion or reward");h.succeed();}
            });}
        });
    }
    @GameTest(template="bow_ritual_test",batch="cod4_sword_dance",setupTicks=20,timeoutTicks=300)
    public static void oldCompletionRequiresActualMissingDanceAndCloneNeverRepays(GameTestHelper h){
        var at=room(h);var p=player(h,at);moonlight(h,p,at,()->{var root=EquipmentBehaviors.saved(p);root.putBoolean(KEY+"_done",true);root.putInt(KEY+"_count",3);root.putLong(KEY+"_start",h.getLevel().getGameTime()-2400);root.putLong(KEY+"_next",h.getLevel().getGameTime()+8000);use(h,p,at);var other=player(h,at);use(h,other,at);
        h.assertTrue(!SecretTracker.swordDanceClaimed(p)&&SwordDance.state(p).getInt("Count")==0,"Old completed generic clicks do not forge missing choreography");
        long begin=h.getTick();for(int i=0;i<3;i++){int stage=i;h.runAtTickTime(begin+1+i*10,()->{rest(p);cut(p,stage);h.assertTrue(SwordDance.state(p).getInt("Count")==stage+1&&root.getInt(KEY+"_count")==3,"Actual legacy sequence preserves old three-count/done and skips obsolete long next window");if(stage==2){
            h.assertTrue(SecretTracker.swordDanceClaimed(p)&&p.getInventory().countItem(ExpansionContent.item("jade"))==1&&p.getInventory().countItem(ExpansionContent.item("copper_coin"))==0,"Only missing original secret reward is earned, never old Site coins");
            h.assertTrue(!SecretTracker.swordDanceClaimed(other)&&SwordDance.state(other).getInt("Count")==0,"Shared wall does not share another character's steps or claim; real network multiplayer remains pending");var q=player(h,at,p.getGameProfile());SecretTracker.clone(new PlayerEvent.Clone(q,p,true));use(h,q,at);h.assertTrue(SecretTracker.swordDanceClaimed(q)&&q.getInventory().countItem(ExpansionContent.item("jade"))==0&&!SwordDance.state(q).getBoolean("DanceFocused"),"Original persisted native claim survives death clone without rewards or active stale pose");h.succeed();
        }});}
        });
    }
}
