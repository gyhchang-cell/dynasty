// ClientPacketHandler.java
package net.sam.simple_combat_indicators.networking;

import net.minecraft.client.Minecraft;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.sam.simple_combat_indicators.config.ClientConfig;
import net.sam.simple_combat_indicators.render.DamageIndicatorRenderer;
import net.sam.simple_combat_indicators.util.ConfigUtils;
import net.sam.simple_combat_indicators.util.DamageDealtIndicator;
import net.sam.simple_combat_indicators.util.DamageTakenIndicator;


public class ClientPacketHandler {
    public static void handleS2CAttackedPacket(int attackerId, int receiverId, float damage) {

        Player play1er = Minecraft.getInstance().player;
        Level level = Minecraft.getInstance().level;
        if (level == null) return;
        Player player = Minecraft.getInstance().player;

        //client player dealt damage
        if(player.getId() == attackerId){
            boolean numbers_enabled = ConfigUtils.getOrDefault(ClientConfig.ENABLE_DAMAGE_NUMBERS);
            if(!numbers_enabled){return;}

            Entity entity = level.getEntity(receiverId);
            if ((entity instanceof LivingEntity livingEntity)) {
                int entityId = livingEntity.getId();

                boolean stackingDamage = ClientConfig.STACKING_NUMBERS.get();
                if(stackingDamage){
                    boolean found = false;
                    for (DamageDealtIndicator dmg : DamageIndicatorRenderer.damageDealtIndicators) {
                        if(dmg.target == livingEntity){
                            DamageIndicatorRenderer.damageDealtIndicators.add(new DamageDealtIndicator(entityId,livingEntity,damage, damage + dmg.totalDamage, DamageDealtIndicator.baseScale + DamageDealtIndicator.incrementScale));
                            DamageIndicatorRenderer.damageDealtIndicators.remove(dmg);
                            found = true;
                            break;
                        }
                    }
                    if(!found){
                        DamageIndicatorRenderer.damageDealtIndicators.add(new DamageDealtIndicator(entityId, livingEntity, damage,damage, DamageDealtIndicator.baseScale + DamageDealtIndicator.incrementScale));
                    }
                }else{
                    DamageIndicatorRenderer.damageDealtIndicators.add(new DamageDealtIndicator(entityId, livingEntity, damage,damage, DamageDealtIndicator.baseScale + DamageDealtIndicator.incrementScale));
                }

            }

        }
        //client player take damage
        else if(player.getId() == receiverId){
            boolean indicator_enabled = ConfigUtils.getOrDefault(ClientConfig.ENABLE_DAMAGE_TAKEN_INDICATOR);
            if(!indicator_enabled){return;}
            Entity entity = level.getEntity(attackerId);
            if (entity != null) {
                int entityId = entity.getId();
                DamageIndicatorRenderer.damageTakenIndicators.add(new DamageTakenIndicator(entityId, entity, damage));
            }
        }
    }
}
