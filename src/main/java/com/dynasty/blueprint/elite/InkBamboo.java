package com.dynasty.blueprint.elite;

import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.phys.*;

/** Usable salvage: twenty-tick breath, a clear six-block sixty-degree cone, at most three clouds. */
public final class InkBamboo extends Item {
    public InkBamboo(){super(new Item.Properties().stacksTo(16));}
    @Override public UseAnim getUseAnimation(ItemStack stack){return UseAnim.TOOT_HORN;}
    @Override public int getUseDuration(ItemStack stack){return 20;}
    @Override public InteractionResultHolder<ItemStack> use(Level world,Player player,InteractionHand hand){player.startUsingItem(hand);return InteractionResultHolder.consume(player.getItemInHand(hand));}
    public static int disperse(Level world,LivingEntity user){
        if(world.isClientSide)return 0;int count=0;var eye=user.getEyePosition();var direction=user.getLookAngle();
        for(var cloud:world.getEntitiesOfClass(InkCloud.class,user.getBoundingBox().inflate(6))){var centre=cloud.position().add(0,.6,0);if(centre.distanceToSqr(eye)>36||centre.subtract(eye).normalize().dot(direction)<Math.cos(Math.toRadians(30))||world.clip(new ClipContext(eye,centre,ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,user)).getType()!=HitResult.Type.MISS)continue;cloud.discard();if(++count>=3)break;}return count;
    }
    @Override public ItemStack finishUsingItem(ItemStack stack,Level world,LivingEntity user){if(!world.isClientSide){disperse(world,user);if(user instanceof Player p){p.getCooldowns().addCooldown(this,40);if(!p.getAbilities().instabuild)stack.shrink(1);}else stack.shrink(1);}return stack;}
}
