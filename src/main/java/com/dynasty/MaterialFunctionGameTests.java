package com.dynasty;

import com.dynasty.expansion.ExpansionContent;
import com.dynasty.infusion.*;
import com.mojang.authlib.GameProfile;
import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.item.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.common.util.FakePlayer;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.gametest.*;

/** Existing paid infusion transactions, equipment-owned NBT and real Curios when installed. */
@GameTestHolder("dynasty_cod4") @PrefixGameTestTemplate(false)
public final class MaterialFunctionGameTests {
    private static ServerPlayer player(GameTestHelper h){
        var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"material-native"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.setPos(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(2,2,2))));return p;
    }
    private static ItemStack infused(String material,ItemStack base){return InfusionTraits.preview(base,InfusionTraits.get(material),0,false);}
    @GameTest(template="bow_ritual_test",batch="cod4_material_functions",setupTicks=20)
    public static void foxPeltUsesPaidNativeMenuAndPreservesDyedInvestedLeatherExactly(GameTestHelper h){
        var p=player(h);p.getAdvancements().award(p.server.getAdvancements().getAdvancement(new ResourceLocation("dynasty","get_jade")),"has_item");p.experienceLevel=9;
        var pos=p.blockPosition();h.getLevel().setBlockAndUpdate(pos,InfusionContent.TABLE.get().defaultBlockState());
        var menu=new InfusionMenu(23,p.getInventory(),pos);p.containerMenu=menu;
        var original=new ItemStack(Items.LEATHER_CHESTPLATE);original.setDamageValue(31);((DyeableLeatherItem)original.getItem()).setColor(original,0x773355);
        original.getOrCreateTagElement(DynastyWeaponProgression.KEY).putUUID("identity",UUID.randomUUID());original.getOrCreateTag().putString("ForeignData","keep");
        menu.getSlot(0).set(original.copy());menu.getSlot(1).set(new ItemStack(ExpansionContent.item("fox_pelt"),4));menu.broadcastChanges();
        h.assertTrue(menu.request(p,0,-1,menu.revision()),"Actual registered infusion menu accepts fox pelt on leather");
        h.assertTrue(p.experienceLevel==6&&menu.material().getCount()==2&&InfusionTraits.effects(menu.gear()).contains("cold_ward"),"Existing transaction charges exactly two fox pelts and three levels");
        h.assertTrue(!menu.request(p,0,-1,menu.revision())&&p.experienceLevel==6&&menu.material().getCount()==2,"Repeated apply cannot repay or duplicate the warmth trait");
        var saved=ItemStack.of(menu.gear().save(new net.minecraft.nbt.CompoundTag()));h.assertTrue(saved.getDamageValue()==31&&saved.getTag().getCompound(DynastyWeaponProgression.KEY).equals(original.getTag().getCompound(DynastyWeaponProgression.KEY)),"Actual upgrade preserves invested identity and does not repair damage");
        h.assertTrue(menu.request(p,1,0,menu.revision())&&ItemStack.isSameItemSameTags(original,menu.gear()),"Native removal returns exact original dye, foreign data and investment without material refund");
        h.assertTrue(infused("fox_pelt",new ItemStack(Items.IRON_CHESTPLATE)).isEmpty()&&infused("fox_pelt",new ItemStack(Items.SHIELD)).isEmpty(),"Leather-only applicability is enforced on the server");
        h.assertTrue(!infused("fox_pelt",new ItemStack(ExpansionContent.item("leather_chestplate"))).isEmpty(),"Existing Dynasty leather armor also accepts lining");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_material_functions",setupTicks=20)
    public static void foxLiningOnlyProtectsWornLeatherAndNeverStacksOrLingers(GameTestHelper h){
        var p=new FakePlayer(h.getLevel(),new GameProfile(UUID.randomUUID(),"warmth"));var chest=infused("fox_pelt",new ItemStack(Items.LEATHER_CHESTPLATE));p.getInventory().add(chest.copy());
        var bare=new LivingHurtEvent(p,p.damageSources().freeze(),10);InfusionCombat.hurt(bare);h.assertTrue(bare.getAmount()==10,"Inventory lining never grants cold defense");
        p.setItemSlot(EquipmentSlot.CHEST,chest);p.setItemSlot(EquipmentSlot.FEET,infused("fox_pelt",new ItemStack(Items.LEATHER_BOOTS)));
        var protectedHit=new LivingHurtEvent(p,p.damageSources().freeze(),10);InfusionCombat.hurt(protectedHit);h.assertTrue(protectedHit.getAmount()==8,"Multiple worn copies grant exactly one twenty-percent reduction");
        p.tickCount=20;p.setTicksFrozen(100);InfusionCombat.cold(new TickEvent.PlayerTickEvent(TickEvent.Phase.END,p));h.assertTrue(p.getTicksFrozen()==92,"Actual equipped lining reduces only eight accumulated ticks per second");
        p.setItemSlot(EquipmentSlot.CHEST,ItemStack.EMPTY);p.setItemSlot(EquipmentSlot.FEET,ItemStack.EMPTY);var removed=new LivingHurtEvent(p,p.damageSources().freeze(),10);InfusionCombat.hurt(removed);InfusionCombat.cold(new TickEvent.PlayerTickEvent(TickEvent.Phase.END,p));
        h.assertTrue(removed.getAmount()==10&&p.getTicksFrozen()==92,"Unequipping immediately stops both effects without a lingering blanket immunity");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_material_functions",setupTicks=20)
    public static void wolfFangUsesExistingPursuitComboAndRejectsDuplicateOrRangedWaste(GameTestHelper h){
        var p=new FakePlayer(h.getLevel(),new GameProfile(UUID.randomUUID(),"wolf-infusion")){@Override public float getAttackStrengthScale(float partial){return 1;}};
        p.setPos(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(2,2,2))));var target=new Zombie(h.getLevel());target.setPos(p.getX()+1,p.getY(),p.getZ());
        var sword=infused("wolf_fang",new ItemStack(Items.IRON_SWORD));p.setItemSlot(EquipmentSlot.MAINHAND,sword);
        h.assertTrue(InfusionTraits.preview(sword,InfusionTraits.get("shanxiao_claw"),1,false).isEmpty()&&infused("wolf_fang",new ItemStack(Items.BOW)).isEmpty(),"Existing family/duplicate-effect and melee-only checks prevent stacking or wasted ranged capacity");
        for(int i=0;i<3;i++){
            InfusionCombat.attack(new net.minecraftforge.event.entity.player.AttackEntityEvent(p,target));var hit=new LivingHurtEvent(target,p.damageSources().playerAttack(p),100);InfusionCombat.hurt(hit);
            h.assertTrue(Math.abs(hit.getAmount()-(i==2?115:100))<.001,"Wolf fang reuses original third-hit pursuit behavior exactly");p.getMainHandItem().setDamageValue(i+1);
        }
        h.assertTrue(target.hasEffect(MobEffects.MOVEMENT_SLOWDOWN),"Successful combo applies existing finite pursuit slow");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_material_functions",setupTicks=20)
    public static void crabShellUpgradesOriginalDragonPalaceArmorWithBoundedRetaliation(GameTestHelper h){
        var p=new FakePlayer(h.getLevel(),new GameProfile(UUID.randomUUID(),"crab-infusion"));p.setPos(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(2,2,2))));
        var original=new ItemStack(ExpansionContent.item("sea_silk_chestplate"));original.setDamageValue(23);original.getOrCreateTag().putString("ForeignData","sea");var upgraded=infused("crab_shell",original);
        h.assertTrue(!upgraded.isEmpty()&&upgraded.getDamageValue()==23&&upgraded.getTag().getString("ForeignData").equals("sea"),"Actual existing Dragon Palace light armor keeps ID, durability and data");
        p.setItemSlot(EquipmentSlot.CHEST,upgraded);var enemy=new Zombie(h.getLevel());enemy.setPos(p.getX()+1,p.getY(),p.getZ());
        InfusionCombat.hurt(new LivingHurtEvent(p,p.damageSources().mobAttack(enemy),5));h.assertTrue(enemy.hasEffect(MobEffects.WEAKNESS)&&enemy.getDeltaMovement().horizontalDistanceSqr()>0,"Original retaliation executes on a real hostile heavy-hit source");
        enemy.removeEffect(MobEffects.WEAKNESS);enemy.setDeltaMovement(Vec3.ZERO);InfusionCombat.hurt(new LivingHurtEvent(p,p.damageSources().mobAttack(enemy),5));
        h.assertTrue(!enemy.hasEffect(MobEffects.WEAKNESS)&&enemy.getDeltaMovement().lengthSqr()==0,"Original player-owned cooldown cannot be bypassed by another hit");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_material_water",setupTicks=20,timeoutTicks=50)
    public static void kappaScaleUpgradesActualSeaPearlAndWaterArmorWithoutReplacingExistingEffects(GameTestHelper h){
        var pearl=infused("kappa_scale",new ItemStack(ExpansionContent.item("sea_pearl")));h.assertTrue(!pearl.isEmpty()&&InfusionTraits.effects(ItemStack.of(pearl.save(new net.minecraft.nbt.CompoundTag()))).contains("water_ward"),"Original non-damageable sea pearl receives persistent equipment-owned upgrade");
        var p=player(h);var pos=p.blockPosition();h.getLevel().setBlockAndUpdate(pos,Blocks.WATER.defaultBlockState());p.setNoGravity(true);p.doTick();h.assertTrue(p.isInWater(),"Actual loaded water establishes the combat condition");
        if(DynastyCuriosSetup.isLoaded())SchoolCombatGameTests.equip(p,"charm",pearl);
        else p.setItemSlot(EquipmentSlot.CHEST,infused("kappa_scale",new ItemStack(Items.IRON_CHESTPLATE)));
        var enemy=new Zombie(h.getLevel());enemy.setPos(p.getX()+1,p.getY(),p.getZ());InfusionCombat.hurt(new LivingHurtEvent(p,p.damageSources().mobAttack(enemy),5));
        h.assertTrue(p.hasEffect(MobEffects.WATER_BREATHING)&&p.hasEffect(MobEffects.DOLPHINS_GRACE),"Actual worn upgrade uses existing water-ward combat trigger");
        p.removeEffect(MobEffects.DOLPHINS_GRACE);InfusionCombat.hurt(new LivingHurtEvent(p,p.damageSources().mobAttack(enemy),5));h.assertTrue(!p.hasEffect(MobEffects.DOLPHINS_GRACE),"Shared native cooldown remains bounded");
        if(DynastyCuriosSetup.isLoaded()){
            DynastyTrinkets.tick(p);h.assertTrue(p.hasEffect(MobEffects.WATER_BREATHING)&&p.hasEffect(MobEffects.DOLPHINS_GRACE),"Original sea-pearl passive remains alongside its new combat upgrade");SchoolCombatGameTests.equip(p,"charm",ItemStack.EMPTY);
        }
        p.setItemSlot(EquipmentSlot.CHEST,ItemStack.EMPTY);p.removeEffect(MobEffects.WATER_BREATHING);p.removeEffect(MobEffects.DOLPHINS_GRACE);
        InfusionCombat.hurt(new LivingHurtEvent(p,p.damageSources().mobAttack(enemy),5));h.assertTrue(!p.hasEffect(MobEffects.WATER_BREATHING),"Removed equipment has no hidden upgrade effect");h.succeed();
    }
}
