package com.dynasty.expansion;

import com.dynasty.*;
import com.dynasty.entity.ImperialSoldier;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid="dynasty")
public final class AccessoryActions {
    @SubscribeEvent public static void use(PlayerInteractEvent.RightClickItem e) {
        if(!(e.getEntity() instanceof ServerPlayer p))return;
        String id=EquipmentBehaviors.id(e.getItemStack());
        if(id.equals("cinnabar") && p.hasEffect(ExpansionEffects.SHA.get())) {
            p.removeEffect(ExpansionEffects.SHA.get());if(!p.getAbilities().instabuild)e.getItemStack().shrink(1);
            e.setCanceled(true);e.setCancellationResult(InteractionResult.SUCCESS);CombatFeedback.send(p,CombatFeedback.HEAL);return;
        }
        if(!id.equals("south_pointing_compass") && !id.equals("tiger_crest"))return;
        e.setCanceled(true);e.setCancellationResult(InteractionResult.SUCCESS);
        if(!EquipmentBehaviors.ready(p,"use_"+id,id.equals("tiger_crest")?6000:1200))return;
        if(id.equals("south_pointing_compass"))ExpansionSupplies.locate(p);
        else {
            var troops=p.level().getEntitiesOfClass(ImperialSoldier.class,p.getBoundingBox().inflate(32),s->s.getOwner()==p);
            if(!troops.isEmpty())return;
            DynastyArmy.formUp(p,"square",3);
        }
    }
    @SubscribeEvent public static void expire(LivingEvent.LivingTickEvent e) {
        var entity=e.getEntity();if(entity.level().isClientSide||!entity.getPersistentData().contains("cod4TallyExpires"))return;
        // The legacy accessory now deploys paid roster members. Its old temporary-summon lease
        // must never remove a purchased carrier, including leases saved by an earlier build.
        if(entity.getPersistentData().hasUUID("ArmySoldier")){entity.getPersistentData().remove("cod4TallyExpires");return;}
        if(entity.level().getGameTime()>=entity.getPersistentData().getLong("cod4TallyExpires"))entity.discard();
    }
    private AccessoryActions() { }
}
