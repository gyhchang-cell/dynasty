package com.yellowbrossproductions.illageandspillage.events;

import com.yellowbrossproductions.illageandspillage.IllageAndSpillage;
import com.yellowbrossproductions.illageandspillage.Config;
import com.yellowbrossproductions.illageandspillage.entities.*;
import com.yellowbrossproductions.illageandspillage.entities.goal.LoseAIGoal;
import com.yellowbrossproductions.illageandspillage.entities.goal.RunFromIntroBossGoal;
import com.yellowbrossproductions.illageandspillage.entities.goal.RunToHinderGoal;
import com.yellowbrossproductions.illageandspillage.entities.projectile.PumpkinBombEntity;
import com.yellowbrossproductions.illageandspillage.init.ModEntityTypes;
import com.yellowbrossproductions.illageandspillage.init.RaidWaveMembers;
import com.yellowbrossproductions.illageandspillage.util.EffectRegisterer;
import com.yellowbrossproductions.illageandspillage.util.EntityUtil;
import com.yellowbrossproductions.illageandspillage.util.ModTags;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.goal.AvoidEntityGoal;
import net.minecraft.world.entity.npc.AbstractVillager;
import net.minecraft.world.entity.npc.Villager;
import net.minecraft.world.entity.npc.WanderingTrader;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.raid.Raid;
import net.minecraft.world.entity.raid.Raid.RaiderType;
import net.minecraft.world.entity.raid.Raider;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.event.entity.living.LivingAttackEvent;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.event.level.LevelEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.common.Mod.EventBusSubscriber;
import org.apache.commons.lang3.ArrayUtils;

import java.util.List;

@EventBusSubscriber(modid = "illageandspillage", bus = Mod.EventBusSubscriber.Bus.FORGE)
public class ForgeEventBusSubscriber {
    @SubscribeEvent
    public static void addGoals(EntityJoinLevelEvent event) {
        Entity entity = event.getEntity();
        if (entity instanceof AbstractVillager) {
            double runSpeed = 1.0;
            if (entity instanceof Villager) {
                runSpeed = 0.8;
            }

            if (entity instanceof WanderingTrader) {
                runSpeed = 0.5;
            }

            ((PathfinderMob) entity).goalSelector.addGoal(0, new AvoidEntityGoal<>((PathfinderMob) entity, BossRandomizerEntity.class, 8.0F, runSpeed, runSpeed));
            ((PathfinderMob) entity).goalSelector.addGoal(0, new AvoidEntityGoal<>((PathfinderMob) entity, IgniterEntity.class, 8.0F, runSpeed, runSpeed));
            ((PathfinderMob) entity).goalSelector.addGoal(0, new AvoidEntityGoal<>((PathfinderMob) entity, EngineerEntity.class, 8.0F, runSpeed, runSpeed));
            ((PathfinderMob) entity).goalSelector.addGoal(0, new AvoidEntityGoal<>((PathfinderMob) entity, ChagrinSentryEntity.class, 8.0F, runSpeed, runSpeed));
            ((PathfinderMob) entity).goalSelector.addGoal(0, new AvoidEntityGoal<>((PathfinderMob) entity, BeeperEntity.class, 4.0F, runSpeed, runSpeed));
            ((PathfinderMob) entity).goalSelector.addGoal(0, new AvoidEntityGoal<>((PathfinderMob) entity, SniperEntity.class, 4.0F, runSpeed, runSpeed));
            ((PathfinderMob) entity).goalSelector.addGoal(0, new AvoidEntityGoal<>((PathfinderMob) entity, PokerEntity.class, 4.0F, runSpeed, runSpeed));
            ((PathfinderMob) entity).goalSelector.addGoal(0, new AvoidEntityGoal<>((PathfinderMob) entity, TwittollagerEntity.class, 8.0F, runSpeed, runSpeed));
            ((PathfinderMob) entity).goalSelector.addGoal(0, new AvoidEntityGoal<>((PathfinderMob) entity, OldMagispellerEntity.class, 8.0F, runSpeed, runSpeed));
            ((PathfinderMob) entity).goalSelector.addGoal(0, new AvoidEntityGoal<>((PathfinderMob) entity, SpiritcallerEntity.class, 8.0F, runSpeed, runSpeed));
            ((PathfinderMob) entity).goalSelector.addGoal(0, new AvoidEntityGoal<>((PathfinderMob) entity, CrocofangEntity.class, 8.0F, runSpeed, runSpeed));
            ((PathfinderMob) entity).goalSelector.addGoal(0, new AvoidEntityGoal<>((PathfinderMob) entity, PreserverEntity.class, 8.0F, runSpeed, runSpeed));
//            ((PathfinderMob) entity).goalSelector.addGoal(0, new AvoidEntityGoal<>((PathfinderMob) entity, DevastatorEntity.class, 24.0F, runSpeed, runSpeed));
            ((PathfinderMob) entity).goalSelector.addGoal(0, new AvoidEntityGoal<>((PathfinderMob) entity, AbsorberEntity.class, 8.0F, runSpeed, runSpeed));
            ((PathfinderMob) entity).goalSelector.addGoal(0, new AvoidEntityGoal<>((PathfinderMob) entity, FreakagerEntity.class, 8.0F, runSpeed, runSpeed));
            ((PathfinderMob) entity).goalSelector.addGoal(0, new AvoidEntityGoal<>((PathfinderMob) entity, RagnoEntity.class, 8.0F, runSpeed, runSpeed));
            ((PathfinderMob) entity).goalSelector.addGoal(0, new AvoidEntityGoal<>((PathfinderMob) entity, OldFreakagerEntity.class, 8.0F, runSpeed, runSpeed));
            ((PathfinderMob) entity).goalSelector.addGoal(0, new AvoidEntityGoal<>((PathfinderMob) entity, OldRagnoEntity.class, 8.0F, runSpeed, runSpeed));
            ((PathfinderMob) entity).goalSelector.addGoal(0, new AvoidEntityGoal<>((PathfinderMob) entity, PumpkinBombEntity.class, 4.0F, runSpeed, runSpeed));
            ((PathfinderMob) entity).goalSelector.addGoal(0, new AvoidEntityGoal<>((PathfinderMob) entity, FunnyboneEntity.class, 8.0F, runSpeed, runSpeed));
            ((PathfinderMob) entity).goalSelector.addGoal(0, new AvoidEntityGoal<>((PathfinderMob) entity, MagispellerEntity.class, 8.0F, runSpeed, runSpeed));
        }

        if (entity instanceof Raider raider && !(entity instanceof IllagerAttack)) {
            raider.goalSelector.addGoal(0, new RunToHinderGoal(raider));
        }
    }

    @SubscribeEvent
    public static void stopMobs(EntityJoinLevelEvent event) {
        Entity entity = event.getEntity();
        if (entity instanceof Mob) {
            ((Mob) entity).goalSelector.addGoal(0, new LoseAIGoal((Mob) entity));
        }

        if (entity instanceof PathfinderMob && Config.CommonConfig.mobs_watch_intros.get()) {
            ((PathfinderMob) entity).goalSelector.addGoal(0, new RunFromIntroBossGoal((PathfinderMob) entity, SpiritcallerEntity.class, 8.0F, 1.0F, 1.0F));
            ((PathfinderMob) entity).goalSelector.addGoal(0, new RunFromIntroBossGoal((PathfinderMob) entity, FreakagerEntity.class, 8.0F, 1.0F, 1.0F));
        }

    }

    @SubscribeEvent
    public static void addRaidMembers(LevelEvent.Load event) {
        RaidWaveMembers.registerWaveMembers();
    }

    @SubscribeEvent
    public static void removeRaidMembers(LevelEvent.Unload event) {
        Raid.RaiderType[] members = RaiderType.values();

        for (RaiderType member : members) {
            if (RaidWaveMembers.CUSTOM_RAID_MEMBERS.contains(member)) {
                ArrayUtils.remove(members, member.ordinal());
                IllageAndSpillage.LOGGER.info("Removed " + member.name() + " from Raids to prevent a post-mod-removal crash");
            }
        }

    }

    @SubscribeEvent
    public static void extinguishIllagers(LivingHurtEvent event) {
        LivingEntity entity = event.getEntity();
        DamageSource reason = event.getSource();
        if (reason.getEntity() instanceof IgniterEntity && reason.is(DamageTypeTags.IS_PROJECTILE) && !reason.is(DamageTypeTags.IS_FIRE) && entity.isOnFire()) {
            entity.clearFire();
        }

    }

    @SubscribeEvent
    public static void misconductionAttack1(PlayerInteractEvent.RightClickBlock event) {
        if (event.getEntity().getMainHandItem() == ItemStack.EMPTY && event.getHitVec().getDirection() == Direction.UP && event.getEntity().hasEffect(EffectRegisterer.MISCONDUCTION.get())) {
            BlockPos blockpos = event.getPos();
            if (event.getLevel().isClientSide) {
                event.getEntity().swing(InteractionHand.MAIN_HAND);
            }

            EntityUtil.createLineImpsAttack(blockpos, event.getEntity(), event.getEntity().getX(), event.getEntity().getY(), event.getEntity().getZ(), event.getLevel());
        }

    }

    @SubscribeEvent
    public static void misconductionAttack2(LivingAttackEvent event) {
        if (!event.isCanceled() && event.getSource().getEntity() instanceof LivingEntity entity && ((LivingEntity) event.getSource().getEntity()).getMainHandItem() == ItemStack.EMPTY && ((LivingEntity) event.getSource().getEntity()).hasEffect(EffectRegisterer.MISCONDUCTION.get()) && event.getSource().is(DamageTypes.PLAYER_ATTACK)) {
            List<IllagerSoulEntity> list = entity.level().getEntitiesOfClass(IllagerSoulEntity.class, entity.getBoundingBox().inflate(100.0), (predicate) -> predicate.getTarget() == event.getEntity() && predicate.getOwner() == entity);
            if (list.isEmpty()) {
                for (int i = 0; i < 3; ++i) {
                    if (!event.getEntity().level().isClientSide) {
                        IllagerSoulEntity soul = ModEntityTypes.IllagerSoul.get().create(event.getEntity().level());

                        assert soul != null;

                        soul.setPos(event.getEntity().getX() + -4.0 + entity.getRandom().nextInt(8), event.getEntity().getY() + (double) (1 + entity.getRandom().nextInt(4)), event.getEntity().getZ() + -4.0 + entity.getRandom().nextInt(8));
                        soul.setOwner(entity);
                        soul.setAngelOrDevil(entity.getRandom().nextBoolean());
                        soul.setTarget(event.getEntity());
                        soul.setDeltaMovement(0.0, 0.1, 0.0);
                        if (entity.getTeam() != null) {
                            event.getEntity().level().getScoreboard().addPlayerToTeam(soul.getStringUUID(), event.getEntity().level().getScoreboard().getPlayerTeam(entity.getTeam().getName()));
                        }

                        event.getEntity().level().addFreshEntity(soul);
                    }
                }
            }
        }

    }

    @SubscribeEvent
    public static void preventGettingHurt(LivingAttackEvent event) {
        Entity var2 = event.getSource().getEntity();
        if (var2 instanceof IllagerSoulEntity soul) {
            if (soul.getOwner() == event.getEntity()) {
                event.setCanceled(true);
            }
        }

    }

    @SubscribeEvent
    public static void absorberGetsHurt(LivingHurtEvent event) {
        if (event.getEntity() instanceof AbsorberEntity) {
            event.getEntity().invulnerableTime = 0;
        }

    }

    @SubscribeEvent
    public static void preserverGetsHurt(LivingEvent.LivingTickEvent event) {
        LivingEntity mob = event.getEntity();
        if (mob instanceof PreserverEntity thing) {
            if (thing.isOnFire() && thing.getRemainingFireTicks() % 5 == 1) {
                thing.invulnerableTime = 3;
                thing.hurt(thing.damageSources().onFire(), 2.0F);
            }
        }

        if (mob.hasEffect(EffectRegisterer.PRESERVED.get()) && mob.isOnFire() && mob.getRemainingFireTicks() % 5 == 1) {
            mob.invulnerableTime = 3;
            mob.hurt(mob.damageSources().onFire(), 2.0F);
        }

    }

    @SubscribeEvent
    public static void calculatePreservedDamage(LivingHurtEvent event) {
        LivingEntity mob = event.getEntity();
        if (mob.hasEffect(EffectRegisterer.PRESERVED.get()) && !event.getSource().is(DamageTypes.FELL_OUT_OF_WORLD) && !event.getSource().is(DamageTypes.GENERIC_KILL) && !event.getSource().is(DamageTypeTags.IS_FIRE)) {
            event.setAmount(event.getAmount() * 0.5F);
        }

    }

    @SubscribeEvent
    public static void mutateNegativeEffect(LivingEvent.LivingTickEvent event) {
        LivingEntity mob = event.getEntity();
        if (mob.hasEffect(EffectRegisterer.MUTATION.get())) {
            mob.setDeltaMovement(mob.getDeltaMovement().add((-0.5 + mob.getRandom().nextDouble()) * 0.1, 0.0, (-0.5 + mob.getRandom().nextDouble()) * 0.1));
            if (mob.tickCount % 15 == 0 && mob.getHealth() > 1.0F && mob.invulnerableTime < 1) {
                mob.hurt(mob.damageSources().magic(), 1.0F);
                mob.invulnerableTime = 0;
            }
        }

    }

    @SubscribeEvent
    public static void magispellerNegateDamage(LivingHurtEvent event) {
        LivingEntity mob = event.getEntity();
        if (mob instanceof MagispellerEntity && ((MagispellerEntity) mob).isWavingArms() && !event.getSource().is(DamageTypes.FELL_OUT_OF_WORLD) && !event.getSource().is(DamageTypes.GENERIC_KILL) && !event.isCanceled()) {
            ((MagispellerEntity) mob).addDamageTaken(event.getAmount());
            event.setAmount(0.0F);
        }

    }

    @SubscribeEvent
    public static void tickOffBosses(LivingHurtEvent event) {
        LivingEntity mob = event.getEntity();
        if (mob.getType().is(ModTags.EntityTypes.ILLAGER_BOSSES) && mob instanceof Mob targeter) {
            Entity var4 = event.getSource().getEntity();
            if (var4 instanceof Player player) {
                if (!player.getAbilities().invulnerable) {
                    targeter.setTarget(player);
                }
            }
        }

    }

    @SubscribeEvent
    public static void webbedEffects(LivingEvent.LivingTickEvent event) {
        LivingEntity mob = event.getEntity();
        if (mob.hasEffect(EffectRegisterer.WEBBED.get())) {
            if (mob.getRandom().nextInt(20) == 0) EntityUtil.makeWebParticles(mob.level(), mob);
            if (!mob.level().isClientSide && !EntityUtil.isWebbed(mob)) EntityUtil.setWebbed(mob, true);
        } else if (!mob.level().isClientSide && EntityUtil.isWebbed(mob)) {
            EntityUtil.setWebbed(mob, false);
        }
    }

    @SubscribeEvent
    public static void preservedEffects(LivingEvent.LivingTickEvent event) {
        LivingEntity mob = event.getEntity();
        if (mob.hasEffect(EffectRegisterer.PRESERVED.get())) {
            if (!mob.level().isClientSide && !EntityUtil.isPreserved(mob)) {
                EntityUtil.setPreserved(mob, true);
            }
        } else if (!mob.level().isClientSide && EntityUtil.isPreserved(mob)) {
            EntityUtil.setPreserved(mob, false);
        }
    }
}