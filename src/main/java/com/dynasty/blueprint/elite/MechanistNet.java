package com.dynasty.blueprint.elite;

import net.minecraft.world.effect.*;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.InteractionResult;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraftforge.event.entity.EntityTeleportEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Finite server status; ordinary walking, looking and attacking remain available. */
@Mod.EventBusSubscriber(modid="dynasty")
public final class MechanistNet extends MobEffect {
    public MechanistNet(){super(MobEffectCategory.HARMFUL,0x79D5DE);
        addAttributeModifier(Attributes.MOVEMENT_SPEED,"c50c9803-c6b5-4d0f-9f59-3287b5894af1",-.9,AttributeModifier.Operation.MULTIPLY_TOTAL);}
    public static boolean allowsDisplacement(LivingEntity entity){return !entity.hasEffect(EliteContent.THREAD_NET.get());}
    @SubscribeEvent public static void use(PlayerInteractEvent.RightClickItem event){
        var tag=TagKey.create(Registries.ITEM,new ResourceLocation("dynasty","movement_abilities"));
        if(!allowsDisplacement(event.getEntity())&&event.getItemStack().is(tag)){
            event.setCancellationResult(InteractionResult.FAIL);event.setCanceled(true);
        }
    }
    @SubscribeEvent public static void teleport(EntityTeleportEvent event){
        if(event.isCancelable()&&event.getEntity() instanceof LivingEntity living&&!allowsDisplacement(living))event.setCanceled(true);
    }
}
