package com.dynasty.army;

import com.dynasty.*;
import com.dynasty.entity.*;
import com.mojang.authlib.GameProfile;
import java.util.*;
import net.minecraft.core.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.network.protocol.game.ServerboundContainerButtonClickPacket;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.*;
import net.minecraft.world.inventory.*;
import net.minecraft.world.item.*;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.*;
import net.minecraftforge.gametest.*;

/** Real native crafting/use/menu/deployment, without claiming a client or multiplayer run. */
@GameTestHolder("dynasty_army") @PrefixGameTestTemplate(false)
public final class TigerTallyNativeGameTests {
    private static void packet(ServerPlayer p,ArmyMenu menu,int action){p.connection.handleContainerButtonClick(new ServerboundContainerButtonClickPacket(menu.containerId,(menu.view.get(2)<<8)|action));}
    private static ArmyMenu tally(GameTestHelper h,ServerPlayer p,InteractionHand hand){
        var result=p.gameMode.useItem(p,h.getLevel(),p.getItemInHand(hand),hand);
        h.assertTrue(result.consumesAction()&&p.containerMenu instanceof ArmyMenu,"Actual native survival item-use opens original army menu");
        var menu=(ArmyMenu)p.containerMenu;h.assertTrue(menu.desk==null&&menu.stillValid(p),"Tally opens owner's original roster, not a free recruitment desk");return menu;
    }
    @GameTest(template="bow_ritual_test",batch="army_tally_native_crafting",setupTicks=20,timeoutTicks=160)
    public static void nativeSurvivalCraftingAndCopiedMainOffhandTalliesShareOnePaidRosterAndOneDeployedCarrier(GameTestHelper h){
        var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"tally-native"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(p.server,new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.gameMode.changeGameModeForPlayer(GameType.SURVIVAL);p.setPos(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(8,2,5))));
        UUID carrier=null;
        try{
            h.assertTrue(!p.isCreative()&&!p.getAbilities().instabuild&&ArmyRoster.soldiers(p).isEmpty(),"Fresh survival owner starts without gifted soldiers or creative ingredient exemptions");
            var recipe=h.getLevel().getRecipeManager().byKey(new ResourceLocation("dynasty","tiger_tally")).orElseThrow();
            h.assertTrue(recipe.getIngredients().size()==3,"Original three-ingredient survival recipe remains registered");
            var menu=new CraftingMenu(7,p.getInventory(),ContainerLevelAccess.create(h.getLevel(),p.blockPosition()));p.containerMenu=menu;
            Item[] ingredients={DynastyItems.BRONZE_INGOT.get(),Items.GOLD_INGOT,DynastyItems.CINNABAR.get()};
            for(int i=0;i<ingredients.length;i++)menu.getSlot(i+1).set(new ItemStack(ingredients[i],2));
            var crafted=new ArrayList<ItemStack>();
            for(int craft=0;craft<2;craft++){
                var output=menu.getSlot(0).remove(1);h.assertTrue(output.is(DynastyItems.TIGER_TALLY.get())&&output.getCount()==1,"Native original crafting grid produces exactly one original tiger_tally");menu.getSlot(0).onTake(p,output);crafted.add(output);
                for(int slot=1;slot<=3;slot++)h.assertTrue(menu.getSlot(slot).getItem().getCount()==1-craft,"Native ResultSlot consumes each real original ingredient exactly once per output");
            }
            h.assertTrue(menu.getSlot(0).getItem().isEmpty()&&ArmyRoster.soldiers(p).isEmpty(),"Empty grid cannot replay a result; crafting two tallies grants no soldier");p.closeContainer();
            var first=crafted.get(0);first.getOrCreateTag().putString("ForeignTallyData","copied-kept");var copy=first.copy();
            p.setItemInHand(InteractionHand.MAIN_HAND,first);p.setItemInHand(InteractionHand.OFF_HAND,copy);p.getInventory().setItem(10,new ItemStack(DynastyItems.SILVER_COIN.get(),20));
            for(var hand:InteractionHand.values()){
                var opened=tally(h,p,hand);h.assertTrue(opened.view.get(0)==0&&ArmyRoster.soldiers(p).isEmpty()&&ArmyRoster.coins(p)==20,"Either identical copied tally exposes the same empty owner roster and gifts no team");packet(p,opened,0);h.assertTrue(ArmyRoster.soldiers(p).isEmpty()&&ArmyRoster.coins(p)==20,"Tally-only native recruitment packet cannot create or charge a soldier");p.closeContainer();
            }
            var desk=h.absolutePos(new BlockPos(8,2,6));h.getLevel().setBlockAndUpdate(desk,ArmyContent.DESK.get().defaultBlockState());
            p.gameMode.useItemOn(p,h.getLevel(),p.getMainHandItem(),InteractionHand.MAIN_HAND,new BlockHitResult(Vec3.atCenterOf(desk),Direction.UP,desk,false));
            h.assertTrue(p.containerMenu instanceof ArmyMenu&&((ArmyMenu)p.containerMenu).desk!=null,"Actual original desk use is still needed to recruit");packet(p,(ArmyMenu)p.containerMenu,0);
            h.assertTrue(ArmyRoster.soldiers(p).size()==1&&ArmyRoster.coins(p)==8,"One legal desk purchase creates one paid original twelve-silver blade guard");var paid=ArmyRoster.soldiers(p).getCompound(0).getUUID("Id");p.closeContainer();
            var primary=tally(h,p,InteractionHand.MAIN_HAND);h.assertTrue(primary.view.get(0)==1&&ArmyRoster.find(p,paid)!=null,"First tally resolves same original paid UUID");packet(p,primary,13);
            for(int x=3;x<=13;x++)for(int z=7;z<=15;z++){h.getLevel().setBlock(h.absolutePos(new BlockPos(x,1,z)),Blocks.STONE.defaultBlockState(),2);for(int y=2;y<=5;y++)h.getLevel().setBlock(h.absolutePos(new BlockPos(x,y,z)),Blocks.AIR.defaultBlockState(),2);}
            p.setYRot(0);packet(p,primary,10);var row=ArmyRoster.find(p,paid);h.assertTrue(row.getString("State").equals("DEPLOYED")&&row.hasUUID("Entity"),"Actual native original formation button deploys one paid unit on real clear terrain");carrier=row.getUUID("Entity");h.assertTrue(h.getLevel().getEntity(carrier) instanceof ImperialSoldier&&row.getLong("Generation")==1,"Paid roster has one real carrier and one original generation");p.closeContainer();
            var secondary=tally(h,p,InteractionHand.OFF_HAND);packet(p,secondary,10);h.assertTrue(secondary.view.get(0)==1&&ArmyRoster.soldiers(p).size()==1&&ArmyRoster.find(p,paid).getUUID("Entity").equals(carrier)&&ArmyRoster.find(p,paid).getLong("Generation")==1&&ArmyRoster.coins(p)==8,"Copied second tally cannot deploy a second team or change paid identity, generation or currency");
            long carriers=h.getLevel().getEntitiesOfClass(ImperialSoldier.class,p.getBoundingBox().inflate(20)).stream().filter(e->e.getPersistentData().hasUUID("ArmySoldier")&&e.getPersistentData().getUUID("ArmySoldier").equals(paid)).count();h.assertTrue(carriers==1,"Actual world contains exactly one carrier for this original paid soldier");
            h.assertTrue(ItemStack.isSameItemSameTags(p.getMainHandItem(),p.getOffhandItem())&&p.getMainHandItem().getCount()==1&&p.getOffhandItem().getCount()==1,"Original copied tally NBT/count remain unchanged by crafting proof and roster use");h.succeed();
        }finally{
            if(carrier!=null&&h.getLevel().getEntity(carrier)!=null)h.getLevel().getEntity(carrier).discard();p.closeContainer();net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(new net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedOutEvent(p));DynastyTrinkets.forget(p);p.discard();
        }
    }
    private TigerTallyNativeGameTests(){}
    @GameTest(template="bow_ritual_test",batch="army_purchase_native_rejections",setupTicks=20,timeoutTicks=160)
    public static void nativeRecruitmentPacketsRejectInsufficientFundsFullBookWrongContainerReplayAndLostDeskAuthorityWithoutAssetLoss(GameTestHelper h){
        var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"purchase-rejections-native"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(p.server,new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);p.gameMode.changeGameModeForPlayer(GameType.SURVIVAL);
        var desk=h.absolutePos(new BlockPos(6,2,6));var entrance=Vec3.atBottomCenterOf(desk.north(2));p.setPos(entrance);h.getLevel().setBlockAndUpdate(desk,ArmyContent.DESK.get().defaultBlockState());
        try{
            for(int role=0;role<3;role++){
                p.getInventory().setItem(10,new ItemStack(DynastyItems.SILVER_COIN.get(),ArmyRoster.PRICE[role]-1));
                p.gameMode.useItemOn(p,h.getLevel(),p.getMainHandItem(),InteractionHand.MAIN_HAND,new BlockHitResult(Vec3.atCenterOf(desk),Direction.UP,desk,false));h.assertTrue(p.containerMenu instanceof ArmyMenu,"Native survival desk-use opens a real server menu");var menu=(ArmyMenu)p.containerMenu;packet(p,menu,role);
                h.assertTrue(ArmyRoster.soldiers(p).isEmpty()&&ArmyRoster.coins(p)==ArmyRoster.PRICE[role]-1&&menu.view.get(0)==0&&menu.view.get(1)==ArmyRoster.PRICE[role]-1,"Each original role refuses insufficient balance without partial payment, soldier or inconsistent native menu receipt");p.closeContainer();
            }
            for(int slot=10;slot<=18;slot++){var coins=new ItemStack(DynastyItems.SILVER_COIN.get(),64);coins.getOrCreateTag().putInt("ForeignCoinSlot",slot);p.getInventory().setItem(slot,coins);}
            p.gameMode.useItemOn(p,h.getLevel(),p.getMainHandItem(),InteractionHand.MAIN_HAND,new BlockHitResult(Vec3.atCenterOf(desk),Direction.UP,desk,false));var menu=(ArmyMenu)p.containerMenu;int initial=ArmyRoster.coins(p);
            for(int n=0;n<ArmyRoster.CAPACITY;n++){
                int code=menu.view.get(2)<<8;int coins=ArmyRoster.coins(p);p.connection.handleContainerButtonClick(new ServerboundContainerButtonClickPacket(menu.containerId,code));
                h.assertTrue(ArmyRoster.soldiers(p).size()==n+1&&ArmyRoster.coins(p)==coins-ArmyRoster.PRICE[0]&&menu.view.get(0)==n+1&&menu.view.get(1)==coins-ArmyRoster.PRICE[0],"Each actual accepted packet atomically updates original book, balance and native receipt");
                p.connection.handleContainerButtonClick(new ServerboundContainerButtonClickPacket(menu.containerId,code));h.assertTrue(ArmyRoster.soldiers(p).size()==n+1&&ArmyRoster.coins(p)==coins-ArmyRoster.PRICE[0],"Every double click/repeated native packet is exactly one purchase");
            }
            var soldiers=ArmyRoster.soldiers(p).copy();var inventory=new net.minecraft.nbt.ListTag();p.getInventory().save(inventory);int balance=initial-ArmyRoster.CAPACITY*ArmyRoster.PRICE[0];
            packet(p,menu,0);packet(p,menu,1);packet(p,menu,2);
            h.assertTrue(ArmyRoster.soldiers(p).equals(soldiers)&&ArmyRoster.coins(p)==balance,"All original role purchases refuse a genuinely purchased full36 book without losing assets");
            p.connection.handleContainerButtonClick(new ServerboundContainerButtonClickPacket(menu.containerId+100,menu.view.get(2)<<8));
            p.setPos(entrance.add(100,0,0));packet(p,menu,0);p.setPos(entrance);h.getLevel().setBlockAndUpdate(desk,Blocks.AIR.defaultBlockState());packet(p,menu,0);
            p.closeContainer();p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(DynastyItems.TIGER_TALLY.get()));var tallyMenu=tally(h,p,InteractionHand.MAIN_HAND);p.setItemInHand(InteractionHand.MAIN_HAND,ItemStack.EMPTY);packet(p,tallyMenu,40);
            var afterInventory=new net.minecraft.nbt.ListTag();p.getInventory().save(afterInventory);
            h.assertTrue(!tallyMenu.stillValid(p)&&ArmyRoster.soldiers(p).equals(soldiers)&&ArmyRoster.coins(p)==balance&&afterInventory.equals(inventory),"Wrong container, remote/removed desk and no-tally authority cannot mutate original paid records or exact foreign-tagged coin inventory");
            h.assertTrue(soldiers.stream().map(n->((net.minecraft.nbt.CompoundTag)n).getUUID("Id")).distinct().count()==ArmyRoster.CAPACITY,"Every native paid original soldier identity is unique");h.succeed();
        }finally{p.closeContainer();net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(new net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedOutEvent(p));DynastyTrinkets.forget(p);p.discard();}
    }
}
