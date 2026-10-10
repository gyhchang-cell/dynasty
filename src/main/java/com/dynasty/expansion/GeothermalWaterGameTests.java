package com.dynasty.expansion;

import java.util.*;
import net.minecraft.core.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty_cod4") @PrefixGameTestTemplate(false)
public final class GeothermalWaterGameTests {
    private static void pool(GameTestHelper h,int center,boolean heated){
        for(int x=center-2;x<=center+2;x++)for(int z=5;z<=11;z++)for(int y=49;y<=54;y++){
            var state=y==49||x==center-2||x==center+2||z==5||z==11?Blocks.STONE.defaultBlockState():y<=52?Blocks.WATER.defaultBlockState():Blocks.AIR.defaultBlockState();
            if(heated&&x==center&&z==8&&y==49)state=Blocks.MAGMA_BLOCK.defaultBlockState();h.getLevel().setBlock(h.absolutePos(new BlockPos(x,y,z)),state,18);
        }
    }
    private static Cow wet(GameTestHelper h,int x){
        var feet=Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(x,51,8)));var cow=h.spawn(EntityType.COW,new BlockPos(x,51,8));cow.setNoAi(true);cow.setNoGravity(true);
        cow.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST,200));ExpansionEffects.apply(cow,ExpansionEffects.FROST,200);
        h.onEachTick(()->{if(!cow.isRemoved()){cow.setPos(feet);cow.setDeltaMovement(Vec3.ZERO);}});return cow;
    }
    @GameTest(template="bow_ritual_test",batch="cod4_geothermal_water",setupTicks=20,timeoutTicks=80)
    public static void nativeWarmWaterRelievesOnlyOriginalFrostAndRestoresItsOriginalAttributeWhilePlainWaterKeepsCold(GameTestHelper h){
        pool(h,4,false);pool(h,11,true);var cold=wet(h,4);var hot=wet(h,11);double ordinary=cold.getAttribute(Attributes.MOVEMENT_SPEED).getBaseValue();
        h.assertTrue(cold.getAttributeValue(Attributes.MOVEMENT_SPEED)<ordinary&&hot.hasEffect(ExpansionEffects.FROST.get()),"Original native frost initially exists and slows both real actors");
        h.runAfterDelay(35,()->{try{
            h.assertTrue(cold.tickCount>=20&&hot.tickCount>=20&&cold.isInWater()&&hot.isInWater(),"Real native world ticks and fluid intersection drive relief, not synthetic status callbacks");
            h.assertTrue(cold.hasEffect(ExpansionEffects.FROST.get())&&cold.getAttributeValue(Attributes.MOVEMENT_SPEED)<ordinary,"Unheated ordinary water does not clear frost or its original slow");
            h.assertTrue(!hot.hasEffect(ExpansionEffects.FROST.get())&&Math.abs(hot.getAttributeValue(Attributes.MOVEMENT_SPEED)-ordinary)<1e-8&&hot.hasEffect(MobEffects.DAMAGE_BOOST)&&!hot.isOnFire(),"Actually submerged native magma bath removes only original frost, restores its existing attribute and preserves other effects without burning actor");h.succeed();
        }finally{cold.discard();hot.discard();}});
    }
    @GameTest(template="bow_ritual_test",batch="cod4_geothermal_connection",setupTicks=20,timeoutTicks=80)
    public static void nativeStoneBarrierRejectsNearbyHeatUntilActualWaterIsConnectedAndRemovingHeatStopsRelief(GameTestHelper h){
        pool(h,4,false);pool(h,8,true);var cold=wet(h,4);var warmFeet=h.absolutePos(new BlockPos(8,51,8));
        h.runAfterDelay(25,()->{
            h.assertTrue(cold.hasEffect(ExpansionEffects.FROST.get())&&!GeothermalWater.warm(h.getLevel(),cold.blockPosition())&&GeothermalWater.warm(h.getLevel(),warmFeet),"Real stone/air-separated water cannot claim an adjacent pool's heat");
            for(int x=5;x<=7;x++)for(int y=50;y<=52;y++)h.getLevel().setBlock(h.absolutePos(new BlockPos(x,y,8)),Blocks.WATER.defaultBlockState(),18);
        });
        h.runAfterDelay(50,()->{try{
            h.assertTrue(!cold.hasEffect(ExpansionEffects.FROST.get())&&GeothermalWater.warm(h.getLevel(),cold.blockPosition()),"Only physical connected water opens original frost relief");
            h.getLevel().setBlock(h.absolutePos(new BlockPos(8,49,8)),Blocks.STONE.defaultBlockState(),18);
            h.assertTrue(!GeothermalWater.warm(h.getLevel(),cold.blockPosition()),"Heat-source removal immediately invalidates bath; no saved scenery flag caches a false warm state");h.succeed();
        }finally{cold.discard();}});
    }
    @GameTest(template="bow_ritual_test",batch="cod4_geothermal_unloaded",setupTicks=20,timeoutTicks=60)
    public static void nativeWaterAtLoadedChunkEdgeNeverLoadsNeighborAndDryMagmaCannotMasqueradeAsSpring(GameTestHelper h){
        var base=new ChunkPos(h.absolutePos(BlockPos.ZERO));var owner=new ChunkPos(base.x+2048,base.z+2048);var neighbor=new ChunkPos(owner.x+1,owner.z);var at=new BlockPos(owner.getMinBlockX()+15,160,owner.getMinBlockZ()+8);h.getLevel().getChunk(owner.x,owner.z);
        h.assertTrue(h.getLevel().getChunkSource().getChunkNow(neighbor.x,neighbor.z)==null,"Actual neighboring native chunk begins unloaded");h.getLevel().setBlock(at,Blocks.WATER.defaultBlockState(),18);h.getLevel().setBlock(at.below(),Blocks.STONE.defaultBlockState(),18);
        h.assertTrue(!GeothermalWater.warm(h.getLevel(),at)&&h.getLevel().getChunkSource().getChunkNow(neighbor.x,neighbor.z)==null,"Bounded native water search refuses unknown heat and does not force neighbor load");
        h.getLevel().setBlock(at,Blocks.AIR.defaultBlockState(),18);h.getLevel().setBlock(at.below(),Blocks.MAGMA_BLOCK.defaultBlockState(),18);h.assertTrue(!GeothermalWater.warm(h.getLevel(),at),"Dry heat source is not a water bath");
        h.getLevel().setBlock(at,Blocks.WATER.defaultBlockState(),18);h.assertTrue(GeothermalWater.warm(h.getLevel(),at)&&h.getLevel().getChunkSource().getChunkNow(neighbor.x,neighbor.z)==null,"Real loaded shallow water touches submerged native heat without loading the neighbor");h.succeed();
    }
    private GeothermalWaterGameTests(){}
}
