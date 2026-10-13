package com.dynasty.client;

import com.dynasty.cod3.*;
import com.dynasty.expansion.*;
import com.mojang.authlib.GameProfile;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.*;
import net.minecraft.world.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.*;
import net.minecraft.world.item.*;
import net.minecraft.world.item.enchantment.*;
import net.minecraftforge.registries.ForgeRegistries;
import java.util.*;

/** Real integrated-server menus/slots, not a simulation of inventory transactions. */
public final class NpcShopChecks {
    static final List<String> LOG=new ArrayList<>();
    static void require(boolean result,String note){if(!result)throw new AssertionError(note);LOG.add("PASS "+note);}
    static ServerPlayer player(ServerLevel world){
        var p=new ServerPlayer(world.getServer(),world,new GameProfile(UUID.randomUUID(),"ShopChecks")){@Override public boolean hasDisconnected(){return false;}};
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(world.getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.setPos(0,-60,3);return p;
    }
    static ItemStack coins(int amount){return new ItemStack(ExpansionContent.item("copper_coin"),amount);}
    static boolean conversation(Player p){try{var method=NpcDialogue.class.getDeclaredMethod("session",UUID.class);method.setAccessible(true);return method.invoke(null,p.getUUID())!=null;}catch(Exception e){throw new RuntimeException(e);}}
    static ItemStack gear(){var s=new ItemStack(Items.DIAMOND_SWORD);s.setDamageValue(500);s.setHoverName(Component.literal("Keep name"));s.getOrCreateTag().putString("DynastyFixture","kept");s.enchant(Enchantments.UNBREAKING,1);return s;}
    public static List<Integer> run(ServerLevel world){
        var p=player(world);var q=player(world);var ids=new ArrayList<Integer>();
        for(String role:NpcContent.NPCS.keySet()){
            var npc=NpcContent.NPCS.get(role).get().create(world);npc.setPos(0,-60,0);npc.setNoAi(true);world.addFreshEntity(npc);ids.add(npc.getId());
            var old=npc.saveWithoutId(new net.minecraft.nbt.CompoundTag());
            npc.mobInteract(p,InteractionHand.MAIN_HAND);require(p.containerMenu instanceof NpcTradeMenu,role+" ordinary right-click opens native trade subclass");
            var menu=(NpcTradeMenu)p.containerMenu;require(!menu.getOffers().isEmpty(),role+" retains real merchant offers");
            var offer=menu.getOffers().get(0);int uses=offer.getUses();menu.getSlot(0).set(offer.getCostA().copy());menu.getSlot(1).set(offer.getCostB().copy());
            require(!menu.quickMoveStack(p,2).isEmpty()&&offer.getUses()==uses+1,role+" native result consumes payment and one stock");
            require(menu.quickMoveStack(p,2).isEmpty()&&offer.getUses()==uses+1,role+" trade result cannot replay");
            p.closeContainer();p.getInventory().clearContent();npc.load(old);
            p.setShiftKeyDown(true);npc.mobInteract(p,InteractionHand.MAIN_HAND);require(conversation(p),role+" Shift right-click retains original dialogue");p.setShiftKeyDown(false);
            npc.setPos((ids.size()-1)%5*2-4,-60,((ids.size()-1)/5)*3);npc.home(npc.blockPosition());
        }
        var npc=(DynastyNpcEntity)world.getEntity(ids.get(0));npc.setPos(0,-60,0);
        require(NpcTrading.open(p,npc,1),"open repair page");var m=(NpcServiceMenu)p.containerMenu;
        m.getSlot(0).set(gear());m.getSlot(1).set(coins(15));require(!m.clickMenuButton(p,20)&&m.getSlot(0).getItem().getDamageValue()==500&&m.getSlot(1).getItem().getCount()==15,"insufficient fixed fee does not mutate either input");
        m.getSlot(1).set(new ItemStack(Items.EMERALD,64));require(!m.clickMenuButton(p,20),"other currency cannot pay");m.getSlot(1).set(coins(32));
        require(!m.clickMenuButton(q,20),"another player cannot submit owner's menu");
        require(m.clickMenuButton(p,20),"repair succeeds once with real inputs");var result=m.getSlot(2).getItem();
        require(result.getDamageValue()==0&&result.getHoverName().getString().equals("Keep name")&&result.getTag().getString("DynastyFixture").equals("kept")&&EnchantmentHelper.getItemEnchantmentLevel(Enchantments.UNBREAKING,result)==1,"full durability repair preserves name, custom NBT and old enchantment");
        require(m.getSlot(0).getItem().isEmpty()&&m.getSlot(1).getItem().getCount()==16&&!m.clickMenuButton(p,20),"exact 16 coins consumed before output; repeated submit rejected");
        require(!m.quickMoveStack(p,2).isEmpty()&&m.quickMoveStack(p,2).isEmpty(),"shift result returns one repaired sword, never duplicates");
        m.getSlot(0).set(new ItemStack(Items.DIAMOND_SWORD));require(!m.clickMenuButton(p,20)&&m.getSlot(1).getItem().getCount()==16,"undamaged gear is not charged");
        m.clickMenuButton(p,2);m.getSlot(1).set(coins(64));require(m.clickMenuButton(p,20),"enchant tab creates paid result");
        require(m.getSlot(1).getItem().getCount()==32&&!EnchantmentHelper.getEnchantments(m.getSlot(2).getItem()).isEmpty(),"exact 32 coins paid for actual vanilla enchantment NBT");
        require(!m.clickMenuButton(p,20),"uncollected output blocks further charge");
        p.getInventory().clearContent();p.closeContainer();require(p.getInventory().countItem(Items.DIAMOND_SWORD)==1&&p.getInventory().countItem(ExpansionContent.item("copper_coin"))==32,"closing returns paid result and remaining coins");
        require(NpcTrading.open(p,npc,1),"reopen independent service inventory");m=(NpcServiceMenu)p.containerMenu;m.getSlot(0).set(gear());m.getSlot(1).set(coins(64));
        require(m.clickMenuButton(p,0)&&p.containerMenu instanceof NpcTradeMenu&&p.getInventory().countItem(Items.DIAMOND_SWORD)==2&&p.getInventory().countItem(ExpansionContent.item("copper_coin"))==96,"switching to trade returns both unpaid inputs and preserves ownership");
        require(p.containerMenu.clickMenuButton(p,3)&&conversation(p)&&npc.getTradingPlayer()==null,"Talk tab releases trading and opens existing role dialogue");
        NpcTrading.open(p,npc,2);m=(NpcServiceMenu)p.containerMenu;m.getSlot(0).set(gear());m.getSlot(1).set(coins(64));p.setPos(20,-60,20);
        require(!m.stillValid(p)&&!m.clickMenuButton(p,20)&&m.getSlot(1).getItem().getCount()==64,"distance invalidates service without charging");p.setPos(0,-60,3);npc.setTradingPlayer(q);require(!m.clickMenuButton(p,20),"trading ownership change invalidates stale menu");npc.setTradingPlayer(p);npc.setHealth(0);require(!m.clickMenuButton(p,20),"dead NPC cannot process items");npc.setHealth(40);p.closeContainer();
        int multiple=0;
        for(int seed=0;seed<256;seed++){
            var before=gear();var after=NpcEquipmentService.enchant(before,net.minecraft.util.RandomSource.create(seed));var values=EnchantmentHelper.getEnchantments(after);
            require(before.getDamageValue()==500&&values.getOrDefault(Enchantments.UNBREAKING,0)>=1&&after.getTag().getString("DynastyFixture").equals("kept"),"enchant copy/NBT preserved seed "+seed);
            for(var e:values.entrySet()){require(!e.getKey().isCurse()&&e.getValue()>=1&&e.getValue()<=e.getKey().getMaxLevel(),"enchantment legal level");for(var other:values.keySet())require(e.getKey()==other||e.getKey().isCompatibleWith(other),"enchantments mutually compatible");}
            if(values.size()>1)multiple++;
        }
        require(multiple>0,"random enhancement can contain multiple compatible enchantments");
        var exhausted=gear();while(!NpcEquipmentService.candidates(exhausted).isEmpty()){var e=NpcEquipmentService.candidates(exhausted).get(0);exhausted.enchant(e,e.getMaxLevel());}
        require(NpcEquipmentService.candidates(new ItemStack(Items.DIRT)).isEmpty()&&NpcEquipmentService.enchant(exhausted,net.minecraft.util.RandomSource.create(1)).isEmpty(),"invalid/maxed gear has no paid no-op enchant");
        var colors=new HashSet<String>();for(String role:NpcContent.NPCS.keySet()){var c=com.dynasty.item.DynastyEggPalette.colors(role);require(colors.add(Arrays.toString(c)),"unique NPC egg "+role);}for(var spec:SecondaryMobs.SPECS){var c=com.dynasty.item.DynastyEggPalette.colors(spec.id());require(colors.add(Arrays.toString(c)),"unique secondary egg "+spec.id());}
        require(colors.size()==45,"all 45 previously uniform egg pairs now distinct");p.discard();q.discard();return ids;
    }
}
