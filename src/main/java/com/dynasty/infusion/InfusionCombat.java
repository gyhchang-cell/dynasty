package com.dynasty.infusion;

import java.util.*;
import com.dynasty.*;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.*;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.event.entity.living.*;
import net.minecraftforge.event.entity.player.*;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.*;
import net.minecraftforge.fml.common.Mod;

/** Server-only, bounded per-player cooldowns. No recursive damage, forced chunks or world edits. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class InfusionCombat {
    private static final Map<UUID,State> STATES=new HashMap<>();
    private static final String ARROW="DynastyInfusionArrow", ARROW_USED="DynastyInfusionArrowUsed";
    private static final class State {
        final Map<String,Long> cooldowns=new HashMap<>();
        UUID attackTarget,comboTarget;
        long attackTick=-1,comboTick=-100;
        float strength;
        int combo;
        ItemStack weapon=ItemStack.EMPTY,comboWeapon=ItemStack.EMPTY;
    }
    private static boolean sameWeapon(ItemStack a,ItemStack b){
        // Normal attacks consume durability; that must not erase a combo.
        var left=a.copy();var right=b.copy();left.removeTagKey("Damage");right.removeTagKey("Damage");
        return ItemStack.isSameItemSameTags(left,right);
    }
    private static State state(Player p){return STATES.computeIfAbsent(p.getUUID(),id->new State());}
    private static long now(Player p){return p.level().getGameTime();}
    public static boolean hostile(Player p,LivingEntity e){return e instanceof Enemy&&e.isAlive()&&e!=p&&!e.isAlliedTo(p)&&!(e instanceof Player);}
    private static boolean ready(Player p,String id,int ticks){var s=state(p);long n=now(p);if(n<s.cooldowns.getOrDefault(id,Long.MIN_VALUE))return false;s.cooldowns.put(id,n+ticks);return true;}
    private static boolean boss(LivingEntity e){return e instanceof DynastyBossCombat.BarHolder||!e.canChangeDimensions()||DynastyBalance.isBossOrBeast(e.getType());}
    private static void effect(LivingEntity e,MobEffect type,int ticks){e.addEffect(new MobEffectInstance(type,ticks,0));}
    private static void slow(LivingEntity e,int ticks){effect(e,MobEffects.MOVEMENT_SLOWDOWN,boss(e)?Math.min(20,ticks):ticks);}
    private static void cue(LivingEntity e,boolean lightning){if(e.level() instanceof net.minecraft.server.level.ServerLevel l)l.sendParticles(lightning?ParticleTypes.ELECTRIC_SPARK:ParticleTypes.ENCHANT,e.getX(),e.getY()+1,e.getZ(),8,.25,.35,.25,.01);}
    public static Set<String> armor(Player p){var ids=new HashSet<String>();for(var stack:p.getArmorSlots())ids.addAll(InfusionTraits.effects(stack));var curios=new ArrayList<ItemStack>();DynastyCuriosSetup.collectStacks(p,curios);for(var stack:curios)ids.addAll(InfusionTraits.effects(stack));if(p.isBlocking())ids.addAll(InfusionTraits.effects(p.getUseItem()));return ids;}
    @SubscribeEvent public static void attack(AttackEntityEvent e){
        Player p=e.getEntity();if(p.level().isClientSide)return;var s=state(p);
        s.attackTick=now(p);s.attackTarget=e.getTarget().getUUID();s.strength=p.getAttackStrengthScale(.5f);s.weapon=p.getMainHandItem().copy();
    }
    @SubscribeEvent public static void arrow(EntityJoinLevelEvent e){
        if(e.getLevel().isClientSide||!(e.getEntity() instanceof AbstractArrow arrow)||!(arrow.getOwner() instanceof Player p)||arrow.getPersistentData().contains(ARROW))return;
        ItemStack held=p.getUseItem();if(!(held.getItem() instanceof ProjectileWeaponItem))held=p.getMainHandItem();
        if(!(held.getItem() instanceof ProjectileWeaponItem))held=p.getOffhandItem();
        if(held.getItem() instanceof ProjectileWeaponItem)arrow.getPersistentData().put(ARROW,held.copy().save(new net.minecraft.nbt.CompoundTag()));
    }
    @SubscribeEvent(priority=EventPriority.LOWEST) public static void hurt(LivingHurtEvent e){
        if(e.isCanceled()||e.getAmount()<=0||e.getEntity().level().isClientSide||DynastyTrinketOnHit.isSyntheticDamage())return;
        if(e.getEntity() instanceof Player p)defend(p,e);
        if(!(e.getSource().getEntity() instanceof Player p)||!hostile(p,e.getEntity()))return;
        var target=e.getEntity();
        boolean spell=e.getSource().is(DamageTypes.INDIRECT_MAGIC)||e.getSource().is(DamageTypes.MAGIC);
        // Existing talismans use indirectMagic and don't have a mana pool: restore food, never invent one.
        if(spell&&(p.getMainHandItem().getItem() instanceof TalismanCharmItem||p.getOffhandItem().getItem() instanceof TalismanCharmItem)){
            var worn=armor(p);
            if(worn.contains("ink_stick")&&ready(p,"ink_stick",200)){effect(p,MobEffects.DAMAGE_RESISTANCE,60);cue(p,false);}
            if(worn.contains("talisman_paper")&&ready(p,"talisman_paper",240)){p.getFoodData().eat(2,0);cue(p,false);}
            return;
        }
        var s=state(p);ItemStack weapon;boolean ranged=false;
        if(e.getSource().getDirectEntity() instanceof AbstractArrow a&&a.getOwner()==p){
            if(a.getPersistentData().getBoolean(ARROW_USED)||!a.isCritArrow())return;
            a.getPersistentData().putBoolean(ARROW_USED,true);weapon=ItemStack.of(a.getPersistentData().getCompound(ARROW));ranged=true;
        }else{
            if(!e.getSource().is(DamageTypes.PLAYER_ATTACK)||e.getSource().getDirectEntity()!=p||s.attackTick!=now(p)||!target.getUUID().equals(s.attackTarget))return;
            s.attackTarget=null;
            if(s.strength<.9f||!ItemStack.isSameItemSameTags(s.weapon,p.getMainHandItem())||!p.hasLineOfSight(target))return;
            weapon=s.weapon;
        }
        var traits=new HashSet<>(InfusionTraits.effects(weapon));
        // Reuse this primary-hit combo and effect set: a worn fang is never another damage/proc pipeline.
        if(!ranged&&(weapon.getItem() instanceof TieredItem||weapon.getItem() instanceof TridentItem)){
            var worn=new ArrayList<ItemStack>();DynastyCuriosSetup.collectStacks(p,worn);
            for(var stack:worn)if(stack.is(com.dynasty.expansion.ExpansionContent.item("tiger_claw"))&&InfusionTraits.active(stack).contains("wolf_fang"))traits.add("shanxiao_claw");
        }
        if(traits.isEmpty())return;
        boolean same=target.getUUID().equals(s.comboTarget)&&now(p)-s.comboTick<=80&&sameWeapon(weapon,s.comboWeapon);
        s.combo=same?s.combo%12+1:1;s.comboTarget=target.getUUID();s.comboTick=now(p);s.comboWeapon=weapon.copy();
        double bonus=0;
        for(String id:traits){switch(id){
            case "shanxiao_claw" -> {if(!ranged&&s.combo%3==0&&ready(p,id,60)){bonus+=.15;slow(target,30);cue(target,false);}}
            case "yin_jade_shard" -> {if(target.getMobType()==MobType.UNDEAD&&ready(p,id,120)){slow(target,40);cue(target,false);}}
            case "vengeful_war_soul" -> {if(s.combo%4==0&&ready(p,id,80)){bonus+=.20;effect(target,MobEffects.WEAKNESS,boss(target)?20:40);cue(target,false);}}
            case "dry_peach_branch" -> {if(target.getMobType()==MobType.UNDEAD&&ready(p,id,120)){effect(target,MobEffects.GLOWING,80);effect(target,MobEffects.WEAKNESS,40);}}
            case "bronze_ingot" -> {if(target.isUsingItem()&&!boss(target)&&ready(p,id,160)){target.stopUsingItem();cue(target,false);}}
            case "silver_ingot" -> {if(target.hasEffect(MobEffects.INVISIBILITY)&&ready(p,id,120)){target.removeEffect(MobEffects.INVISIBILITY);effect(target,MobEffects.GLOWING,80);}}
            case "jade" -> {if(s.combo%3==0&&ready(p,id,200)){p.getFoodData().eat(1,0);cue(p,false);}}
            case "dragon_crystal" -> {if(s.combo%2==0&&ready(p,id,160)){bonus+=.12;slow(target,20);cue(target,true);}}
            case "cinnabar" -> {if(!target.fireImmune()&&ready(p,id,120)){target.setSecondsOnFire(3);cue(target,false);}}
            case "refined_steel" -> {if(target.getArmorValue()>0&&ready(p,id,100)){bonus+=.10;effect(target,MobEffects.WEAKNESS,20);cue(target,false);}}
            case "qinglong_scale" -> {if(target.getHealth()<target.getMaxHealth()*.5&&ready(p,id,160)){effect(p,MobEffects.MOVEMENT_SPEED,40);effect(p,MobEffects.JUMP,40);cue(p,false);}}
            case "baihu_fang" -> {if(!ranged&&p.fallDistance>0&&!p.onGround()&&!p.isInWater()&&!p.isSprinting()&&!p.hasEffect(MobEffects.BLINDNESS)&&ready(p,id,120)){bonus+=.15;if(!boss(target))target.knockback(.4,p.getX()-target.getX(),p.getZ()-target.getZ());cue(target,false);}}
            case "heavy_stagger" -> {if(!ranged&&s.combo%3==0&&ready(p,id,120)){slow(target,30);if(!boss(target)){target.stopUsingItem();target.knockback(.5,p.getX()-target.getX(),p.getZ()-target.getZ());}cue(target,false);}}
            case "venom" -> {if(s.combo%2==0&&target.getMobType()!=MobType.UNDEAD&&ready(p,id,160)){effect(target,MobEffects.POISON,60);cue(target,false);}}
            case "backstrike" -> {if(!ranged&&target.getLookAngle().dot(p.position().subtract(target.position()).normalize())<-.5&&ready(p,id,120)){effect(target,MobEffects.WEAKNESS,40);slow(target,40);cue(target,false);}}
            case "night_soul" -> {if(dark(p)&&ready(p,id,160)){effect(target,MobEffects.GLOWING,60);effect(target,MobEffects.WEAKNESS,boss(target)?20:60);cue(target,false);}}
            case "storm_call" -> {if(p.level().isThundering()&&ready(p,id,160)){effect(target,MobEffects.WEAKNESS,40);slow(target,40);cue(target,true);}}
            case "sunpurge" -> {if(p.level().isDay()&&target.getMobType()==MobType.UNDEAD&&ready(p,id,160)){if(!target.fireImmune())target.setSecondsOnFire(2);p.removeEffect(MobEffects.POISON);cue(target,false);}}
            case "hunter_mark" -> {if(ranged&&p.distanceToSqr(target)>=64&&ready(p,id,160)){effect(target,MobEffects.GLOWING,100);effect(p,MobEffects.MOVEMENT_SPEED,40);cue(target,false);}}
            case "air_step" -> {if(!ranged&&!p.onGround()&&ready(p,id,160)){effect(p,MobEffects.SLOW_FALLING,60);if(!boss(target))target.knockback(.4,p.getX()-target.getX(),p.getZ()-target.getZ());cue(p,false);}}
            case "soul_siphon" -> {if(dark(p)&&target.getMobType()==MobType.UNDEAD&&ready(p,id,200)){effect(target,MobEffects.WITHER,boss(target)?20:40);cue(target,false);}}
            default -> {}
        }}
        if(bonus>0)e.setAmount((float)Math.min(Float.MAX_VALUE,e.getAmount()*(1+Math.min(.35,bonus))));
    }
    private static boolean dark(Player p){return p.level().isNight()||p.level().dimension().location().getPath().equals("underworld");}
    private static void defend(Player p,LivingHurtEvent e){
        var traits=armor(p);boolean enemy=e.getSource().getEntity() instanceof LivingEntity attacker&&hostile(p,attacker);
        boolean heavy=e.getAmount()>=p.getMaxHealth()*.08;
        if(e.getSource().is(DamageTypes.FREEZE)&&(traits.contains("cold_ward")||com.dynasty.expansion.ExpansionSupplies.warm(p)))e.setAmount(e.getAmount()*.8f);
        if(enemy&&heavy&&traits.contains("ghost_face_fur")&&ready(p,"ghost_face_fur",240))effect(p,MobEffects.INVISIBILITY,40);
        if((e.getSource().is(DamageTypes.MAGIC)||e.getSource().is(DamageTypes.INDIRECT_MAGIC))&&traits.contains("nether_tatter")&&ready(p,"nether_tatter",160)){e.setAmount(e.getAmount()*.8f);effect(p,MobEffects.SLOW_FALLING,60);}
        if(enemy&&e.getSource().getEntity() instanceof LivingEntity a&&a.getMobType()==MobType.UNDEAD&&traits.contains("blackened_bone")&&ready(p,"blackened_bone",200)){p.removeEffect(MobEffects.POISON);effect(p,MobEffects.DAMAGE_RESISTANCE,40);}
        if(enemy&&traits.contains("swift_boot_scrap")&&ready(p,"swift_boot_scrap",160))effect(p,MobEffects.MOVEMENT_SPEED,40);
        if(enemy&&heavy&&traits.contains("dragon_scale")&&ready(p,"dragon_scale",240))effect(p,MobEffects.ABSORPTION,60);
        if(enemy&&p.isInWater()&&traits.contains("water_ward")&&ready(p,"water_ward",200)){effect(p,MobEffects.WATER_BREATHING,100);effect(p,MobEffects.DOLPHINS_GRACE,100);cue(p,false);}
        if(enemy&&p.getHealth()<=p.getMaxHealth()*.3&&traits.contains("last_stand")&&ready(p,"last_stand",240)){e.setAmount(e.getAmount()*.75f);effect(p,MobEffects.ABSORPTION,60);cue(p,false);}
        if(enemy&&heavy&&traits.contains("retaliation")&&ready(p,"retaliation",160)&&e.getSource().getEntity() instanceof LivingEntity a){if(!boss(a))a.knockback(.4,p.getX()-a.getX(),p.getZ()-a.getZ());effect(a,MobEffects.WEAKNESS,20);cue(a,false);}
        if(enemy&&p.hasEffect(MobEffects.POISON)&&traits.contains("poison_ward")&&ready(p,"poison_ward",200)){p.removeEffect(MobEffects.POISON);p.removeEffect(MobEffects.MOVEMENT_SLOWDOWN);cue(p,false);}
        if(enemy&&heavy&&traits.contains("lifebloom")&&ready(p,"lifebloom",240)){effect(p,MobEffects.REGENERATION,60);cue(p,false);}
        if(enemy&&e.getSource().getEntity() instanceof LivingEntity a&&a.getMobType()==MobType.UNDEAD&&traits.contains("wither_ward")&&ready(p,"wither_ward",200)){p.removeEffect(MobEffects.WITHER);p.removeEffect(MobEffects.WEAKNESS);cue(p,false);}
        if(e.getSource().is(DamageTypeTags.IS_FIRE)&&traits.contains("zhuque_feather")&&ready(p,"zhuque_feather",240)){p.clearFire();effect(p,MobEffects.FIRE_RESISTANCE,60);}
    }
    /** Original fox lining and finite warming wine share one nonstacking cold relief. */
    @SubscribeEvent public static void cold(net.minecraftforge.event.TickEvent.PlayerTickEvent e){
        if(e.phase!=net.minecraftforge.event.TickEvent.Phase.END||e.player.level().isClientSide||e.player.tickCount%20!=0)return;
        if(e.player.getTicksFrozen()>0&&(armor(e.player).contains("cold_ward")||com.dynasty.expansion.ExpansionSupplies.warm(e.player)))e.player.setTicksFrozen(Math.max(0,e.player.getTicksFrozen()-8));
    }
    @SubscribeEvent public static void shield(ShieldBlockEvent e){
        if(!(e.getEntity() instanceof Player p)||p.level().isClientSide||e.getBlockedDamage()<=0||!(e.getDamageSource().getEntity() instanceof LivingEntity a)||!hostile(p,a))return;
        var worn=armor(p);
        if(worn.contains("parry_cleanse")&&p.getTicksUsingItem()<=8&&ready(p,"parry_cleanse",160)){p.removeEffect(MobEffects.POISON);p.removeEffect(MobEffects.WEAKNESS);p.removeEffect(MobEffects.MOVEMENT_SLOWDOWN);cue(p,false);}
        if(worn.contains("heavy_shield_remnant")&&ready(p,"heavy_shield_remnant",120))e.setShieldTakesDamage(false);
        if(worn.contains("xuanwu_shell")&&p.getTicksUsingItem()<=8&&ready(p,"xuanwu_shell",200)){effect(p,MobEffects.DAMAGE_RESISTANCE,60);cue(p,false);}
    }
    @SubscribeEvent public static void knockback(LivingKnockBackEvent e){if(e.getEntity() instanceof Player p&&!p.level().isClientSide&&p.getLastHurtByMob()!=null&&hostile(p,p.getLastHurtByMob())&&armor(p).contains("fine_steel_chain")&&ready(p,"fine_steel_chain",100))e.setStrength(e.getStrength()*.5f);}
    @SubscribeEvent public static void fall(LivingFallEvent e){if(e.getEntity() instanceof Player p&&!p.level().isClientSide&&e.getDistance()>3&&armor(p).contains("taiyi_jade")&&ready(p,"taiyi_jade",160))e.setDamageMultiplier(e.getDamageMultiplier()*.5f);}
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){STATES.remove(e.getEntity().getUUID());}
    @SubscribeEvent public static void dimension(PlayerEvent.PlayerChangedDimensionEvent e){var s=STATES.get(e.getEntity().getUUID());if(s!=null){s.combo=0;s.attackTarget=null;s.comboTarget=null;}}
    @SubscribeEvent public static void death(LivingDeathEvent e){if(e.getEntity() instanceof Player p)STATES.remove(p.getUUID());}
    @SubscribeEvent public static void stop(ServerStoppedEvent e){STATES.clear();}
    private InfusionCombat(){}
}
