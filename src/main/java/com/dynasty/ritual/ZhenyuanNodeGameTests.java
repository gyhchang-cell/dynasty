package com.dynasty.ritual;

import com.dynasty.Dynasty;
import com.mojang.authlib.GameProfile;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.material.PushReaction;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.common.util.FakePlayer;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;
import java.util.UUID;

/** Isolated engine tests; no player-created world is used. */
@GameTestHolder(Dynasty.MODID)
@PrefixGameTestTemplate(false)
public final class ZhenyuanNodeGameTests {
    @GameTest(template="bow_ritual_test",timeoutTicks=60)
    public static void sceneLightingIsSparseAirOnlyAndRepeatable(GameTestHelper h) {
        var level=h.getLevel();var center=h.absolutePos(new BlockPos(0,30,0));
        for(int x=-30;x<=30;x++)for(int z=-30;z<=30;z++)
            level.setBlock(center.offset(x,-1,z),net.minecraft.world.level.block.Blocks.DEEPSLATE.defaultBlockState(),2);
        var protectedPos=center.offset(3,3,0);
        level.setBlock(protectedPos,net.minecraft.world.level.block.Blocks.DIAMOND_BLOCK.defaultBlockState(),2);
        var lights=ZhenyuanSceneLighting.mouth(level,center,java.util.List.of(center));
        h.assertTrue(lights.size()>10&&lights.size()<=42,"Sparse lighting count out of bounds: "+lights.size());
        for(var p:lights) {
            h.assertTrue(level.getBlockState(p).is(net.minecraft.world.level.block.Blocks.LIGHT),"Missing light block");
            int strength=level.getBlockState(p).getValue(net.minecraft.world.level.block.LightBlock.LEVEL);
            h.assertTrue(strength>=10&&strength<=11,"Overbright light");
            for(var q:lights)if(!p.equals(q))h.assertTrue(p.distSqr(q)>=49,"Lights too dense");
        }
        h.assertTrue(lights.equals(ZhenyuanSceneLighting.mouth(level,center,java.util.List.of(center))),"Reapplying changed light layout");
        h.assertTrue(level.getBlockState(protectedPos).is(net.minecraft.world.level.block.Blocks.DIAMOND_BLOCK),"Architecture was replaced");
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=30)
    public static void nodeNbtAndClientTagRoundTrip(GameTestHelper h) {
        BlockPos pos=h.absolutePos(new BlockPos(3,2,3)), core=pos.offset(8,0,5);
        for(int slot=0;slot<5;slot++) {
            var state=ZhenyuanRitualContent.NODE.get().defaultBlockState().setValue(ZhenyuanNodeBlock.SLOT,slot);
            var original=new ZhenyuanNodeBlockEntity(pos,state);
            original.configure(core,slot);
            original.syncRitual(21,1);
            var saved=original.saveWithoutMetadata();
            var restored=new ZhenyuanNodeBlockEntity(pos,state);
            restored.load(saved);
            h.assertTrue(restored.getCorePos().equals(core),"Core anchor must persist exactly");
            h.assertTrue(restored.getSlot()==slot,"Offering slot must persist");
            h.assertTrue(restored.getOfferingMask()==21 && restored.getStage()==1,"Offerings/stage must persist");
            var client=new ZhenyuanNodeBlockEntity(pos,state);
            client.handleUpdateTag(original.getUpdateTag());
            h.assertTrue(client.getCorePos().equals(core) && client.getSlot()==slot
                    && client.getOfferingMask()==21 && client.getStage()==1,"Client tag must retain the server ritual snapshot");
            client.load(new CompoundTag());
            h.assertTrue(client.getSlot()==slot,"Empty schematic NBT must retain the blockstate slot");
            h.assertTrue(client.getCorePos().equals(pos),"Missing anchor must default to own block");
        }
        var invalid=new CompoundTag();
        invalid.putInt("Slot",99);invalid.putInt("Stage",99);invalid.putInt("OfferingMask",255);
        var clamped=new ZhenyuanNodeBlockEntity(pos,ZhenyuanRitualContent.NODE.get().defaultBlockState());
        clamped.load(invalid);
        h.assertTrue(clamped.getSlot()==4 && clamped.getStage()==3 && clamped.getOfferingMask()==31,"Malformed values must be bounded");
        h.succeed();
    }

    @GameTest(template="bow_ritual_test",timeoutTicks=30)
    public static void lowShapesAreNotGlobeCollisionCubes(GameTestHelper h) {
        var pos=h.absolutePos(new BlockPos(3,2,3));
        for(int slot=0;slot<5;slot++) for(boolean active:new boolean[]{false,true}) {
            var state=ZhenyuanRitualContent.NODE.get().defaultBlockState().setValue(ZhenyuanNodeBlock.SLOT,slot)
                    .setValue(ZhenyuanNodeBlock.ACTIVE,active);
            var shape=state.getCollisionShape(h.getLevel(),pos);
            h.assertTrue(!shape.isEmpty(),"The pedestal must have real physical support");
            h.assertTrue(Math.abs(shape.bounds().maxY-(slot==4?.75:.50))<.0001,"Only low stone support is solid");
            h.assertTrue(shape.bounds().minY==0,"The base must rest on the floor");
            h.assertTrue(state.getShape(h.getLevel(),pos).bounds().equals(shape.bounds()),"Selection and collision must agree");
            h.assertTrue(state.getPistonPushReaction()==PushReaction.BLOCK,"Pistons must not split a registered ritual");
            h.assertTrue(state.getDestroySpeed(h.getLevel(),pos)<0,"Survival mining must not destroy the final-ritual node");
            h.assertTrue(Block.getDrops(state,h.getLevel(),pos,null).isEmpty(),"Scripted altar disappearance must not duplicate loot");
        }
        h.succeed();
    }

    @GameTest(template="bow_ritual_test",timeoutTicks=30)
    public static void configurationSynchronizesBlockStateWithoutReplacingNode(GameTestHelper h) {
        var pos=h.absolutePos(new BlockPos(4,2,4));
        h.getLevel().setBlockAndUpdate(pos,ZhenyuanRitualContent.NODE.get().defaultBlockState());
        var node=(ZhenyuanNodeBlockEntity)h.getLevel().getBlockEntity(pos);
        h.assertTrue(node!=null,"Placed node needs its registered block entity");
        node.configure(pos.offset(4,0,0),2);
        node.syncRitual(4,0);
        var state=h.getLevel().getBlockState(pos);
        h.assertTrue(state.getValue(ZhenyuanNodeBlock.SLOT)==2 && state.getValue(ZhenyuanNodeBlock.ACTIVE),"Slot and active state must reflect the node snapshot");
        h.assertTrue(h.getLevel().getBlockEntity(pos)==node,"State changes must preserve node identity and anchor");
        node.syncRitual(0,0);
        h.assertTrue(!h.getLevel().getBlockState(pos).getValue(ZhenyuanNodeBlock.ACTIVE),"Reset clears glow model as well as NBT");
        h.succeed();
    }

    @GameTest(template="bow_ritual_test",timeoutTicks=30)
    public static void offhandCannotSubmitAnOfferingTwice(GameTestHelper h) {
        var pos=h.absolutePos(new BlockPos(4,2,4));
        var block=ZhenyuanRitualContent.NODE.get();
        h.getLevel().setBlockAndUpdate(pos,block.defaultBlockState());
        var player=new FakePlayer(h.getLevel(),new GameProfile(UUID.randomUUID(),"zhenyuan-hand-test"));
        player.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.DIAMOND,3));
        player.setItemInHand(InteractionHand.OFF_HAND,new ItemStack(Items.EMERALD,2));
        var result=block.use(h.getLevel().getBlockState(pos),h.getLevel(),pos,player,InteractionHand.OFF_HAND,
                new BlockHitResult(Vec3.atCenterOf(pos),Direction.UP,pos,false));
        var node=(ZhenyuanNodeBlockEntity)h.getLevel().getBlockEntity(pos);
        h.assertTrue(result==InteractionResult.CONSUME,"Offhand branch must finish without dispatching a second interaction");
        h.assertTrue(player.getMainHandItem().getCount()==3 && player.getOffhandItem().getCount()==2,"No hand may be consumed by the offhand branch");
        h.assertTrue(node.getOfferingMask()==0,"Offhand cannot set offering progress");
        h.succeed();
    }
}
