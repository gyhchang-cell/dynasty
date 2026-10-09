package com.dynasty.workshop;

import com.dynasty.DynastyBlocks;
import com.dynasty.cod3.*;
import com.dynasty.expansion.ExpansionContent;
import com.mojang.authlib.GameProfile;
import java.util.UUID;
import net.minecraft.core.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.*;
import net.minecraft.world.phys.*;
import net.minecraftforge.gametest.*;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.entity.player.*;
import net.minecraftforge.common.capabilities.ForgeCapabilities;

@GameTestHolder("dynasty_cod4") @PrefixGameTestTemplate(false)
public final class SpriteJadeGameTests {
    private static ItemStack item(String id,int count){return new ItemStack(ExpansionContent.item(id),count);}
    private static ServerPlayer player(GameTestHelper h,BlockPos pos){
        var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"sprite-paid"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.setPos(Vec3.atCenterOf(pos).add(0,0,2));return p;
    }
    private static WorkshopBlockEntity station(GameTestHelper h,BlockPos pos){h.getLevel().setBlock(pos,DynastyBlocks.LAPIDARY_BENCH.get().defaultBlockState(),3);return (WorkshopBlockEntity)h.getLevel().getBlockEntity(pos);}
    @GameTest(template="bow_ritual_test",batch="cod4_sprite_material",setupTicks=20)
    public static void physicalLapidaryUseReloadAndDemolitionReturnExactPaidItems(GameTestHelper h){
        var pos=h.absolutePos(new BlockPos(3,2,3));var vat=station(h,pos);var p=player(h,pos);var block=vat.getBlockState().getBlock();
        for(var id:new String[]{"bamboo_slip","bamboo_slip","sprite_jade"}){
            var held=item(id,2);if(id.equals("sprite_jade"))held.getOrCreateTag().putString("ReceiptMark","original stone-sprite payment");
            p.setItemInHand(InteractionHand.MAIN_HAND,held);
            block.use(vat.getBlockState(),h.getLevel(),pos,p,InteractionHand.MAIN_HAND,new BlockHitResult(Vec3.atCenterOf(pos),Direction.UP,pos,false));
            h.assertTrue(held.getCount()==1,"Native block use consumes exactly one actual ordered ingredient");
            var saved=vat.saveWithoutMetadata();vat.load(saved);h.assertTrue(vat.deposited()>0,"Actual station NBT reload preserves payment");
        }
        h.assertTrue(vat.deposited()==3&&!vat.ready()&&!vat.accept(item("sprite_jade",1)),"Jade replaces only the crystal slot; it cannot replace ink or produce an incomplete output");
        h.assertTrue(p.gameMode.destroyBlock(pos)&&h.getLevel().getBlockState(pos).isAir(),"Native permitted demolition really removes the paid station");
        var drops=h.getLevel().getEntitiesOfClass(ItemEntity.class,new AABB(pos).inflate(1.5));
        int jade=0,slips=0,crystals=0;for(var entity:drops){var stack=entity.getItem();if(stack.is(ExpansionContent.item("sprite_jade"))){jade+=stack.getCount();h.assertTrue(stack.hasTag()&&stack.getTag().getString("ReceiptMark").equals("original stone-sprite payment"),"Refund preserves the actual paid item NBT");}if(stack.is(ExpansionContent.item("bamboo_slip")))slips+=stack.getCount();if(stack.is(ExpansionContent.item("dragon_crystal")))crystals+=stack.getCount();}
        h.assertTrue(jade==1&&slips==2&&crystals==0,"Native destruction refunds actual jade and slips, never fabricates original crystal");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_sprite_material",setupTicks=20)
    public static void sidedInputNativeMenuCollectsOnceAndOldDepositsRefundOriginalCosts(GameTestHelper h){
        var pos=h.absolutePos(new BlockPos(3,2,3));var vat=station(h,pos);var p=player(h,pos);
        var input=vat.getCapability(ForgeCapabilities.ITEM_HANDLER,Direction.UP).orElseThrow(()->new AssertionError("Native sided input missing"));
        for(var id:new String[]{"bamboo_slip","sprite_jade","ink_stick"}){
            var held=item(id,id.equals("bamboo_slip")?2:1);h.assertTrue(input.insertItem(0,held,false).isEmpty(),"Existing sided automation accepts actual ordered alternate material");
        }
        h.assertTrue(vat.ready()&&vat.getItem(3).is(ExpansionContent.item("zhouguang_star_leaf")),"Same original output appears only after all four actual payments");
        var saved=vat.saveWithoutMetadata();vat.load(saved);var menu=new WorkshopMenu(1,p.getInventory(),vat,vat.data);
        h.assertTrue(!menu.quickMoveStack(p,3).isEmpty()&&p.getInventory().countItem(ExpansionContent.item("zhouguang_star_leaf"))==1,"Actual native output slot transfers original output to inventory");
        h.assertTrue(menu.quickMoveStack(p,3).isEmpty()&&!vat.ready()&&vat.deposited()==0&&vat.saveWithoutMetadata().getList("Paid",10).isEmpty(),"Extraction clears the exact payment receipt and cannot duplicate output");
        var old=new CompoundTag();old.putInt("Deposited",3);old.putString("Recipe",vat.recipe().output());vat.load(old);
        h.assertTrue(vat.deposited()==3,"Legacy Deposited-only transaction remains intact");
        h.getLevel().destroyBlock(pos,false);
        var drops=h.getLevel().getEntitiesOfClass(ItemEntity.class,new AABB(pos).inflate(1.5));int crystals=0,jade=0,slips=0;
        for(var entity:drops){var stack=entity.getItem();if(stack.is(ExpansionContent.item("dragon_crystal")))crystals+=stack.getCount();if(stack.is(ExpansionContent.item("sprite_jade")))jade+=stack.getCount();if(stack.is(ExpansionContent.item("bamboo_slip")))slips+=stack.getCount();}
        h.assertTrue(crystals==1&&slips==2&&jade==0,"Old saves without a receipt refund the original recipe, not newly introduced jade");
        var forge=new WorkshopRecipes.Cost("dynasty:jade_mending_forge",1).stack();h.assertTrue(forge.getItem() instanceof BlockItem,"Original jade forge still registered");
        h.succeed();
    }
    private static void click(ServerPlayer p,BlockPos pos){MinecraftForge.EVENT_BUS.post(new PlayerInteractEvent.RightClickBlock(p,InteractionHand.MAIN_HAND,pos,new BlockHitResult(Vec3.atCenterOf(pos),Direction.UP,pos,false)));}
    @GameTest(template="bow_ritual_test",batch="cod4_sprite_secret",setupTicks=20)
    public static void realStoneAnchorBrushGestureChargesJadeOnceAndRetainsCinnabarAndPersonalClaim(GameTestHelper h){
        var pos=h.absolutePos(new BlockPos(3,2,3));h.getLevel().setBlock(pos,StoryAnchor.BLOCK.get().defaultBlockState().setValue(StoryAnchor.KIND,15),3);
        h.runAfterDelay(2,()->{
            h.assertTrue(SecretTracker.get(h.getLevel()).nearby(pos).get(pos)==16,"Actual loaded native stone anchor is indexed as original secret 16");
            var p=player(h,pos);p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.STICK));p.getInventory().add(item("sprite_jade",2));click(p,pos);
            h.assertTrue(p.getInventory().countItem(ExpansionContent.item("sprite_jade"))==2&&p.getInventory().countItem(ExpansionContent.item("blueprint"))==0,"Wrong gesture cannot consume a carried offering or grant reward");
            p.setItemInHand(InteractionHand.MAIN_HAND,item("chiling_brush",1));click(p,pos);click(p,pos);
            h.assertTrue(p.getInventory().countItem(ExpansionContent.item("sprite_jade"))==1&&p.getInventory().countItem(ExpansionContent.item("blueprint"))==1,"Actual Forge interaction trigger charges one jade and original native personal ledger prevents replay");
            var clone=player(h,pos);SecretTracker.clone(new PlayerEvent.Clone(clone,p,true));clone.setItemInHand(InteractionHand.MAIN_HAND,item("chiling_brush",1));clone.getInventory().add(item("sprite_jade",1));click(clone,pos);
            h.assertTrue(clone.getInventory().countItem(ExpansionContent.item("sprite_jade"))==1&&clone.getInventory().countItem(ExpansionContent.item("blueprint"))==0,"Original death-cloned claim prevents new payment/reward");
            var other=player(h,pos);other.setItemInHand(InteractionHand.MAIN_HAND,item("chiling_brush",1));other.getInventory().add(item("cinnabar",2));click(other,pos);
            h.assertTrue(other.getInventory().countItem(ExpansionContent.item("cinnabar"))==1&&other.getInventory().countItem(ExpansionContent.item("blueprint"))==1,"Existing cinnabar path and a separate character's claim remain available; real network multiplayer pending");
            h.getLevel().removeBlock(pos,false);h.succeed();
        });
    }
}
