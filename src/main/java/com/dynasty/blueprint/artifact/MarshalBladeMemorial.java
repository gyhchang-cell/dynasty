package com.dynasty.blueprint.artifact;

import com.dynasty.blueprint.boss.MarshalCourtyardState;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.*;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.*;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.*;
import software.bernie.geckolib.util.GeckoLibUtil;

/** Persistent, invulnerable world-space blade. Each eligible player claims once; memorial remains. */
public final class MarshalBladeMemorial extends Entity implements GeoEntity {
    private static final EntityDataAccessor<BlockPos> CENTRE=SynchedEntityData.defineId(MarshalBladeMemorial.class,EntityDataSerializers.BLOCK_POS);
    private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    public MarshalBladeMemorial(EntityType<? extends MarshalBladeMemorial> type,Level level){super(type,level);setNoGravity(true);setInvulnerable(true);}
    @Override protected void defineSynchedData(){entityData.define(CENTRE,BlockPos.ZERO);}
    public void bind(BlockPos p){entityData.set(CENTRE,p.immutable());setPos(Vec3.atBottomCenterOf(p));setYRot(0);}
    public BlockPos centre(){return entityData.get(CENTRE);}
    @Override public boolean isPickable(){return true;}
    @Override public InteractionResult interact(Player player,InteractionHand hand){
        if(hand!=InteractionHand.MAIN_HAND||player.isSpectator()||player.isCreative()||distanceToSqr(player)>4*4)return InteractionResult.PASS;
        if(level().isClientSide)return InteractionResult.SUCCESS;
        if(!(player instanceof ServerPlayer p)||!(level() instanceof ServerLevel w)||!p.isAlive())return InteractionResult.PASS;
        var state=MarshalCourtyardState.get(w);var yard=state.yards.get(centre().asLong());
        if(yard==null||!yard.defeated||!getUUID().equals(yard.memorial)||!state.firstRewarded.contains(p.getUUID())||state.bladeClaimed.contains(p.getUUID()))return InteractionResult.PASS;
        if(!p.getMainHandItem().isEmpty()){p.displayClientMessage(Component.translatable("message.dynasty.marshal_blade_empty_hand"),true);return InteractionResult.FAIL;}
        var reward=new ItemStack(ArtifactContent.LONGYIN.get());if(!p.addItem(reward)){p.displayClientMessage(Component.translatable("message.dynasty.marshal_blade_inventory"),true);return InteractionResult.FAIL;}
        state.bladeClaimed.add(p.getUUID());state.setDirty();return InteractionResult.SUCCESS;
    }
    @Override public void tick(){super.tick();if(level() instanceof ServerLevel w){var yard=MarshalCourtyardState.get(w).yards.get(centre().asLong());if(yard==null||!yard.defeated||!getUUID().equals(yard.memorial)){discard();return;}setPos(Vec3.atBottomCenterOf(centre()));setDeltaMovement(0,0,0);}}
    @Override public void remove(RemovalReason reason){if(reason.shouldDestroy()&&level() instanceof ServerLevel w){var state=MarshalCourtyardState.get(w);var yard=state.yards.get(centre().asLong());if(yard!=null&&getUUID().equals(yard.memorial)){yard.memorial=null;state.setDirty();}}super.remove(reason);}
    @Override public boolean shouldRenderAtSqrDistance(double d){return Double.isFinite(d)&&d<64*64;}
    @Override protected void addAdditionalSaveData(CompoundTag t){t.putLong("MarshalYard",centre().asLong());}
    @Override protected void readAdditionalSaveData(CompoundTag t){entityData.set(CENTRE,t.contains("MarshalYard")?BlockPos.of(t.getLong("MarshalYard")):blockPosition());setNoGravity(true);setInvulnerable(true);}
    @Override public net.minecraft.network.protocol.Packet<net.minecraft.network.protocol.game.ClientGamePacketListener> getAddEntityPacket(){return net.minecraftforge.network.NetworkHooks.getEntitySpawningPacket(this);}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar c){c.add(new AnimationController<MarshalBladeMemorial>(this,"memorial",0,s->{s.setAnimation(RawAnimation.begin().thenLoop("animation.longyin_zhanma_duanyue_dao.idle"));return software.bernie.geckolib.core.object.PlayState.CONTINUE;}));}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
}
