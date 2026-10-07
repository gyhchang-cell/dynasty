package com.dynasty.blueprint;

import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraftforge.event.entity.living.LivingEntityUseItemEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Temporary item-use denial on both hands, without blocking movement, attacks, inventory or camera. */
@Mod.EventBusSubscriber(modid="dynasty")
public final class ColdPoolCoilEffect extends MobEffect {
    public ColdPoolCoilEffect(){
        super(MobEffectCategory.HARMFUL,0x388C82);
        addAttributeModifier(Attributes.MOVEMENT_SPEED,"df824dbf-de3c-4346-a6cb-dfd2216e0521",-.5,AttributeModifier.Operation.MULTIPLY_TOTAL);
    }
    @SubscribeEvent public static void start(LivingEntityUseItemEvent.Start event){
        if(event.getEntity().hasEffect(BlueprintEntities.COLD_POOL_COIL.get()))event.setCanceled(true);
    }
    @SubscribeEvent public static void item(PlayerInteractEvent.RightClickItem event){
        if(event.getEntity().hasEffect(BlueprintEntities.COLD_POOL_COIL.get()))event.setCanceled(true);
    }
    @SubscribeEvent public static void block(PlayerInteractEvent.RightClickBlock event){
        if(event.getEntity().hasEffect(BlueprintEntities.COLD_POOL_COIL.get()))event.setCanceled(true);
    }
    @SubscribeEvent public static void entity(PlayerInteractEvent.EntityInteract event){
        if(event.getEntity().hasEffect(BlueprintEntities.COLD_POOL_COIL.get()))event.setCanceled(true);
    }
    @SubscribeEvent public static void entityAt(PlayerInteractEvent.EntityInteractSpecific event){
        if(event.getEntity().hasEffect(BlueprintEntities.COLD_POOL_COIL.get()))event.setCanceled(true);
    }
}
