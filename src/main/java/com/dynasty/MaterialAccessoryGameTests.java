package com.dynasty;

import com.dynasty.expansion.*;
import com.dynasty.infusion.*;
import com.mojang.authlib.GameProfile;
import java.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.entity.projectile.Arrow;
import net.minecraft.world.inventory.*;
import net.minecraft.world.item.*;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.event.entity.player.*;
import net.minecraftforge.gametest.*;

/** Native recipes, exact existing slot-owned stack NBT, real attack/hurt rather than another proc engine. */
@GameTestHolder("dynasty_cod4") @PrefixGameTestTemplate(false)
public final class MaterialAccessoryGameTests {
    private static ItemStack item(String id){return new ItemStack(ExpansionContent.item(id));}
    private static ServerPlayer player(GameTestHelper h){
        var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"material-charm"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.setPos(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(4,2,4))));p.setNoGravity(true);return p;
    }
    private static ItemStack variant(GameTestHelper h,String recipe){return h.getLevel().getRecipeManager().byKey(new ResourceLocation("dynasty","cod4/"+recipe)).orElseThrow().getResultItem(h.getLevel().registryAccess()).copy();}
    private static void close(ServerPlayer p){InfusionCombat.logout(new PlayerEvent.PlayerLoggedOutEvent(p));DynastyTrinkets.forget(p);DynastySchoolCombat.forget(p);p.discard();}
    @GameTest(template="bow_ritual_test",batch="cod4_material_accessory",setupTicks=20)
    public static void nativeCraftingConsumesExactMaterialsPreservesBaseRecipesAndDiscoversBothVariants(GameTestHelper h){
        var p=player(h);p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.STICK));
        String[][] rows={{"wolf_fang","gray_wolf_fang_charm","tiger_claw","shanxiao_claw"},{"crab_shell","crab_soldier_shell_charm","scale_plate","retaliation"}};
        for(var row:rows){
            var menu=new CraftingMenu(7,p.getInventory(),ContainerLevelAccess.create(h.getLevel(),p.blockPosition()));p.containerMenu=menu;
            menu.getSlot(1).set(item(row[0]));menu.getSlot(3).set(item("refined_steel"));menu.getSlot(4).set(new ItemStack(Items.STRING));
            h.assertTrue(menu.getSlot(0).getItem().isEmpty(),"One material cannot create a two-material charm");menu.getSlot(2).set(item(row[0]));
            var out=menu.getSlot(0).remove(1);h.assertTrue(out.is(ExpansionContent.item(row[2]))&&InfusionTraits.effects(out).contains(row[3]),"Actual recipe output retains original ID and has one legal native material effect: "+row[1]);
            menu.getSlot(0).onTake(p,out);for(int i=1;i<=4;i++)h.assertTrue(menu.getSlot(i).getItem().isEmpty(),"Actual result take consumes every real ingredient once");
            h.assertTrue(menu.getSlot(0).getItem().isEmpty(),"Empty recipe cannot replay output");
            var reloaded=ItemStack.of(out.save(new CompoundTag()));h.assertTrue(ItemStack.isSameItemSameTags(out,reloaded)&&InfusionTraits.active(reloaded).equals(Set.of(row[0])),"Native stack reload retains only the original one-capacity material trait");
            h.assertTrue(out.getHoverName().getString().contains(row[1])||out.hasCustomHoverName(),"Variant has its own localized display name");
            p.getInventory().add(item(row[0]));ContentProgress.reconcile(p);var recipe=h.getLevel().getRecipeManager().byKey(new ResourceLocation("dynasty","cod4/"+row[1])).orElseThrow();
            h.assertTrue(p.getRecipeBook().contains(recipe),"Actually obtained material discovers native recipe without adding a use gate");
            var old=h.getLevel().getRecipeManager().byKey(new ResourceLocation("dynasty",row[2])).orElseThrow().getResultItem(h.getLevel().registryAccess());
            h.assertTrue(old.is(out.getItem())&&!old.hasTag(),"Original basic recipe and uninfused old accessory remain unchanged");
        }
        h.assertTrue(DynastyTrinkets.IDS.size()==201,"Canonical accessory registry and existing gift pool retain all original IDs");close(p);h.succeed();
    }
    private static Zombie target(GameTestHelper h,ServerPlayer p){
        var z=new Zombie(h.getLevel());z.setPos(p.position().add(1,0,0));z.setNoAi(true);z.setNoGravity(true);
        z.getAttribute(Attributes.MAX_HEALTH).setBaseValue(10000);z.setHealth(10000);z.getAttribute(Attributes.ARMOR).setBaseValue(0);z.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);return z;
    }
    private static float hit(GameTestHelper h,ServerPlayer p,Zombie z){
        for(int i=0;i<22;i++)p.doTick();p.setOnGround(true);p.setSprinting(false);z.invulnerableTime=0;
        h.assertTrue(p.getAttackStrengthScale(.5f)>.9f,"Actual attack cooldown is charged");float before=z.getHealth();p.attack(z);
        h.assertTrue(z.getHealth()<before&&p.getAttackStrengthScale(.5f)<.2f,"Real vanilla Player.attack changes health and resets cooldown");return before-z.getHealth();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_material_accessory",setupTicks=20,timeoutTicks=60)
    public static void wornFangUsesThreeActualPrimaryAttacksAndUnequipImmediatelyStopsIt(GameTestHelper h){
        if(!DynastyCuriosSetup.isLoaded()){h.succeed();return;}
        var p=player(h);p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.IRON_SWORD));var z=target(h,p);h.getLevel().addFreshEntity(z);
        SchoolCombatGameTests.equip(p,"hands",variant(h,"gray_wolf_fang_charm"));
        h.runAfterDelay(3,()->{try{
            float a=hit(h,p,z),b=hit(h,p,z),c=hit(h,p,z);
            h.assertTrue(Math.abs(a-b)<.02&&Math.abs(c-a*1.15)<.02&&z.hasEffect(MobEffects.MOVEMENT_SLOWDOWN),"Only third native primary hit receives the existing fifteen-percent pursuit: "+a+"/"+b+"/"+c);
            z.removeEffect(MobEffects.MOVEMENT_SLOWDOWN);hit(h,p,z);hit(h,p,z);hit(h,p,z);h.assertTrue(!z.hasEffect(MobEffects.MOVEMENT_SLOWDOWN),"Original sixty-tick world cooldown cannot be bypassed by rapid inputs");
            SchoolCombatGameTests.equip(p,"hands",ItemStack.EMPTY);for(int i=0;i<3;i++)hit(h,p,z);h.assertTrue(!z.hasEffect(MobEffects.MOVEMENT_SLOWDOWN),"Removed charm leaves no active pursuit trait");h.succeed();
        }finally{close(p);z.discard();}});
    }
    @GameTest(template="bow_ritual_test",batch="cod4_material_accessory",setupTicks=20,timeoutTicks=60)
    public static void weaponAndWornFangShareOneProcAndInventoryArrowsUncapturedSourcesCannotAdvanceIt(GameTestHelper h){
        if(!DynastyCuriosSetup.isLoaded()){h.succeed();return;}
        var p=player(h);var fang=variant(h,"gray_wolf_fang_charm");p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.IRON_SWORD));p.getInventory().setItem(9,fang.copy());
        var z=target(h,p);h.getLevel().addFreshEntity(z);
        h.runAfterDelay(3,()->{try{
            float a=hit(h,p,z);hit(h,p,z);float c=hit(h,p,z);h.assertTrue(Math.abs(a-c)<.02&&!z.hasEffect(MobEffects.MOVEMENT_SLOWDOWN),"Carried unworn variant has no combat benefit");
            SchoolCombatGameTests.equip(p,"hands",fang);p.setItemInHand(InteractionHand.MAIN_HAND,InfusionTraits.preview(new ItemStack(Items.IRON_SWORD),InfusionTraits.get("wolf_fang"),0,false));
            var arrow=new Arrow(h.getLevel(),p);arrow.setCritArrow(true);var arrowHit=new LivingHurtEvent(z,p.damageSources().arrow(arrow,p),100);InfusionCombat.hurt(arrowHit);
            var stale=new LivingHurtEvent(z,p.damageSources().playerAttack(p),100);InfusionCombat.hurt(stale);
            h.assertTrue(arrowHit.getAmount()==100&&stale.getAmount()==100&&!z.hasEffect(MobEffects.MOVEMENT_SLOWDOWN),"Arrow and uncaptured secondary damage cannot start or advance charm pursuit");
            a=hit(h,p,z);hit(h,p,z);c=hit(h,p,z);h.assertTrue(Math.abs(c-a*1.15)<.02,"Same weapon and charm effect is deduplicated by the original set, not twice applied");h.succeed();
        }finally{close(p);z.discard();}});
    }
    @GameTest(template="bow_ritual_test",batch="cod4_material_accessory",setupTicks=20)
    public static void actualIncomingDamageUsesWornShellOriginalRetaliationCooldownAndRemoval(GameTestHelper h){
        if(!DynastyCuriosSetup.isLoaded()){h.succeed();return;}
        var p=player(h);var z=target(h,p);p.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);p.setHealth(1000);for(int i=0;i<61;i++)p.tick();
        try{
            SchoolCombatGameTests.equip(p,"body",variant(h,"crab_soldier_shell_charm"));DynastyTrinkets.tick(p);
            h.assertTrue(InfusionCombat.armor(p).contains("retaliation"),"Actual Curios body slot exposes its original shell trait");
            float before=p.getHealth();boolean damaged=p.hurt(p.damageSources().mobAttack(z),300);h.assertTrue(damaged&&p.getHealth()<before&&z.hasEffect(MobEffects.WEAKNESS),"Actual native damage executes original worn-shell retaliation: damaged="+damaged+", health="+before+" -> "+p.getHealth()+", max="+p.getMaxHealth()+", weakness="+z.hasEffect(MobEffects.WEAKNESS));
            z.removeEffect(MobEffects.WEAKNESS);p.invulnerableTime=0;p.hurt(p.damageSources().mobAttack(z),300);h.assertTrue(!z.hasEffect(MobEffects.WEAKNESS),"Original eight-second cooldown is shared and remains finite");
            SchoolCombatGameTests.equip(p,"body",ItemStack.EMPTY);DynastyTrinkets.tick(p);InfusionCombat.logout(new PlayerEvent.PlayerLoggedOutEvent(p));p.invulnerableTime=0;p.hurt(p.damageSources().mobAttack(z),300);
            h.assertTrue(!z.hasEffect(MobEffects.WEAKNESS),"Removed armor charm cannot trigger even after cooldown ledger reset");h.succeed();
        }finally{close(p);z.discard();}
    }
}
