package com.dynasty.expansion;

import com.mojang.authlib.GameProfile;
import java.util.*;
import net.minecraft.core.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.*;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty_cod4") @PrefixGameTestTemplate(false)
public final class CropDustGameTests {
    private static BlockPos crop(GameTestHelper h){
        // Isolate physical AI/crops from the lower simultaneously running fixtures.
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=51;y<=57;y++)h.setBlock(x,y,z,y==51?Blocks.STONE:Blocks.AIR);
        var at=h.absolutePos(new BlockPos(4,52,8));h.getLevel().setBlock(at.below(),Blocks.FARMLAND.defaultBlockState().setValue(FarmBlock.MOISTURE,7),3);
        h.getLevel().setBlock(at,Blocks.WHEAT.defaultBlockState().setValue(CropBlock.AGE,4),3);return at;
    }
    private static ServerPlayer player(GameTestHelper h,BlockPos at,boolean registered){
        var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"crop-native"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);p.setPos(Vec3.atBottomCenterOf(at));p.setNoGravity(true);
        p.getAttribute(Attributes.MAX_HEALTH).setBaseValue(5000);p.setHealth(5000);p.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);p.getFoodData().setFoodLevel(17);p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(ExpansionContent.item("locust_dust"),5));
        if(registered){h.getLevel().addNewPlayer(p);h.onEachTick(()->{if(!p.isRemoved())p.doTick();});}return p;
    }
    private static SecondaryMob pest(GameTestHelper h,String id,BlockPos at){var m=SecondaryMobs.TYPES.get(id).get().create(h.getLevel());m.setPos(Vec3.atBottomCenterOf(at));h.getLevel().addFreshEntity(m);return m;}
    private static InteractionResult use(GameTestHelper h,ServerPlayer p,BlockPos at,InteractionHand hand){return p.gameMode.useItemOn(p,h.getLevel(),p.getItemInHand(hand),hand,new BlockHitResult(Vec3.atCenterOf(at),Direction.UP,at,false));}
    @GameTest(template="bow_ritual_test",batch="cod4_crop_flee",setupTicks=20,timeoutTicks=220)
    public static void actualNativeCropUseChargesOneAndOriginalFlyingGroundNavigationReallyFleesThenExpiresWithSavedData(GameTestHelper h){
        var at=crop(h);var p=player(h,at.west(),true);var bugs=new SecondaryMob[]{pest(h,"locust_swarm",at.east(3)),pest(h,"corpse_beetle",at.east(3).south(2))};
        h.startSequence().thenWaitUntil(()->{for(var m:bugs)h.assertTrue(m.tickCount>=3&&h.getLevel().getEntity(m.getUUID())==m,"Actual AI-on insect visible and ticking");})
        .thenExecute(()->{
            var oldCrop=h.getLevel().getBlockState(at);var oldSoil=h.getLevel().getBlockState(at.below());var start=new Vec3[]{bugs[0].position(),bugs[1].position()};
            h.assertTrue(use(h,p,at,InteractionHand.MAIN_HAND).consumesAction()&&p.getMainHandItem().getCount()==4,"Actual native use-on-crop consumes one real original dust");
            h.assertTrue(h.getLevel().getBlockState(at).equals(oldCrop)&&h.getLevel().getBlockState(at.below()).equals(oldSoil),"Native material action preserves crop age and soil moisture");
            use(h,p,at,InteractionHand.MAIN_HAND);h.assertTrue(p.getMainHandItem().getCount()==4,"Original item cooldown/active flee cannot duplicate payment");
            for(var m:bugs){
                var saved=m.saveWithoutId(new CompoundTag());h.assertTrue(saved.getInt("Cod4Flee")==SecondaryMob.CROP_FLEE_TICKS&&saved.getLong("Cod4CropFleeOrigin")==at.asLong()&&!m.isNoAi()&&!saved.getBoolean("Cod4Friendly"),"Original finite flee clock saves real crop origin, AI and allegiance retained");
                var reload=SecondaryMobs.TYPES.get(m.spec.id()).get().create(h.getLevel());reload.load(saved);var again=reload.saveWithoutId(new CompoundTag());h.assertTrue(again.getInt("Cod4Flee")==120&&again.getLong("Cod4CropFleeOrigin")==at.asLong()&&reload.getHealth()==m.getHealth(),"Native reload retains finite current state and original health");reload.discard();
            }
            h.runAfterDelay(40,()->{for(int i=0;i<2;i++){var m=bugs[i];h.assertTrue(!m.isNoAi()&&m.position().distanceToSqr(start[i])>1&&m.distanceToSqr(Vec3.atCenterOf(at))>start[i].distanceToSqr(Vec3.atCenterOf(at))+1,"Actual original native navigation moves both flying/ground insects away, no teleport: "+m.spec.id()+" "+start[i]+" -> "+m.position()+", ticks="+m.tickCount);}});
            h.runAfterDelay(135,()->{try{h.assertTrue(!p.getCooldowns().isOnCooldown(ExpansionContent.item("locust_dust")),"Actual native player ticking also expires original dust cooldown");for(var m:bugs){var saved=m.saveWithoutId(new CompoundTag());h.assertTrue(saved.getInt("Cod4Flee")==0&&!saved.contains("Cod4CropFleeOrigin")&&!saved.getBoolean("Cod4Friendly")&&!m.isNoAi()&&m.getAttributeValue(Attributes.ATTACK_DAMAGE)==m.spec.damage(),"Real native ticking expires paid flee and clears saved origin while original hostile stats remain");}h.succeed();}finally{for(var m:bugs)m.discard();p.discard();}});
        });
    }
    @GameTest(template="bow_ritual_test",batch="cod4_crop_controls",setupTicks=20,timeoutTicks=80)
    public static void actualInputRejectsNoAiWrongSpeciesWallRemoteOffhandAndSummonedActorsWithoutMaterialLoss(GameTestHelper h){
        var at=crop(h);var p=player(h,at.west(),false);var bug=pest(h,"venom_scorpion",at.east(4));bug.setNoAi(true);var wolf=pest(h,"gray_wolf",at.south(3));wolf.setNoAi(true);
        h.startSequence().thenWaitUntil(()->h.assertTrue(h.getLevel().getEntity(bug.getUUID())==bug&&bug.tickCount>1,"Actual no-AI negative actor is visible"))
        .thenExecute(()->{try{
            var state=h.getLevel().getBlockState(at);use(h,p,at,InteractionHand.MAIN_HAND);h.assertTrue(p.getMainHandItem().getCount()==5,"Native no-AI/wrong-species targets cannot consume crop powder");bug.setNoAi(false);
            for(int z=-1;z<=1;z++)for(int y=0;y<=3;y++)h.getLevel().setBlock(at.east(2).offset(0,y,z),Blocks.STONE.defaultBlockState(),3);
            use(h,p,at,InteractionHand.MAIN_HAND);h.assertTrue(p.getMainHandItem().getCount()==5&&bug.saveWithoutId(new CompoundTag()).getInt("Cod4Flee")==0,"Actual collision wall blocks crop-to-insect line without charge");
            for(int z=-1;z<=1;z++)for(int y=0;y<=3;y++)h.getLevel().setBlock(at.east(2).offset(0,y,z),Blocks.AIR.defaultBlockState(),3);
            p.setPos(Vec3.atBottomCenterOf(at.west(10)));use(h,p,at,InteractionHand.MAIN_HAND);h.assertTrue(p.getMainHandItem().getCount()==5,"Far native interaction cannot spend material or remotely repel");p.setPos(Vec3.atBottomCenterOf(at.west()));
            p.setItemInHand(InteractionHand.OFF_HAND,new ItemStack(ExpansionContent.item("locust_dust"),2));use(h,p,at,InteractionHand.OFF_HAND);h.assertTrue(p.getOffhandItem().getCount()==2&&p.getMainHandItem().getCount()==5,"Offhand cannot duplicate main-hand dust action");
            bug.getPersistentData().putUUID("cod4Summoner",p.getUUID());use(h,p,at,InteractionHand.MAIN_HAND);h.assertTrue(p.getMainHandItem().getCount()==5,"Original summoned/owned actors are protected, not free crop targets");bug.getPersistentData().remove("cod4Summoner");
            use(h,p,at.below(),InteractionHand.MAIN_HAND);h.assertTrue(p.getMainHandItem().getCount()==4&&h.getLevel().getBlockState(at).equals(state),"Actual original farmland use is reachable as well as crop and changes no plants");h.succeed();
        }finally{bug.discard();wolf.discard();p.discard();}});
    }
    @GameTest(template="bow_ritual_test",batch="cod4_crop_contact",setupTicks=20,timeoutTicks=220)
    public static void nativeLocustPhysicalContactStopsOnlyDuringPaidFleeAndOriginalBiteReturnsAfterTimeout(GameTestHelper h){
        var at=crop(h);var p=player(h,at,true);for(int i=0;i<61;i++)p.tick();var m=pest(h,"locust_swarm",at);
        h.startSequence().thenWaitUntil(()->h.assertTrue(h.getLevel().getEntity(m.getUUID())==m&&m.tickCount>=2&&m.touching(p),"Actual original swarm/player body contact visible"))
        .thenExecute(()->{
            h.assertTrue(use(h,p,at,InteractionHand.MAIN_HAND).consumesAction(),"One actual crop dust starts original flee state");float hp=p.getHealth();p.invulnerableTime=0;
            h.assertTrue(!m.contactAttack(p)&&!m.doHurtTarget(p)&&p.getHealth()==hp,"Paid native flee blocks body bite and an already queued native melee contact, not permanent damage/stat removal");
            h.runAfterDelay(135,()->{try{
                p.setPos(m.position());p.invulnerableTime=0;float before=p.getHealth();
                h.assertTrue(m.touching(p)&&m.contactAttack(p)&&p.getHealth()<before&&m.getAttributeValue(Attributes.ATTACK_DAMAGE)==m.spec.damage(),"Actual body contact after real finite timeout again applies original native bite/health loss");h.succeed();
            }finally{m.discard();p.discard();}});
        });
    }
}
