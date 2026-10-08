package com.dynasty;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.eventbus.api.*;
import net.minecraftforge.fml.common.Mod;
import java.util.Map;
/** Explicit encounter budgets, versioned old-save migration only while no target/recent damage exists. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class BossEncounterBalance {
    private static final Map<String,Double> HEALTH=Map.of("rebel_general",8000D,"eunuch_mastermind",10000D,"undead_first_emperor",16000D,
            "nine_heaven_general",18000D,"dragon_king",20000D,"dragon_emperor",24000D);
    private static void apply(Mob mob) {
        var id=net.minecraftforge.registries.ForgeRegistries.ENTITY_TYPES.getKey(mob.getType());
        if(id==null||!id.getNamespace().equals("dynasty")||!HEALTH.containsKey(id.getPath())||mob.getPersistentData().getInt("EncounterBalance")>=1)return;
        double ratio=mob.getHealth()/Math.max(1,mob.getMaxHealth());
        var health=mob.getAttribute(Attributes.MAX_HEALTH);if(health==null)return;
        health.setBaseValue(Math.max(health.getBaseValue(),HEALTH.get(id.getPath())));
        var attack=mob.getAttribute(Attributes.ATTACK_DAMAGE);if(attack!=null)attack.setBaseValue(attack.getBaseValue()*1.5);
        mob.setHealth((float)Math.min(mob.getMaxHealth(),mob.getMaxHealth()*ratio));mob.getPersistentData().putInt("EncounterBalance",1);
    }
    @SubscribeEvent(priority=EventPriority.HIGH) public static void join(EntityJoinLevelEvent e){if(!e.getLevel().isClientSide&&!e.loadedFromDisk()&&e.getEntity() instanceof Mob mob)apply(mob);}
    @SubscribeEvent public static void tick(LivingEvent.LivingTickEvent e){if(!e.getEntity().level().isClientSide&&e.getEntity() instanceof Mob mob&&mob.tickCount%40==0&&mob.getTarget()==null&&mob.hurtTime==0&&mob.tickCount-mob.getLastHurtByMobTimestamp()>200)apply(mob);}
    private BossEncounterBalance(){}
}
