package com.dynasty.expansion;

import com.dynasty.DynastyBlocks;
import com.dynasty.block.OilFueledBlock;
import com.mojang.authlib.GameProfile;
import java.util.*;
import net.minecraft.core.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.*;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.*;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty_cod4") @PrefixGameTestTemplate(false)
public final class OilFuelGameTests {
    private static final List<ServerPlayer> PLAYERS=new ArrayList<>();
    private static long oldDay;
    private static ServerPlayer player(GameTestHelper h,BlockPos at,boolean registered){
        var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"oil-native"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.setPos(Vec3.atBottomCenterOf(at));p.setNoGravity(true);
        p.getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.MAX_HEALTH).setBaseValue(500);p.setHealth(500);
        p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(ExpansionContent.item("lantern_oil"),5));
        if(registered){h.getLevel().addNewPlayer(p);PLAYERS.add(p);}return p;
    }
    @BeforeBatch(batch="cod4_oil_night") public static void nightSetup(net.minecraft.server.level.ServerLevel level){oldDay=level.getDayTime();level.setDayTime(6000);level.updateSkyBrightness();}
    @AfterBatch(batch="cod4_oil_night") public static void nightCleanup(net.minecraft.server.level.ServerLevel level){level.setDayTime(oldDay);level.updateSkyBrightness();PLAYERS.forEach(Entity::discard);PLAYERS.clear();}
    @AfterBatch(batch="cod4_oil_cleanse") public static void cleanseCleanup(net.minecraft.server.level.ServerLevel level){PLAYERS.forEach(Entity::discard);PLAYERS.clear();}
    private static void use(GameTestHelper h,ServerPlayer p,BlockPos at,InteractionHand hand){var s=h.getLevel().getBlockState(at);s.getBlock().use(s,h.getLevel(),at,p,hand,new BlockHitResult(Vec3.atCenterOf(at),Direction.UP,at,false));}
    private static BlockState state(GameTestHelper h,BlockPos at){return h.getLevel().getBlockState(at);}
    @GameTest(template="bow_ritual_test",batch="cod4_oil_input",setupTicks=20)
    public static void actualInputPaidBoundedFuelNativeStateReloadLegacyDefaultAndOnceReserveRefund(GameTestHelper h){
        var at=h.absolutePos(new BlockPos(4,2,4));var block=DynastyBlocks.INCENSE_BURNER.get();h.getLevel().setBlock(at,block.defaultBlockState(),3);var p=player(h,at.east(),false);
        try{
            p.setItemInHand(InteractionHand.OFF_HAND,new ItemStack(ExpansionContent.item("lantern_oil"),2));use(h,p,at,InteractionHand.OFF_HAND);h.assertTrue(state(h,at).getValue(OilFueledBlock.FUEL)==0&&p.getOffhandItem().getCount()==2,"Offhand cannot duplicate fuel input");
            use(h,p,at,InteractionHand.MAIN_HAND);h.getLevel().setBlock(at,state(h,at).setValue(OilFueledBlock.BURN_STEP,37),3);
            use(h,p,at,InteractionHand.MAIN_HAND);use(h,p,at,InteractionHand.MAIN_HAND);use(h,p,at,InteractionHand.MAIN_HAND);
            h.assertTrue(p.getMainHandItem().getCount()==2&&state(h,at).getValue(OilFueledBlock.FUEL)==3&&state(h,at).getValue(OilFueledBlock.BURN_STEP)==37,"Exactly three paid native inputs, full lamp rejects payment and refueling preserves elapsed burn");
            var encoded=NbtUtils.writeBlockState(state(h,at));var restored=NbtUtils.readBlockState(h.getLevel().holderLookup(net.minecraft.core.registries.Registries.BLOCK),encoded);
            h.assertTrue(restored.equals(state(h,at)),"Native saved block state preserves remaining fuel and elapsed time");
            for(String id:List.of("incense_burner","imperial_lantern")){var legacy=new CompoundTag();legacy.putString("Name","dynasty:"+id);var old=NbtUtils.readBlockState(h.getLevel().holderLookup(net.minecraft.core.registries.Registries.BLOCK),legacy);h.assertTrue(old.getValue(OilFueledBlock.FUEL)==0&&old.getValue(OilFueledBlock.BURN_STEP)==0,"Old ID-only block state migrates to zero fuel without inventing paid reserves");}
            // Native block destruction calls real onRemove; only queued unburned units return.
            h.getLevel().destroyBlock(at,false);h.getLevel().destroyBlock(at,false);
            h.runAfterDelay(3,()->{var drops=h.getLevel().getEntitiesOfClass(ItemEntity.class,new AABB(at).inflate(2),e->e.getItem().is(ExpansionContent.item("lantern_oil")));h.assertTrue(drops.stream().mapToInt(e->e.getItem().getCount()).sum()==2,"Actual repeated demolition refunds exactly two queued units once, current burning unit spent");drops.forEach(Entity::discard);h.succeed();});
        }finally{p.discard();}
    }
    @GameTest(template="bow_ritual_test",batch="cod4_oil_cleanse",setupTicks=20,timeoutTicks=1400)
    public static void actualScheduledIncenseTicksCleanseNearNotFarBurnOneMinuteAndRestoreOriginalLight(GameTestHelper h){
        var at=h.absolutePos(new BlockPos(4,3,4));var block=DynastyBlocks.INCENSE_BURNER.get();h.getLevel().setBlock(at,block.defaultBlockState(),3);
        var near=player(h,at.east(2),true);var far=player(h,at.east(9),true);
        h.startSequence().thenWaitUntil(()->h.assertTrue(h.getLevel().getEntity(near.getUUID())==near&&h.getLevel().getEntity(far.getUUID())==far,"Actual server players are entity-visible"))
        .thenExecute(()->{
            h.assertTrue(state(h,at).getLightEmission(h.getLevel(),at)==5,"Original incense light retained before oil");
            for(var p:List.of(near,far)){p.addEffect(new MobEffectInstance(ExpansionEffects.YIN.get(),2400));p.addEffect(new MobEffectInstance(ExpansionEffects.SOUL.get(),2400));}
            use(h,near,at,InteractionHand.MAIN_HAND);h.assertTrue(near.getMainHandItem().getCount()==4&&state(h,at).getLightEmission(h.getLevel(),at)==15,"Native input consumes one oil and activates brighter existing block");
            h.runAfterDelay(25,()->{
                h.assertTrue(state(h,at).getValue(OilFueledBlock.BURN_STEP)>0&&!near.hasEffect(ExpansionEffects.YIN.get())&&!near.hasEffect(ExpansionEffects.SOUL.get())&&far.hasEffect(ExpansionEffects.YIN.get())&&far.hasEffect(ExpansionEffects.SOUL.get()),"Actual native scheduled world tick burns and cleanses only within real radius");
            });
            h.runAfterDelay(1210,()->{
                h.assertTrue(state(h,at).getValue(OilFueledBlock.FUEL)==0&&state(h,at).getValue(OilFueledBlock.BURN_STEP)==0&&state(h,at).getLightEmission(h.getLevel(),at)==5,"Actual minute of server scheduled ticks exhausts one unit and restores original light");near.addEffect(new MobEffectInstance(ExpansionEffects.YIN.get(),400));
                h.runAfterDelay(25,()->{h.assertTrue(near.hasEffect(ExpansionEffects.YIN.get()),"Exhausted oil cannot leave a permanent cleanse clock");near.discard();far.discard();h.succeed();});
            });
        });
    }
    @GameTest(template="bow_ritual_test",batch="cod4_oil_night",setupTicks=20,timeoutTicks=1400)
    public static void originalLanternBaseLightDayPauseNightScheduledFieldAndFiniteFuel(GameTestHelper h){
        var at=h.absolutePos(new BlockPos(4,3,4));var block=DynastyBlocks.IMPERIAL_LANTERN.get();h.getLevel().setBlock(at,block.defaultBlockState(),3);
        var near=player(h,at.east(2),true);var far=player(h,at.east(9),true);
        h.startSequence().thenWaitUntil(()->h.assertTrue(h.getLevel().getEntity(near.getUUID())==near&&h.getLevel().getEntity(far.getUUID())==far,"Actual server players visible before testing nighttime field"))
        .thenExecute(()->{
            h.assertTrue(state(h,at).getLightEmission(h.getLevel(),at)==15,"Original permanent palace lamp lighting retained");use(h,near,at,InteractionHand.MAIN_HAND);
            h.runAfterDelay(25,()->{
                h.assertTrue(state(h,at).getValue(OilFueledBlock.BURN_STEP)==0&&!near.hasEffect(MobEffects.NIGHT_VISION),"Native daytime schedule pauses fuel and night field");h.getLevel().setDayTime(18000);h.getLevel().updateSkyBrightness();
                h.runAfterDelay(25,()->h.assertTrue(state(h,at).getValue(OilFueledBlock.BURN_STEP)>0&&near.hasEffect(MobEffects.NIGHT_VISION)&&!far.hasEffect(MobEffects.NIGHT_VISION),"Actual native nighttime schedule powers finite nearby night vision, not distant players"));
                h.runAfterDelay(1210,()->{h.assertTrue(state(h,at).getValue(OilFueledBlock.FUEL)==0&&state(h,at).getLightEmission(h.getLevel(),at)==15,"Oil burns out after real scheduled minute while original base light survives");near.discard();far.discard();h.succeed();});
            });
        });
    }
}
