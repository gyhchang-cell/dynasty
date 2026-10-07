package com.dynasty.expansion;

import com.dynasty.*;
import net.minecraft.nbt.*;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.*;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.phys.*;
import net.minecraft.world.effect.*;
import net.minecraft.sounds.*;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.function.Predicate;

@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class ExpansionWeapons {
    public static boolean enemy(Player player, LivingEntity target) {
        return target!=player && target.isAlive() && !(target instanceof Player) && !player.isAlliedTo(target) && !target.isAlliedTo(player);
    }
    public static final class SpecialArrow extends ArrowItem {
        private final String kind;
        SpecialArrow(String kind) { super(new Properties());this.kind=kind; }
        @Override public AbstractArrow createArrow(Level level,ItemStack stack,LivingEntity shooter) {
            var arrow=super.createArrow(level,stack,shooter);
            arrow.getPersistentData().putString("cod4Ammo",kind);
            if(kind.equals("pierce_arrow") || kind.equals("heavy_bolt")) arrow.setPierceLevel((byte)1);
            if(kind.equals("poison_arrow") && arrow instanceof Arrow a) a.addEffect(new MobEffectInstance(MobEffects.POISON,100,0));
            return arrow;
        }
    }
    public static final class BurstCrossbow extends CrossbowItem {
        private final boolean siege;
        BurstCrossbow(boolean siege) { super(new Properties().durability(siege?2200:1600));this.siege=siege; }
        @Override public Predicate<ItemStack> getAllSupportedProjectiles() {
            return s -> s.getItem() instanceof ArrowItem && (!isBolt(s) || s.is(ExpansionContent.AMMO.get(siege?"heavy_bolt":"repeating_bolt").get()));
        }
        @Override public Predicate<ItemStack> getSupportedHeldProjectiles() { return getAllSupportedProjectiles(); }
        @Override public int getUseDuration(ItemStack stack) { return 72000; }
        @Override public InteractionResultHolder<ItemStack> use(Level level,Player p,InteractionHand hand) {
            ItemStack stack=p.getItemInHand(hand);
            if(!isCharged(stack) && p.getProjectile(stack).isEmpty() && !p.getAbilities().instabuild) return InteractionResultHolder.fail(stack);
            p.startUsingItem(hand);return InteractionResultHolder.consume(stack);
        }
        @Override public void releaseUsing(ItemStack stack,Level level,LivingEntity user,int remaining) {
            if(level.isClientSide || !(user instanceof Player p) || isCharged(stack) || getUseDuration(stack)-remaining < CrossbowItem.getChargeDuration(stack)) return;
            ListTag magazine=new ListTag();
            for(int n=0;n<(siege?1:3);n++) {
                ItemStack ammo=p.getProjectile(stack);
                if(ammo.isEmpty()) { if(!p.getAbilities().instabuild) break; ammo=new ItemStack(Items.ARROW); }
                ItemStack shot=ammo.copy();shot.setCount(1);magazine.add(shot.save(new CompoundTag()));
                if(!p.getAbilities().instabuild) ammo.shrink(1);
            }
            if(!magazine.isEmpty()) { stack.getOrCreateTag().put("cod4Magazine",magazine);setCharged(stack,true);level.playSound(null,p.blockPosition(),SoundEvents.CROSSBOW_LOADING_END,SoundSource.PLAYERS,1,1); }
        }
        @Override public void onUseTick(Level level,LivingEntity user,ItemStack stack,int remaining) {
            if(level.isClientSide || !(user instanceof Player p) || !isCharged(stack) || (getUseDuration(stack)-remaining)%6!=0) return;
            ListTag magazine=stack.getOrCreateTag().getList("cod4Magazine",Tag.TAG_COMPOUND);
            if(magazine.isEmpty()) { setCharged(stack,false);p.stopUsingItem();return; }
            ItemStack ammo=ItemStack.of(magazine.getCompound(0));magazine.remove(0);
            if(!(ammo.getItem() instanceof ArrowItem item)) { setCharged(stack,false);p.stopUsingItem();return; }
            AbstractArrow arrow=item.createArrow(level,ammo,p);
            arrow.shootFromRotation(p,p.getXRot(),p.getYRot(),0,3.15F,siege?.2F:1F);
            arrow.setBaseDamage((siege?900:260)/3.15);arrow.setShotFromCrossbow(true);
            arrow.setPierceLevel((byte)Math.max(arrow.getPierceLevel(),siege?2:0));
            arrow.pickup=p.getAbilities().instabuild?AbstractArrow.Pickup.CREATIVE_ONLY:AbstractArrow.Pickup.ALLOWED;
            arrow.getPersistentData().putBoolean("cod4Siege",siege);
            arrow.getPersistentData().put("cod4FiringWeapon",stack.save(new CompoundTag()));
            level.addFreshEntity(arrow);
            if(siege) { p.push(-p.getLookAngle().x*.25,0,-p.getLookAngle().z*.25);p.hurtMarked=true; }
            stack.hurtAndBreak(1,p,e->e.broadcastBreakEvent(p.getUsedItemHand()));
            level.playSound(null,p.blockPosition(),SoundEvents.CROSSBOW_SHOOT,SoundSource.PLAYERS,1,siege?.7F:1.2F);
            if(magazine.isEmpty()) { setCharged(stack,false);p.stopUsingItem(); }
        }
    }
    public static boolean isBolt(ItemStack s) {
        return s.is(ExpansionContent.AMMO.get("heavy_bolt").get()) || s.is(ExpansionContent.AMMO.get("repeating_bolt").get());
    }
    public static final class QimenSword extends SwordItem {
        private final String kind;
        QimenSword(String kind,int damage,float speed) { super(DynastyTiers.JADE,damage-71,speed,new Properties());this.kind=kind; }
        @Override public UseAnim getUseAnimation(ItemStack stack) { return kind.equals("mandarin_duck_axe")?UseAnim.BLOCK:UseAnim.NONE; }
        @Override public int getUseDuration(ItemStack stack) { return 72000; }
        @Override public InteractionResultHolder<ItemStack> use(Level level,Player p,InteractionHand hand) {
            ItemStack stack=p.getItemInHand(hand);
            if(p.getCooldowns().isOnCooldown(this)) return InteractionResultHolder.fail(stack);
            if(kind.equals("mandarin_duck_axe")) { p.startUsingItem(hand);return InteractionResultHolder.consume(stack); }
            if(level.isClientSide) return InteractionResultHolder.success(stack);
            Vec3 start=p.getEyePosition(),end=start.add(p.getLookAngle().scale(12));
            BlockHitResult block=level.clip(new ClipContext(start,end,ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,p));
            Vec3 limit=block.getLocation();
            var hit=ProjectileUtil.getEntityHitResult(level,p,start,limit,new AABB(start,limit).inflate(1),e->e instanceof LivingEntity l && enemy(p,l));
            if(hit!=null && hit.getEntity() instanceof LivingEntity target) {
                CombatFeedback.tether(p,hit.getLocation());
                if(ExpansionEffects.boss(target)) CombatFeedback.send(target,CombatFeedback.IMMUNE);
                else { Vec3 pull=p.position().subtract(target.position()).normalize().scale(.65);target.setDeltaMovement(pull.x,.18,pull.z);target.hurtMarked=true;ExpansionEffects.apply(target,ExpansionEffects.STAGGER,40);CombatFeedback.send(target,CombatFeedback.KNOCKDOWN); }
            } else if(kind.equals("flying_claw") && block.getType()==HitResult.Type.BLOCK) {
                // Physical velocity, never a teleport through a wall. Normal collision remains active.
                CombatFeedback.tether(p,limit);
                Vec3 pull=limit.subtract(start).normalize().scale(.9);p.setDeltaMovement(pull);p.hurtMarked=true;
            } else return InteractionResultHolder.pass(stack);
            p.getCooldowns().addCooldown(this,EquipmentBehaviors.cooldown(p,40));stack.hurtAndBreak(1,p,e->e.broadcastBreakEvent(hand));
            return InteractionResultHolder.success(stack);
        }
    }
    public static final class MeteorHammer extends AxeItem {
        MeteorHammer() { super(DynastyTiers.DRAGON_CRYSTAL,959,-2.8F,new Properties()); }
        @Override public UseAnim getUseAnimation(ItemStack s) { return UseAnim.BOW; }
        @Override public int getUseDuration(ItemStack s) { return 72000; }
        @Override public InteractionResultHolder<ItemStack> use(Level level,Player p,InteractionHand hand) { p.startUsingItem(hand);return InteractionResultHolder.consume(p.getItemInHand(hand)); }
        @Override public void releaseUsing(ItemStack stack,Level level,LivingEntity user,int remaining) {
            if(level.isClientSide || !(user instanceof Player p) || getUseDuration(stack)-remaining<20) return;
            for(var target:level.getEntitiesOfClass(LivingEntity.class,p.getBoundingBox().inflate(4),t->enemy(p,t)&&p.hasLineOfSight(t))) {
                target.hurt(p.damageSources().playerAttack(p),(float)p.getAttributeValue(net.minecraft.world.entity.ai.attributes.Attributes.ATTACK_DAMAGE)*.6F);
                if(!ExpansionEffects.boss(target)) target.knockback(.6,p.getX()-target.getX(),p.getZ()-target.getZ());
            }
            CombatFeedback.send(p,CombatFeedback.HEAVY);p.getCooldowns().addCooldown(this,EquipmentBehaviors.cooldown(p,80));stack.hurtAndBreak(3,p,e->e.broadcastBreakEvent(p.getUsedItemHand()));
        }
    }
    @SubscribeEvent public static void ammoHit(LivingHurtEvent e) {
        if(e.getEntity().level().isClientSide || !(e.getSource().getDirectEntity() instanceof AbstractArrow arrow)) return;
        String kind=arrow.getPersistentData().getString("cod4Ammo");
        if(kind.equals("thunder_arrow")) ExpansionEffects.apply(e.getEntity(),ExpansionEffects.THUNDER,60);
        if(kind.equals("pierce_arrow") || kind.equals("heavy_bolt") || arrow.getPersistentData().getBoolean("cod4Siege")) ExpansionEffects.apply(e.getEntity(),ExpansionEffects.BREAK,80);
    }
    private ExpansionWeapons() { }
}
