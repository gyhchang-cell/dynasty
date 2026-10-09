package com.dynasty.expansion;

import com.dynasty.cod3.*;
import com.dynasty.infusion.*;
import com.mojang.authlib.GameProfile;
import java.util.*;
import net.minecraft.core.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.*;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.inventory.*;
import net.minecraft.world.item.*;
import net.minecraft.world.item.alchemy.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.*;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty_cod4") @PrefixGameTestTemplate(false)
public final class MaterialBrewGameTests {
    private static ItemStack item(String id){return new ItemStack(ExpansionContent.item(id));}
    private static ServerPlayer player(GameTestHelper h){
        var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"brew-native"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.setPos(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(4,2,4))));p.setNoGravity(true);p.getAttribute(Attributes.MAX_HEALTH).setBaseValue(500);p.setHealth(500);p.getFoodData().setFoodLevel(17);return p;
    }
    private static ItemStack result(GameTestHelper h,String id){return h.getLevel().getRecipeManager().byKey(new ResourceLocation("dynasty","cod4/"+id)).orElseThrow().getResultItem(h.getLevel().registryAccess()).copy();}
    @GameTest(template="bow_ritual_test",batch="cod4_brew_recipe",setupTicks=20)
    public static void actualNativeCraftingChargesBothMaterialsDiscoveriesPreservesOldWineAndVanillaCloudItem(GameTestHelper h){
        var p=player(h);p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.STICK));
        for(String id:List.of("warm_wine","poison_smoke_bomb")){
            var menu=new CraftingMenu(7,p.getInventory(),ContainerLevelAccess.create(h.getLevel(),p.blockPosition()));p.containerMenu=menu;
            if(id.equals("warm_wine")){menu.getSlot(1).set(item("marching_wine"));menu.getSlot(2).set(item("python_gall"));menu.getSlot(4).set(new ItemStack(Items.SUGAR));}
            else{menu.getSlot(1).set(item("locust_dust"));menu.getSlot(3).set(new ItemStack(Items.GUNPOWDER));menu.getSlot(4).set(new ItemStack(Items.GLASS_BOTTLE));}
            h.assertTrue(menu.getSlot(0).getItem().isEmpty(),"Missing second native material yields no output");menu.getSlot(id.equals("warm_wine")?3:2).set(item(id.equals("warm_wine")?"python_gall":"locust_dust"));
            var out=menu.getSlot(0).remove(1);h.assertTrue(!out.isEmpty(),"Actual native result slot has authored output");menu.getSlot(0).onTake(p,out);
            for(int i=1;i<=4;i++)h.assertTrue(menu.getSlot(i).getItem().isEmpty(),"Each actual input paid exactly once");h.assertTrue(menu.getSlot(0).getItem().isEmpty(),"Empty grid cannot repeat reward");
            if(id.equals("warm_wine"))h.assertTrue(ExpansionSupplies.warmWine(out)&&out.getItem()==ExpansionContent.item("marching_wine"),"Warm variant retains original wine registry ID");
            else h.assertTrue(out.is(Items.LINGERING_POTION)&&PotionUtils.getPotion(out)==Potions.POISON&&out.getTag().getBoolean("cod4PoisonSmoke"),"Smoke uses actual vanilla lingering potion/poison/color rather than new projectile system");
            h.assertTrue(ItemStack.isSameItemSameTags(out,ItemStack.of(out.save(new CompoundTag()))),"Native stack save retains authored potion/variant/name NBT");
        }
        p.getInventory().add(item("python_gall"));p.getInventory().add(item("locust_dust"));ContentProgress.reconcile(p);
        for(String id:List.of("warm_wine","poison_smoke_bomb"))h.assertTrue(p.getRecipeBook().contains(h.getLevel().getRecipeManager().byKey(new ResourceLocation("dynasty","cod4/"+id)).orElseThrow()),"Actual material obtain discovers exact native recipe");
        h.assertTrue(!ExpansionSupplies.warmWine(result(h,"marching_wine")),"Original plain wine recipe remains plain, original effects retained");p.discard();h.succeed();
    }
    private static float freeze(ServerPlayer p){p.invulnerableTime=0;float old=p.getHealth();boolean hit=p.hurt(p.damageSources().freeze(),40);if(!hit)throw new IllegalStateException("Native freeze hit did not reach health");return old-p.getHealth();}
    @GameTest(template="bow_ritual_test",batch="cod4_warm_wine",setupTicks=20,timeoutTicks=1300)
    public static void actualNativeDrinkConsumesOneReturnsBottleProtectsColdWithoutStackingAndExpires(GameTestHelper h){
        var p=player(h);for(int i=0;i<61;i++)p.tick();float baseline=freeze(p);p.setHealth(500);
        var wine=result(h,"warm_wine");wine.setCount(2);p.setItemInHand(InteractionHand.MAIN_HAND,wine);p.addEffect(new MobEffectInstance(ExpansionEffects.FROST.get(),400));
        h.assertTrue(p.gameMode.useItem(p,h.getLevel(),wine,InteractionHand.MAIN_HAND).consumesAction()&&p.isUsingItem()&&wine.getUseAnimation()==UseAnim.DRINK,"Actual native survival use starts original drink action");
        for(int i=0;i<36;i++){p.tick();p.doTick();}
        h.assertTrue(p.getMainHandItem().getCount()==1&&p.getInventory().countItem(Items.GLASS_BOTTLE)==1&&ExpansionSupplies.warm(p),"Actual full native drink charges one wine, returns one real bottle and starts finite warmth");
        h.assertTrue(!p.hasEffect(ExpansionEffects.FROST.get())&&p.hasEffect(ExpansionEffects.YANG.get())&&p.hasEffect(MobEffects.CONFUSION),"Warmth clears frost while original Marching Wine effects survive");
        p.addEffect(new MobEffectInstance(ExpansionEffects.FROST.get(),400));h.assertTrue(!p.hasEffect(ExpansionEffects.FROST.get()),"Native applicable-effect hook rejects frost only while warm");
        p.setHealth(500);float warmed=freeze(p);h.assertTrue(Math.abs(warmed-baseline*.8)<.05,"Actual native freeze health loss falls exactly20%: "+baseline+" -> "+warmed);
        var saved=p.saveWithoutId(new CompoundTag());var loaded=player(h);loaded.load(saved);h.assertTrue(ExpansionSupplies.warm(loaded),"Native player save/reload retains finite same-dimension warmth");loaded.discard();
        p.setItemSlot(EquipmentSlot.CHEST,InfusionTraits.preview(new ItemStack(Items.LEATHER_CHESTPLATE),InfusionTraits.get("fox_pelt"),0,false));p.setHealth(500);float both=freeze(p);
        p.getPersistentData().putLong("cod4WarmUntil",h.getLevel().getGameTime());p.setHealth(500);float lining=freeze(p);h.assertTrue(Math.abs(both-lining)<.05,"Original lining and wine use one shared reduction, never multiply/stack");p.setItemSlot(EquipmentSlot.CHEST,ItemStack.EMPTY);
        p.getPersistentData().putLong("cod4WarmUntil",h.getLevel().getGameTime()+ExpansionSupplies.WARM_TICKS);
        h.runAfterDelay(1210,()->{try{h.assertTrue(!ExpansionSupplies.warm(p),"Actual server elapsed time expires wine warmth");p.addEffect(new MobEffectInstance(ExpansionEffects.FROST.get(),400));h.assertTrue(p.hasEffect(ExpansionEffects.FROST.get()),"Native frost immunity cannot linger after expiration");p.setHealth(500);h.assertTrue(Math.abs(freeze(p)-baseline)<.05,"Native freeze damage returns to baseline after finite expiration");h.succeed();}finally{p.discard();}});
    }
    @GameTest(template="bow_ritual_test",batch="cod4_gu_trade",setupTicks=20)
    public static void existingHeiPoNativeTwoMaterialTradeKeepsAllOldOffersUsesDemandAndFiniteStockAcrossReload(GameTestHelper h){
        var npc=NpcContent.NPCS.get("hei_po").get().create(h.getLevel());npc.setPos(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(4,2,5))));npc.setNoAi(true);npc.getOffers().get(0).increaseUses();npc.getOffers().get(0).increaseUses();npc.getOffers().get(0).addToSpecialPriceDiff(4);var old=npc.saveWithoutId(new CompoundTag());npc.load(old);npc.ensureContentTrades();
        var gu=npc.getOffers().stream().filter(o->ItemStack.isSameItemSameTags(o.getResult(),MaterialBrews.gu())).findFirst().orElseThrow();int size=npc.getOffers().size();for(int i=0;i<10;i++)npc.ensureContentTrades();h.assertTrue(npc.getOffers().size()==size&&npc.getOffers().get(0).getUses()==2&&npc.getOffers().get(0).getSpecialPriceDiff()==4,"Native migration appends one gu offer and retains all original stock/price state");
        var p=player(h);p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.STICK));h.assertTrue(npc.trade(p)&&p.containerMenu instanceof MerchantMenu,"Actual original role opens native merchant screen");var menu=(MerchantMenu)p.containerMenu;menu.setSelectionHint(npc.getOffers().indexOf(gu));menu.getSlot(0).set(item("python_gall"));menu.getSlot(1).set(item("locust_dust"));h.assertTrue(menu.getSlot(2).getItem().isEmpty()&&gu.getUses()==0,"One missing dust rejects output/stock");
        for(int i=0;i<8;i++){menu.getSlot(0).set(item("python_gall"));menu.getSlot(1).set(new ItemStack(ExpansionContent.item("locust_dust"),2));h.assertTrue(!menu.quickMoveStack(p,2).isEmpty()&&menu.getSlot(0).getItem().isEmpty()&&menu.getSlot(1).getItem().isEmpty()&&gu.getUses()==i+1,"Native result take pays both real materials once");}
        menu.getSlot(0).set(item("python_gall"));menu.getSlot(1).set(new ItemStack(ExpansionContent.item("locust_dust"),2));h.assertTrue(menu.quickMoveStack(p,2).isEmpty()&&menu.getSlot(0).getItem().getCount()==1&&menu.getSlot(1).getItem().getCount()==2,"Native eight-stock cap rejects ninth without payment");
        var reloaded=NpcContent.NPCS.get("hei_po").get().create(h.getLevel());reloaded.load(npc.saveWithoutId(new CompoundTag()));reloaded.ensureContentTrades();h.assertTrue(reloaded.getOffers().size()==size&&reloaded.getOffers().stream().filter(o->ItemStack.isSameItemSameTags(o.getResult(),MaterialBrews.gu())).findFirst().orElseThrow().getUses()==8,"Native old-save reload preserves exhausted gu stock without duplicate offers");p.closeContainer();p.discard();npc.discard();reloaded.discard();h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_poison_smoke",setupTicks=20,timeoutTicks=140)
    public static void actualNativeThrowImpactCreatesCloudPoisonsNearWithRealHealthLossAndRetainsUndeadImmunity(GameTestHelper h){
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=1;y<=5;y++)h.setBlock(x,y,z,y==1?Blocks.STONE:Blocks.AIR);
        var p=player(h);p.setYRot(0);p.setXRot(40);
        var cow=h.spawn(EntityType.COW,new BlockPos(4,2,7));cow.setNoAi(true);cow.getAttribute(Attributes.MAX_HEALTH).setBaseValue(200);cow.setHealth(200);
        var undead=h.spawn(EntityType.ZOMBIE,new BlockPos(5,2,7));undead.setNoAi(true);undead.setNoGravity(true);
        var far=h.spawn(EntityType.COW,new BlockPos(4,2,14));far.setNoAi(true);far.setNoGravity(true);
        h.startSequence().thenWaitUntil(()->h.assertTrue(cow.tickCount>1&&h.getLevel().getEntity(cow.getUUID())==cow,"Actual native target visible and ticking"))
        .thenExecute(()->{
            var smoke=result(h,"poison_smoke_bomb");smoke.setCount(2);p.setItemInHand(InteractionHand.MAIN_HAND,smoke);var success=p.gameMode.useItem(p,h.getLevel(),smoke,InteractionHand.MAIN_HAND);
            h.assertTrue(success.consumesAction()&&p.getMainHandItem().getCount()==1,"Actual native throw consumes one original vanilla potion");
            var cloud=new AreaEffectCloud[1];
            h.runAfterDelay(25,()->{
                var clouds=h.getLevel().getEntitiesOfClass(AreaEffectCloud.class,new AABB(h.absolutePos(BlockPos.ZERO),h.absolutePos(new BlockPos(16,6,16))));
                h.assertTrue(clouds.size()==1&&clouds.get(0).getOwner()==p&&clouds.get(0).getColor()==0x777477,"Real thrown projectile collision creates one native gray cloud with original owner: "+clouds.stream().map(e->"at="+e.position()+", age="+e.tickCount+", color="+e.getColor()+", owner="+(e.getOwner()==p)).toList());
                cloud[0]=clouds.get(0);var tag=cloud[0].saveWithoutId(new CompoundTag());h.assertTrue(tag.getInt("Duration")>0&&tag.getInt("Age")>0,"Native cloud saves finite duration and elapsed life");
            });
            h.runAfterDelay(70,()->{try{
                h.assertTrue(cow.hasEffect(MobEffects.POISON)&&cow.getHealth()<200&&!far.hasEffect(MobEffects.POISON)&&!undead.hasEffect(MobEffects.POISON),"Actual native cloud poisoning changes health within range, excludes far target and keeps vanilla undead immunity: cow="+cow.getHealth()+", poison="+cow.hasEffect(MobEffects.POISON));
                h.assertTrue(cloud[0]!=null&&(cloud[0].isRemoved()||cloud[0].getRadius()<3),"Vanilla native cloud radius shrinks on actual use, including lawful early exhaustion");h.succeed();
            }finally{if(cloud[0]!=null)cloud[0].discard();cow.discard();undead.discard();far.discard();p.discard();}});
        });
    }
}
