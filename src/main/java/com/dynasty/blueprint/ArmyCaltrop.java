package com.dynasty.blueprint;

import com.dynasty.blueprint.combat.Combatant;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.ThrowableItemProjectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.HitResult;
import net.minecraftforge.network.NetworkHooks;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;

/** A short-lived, non-pickup ground obstacle: no block replacement or dropped-item duplication. */
public final class ArmyCaltrop extends ThrowableItemProjectile {
    private long expires=-1,nextPulse;
    public ArmyCaltrop(EntityType<? extends ArmyCaltrop> type,Level level){super(type,level);setNoGravity(true);}
    public static void spawn(TemplateMob owner){
        if(!(owner.level() instanceof ServerLevel level)||level.getEntitiesOfClass(ArmyCaltrop.class,owner.getBoundingBox().inflate(24),
                e->e.getOwner()!=null&&e.getOwner().getUUID().equals(owner.getUUID())).size()>=3)return;
        var trap=new ArmyCaltrop(BlueprintEntities.ARMY_CALTROP.get(),level);trap.setOwner(owner);
        trap.setItem(new ItemStack(Items.IRON_NUGGET));trap.setPos(owner.getX(),owner.getY()+.07,owner.getZ());
        trap.expires=level.getGameTime()+100;level.addFreshEntity(trap);
    }
    @Override protected Item getDefaultItem(){return Items.IRON_NUGGET;}
    @Override protected void onHit(HitResult hit){} // It remains a ground obstacle, not a projectile impact.
    @Override public Packet<ClientGamePacketListener> getAddEntityPacket(){return NetworkHooks.getEntitySpawningPacket(this);}
    @Override public void tick(){
        super.tick();
        if(!(level() instanceof ServerLevel level))return;
        long now=level.getGameTime();
        if(expires<0||now>=expires||getOwner()==null||!getOwner().isAlive()){discard();return;}
        if(now<nextPulse)return;nextPulse=now+10;
        for(var target:level.getEntitiesOfClass(LivingEntity.class,getBoundingBox().inflate(.55,.2,.55),
                e->e.isAlive()&&!e.isSpectator()&&!Combatant.allied(getOwner(),e)))
            target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,30,1),getOwner());
    }
    @Override public void addAdditionalSaveData(CompoundTag tag){super.addAdditionalSaveData(tag);tag.putLong("Expires",expires);}
    @Override public void readAdditionalSaveData(CompoundTag tag){super.readAdditionalSaveData(tag);expires=tag.contains("Expires")?tag.getLong("Expires"):-1;nextPulse=level().getGameTime();}
}
