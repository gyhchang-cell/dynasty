package artifacts.neoforge.event;

import artifacts.component.ability.ToolTierUpgrade;
import artifacts.equipment.EquipmentSlotManager;
import artifacts.event.ArtifactHooks;
import artifacts.integration.ModCompat;
import artifacts.registry.ModDataComponents;
import artifacts.registry.ModTags;
import artifacts.util.TooltipHelper;
import be.florens.expandability.api.EventResult;
import be.florens.expandability.api.forge.LivingFluidCollisionEvent;
import be.florens.expandability.api.forge.PlayerSwimEvent;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Player;
import net.neoforged.bus.api.EventPriority;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.AddAttributeTooltipsEvent;
import net.neoforged.neoforge.event.entity.EntityJoinLevelEvent;
import net.neoforged.neoforge.event.entity.living.LivingChangeTargetEvent;
import net.neoforged.neoforge.event.entity.living.LivingEntityUseItemEvent;
import net.neoforged.neoforge.event.entity.living.LivingExperienceDropEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.entity.player.PlayerInteractEvent;
import net.neoforged.neoforge.event.level.BlockDropsEvent;
import net.neoforged.neoforge.event.level.block.BreakBlockEvent;
import net.neoforged.neoforge.event.tick.EntityTickEvent;
import org.apache.commons.lang3.mutable.MutableInt;

import java.util.List;

public class ArtifactHooksNeoForge {

    public static void register() {
        if (ModCompat.EXPANDABILITY.isLoaded()) {
            NeoForge.EVENT_BUS.addListener(ArtifactHooksNeoForge::onPlayerSwim);
            NeoForge.EVENT_BUS.addListener(ArtifactHooksNeoForge::onAquaDashersFluidCollision);
        }
        NeoForge.EVENT_BUS.addListener(ArtifactHooksNeoForge::onEntityAdded);
        NeoForge.EVENT_BUS.addListener(ArtifactHooksNeoForge::onLivingUpdate);
        NeoForge.EVENT_BUS.addListener(ArtifactHooksNeoForge::onDrinkingHatItemUse);
        NeoForge.EVENT_BUS.addListener(ArtifactHooksNeoForge::onGoldenHookExperienceDrop);
        NeoForge.EVENT_BUS.addListener(ArtifactHooksNeoForge::onKittySlippersChangeTarget);
        NeoForge.EVENT_BUS.addListener(ArtifactHooksNeoForge::onDiggingClawsHarvestCheck);
        NeoForge.EVENT_BUS.addListener(ArtifactHooksNeoForge::onBlockDrops);
        NeoForge.EVENT_BUS.addListener(ArtifactHooksNeoForge::addAttributeTooltips);
        NeoForge.EVENT_BUS.addListener(ArtifactHooksNeoForge::onRightClickItem);
        NeoForge.EVENT_BUS.addListener(EventPriority.LOWEST, ArtifactHooksNeoForge::onBreakBlock);
    }

    private static void onEntityAdded(EntityJoinLevelEvent event) {
        ArtifactHooks.onEntityAdded(event.getEntity());
    }

    private static void onLivingUpdate(EntityTickEvent.Post event) {
        if (event.getEntity() instanceof LivingEntity entity) {
            onKittySlippersLivingUpdate(entity);
            ArtifactHooks.livingUpdate(entity);
        }
    }

    private static void onDrinkingHatItemUse(LivingEntityUseItemEvent.Start event) {
        event.setDuration(ArtifactHooks.modifyUseDuration(event.getDuration(), event.getItem(), event.getEntity()));
    }

    private static void onGoldenHookExperienceDrop(LivingExperienceDropEvent event) {
        int droppedXp = event.getDroppedExperience();
        int modifiedXp = ArtifactHooks.modifyExperience(droppedXp, event.getEntity(), event.getAttackingPlayer());
        event.setDroppedExperience(modifiedXp);
    }

    private static void onKittySlippersChangeTarget(LivingChangeTargetEvent event) {
        LivingEntity target = event.getNewAboutToBeSetTarget();
        if (event.getEntity().is(ModTags.CREEPERS) && ModDataComponents.CREEPER_REPELLENT.on(target).findAny()) {
            event.setCanceled(true);
        }
    }

    private static void onKittySlippersLivingUpdate(LivingEntity entity) {
        if (entity.getLastHurtByMob() != null
                && ModDataComponents.CREEPER_REPELLENT.on(entity.getLastHurtByMob()).findAny()
                && entity.is(ModTags.CREEPERS)
        ) {
            entity.setLastHurtByMob(null);
        }
    }

    private static void onDiggingClawsHarvestCheck(PlayerEvent.HarvestCheck event) {
        event.setCanHarvest(event.canHarvest() || ToolTierUpgrade.canHarvestWithTier(event.getEntity(), event.getTargetBlock()));
    }

    private static void onBlockDrops(BlockDropsEvent event) {
        List<ItemEntity> drops = event.getDrops();
        MutableInt experience = new MutableInt(0);
        drops.forEach(itemEntity -> itemEntity.setItem(ArtifactHooks.applySmeltOresAbility(
                itemEntity.getItem(),
                event.getBreaker(),
                event.getState(),
                experience::add
        )));
        event.setDroppedExperience(event.getDroppedExperience() + experience.get().intValue());
    }

    private static void onBreakBlock(BreakBlockEvent event) {
        if (!event.isCanceled()) {
            ArtifactHooks.onBlockBroken(event.getPlayer(), event.getState());
        }
    }

    private static void addAttributeTooltips(AddAttributeTooltipsEvent event) {
        TooltipHelper.addAttributeTooltips(event::addTooltipLines, event.getStack(), event.getContext(), event.getContext().tooltipDisplay());
    }

    private static void onRightClickItem(PlayerInteractEvent.RightClickItem event) {
        InteractionResult result = EquipmentSlotManager.tryEquipFromUse(event.getEntity(), event.getHand());
        if (result != InteractionResult.PASS) {
            event.setCancellationResult(result);
            event.setCanceled(true);
        }
    }

    public static void onPlayerSwim(PlayerSwimEvent event) {
        if (event.getResult() == EventResult.PASS && event.getEntity() instanceof Player player) {
            event.setResult(ArtifactHooks.onPlayerSwim(player));
        }
    }

    private static void onAquaDashersFluidCollision(LivingFluidCollisionEvent event) {
        if (ArtifactHooks.onFluidCollision(event.getEntity(), event.getFluidState())) {
            event.setColliding(true);
        }
    }
}
