package com.dynasty.infusion;

import java.util.*;
import com.mojang.authlib.GameProfile;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.item.*;
import net.minecraftforge.common.util.FakePlayer;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.gametest.*;
import net.minecraftforge.registries.ForgeRegistries;

@GameTestHolder("dynasty_infusion")
@PrefixGameTestTemplate(false)
public final class InfusionGameTests {
    private static Item item(String id){return ForgeRegistries.ITEMS.getValue(new ResourceLocation("dynasty",id));}
    private static FakePlayer player(GameTestHelper h){var p=new FakePlayer(h.getLevel(),new GameProfile(UUID.randomUUID(),"infusion-qa"));p.setPos(net.minecraft.world.phys.Vec3.atCenterOf(h.absolutePos(new BlockPos(2,2,2))));return p;}
    private static InfusionMenu menu(GameTestHelper h,net.minecraft.world.entity.player.Player p){var pos=p.blockPosition();h.getLevel().setBlockAndUpdate(pos,InfusionContent.TABLE.get().defaultBlockState());return new InfusionMenu(3,p.getInventory(),pos);}
    private static ItemStack gear(String id,Item type){return InfusionTraits.preview(new ItemStack(type),InfusionTraits.get(id),0,false);}
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="infusion")
    public static void all24ExistingMaterialsRoundTripWithoutTouchingForeignNbt(GameTestHelper h){
        h.assertTrue(InfusionTraits.ALL.size()==24,"24 profiles");
        for(var t:InfusionTraits.ALL){h.assertTrue(item(t.material())!=null&&item(t.material())!=Items.AIR,"Registered original material: "+t.material());
            var base=new ItemStack(t.kind()==InfusionTraits.Kind.ARMOR?Items.IRON_CHESTPLATE:Items.IRON_SWORD);base.setDamageValue(11);base.getOrCreateTag().putString("ForeignData","preserve");
            var out=InfusionTraits.preview(base,t,0,false);h.assertTrue(!out.isEmpty()&&InfusionTraits.active(out).contains(t.material()),"Active correct trait: "+t.material());
            var restored=ItemStack.of(out.save(new net.minecraft.nbt.CompoundTag()));
            h.assertTrue(restored.getDamageValue()==11&&restored.getTag().getString("ForeignData").equals("preserve")&&InfusionTraits.active(restored).contains(t.material()),"NBT survives serialization");
            var clean=InfusionTraits.preview(restored,null,0,true);h.assertTrue(ItemStack.isSameItemSameTags(base,clean),"Removal preserves original item exactly");}
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="infusion")
    public static void conflictCapacityAndIncompatibleEquipmentAreRejected(GameTestHelper h){
        var sword=gear("dragon_crystal",Items.IRON_SWORD);
        h.assertTrue(InfusionTraits.preview(sword,InfusionTraits.get("cinnabar"),1,false).isEmpty(),"Same spell family conflicts");
        sword=InfusionTraits.preview(sword,InfusionTraits.get("baihu_fang"),1,false);
        h.assertTrue(!sword.isEmpty()&&InfusionTraits.preview(sword,InfusionTraits.get("jade"),2,false).isEmpty(),"4 capacity cap");
        h.assertTrue(gear("ghost_face_fur",Items.IRON_SWORD).isEmpty(),"Armor effect cannot enter sword");
        h.assertTrue(gear("shanxiao_claw",Items.BOW).isEmpty()&&gear("baihu_fang",Items.CROSSBOW).isEmpty(),"Melee-only traits cannot waste bow capacity");
        h.assertTrue(gear("jade",Items.APPLE).isEmpty(),"Food cannot become equipment");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="infusion")
    public static void transactionConsumesOnceAndDuplicateClicksCannotDuplicateGear(GameTestHelper h){
        // Forge rejects advancement awards for FakePlayer; exercise the real server-player path.
        var p=new net.minecraft.server.level.ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"infusion-use"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.setPos(net.minecraft.world.phys.Vec3.atCenterOf(h.absolutePos(new BlockPos(2,2,2))));
        var adv=h.getLevel().getServer().getAdvancements().getAdvancement(new ResourceLocation("dynasty","get_jade"));p.getAdvancements().award(adv,"has_item");p.experienceLevel=9;
        var m=menu(h,p);m.getSlot(0).set(new ItemStack(Items.IRON_SWORD));m.getSlot(1).set(new ItemStack(item("cinnabar"),4));
        h.assertTrue(m.clickMenuButton(p,3),"Apply succeeds, status="+m.check(false));
        h.assertTrue(p.getAdvancements().getOrStartProgress(h.getLevel().getServer().getAdvancements().getAdvancement(new ResourceLocation("dynasty","first_infusion"))).isDone(),"First use advances existing task bridge");h.assertTrue(p.experienceLevel==6&&m.material().getCount()==2,"Exactly 2 materials, 3 XP levels");
        h.assertTrue(!m.clickMenuButton(p,3)&&p.experienceLevel==6&&m.material().getCount()==2,"Duplicate click is a no-op");
        h.assertTrue(m.clickMenuButton(p,4)&&p.experienceLevel==5&&InfusionTraits.active(m.gear()).isEmpty(),"Remove consumes only 1 level, no refund");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="infusion")
    public static void progressionOutOfRangeAndForeignPlayerCannotMutateInputs(GameTestHelper h){
        var p=player(h);var m=menu(h,p);m.getSlot(0).set(new ItemStack(Items.IRON_SWORD));m.getSlot(1).set(new ItemStack(item("cinnabar"),2));p.experienceLevel=9;
        h.assertTrue(!m.clickMenuButton(p,3)&&m.material().getCount()==2,"Base progression gates transaction");
        p.getAbilities().instabuild=true;var stranger=player(h);h.assertTrue(!m.clickMenuButton(stranger,3),"Menu belongs to owner");
        p.setPos(p.getX()+30,p.getY(),p.getZ());h.assertTrue(!m.clickMenuButton(p,3)&&m.material().getCount()==2,"Out of reach fails");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="infusion")
    public static void closingMenusReturnsEachPlayersInputsWithoutSharedStorage(GameTestHelper h){
        var a=player(h);var b=player(h);var one=menu(h,a);var two=menu(h,b);
        one.getSlot(0).set(new ItemStack(Items.IRON_SWORD));two.getSlot(0).set(new ItemStack(Items.IRON_CHESTPLATE));
        one.removed(a);two.removed(b);
        h.assertTrue(a.getInventory().countItem(Items.IRON_SWORD)==1&&a.getInventory().countItem(Items.IRON_CHESTPLATE)==0,"A gets only A gear");
        h.assertTrue(b.getInventory().countItem(Items.IRON_CHESTPLATE)==1,"B gets own gear");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="infusion")
    public static void defenseRequiresEquippedGearAndHasPlayerScopedCooldown(GameTestHelper h){
        var p=player(h);var zombie=new Zombie(EntityType.ZOMBIE,h.getLevel());p.getInventory().add(gear("swift_boot_scrap",Items.IRON_BOOTS));
        var hit=new LivingHurtEvent(p,p.damageSources().mobAttack(zombie),5);InfusionCombat.hurt(hit);
        h.assertTrue(!p.hasEffect(MobEffects.MOVEMENT_SPEED),"Inventory gear cannot grant effects");
        p.setItemSlot(EquipmentSlot.FEET,gear("swift_boot_scrap",Items.IRON_BOOTS));InfusionCombat.hurt(new LivingHurtEvent(p,p.damageSources().mobAttack(zombie),5));
        h.assertTrue(p.hasEffect(MobEffects.MOVEMENT_SPEED),"Equipped armor triggers");p.removeEffect(MobEffects.MOVEMENT_SPEED);
        p.setItemSlot(EquipmentSlot.FEET,gear("swift_boot_scrap",Items.IRON_BOOTS));InfusionCombat.hurt(new LivingHurtEvent(p,p.damageSources().mobAttack(zombie),5));
        h.assertTrue(!p.hasEffect(MobEffects.MOVEMENT_SPEED),"Swapping copies cannot reset cooldown");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="infusion")
    public static void originalMaterialRepairStillWorks(GameTestHelper h){
        var p=player(h);var anvil=new net.minecraft.world.inventory.AnvilMenu(0,p.getInventory());
        var axe=new ItemStack(Items.IRON_AXE);axe.setDamageValue(100);anvil.getSlot(0).set(axe);anvil.getSlot(1).set(new ItemStack(item("shanxiao_claw")));anvil.createResult();
        h.assertTrue(!anvil.getSlot(2).getItem().isEmpty()&&anvil.getSlot(2).getItem().getDamageValue()<100,"Existing anvil repair untouched");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="infusion")
    public static void everyOffensiveProfileExecutesItsDistinctCondition(GameTestHelper h){
        for(String id:List.of("shanxiao_claw","yin_jade_shard","vengeful_war_soul","dry_peach_branch","bronze_ingot","silver_ingot","jade","dragon_crystal","cinnabar","refined_steel","qinglong_scale","baihu_fang")){
            var p=new FakePlayer(h.getLevel(),new GameProfile(UUID.randomUUID(),"infusion-hit")){
                @Override public float getAttackStrengthScale(float partial){return 1f;}
            };
            p.setPos(net.minecraft.world.phys.Vec3.atCenterOf(h.absolutePos(new BlockPos(3,3,3))));
            var z=new Zombie(EntityType.ZOMBIE,h.getLevel());z.setPos(p.getX()+1,p.getY(),p.getZ());z.setHealth(5);
            z.setItemSlot(EquipmentSlot.CHEST,new ItemStack(Items.IRON_CHESTPLATE));z.setItemSlot(EquipmentSlot.MAINHAND,new ItemStack(Items.BOW));z.startUsingItem(net.minecraft.world.InteractionHand.MAIN_HAND);
            z.addEffect(new net.minecraft.world.effect.MobEffectInstance(MobEffects.INVISIBILITY,100));
            p.setItemSlot(EquipmentSlot.MAINHAND,gear(id,Items.IRON_SWORD));p.getFoodData().setFoodLevel(10);
            p.fallDistance=1;p.setOnGround(false);
            LivingHurtEvent hit=null;int times=id.equals("vengeful_war_soul")?4:id.equals("shanxiao_claw")||id.equals("jade")?3:id.equals("dragon_crystal")?2:1;
            for(int i=0;i<times;i++){
                InfusionCombat.attack(new net.minecraftforge.event.entity.player.AttackEntityEvent(p,z));
                hit=new LivingHurtEvent(z,p.damageSources().playerAttack(p),100);InfusionCombat.hurt(hit);
                // Real weapons lose durability between successive attacks.
                p.getMainHandItem().setDamageValue(i+1);
            }
            boolean ok=switch(id){
                case "shanxiao_claw","vengeful_war_soul","dragon_crystal","refined_steel","baihu_fang"->hit.getAmount()>100;
                case "yin_jade_shard"->z.hasEffect(MobEffects.MOVEMENT_SLOWDOWN);
                case "dry_peach_branch"->z.hasEffect(MobEffects.GLOWING)&&z.hasEffect(MobEffects.WEAKNESS);
                case "bronze_ingot"->!z.isUsingItem();
                case "silver_ingot"->!z.hasEffect(MobEffects.INVISIBILITY)&&z.hasEffect(MobEffects.GLOWING);
                case "jade"->p.getFoodData().getFoodLevel()==11;
                case "cinnabar"->z.isOnFire();
                case "qinglong_scale"->p.hasEffect(MobEffects.MOVEMENT_SPEED)&&p.hasEffect(MobEffects.JUMP);
                default->false;
            };
            h.assertTrue(ok,"Actual offensive trigger: "+id);
        }
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="infusion")
    public static void defensiveAndTalismanProfilesExecuteWithoutChangingMaterials(GameTestHelper h){
        for(String id:List.of("ghost_face_fur","nether_tatter","blackened_bone","dragon_scale","zhuque_feather","ink_stick","talisman_paper")){
            var p=player(h);p.setItemSlot(EquipmentSlot.CHEST,gear(id,Items.IRON_CHESTPLATE));p.getFoodData().setFoodLevel(10);
            var z=new Zombie(EntityType.ZOMBIE,h.getLevel());p.addEffect(new net.minecraft.world.effect.MobEffectInstance(MobEffects.POISON,100));
            var source=id.equals("nether_tatter")?p.damageSources().magic():id.equals("zhuque_feather")?p.damageSources().onFire():p.damageSources().mobAttack(z);
            var hit=new LivingHurtEvent(p,source,10);
            if(id.equals("ink_stick")||id.equals("talisman_paper")){
                p.setItemSlot(EquipmentSlot.MAINHAND,new ItemStack(item("fire_talisman")));
                InfusionCombat.hurt(new LivingHurtEvent(z,p.damageSources().indirectMagic(p,p),10));
            }else InfusionCombat.hurt(hit);
            boolean ok=switch(id){
                case "ghost_face_fur"->p.hasEffect(MobEffects.INVISIBILITY);
                case "nether_tatter"->hit.getAmount()==8&&p.hasEffect(MobEffects.SLOW_FALLING);
                case "blackened_bone"->!p.hasEffect(MobEffects.POISON)&&p.hasEffect(MobEffects.DAMAGE_RESISTANCE);
                case "dragon_scale"->p.hasEffect(MobEffects.ABSORPTION);
                case "zhuque_feather"->p.hasEffect(MobEffects.FIRE_RESISTANCE);
                case "ink_stick"->p.hasEffect(MobEffects.DAMAGE_RESISTANCE);
                case "talisman_paper"->p.getFoodData().getFoodLevel()==12;
                default->false;
            };
            h.assertTrue(ok,"Actual defensive/spell trigger: "+id);
        }
        h.succeed();
    }

    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="infusion")
    public static void shieldKnockbackAndFallProfilesHaveBoundedEffects(GameTestHelper h){
        var p=player(h);var z=new Zombie(EntityType.ZOMBIE,h.getLevel());
        p.setItemSlot(EquipmentSlot.CHEST,gear("heavy_shield_remnant",Items.IRON_CHESTPLATE));
        var block=new net.minecraftforge.event.entity.living.ShieldBlockEvent(p,p.damageSources().mobAttack(z),5);
        InfusionCombat.shield(block);h.assertTrue(!block.shieldTakesDamage(),"Remnant protects shield durability");
        p.setItemSlot(EquipmentSlot.CHEST,gear("xuanwu_shell",Items.IRON_CHESTPLATE));
        p.setItemSlot(EquipmentSlot.OFFHAND,new ItemStack(Items.SHIELD));p.startUsingItem(net.minecraft.world.InteractionHand.OFF_HAND);
        InfusionCombat.shield(new net.minecraftforge.event.entity.living.ShieldBlockEvent(p,p.damageSources().mobAttack(z),5));
        h.assertTrue(p.hasEffect(MobEffects.DAMAGE_RESISTANCE),"Timed block grants resistance");
        p.setItemSlot(EquipmentSlot.CHEST,gear("fine_steel_chain",Items.IRON_CHESTPLATE));p.setLastHurtByMob(z);
        var push=new net.minecraftforge.event.entity.living.LivingKnockBackEvent(p,1,1,0);InfusionCombat.knockback(push);
        h.assertTrue(push.getStrength()==.5f,"Chain halves knockback");
        p.setItemSlot(EquipmentSlot.CHEST,gear("taiyi_jade",Items.IRON_CHESTPLATE));
        var fall=new net.minecraftforge.event.entity.living.LivingFallEvent(p,10,1);InfusionCombat.fall(fall);
        h.assertTrue(fall.getDamageMultiplier()==.5f,"Wind halves fall damage");
        var again=new net.minecraftforge.event.entity.living.LivingFallEvent(p,10,1);InfusionCombat.fall(again);
        h.assertTrue(again.getDamageMultiplier()==1,"Wind cooldown cannot be bypassed");h.succeed();
    }

}
