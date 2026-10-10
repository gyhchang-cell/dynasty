package com.dynasty.expansion;

import com.dynasty.dungeon.*;
import com.mojang.authlib.GameProfile;
import java.util.*;
import net.minecraft.core.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.*;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty_cod4") @PrefixGameTestTemplate(false)
public final class QimenMaterialGameTests {
    private static ItemStack item(String id,int count){return new ItemStack(ExpansionContent.item(id),count);}
    private static ServerPlayer player(GameTestHelper h,BlockPos pos){
        var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"qimen-native"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.setPos(Vec3.atBottomCenterOf(pos));return p;
    }
    @GameTest(template="bow_ritual_test",batch="cod4_qimen_material",setupTicks=20)
    public static void nativeMagpieInteractionRepairsOnlyMissingHealthAndKeepsOriginalActor(GameTestHelper h){
        var at=h.absolutePos(new BlockPos(4,2,4));var p=player(h,at.east());var mob=SecondaryMobs.TYPES.get("wooden_magpie").get().create(h.getLevel());mob.setPos(Vec3.atBottomCenterOf(at));mob.setNoAi(true);mob.setHealth(30);mob.setTarget(p);h.getLevel().addFreshEntity(mob);
        try{
            p.setItemInHand(InteractionHand.MAIN_HAND,item("qimen_cable",4));p.setItemInHand(InteractionHand.OFF_HAND,item("qimen_cable",2));
            mob.interact(p,InteractionHand.OFF_HAND);h.assertTrue(mob.getHealth()==30&&p.getOffhandItem().getCount()==2,"Off-hand repair cannot double-charge the same native click");
            for(float expected:new float[]{50,70,80}){mob.interact(p,InteractionHand.MAIN_HAND);h.assertTrue(mob.getHealth()==expected,"Actual existing actor heals twenty, clamped at its original maximum");}
            h.assertTrue(p.getMainHandItem().getCount()==1&&mob.getTarget()==p&&mob.getAttributeValue(net.minecraft.world.entity.ai.attributes.Attributes.ATTACK_DAMAGE)==150,"Three actual cables charged, original hostile target/damage retained; no duplicate tame/ownership system");
            mob.interact(p,InteractionHand.MAIN_HAND);h.assertTrue(p.getMainHandItem().getCount()==1,"Full-health actor cannot consume another repair cable");
            mob.setHealth(40);p.setPos(p.position().add(10,0,0));mob.interact(p,InteractionHand.MAIN_HAND);h.assertTrue(mob.getHealth()==40&&p.getMainHandItem().getCount()==1,"Far native interaction cannot repair or consume material");
            var saved=new CompoundTag();mob.save(saved);mob.load(saved);h.assertTrue(mob.getHealth()==40&&!saved.getBoolean("Cod4Friendly"),"Native save reload retains actual health and original allegiance");h.succeed();
        }finally{mob.discard();p.discard();}
    }
    @GameTest(template="bow_ritual_test",batch="cod4_qimen_bait",setupTicks=20,timeoutTicks=260)
    public static void realRatNavigationFindsVisibleGearConsumesOneAndNativeDeathReturnsExactSavedStack(GameTestHelper h){
        for(int lane=0;lane<2;lane++)for(int x=1;x<=12;x++)for(int z=6+lane*5;z<=10+lane*5;z++)for(int y=1;y<=4;y++)
            h.setBlock(x,y,z,y==1||z==6+lane*5||z==10+lane*5||x==1||x==12?Blocks.STONE:Blocks.AIR);
        for(int lane=0;lane<2;lane++)for(int z=7+lane*5;z<=9+lane*5;z++)for(int y=2;y<=4;y++)h.setBlock(7,y,z,Blocks.STONE);
        // Consecutive native IDs exercise both alternating Mob.serverAiStep scheduling phases.
        var rats=new SecondaryMob[]{SecondaryMobs.TYPES.get("clockwork_rat").get().create(h.getLevel()),SecondaryMobs.TYPES.get("clockwork_rat").get().create(h.getLevel())};
        h.assertTrue((rats[0].getId()&1)!=(rats[1].getId()&1),"Native pair covers both real AI scheduling parities");
        var baits=new ItemEntity[2];var starts=new Vec3[2];
        for(int lane=0;lane<2;lane++){
            var at=h.absolutePos(new BlockPos(3,2,8+lane*5));rats[lane].setPos(Vec3.atBottomCenterOf(at));h.getLevel().addFreshEntity(rats[lane]);starts[lane]=rats[lane].position();
            var gear=item("qimen_gear",2);gear.getOrCreateTag().putString("NativeBaitReceipt","exact-original-"+lane);var end=h.absolutePos(new BlockPos(9,2,8+lane*5));
            baits[lane]=new ItemEntity(h.getLevel(),end.getX()+.5,end.getY(),end.getZ()+.5,gear);baits[lane].setDeltaMovement(Vec3.ZERO);h.getLevel().addFreshEntity(baits[lane]);
        }
        h.startSequence().thenWaitUntil(()->{
            for(int i=0;i<2;i++)h.assertTrue(h.getLevel().getEntity(rats[i].getUUID())==rats[i]&&rats[i].tickCount>=3
                &&h.getLevel().getEntity(baits[i].getUUID())==baits[i],"Wait for both actual native rats and baits being entity-visible and ticking");
        }).thenExecute(()->{
            h.runAfterDelay(35,()->{
                for(int i=0;i<2;i++){var before=new CompoundTag();rats[i].addAdditionalSaveData(before);
                    h.assertTrue(!rats[i].isNoAi()&&ItemStack.of(before.getCompound("Cod4Stolen")).isEmpty()&&baits[i].getItem().getCount()==2,"Wall blocks bait attraction and remote inventory transfer for native phase "+i);}
                for(int lane=0;lane<2;lane++)for(int z=7+lane*5;z<=9+lane*5;z++)for(int y=2;y<=4;y++)h.setBlock(7,y,z,Blocks.AIR);
            });
            h.runAfterDelay(115,()->{
                var restored=new SecondaryMob[2];
                for(int i=0;i<2;i++){
                    var rat=rats[i];var saved=new CompoundTag();rat.save(saved);var stolen=ItemStack.of(saved.getCompound("Cod4Stolen"));
                    h.assertTrue(rat.position().distanceToSqr(starts[i])>4&&!rat.isNoAi()&&stolen.is(ExpansionContent.item("qimen_gear"))&&stolen.getCount()==1&&baits[i].getItem().getCount()==1,
                        "Actual native navigation reaches gear in both AI scheduling phases: phase="+i+", start="+starts[i]+", rat="+rat.position()+", ticks="+rat.tickCount+", id="+rat.getId()+", stolen="+stolen+", bait="+baits[i].getItem()+", baitPos="+baits[i].position()+", los="+rat.hasLineOfSight(baits[i])+", collisionFree="+h.getLevel().noCollision(rat)+", navDone="+rat.getNavigation().isDone()+", path="+rat.getNavigation().getPath()+", water="+rat.isInWater()+", target="+rat.getTarget()+", below="+h.getLevel().getBlockState(rat.blockPosition().below())+", barrier="+h.getBlockState(new BlockPos(7,2,8+i*5)));
                    rat.discard();restored[i]=SecondaryMobs.TYPES.get("clockwork_rat").get().create(h.getLevel());restored[i].load(saved);
                }
                h.runAfterDelay(3,()->{for(var rat:restored)h.getLevel().addFreshEntity(rat);
                    h.runAfterDelay(3,()->{try{
                        for(int i=0;i<2;i++){
                            var rat=restored[i];var marker="exact-original-"+i;var bait=baits[i];
                            h.assertTrue(rat.hurt(rat.damageSources().genericKill(),10000)&&rat.isDeadOrDying(),"Actual native death executes original theft return");
                            var returned=h.getLevel().getEntitiesOfClass(ItemEntity.class,rat.getBoundingBox().inflate(3),e->e!=bait&&e.getItem().is(ExpansionContent.item("qimen_gear"))&&e.getItem().hasTag()&&e.getItem().getTag().getString("NativeBaitReceipt").equals(marker));
                            h.assertTrue(returned.stream().mapToInt(e->e.getItem().getCount()).sum()==1&&bait.getItem().getCount()==1,"Native reloaded actor returns exactly one consumed gear with exact foreign NBT, not remaining bait or duplicate");
                            h.assertTrue(ItemStack.of(rat.saveWithoutId(new CompoundTag()).getCompound("Cod4Stolen")).isEmpty(),"Native death clears original stolen receipt");returned.forEach(Entity::discard);
                        }h.succeed();
                    }finally{for(var rat:restored)rat.discard();for(var bait:baits)bait.discard();}});
                });
            });
        });
    }
    private static DungeonMechanismBlockEntity marker(GameTestHelper h,BlockPos pos,net.minecraft.world.level.block.Block block,UUID instance,String mechanism,BlockPos core){
        h.getLevel().setBlock(pos,block.defaultBlockState(),3);var be=(DungeonMechanismBlockEntity)h.getLevel().getBlockEntity(pos);be.configure(instance,"qimen_qa",mechanism,core,-1,List.of());return be;
    }
    private static void use(GameTestHelper h,ServerPlayer p,BlockPos at){var state=h.getLevel().getBlockState(at);state.getBlock().use(state,h.getLevel(),at,p,InteractionHand.MAIN_HAND,new BlockHitResult(Vec3.atCenterOf(at),Direction.UP,at,false));}
    @GameTest(template="bow_ritual_test",batch="cod4_qimen_material",setupTicks=20)
    public static void actualBoundTrapChargesOnceSharesGearPersistsOriginalContactsAndRejectsForgedBinding(GameTestHelper h){
        var core=h.absolutePos(new BlockPos(2,2,2));var at=core.east(2);var other=at.south();var id=UUID.randomUUID();marker(h,core,DungeonContent.CORE.get(),id,"core",core);
        var trap=marker(h,at,DungeonContent.TRAP.get(),id,"arrow_qa",core);marker(h,other,DungeonContent.TRAP.get(),id,"arrow_qa",core);var p=player(h,at.east());var room=DungeonStateStore.get(h.getLevel()).room(id,"qimen_qa");var clock=room.hazard("arrow_qa",false);
        p.setItemInHand(InteractionHand.MAIN_HAND,item("qimen_gear",3));use(h,p,at);use(h,p,other);
        h.assertTrue(p.getMainHandItem().getCount()==2&&clock.warningGear()==5,"Native physical shared trap markers consume one real gear for one room-owned five-tick warning fitting");
        var store= DungeonStateStore.load(DungeonStateStore.get(h.getLevel()).save(new CompoundTag()));var copy=store.room(id,"qimen_qa").hazard("arrow_qa",false);
        h.assertTrue(copy.warningGear()==5&&!copy.fitWarningGear()&&copy.phase()==DungeonMechanism.Phase.IDLE,"Native SavedData reload retains fitting once without triggering or upgrading again");
        p.setItemInHand(InteractionHand.MAIN_HAND,item("qimen_cable",3));use(h,p,at);use(h,p,other);h.assertTrue(p.getMainHandItem().getCount()==2&&clock.phase()==DungeonMechanism.Phase.WARNING&&clock.duration()==25,"Actual paid cable triggers original clock once; busy shared marker does not charge again");
        long now=h.getLevel().getGameTime();for(int i=1;i<=24;i++){clock.tickActive(now+i);h.assertTrue(!clock.consumeContact(),"Original contact waits for the upgraded native tell");}clock.tickActive(now+25);h.assertTrue(clock.consumeContact()&&!clock.consumeContact()&&clock.duration()==6,"One original volley begins, original active duration retained");
        for(int i=26;i<=31;i++)clock.tickActive(now+i);h.assertTrue(clock.phase()==DungeonMechanism.Phase.RECOVERY&&clock.duration()==36,"Original recovery and all volley timing remain, no auto-solve or disabled trap");
        var snapshot=clock.save();h.assertTrue(snapshot.getInt("Active")==6&&snapshot.getInt("PulseTicks")==2&&snapshot.getInt("Recovery")==36,"Actual saved hazard preserves the original damage-contact cadence");
        trap.configure(UUID.randomUUID(),"qimen_qa","arrow_qa",core,-1,List.of());p.setItemInHand(InteractionHand.MAIN_HAND,item("qimen_gear",2));use(h,p,at);h.assertTrue(p.getMainHandItem().getCount()==2,"Different instance cannot charge or fit a forged core binding");
        trap.configure(id,"qimen_qa","arrow_qa",core.offset(200000,0,0),-1,List.of());int tickets=h.getLevel().getForcedChunks().size();use(h,p,at);h.assertTrue(p.getMainHandItem().getCount()==2&&h.getLevel().getForcedChunks().size()==tickets,"Missing/unloaded core is rejected without payment or forced chunk tickets");
        var max=new DungeonHazard(30,4,20);h.assertTrue(!max.fitWarningGear(),"Already maximum warning cannot consume a useless fitting");p.discard();h.succeed();
    }
}
